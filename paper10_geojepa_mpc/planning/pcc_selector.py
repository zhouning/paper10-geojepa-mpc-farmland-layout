from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from paper10_geojepa_mpc.models.pcc_geojepa import HORIZONS


@dataclass(frozen=True)
class PairedEnsembleStatistics:
    mean_delta: np.ndarray
    epistemic_variance: np.ndarray
    aleatoric_variance: np.ndarray
    paired_scale: np.ndarray
    uncertainty_rank: np.ndarray


@dataclass(frozen=True)
class EnsemblePrediction:
    actions: np.ndarray
    mean_delta: np.ndarray
    paired_scale: np.ndarray
    uncertainty_rank: np.ndarray
    executable_probability: np.ndarray
    candidate_mean: np.ndarray
    candidate_base_scale: np.ndarray
    member_evaluations: int
    model_forward_count: int


@dataclass(frozen=True)
class EnsembleHorizonPrediction:
    actions: np.ndarray
    mean_delta: np.ndarray
    paired_scale: np.ndarray
    executable_probability: np.ndarray
    candidate_mean: np.ndarray
    candidate_base_scale: np.ndarray
    member_evaluations: int
    model_forward_count: int


def paired_ensemble_statistics(
    candidate_mean,
    candidate_log_scale,
    reference_mean,
    reference_log_scale,
) -> PairedEnsembleStatistics:
    candidate_mean = np.asarray(candidate_mean, dtype=np.float64)
    candidate_log_scale = np.asarray(candidate_log_scale, dtype=np.float64)
    reference_mean = np.asarray(reference_mean, dtype=np.float64)
    reference_log_scale = np.asarray(reference_log_scale, dtype=np.float64)
    if candidate_mean.shape != candidate_log_scale.shape:
        raise ValueError("candidate mean and log scale shape must match")
    if reference_mean.shape != reference_log_scale.shape:
        raise ValueError("reference mean and log scale shape must match")
    if candidate_mean.ndim < 3 or reference_mean.shape != (
        candidate_mean.shape[0],
        *candidate_mean.shape[2:],
    ):
        raise ValueError("reference predictions must omit only the candidate axis")
    if not all(
        np.isfinite(value).all()
        for value in (
            candidate_mean,
            candidate_log_scale,
            reference_mean,
            reference_log_scale,
        )
    ):
        raise ValueError("ensemble predictions must be finite")

    expanded_reference_mean = reference_mean[:, None, ...]
    expanded_reference_log_scale = reference_log_scale[:, None, ...]
    member_delta = candidate_mean - expanded_reference_mean
    mean_delta = member_delta.mean(axis=0)
    if member_delta.shape[0] > 1:
        epistemic_variance = member_delta.var(axis=0, ddof=1)
    else:
        epistemic_variance = np.zeros_like(mean_delta)
    aleatoric_variance = np.mean(
        np.exp(2.0 * candidate_log_scale)
        + np.exp(2.0 * expanded_reference_log_scale),
        axis=0,
    )
    paired_scale = np.sqrt(
        np.maximum(epistemic_variance + aleatoric_variance, 1e-12)
    )
    uncertainty_rank = paired_scale.reshape(paired_scale.shape[0], -1).max(axis=1)
    return PairedEnsembleStatistics(
        mean_delta=mean_delta,
        epistemic_variance=epistemic_variance,
        aleatoric_variance=aleatoric_variance,
        paired_scale=paired_scale,
        uncertainty_rank=uncertainty_rank,
    )


