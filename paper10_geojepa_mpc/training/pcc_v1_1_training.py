import hashlib
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.models.pcc_paired_delta import (
    HORIZONS,
    PCCPairedDeltaMember,
)
from paper10_geojepa_mpc.models.sigreg import sigreg_loss
from paper10_geojepa_mpc.training.e0_training import load_e0_checkpoint
from paper10_geojepa_mpc.training.pcc_training import (
    _load_artifact_index,
    _load_manifest,
    _load_single_artifact,
    _member_seed,
    bootstrap_trajectory_ids,
    heteroscedastic_objective_loss,
)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_paired_batches(
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
        candidate_targets = arrays["objective_returns"][
            state_indexes,
            candidate_indexes,
        ]
        reference_targets = arrays["reference_objective_returns"][
            state_indexes,
            candidate_indexes,
        ]
        yield {
            "block": arrays["states_bf"][state_indexes],
            "neighbour": arrays["states_neighbor_bf"][state_indexes],
            "global_features": arrays["states_gf"][state_indexes],
            "candidate_actions": actions[state_indexes, candidate_indexes],
            "reference_actions": arrays["reference_actions"][state_indexes],
            "target_delta": candidate_targets - reference_targets,
            "candidate_absolute_target": candidate_targets[:, 0],
            "candidate_next_block": arrays["candidate_next_bf"][
                state_indexes,
                candidate_indexes,
            ],
            "candidate_next_global": arrays["candidate_next_gf"][
                state_indexes,
                candidate_indexes,
            ],
            "reference_next_block": arrays["reference_next_bf"][
                state_indexes,
                candidate_indexes,
            ],
            "reference_next_global": arrays["reference_next_gf"][
                state_indexes,
                candidate_indexes,
            ],
            "executable": arrays["executable_targets"][
                state_indexes,
                candidate_indexes,
            ],
        }


def direct_delta_nll(target, mean, log_scale):
    return heteroscedastic_objective_loss(target, mean, log_scale)


def zero_boundary_delta_ranking_loss(
    raw_target,
    *,
    predicted_normalized,
    center,
    scale,
):
    signed = torch.sign(raw_target)
    active = signed.ne(0)
    if not active.any():
        return predicted_normalized.sum() * 0.0
    predicted_from_zero = predicted_normalized + center / scale
    return F.softplus(
        -signed[active] * predicted_from_zero[active]
    ).mean()


def _robust_scaling(values: np.ndarray) -> dict[str, object]:
    values = np.asarray(values, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError("scaling targets must be finite")
    center = np.median(values, axis=0)
    mad = np.median(np.abs(values - center), axis=0)
    standard_deviation = values.std(axis=0)
    scale = np.where(mad > 1e-8, 1.4826 * mad, standard_deviation)
    scale = np.maximum(scale, 1e-6)
    return {"center": center.tolist(), "scale": scale.tolist()}


def compute_paired_scaling(
    candidate_targets: np.ndarray,
    reference_targets: np.ndarray,
) -> tuple[dict[str, object], dict[str, object]]:
    candidate = np.asarray(candidate_targets, dtype=np.float64)
    reference = np.asarray(reference_targets, dtype=np.float64)
    expected_tail = (len(HORIZONS), len(OBJECTIVE_NAMES))
    if (
        candidate.shape != reference.shape
        or candidate.ndim != 3
        or candidate.shape[1:] != expected_tail
    ):
        raise ValueError(
            "paired targets must share shape [samples, horizons, objectives]"
        )
    delta_scaling = _robust_scaling(candidate - reference)
    absolute_scaling = _robust_scaling(candidate[:, 0])
    return delta_scaling, absolute_scaling


def _validate_scaling(
    checkpoint: dict[str, object],
    field: str,
    expected_shape: tuple[int, ...],
) -> None:
    try:
        scaling = checkpoint[field]
        center = np.asarray(scaling["center"], dtype=np.float64)
        scale = np.asarray(scaling["scale"], dtype=np.float64)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid {field}") from error
    if center.shape != expected_shape or scale.shape != expected_shape:
        raise ValueError(f"invalid {field} shape")
    if not np.isfinite(center).all() or not np.isfinite(scale).all():
        raise ValueError(f"invalid {field}: values must be finite")
    if np.any(scale <= 0.0):
        raise ValueError(f"invalid {field}: scale must be positive")


def load_pcc_v1_1_checkpoint(path: str | Path, device: str = "cpu"):
    checkpoint = torch.load(Path(path), map_location=device, weights_only=False)
    if (
        checkpoint.get("model_class") != "PCCPairedDeltaMember"
        or checkpoint.get("protocol_id") != "pcc_v1_1"
        or checkpoint.get("source_protocol_id") != "pcc_v1"
    ):
        raise ValueError("PCC v1.1 checkpoint protocol mismatch")
    if tuple(checkpoint.get("objective_names", ())) != OBJECTIVE_NAMES:
        raise ValueError("PCC v1.1 checkpoint objective order mismatch")
    if tuple(checkpoint.get("horizons", ())) != HORIZONS:
        raise ValueError("PCC v1.1 checkpoint horizon mismatch")
    _validate_scaling(
        checkpoint,
        "delta_scaling",
        (len(HORIZONS), len(OBJECTIVE_NAMES)),
    )
    _validate_scaling(
        checkpoint,
        "absolute_scaling",
        (len(OBJECTIVE_NAMES),),
    )
    model = PCCPairedDeltaMember(**checkpoint["model_kwargs"]).to(device)
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.eval()
    return model, checkpoint


def train_paired_batch(
    model,
    optimizer,
    tensors,
    *,
    delta_center,
    delta_scale,
    absolute_center,
    absolute_scale,
) -> dict[str, float]:
    output = model(
        tensors["block"],
        tensors["neighbour"],
        tensors["global_features"],
        tensors["candidate_actions"],
        tensors["reference_actions"],
    )
    target_delta = (tensors["target_delta"] - delta_center) / delta_scale
    absolute_target = (
        tensors["candidate_absolute_target"] - absolute_center
    ) / absolute_scale
    delta_nll = direct_delta_nll(
        target_delta,
        output.delta_mean,
        output.delta_log_scale,
    )
    absolute_nll = heteroscedastic_objective_loss(
        absolute_target,
        output.candidate_absolute_mean,
        output.candidate_absolute_log_scale,
    )
    candidate_target = model.encode_target(
        tensors["candidate_next_block"],
        tensors["neighbour"],
        tensors["candidate_next_global"],
        tensors["candidate_actions"],
    )
    reference_target = model.encode_target(
        tensors["reference_next_block"],
        tensors["neighbour"],
        tensors["reference_next_global"],
        tensors["reference_actions"],
    )
    jepa_loss = 0.5 * (
        F.smooth_l1_loss(
            model.jepa_predictor(output.candidate_latent),
            candidate_target,
        )
        + F.smooth_l1_loss(
            model.jepa_predictor(output.reference_latent),
            reference_target,
        )
    )
    rank_loss = zero_boundary_delta_ranking_loss(
        tensors["target_delta"][..., :1],
        predicted_normalized=output.delta_mean[..., :1],
        center=delta_center[..., :1],
        scale=delta_scale[..., :1],
    )
    executable_bce = F.binary_cross_entropy_with_logits(
        output.executable_logit,
        tensors["executable"],
    )
    representation = sigreg_loss(
        torch.cat(
            [output.candidate_latent, output.reference_latent],
            dim=0,
        ),
        n_projections=16,
        n_knots=8,
    )
    loss = (
        delta_nll
        + 0.25 * absolute_nll
        + 0.25 * jepa_loss
        + 0.20 * rank_loss
        + 0.10 * executable_bce
        + 0.01 * representation
    )
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
    model.update_target_encoder()
    return {
        "loss": float(loss.detach().cpu()),
        "delta_nll": float(delta_nll.detach().cpu()),
        "absolute_nll": float(absolute_nll.detach().cpu()),
        "jepa_loss": float(jepa_loss.detach().cpu()),
        "rank_loss": float(rank_loss.detach().cpu()),
        "executable_bce": float(executable_bce.detach().cpu()),
        "sigreg": float(representation.detach().cpu()),
    }


def _copy_encoder_module(source_state, source_prefix, target_module) -> None:
    target_state = target_module.state_dict()
    copied = {}
    for name, target in target_state.items():
        source_name = f"{source_prefix}.{name}"
        if source_name not in source_state:
            raise ValueError(f"Paper9 checkpoint lacks encoder key: {source_name}")
        source = source_state[source_name]
        if source.shape != target.shape:
            raise ValueError(
                f"Paper9 encoder shape mismatch for {source_name}: "
                f"{tuple(source.shape)} != {tuple(target.shape)}"
            )
        copied[name] = source.detach().clone()
    target_module.load_state_dict(copied, strict=True)


def initialize_from_paper9(model, checkpoint_path: str | Path) -> str:
    _, checkpoint = load_e0_checkpoint(checkpoint_path, device="cpu")
    source_state = checkpoint["state_dict"]
    _copy_encoder_module(
        source_state,
        "block_encoder",
        model.online_encoder.block_encoder,
    )
    _copy_encoder_module(
        source_state,
        "block_encoder",
        model.online_encoder.neighbour_encoder,
    )
    _copy_encoder_module(
        source_state,
        "global_encoder",
        model.online_encoder.global_encoder,
    )
    model.target_encoder.load_state_dict(
        model.online_encoder.state_dict(),
        strict=True,
    )
    return sha256_file(checkpoint_path)


def _scaling_from_artifact_index(artifact_index):
    candidate_targets = []
    reference_targets = []
    for trajectory_id in sorted(artifact_index):
        path = artifact_index[trajectory_id]["path"]
        with np.load(path) as arrays:
            candidate_targets.append(
                np.asarray(
                    arrays["objective_returns"],
                    dtype=np.float32,
                ).reshape(-1, len(HORIZONS), len(OBJECTIVE_NAMES))
            )
            reference_targets.append(
                np.asarray(
                    arrays["reference_objective_returns"],
                    dtype=np.float32,
                ).reshape(-1, len(HORIZONS), len(OBJECTIVE_NAMES))
            )
    return compute_paired_scaling(
        np.concatenate(candidate_targets, axis=0),
        np.concatenate(reference_targets, axis=0),
    )


def _cpu_state_dict(model) -> dict[str, torch.Tensor]:
    return {
        name: value.detach().cpu().clone()
        for name, value in model.state_dict().items()
    }


def _checkpoint_payload(
    model,
    *,
    registry_digest,
    source_manifest_digest,
    transfer_checkpoint_sha256,
    model_seed,
    ensemble_size,
    member_index,
    member_seed,
    bootstrap_ids,
    delta_scaling,
    absolute_scaling,
    trainable_parameter_names,
    metrics,
) -> dict[str, object]:
    return {
        "model_class": "PCCPairedDeltaMember",
        "protocol_id": "pcc_v1_1",
        "source_protocol_id": "pcc_v1",
        "registry_digest": str(registry_digest),
        "source_manifest_digest": str(source_manifest_digest),
        "transfer_checkpoint_sha256": str(transfer_checkpoint_sha256),
        "model_seed": int(model_seed),
        "ensemble_size": int(ensemble_size),
        "member_index": int(member_index),
        "member_seed": int(member_seed),
        "bootstrap_trajectory_ids": [
            int(value) for value in bootstrap_ids
        ],
        "model_kwargs": model.model_kwargs(),
        "objective_names": list(OBJECTIVE_NAMES),
        "horizons": list(HORIZONS),
        "delta_scaling": delta_scaling,
        "absolute_scaling": absolute_scaling,
        "trainable_parameter_names": list(trainable_parameter_names),
        "metrics": dict(metrics),
        "state_dict": _cpu_state_dict(model),
    }


def train_pcc_v1_1_ensemble(
    *,
    labels_manifest: str | Path,
    reference_checkpoint: str | Path,
    expected_source_manifest_digest: str,
    expected_transfer_checkpoint_sha256: str,
    registry_digest: str,
    model_seed: int,
    ensemble_size: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: str,
    output_dir: str | Path,
    hidden_dim: int = 32,
    ema_decay: float = 0.99,
) -> list[Path]:
    if min(int(ensemble_size), int(epochs), int(batch_size)) <= 0:
        raise ValueError("ensemble_size, epochs, and batch_size must be positive")
    if float(learning_rate) < 0.0:
        raise ValueError("learning_rate must be non-negative")

    manifest_path, manifest = _load_manifest(labels_manifest)
    if manifest.get("protocol_id") != "pcc_v1":
        raise ValueError("source manifest protocol must be pcc_v1")
    if manifest.get("partition") != "train":
        raise ValueError("source manifest partition must be train")
    source_manifest_digest = str(manifest["manifest_digest"])
    if source_manifest_digest != str(expected_source_manifest_digest):
        raise ValueError("source manifest digest mismatch")
    transfer_digest = sha256_file(reference_checkpoint)
    if transfer_digest != str(expected_transfer_checkpoint_sha256):
        raise ValueError("transfer checkpoint digest mismatch")

    artifact_index = _load_artifact_index(manifest_path, manifest)
    unique_ids = np.asarray(sorted(artifact_index), dtype=np.int64)
    if unique_ids.size == 0:
        raise ValueError("source manifest has no trajectory artifacts")
    delta_scaling, absolute_scaling = _scaling_from_artifact_index(
        artifact_index
    )
    first = _load_single_artifact(artifact_index[int(unique_ids[0])]["path"])
    block_feature_dim = int(first["states_bf"].shape[-1])
    global_feature_dim = int(first["states_gf"].shape[-1])
    del first

    probe = PCCPairedDeltaMember(
        block_feature_dim,
        global_feature_dim,
        hidden_dim=int(hidden_dim),
        ema_decay=float(ema_decay),
    )
    initialize_from_paper9(probe, reference_checkpoint)
    del probe

    device_object = torch.device(device)
    delta_center = torch.as_tensor(
        delta_scaling["center"],
        dtype=torch.float32,
        device=device_object,
    )
    delta_scale = torch.as_tensor(
        delta_scaling["scale"],
        dtype=torch.float32,
        device=device_object,
    )
    absolute_center = torch.as_tensor(
        absolute_scaling["center"],
        dtype=torch.float32,
        device=device_object,
    )
    absolute_scale = torch.as_tensor(
        absolute_scaling["scale"],
        dtype=torch.float32,
        device=device_object,
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_paths = []
    metric_names = (
        "loss",
        "delta_nll",
        "absolute_nll",
        "jepa_loss",
        "rank_loss",
        "executable_bce",
        "sigreg",
    )
    for member_index in range(int(ensemble_size)):
        member_seed = _member_seed(
            model_seed,
            member_index,
            ensemble_size=ensemble_size,
        )
        torch.manual_seed(member_seed)
        np.random.seed(member_seed)
        bootstrap_ids = bootstrap_trajectory_ids(unique_ids, seed=member_seed)
        model = PCCPairedDeltaMember(
            block_feature_dim,
            global_feature_dim,
            hidden_dim=int(hidden_dim),
            ema_decay=float(ema_decay),
        ).to(device_object)
        initialize_from_paper9(model, reference_checkpoint)
        trainable_names = sorted(
            name
            for name, parameter in model.named_parameters()
            if parameter.requires_grad
        )
        optimizer = torch.optim.AdamW(
            [
                parameter
                for parameter in model.parameters()
                if parameter.requires_grad
            ],
            lr=float(learning_rate),
        )
        totals = {name: 0.0 for name in metric_names}
        updates = 0
        member_rng = np.random.default_rng(member_seed)
        model.train()
        for _ in range(int(epochs)):
            epoch_ids = bootstrap_ids[
                member_rng.permutation(len(bootstrap_ids))
            ]
            for trajectory_id in epoch_ids:
                arrays = _load_single_artifact(
                    artifact_index[int(trajectory_id)]["path"]
                )
                for batch in iter_paired_batches(
                    arrays,
                    batch_size=batch_size,
                    rng=member_rng,
                ):
                    tensors = {
                        key: torch.as_tensor(
                            value,
                            device=device_object,
                            dtype=torch.long
                            if key
                            in {"candidate_actions", "reference_actions"}
                            else torch.float32,
                        )
                        for key, value in batch.items()
                    }
                    observed = train_paired_batch(
                        model,
                        optimizer,
                        tensors,
                        delta_center=delta_center,
                        delta_scale=delta_scale,
                        absolute_center=absolute_center,
                        absolute_scale=absolute_scale,
                    )
                    for name, value in observed.items():
                        totals[name] += value
                    updates += 1
                del arrays

        metrics = {
            name: value / max(updates, 1)
            for name, value in totals.items()
        }
        metrics["n_updates"] = int(updates)
        metrics["n_trainable_parameters"] = int(
            sum(
                parameter.numel()
                for parameter in model.parameters()
                if parameter.requires_grad
            )
        )
        checkpoint_path = output_dir / f"member_{member_index}.pt"
        temporary = checkpoint_path.with_suffix(".tmp.pt")
        torch.save(
            _checkpoint_payload(
                model,
                registry_digest=registry_digest,
                source_manifest_digest=source_manifest_digest,
                transfer_checkpoint_sha256=transfer_digest,
                model_seed=model_seed,
                ensemble_size=ensemble_size,
                member_index=member_index,
                member_seed=member_seed,
                bootstrap_ids=bootstrap_ids,
                delta_scaling=delta_scaling,
                absolute_scaling=absolute_scaling,
                trainable_parameter_names=trainable_names,
                metrics=metrics,
            ),
            temporary,
        )
        temporary.replace(checkpoint_path)
        checkpoint_paths.append(checkpoint_path)
    return checkpoint_paths
