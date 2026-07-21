from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.models.pcc_paired_delta import HORIZONS


@dataclass(frozen=True)
class DirectPairedStatistics:
    mean_delta: np.ndarray
    epistemic_variance: np.ndarray
    aleatoric_variance: np.ndarray
    paired_scale: np.ndarray


@dataclass(frozen=True)
class DirectEnsemblePrediction:
    actions: np.ndarray
    reference_action: int
    mean_delta: np.ndarray
    paired_scale: np.ndarray
    executable_probability: np.ndarray
    candidate_absolute_mean: np.ndarray
    candidate_absolute_scale: np.ndarray
    compute_mode: str
    member_evaluations: int
    model_forward_count: int


def direct_paired_statistics(
    member_means,
    member_log_scales,
) -> DirectPairedStatistics:
    means = np.asarray(member_means, dtype=np.float64)
    log_scales = np.asarray(member_log_scales, dtype=np.float64)
    if means.shape != log_scales.shape or means.ndim < 2:
        raise ValueError("direct member mean and log scale shapes must match")
    if not np.isfinite(means).all() or not np.isfinite(log_scales).all():
        raise ValueError("direct member predictions must be finite")
    mean_delta = means.mean(axis=0)
    epistemic = (
        means.var(axis=0, ddof=1)
        if means.shape[0] > 1
        else np.zeros_like(mean_delta)
    )
    aleatoric = np.mean(np.exp(2.0 * log_scales), axis=0)
    paired_scale = np.sqrt(np.maximum(epistemic + aleatoric, 1e-12))
    return DirectPairedStatistics(
        mean_delta=mean_delta,
        epistemic_variance=epistemic,
        aleatoric_variance=aleatoric,
        paired_scale=paired_scale,
    )


def choose_base_candidate(
    actions,
    mean_delta,
    *,
    scales,
    executable_probability,
    tolerances,
    executable_threshold: float,
):
    actions = np.asarray(actions, dtype=np.int64).reshape(-1)
    means = np.asarray(mean_delta, dtype=np.float64)
    scales = np.asarray(scales, dtype=np.float64)
    probability = np.asarray(
        executable_probability,
        dtype=np.float64,
    ).reshape(-1)
    tolerances = np.asarray(tolerances, dtype=np.float64).reshape(-1)
    if means.shape != (actions.size, 4) or scales.shape != means.shape:
        raise ValueError("base-selection means and scales must have shape [n, 4]")
    if probability.shape != actions.shape:
        raise ValueError("executable probability must align with actions")
    if tolerances.shape != (3,) or np.any(tolerances < 0.0):
        raise ValueError("planning tolerances must contain three non-negative values")
    if not 0.0 <= float(executable_threshold) <= 1.0:
        raise ValueError("executable threshold must be in [0, 1]")
    if actions.size and np.unique(actions).size != actions.size:
        raise ValueError("base-selection actions must be unique")
    if not all(
        np.isfinite(value).all()
        for value in (means, scales, probability, tolerances)
    ) or np.any(scales < 0.0):
        raise ValueError("base-selection inputs must be finite")

    executable_indexes = np.flatnonzero(
        probability >= float(executable_threshold)
    )
    if executable_indexes.size == 0:
        return None, {
            "base_selection_reason": "no_executable_alternative",
            "executable_actions": [],
            "mean_safe_actions": [],
        }
    mean_safe_mask = np.all(
        means[executable_indexes, 1:] >= -tolerances,
        axis=1,
    )
    mean_safe_indexes = executable_indexes[mean_safe_mask]
    if mean_safe_indexes.size == 0:
        return None, {
            "base_selection_reason": "no_mean_safe_candidate",
            "executable_actions": [
                int(actions[index]) for index in executable_indexes
            ],
            "mean_safe_actions": [],
        }
    selected_index = sorted(
        mean_safe_indexes.tolist(),
        key=lambda index: (
            -float(means[index, 0]),
            -float(means[index, 1:].min()),
            float(scales[index, 1:].max()),
            int(actions[index]),
        ),
    )[0]
    if float(means[selected_index, 0]) < 0.0:
        return None, {
            "base_selection_reason": "reference_reward_dominates",
            "executable_actions": [
                int(actions[index]) for index in executable_indexes
            ],
            "mean_safe_actions": [
                int(actions[index]) for index in mean_safe_indexes
            ],
        }
    return int(actions[selected_index]), {
        "base_selection_reason": "reward_mean_among_mean_safe",
        "base_selected_index": int(selected_index),
        "executable_actions": [
            int(actions[index]) for index in executable_indexes
        ],
        "mean_safe_actions": [
            int(actions[index]) for index in mean_safe_indexes
        ],
    }