def choose_from_bounds(
    actions,
    lower_bounds,
    executable_probability,
    uncertainty,
    reference_action: int,
    tolerances,
    executable_threshold: float = 0.95,
):
    actions = np.asarray(actions, dtype=np.int64).reshape(-1)
    lower = np.asarray(lower_bounds, dtype=np.float64)
    probability = np.asarray(executable_probability, dtype=np.float64).reshape(-1)
    uncertainty = np.asarray(uncertainty, dtype=np.float64).reshape(-1)
    tolerances = np.asarray(tolerances, dtype=np.float64).reshape(-1)
    if lower.shape != (actions.size, 4):
        raise ValueError("lower_bounds must have shape [n_actions, 4]")
    if probability.shape != actions.shape or uncertainty.shape != actions.shape:
        raise ValueError("probability and uncertainty must align with actions")
    if tolerances.shape != (3,) or np.any(tolerances < 0.0):
        raise ValueError("tolerances must contain three non-negative values")
    if not 0.0 <= float(executable_threshold) <= 1.0:
        raise ValueError("executable_threshold must be in [0, 1]")
    if actions.size == 0 or not all(
        np.isfinite(value).all()
        for value in (lower, probability, uncertainty, tolerances)
    ):
        return int(reference_action), {
            "fallback": True,
            "fallback_reason": "non_finite_prediction"
            if actions.size
            else "empty_candidate_pool",
            "admissible_actions": [],
        }

    admissible = probability >= float(executable_threshold)
    admissible &= lower[:, 0] > 0.0
    admissible &= np.all(lower[:, 1:] >= -tolerances[None, :], axis=1)
    indexes = np.flatnonzero(admissible)
    if indexes.size == 0:
        return int(reference_action), {
            "fallback": True,
            "fallback_reason": "no_admissible_candidate",
            "admissible_actions": [],
        }

    order = sorted(
        indexes.tolist(),
        key=lambda index: (
            -float(lower[index, 0]),
            -float(lower[index, 1:].min()),
            float(uncertainty[index]),
            int(actions[index]),
        ),
    )
    selected = order[0]
    return int(actions[selected]), {
        "fallback": False,
        "fallback_reason": None,
        "admissible_actions": [int(actions[index]) for index in indexes],
        "selected_index": int(selected),
        "selected_lower_bounds": lower[selected].tolist(),
    }


def build_candidate_pool(
    *,
    reference_action: int,
    proposal_groups,
    executable_mask,
    candidate_budget: int,
) -> np.ndarray:
    mask = np.asarray(executable_mask, dtype=bool).reshape(-1)
    if int(candidate_budget) <= 0:
        raise ValueError("candidate_budget must be positive")
    reference_action = int(reference_action)
    if reference_action < 0 or reference_action >= mask.size or not mask[reference_action]:
        raise ValueError("reference action must be executable")

    ordered = [reference_action]
    seen = {reference_action}
    for group in proposal_groups:
        for raw_action in group:
            action = int(raw_action)
            if action < 0 or action >= mask.size or not mask[action] or action in seen:
                continue
            ordered.append(action)
            seen.add(action)
    for action in np.flatnonzero(mask):
        action = int(action)
        if action not in seen:
            ordered.append(action)
            seen.add(action)
    return np.asarray(ordered[: int(candidate_budget)], dtype=np.int64)


