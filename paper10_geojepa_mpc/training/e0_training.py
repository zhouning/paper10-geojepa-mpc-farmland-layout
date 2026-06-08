from pathlib import Path
from typing import Dict, Optional

import numpy as np
import torch
import torch.nn.functional as F

from paper10_geojepa_mpc.models.geojepa_transition_model import GeoJEPATransitionModel
from paper10_geojepa_mpc.models.sigreg import sigreg_loss
from paper10_geojepa_mpc.planning.scoring import (
    scalar_score_from_model_output,
    score_candidate_actions,
)
from paper10_geojepa_mpc.training.ranking import (
    pairwise_margin_ranking_loss,
    pairwise_rank_accuracy,
)


def load_npz_arrays(
    path: str | Path, max_rows: Optional[int] = None
) -> Dict[str, np.ndarray]:
    with np.load(Path(path)) as data:
        arrays = {}
        for key in data.files:
            array = data[key]
            if max_rows is not None and array.shape[0] > max_rows:
                array = array[:max_rows].copy()
            arrays[key] = array
        return arrays


def _ensure_column(values: torch.Tensor) -> torch.Tensor:
    if values.ndim == 1:
        return values.unsqueeze(-1)
    return values


def transition_mse_loss(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    rewards: torch.Tensor,
    next_block_features: torch.Tensor,
    next_global_features: torch.Tensor,
    geofm_features: Optional[torch.Tensor] = None,
    return_aux: bool = False,
):
    pred_nbf, pred_ngf, pred_rewards, aux = model(
        block_features, global_features, actions, geofm_features=geofm_features
    )
    rewards = _ensure_column(rewards)

    block_mse = F.mse_loss(pred_nbf - block_features, next_block_features - block_features)
    global_mse = F.mse_loss(
        pred_ngf - global_features, next_global_features - global_features
    )
    reward_mse = F.mse_loss(pred_rewards, rewards)
    loss = block_mse + global_mse + 0.1 * reward_mse

    metrics = {
        "block_mse": float(block_mse.detach().cpu()),
        "global_mse": float(global_mse.detach().cpu()),
        "reward_mse": float(reward_mse.detach().cpu()),
    }
    if return_aux:
        return loss, metrics, aux
    return loss, metrics


def pairwise_ranking_loss_for_batch(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    rewards: torch.Tensor,
    n_pairs: int = 8,
    margin: float = 0.1,
    generator: Optional[torch.Generator] = None,
    score_mode: str = "reward",
    value_weight: float = 0.5,
):
    n_states, n_actions = actions.shape
    device = actions.device
    pair_i = torch.randint(
        0, n_actions, (n_states, n_pairs), device=device, generator=generator
    )
    pair_j = torch.randint(
        0, n_actions, (n_states, n_pairs), device=device, generator=generator
    )

    flat_i = pair_i.reshape(-1)
    flat_j = pair_j.reshape(-1)
    state_idx = (
        torch.arange(n_states, device=device)
        .unsqueeze(1)
        .expand(n_states, n_pairs)
        .reshape(-1)
    )

    bf_flat = block_features[state_idx]
    gf_flat = global_features[state_idx]
    action_i = actions[state_idx, flat_i]
    action_j = actions[state_idx, flat_j]
    true_i = rewards[state_idx, flat_i]
    true_j = rewards[state_idx, flat_j]

    _, _, reward_i, aux_i = model(bf_flat, gf_flat, action_i)
    _, _, reward_j, aux_j = model(bf_flat, gf_flat, action_j)
    pred_i = scalar_score_from_model_output(
        reward_i,
        aux_i,
        score_mode=score_mode,
        value_weight=value_weight,
    ).squeeze(-1)
    pred_j = scalar_score_from_model_output(
        reward_j,
        aux_j,
        score_mode=score_mode,
        value_weight=value_weight,
    ).squeeze(-1)

    loss = pairwise_margin_ranking_loss(pred_i, pred_j, true_i, true_j, margin=margin)
    accuracy = pairwise_rank_accuracy(pred_i.detach(), pred_j.detach(), true_i, true_j)
    return loss, accuracy