def candidate_budget(*, compute_mode: str, ensemble_size: int) -> int:
    ensemble_size = int(ensemble_size)
    if ensemble_size <= 0:
        raise ValueError("ensemble size must be positive")
    if compute_mode == "matched":
        return 50 // ensemble_size
    if compute_mode == "full":
        return 50
    raise ValueError("compute mode must be matched or full")


def build_v1_1_candidate_pool(
    *,
    reference_action: int,
    proposal_groups,
    executable_mask,
    compute_mode: str,
    ensemble_size: int,
) -> np.ndarray:
    mask = np.asarray(executable_mask, dtype=bool).reshape(-1)
    reference_action = int(reference_action)
    if (
        reference_action < 0
        or reference_action >= mask.size
        or not mask[reference_action]
    ):
        raise ValueError("reference action must be executable")
    budget = candidate_budget(
        compute_mode=compute_mode,
        ensemble_size=ensemble_size,
    )
    ordered = []
    seen = {reference_action}
    for group in proposal_groups:
        for raw_action in group:
            action = int(raw_action)
            if (
                action < 0
                or action >= mask.size
                or not mask[action]
                or action in seen
            ):
                continue
            ordered.append(action)
            seen.add(action)
    for raw_action in np.flatnonzero(mask):
        action = int(raw_action)
        if action not in seen:
            ordered.append(action)
            seen.add(action)
    return np.asarray(ordered[:budget], dtype=np.int64)


def _checkpoint_scaling(checkpoint, field: str, shape: tuple[int, ...]):
    try:
        scaling = checkpoint[field]
        center = np.asarray(scaling["center"], dtype=np.float64)
        scale = np.asarray(scaling["scale"], dtype=np.float64)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid {field}") from error
    if center.shape != shape or scale.shape != shape:
        raise ValueError(f"invalid {field} shape")
    if not np.isfinite(center).all() or not np.isfinite(scale).all():
        raise ValueError(f"invalid {field}: values must be finite")
    if np.any(scale <= 0.0):
        raise ValueError(f"invalid {field}: scale must be positive")
    return center, scale


