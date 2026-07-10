import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


@dataclass(frozen=True)
class JointPairedCalibrator:
    coverage: float
    q_joint: float
    trajectory_ids: np.ndarray
    trajectory_scores: np.ndarray
    objective_names: tuple[str, ...]
    protocol_id: str | None = None
    calibration_seeds: tuple[int, ...] = ()

    def lower_bounds(
        self,
        mean_delta,
        scale,
        online_multiplier=1.0,
    ) -> np.ndarray:
        mean_delta = np.asarray(mean_delta, dtype=np.float64)
        scale = np.asarray(scale, dtype=np.float64)
        multiplier = np.asarray(online_multiplier, dtype=np.float64)
        if not np.isfinite(mean_delta).all() or not np.isfinite(scale).all():
            raise ValueError("mean_delta and scale must be finite")
        if np.any(scale <= 0.0):
            raise ValueError("scale must be strictly positive")
        if not np.isfinite(multiplier).all() or np.any(multiplier < 1.0):
            raise ValueError("online multiplier must be finite and at least 1")
        return mean_delta - self.q_joint * scale * multiplier


def _validated_arrays(target_delta, predicted_delta, scale, trajectory_ids):
    target = np.asarray(target_delta, dtype=np.float64)
    predicted = np.asarray(predicted_delta, dtype=np.float64)
    uncertainty = np.asarray(scale, dtype=np.float64)
    ids = np.asarray(trajectory_ids, dtype=np.int64).reshape(-1)
    if target.shape != predicted.shape or target.shape != uncertainty.shape:
        raise ValueError("target, predicted, and scale shape must match")
    if target.ndim < 2 or target.shape[0] != ids.shape[0]:
        raise ValueError("trajectory_ids shape must match the first data axis")
    if not (
        np.isfinite(target).all()
        and np.isfinite(predicted).all()
        and np.isfinite(uncertainty).all()
    ):
        raise ValueError("calibration arrays must be finite")
    if np.any(uncertainty <= 0.0):
        raise ValueError("calibration scale must be strictly positive")
    if ids.size == 0:
        raise ValueError("calibration requires at least one trajectory")
    return target, predicted, uncertainty, ids


def _trajectory_scores(target, predicted, scale, trajectory_ids):
    normalized = np.abs(target - predicted) / scale
    unique_ids = np.unique(trajectory_ids)
    scores = np.asarray(
        [normalized[trajectory_ids == value].max() for value in unique_ids],
        dtype=np.float64,
    )
    return unique_ids, scores


def fit_joint_calibrator(
    target_delta,
    predicted_delta,
    scale,
    trajectory_ids,
    coverage: float,
    objective_names: Sequence[str] = OBJECTIVE_NAMES,
    protocol_id: str | None = None,
    calibration_seeds: Sequence[int] = (),
) -> JointPairedCalibrator:
    if not 0.0 < float(coverage) < 1.0:
        raise ValueError("coverage must be in (0, 1)")
    target, predicted, uncertainty, ids = _validated_arrays(
        target_delta,
        predicted_delta,
        scale,
        trajectory_ids,
    )
    unique_ids, scores = _trajectory_scores(
        target,
        predicted,
        uncertainty,
        ids,
    )
    rank = min(
        len(scores),
        math.ceil((len(scores) + 1) * float(coverage)),
    )
    q_joint = float(np.partition(scores, rank - 1)[rank - 1])
    return JointPairedCalibrator(
        coverage=float(coverage),
        q_joint=q_joint,
        trajectory_ids=unique_ids,
        trajectory_scores=scores,
        objective_names=tuple(str(value) for value in objective_names),
        protocol_id=None if protocol_id is None else str(protocol_id),
        calibration_seeds=tuple(int(value) for value in calibration_seeds),
    )


def audit_joint_coverage(
    calibrator: JointPairedCalibrator,
    target_delta,
    predicted_delta,
    scale,
    trajectory_ids,
) -> dict[str, float | int]:
    target, predicted, uncertainty, ids = _validated_arrays(
        target_delta,
        predicted_delta,
        scale,
        trajectory_ids,
    )
    unique_ids, scores = _trajectory_scores(
        target,
        predicted,
        uncertainty,
        ids,
    )
    covered = scores <= float(calibrator.q_joint)
    return {
        "n_trajectories": int(len(unique_ids)),
        "covered_trajectories": int(covered.sum()),
        "joint_coverage": float(covered.mean()),
        "target_coverage": float(calibrator.coverage),
    }


def _payload(calibrator: JointPairedCalibrator) -> dict[str, object]:
    return {
        "schema_version": 1,
        "coverage": float(calibrator.coverage),
        "q_joint": float(calibrator.q_joint),
        "trajectory_ids": calibrator.trajectory_ids.astype(int).tolist(),
        "trajectory_scores": calibrator.trajectory_scores.astype(float).tolist(),
        "objective_names": list(calibrator.objective_names),
        "protocol_id": calibrator.protocol_id,
        "calibration_seeds": list(calibrator.calibration_seeds),
    }


def _digest(payload: dict[str, object]) -> str:
    clean = {
        key: value for key, value in payload.items() if key != "calibrator_digest"
    }
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def save_joint_calibrator(
    path: str | Path,
    calibrator: JointPairedCalibrator,
) -> dict[str, object]:
    payload = _payload(calibrator)
    payload["calibrator_digest"] = _digest(payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def load_joint_calibrator(path: str | Path) -> JointPairedCalibrator:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = payload.get("calibrator_digest")
    observed = _digest(payload)
    if not isinstance(expected, str) or expected != observed:
        raise ValueError("calibrator digest mismatch")
    objective_names = tuple(payload["objective_names"])
    if objective_names != OBJECTIVE_NAMES:
        raise ValueError("calibrator objective order mismatch")
    return JointPairedCalibrator(
        coverage=float(payload["coverage"]),
        q_joint=float(payload["q_joint"]),
        trajectory_ids=np.asarray(payload["trajectory_ids"], dtype=np.int64),
        trajectory_scores=np.asarray(
            payload["trajectory_scores"],
            dtype=np.float64,
        ),
        objective_names=objective_names,
        protocol_id=payload.get("protocol_id"),
        calibration_seeds=tuple(
            int(value) for value in payload.get("calibration_seeds", [])
        ),
    )
