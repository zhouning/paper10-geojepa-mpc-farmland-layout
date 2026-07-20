import json
from dataclasses import replace
import hashlib
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
)
from paper10_geojepa_mpc.experiments.run_pcc_confirmation import (
    assert_frozen_registry_committed,
    build_confirmation_plan,
    close_confirmation_plan,
    execute_confirmation_plan,
    main,
)


class _FakeInventory:
    def checkpoint_root(self, model_seed, ensemble_size, policy_round):
        return Path(
            f"checkpoints/model-{model_seed}/k-{ensemble_size}/round-{policy_round}"
        )

    def checkpoint_digests(self, model_seed, ensemble_size, policy_round):
        return tuple(
            f"{model_seed:04x}{ensemble_size:02x}{policy_round:02x}{member:02x}".ljust(
                64,
                "0",
            )
            for member in range(ensemble_size)
        )

    def calibrator(self, model_seed, ensemble_size, policy_round, coverage):
        return Path(
            f"calibration/model-{model_seed}/k-{ensemble_size}/"
            f"round-{policy_round}/coverage-{coverage}.json"
        )

    def calibrator_digest(
        self,
        model_seed,
        ensemble_size,
        policy_round,
        coverage,
    ):
        return f"{model_seed:04x}{ensemble_size:02x}{policy_round:02x}".ljust(
            64,
            "f",
        )


def _selected_config():
    return {
        "id": "winner",
        "ensemble_size": 3,
        "policy_round": 2,
        "joint_coverage": 0.9,
        "planning_horizon": 3,
        "tolerance_scale": 0.05,
        "residual_window": 10,
        "primary_comparator": "paper9_mpc",
        "compute_budget": 50,
    }


def _frozen_registry(tmp_path):
    path = tmp_path / "pcc_v1.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")
    return path, freeze_registry(path, selected_config=_selected_config())


