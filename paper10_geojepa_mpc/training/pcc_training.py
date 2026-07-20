import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
import torch.nn.functional as F

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.models.pcc_geojepa import (
    HORIZONS,
    PCCGeoJEPAMember,
)
from paper10_geojepa_mpc.models.sigreg import sigreg_loss


def bootstrap_trajectory_ids(unique_ids: np.ndarray, seed: int) -> np.ndarray:
    ids = np.asarray(unique_ids, dtype=np.int64).reshape(-1)
    if ids.size == 0 or np.unique(ids).size != ids.size:
        raise ValueError("unique_ids must contain distinct trajectory identifiers")
    return np.random.default_rng(int(seed)).choice(
        ids,
        size=len(ids),
        replace=True,
    )


def heteroscedastic_objective_loss(target, mean, log_scale):
    log_scale = log_scale.clamp(-8.0, 5.0)
    inverse_variance = torch.exp(-2.0 * log_scale)
    return (0.5 * (target - mean).square() * inverse_variance + log_scale).mean()


def pairwise_delta_ranking_loss(
    candidate_mean,
    reference_mean,
    target_delta,
    margin: float = 0.05,
):
    signed = torch.sign(target_delta)
    active = signed.ne(0)
    if not active.any():
        return (candidate_mean - reference_mean).sum() * 0.0
    predicted_delta = candidate_mean - reference_mean
    return torch.relu(
        float(margin) - signed[active] * predicted_delta[active]
    ).mean()


def compute_robust_objective_scaling(
    candidate: np.ndarray,
    reference: np.ndarray,
) -> dict[str, list[list[float]]]:
    candidate = np.asarray(candidate, dtype=np.float64)
    reference = np.asarray(reference, dtype=np.float64)
    if candidate.shape != reference.shape or candidate.ndim != 3:
        raise ValueError("objective arrays must share shape [samples, horizons, objectives]")
    combined = np.concatenate([candidate, reference], axis=0)
    if not np.isfinite(combined).all():
        raise ValueError("objective scaling inputs must be finite")
    center = np.median(combined, axis=0)
    mad = np.median(np.abs(combined - center), axis=0)
    standard_deviation = combined.std(axis=0)
    scale = np.where(mad > 1e-8, 1.4826 * mad, standard_deviation)
    scale = np.maximum(scale, 1e-6)
    return {
        "center": center.tolist(),
        "scale": scale.tolist(),
    }


def set_trainable_scope(model: PCCGeoJEPAMember, scope: str) -> list[str]:
    if scope not in {"all", "objective_heads"}:
        raise ValueError("trainable_scope must be 'all' or 'objective_heads'")
    trainable = []
    for name, parameter in model.named_parameters():
        enabled = scope == "all" or name.startswith(
            ("immediate_head.", "horizon_head.")
        )
        parameter.requires_grad = enabled
        if enabled:
            trainable.append(name)
    if not trainable:
        raise ValueError(f"No trainable parameters for scope: {scope}")
    return trainable


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(path: str | Path) -> tuple[Path, dict[str, object]]:
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
    observed = hashlib.sha256(canonical).hexdigest()
    if expected != observed:
        raise ValueError("label manifest digest mismatch")
    if "confirmation" in str(payload.get("partition", "")).lower():
        raise ValueError("confirmation-labelled inputs are forbidden for training")
    return path, payload


def _load_artifact_arrays(
    manifest_path: Path,
    manifest: dict[str, object],
) -> dict[int, dict[str, np.ndarray]]:
    by_seed = {}
    for artifact in manifest["artifacts"]:
        path = manifest_path.parent / str(artifact["path"])
        if _sha256_file(path) != artifact["sha256"]:
            raise ValueError(f"label artifact digest mismatch: {path}")
        with np.load(path) as data:
            arrays = {key: data[key].copy() for key in data.files}
        seed = int(artifact["trajectory_seed"])
        if seed in by_seed:
            raise ValueError(f"duplicate trajectory artifact: {seed}")
        if not np.all(arrays["trajectory_ids"] == seed):
            raise ValueError(f"trajectory identity mismatch: {seed}")
        if tuple(arrays["horizons"].tolist()) != HORIZONS:
            raise ValueError("PCC training labels must use horizons 1, 3, and 5")
        by_seed[seed] = arrays
    return by_seed


