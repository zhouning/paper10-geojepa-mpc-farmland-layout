import json
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest


V11_REGISTRY = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "protocols"
    / "pcc_v1_1.json"
)


def _pilot():
    return import_module(
        "paper10_geojepa_mpc.experiments.run_pcc_v1_1_pilot"
    )


def _args(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "--registry",
        str(V11_REGISTRY),
        "--train-manifest",
        str(tmp_path / "train" / "manifest.json"),
        "--reference-checkpoint",
        str(tmp_path / "reference.pt"),
        "--prepared-dir",
        str(tmp_path),
        "--output-dir",
        str(tmp_path / "pilot"),
        "--epochs",
        "20",
        "--batch-size",
        "128",
        "--learning-rate",
        "0.001",
        "--states-per-selected-trajectory",
        "20",
        "--max-workers",
        "2",
        "--device",
        "cpu",
        "--audit-json",
        str(tmp_path / "pilot_audit.json"),
        "--audit-md",
        str(tmp_path / "pilot_audit.md"),
        *extra,
    ]


def _fake_external_inputs(**_kwargs):
    return [
        {"kind": "train_manifest", "path": "fixture", "sha256": "a" * 64},
        {
            "kind": "reference_checkpoint",
            "path": "fixture",
            "sha256": "b" * 64,
        },
    ]


def test_pilot_dry_run_contains_no_confirmation_seed_or_full_factorial(
    tmp_path,
    monkeypatch,
):
    pilot = _pilot()
    monkeypatch.setattr(
        pilot,
        "_validate_external_inputs",
        _fake_external_inputs,
    )

    result = pilot.main(_args(tmp_path, "--dry-run"))
    plan = json.loads(
        (tmp_path / "pilot" / "execution_plan.json").read_text(
            encoding="utf-8"
        )
    )

    assert result["status"] == "dry_run"
    assert plan["phase"] == "viability_pilot"
    assert plan["model_seeds"] == [5101, 5102, 5103]
    assert plan["ensemble_size"] == 3
    assert plan["policy_round"] == 1
    assert len(plan["jobs"]) == 19
    assert {job["phase"] for job in plan["jobs"]} == {
        "train",
        "selected_calibration_labels",
        "fit_selected_calibrators",
        "selected_development_labels",
        "viability_closeout",
    }
    phase_counts = {
        phase: sum(job["phase"] == phase for job in plan["jobs"])
        for phase in {job["phase"] for job in plan["jobs"]}
    }
    assert phase_counts == {
        "train": 3,
        "selected_calibration_labels": 3,
        "fit_selected_calibrators": 9,
        "selected_development_labels": 3,
        "viability_closeout": 1,
    }
    command_text = "\n".join(
        " ".join(job["command"]) for job in plan["jobs"]
    )
    assert "4000" not in command_text
    assert "8000" not in command_text
    assert "--ensemble-size 5" not in command_text
    assert "--policy-round 2" not in command_text