def _git(repo, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def test_confirmation_plan_refuses_development_registry(tmp_path):
    with pytest.raises(ValueError, match="not frozen"):
        build_confirmation_plan(
            load_registry(),
            registry_path=tmp_path / "pcc_v1.json",
            run_root=tmp_path,
            region="bishan",
            inventory=_FakeInventory(),
        )


def test_confirmation_requires_frozen_registry_blob_in_git(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "paper10@example.invalid")
    _git(repo, "config", "user.name", "Paper10 Test")
    registry_path = repo / "pcc_v1.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    _git(repo, "add", "pcc_v1.json")
    _git(repo, "commit", "-m", "development registry")
    frozen = freeze_registry(registry_path, selected_config=_selected_config())

    with pytest.raises(ValueError, match="committed"):
        assert_frozen_registry_committed(
            registry_path,
            frozen["frozen_digest"],
        )

    _git(repo, "add", "pcc_v1.json")
    _git(repo, "commit", "-m", "freeze registry")
    assert_frozen_registry_committed(registry_path, frozen["frozen_digest"])


def test_bishan_plan_has_one_job_per_policy_and_model_dependency(tmp_path):
    registry_path, frozen = _frozen_registry(tmp_path)

    plan = build_confirmation_plan(
        frozen,
        registry_path=registry_path,
        run_root=tmp_path / "runs",
        region="bishan",
        inventory=_FakeInventory(),
    )

    assert {job.policy for job in plan.jobs} == set(frozen["deployable_baselines"])
    assert all(job.seeds == tuple(range(4000, 4020)) for job in plan.jobs)
    assert len([job for job in plan.jobs if job.policy == "pcc_full"]) == 3
    assert len([job for job in plan.jobs if job.policy == "paper9_mpc"]) == 1
    assert len(plan.jobs) == 17


def _job_payload(plan, job):
    return {
        "schema_version": 1,
        "registry_digest": plan.registry_digest,
        "checkpoint_digests": list(job.checkpoint_digests),
        "seed_results": [
            {
                "seed": seed,
                "policy": job.policy,
                "model_seed": job.model_seed,
                "registry_digest": plan.registry_digest,
                "checkpoint_digests": list(job.checkpoint_digests),
                "objective_outcome": [1.0, 0.2, 0.3, 0.4],
                "environment_step_count": 1,
                "steps": [{"unexecuted_real_reward_queries": 0}],
            }
            for seed in job.seeds
        ],
    }


def test_execution_plan_and_metadata_are_written_before_worker(tmp_path):
    registry_path, frozen = _frozen_registry(tmp_path)
    full_plan = build_confirmation_plan(
        frozen,
        registry_path=registry_path,
        run_root=tmp_path / "runs",
        region="bishan",
        inventory=_FakeInventory(),
    )
    job = replace(full_plan.jobs[0], seeds=(4000, 4001))
    plan = replace(full_plan, jobs=(job,))
    plan_path = tmp_path / "runs" / "confirmation" / "bishan" / "plan.json"

    def fake_runner(command, check=False):
        assert plan_path.is_file()
        assert job.metadata.is_file()
        metadata = json.loads(job.metadata.read_text(encoding="utf-8"))
        assert metadata["output_sha256"] is None
        job.output.parent.mkdir(parents=True, exist_ok=True)
        job.output.write_text(json.dumps(_job_payload(plan, job)), encoding="utf-8")
        return SimpleNamespace(returncode=0)

    results = execute_confirmation_plan(
        plan,
        plan_path=plan_path,
        runner=fake_runner,
    )

    assert len(results) == 1
    metadata = json.loads(job.metadata.read_text(encoding="utf-8"))
    assert len(metadata["output_sha256"]) == 64
    assert results[0]["seed_results"][0]["seed"] == 4000


def test_confirmation_resume_continues_digest_bound_partial_output(
    tmp_path,
):
    registry_path, frozen = _frozen_registry(tmp_path)
    full_plan = build_confirmation_plan(
        frozen,
        registry_path=registry_path,
        run_root=tmp_path / "runs",
        region="bishan",
        inventory=_FakeInventory(),
    )
    job = replace(full_plan.jobs[0], seeds=(4000, 4001))
    plan = replace(full_plan, jobs=(job,))
    plan_path = tmp_path / "runs" / "confirmation" / "bishan" / "plan.json"
    partial = _job_payload(plan, job)
    partial["seed_results"] = partial["seed_results"][:1]
    job.output.parent.mkdir(parents=True, exist_ok=True)
    job.output.write_text(json.dumps(partial), encoding="utf-8")
    metadata = {
        "schema_version": 1,
        "registry_digest": plan.registry_digest,
        "region": job.region,
        "policy": job.policy,
        "model_seed": job.model_seed,
        "seeds": list(job.seeds),
        "checkpoint_digests": list(job.checkpoint_digests),
        "calibrator_digest": job.calibrator_digest,
        "output_sha256": None,
    }
    job.metadata.write_text(json.dumps(metadata), encoding="utf-8")

    def fake_runner(command, check=False):
        assert "--resume" in command
        job.output.write_text(json.dumps(_job_payload(plan, job)), encoding="utf-8")
        return SimpleNamespace(returncode=0)

    results = execute_confirmation_plan(
        plan,
        plan_path=plan_path,
        resume=True,
        runner=fake_runner,
    )

    assert len(results[0]["seed_results"]) == 2
    sealed = json.loads(job.metadata.read_text(encoding="utf-8"))
    assert len(sealed["output_sha256"]) == 64


def _seal_job(plan, job):
    job.output.parent.mkdir(parents=True, exist_ok=True)
    job.output.write_text(json.dumps(_job_payload(plan, job)), encoding="utf-8")
    metadata = {
        "schema_version": 1,
        "registry_digest": plan.registry_digest,
        "region": job.region,
        "policy": job.policy,
        "model_seed": job.model_seed,
        "seeds": list(job.seeds),
        "checkpoint_digests": list(job.checkpoint_digests),
        "calibrator_digest": job.calibrator_digest,
        "output_sha256": hashlib.sha256(job.output.read_bytes()).hexdigest(),
    }
    job.metadata.write_text(json.dumps(metadata), encoding="utf-8")


def test_confirmation_closeout_requires_complete_physical_policy_blocks(tmp_path):
    registry_path, frozen = _frozen_registry(tmp_path)
    plan = build_confirmation_plan(
        frozen,
        registry_path=registry_path,
        run_root=tmp_path / "runs",
        region="bishan",
        inventory=_FakeInventory(),
    )
    manifest_path = (
        tmp_path / "runs" / "confirmation" / "bishan" / "manifest.json"
    )
    for job in plan.jobs[:-1]:
        _seal_job(plan, job)

    with pytest.raises((FileNotFoundError, ValueError), match="missing|complete"):
        close_confirmation_plan(plan, manifest_path=manifest_path)

    _seal_job(plan, plan.jobs[-1])
    manifest = close_confirmation_plan(plan, manifest_path=manifest_path)

    assert manifest["complete"] is True
    assert manifest["physical_model_blocks"]["paper9_mpc"] == 1
    assert manifest["physical_model_blocks"]["pcc_full"] == 3
    assert manifest_path.is_file()


def test_confirmation_cli_dry_run_writes_plan_from_committed_freeze(
    tmp_path,
    monkeypatch,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "paper10@example.invalid")
    _git(repo, "config", "user.name", "Paper10 Test")
    registry_path = repo / "pcc_v1.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    freeze_registry(registry_path, selected_config=_selected_config())
    _git(repo, "add", "pcc_v1.json")
    _git(repo, "commit", "-m", "freeze registry")
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_confirmation.build_inventory",
        lambda *args, **kwargs: _FakeInventory(),
    )
    run_root = tmp_path / "runs"

    main(
        [
            "--registry",
            str(registry_path),
            "--region",
            "bishan",
            "--run-root",
            str(run_root),
            "--prepared-dir-bishan",
            str(tmp_path),
            "--prepared-dir-dongxing",
            str(tmp_path),
            "--checkpoint-root",
            str(tmp_path / "checkpoints"),
            "--dry-run",
        ]
    )

    plan_path = run_root / "confirmation" / "bishan" / "execution_plan.json"
    assert plan_path.is_file()
    assert not any(job.output.exists() for job in build_confirmation_plan(
        load_registry(registry_path),
        registry_path=registry_path,
        run_root=run_root,
        region="bishan",
        inventory=_FakeInventory(),
        prepared_dir_bishan=tmp_path,
    ).jobs)