def predict_paired_ensemble_all_horizons(
    ensemble,
    *,
    block_features,
    neighbour_features,
    global_features,
    actions,
    reference_action: int,
    device: str = "cpu",
) -> EnsembleHorizonPrediction:
    actions = np.asarray(actions, dtype=np.int64).reshape(-1)
    if actions.size == 0 or np.unique(actions).size != actions.size:
        raise ValueError("actions must be non-empty and unique")
    reference_matches = np.flatnonzero(actions == int(reference_action))
    if reference_matches.size != 1:
        raise ValueError("candidate pool must contain the reference action exactly once")
    if not ensemble:
        raise ValueError("ensemble must contain at least one member")

    block = np.asarray(block_features, dtype=np.float32)
    neighbour = np.asarray(neighbour_features, dtype=np.float32)
    global_array = np.asarray(global_features, dtype=np.float32)
    if block.ndim != 2 or neighbour.shape != block.shape or global_array.ndim != 1:
        raise ValueError("observable feature shapes are invalid")

    member_means = []
    member_log_scales = []
    member_probabilities = []
    expected_center = None
    expected_scale = None
    device_obj = torch.device(device)
    for model, checkpoint in ensemble:
        scaling = checkpoint.get("objective_scaling", {})
        center = np.asarray(scaling.get("center"), dtype=np.float64)
        scale = np.asarray(scaling.get("scale"), dtype=np.float64)
        if center.shape != (len(HORIZONS), 4) or scale.shape != center.shape:
            raise ValueError("checkpoint objective scaling shape mismatch")
        if not np.isfinite(center).all() or not np.isfinite(scale).all() or np.any(
            scale <= 0.0
        ):
            raise ValueError("checkpoint objective scaling is invalid")
        if expected_center is None:
            expected_center = center
            expected_scale = scale
        elif not np.allclose(center, expected_center) or not np.allclose(
            scale, expected_scale
        ):
            raise ValueError("ensemble members use inconsistent objective scaling")

        batch_size = actions.size
        bf = torch.as_tensor(
            np.repeat(block[None, ...], batch_size, axis=0),
            dtype=torch.float32,
            device=device_obj,
        )
        nf = torch.as_tensor(
            np.repeat(neighbour[None, ...], batch_size, axis=0),
            dtype=torch.float32,
            device=device_obj,
        )
        gf = torch.as_tensor(
            np.repeat(global_array[None, ...], batch_size, axis=0),
            dtype=torch.float32,
            device=device_obj,
        )
        act = torch.as_tensor(actions, dtype=torch.long, device=device_obj)
        model = model.to(device_obj)
        model.eval()
        with torch.no_grad():
            output = model(bf, nf, gf, act)
        normalized_mean = output.horizon_mean.detach().cpu().numpy()
        normalized_log_scale = output.horizon_log_scale.detach().cpu().numpy()
        physical_mean = normalized_mean * scale[None, :, :] + center[None, :, :]
        physical_standard_deviation = (
            np.exp(normalized_log_scale) * scale[None, :, :]
        )
        member_means.append(physical_mean)
        member_log_scales.append(np.log(physical_standard_deviation))
        member_probabilities.append(
            torch.sigmoid(output.executable_logit).detach().cpu().numpy()
        )

    member_means = np.stack(member_means, axis=0)
    member_log_scales = np.stack(member_log_scales, axis=0)
    reference_index = int(reference_matches[0])
    statistics = paired_ensemble_statistics(
        member_means,
        member_log_scales,
        member_means[:, reference_index],
        member_log_scales[:, reference_index],
    )
    if member_means.shape[0] > 1:
        marginal_epistemic = member_means.var(axis=0, ddof=1)
    else:
        marginal_epistemic = np.zeros_like(member_means[0])
    marginal_aleatoric = np.mean(np.exp(2.0 * member_log_scales), axis=0)
    candidate_base_scale = np.sqrt(
        np.maximum(marginal_epistemic + marginal_aleatoric, 1e-12)
    )
    executable_probability = np.stack(member_probabilities, axis=0).mean(axis=0)
    return EnsembleHorizonPrediction(
        actions=actions,
        mean_delta=statistics.mean_delta,
        paired_scale=statistics.paired_scale,
        executable_probability=executable_probability,
        candidate_mean=member_means.mean(axis=0),
        candidate_base_scale=candidate_base_scale,
        member_evaluations=int(member_means.shape[0] * actions.size),
        model_forward_count=int(member_means.shape[0]),
    )


