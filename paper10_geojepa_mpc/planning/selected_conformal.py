import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)
from paper10_geojepa_mpc.models.pcc_paired_delta import HORIZONS


@dataclass(frozen=True)
class SelectedPlanningCalibrator:
    coverage: float
    q_planning: float
    finite_sample_rank: int
    planning_horizon: int
    trajectory_ids: np.ndarray
    trajectory_scores: np.ndarray
    model_seed: int
    ensemble_size: int
    policy_round: int
    compute_mode: str
    checkpoint_digests: tuple[str, ...]
    selected_labels_manifest_digest: str
    candidate_generator_digest: str
    base_selector_digest: str
    protocol_id: str = "pcc_v1_1"


def selected_trajectory_scores(
    true_delta,
    predicted_delta,
    scale,
    *,
    trajectory_ids,
    planning_horizon_index: int,
    epsilon: float = 1e-6,
) -> np.ndarray:
    true = np.asarray(true_delta, dtype=np.float64)
    predicted = np.asarray(predicted_delta, dtype=np.float64)
    uncertainty = np.asarray(scale, dtype=np.float64)
    ids = np.asarray(trajectory_ids, dtype=np.int64).reshape(-1)
    expected_tail = (len(HORIZONS), 4)
    if (
        true.shape != predicted.shape
        or true.shape != uncertainty.shape
        or true.ndim != 3
        or true.shape[1:] != expected_tail
    ):
        raise ValueError(
            "selected calibration arrays must share shape [states, 3, 4]"
        )
    if true.shape[0] != ids.size or ids.size == 0:
        raise ValueError("trajectory IDs must align with selected state rows")
    if not all(
        np.isfinite(value).all()
        for value in (true, predicted, uncertainty)
    ):
        raise ValueError("selected calibration arrays must be finite")
    if np.any(uncertainty < 0.0):
        raise ValueError("selected calibration scale must be non-negative")
    if not 0 <= int(planning_horizon_index) < len(HORIZONS):
        raise ValueError("planning horizon index is out of range")
    if not np.isfinite(epsilon) or float(epsilon) <= 0.0:
        raise ValueError("epsilon must be finite and positive")

    horizon = int(planning_horizon_index)
    normalized_overprediction = (
        predicted[:, horizon, 1:] - true[:, horizon, 1:]
    ) / np.maximum(uncertainty[:, horizon, 1:], float(epsilon))
    state_scores = np.maximum(normalized_overprediction, 0.0).max(axis=1)
    unique_ids = np.unique(ids)
    return np.asarray(
        [state_scores[ids == trajectory_id].max() for trajectory_id in unique_ids],
        dtype=np.float64,
    )


def _is_sha256(value) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _validated_lineage(lineage) -> dict[str, object]:
    required = {
        "planning_horizon",
        "model_seed",
        "ensemble_size",
        "policy_round",
        "compute_mode",
        "checkpoint_digests",
        "selected_labels_manifest_digest",
        "candidate_generator_digest",
        "base_selector_digest",
    }
    if not isinstance(lineage, dict) or set(lineage) != required:
        raise ValueError("selected calibrator lineage fields mismatch")
    values = dict(lineage)
    values["planning_horizon"] = int(values["planning_horizon"])
    values["model_seed"] = int(values["model_seed"])
    values["ensemble_size"] = int(values["ensemble_size"])
    values["policy_round"] = int(values["policy_round"])
    values["compute_mode"] = str(values["compute_mode"])
    values["checkpoint_digests"] = tuple(
        str(value) for value in values["checkpoint_digests"]
    )
    if values["planning_horizon"] not in HORIZONS:
        raise ValueError("selected calibrator planning horizon is invalid")
    if min(
        values["model_seed"],
        values["ensemble_size"],
        values["policy_round"],
    ) <= 0:
        raise ValueError("selected calibrator lineage integers must be positive")
    if values["compute_mode"] not in {"matched", "full"}:
        raise ValueError("selected calibrator compute mode is invalid")
    if len(values["checkpoint_digests"]) != values["ensemble_size"] or not all(
        _is_sha256(value) for value in values["checkpoint_digests"]
    ):
        raise ValueError("selected calibrator checkpoint lineage is invalid")
    for field in (
        "selected_labels_manifest_digest",
        "candidate_generator_digest",
        "base_selector_digest",
    ):
        values[field] = str(values[field])
        if not _is_sha256(values[field]):
            raise ValueError(f"selected calibrator {field} is invalid")
    return values


