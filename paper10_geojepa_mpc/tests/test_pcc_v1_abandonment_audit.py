import hashlib
import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments import pcc_v1_abandonment_audit


audit_abandoned_pcc_v1 = pcc_v1_abandonment_audit.audit_abandoned_pcc_v1


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_old_run_fixture(tmp_path: Path) -> tuple[Path, Path]:
    run_root = tmp_path / "policy_iteration"
    train_root = (
        run_root / "seed_5101" / "round2" / "labels" / "train"
    )
    complete = train_root / "seed_1000"
    complete.mkdir(parents=True, exist_ok=True)
    artifact = complete / "trajectory_1000.npz"
    artifact.write_bytes(b"same scientific artifact")
    (complete / "manifest.json").write_text(
        json.dumps(
            {
                "artifacts": [
                    {
                        "trajectory_seed": 1000,
                        "path": artifact.name,
                        "sha256": _sha256(artifact),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    incomplete = train_root / "seed_1001"
    incomplete.mkdir(exist_ok=True)
    (incomplete / "trajectory_1001.tmp.npz").write_bytes(b"partial")

    round0_root = tmp_path / "round0"
    round0_seed = round0_root / "seed_1000"
    round0_seed.mkdir(parents=True, exist_ok=True)
    (round0_seed / "trajectory_1000.npz").write_bytes(artifact.read_bytes())
    return run_root, round0_root


def test_abandonment_audit_records_only_atomic_complete_seeds(tmp_path):
    old_root, round0_root = _make_old_run_fixture(tmp_path)

    report = audit_abandoned_pcc_v1(
        old_root,
        round0_root=round0_root,
        registry_digest="a" * 64,
        stop_verified_at="2026-07-21T12:40:00+09:00",
        confirmation_seeds_run=(),
    )

    assert report["status"] == "abandoned_before_freeze"
    assert report["completed_round2_train_seeds"] == [1000]
    assert report["byte_identical_to_round0_seeds"] == [1000]
    assert report["incomplete_seed_directories"] == ["seed_1001"]
    assert report["confirmation_seeds_run"] == []
    assert report["eligible_for_pcc_v1_1_resume"] is False


def test_abandonment_audit_rejects_any_confirmation_seed(tmp_path):
    old_root, round0_root = _make_old_run_fixture(tmp_path)

    with pytest.raises(ValueError, match="confirmation"):
        audit_abandoned_pcc_v1(
            old_root,
            round0_root=round0_root,
            registry_digest="a" * 64,
            stop_verified_at="2026-07-21T12:40:00+09:00",
            confirmation_seeds_run=(4000,),
        )


def _run_audit_cli(
    tmp_path: Path,
    *,
    output_json: Path,
    output_md: Path,
) -> None:
    old_root, round0_root = _make_old_run_fixture(tmp_path)
    registry = tmp_path / "pcc_v1.json"
    registry.write_text('{"protocol_id": "pcc_v1"}\n', encoding="utf-8")
    pcc_v1_abandonment_audit.main(
        [
            "--registry",
            str(registry),
            "--run-root",
            str(old_root),
            "--round0-root",
            str(round0_root),
            "--stop-verified-at",
            "2026-07-21T12:40:00+09:00",
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ]
    )


def test_abandonment_audit_cli_writes_canonical_outputs_idempotently(tmp_path):
    output_json = tmp_path / "audit" / "abandonment.json"
    output_md = tmp_path / "audit" / "abandonment.md"

    _run_audit_cli(tmp_path, output_json=output_json, output_md=output_md)
    first_json = output_json.read_bytes()
    first_md = output_md.read_bytes()
    _run_audit_cli(tmp_path, output_json=output_json, output_md=output_md)

    report = json.loads(first_json)
    assert report["completed_round2_train_seeds"] == [1000]
    assert output_json.read_bytes() == first_json
    assert output_md.read_bytes() == first_md
    assert b"Completed round-2 train seeds: 1000" in first_md
    assert not output_json.with_suffix(".json.tmp").exists()
    assert not output_md.with_suffix(".md.tmp").exists()


@pytest.mark.parametrize("tampered_output", ["json", "markdown"])
def test_abandonment_audit_cli_refuses_different_existing_output(
    tmp_path,
    tampered_output,
):
    output_json = tmp_path / "audit" / "abandonment.json"
    output_md = tmp_path / "audit" / "abandonment.md"
    _run_audit_cli(tmp_path, output_json=output_json, output_md=output_md)
    target = output_json if tampered_output == "json" else output_md
    target.write_text("different\n", encoding="utf-8")

    with pytest.raises(ValueError, match="refusing to overwrite different audit"):
        _run_audit_cli(tmp_path, output_json=output_json, output_md=output_md)