def _load_artifact_index(
    manifest_path: Path,
    manifest: dict[str, object],
) -> dict[int, dict[str, object]]:
    index = {}
    for artifact in manifest["artifacts"]:
        path = manifest_path.parent / str(artifact["path"])
        if _sha256_file(path) != artifact["sha256"]:
            raise ValueError(f"label artifact digest mismatch: {path}")
        seed = int(artifact["trajectory_seed"])
        if seed in index:
            raise ValueError(f"duplicate trajectory artifact: {seed}")
        with np.load(path) as data:
            trajectory_ids = data["trajectory_ids"]
            horizons = data["horizons"]
            actions_shape = data["actions"].shape
        if not np.all(trajectory_ids == seed):
            raise ValueError(f"trajectory identity mismatch: {seed}")
        if tuple(horizons.tolist()) != HORIZONS:
            raise ValueError("PCC training labels must use horizons 1, 3, and 5")
        index[seed] = {
            "path": path,
            "n_states": int(actions_shape[0]),
            "n_candidates": int(actions_shape[1]),
        }
    return index


def _load_single_artifact(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {key: data[key].copy() for key in data.files}


def _scaling_from_artifact_index(
    artifact_index: dict[int, dict[str, object]],
) -> dict[str, list[list[float]]]:
    candidate = []
    reference = []
    for seed in sorted(artifact_index):
        path = artifact_index[seed]["path"]
        with np.load(path) as data:
            candidate.append(
                np.asarray(data["objective_returns"], dtype=np.float32).reshape(
                    -1, len(HORIZONS), len(OBJECTIVE_NAMES)
                )
            )
            reference.append(
                np.asarray(
                    data["reference_objective_returns"],
                    dtype=np.float32,
                ).reshape(-1, len(HORIZONS), len(OBJECTIVE_NAMES))
            )
    return compute_robust_objective_scaling(
        np.concatenate(candidate, axis=0),
        np.concatenate(reference, axis=0),
    )


def _iter_artifact_batches(
    arrays: dict[str, np.ndarray],
    *,
    batch_size: int,
    rng: np.random.Generator,
):
    actions = np.asarray(arrays["actions"], dtype=np.int64)
    n_states, n_candidates = actions.shape
    order = rng.permutation(n_states * n_candidates)
    for start in range(0, len(order), int(batch_size)):
        flat = order[start : start + int(batch_size)]
        state_indexes = flat // n_candidates
        candidate_indexes = flat % n_candidates
        yield {
            "block": arrays["states_bf"][state_indexes],
            "neighbour": arrays["states_neighbor_bf"][state_indexes],
            "global": arrays["states_gf"][state_indexes],
            "actions": actions[state_indexes, candidate_indexes],
            "reference_actions": arrays["reference_actions"][state_indexes],
            "target": arrays["objective_returns"][
                state_indexes, candidate_indexes
            ],
            "reference_target": arrays["reference_objective_returns"][
                state_indexes, candidate_indexes
            ],
            "candidate_next_bf": arrays["candidate_next_bf"][
                state_indexes, candidate_indexes
            ],
            "candidate_next_gf": arrays["candidate_next_gf"][
                state_indexes, candidate_indexes
            ],
            "reference_next_bf": arrays["reference_next_bf"][
                state_indexes, candidate_indexes
            ],
            "reference_next_gf": arrays["reference_next_gf"][
                state_indexes, candidate_indexes
            ],
            "executable": arrays["executable_targets"][
                state_indexes, candidate_indexes
            ],
        }


def _flatten_dataset(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    states = np.asarray(arrays["states_bf"], dtype=np.float32)
    neighbours = np.asarray(arrays["states_neighbor_bf"], dtype=np.float32)
    global_features = np.asarray(arrays["states_gf"], dtype=np.float32)
    actions = np.asarray(arrays["actions"], dtype=np.int64)
    n_states, n_candidates = actions.shape

    repeated_states = np.repeat(states[:, None], n_candidates, axis=1)
    repeated_neighbours = np.repeat(neighbours[:, None], n_candidates, axis=1)
    repeated_global = np.repeat(global_features[:, None], n_candidates, axis=1)
    reference_actions = np.repeat(
        np.asarray(arrays["reference_actions"], dtype=np.int64)[:, None],
        n_candidates,
        axis=1,
    )
    return {
        "block": repeated_states.reshape(-1, *states.shape[1:]),
        "neighbour": repeated_neighbours.reshape(-1, *neighbours.shape[1:]),
        "global": repeated_global.reshape(-1, global_features.shape[-1]),
        "actions": actions.reshape(-1),
        "reference_actions": reference_actions.reshape(-1),
        "target": np.asarray(arrays["objective_returns"], dtype=np.float32).reshape(
            -1, len(HORIZONS), len(OBJECTIVE_NAMES)
        ),
        "reference_target": np.asarray(
            arrays["reference_objective_returns"],
            dtype=np.float32,
        ).reshape(-1, len(HORIZONS), len(OBJECTIVE_NAMES)),
        "candidate_next_bf": np.asarray(
            arrays["candidate_next_bf"], dtype=np.float32
        ).reshape(-1, *states.shape[1:]),
        "candidate_next_gf": np.asarray(
            arrays["candidate_next_gf"], dtype=np.float32
        ).reshape(-1, global_features.shape[-1]),
        "reference_next_bf": np.asarray(
            arrays["reference_next_bf"], dtype=np.float32
        ).reshape(-1, *states.shape[1:]),
        "reference_next_gf": np.asarray(
            arrays["reference_next_gf"], dtype=np.float32
        ).reshape(-1, global_features.shape[-1]),
        "executable": np.asarray(
            arrays["executable_targets"], dtype=np.float32
        ).reshape(-1),
    }


def _concatenate_datasets(
    by_seed: dict[int, dict[str, np.ndarray]],
    selected_seeds: Sequence[int],
) -> dict[str, np.ndarray]:
    flattened = [_flatten_dataset(by_seed[int(seed)]) for seed in selected_seeds]
    keys = flattened[0]
    return {
        key: np.concatenate([dataset[key] for dataset in flattened], axis=0)
        for key in keys
    }


def _member_seed(model_seed: int, member_index: int) -> int:
    value = np.random.SeedSequence(
        [int(model_seed), int(member_index)]
    ).generate_state(1, dtype=np.uint32)[0]
    return int(value)


def _resolve_init_checkpoint(
    root: str | Path | None,
    member_index: int,
) -> Path | None:
    if root is None:
        return None
    root = Path(root)
    if root.is_file():
        return root
    candidates = sorted(root.rglob("*.pt"))
    if member_index >= len(candidates):
        raise ValueError("init checkpoint root has too few ensemble members")
    return candidates[member_index]


def _checkpoint_payload(
    model: PCCGeoJEPAMember,
    *,
    model_seed: int,
    member_seed: int,
    member_index: int,
    bootstrap_ids: np.ndarray,
    objective_scaling: dict[str, object],
    manifest: dict[str, object],
    trainable_scope: str,
    metrics: dict[str, float],
    registry_digest: str | None,
) -> dict[str, object]:
    return {
        "model_class": "PCCGeoJEPAMember",
        "model_kwargs": {
            "block_feature_dim": model.block_feature_dim,
            "k_global": model.k_global,
            "hidden_dim": model.hidden_dim,
            "representation": model.representation,
            "county_action_count": model.county_action_count,
        },
        "state_dict": {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        },
        "model_seed": int(model_seed),
        "member_seed": int(member_seed),
        "member_index": int(member_index),
        "bootstrap_trajectory_ids": [int(value) for value in bootstrap_ids],
        "objective_names": list(OBJECTIVE_NAMES),
        "horizons": list(HORIZONS),
        "objective_scaling": objective_scaling,
        "protocol_id": manifest["protocol_id"],
        "registry_digest": registry_digest,
        "labels_manifest_digest": manifest["manifest_digest"],
        "trainable_scope": trainable_scope,
        "metrics": metrics,
    }


def _train_pcc_batch(model, optimizer, tensors, center, scale) -> dict[str, float]:
    candidate = model(
        tensors["block"],
        tensors["neighbour"],
        tensors["global"],
        tensors["actions"],
    )
    reference = model(
        tensors["block"],
        tensors["neighbour"],
        tensors["global"],
        tensors["reference_actions"],
    )
    candidate_target = (tensors["target"] - center) / scale
    reference_target = (tensors["reference_target"] - center) / scale
    transition_huber = 0.5 * (
        F.smooth_l1_loss(candidate.next_block, tensors["candidate_next_bf"])
        + F.smooth_l1_loss(candidate.next_global, tensors["candidate_next_gf"])
        + F.smooth_l1_loss(reference.next_block, tensors["reference_next_bf"])
        + F.smooth_l1_loss(reference.next_global, tensors["reference_next_gf"])
    )
    objective_nll = 0.5 * (
        heteroscedastic_objective_loss(
            candidate_target,
            candidate.horizon_mean,
            candidate.horizon_log_scale,
        )
        + heteroscedastic_objective_loss(
            reference_target,
            reference.horizon_mean,
            reference.horizon_log_scale,
        )
    )
    immediate_nll = 0.5 * (
        heteroscedastic_objective_loss(
            candidate_target[:, 0],
            candidate.immediate_mean,
            candidate.immediate_log_scale,
        )
        + heteroscedastic_objective_loss(
            reference_target[:, 0],
            reference.immediate_mean,
            reference.immediate_log_scale,
        )
    )
    rank_loss = pairwise_delta_ranking_loss(
        candidate.horizon_mean,
        reference.horizon_mean,
        candidate_target - reference_target,
    )
    executable_bce = F.binary_cross_entropy_with_logits(
        candidate.executable_logit,
        tensors["executable"],
    )
    representation = sigreg_loss(
        torch.cat([candidate.latent, reference.latent], dim=0),
        n_projections=16,
        n_knots=8,
    )
    loss = (
        transition_huber
        + objective_nll
        + 0.25 * immediate_nll
        + 0.20 * rank_loss
        + 0.10 * executable_bce
        + 0.01 * representation
    )
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    return {
        "loss": float(loss.detach().cpu()),
        "transition_huber": float(transition_huber.detach().cpu()),
        "objective_nll": float(objective_nll.detach().cpu()),
        "rank_loss": float(rank_loss.detach().cpu()),
        "executable_bce": float(executable_bce.detach().cpu()),
    }


def train_pcc_ensemble(
    *,
    labels_manifest: str | Path,
    model_seed: int,
    ensemble_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: str,
    output_dir: str | Path,
    hidden_dim: int = 32,
    trainable_scope: str = "all",
    init_checkpoint_root: str | Path | None = None,
    registry_digest: str | None = None,
    representation: str = "action_relative",
    county_action_count: int | None = None,
) -> list[Path]:
    if min(int(ensemble_size), int(epochs), int(batch_size)) <= 0:
        raise ValueError("ensemble_size, epochs, and batch_size must be positive")
    if float(learning_rate) < 0.0:
        raise ValueError("learning_rate must be non-negative")

    manifest_path, manifest = _load_manifest(labels_manifest)
    artifact_index = _load_artifact_index(manifest_path, manifest)
    unique_ids = np.asarray(sorted(artifact_index), dtype=np.int64)
    objective_scaling = _scaling_from_artifact_index(artifact_index)
    center_np = np.asarray(objective_scaling["center"], dtype=np.float32)
    scale_np = np.asarray(objective_scaling["scale"], dtype=np.float32)
    first_arrays = _load_single_artifact(artifact_index[int(unique_ids[0])]["path"])
    block_feature_dim = int(first_arrays["states_bf"].shape[-1])
    global_feature_dim = int(first_arrays["states_gf"].shape[-1])
    del first_arrays

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_paths = []
    device_obj = torch.device(device)

    for member_index in range(int(ensemble_size)):
        seed = _member_seed(model_seed, member_index)
        torch.manual_seed(seed)
        np.random.seed(seed)
        bootstrap_ids = bootstrap_trajectory_ids(unique_ids, seed=seed)
        model = PCCGeoJEPAMember(
            block_feature_dim=block_feature_dim,
            k_global=global_feature_dim,
            hidden_dim=hidden_dim,
            representation=representation,
            county_action_count=county_action_count,
        ).to(device_obj)
        init_path = _resolve_init_checkpoint(init_checkpoint_root, member_index)
        if init_path is not None:
            initial_model, _ = load_pcc_checkpoint(init_path, device=device)
            model.load_state_dict(initial_model.state_dict(), strict=True)
        elif trainable_scope != "all":
            raise ValueError("objective_heads training requires init_checkpoint_root")
        trainable_names = set_trainable_scope(model, trainable_scope)
        optimizer = torch.optim.AdamW(
            [parameter for parameter in model.parameters() if parameter.requires_grad],
            lr=float(learning_rate),
        )

        center = torch.as_tensor(center_np, device=device_obj)
        scale = torch.as_tensor(scale_np, device=device_obj)
        n_samples = int(
            sum(
                int(artifact_index[int(trajectory_id)]["n_states"])
                * int(artifact_index[int(trajectory_id)]["n_candidates"])
                for trajectory_id in bootstrap_ids
            )
        )
        totals = {
            "loss": 0.0,
            "transition_huber": 0.0,
            "objective_nll": 0.0,
            "rank_loss": 0.0,
            "executable_bce": 0.0,
        }
        updates = 0
        model.train()
        member_rng = np.random.default_rng(seed)
        for _ in range(int(epochs)):
            epoch_ids = bootstrap_ids[member_rng.permutation(len(bootstrap_ids))]
            for trajectory_id in epoch_ids:
                arrays = _load_single_artifact(
                    artifact_index[int(trajectory_id)]["path"]
                )
                for batch in _iter_artifact_batches(
                    arrays,
                    batch_size=batch_size,
                    rng=member_rng,
                ):
                    tensors = {
                        key: torch.as_tensor(
                            value,
                            device=device_obj,
                            dtype=torch.long
                            if key in {"actions", "reference_actions"}
                            else torch.float32,
                        )
                        for key, value in batch.items()
                    }
                    batch_metrics = _train_pcc_batch(
                        model,
                        optimizer,
                        tensors,
                        center,
                        scale,
                    )
                    for key, value in batch_metrics.items():
                        totals[key] += value
                    updates += 1
                del arrays

        metrics = {key: value / max(updates, 1) for key, value in totals.items()}
        metrics["n_samples"] = int(n_samples)
        metrics["n_trainable_parameters"] = int(
            sum(
                parameter.numel()
                for parameter in model.parameters()
                if parameter.requires_grad
            )
        )
        metrics["trainable_parameter_names"] = sorted(trainable_names)
        checkpoint_path = output_dir / f"member_{member_index}.pt"
        torch.save(
            _checkpoint_payload(
                model,
                model_seed=model_seed,
                member_seed=seed,
                member_index=member_index,
                bootstrap_ids=bootstrap_ids,
                objective_scaling=objective_scaling,
                manifest=manifest,
                trainable_scope=trainable_scope,
                metrics=metrics,
                registry_digest=registry_digest,
            ),
            checkpoint_path,
        )
        checkpoint_paths.append(checkpoint_path)
    return checkpoint_paths


def load_pcc_checkpoint(path: str | Path, device: str = "cpu"):
    checkpoint = torch.load(Path(path), map_location=device, weights_only=False)
    if checkpoint.get("model_class") != "PCCGeoJEPAMember":
        raise ValueError(f"Unsupported checkpoint model: {checkpoint.get('model_class')}")
    if tuple(checkpoint.get("objective_names", ())) != OBJECTIVE_NAMES:
        raise ValueError("PCC checkpoint objective order mismatch")
    if tuple(checkpoint.get("horizons", ())) != HORIZONS:
        raise ValueError("PCC checkpoint horizon mismatch")
    model = PCCGeoJEPAMember(**checkpoint["model_kwargs"]).to(device)
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.eval()
    return model, checkpoint