def test_confirmation_cli_uses_adapted_inventory_for_dongxing(
    tmp_path,
    monkeypatch,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "paper10@example.invalid")
    _git(repo, "config", "user.name", "Paper10 Test")
    registry_path = repo / "pcc_v1.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    frozen = freeze_registry(registry_path, selected_config=_selected_config())
    _git(repo, "add", "pcc_v1.json")
    _git(repo, "commit", "-m", "freeze registry")
    checkpoint_root = tmp_path / "dongxing-checkpoints"
    calibration_root = tmp_path / "dongxing-calibration"
    captured = {}

    def fake_adapted_inventory(root, *, calibrator_root, registry):
        captured.update(
            root=Path(root),
            calibrator_root=Path(calibrator_root),
            registry=registry,
        )
        return _FakeInventory()

    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_confirmation.build_inventory",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Dongxing must not use the development inventory")
        ),
    )
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_confirmation.build_adapted_inventory",
        fake_adapted_inventory,
        raising=False,
    )

    main(
        [
            "--registry",
            str(registry_path),
            "--region",
            "dongxing",
            "--run-root",
            str(tmp_path / "runs"),
            "--prepared-dir-bishan",
            str(tmp_path),
            "--prepared-dir-dongxing",
            str(tmp_path),
            "--checkpoint-root",
            str(tmp_path / "bishan-checkpoints"),
            "--dongxing-checkpoint-root",
            str(checkpoint_root),
            "--dongxing-calibration-root",
            str(calibration_root),
            "--dry-run",
        ]
    )

    assert captured["root"] == checkpoint_root
    assert captured["calibrator_root"] == calibration_root
    assert captured["registry"] == frozen