def predict_paired_ensemble(
    ensemble,
    *,
    block_features,
    neighbour_features,
    global_features,
    actions,
    reference_action: int,
    planning_horizon: int,
    device: str = "cpu",
) -> EnsemblePrediction:
    if int(planning_horizon) not in HORIZONS:
        raise ValueError("planning horizon must be one of 1, 3, or 5")
    all_horizons = predict_paired_ensemble_all_horizons(
        ensemble,
        block_features=block_features,
        neighbour_features=neighbour_features,
        global_features=global_features,
        actions=actions,
        reference_action=reference_action,
        device=device,
    )
    horizon_index = HORIZONS.index(int(planning_horizon))
    paired_scale = all_horizons.paired_scale[:, horizon_index]
    return EnsemblePrediction(
        actions=all_horizons.actions,
        mean_delta=all_horizons.mean_delta[:, horizon_index],
        paired_scale=paired_scale,
        uncertainty_rank=paired_scale.max(axis=-1),
        executable_probability=all_horizons.executable_probability,
        candidate_mean=all_horizons.candidate_mean[:, horizon_index],
        candidate_base_scale=all_horizons.candidate_base_scale[:, horizon_index],
        member_evaluations=all_horizons.member_evaluations,
        model_forward_count=all_horizons.model_forward_count,
    )


def pcc_select_action(
    *,
    ensemble,
    calibrator,
    feedback_scaler,
    block_features,
    neighbour_features,
    global_features,
    executable_mask,
    reference_policy,
    proposal_groups,
    candidate_budget: int,
    planning_horizon: int,
    tolerances,
    executable_threshold: float,
    device: str = "cpu",
    max_member_evaluations: int | None = None,
):
    reference_action = int(reference_policy())
    try:
        actions = build_candidate_pool(
            reference_action=reference_action,
            proposal_groups=proposal_groups,
            executable_mask=executable_mask,
            candidate_budget=candidate_budget,
        )
        prediction = predict_paired_ensemble(
            ensemble,
            block_features=block_features,
            neighbour_features=neighbour_features,
            global_features=global_features,
            actions=actions,
            reference_action=reference_action,
            planning_horizon=planning_horizon,
            device=device,
        )
        if (
            max_member_evaluations is not None
            and prediction.member_evaluations > int(max_member_evaluations)
        ):
            raise ValueError("matched compute budget exceeded")
        online_multiplier = feedback_scaler.multiplier()
        lower_bounds = calibrator.lower_bounds(
            prediction.mean_delta,
            prediction.paired_scale,
            online_multiplier=online_multiplier,
        )
        selected_action, info = choose_from_bounds(
            prediction.actions,
            lower_bounds,
            prediction.executable_probability,
            prediction.uncertainty_rank,
            reference_action=reference_action,
            tolerances=tolerances,
            executable_threshold=executable_threshold,
        )
        selected_index = int(np.flatnonzero(prediction.actions == selected_action)[0])
        info.update(
            {
                "reference_action": reference_action,
                "joint_q": float(calibrator.q_joint),
                "online_multiplier": online_multiplier.tolist(),
                "member_evaluations": prediction.member_evaluations,
                "model_forward_count": prediction.model_forward_count,
                "selected_predicted_mean": prediction.candidate_mean[
                    selected_index
                ].tolist(),
                "selected_base_scale": prediction.candidate_base_scale[
                    selected_index
                ].tolist(),
                "unexecuted_real_reward_queries": 0,
            }
        )
        return selected_action, info
    except (ValueError, RuntimeError, FloatingPointError) as error:
        return reference_action, {
            "fallback": True,
            "fallback_reason": f"invalid_pcc_state:{error}",
            "admissible_actions": [],
            "reference_action": reference_action,
            "member_evaluations": 0,
            "model_forward_count": 0,
            "unexecuted_real_reward_queries": 0,
        }


def load_pcc_ensemble(checkpoint_root, device: str = "cpu"):
    from paper10_geojepa_mpc.training.pcc_training import load_pcc_checkpoint

    path = Path(checkpoint_root)
    checkpoints = [path] if path.is_file() else sorted(path.glob("member_*.pt"))
    if not checkpoints:
        raise ValueError(f"no PCC member checkpoints found under {path}")
    return [load_pcc_checkpoint(checkpoint, device=device) for checkpoint in checkpoints]