def predict_direct_paired_ensemble(
    ensemble,
    *,
    block_features,
    neighbour_features,
    global_features,
    actions,
    reference_action: int,
    compute_mode: str,
    device: str = "cpu",
) -> DirectEnsemblePrediction:
    actions = np.asarray(actions, dtype=np.int64).reshape(-1)
    reference_action = int(reference_action)
    if actions.size == 0 or np.unique(actions).size != actions.size:
        raise ValueError("alternative actions must be non-empty and unique")
    if np.any(actions == reference_action):
        raise ValueError("alternative actions must exclude the reference")
    if not ensemble:
        raise ValueError("direct ensemble must contain at least one member")
    budget = candidate_budget(
        compute_mode=compute_mode,
        ensemble_size=len(ensemble),
    )
    if actions.size > budget:
        raise ValueError("candidate count exceeds the compute-mode budget")

    block = np.asarray(block_features, dtype=np.float32)
    neighbour = np.asarray(neighbour_features, dtype=np.float32)
    global_array = np.asarray(global_features, dtype=np.float32)
    if (
        block.ndim != 2
        or neighbour.shape != block.shape
        or global_array.ndim != 1
    ):
        raise ValueError("observable feature shapes are invalid")
    batch_size = actions.size
    device_object = torch.device(device)
    block_tensor = torch.as_tensor(
        np.repeat(block[None, ...], batch_size, axis=0),
        dtype=torch.float32,
        device=device_object,
    )
    neighbour_tensor = torch.as_tensor(
        np.repeat(neighbour[None, ...], batch_size, axis=0),
        dtype=torch.float32,
        device=device_object,
    )
    global_tensor = torch.as_tensor(
        np.repeat(global_array[None, ...], batch_size, axis=0),
        dtype=torch.float32,
        device=device_object,
    )
    candidate_tensor = torch.as_tensor(
        actions,
        dtype=torch.long,
        device=device_object,
    )
    reference_tensor = torch.full_like(candidate_tensor, reference_action)

    member_means = []
    member_log_scales = []
    member_absolute_means = []
    member_absolute_log_scales = []
    member_probabilities = []
    expected_delta = None
    expected_absolute = None
    for model, checkpoint in ensemble:
        delta_center, delta_scale = _checkpoint_scaling(
            checkpoint,
            "delta_scaling",
            (len(HORIZONS), len(OBJECTIVE_NAMES)),
        )
        absolute_center, absolute_scale = _checkpoint_scaling(
            checkpoint,
            "absolute_scaling",
            (len(OBJECTIVE_NAMES),),
        )
        observed_delta = (delta_center, delta_scale)
        observed_absolute = (absolute_center, absolute_scale)
        if expected_delta is None:
            expected_delta = observed_delta
            expected_absolute = observed_absolute
        elif not all(
            np.array_equal(observed, expected)
            for observed, expected in zip(observed_delta, expected_delta)
        ):
            raise ValueError("ensemble members use inconsistent delta_scaling")
        elif not all(
            np.array_equal(observed, expected)
            for observed, expected in zip(
                observed_absolute,
                expected_absolute,
            )
        ):
            raise ValueError("ensemble members use inconsistent absolute_scaling")

        model = model.to(device_object)
        model.eval()
        with torch.no_grad():
            output = model(
                block_tensor,
                neighbour_tensor,
                global_tensor,
                candidate_tensor,
                reference_tensor,
            )
        normalized_mean = output.delta_mean.detach().cpu().numpy()
        normalized_log_scale = output.delta_log_scale.detach().cpu().numpy()
        member_means.append(
            normalized_mean * delta_scale[None, :, :]
            + delta_center[None, :, :]
        )
        member_log_scales.append(
            normalized_log_scale + np.log(delta_scale)[None, :, :]
        )
        normalized_absolute = (
            output.candidate_absolute_mean.detach().cpu().numpy()
        )
        normalized_absolute_log_scale = (
            output.candidate_absolute_log_scale.detach().cpu().numpy()
        )
        member_absolute_means.append(
            normalized_absolute * absolute_scale[None, :]
            + absolute_center[None, :]
        )
        member_absolute_log_scales.append(
            normalized_absolute_log_scale
            + np.log(absolute_scale)[None, :]
        )
        member_probabilities.append(
            torch.sigmoid(output.executable_logit).detach().cpu().numpy()
        )

    delta_statistics = direct_paired_statistics(
        np.stack(member_means, axis=0),
        np.stack(member_log_scales, axis=0),
    )
    absolute_statistics = direct_paired_statistics(
        np.stack(member_absolute_means, axis=0),
        np.stack(member_absolute_log_scales, axis=0),
    )
    return DirectEnsemblePrediction(
        actions=actions,
        reference_action=reference_action,
        mean_delta=delta_statistics.mean_delta,
        paired_scale=delta_statistics.paired_scale,
        executable_probability=np.stack(
            member_probabilities,
            axis=0,
        ).mean(axis=0),
        candidate_absolute_mean=absolute_statistics.mean_delta,
        candidate_absolute_scale=absolute_statistics.paired_scale,
        compute_mode=str(compute_mode),
        member_evaluations=int(len(ensemble) * actions.size),
        model_forward_count=int(len(ensemble)),
    )