def evaluate_pairwise_rank_accuracy(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    rewards: torch.Tensor,
    max_states: int = 64,
    n_pairs: int = 16,
    eval_seed: int = 12345,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> float:
    was_training = model.training
    model.eval()
    with torch.no_grad():
        n = min(max_states, block_features.shape[0])
        _, accuracy = pairwise_ranking_loss_for_batch(
            model,
            block_features[:n],
            global_features[:n],
            actions[:n],
            rewards[:n],
            n_pairs=n_pairs,
            generator=torch.Generator(device=block_features.device).manual_seed(eval_seed),
            score_mode=score_mode,
            value_weight=value_weight,
        )
    if was_training:
        model.train()
    return accuracy


def evaluate_candidate_action_metrics(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    rewards: torch.Tensor,
    top_k: int = 5,
    batch_states: int = 4,
    max_states: Optional[int] = None,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> Dict[str, float]:
    if batch_states <= 0:
        raise ValueError("batch_states must be positive")

    n_states = block_features.shape[0]
    if max_states is not None:
        n_states = min(n_states, max_states)
    n_actions = actions.shape[1]
    top_k = min(top_k, n_actions)

    was_training = model.training
    model.eval()

    top1_hits = 0.0
    topk_hits = 0.0
    top1_regret_sum = 0.0
    topk_regret_sum = 0.0

    with torch.no_grad():
        for start in range(0, n_states, batch_states):
            end = min(start + batch_states, n_states)
            bf_chunk = block_features[start:end]
            gf_chunk = global_features[start:end]
            actions_chunk = actions[start:end]
            rewards_chunk = rewards[start:end]
            pred_scores = score_candidate_actions(
                model,
                bf_chunk,
                gf_chunk,
                actions_chunk,
                score_mode=score_mode,
                value_weight=value_weight,
            )

            true_best_values, true_best_idx = rewards_chunk.max(dim=1)
            pred_topk_idx = pred_scores.topk(top_k, dim=1).indices
            pred_top1_idx = pred_topk_idx[:, 0]

            top1_true_values = rewards_chunk.gather(
                1, pred_top1_idx.unsqueeze(1)
            ).squeeze(1)
            topk_true_values = rewards_chunk.gather(1, pred_topk_idx).max(dim=1).values

            top1_hits += (pred_top1_idx == true_best_idx).float().sum().item()
            topk_hits += (
                pred_topk_idx == true_best_idx.unsqueeze(1)
            ).any(dim=1).float().sum().item()
            top1_regret_sum += (true_best_values - top1_true_values).sum().item()
            topk_regret_sum += (true_best_values - topk_true_values).sum().item()

    if was_training:
        model.train()

    denom = float(n_states)
    return {
        "candidate_states": int(n_states),
        "candidate_actions": int(n_actions),
        "candidate_top_k": int(top_k),
        "candidate_top1_hit_rate": top1_hits / denom,
        f"candidate_top{top_k}_hit_rate": topk_hits / denom,
        "candidate_top1_regret": top1_regret_sum / denom,
        f"candidate_top{top_k}_regret": topk_regret_sum / denom,
    }


def _to_tensor(array: np.ndarray, device: torch.device, dtype=None) -> torch.Tensor:
    return torch.tensor(array, device=device, dtype=dtype)


def _pairwise_label_key(pairwise_data: Dict[str, np.ndarray]) -> str:
    if "returns" in pairwise_data:
        return "returns"
    if "rewards" in pairwise_data:
        return "rewards"
    raise KeyError("pairwise data must contain either 'returns' or 'rewards'")


def _state_dict_cpu(model) -> Dict[str, torch.Tensor]:
    return {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}


def _set_trainable_scope(model, trainable_scope: str) -> list[str]:
    if trainable_scope not in {"all", "reward_head", "value_head"}:
        raise ValueError(
            "trainable_scope must be 'all', 'reward_head', or 'value_head'"
        )

    trainable = []
    for name, parameter in model.named_parameters():
        is_trainable = (
            trainable_scope == "all"
            or name.startswith(f"{trainable_scope}.")
        )
        parameter.requires_grad = is_trainable
        if is_trainable:
            trainable.append(name)
    if not trainable:
        raise ValueError(f"No trainable parameters for scope: {trainable_scope}")
    return trainable


def _metric_improved(value: float, best_value: Optional[float], mode: str) -> bool:
    if mode not in {"min", "max"}:
        raise ValueError("checkpoint_mode must be 'min' or 'max'")
    if best_value is None:
        return True
    if mode == "min":
        return value < best_value
    return value > best_value


def _save_e0_checkpoint(
    checkpoint_path: Path,
    model,
    model_kwargs: Dict[str, object],
    epoch: int,
    checkpoint_metric: str,
    checkpoint_value: float,
    metrics: Dict[str, float],
    init_checkpoint_path: Optional[str] = None,
    trainable_scope: str = "all",
    rank_score_mode: str = "reward",
    rank_value_weight: float = 0.5,
) -> None:
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": model_kwargs,
            "state_dict": _state_dict_cpu(model),
            "epoch": epoch,
            "checkpoint_metric": checkpoint_metric,
            "checkpoint_value": checkpoint_value,
            "metrics": metrics,
            "init_checkpoint_path": init_checkpoint_path,
            "trainable_scope": trainable_scope,
            "rank_score_mode": rank_score_mode,
            "rank_value_weight": float(rank_value_weight),
        },
        checkpoint_path,
    )