def test_job_metadata_precedes_worker_and_resume_rejects_command_change(
    tmp_path,
):
    pilot = _pilot()
    source = tmp_path / "source.txt"
    source.write_text("source", encoding="utf-8")
    output = tmp_path / "result.txt"
    metadata = tmp_path / "job_metadata.json"
    job = {
        "id": "fixture",
        "phase": "fixture",
        "command": ["fixture-worker"],
        "registry_digest": "a" * 64,
        "input_paths": [str(source)],
        "expected_outputs": [str(output)],
        "metadata": str(metadata),
    }

    def runner(command, check=False):
        assert command == ["fixture-worker"]
        assert check is False
        before = json.loads(metadata.read_text(encoding="utf-8"))
        assert before["exit_code"] is None
        assert before["output_digests"] == []
        output.write_text("complete", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    completed = pilot.execute_pilot_job(job, resume=False, runner=runner)

    assert completed["exit_code"] == 0
    assert len(completed["input_digests"]) == 1
    assert len(completed["output_digests"]) == 1
    assert completed["completed_at"] is not None
    changed = {**job, "command": ["different-worker"]}
    with pytest.raises(ValueError, match="metadata mismatch"):
        pilot.execute_pilot_job(
            changed,
            resume=True,
            runner=lambda *_args, **_kwargs: pytest.fail(
                "valid completed jobs must not rerun"
            ),
        )


def test_failed_pilot_closes_without_factorial_jobs(tmp_path, monkeypatch):
    pilot = _pilot()
    monkeypatch.setattr(
        pilot,
        "_validate_external_inputs",
        _fake_external_inputs,
    )
    monkeypatch.setattr(pilot, "_execute_pilot_jobs", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        pilot,
        "verify_pilot_inventory",
        lambda *_args, **_kwargs: {
            "passed": False,
            "status": "scientific_failure",
            "selected_coverage": None,
            "checkpoint_families": 3,
            "physical_checkpoints": 9,
            "selected_calibration_manifests": 3,
            "calibrators": 9,
            "selected_development_manifests": 3,
            "failed_gates": ["minimum_nonfallback_rate"],
            "input_digests": [],
        },
    )

    result = pilot.main(_args(tmp_path))

    assert result["status"] == "scientific_failure"
    assert result["selected_coverage"] is None
    assert not (tmp_path / "pilot" / "round2").exists()
    assert not (tmp_path / "pilot" / "factorial").exists()


def test_fresh_inventory_verification_binds_all_outputs(tmp_path, monkeypatch):
    pilot = _pilot()
    train_manifest = tmp_path / "train" / "manifest.json"
    train_manifest.parent.mkdir(parents=True)
    train_manifest.write_text("{}", encoding="utf-8")
    (tmp_path / "reference.pt").write_bytes(b"reference")
    monkeypatch.setattr(
        pilot,
        "_validate_external_inputs",
        _fake_external_inputs,
    )
    pilot.main(_args(tmp_path, "--dry-run"))
    plan = json.loads(
        (tmp_path / "pilot" / "execution_plan.json").read_text(
            encoding="utf-8"
        )
    )

    for job in plan["jobs"]:
        def runner(_command, check=False, *, current=job):
            assert check is False
            for raw_output in current["expected_outputs"]:
                output = Path(raw_output)
                output.parent.mkdir(parents=True, exist_ok=True)
                if (
                    current["phase"] == "viability_closeout"
                    and output.suffix == ".json"
                ):
                    output.write_text(
                        json.dumps(
                            {
                                "protocol_id": "pcc_v1_1",
                                "registry_digest": plan["registry_digest"],
                                "status": "scientific_failure",
                                "passed": False,
                                "selected_coverage": None,
                                "failed_gates": ["minimum_nonfallback_rate"],
                                "reports": {
                                    "0.80": {"passed": False},
                                    "0.90": {"passed": False},
                                    "0.95": {"passed": False},
                                },
                            }
                        ),
                        encoding="utf-8",
                    )
                else:
                    output.write_bytes(
                        f"{current['id']}:{output.name}".encode("ascii")
                    )
            return SimpleNamespace(returncode=0)

        pilot.execute_pilot_job(job, resume=False, runner=runner)

    result = pilot.verify_pilot_inventory(
        tmp_path / "pilot",
        registry_digest=plan["registry_digest"],
    )

    assert result["passed"] is False
    assert result["status"] == "scientific_failure"
    assert result["checkpoint_families"] == 3
    assert result["physical_checkpoints"] == 9
    assert result["selected_calibration_manifests"] == 3
    assert result["calibrators"] == 9
    assert result["selected_development_manifests"] == 3
    assert set(result["coverage_reports"]) == {"0.80", "0.90", "0.95"}

    tampered = Path(plan["jobs"][0]["expected_outputs"][0])
    tampered.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="output digest"):
        pilot.verify_pilot_inventory(
            tmp_path / "pilot",
            registry_digest=plan["registry_digest"],
        )