def _prediction_log_fields(prediction) -> dict[str, object]:
    return {
        "reference_action": int(prediction.reference_action),
        "compute_mode": str(prediction.compute_mode),
        "candidate_count": int(prediction.actions.size),
        "member_evaluations": int(prediction.member_evaluations),
        "model_forward_count": int(prediction.model_forward_count),
        "unexecuted_real_reward_queries": 0,
    }


def select_with_certificate(
    prediction: DirectEnsemblePrediction,
    calibrator,
    *,
    tolerances=None,
    executable_threshold: float = 0.95,
    feedback_multiplier=None,
):
    tolerances = np.asarray(
        np.zeros(3) if tolerances is None else tolerances,
        dtype=np.float64,
    ).reshape(-1)
    feedback = np.asarray(
        np.ones(4) if feedback_multiplier is None else feedback_multiplier,
        dtype=np.float64,
    ).reshape(-1)
    if tolerances.shape != (3,) or np.any(tolerances < 0.0):
        raise ValueError("planning tolerances must contain three non-negative values")
    if (
        feedback.shape != (4,)
        or not np.isfinite(feedback).all()
        or np.any(feedback <= 0.0)
    ):
        raise ValueError("feedback multiplier must contain four positive values")
    planning_horizon = int(calibrator.planning_horizon)
    if planning_horizon not in HORIZONS:
        raise ValueError("calibrator planning horizon must be 1, 3, or 5")
    q_planning = float(calibrator.q_planning)
    if not np.isfinite(q_planning) or q_planning < 0.0:
        raise ValueError("planning calibration multiplier must be non-negative")
    horizon_index = HORIZONS.index(planning_horizon)
    selected_action, base_info = choose_base_candidate(
        prediction.actions,
        prediction.mean_delta[:, horizon_index],
        scales=prediction.paired_scale[:, horizon_index],
        executable_probability=prediction.executable_probability,
        tolerances=tolerances,
        executable_threshold=executable_threshold,
    )
    info = {
        **_prediction_log_fields(prediction),
        **base_info,
        "base_selected_action": selected_action,
        "planning_horizon": planning_horizon,
        "coverage": float(calibrator.coverage),
        "q_planning": q_planning,
        "feedback_multiplier": feedback.tolist(),
        "planning_lower_bounds": [None, None, None],
    }
    if selected_action is None:
        reason = str(base_info["base_selection_reason"])
        info.update(
            {
                "fallback": True,
                "fallback_reason": reason,
                "decision_reason": reason,
                "certificate_passed": False,
            }
        )
        return int(prediction.reference_action), info

    selected_index = int(
        np.flatnonzero(prediction.actions == int(selected_action))[0]
    )
    selected_mean = prediction.mean_delta[selected_index, horizon_index]
    selected_scale = prediction.paired_scale[selected_index, horizon_index]
    planning_lower = (
        selected_mean[1:]
        - q_planning * selected_scale[1:] * feedback[1:]
    )
    certified = bool(np.all(planning_lower >= -tolerances))
    reason = (
        "selected_candidate"
        if certified
        else "planning_certificate_rejected"
    )
    info.update(
        {
            "fallback": not certified,
            "fallback_reason": None if certified else reason,
            "decision_reason": reason,
            "certificate_passed": certified,
            "planning_lower_bounds": planning_lower.tolist(),
            "selected_executable_probability": float(
                prediction.executable_probability[selected_index]
            ),
            "selected_predicted_delta": prediction.mean_delta[
                selected_index
            ].tolist(),
            "selected_predicted_scale": prediction.paired_scale[
                selected_index
            ].tolist(),
            "selected_absolute_mean": prediction.candidate_absolute_mean[
                selected_index
            ].tolist(),
            "selected_absolute_scale": prediction.candidate_absolute_scale[
                selected_index
            ].tolist(),
        }
    )
    action = selected_action if certified else prediction.reference_action
    return int(action), info