def load_e0_checkpoint(path: str | Path, device: str = "cpu"):
    checkpoint = torch.load(Path(path), map_location=device, weights_only=False)
    if checkpoint.get("model_class") != "GeoJEPATransitionModel":
        raise ValueError(f"Unsupported checkpoint model: {checkpoint.get('model_class')}")
    model = GeoJEPATransitionModel(**checkpoint["model_kwargs"]).to(device)
    loaded_state = dict(checkpoint["state_dict"])
    model_state = model.state_dict()
    missing_keys = [key for key in model_state if key not in loaded_state]
    for key in missing_keys:
        if key.startswith("value_head."):
            reward_key = key.replace("value_head.", "reward_head.", 1)
            if reward_key in loaded_state and loaded_state[reward_key].shape == model_state[key].shape:
                loaded_state[key] = loaded_state[reward_key].detach().clone()
    load_result = model.load_state_dict(loaded_state, strict=False)
    if load_result.unexpected_keys:
        raise ValueError(
            f"Unexpected checkpoint state keys: {list(load_result.unexpected_keys)}"
        )
    if load_result.missing_keys:
        raise ValueError(f"Missing checkpoint state keys: {list(load_result.missing_keys)}")
    checkpoint = dict(checkpoint)
    checkpoint["missing_state_keys"] = missing_keys
    model.eval()
    return model, checkpoint