def fit_selected_planning_calibrator(
    *,
    trajectory_scores,
    trajectory_ids,
    coverage: float,
    lineage,
) -> SelectedPlanningCalibrator:
    scores = np.asarray(trajectory_scores, dtype=np.float64).reshape(-1)
    ids = np.asarray(trajectory_ids, dtype=np.int64).reshape(-1)
    if not 0.0 < float(coverage) < 1.0:
        raise ValueError("coverage must be in (0, 1)")
    if scores.size == 0 or scores.shape != ids.shape:
        raise ValueError("trajectory scores and IDs must be non-empty and aligned")
    if np.unique(ids).size != ids.size:
        raise ValueError("calibrator inputs must contain one score per trajectory")
    if not np.isfinite(scores).all() or np.any(scores < 0.0):
        raise ValueError("trajectory scores must be finite and non-negative")
    lineage = _validated_lineage(lineage)
    rank = min(
        scores.size,
        math.ceil((scores.size + 1) * float(coverage)),
    )
    q_planning = float(np.sort(scores, kind="stable")[rank - 1])
    return SelectedPlanningCalibrator(
        coverage=float(coverage),
        q_planning=q_planning,
        finite_sample_rank=int(rank),
        planning_horizon=lineage["planning_horizon"],
        trajectory_ids=ids.copy(),
        trajectory_scores=scores.copy(),
        model_seed=lineage["model_seed"],
        ensemble_size=lineage["ensemble_size"],
        policy_round=lineage["policy_round"],
        compute_mode=lineage["compute_mode"],
        checkpoint_digests=lineage["checkpoint_digests"],
        selected_labels_manifest_digest=lineage[
            "selected_labels_manifest_digest"
        ],
        candidate_generator_digest=lineage["candidate_generator_digest"],
        base_selector_digest=lineage["base_selector_digest"],
    )


def audit_selected_coverage(
    calibrator: SelectedPlanningCalibrator,
    true_delta,
    predicted_delta,
    scale,
    *,
    trajectory_ids,
) -> dict[str, float | int]:
    horizon_index = HORIZONS.index(int(calibrator.planning_horizon))
    scores = selected_trajectory_scores(
        true_delta,
        predicted_delta,
        scale,
        trajectory_ids=trajectory_ids,
        planning_horizon_index=horizon_index,
    )
    covered = scores <= float(calibrator.q_planning)
    return {
        "n_trajectories": int(scores.size),
        "covered_trajectories": int(covered.sum()),
        "planning_coverage": float(covered.mean()),
        "target_coverage": float(calibrator.coverage),
    }


def _calibrator_payload(
    calibrator: SelectedPlanningCalibrator,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "protocol_id": calibrator.protocol_id,
        "coverage": float(calibrator.coverage),
        "q_planning": float(calibrator.q_planning),
        "finite_sample_rank": int(calibrator.finite_sample_rank),
        "planning_horizon": int(calibrator.planning_horizon),
        "trajectory_ids": calibrator.trajectory_ids.astype(int).tolist(),
        "trajectory_scores": calibrator.trajectory_scores.astype(float).tolist(),
        "model_seed": int(calibrator.model_seed),
        "ensemble_size": int(calibrator.ensemble_size),
        "policy_round": int(calibrator.policy_round),
        "compute_mode": calibrator.compute_mode,
        "checkpoint_digests": list(calibrator.checkpoint_digests),
        "selected_labels_manifest_digest": (
            calibrator.selected_labels_manifest_digest
        ),
        "candidate_generator_digest": calibrator.candidate_generator_digest,
        "base_selector_digest": calibrator.base_selector_digest,
    }


def _calibrator_digest(payload: dict[str, object]) -> str:
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


