import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROUND1_LABEL_POLICY_CONFIG = {
    "ensemble_size": 3,
    "joint_coverage": 0.90,
    "tolerance_scale": 0.05,
    "planning_horizon": 3,
    "executed_feedback": False,
    "reference_policy": "paper9_mpc",
}


@dataclass(frozen=True)
class PolicyRound:
    round_index: int
    label_policy: str
    parent_digest: str | None

    def __post_init__(self):
        if self.round_index not in {0, 1, 2}:
            raise ValueError("PCC uses exactly two policy-improvement rounds")
        if self.round_index == 0 and self.parent_digest is not None:
            raise ValueError("round 0 cannot have a parent digest")
        if self.round_index > 0 and not self.parent_digest:
            raise ValueError("improvement rounds require a parent digest")


def build_policy_rounds(reference_policy: str) -> tuple[PolicyRound, ...]:
    return (
        PolicyRound(0, str(reference_policy), None),
        PolicyRound(1, "pcc_round1", "resolved_after_round0"),
        PolicyRound(2, "pcc_round2", "resolved_after_round1"),
    )


def _canonical(payload: dict[str, object]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "round_digest"}
    return json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _round_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def write_round_manifest(
    path: str | Path,
    *,
    model_seed: int,
    round_index: int,
    parent_digest: str,
    train_labels_digest: str,
    calibration_labels_digest: str,
    checkpoint_digests: list[str],
    calibrator_digest: str,
    continuation_policy: dict[str, object],
) -> dict[str, object]:
    PolicyRound(
        round_index=int(round_index),
        label_policy=f"pcc_round{int(round_index)}",
        parent_digest=str(parent_digest),
    )
    if len(checkpoint_digests) == 0 or len(set(checkpoint_digests)) != len(
        checkpoint_digests
    ):
        raise ValueError("checkpoint digests must be non-empty and distinct")
    if not str(calibrator_digest):
        raise ValueError("calibrator digest is required")
    payload: dict[str, object] = {
        "schema_version": 1,
        "model_seed": int(model_seed),
        "round_index": int(round_index),
        "parent_digest": str(parent_digest),
        "train_labels_digest": str(train_labels_digest),
        "calibration_labels_digest": str(calibration_labels_digest),
        "checkpoint_digests": list(checkpoint_digests),
        "calibrator_digest": str(calibrator_digest),
        "continuation_policy": dict(continuation_policy),
    }
    payload["round_digest"] = _round_digest(payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def verify_round_manifest(payload: dict[str, object]) -> str:
    expected = payload.get("round_digest")
    observed = _round_digest(payload)
    if not isinstance(expected, str) or observed != expected:
        raise ValueError("policy round digest mismatch")
    PolicyRound(
        round_index=int(payload["round_index"]),
        label_policy=f"pcc_round{int(payload['round_index'])}",
        parent_digest=str(payload["parent_digest"]),
    )
    int(payload["model_seed"])
    if not str(payload.get("calibrator_digest", "")):
        raise ValueError("policy round calibrator digest is missing")
    return observed


def verify_policy_iteration_root(
    input_root: str | Path,
    *,
    registry: dict[str, object],
) -> dict[str, object]:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        validate_registry,
        verify_frozen_registry,
    )
    from paper10_geojepa_mpc.planning.paired_conformal import (
        load_joint_calibrator,
    )

    validate_registry(registry)
    if registry.get("status") == "frozen":
        verify_frozen_registry(registry)
    root = Path(input_root)
    if not root.is_dir():
        raise FileNotFoundError(f"policy iteration root does not exist: {root}")
    if list(root.rglob("round3")) or list(root.rglob("*round3*.json")):
        raise ValueError("round 3 artifact is forbidden")

    expected_calibration = tuple(
        map(int, registry["partitions"]["calibration"])
    )
    seen_checkpoint_digests = set()
    rows = []
    for model_seed in map(int, registry["model_seeds"]):
        parent_digest = str(
            registry["offline_reference_policy"]["checkpoint_sha256"]
        )
        for round_index in (1, 2):
            round_root = root / f"seed_{model_seed}" / f"round{round_index}"
            manifest_path = round_root / "round_manifest.json"
            if not manifest_path.exists():
                raise ValueError(
                    f"policy iteration round manifest is missing: {manifest_path}"
                )
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            round_digest = verify_round_manifest(payload)
            if int(payload["round_index"]) != round_index:
                raise ValueError("policy iteration round index mismatch")
            if int(payload["model_seed"]) != model_seed:
                raise ValueError("policy iteration model seed mismatch")
            if str(payload["parent_digest"]) != parent_digest:
                raise ValueError("policy iteration parent digest mismatch")
            checkpoint_digests = [
                str(value) for value in payload["checkpoint_digests"]
            ]
            if seen_checkpoint_digests & set(checkpoint_digests):
                raise ValueError("checkpoint digest reused across policy rounds")
            seen_checkpoint_digests.update(checkpoint_digests)

            calibrator_path = round_root / "calibration" / "calibrator.json"
            calibrator_payload = json.loads(
                calibrator_path.read_text(encoding="utf-8")
            )
            if calibrator_payload.get("calibrator_digest") != payload.get(
                "calibrator_digest"
            ):
                raise ValueError("policy round calibrator lineage mismatch")
            calibrator = load_joint_calibrator(calibrator_path)
            if tuple(calibrator.calibration_seeds) != expected_calibration:
                raise ValueError("policy round calibration seed block mismatch")
            if calibrator.labels_manifest_digest != str(
                payload["calibration_labels_digest"]
            ):
                raise ValueError("policy round calibration label lineage mismatch")
            if tuple(calibrator.checkpoint_digests) != tuple(checkpoint_digests):
                raise ValueError("policy round calibration checkpoint lineage mismatch")
            if (
                len(calibrator.trajectory_scores) != len(expected_calibration)
                or not np.isfinite(calibrator.trajectory_scores).all()
                or not np.isfinite(calibrator.q_joint)
            ):
                raise ValueError("policy round calibration artifact is incomplete")
            expected_policy = "paper9_mpc" if round_index == 1 else "pcc_round1"
            if payload["continuation_policy"].get("name") != expected_policy:
                raise ValueError("policy round continuation policy mismatch")
            rows.append(
                {
                    "model_seed": model_seed,
                    "round_index": round_index,
                    "round_digest": round_digest,
                    "calibrator_digest": calibrator_payload[
                        "calibrator_digest"
                    ],
                    "n_calibration_trajectories": len(
                        calibrator.trajectory_scores
                    ),
                }
            )
            parent_digest = round_digest
    return {
        "passed": True,
        "protocol_id": registry["protocol_id"],
        "model_seeds": [int(value) for value in registry["model_seeds"]],
        "rounds": rows,
    }