def train_e0_smoke_config(
    transition_path: str | Path,
    pairwise_path: str | Path,
    n_blocks: int,
    k_global: int,
    epochs: int = 3,
    batch_size: int = 64,
    lr: float = 1e-3,
    lambda_rank: float = 0.0,
    lambda_sig: float = 0.0,
    n_pairs: int = 8,
    margin: float = 0.1,
    pairwise_subsample: int = 32,
    max_transition_samples: Optional[int] = None,
    max_pairwise_states: Optional[int] = None,
    compute_candidate_metrics: bool = False,
    candidate_top_k: int = 5,
    candidate_batch_states: int = 4,
    candidate_max_states: Optional[int] = None,
    checkpoint_path: Optional[str | Path] = None,
    checkpoint_metric: str = "candidate_top5_regret",
    checkpoint_mode: str = "min",
    init_checkpoint_path: Optional[str | Path] = None,
    trainable_scope: str = "all",
    rank_score_mode: str = "reward",
    rank_value_weight: float = 0.5,
    seed: int = 0,
    eval_seed: int = 12345,
    device: str = "cpu",
) -> Dict[str, float]:
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    if rank_score_mode not in {"reward", "value", "blend"}:
        raise ValueError("rank_score_mode must be 'reward', 'value', or 'blend'")
    if not 0.0 <= rank_value_weight <= 1.0:
        raise ValueError("rank_value_weight must be in [0, 1]")

    torch.manual_seed(seed)
    np.random.seed(seed)
    device_obj = torch.device(device)

    transition_data = load_npz_arrays(transition_path, max_rows=max_transition_samples)
    pairwise_data = load_npz_arrays(pairwise_path, max_rows=max_pairwise_states)

    bf = _to_tensor(transition_data["block_features"], device_obj, torch.float32)
    gf = _to_tensor(transition_data["global_features"], device_obj, torch.float32)
    actions = _to_tensor(transition_data["actions"], device_obj, torch.long)
    rewards = _ensure_column(
        _to_tensor(transition_data["rewards"], device_obj, torch.float32)
    )
    nbf = _to_tensor(transition_data["next_block_features"], device_obj, torch.float32)
    ngf = _to_tensor(transition_data["next_global_features"], device_obj, torch.float32)

    pw_bf = _to_tensor(pairwise_data["states_bf"], device_obj, torch.float32)
    pw_gf = _to_tensor(pairwise_data["states_gf"], device_obj, torch.float32)
    pw_actions = _to_tensor(pairwise_data["actions"], device_obj, torch.long)
    pairwise_label_key = _pairwise_label_key(pairwise_data)
    pw_rewards = _to_tensor(pairwise_data[pairwise_label_key], device_obj, torch.float32)

    model_kwargs = {
        "n_blocks": n_blocks,
        "k_global": k_global,
        "block_feature_dim": bf.shape[-1],
    }
    init_checkpoint_path_obj = (
        Path(init_checkpoint_path) if init_checkpoint_path is not None else None
    )
    if init_checkpoint_path_obj is None:
        model = GeoJEPATransitionModel(
            n_blocks=n_blocks,
            k_global=k_global,
            block_feature_dim=bf.shape[-1],
        ).to(device_obj)
    else:
        model, init_checkpoint = load_e0_checkpoint(
            init_checkpoint_path_obj, device=str(device_obj)
        )
        if init_checkpoint["model_kwargs"] != model_kwargs:
            raise ValueError(
                "init checkpoint model_kwargs do not match requested training config"
            )
        model.train()
    trainable_parameter_names = _set_trainable_scope(model, trainable_scope)
    optimizer = torch.optim.Adam(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=lr,
    )
    generator = torch.Generator(device=device_obj).manual_seed(seed)

    final_loss = None
    final_mse = None
    final_rank_loss = 0.0
    final_sig_loss = 0.0
    final_train_rank_acc = 0.5
    n_samples = bf.shape[0]
    checkpoint_path_obj = Path(checkpoint_path) if checkpoint_path is not None else None
    best_checkpoint_epoch = None
    best_checkpoint_value = None

    for epoch in range(1, epochs + 1):
        model.train()
        permutation = torch.randperm(n_samples, device=device_obj, generator=generator)
        for start in range(0, n_samples, batch_size):
            idx = permutation[start : start + batch_size]
            optimizer.zero_grad()

            mse_loss, mse_metrics, aux = transition_mse_loss(
                model,
                bf[idx],
                gf[idx],
                actions[idx],
                rewards[idx],
                nbf[idx],
                ngf[idx],
                return_aux=True,
            )

            if lambda_rank > 0:
                n_pw = pw_bf.shape[0]
                sub_n = min(pairwise_subsample, n_pw)
                pw_idx = torch.randperm(
                    n_pw, device=device_obj, generator=generator
                )[:sub_n]
                rank_loss, train_rank_acc = pairwise_ranking_loss_for_batch(
                    model,
                    pw_bf[pw_idx],
                    pw_gf[pw_idx],
                    pw_actions[pw_idx],
                    pw_rewards[pw_idx],
                    n_pairs=n_pairs,
                    margin=margin,
                    generator=generator,
                    score_mode=rank_score_mode,
                    value_weight=rank_value_weight,
                )
            else:
                rank_loss = bf.new_tensor(0.0)
                train_rank_acc = 0.5

            if lambda_sig > 0:
                sig_loss = sigreg_loss(aux["latent"], n_projections=32, n_knots=16)
            else:
                sig_loss = bf.new_tensor(0.0)

            total_loss = mse_loss + lambda_rank * rank_loss + lambda_sig * sig_loss
            total_loss.backward()
            optimizer.step()

            final_loss = float(total_loss.detach().cpu())
            final_mse = float(mse_loss.detach().cpu())
            final_rank_loss = float(rank_loss.detach().cpu())
            final_sig_loss = float(sig_loss.detach().cpu())
            final_train_rank_acc = float(train_rank_acc)

        if checkpoint_path_obj is not None:
            checkpoint_metrics = {
                "final_loss": final_loss,
                "final_mse": final_mse,
                "final_rank_loss": final_rank_loss,
                "final_sig_loss": final_sig_loss,
                "ranking_acc": evaluate_pairwise_rank_accuracy(
                    model,
                    pw_bf,
                    pw_gf,
                    pw_actions,
                    pw_rewards,
                    n_pairs=n_pairs,
                    eval_seed=eval_seed,
                    score_mode=rank_score_mode,
                    value_weight=rank_value_weight,
                ),
            }
            if compute_candidate_metrics:
                checkpoint_metrics.update(
                    evaluate_candidate_action_metrics(
                        model,
                        pw_bf,
                        pw_gf,
                        pw_actions,
                        pw_rewards,
                        top_k=candidate_top_k,
                        batch_states=candidate_batch_states,
                        max_states=candidate_max_states,
                        score_mode=rank_score_mode,
                        value_weight=rank_value_weight,
                    )
                )
            if checkpoint_metric not in checkpoint_metrics:
                raise ValueError(f"checkpoint_metric not available: {checkpoint_metric}")
            checkpoint_value = float(checkpoint_metrics[checkpoint_metric])
            if _metric_improved(checkpoint_value, best_checkpoint_value, checkpoint_mode):
                best_checkpoint_value = checkpoint_value
                best_checkpoint_epoch = epoch
                _save_e0_checkpoint(
                    checkpoint_path_obj,
                    model,
                    model_kwargs,
                    epoch,
                    checkpoint_metric,
                    checkpoint_value,
                    checkpoint_metrics,
                    str(init_checkpoint_path_obj) if init_checkpoint_path_obj else None,
                    trainable_scope,
                    rank_score_mode,
                    rank_value_weight,
                )

    ranking_acc = evaluate_pairwise_rank_accuracy(
        model,
        pw_bf,
        pw_gf,
        pw_actions,
        pw_rewards,
        n_pairs=n_pairs,
        eval_seed=eval_seed,
        score_mode=rank_score_mode,
        value_weight=rank_value_weight,
    )

    result = {
        "epochs": epochs,
        "final_loss": final_loss,
        "final_mse": final_mse,
        "final_rank_loss": final_rank_loss,
        "final_sig_loss": final_sig_loss,
        "train_ranking_acc": final_train_rank_acc,
        "ranking_acc": float(ranking_acc),
        "lambda_rank": float(lambda_rank),
        "lambda_sig": float(lambda_sig),
        "n_transition_samples": int(n_samples),
        "n_pairwise_states": int(pw_bf.shape[0]),
        "pairwise_label_key": pairwise_label_key,
        "trainable_scope": trainable_scope,
        "rank_score_mode": rank_score_mode,
        "rank_value_weight": float(rank_value_weight),
        "n_trainable_parameters": int(
            sum(
                parameter.numel()
                for parameter in model.parameters()
                if parameter.requires_grad
            )
        ),
        "eval_seed": int(eval_seed),
    }
    if init_checkpoint_path_obj is not None:
        result["init_checkpoint_path"] = str(init_checkpoint_path_obj)
    if compute_candidate_metrics:
        result.update(
            evaluate_candidate_action_metrics(
                model,
                pw_bf,
                pw_gf,
                pw_actions,
                pw_rewards,
                top_k=candidate_top_k,
                batch_states=candidate_batch_states,
                max_states=candidate_max_states,
                score_mode=rank_score_mode,
                value_weight=rank_value_weight,
            )
        )
    if checkpoint_path_obj is not None:
        result.update(
            {
                "checkpoint_path": str(checkpoint_path_obj),
                "best_checkpoint_epoch": int(best_checkpoint_epoch),
                "best_checkpoint_metric": checkpoint_metric,
                "best_checkpoint_value": float(best_checkpoint_value),
                "checkpoint_mode": checkpoint_mode,
            }
        )
    return result
