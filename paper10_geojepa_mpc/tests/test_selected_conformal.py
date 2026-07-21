import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from paper10_geojepa_mpc.planning import selected_conformal as conformal


def _valid_lineage() -> dict[str, object]:
    return {
        "planning_horizon": 3,
        "model_seed": 5101,
        "ensemble_size": 3,
        "policy_round": 1,
        "compute_mode": "matched",
        "checkpoint_digests": ["a" * 64, "b" * 64, "c" * 64],
        "selected_labels_manifest_digest": "d" * 64,
        "candidate_generator_digest": "e" * 64,
        "base_selector_digest": "f" * 64,
    }


def test_one_sided_score_ignores_harmless_underprediction():
    true = np.zeros((1, 3, 4))
    true[0, 0, 1:] = 10.0
    predicted = np.zeros_like(true)
    scale = np.ones_like(true)

    scores = conformal.selected_trajectory_scores(
        true,
        predicted,
        scale,
        trajectory_ids=np.array([2000]),
        planning_horizon_index=0,
    )

    assert scores.tolist() == [0.0]


def test_score_uses_only_selected_horizon_and_planning_objectives():
    true = np.zeros((2, 3, 4))
    predicted = np.zeros_like(true)
    predicted[0, 0, 0] = 1_000.0
    predicted[0, 2, 1:] = 1_000.0
    predicted[1, 1, 2] = 3.0

    scores = conformal.selected_trajectory_scores(
        true,
        predicted,
        np.ones_like(true),
        trajectory_ids=np.array([2000, 2000]),
        planning_horizon_index=1,
    )

    assert scores.tolist() == [3.0]


@pytest.mark.parametrize(
    ("coverage", "expected_rank"),
    [(0.8, 17), (0.9, 19), (0.95, 20)],
)
def test_twenty_trajectory_finite_sample_rank(coverage, expected_rank):
    calibrator = conformal.fit_selected_planning_calibrator(
        trajectory_scores=np.arange(1, 21, dtype=float),
        trajectory_ids=np.arange(2000, 2020),
        coverage=coverage,
        lineage=_valid_lineage(),
    )

    assert calibrator.finite_sample_rank == expected_rank
    assert calibrator.q_planning == float(expected_rank)
    assert calibrator.planning_horizon == 3


def _fit_small_calibrator(conformal):
    return conformal.fit_selected_planning_calibrator(
        trajectory_scores=np.array([0.0, 0.0]),
        trajectory_ids=np.array([10, 11]),
        coverage=0.5,
        lineage=_valid_lineage(),
    )


def _canonical_digest(payload: dict[str, object]) -> str:
    clean = {
        key: value
        for key, value in payload.items()
        if key != "calibrator_digest"
    }
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def test_selected_coverage_audit_counts_trajectories_not_rows():
    calibrator = _fit_small_calibrator(conformal)
    true = np.zeros((4, 3, 4))
    predicted = np.zeros_like(true)
    predicted[1, 1, 2] = 1.0

    audit = conformal.audit_selected_coverage(
        calibrator,
        true,
        predicted,
        np.ones_like(true),
        trajectory_ids=np.array([10, 10, 11, 11]),
    )

    assert audit["n_trajectories"] == 2
    assert audit["covered_trajectories"] == 1
    assert audit["planning_coverage"] == 0.5


def test_serialized_selected_calibrator_detects_content_mutation(tmp_path):
    calibrator = _fit_small_calibrator(conformal)
    path = tmp_path / "calibrator.json"
    saved = conformal.save_selected_planning_calibrator(path, calibrator)

    loaded = conformal.load_selected_planning_calibrator(
        path,
        expected_lineage=_valid_lineage(),
    )
    assert loaded.q_planning == calibrator.q_planning
    saved["q_planning"] += 1.0
    path.write_text(json.dumps(saved), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        conformal.load_selected_planning_calibrator(path)


def test_loader_recomputes_finite_sample_quantile_after_digest_check(tmp_path):
    calibrator = conformal.fit_selected_planning_calibrator(
        trajectory_scores=np.array([1.0, 2.0, 3.0]),
        trajectory_ids=np.array([10, 11, 12]),
        coverage=0.5,
        lineage=_valid_lineage(),
    )
    path = tmp_path / "calibrator.json"
    payload = conformal.save_selected_planning_calibrator(path, calibrator)
    payload["q_planning"] = 99.0
    payload["calibrator_digest"] = _canonical_digest(payload)
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="quantile"):
        conformal.load_selected_planning_calibrator(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("compute_mode", "full"),
        ("planning_horizon", 5),
        ("selected_labels_manifest_digest", "9" * 64),
        (
            "checkpoint_digests",
            ["c" * 64, "b" * 64, "a" * 64],
        ),
    ],
)
def test_loader_rejects_expected_lineage_mutation(tmp_path, field, value):
    path = tmp_path / "calibrator.json"
    conformal.save_selected_planning_calibrator(
        path,
        _fit_small_calibrator(conformal),
    )
    expected = _valid_lineage()
    expected[field] = value

    with pytest.raises(ValueError, match="lineage"):
        conformal.load_selected_planning_calibrator(
            path,
            expected_lineage=expected,
        )


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_digest(payload: dict[str, object]) -> str:
    clean = {
        key: value for key, value in payload.items() if key != "manifest_digest"
    }
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _write_selected_manifest(
    root: Path,
    *,
    registry_digest: str,
    checkpoint_digests: list[str],
) -> tuple[Path, dict[str, object]]:
    root.mkdir(parents=True)
    artifacts = []
    for offset, seed in enumerate((2000, 2001), start=1):
        true = np.zeros((2, 3, 4), dtype=np.float32)
        predicted = np.zeros_like(true)
        predicted[0, 2, 1] = float(offset)
        path = root / f"trajectory_{seed}.npz"
        np.savez_compressed(
            path,
            true_delta=true,
            predicted_delta=predicted,
            predicted_scale=np.ones_like(true),
            trajectory_ids=np.full(2, seed, dtype=np.int64),
        )
        artifacts.append(
            {
                "trajectory_seed": seed,
                "path": path.name,
                "sha256": _sha256_file(path),
                "n_states": 2,
            }
        )
    payload = {
        "schema_version": 1,
        "protocol_id": "pcc_v1_1",
        "registry_digest": registry_digest,
        "partition": "calibration",
        "trajectory_seeds": [2000, 2001],
        "model_seed": 5101,
        "ensemble_size": 3,
        "policy_round": 1,
        "compute_mode": "matched",
        "checkpoint_digests": checkpoint_digests,
        "candidate_generator_digest": "e" * 64,
        "base_selector_digest": "f" * 64,
        "reference_checkpoint_digest": "9" * 64,
        "artifacts": artifacts,
    }
    payload["manifest_digest"] = _manifest_digest(payload)
    path = root / "manifest.json"
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path, payload


