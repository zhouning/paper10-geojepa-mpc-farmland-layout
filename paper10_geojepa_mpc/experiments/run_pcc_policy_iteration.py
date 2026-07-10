import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


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


def run_two_round_policy_iteration(
    *,
    rounds: int,
    round0_train_labels,
    round0_calibration_labels,
    round1_checkpoints,
    validate_labels: Callable,
    calibrate: Callable,
    generate_labels: Callable,
    train: Callable,
) -> dict[str, object]:
    if int(rounds) != 2:
        raise ValueError("PCC requires exactly two policy-improvement rounds")

    validate_labels(1, round0_train_labels)
    round1_calibrator = calibrate(
        1,
        round0_calibration_labels,
        round1_checkpoints,
    )
    round2_train_labels = generate_labels(
        "train_labels",
        2,
        "pcc_round1",
        dict(ROUND1_LABEL_POLICY_CONFIG),
    )
    round2_calibration_labels = generate_labels(
        "calibration_labels",
        2,
        "pcc_round1",
        dict(ROUND1_LABEL_POLICY_CONFIG),
    )
    round2_checkpoints = train(
        2,
        round2_train_labels,
        {
            "round1_checkpoints": round1_checkpoints,
            "round1_calibrator": round1_calibrator,
        },
    )
    round2_calibrator = calibrate(
        2,
        round2_calibration_labels,
        round2_checkpoints,
    )
    return {
        "round1_calibrator": round1_calibrator,
        "round2_train_labels": round2_train_labels,
        "round2_calibration_labels": round2_calibration_labels,
        "round2_checkpoints": round2_checkpoints,
        "round2_calibrator": round2_calibrator,
    }


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
    round_index: int,
    parent_digest: str,
    train_labels_digest: str,
    calibration_labels_digest: str,
    checkpoint_digests: list[str],
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
    payload: dict[str, object] = {
        "schema_version": 1,
        "round_index": int(round_index),
        "parent_digest": str(parent_digest),
        "train_labels_digest": str(train_labels_digest),
        "calibration_labels_digest": str(calibration_labels_digest),
        "checkpoint_digests": list(checkpoint_digests),
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
    return observed
