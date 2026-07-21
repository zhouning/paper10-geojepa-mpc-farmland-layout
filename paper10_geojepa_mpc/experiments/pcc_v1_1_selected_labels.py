import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    derive_continuation_seed,
    evaluate_paired_objectives,
)
from paper10_geojepa_mpc.models.pcc_paired_delta import HORIZONS


_SELECTED_LINEAGE_FIELDS = {
    "protocol_id",
    "registry_digest",
    "partition",
    "model_seed",
    "ensemble_size",
    "policy_round",
    "compute_mode",
    "checkpoint_digests",
    "candidate_generator_digest",
    "base_selector_digest",
    "reference_checkpoint_digest",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _validated_lineage(lineage: object) -> dict[str, object]:
    if not isinstance(lineage, dict) or set(lineage) != _SELECTED_LINEAGE_FIELDS:
        raise ValueError("selected-label lineage fields mismatch")
    values = dict(lineage)
    values["protocol_id"] = str(values["protocol_id"])
    values["registry_digest"] = str(values["registry_digest"])
    values["partition"] = str(values["partition"])
    values["model_seed"] = int(values["model_seed"])
    values["ensemble_size"] = int(values["ensemble_size"])
    values["policy_round"] = int(values["policy_round"])
    values["compute_mode"] = str(values["compute_mode"])
    values["checkpoint_digests"] = [
        str(value) for value in values["checkpoint_digests"]
    ]
    for field in (
        "candidate_generator_digest",
        "base_selector_digest",
        "reference_checkpoint_digest",
    ):
        values[field] = str(values[field])

    if "confirmation" in values["partition"].lower():
        raise ValueError("confirmation partitions cannot produce selected labels")
    if values["partition"] not in {"calibration", "development"}:
        raise ValueError("selected-label partition must be calibration or development")
    if values["protocol_id"] != "pcc_v1_1":
        raise ValueError("selected-label protocol lineage is invalid")
    if min(
        values["model_seed"],
        values["ensemble_size"],
        values["policy_round"],
    ) <= 0:
        raise ValueError("selected-label lineage integers must be positive")
    if values["compute_mode"] not in {"matched", "full"}:
        raise ValueError("selected-label compute mode is invalid")
    if (
        len(values["checkpoint_digests"]) != values["ensemble_size"]
        or not all(_is_sha256(value) for value in values["checkpoint_digests"])
    ):
        raise ValueError("selected-label checkpoint lineage is invalid")
    for field in (
        "registry_digest",
        "candidate_generator_digest",
        "base_selector_digest",
        "reference_checkpoint_digest",
    ):
        if not _is_sha256(values[field]):
            raise ValueError(f"selected-label {field} lineage is invalid")
    return values


def _validated_artifact(
    root: Path,
    artifact: object,
    *,
    expected_seed: int | None = None,
) -> dict[str, object]:
    required = {"trajectory_seed", "path", "sha256", "n_states"}
    if not isinstance(artifact, dict) or set(artifact) != required:
        raise ValueError("selected-label artifact fields mismatch")
    row = dict(artifact)
    seed = int(row["trajectory_seed"])
    n_states = int(row["n_states"])
    if expected_seed is not None and seed != int(expected_seed):
        raise ValueError("selected-label artifact seed mismatch")
    if seed < 0 or n_states <= 0 or not _is_sha256(row["sha256"]):
        raise ValueError("selected-label artifact metadata is invalid")
    relative = Path(str(row["path"]))
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("selected-label artifact path is invalid")
    path = root / relative
    if not path.is_file() or _sha256_file(path) != row["sha256"]:
        raise ValueError("selected-label artifact digest mismatch")
    try:
        with np.load(path, allow_pickle=False) as data:
            trajectory_ids = np.asarray(data["trajectory_ids"], dtype=np.int64)
            if trajectory_ids.shape != (n_states,) or not np.all(
                trajectory_ids == seed
            ):
                raise ValueError("selected-label artifact trajectory identity mismatch")
    except (OSError, KeyError, ValueError) as exc:
        if isinstance(exc, ValueError) and "selected-label" in str(exc):
            raise
        raise ValueError("selected-label artifact trajectory identity mismatch") from exc
    return {
        "trajectory_seed": seed,
        "path": relative.as_posix(),
        "sha256": str(row["sha256"]),
        "n_states": n_states,
    }


def write_selected_trajectory_artifact(
    output_root: str | Path,
    trajectory_seed: int,
    dataset: dict[str, np.ndarray],
) -> dict[str, object]:
    trajectory_seed = int(trajectory_seed)
    if "trajectory_ids" not in dataset:
        raise ValueError("selected-label dataset requires trajectory IDs")
    trajectory_ids = np.asarray(dataset["trajectory_ids"], dtype=np.int64)
    if (
        trajectory_ids.ndim != 1
        or trajectory_ids.size == 0
        or not np.all(trajectory_ids == trajectory_seed)
    ):
        raise ValueError("selected-label dataset trajectory identity mismatch")
    n_states = int(trajectory_ids.size)
    if any(np.asarray(value).shape[0] != n_states for value in dataset.values()):
        raise ValueError("selected-label dataset arrays must align by state")

    output_root = Path(output_root)
    seed_dir = output_root / f"seed_{trajectory_seed}"
    seed_dir.mkdir(parents=True, exist_ok=True)
    path = seed_dir / f"trajectory_{trajectory_seed}.npz"
    temporary = path.with_suffix(".tmp.npz")
    np.savez_compressed(temporary, **dataset)
    temporary.replace(path)
    return {
        "trajectory_seed": trajectory_seed,
        "path": path.relative_to(output_root).as_posix(),
        "sha256": _sha256_file(path),
        "n_states": n_states,
    }


def write_selected_manifest(
    output_root: str | Path,
    *,
    lineage: dict[str, object],
    artifacts: Sequence[dict[str, object]],
) -> dict[str, object]:
    lineage = _validated_lineage(lineage)
    if not artifacts:
        raise ValueError("at least one selected-label artifact is required")
    output_root = Path(output_root)
    ordered = sorted(artifacts, key=lambda row: int(row["trajectory_seed"]))
    validated = [
        _validated_artifact(output_root, row) for row in ordered
    ]
    seeds = [int(row["trajectory_seed"]) for row in validated]
    if len(seeds) != len(set(seeds)):
        raise ValueError("selected-label artifact seeds must be unique")
    payload: dict[str, object] = {
        "schema_version": 1,
        **lineage,
        "trajectory_seeds": seeds,
        "artifacts": validated,
    }
    payload["manifest_digest"] = _manifest_digest(payload)

    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "manifest.json"
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("existing selected-label manifest is invalid") from exc
        if existing != payload:
            raise ValueError("refusing to overwrite selected-label manifest")
        return payload
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def load_resumable_selected_manifest(
    path: str | Path,
    *,
    expected_lineage: dict[str, object],
) -> dict[str, object]:
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("selected-label manifest is unreadable") from exc
    if payload.get("manifest_digest") != _manifest_digest(payload):
        raise ValueError("selected-label manifest digest mismatch")
    expected = _validated_lineage(expected_lineage)
    observed = {field: payload.get(field) for field in _SELECTED_LINEAGE_FIELDS}
    if observed != expected:
        raise ValueError("selected-label manifest lineage mismatch")
    if payload.get("schema_version") != 1 or "coverage" in payload:
        raise ValueError("selected-label manifest schema is invalid")

    seeds = payload.get("trajectory_seeds")
    artifacts = payload.get("artifacts")
    if (
        not isinstance(seeds, list)
        or not isinstance(artifacts, list)
        or len(seeds) == 0
        or len(seeds) != len(artifacts)
        or seeds != sorted(seeds)
        or len(seeds) != len(set(seeds))
    ):
        raise ValueError("selected-label manifest artifact order mismatch")
    validated = [
        _validated_artifact(path.parent, row, expected_seed=int(seed))
        for seed, row in zip(seeds, artifacts)
    ]
    if validated != artifacts:
        raise ValueError("selected-label manifest artifact metadata mismatch")
    return payload


def generate_selected_label_trajectory(
    *,
    env,
    trajectory_seed: int,
    n_states: int,
    horizons: Sequence[int],
    gamma: float,
    base_policy,
    continuation_policy,
    metric_reader,
    state_attrs: Sequence[str] | None = None,
) -> dict[str, np.ndarray]:
    if int(n_states) <= 0:
        raise ValueError("n_states must be positive")
    horizons = tuple(int(value) for value in horizons)
    if horizons != HORIZONS:
        raise ValueError("selected labels require horizons 1, 3, and 5")
    if not 0.0 <= float(gamma) <= 1.0:
        raise ValueError("gamma must be in [0, 1]")
    trajectory_seed = int(trajectory_seed)
    rng = np.random.default_rng(trajectory_seed)
    env.reset(seed=trajectory_seed)

    selected_actions = []
    reference_actions = []
    predicted_delta = []
    predicted_scale = []
    true_delta = []
    probabilities = []
    reasons = []
    state_steps = []
    continuation_seeds = []
    for _ in range(int(n_states)):
        executable_mask = np.asarray(env.action_masks(), dtype=bool).reshape(-1)
        if not executable_mask.any():
            break
        state_step = int(getattr(env, "step_count", len(state_steps)))
        selected_action, info = base_policy(env, rng)
        selected_action = int(selected_action)
        reference_action = int(info["reference_action"])
        if int(info.get("base_selected_action", -1)) != selected_action:
            raise ValueError("base policy selected-action metadata mismatch")
        if int(info.get("unexecuted_real_reward_queries", -1)) != 0:
            raise ValueError(
                "selected labels forbid unexecuted real-reward queries"
            )
        for name, action in (
            ("selected", selected_action),
            ("reference", reference_action),
        ):
            if (
                action < 0
                or action >= executable_mask.size
                or not executable_mask[action]
            ):
                raise ValueError(f"base policy returned non-executable {name} action")
        mean = np.asarray(
            info["selected_predicted_delta"],
            dtype=np.float64,
        )
        scale = np.asarray(
            info["selected_predicted_scale"],
            dtype=np.float64,
        )
        probability = float(info["selected_executable_probability"])
        if mean.shape != (len(HORIZONS), 4) or scale.shape != mean.shape:
            raise ValueError("base policy prediction shape mismatch")
        if (
            not np.isfinite(mean).all()
            or not np.isfinite(scale).all()
            or np.any(scale < 0.0)
            or not np.isfinite(probability)
            or not 0.0 <= probability <= 1.0
        ):
            raise ValueError("base policy predictions must be finite and valid")
        if selected_action == reference_action:
            if np.any(mean != 0.0) or np.any(scale != 0.0):
                raise ValueError(
                    "reference-selected predictions must be exact zero deltas"
                )
        elif np.any(scale <= 0.0):
            raise ValueError("non-reference selected scales must be positive")

        continuation_seed = derive_continuation_seed(
            trajectory_seed,
            state_step,
            selected_action,
        )
        paired = evaluate_paired_objectives(
            env=env,
            candidate_action=selected_action,
            reference_action=reference_action,
            horizons=horizons,
            gamma=gamma,
            continuation_policy=continuation_policy,
            continuation_seed=continuation_seed,
            metric_reader=metric_reader,
            state_attrs=state_attrs,
        )
        observed_delta = np.asarray(
            paired.candidate - paired.reference,
            dtype=np.float64,
        )
        if observed_delta.shape != mean.shape or not np.isfinite(
            observed_delta
        ).all():
            raise ValueError("paired selected-label outcome is invalid")

        selected_actions.append(selected_action)
        reference_actions.append(reference_action)
        predicted_delta.append(mean)
        predicted_scale.append(scale)
        true_delta.append(observed_delta)
        probabilities.append(probability)
        reasons.append(str(info["base_selection_reason"]))
        state_steps.append(state_step)
        continuation_seeds.append(continuation_seed)

        _, _, terminated, truncated, _ = env.step(reference_action)
        if terminated or truncated:
            break

    if not state_steps:
        raise RuntimeError("No selected-label states were generated")
    count = len(state_steps)
    return {
        "selected_actions": np.asarray(selected_actions, dtype=np.int64),
        "reference_actions": np.asarray(reference_actions, dtype=np.int64),
        "predicted_delta": np.stack(predicted_delta).astype(np.float32),
        "predicted_scale": np.stack(predicted_scale).astype(np.float32),
        "true_delta": np.stack(true_delta).astype(np.float32),
        "executable_probability": np.asarray(
            probabilities,
            dtype=np.float32,
        ),
        "base_selection_reason": np.asarray(reasons, dtype="U64"),
        "state_steps": np.asarray(state_steps, dtype=np.int64),
        "trajectory_ids": np.full(count, trajectory_seed, dtype=np.int64),
        "continuation_seeds": np.asarray(
            continuation_seeds,
            dtype=np.uint64,
        ),
        "unexecuted_real_reward_queries": np.zeros(count, dtype=np.int64),
    }