def _selected_cli_args(
    *,
    registry: Path,
    manifest: Path,
    checkpoint_root: Path,
    output_dir: Path,
    compute_mode: str = "matched",
) -> list[str]:
    return [
        "--registry",
        str(registry),
        "--selected-labels-manifest",
        str(manifest),
        "--checkpoint-root",
        str(checkpoint_root),
        "--model-seed",
        "5101",
        "--ensemble-size",
        "3",
        "--policy-round",
        "1",
        "--planning-horizon",
        "5",
        "--compute-mode",
        compute_mode,
        "--coverage",
        "0.9",
        "--output-dir",
        str(output_dir),
    ]


def test_selected_calibrator_cli_fits_bound_artifacts(tmp_path, monkeypatch):
    registry_path = tmp_path / "pcc_v1_1.json"
    registry_path.write_text("{}\n", encoding="utf-8")
    registry_digest = _sha256_file(registry_path)
    checkpoint_root = tmp_path / "checkpoints"
    checkpoint_root.mkdir()
    checkpoint_paths = []
    for index in range(3):
        path = checkpoint_root / f"member_{index}.pt"
        path.write_bytes(f"checkpoint-{index}".encode("ascii"))
        checkpoint_paths.append(path)
    checkpoint_digests = [_sha256_file(path) for path in checkpoint_paths]
    manifest, payload = _write_selected_manifest(
        tmp_path / "selected",
        registry_digest=registry_digest,
        checkpoint_digests=checkpoint_digests,
    )
    registry = {
        "protocol_id": "pcc_v1_1",
        "status": "development",
        "model_seeds": [5101],
        "viability": {"ensemble_size": 3, "policy_round": 1},
        "selected_conformal": {"coverages": [0.8, 0.9, 0.95]},
    }
    monkeypatch.setattr(conformal, "load_registry", lambda _: registry)
    monkeypatch.setattr(conformal, "validate_registry", lambda _: None)
    output_dir = tmp_path / "calibrator"

    summary = conformal.main(
        _selected_cli_args(
            registry=registry_path,
            manifest=manifest,
            checkpoint_root=checkpoint_root,
            output_dir=output_dir,
        )
    )

    loaded = conformal.load_selected_planning_calibrator(
        output_dir / "calibrator.json"
    )
    assert summary["q_planning"] == 2.0
    assert loaded.q_planning == 2.0
    assert loaded.selected_labels_manifest_digest == payload["manifest_digest"]
    assert loaded.checkpoint_digests == tuple(checkpoint_digests)


def test_selected_calibrator_cli_rejects_lineage_before_output(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "pcc_v1_1.json"
    registry_path.write_text("{}\n", encoding="utf-8")
    checkpoint_root = tmp_path / "checkpoints"
    checkpoint_root.mkdir()
    checkpoint_paths = []
    for index in range(3):
        path = checkpoint_root / f"member_{index}.pt"
        path.write_bytes(f"checkpoint-{index}".encode("ascii"))
        checkpoint_paths.append(path)
    manifest, _ = _write_selected_manifest(
        tmp_path / "selected",
        registry_digest=_sha256_file(registry_path),
        checkpoint_digests=[_sha256_file(path) for path in checkpoint_paths],
    )
    registry = {
        "protocol_id": "pcc_v1_1",
        "status": "development",
        "model_seeds": [5101],
        "viability": {"ensemble_size": 3, "policy_round": 1},
        "selected_conformal": {"coverages": [0.8, 0.9, 0.95]},
    }
    monkeypatch.setattr(conformal, "load_registry", lambda _: registry)
    monkeypatch.setattr(conformal, "validate_registry", lambda _: None)
    output_dir = tmp_path / "must_not_exist"

    with pytest.raises(ValueError, match="lineage"):
        conformal.main(
            _selected_cli_args(
                registry=registry_path,
                manifest=manifest,
                checkpoint_root=checkpoint_root,
                output_dir=output_dir,
                compute_mode="full",
            )
        )

    assert not output_dir.exists()
