import hashlib
import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.pcc_input_audit import (
    audit_pcc_inputs,
    main,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry


def _manifest_digest(payload):
    clean = {key: value for key, value in payload.items() if key != "manifest_digest"}
    return hashlib.sha256(
        json.dumps(
            clean,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _write_manifest(
    root: Path,
    registry,
    partition: str,
    seeds,
    *,
    continuation="paper9_mpc",
):
    root.mkdir(parents=True)
    sampling = registry["offline_sampling"][partition]
    artifacts = []
    for seed in seeds:
        seed_root = root / f"seed_{seed}"
        seed_root.mkdir()
        artifact = seed_root / f"trajectory_{seed}.npz"
        artifact.write_bytes(f"fixture-{seed}".encode("ascii"))
        artifacts.append(
            {
                "n_candidates": sampling["candidate_actions"],
                "n_states": sampling["states_per_trajectory"],
                "path": artifact.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "trajectory_seed": seed,
            }
        )
    reference = registry["offline_reference_policy"]
    payload = {
        "artifacts": artifacts,
        "continuation_policy": {
            "checkpoint": "D:/fixture/reference.pt",
            "checkpoint_sha256": reference["checkpoint_sha256"],
            "gamma": reference["gamma"],
            "name": reference["name"],
            "planning_horizon": reference["planning_horizon"],
            "top_k": reference["top_k"],
        },
        "horizons": registry["horizons"],
        "partition": partition,
        "protocol_id": registry["protocol_id"],
        "schema_version": 1,
        "trajectory_seeds": list(seeds),
    }
    payload["continuation_policy"]["name"] = continuation
    payload["manifest_digest"] = _manifest_digest(payload)
    path = root / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_input_audit_accepts_matching_train_and_calibration_manifests(tmp_path):
    registry = load_registry()
    train = _write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = _write_manifest(
        tmp_path / "calibration",
        registry,
        "calibration",
        range(2000, 2020),
    )

    report = audit_pcc_inputs(registry, train, calibration)

    assert report["passed"] is True
    assert report["continuation_policy"] == "paper9_mpc"
    assert report["train"]["artifact_count"] == 8
    assert report["calibration"]["artifact_count"] == 20


def test_input_audit_rejects_continuation_mismatch(tmp_path):
    registry = load_registry()
    train = _write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = _write_manifest(
        tmp_path / "calibration",
        registry,
        "calibration",
        range(2000, 2020),
        continuation="random",
    )

    with pytest.raises(ValueError, match="continuation"):
        audit_pcc_inputs(registry, train, calibration)


def test_input_audit_rejects_tampered_artifact(tmp_path):
    registry = load_registry()
    train = _write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = _write_manifest(
        tmp_path / "calibration",
        registry,
        "calibration",
        range(2000, 2020),
    )
    (train.parent / "seed_1000" / "trajectory_1000.npz").write_bytes(b"tampered")

    with pytest.raises(ValueError, match="artifact digest"):
        audit_pcc_inputs(registry, train, calibration)


def test_input_audit_rejects_artifact_path_outside_manifest_root(tmp_path):
    registry = load_registry()
    train = _write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = _write_manifest(
        tmp_path / "calibration",
        registry,
        "calibration",
        range(2000, 2020),
    )
    payload = json.loads(train.read_text(encoding="utf-8"))
    payload["artifacts"][0]["path"] = "../outside.npz"
    payload["manifest_digest"] = _manifest_digest(payload)
    train.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="outside manifest root"):
        audit_pcc_inputs(registry, train, calibration)


def test_input_audit_cli_writes_json_and_markdown(tmp_path):
    registry = load_registry()
    train = _write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = _write_manifest(
        tmp_path / "calibration",
        registry,
        "calibration",
        range(2000, 2020),
    )
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"

    main(
        [
            "--registry",
            str(registry_path),
            "--train-manifest",
            str(train),
            "--calibration-manifest",
            str(calibration),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ]
    )

    report = json.loads(output_json.read_text(encoding="utf-8"))
    assert report["passed"] is True
    markdown = output_md.read_text(encoding="utf-8")
    assert "Paper9 MPC" in markdown
    assert "1000-1007" in markdown
    assert "2000-2019" in markdown