def _empty_decision_info(
    *,
    reference_action,
    compute_mode,
    reason,
    candidate_count,
    member_evaluations=0,
    model_forward_count=0,
) -> dict[str, object]:
    return {
        "fallback": True,
        "fallback_reason": str(reason),
        "decision_reason": str(reason),
        "certificate_passed": False,
        "base_selection_reason": None,
        "base_selected_action": None,
        "reference_action": int(reference_action),
        "compute_mode": str(compute_mode),
        "candidate_count": int(candidate_count),
        "member_evaluations": int(member_evaluations),
        "model_forward_count": int(model_forward_count),
        "planning_lower_bounds": [None, None, None],
        "unexecuted_real_reward_queries": 0,
    }


def pcc_v1_1_select_action(
    *,
    ensemble,
    calibrator,
    block_features,
    neighbour_features,
    global_features,
    executable_mask,
    reference_policy,
    proposal_groups,
    compute_mode: str,
    tolerances,
    executable_threshold: float,
    feedback_multiplier=None,
    device: str = "cpu",
):
    reference_action = int(reference_policy())
    actions = np.asarray([], dtype=np.int64)
    prediction = None
    try:
        actions = build_v1_1_candidate_pool(
            reference_action=reference_action,
            proposal_groups=proposal_groups,
            executable_mask=executable_mask,
            compute_mode=compute_mode,
            ensemble_size=len(ensemble),
        )
        if actions.size == 0:
            return reference_action, _empty_decision_info(
                reference_action=reference_action,
                compute_mode=compute_mode,
                reason="no_executable_alternative",
                candidate_count=0,
            )
        prediction = predict_direct_paired_ensemble(
            ensemble,
            block_features=block_features,
            neighbour_features=neighbour_features,
            global_features=global_features,
            actions=actions,
            reference_action=reference_action,
            compute_mode=compute_mode,
            device=device,
        )
        return select_with_certificate(
            prediction,
            calibrator,
            tolerances=tolerances,
            executable_threshold=executable_threshold,
            feedback_multiplier=feedback_multiplier,
        )
    except (ValueError, RuntimeError, FloatingPointError) as error:
        reason = f"invalid_pcc_v1_1_state:{error}"
        return reference_action, _empty_decision_info(
            reference_action=reference_action,
            compute_mode=compute_mode,
            reason=reason,
            candidate_count=actions.size,
            member_evaluations=(
                0 if prediction is None else prediction.member_evaluations
            ),
            model_forward_count=(
                0 if prediction is None else prediction.model_forward_count
            ),
        )


def load_pcc_v1_1_ensemble(checkpoint_root, device: str = "cpu"):
    from paper10_geojepa_mpc.training.pcc_v1_1_training import (
        load_pcc_v1_1_checkpoint,
    )

    root = Path(checkpoint_root)
    paths = [root] if root.is_file() else sorted(root.glob("member_*.pt"))
    if not paths:
        raise ValueError(f"no PCC v1.1 checkpoints found under {root}")
    ensemble = [
        load_pcc_v1_1_checkpoint(path, device=device) for path in paths
    ]
    declared_sizes = {
        int(checkpoint.get("ensemble_size", -1))
        for _, checkpoint in ensemble
    }
    indexes = [
        int(checkpoint.get("member_index", -1))
        for _, checkpoint in ensemble
    ]
    model_seeds = {
        int(checkpoint.get("model_seed", -1)) for _, checkpoint in ensemble
    }
    lineage_fields = (
        "registry_digest",
        "source_manifest_digest",
        "transfer_checkpoint_sha256",
    )
    lineages = {
        tuple(checkpoint.get(field) for field in lineage_fields)
        for _, checkpoint in ensemble
    }
    if declared_sizes != {len(ensemble)} or indexes != list(
        range(len(ensemble))
    ):
        raise ValueError("incomplete PCC v1.1 ensemble member inventory")
    if len(model_seeds) != 1 or -1 in model_seeds:
        raise ValueError("inconsistent PCC v1.1 ensemble model seed")
    if len(lineages) != 1 or any(
        not isinstance(value, str) or not value
        for value in next(iter(lineages))
    ):
        raise ValueError("inconsistent PCC v1.1 ensemble lineage")
    return ensemble
