import argparse
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_label_manifest(path: str | Path) -> tuple[Path, dict[str, object]]:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = payload.get("manifest_digest")
    clean = {key: value for key, value in payload.items() if key != "manifest_digest"}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    if expected != hashlib.sha256(canonical).hexdigest():
        raise ValueError("label manifest digest mismatch")
    if "confirmation" in str(payload.get("partition", "")).lower():
        raise ValueError("confirmation labels cannot fit a calibrator")
    return path, payload


def fit_calibrator_from_artifacts(
    labels_manifest: str | Path,
    *,
    ensemble,
    coverage: float,
    output_path: str | Path,
    device: str = "cpu",
) -> JointPairedCalibrator:
    from paper10_geojepa_mpc.planning.pcc_selector import (
        predict_paired_ensemble_all_horizons,
    )

    manifest_path, manifest = _load_label_manifest(labels_manifest)
    target_rows = []
    predicted_rows = []
    scale_rows = []
    trajectory_rows = []
    calibration_seeds = []
    for artifact in manifest["artifacts"]:
        path = manifest_path.parent / str(artifact["path"])
        if _sha256_file(path) != artifact["sha256"]:
            raise ValueError(f"label artifact digest mismatch: {path}")
        with np.load(path) as data:
            arrays = {key: data[key].copy() for key in data.files}
        trajectory_seed = int(artifact["trajectory_seed"])
        calibration_seeds.append(trajectory_seed)
        if not np.all(arrays["trajectory_ids"] == trajectory_seed):
            raise ValueError("trajectory identity mismatch in calibration labels")
        n_states, n_candidates = arrays["actions"].shape
        for state_index in range(n_states):
            candidate_actions = np.asarray(
                arrays["actions"][state_index],
                dtype=np.int64,
            )
            reference_action = int(arrays["reference_actions"][state_index])
            pool = np.asarray(
                list(
                    dict.fromkeys(
                        [reference_action, *candidate_actions.astype(int).tolist()]
                    )
                ),
                dtype=np.int64,
            )
            prediction = predict_paired_ensemble_all_horizons(
                ensemble,
                block_features=arrays["states_bf"][state_index],
                neighbour_features=arrays["states_neighbor_bf"][state_index],
                global_features=arrays["states_gf"][state_index],
                actions=pool,
                reference_action=reference_action,
                device=device,
            )
            index_by_action = {
                int(action): index for index, action in enumerate(prediction.actions)
            }
            indexes = np.asarray(
                [index_by_action[int(action)] for action in candidate_actions],
                dtype=np.int64,
            )
            target_delta = (
                arrays["objective_returns"][state_index]
                - arrays["reference_objective_returns"][state_index]
            )
            if target_delta.shape != (n_candidates, 3, 4):
                raise ValueError("calibration objective label shape mismatch")
            target_rows.append(target_delta)
            predicted_rows.append(prediction.mean_delta[indexes])
            scale_rows.append(prediction.paired_scale[indexes])
            trajectory_rows.append(
                np.full(n_candidates, trajectory_seed, dtype=np.int64)
            )

    target = np.concatenate(target_rows, axis=0)
    predicted = np.concatenate(predicted_rows, axis=0)
    scale = np.concatenate(scale_rows, axis=0)
    trajectory_ids = np.concatenate(trajectory_rows, axis=0)
    calibrator = fit_joint_calibrator(
        target,
        predicted,
        scale,
        trajectory_ids,
        coverage=coverage,
        protocol_id=str(manifest["protocol_id"]),
        calibration_seeds=sorted(set(calibration_seeds)),
    )
    save_joint_calibrator(output_path, calibrator)
    return calibrator


def _resolve_coverage(registry, explicit: float | None, from_frozen: bool) -> float:
    if from_frozen:
        if explicit is not None or registry.get("status") != "frozen":
            raise ValueError("frozen coverage requires a frozen registry and no override")
        return float(registry["selected_config"]["joint_coverage"])
    if explicit is None:
        raise ValueError("--coverage is required during development")
    declared = {float(value) for value in registry["grid"]["joint_coverage"]}
    if float(explicit) not in declared:
        raise ValueError("coverage is outside the declared development grid")
    return float(explicit)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--labels-manifest", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--coverage", type=float, default=None)
    parser.add_argument("--coverage-from-frozen-registry", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
        validate_registry,
        verify_frozen_registry,
    )
    from paper10_geojepa_mpc.planning.pcc_selector import load_pcc_ensemble

    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    if registry.get("status") == "frozen":
        verify_frozen_registry(registry)
    coverage = _resolve_coverage(
        registry,
        args.coverage,
        args.coverage_from_frozen_registry,
    )
    ensemble = load_pcc_ensemble(args.checkpoint_root, device=args.device)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    calibrator = fit_calibrator_from_artifacts(
        args.labels_manifest,
        ensemble=ensemble,
        coverage=coverage,
        output_path=output_dir / "calibrator.json",
        device=args.device,
    )
    print(
        json.dumps(
            {
                "coverage": calibrator.coverage,
                "q_joint": calibrator.q_joint,
                "n_calibration_trajectories": len(calibrator.trajectory_ids),
                "output": str(output_dir / "calibrator.json"),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