def save_selected_planning_calibrator(
    path: str | Path,
    calibrator: SelectedPlanningCalibrator,
) -> dict[str, object]:
    payload = _calibrator_payload(calibrator)
    payload["calibrator_digest"] = _calibrator_digest(payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def _payload_lineage(payload) -> dict[str, object]:
    return {
        "planning_horizon": payload["planning_horizon"],
        "model_seed": payload["model_seed"],
        "ensemble_size": payload["ensemble_size"],
        "policy_round": payload["policy_round"],
        "compute_mode": payload["compute_mode"],
        "checkpoint_digests": payload["checkpoint_digests"],
        "selected_labels_manifest_digest": payload[
            "selected_labels_manifest_digest"
        ],
        "candidate_generator_digest": payload["candidate_generator_digest"],
        "base_selector_digest": payload["base_selector_digest"],
    }


def load_selected_planning_calibrator(
    path: str | Path,
    *,
    expected_lineage=None,
) -> SelectedPlanningCalibrator:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    expected_digest = payload.get("calibrator_digest")
    if (
        not isinstance(expected_digest, str)
        or expected_digest != _calibrator_digest(payload)
    ):
        raise ValueError("selected calibrator digest mismatch")
    if payload.get("protocol_id") != "pcc_v1_1":
        raise ValueError("selected calibrator protocol mismatch")
    observed_lineage = _validated_lineage(_payload_lineage(payload))
    if expected_lineage is not None:
        expected = _validated_lineage(expected_lineage)
        if observed_lineage != expected:
            raise ValueError("selected calibrator lineage mismatch")
    fitted = fit_selected_planning_calibrator(
        trajectory_scores=payload["trajectory_scores"],
        trajectory_ids=payload["trajectory_ids"],
        coverage=payload["coverage"],
        lineage=observed_lineage,
    )
    if (
        int(payload.get("finite_sample_rank", -1))
        != fitted.finite_sample_rank
        or float(payload.get("q_planning", float("nan")))
        != fitted.q_planning
    ):
        raise ValueError("selected calibrator finite-sample quantile mismatch")
    return fitted


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_selected_manifest(path: str | Path):
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
    if not isinstance(expected, str) or expected != hashlib.sha256(
        canonical
    ).hexdigest():
        raise ValueError("selected-label manifest digest mismatch")
    if payload.get("protocol_id") != "pcc_v1_1":
        raise ValueError("selected-label manifest protocol mismatch")
    if payload.get("partition") != "calibration":
        raise ValueError("selected calibrator requires calibration labels")
    if not payload.get("artifacts"):
        raise ValueError("selected-label manifest has no artifacts")
    return path, payload


def fit_selected_calibrator_from_artifacts(
    selected_labels_manifest: str | Path,
    *,
    expected_registry_digest: str,
    checkpoint_digests,
    model_seed: int,
    ensemble_size: int,
    policy_round: int,
    planning_horizon: int,
    compute_mode: str,
    coverage: float,
    output_path: str | Path,
) -> SelectedPlanningCalibrator:
    manifest_path, manifest = _load_selected_manifest(
        selected_labels_manifest
    )
    checkpoint_digests = tuple(str(value) for value in checkpoint_digests)
    expected_fields = {
        "registry_digest": str(expected_registry_digest),
        "model_seed": int(model_seed),
        "ensemble_size": int(ensemble_size),
        "policy_round": int(policy_round),
        "compute_mode": str(compute_mode),
        "checkpoint_digests": list(checkpoint_digests),
    }
    if any(manifest.get(field) != value for field, value in expected_fields.items()):
        raise ValueError("selected-label lineage mismatch")
    trajectory_seeds = [int(value) for value in manifest["trajectory_seeds"]]
    if len(trajectory_seeds) != len(set(trajectory_seeds)):
        raise ValueError("selected-label trajectory seeds must be unique")
    if [
        int(artifact["trajectory_seed"])
        for artifact in manifest["artifacts"]
    ] != trajectory_seeds:
        raise ValueError("selected-label artifact seed order mismatch")

    true_rows = []
    predicted_rows = []
    scale_rows = []
    id_rows = []
    for artifact in manifest["artifacts"]:
        path = manifest_path.parent / str(artifact["path"])
        if _sha256_file(path) != str(artifact["sha256"]):
            raise ValueError(f"selected-label artifact digest mismatch: {path}")
        with np.load(path) as arrays:
            true = np.asarray(arrays["true_delta"], dtype=np.float64)
            predicted = np.asarray(
                arrays["predicted_delta"],
                dtype=np.float64,
            )
            scale = np.asarray(arrays["predicted_scale"], dtype=np.float64)
            ids = np.asarray(arrays["trajectory_ids"], dtype=np.int64)
        seed = int(artifact["trajectory_seed"])
        if ids.ndim != 1 or not np.all(ids == seed):
            raise ValueError("selected-label trajectory identity mismatch")
        true_rows.append(true)
        predicted_rows.append(predicted)
        scale_rows.append(scale)
        id_rows.append(ids)

    true = np.concatenate(true_rows, axis=0)
    predicted = np.concatenate(predicted_rows, axis=0)
    scale = np.concatenate(scale_rows, axis=0)
    row_ids = np.concatenate(id_rows, axis=0)
    planning_horizon = int(planning_horizon)
    if planning_horizon not in HORIZONS:
        raise ValueError("selected calibrator planning horizon is invalid")
    scores = selected_trajectory_scores(
        true,
        predicted,
        scale,
        trajectory_ids=row_ids,
        planning_horizon_index=HORIZONS.index(planning_horizon),
    )
    unique_ids = np.unique(row_ids)
    lineage = {
        "planning_horizon": planning_horizon,
        "model_seed": int(model_seed),
        "ensemble_size": int(ensemble_size),
        "policy_round": int(policy_round),
        "compute_mode": str(compute_mode),
        "checkpoint_digests": checkpoint_digests,
        "selected_labels_manifest_digest": manifest["manifest_digest"],
        "candidate_generator_digest": manifest["candidate_generator_digest"],
        "base_selector_digest": manifest["base_selector_digest"],
    }
    calibrator = fit_selected_planning_calibrator(
        trajectory_scores=scores,
        trajectory_ids=unique_ids,
        coverage=coverage,
        lineage=lineage,
    )
    save_selected_planning_calibrator(output_path, calibrator)
    return calibrator


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--selected-labels-manifest", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--ensemble-size", type=int, required=True)
    parser.add_argument("--policy-round", type=int, required=True)
    parser.add_argument("--planning-horizon", type=int, required=True)
    parser.add_argument(
        "--compute-mode",
        choices=("matched", "full"),
        required=True,
    )
    parser.add_argument("--coverage", type=float, required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def _validate_registry_request(registry, args) -> None:
    if (
        registry.get("protocol_id") != "pcc_v1_1"
        or registry.get("status") != "development"
    ):
        raise ValueError("selected calibration requires PCC v1.1 development")
    if int(args.model_seed) not in {
        int(value) for value in registry["model_seeds"]
    }:
        raise ValueError("selected calibrator model seed is outside the registry")
    if int(args.ensemble_size) != int(registry["viability"]["ensemble_size"]):
        raise ValueError("selected calibrator ensemble size mismatch")
    if int(args.policy_round) != int(registry["viability"]["policy_round"]):
        raise ValueError("selected calibrator policy round mismatch")
    if float(args.coverage) not in {
        float(value) for value in registry["selected_conformal"]["coverages"]
    }:
        raise ValueError("selected calibrator coverage is outside the registry")
    if int(args.planning_horizon) not in HORIZONS:
        raise ValueError("selected calibrator planning horizon is invalid")


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    _validate_registry_request(registry, args)
    checkpoint_root = Path(args.checkpoint_root)
    checkpoint_paths = sorted(checkpoint_root.glob("member_*.pt"))
    if len(checkpoint_paths) != int(args.ensemble_size):
        raise ValueError("selected calibrator checkpoint inventory is incomplete")
    checkpoint_digests = [_sha256_file(path) for path in checkpoint_paths]
    output_path = Path(args.output_dir) / "calibrator.json"
    calibrator = fit_selected_calibrator_from_artifacts(
        args.selected_labels_manifest,
        expected_registry_digest=_sha256_file(args.registry),
        checkpoint_digests=checkpoint_digests,
        model_seed=args.model_seed,
        ensemble_size=args.ensemble_size,
        policy_round=args.policy_round,
        planning_horizon=args.planning_horizon,
        compute_mode=args.compute_mode,
        coverage=args.coverage,
        output_path=output_path,
    )
    summary = {
        "protocol_id": calibrator.protocol_id,
        "coverage": calibrator.coverage,
        "q_planning": calibrator.q_planning,
        "finite_sample_rank": calibrator.finite_sample_rank,
        "n_calibration_trajectories": int(calibrator.trajectory_ids.size),
        "output": str(output_path.resolve()),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
