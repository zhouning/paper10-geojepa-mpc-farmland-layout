import torch


SCORE_MODES = {"reward", "value", "blend", "zscore_blend"}


def _validate_score_request(score_mode: str, value_weight: float) -> None:
    if score_mode not in SCORE_MODES:
        raise ValueError(
            "score_mode must be 'reward', 'value', 'blend', or 'zscore_blend'"
        )
    if not 0.0 <= value_weight <= 1.0:
        raise ValueError("value_weight must be in [0, 1]")


def _zscore_last_dim(scores: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    centered = scores - scores.mean(dim=-1, keepdim=True)
    scale = centered.pow(2).mean(dim=-1, keepdim=True).sqrt()
    return torch.where(
        scale > eps,
        centered / scale.clamp_min(eps),
        torch.zeros_like(scores),
    )


def zscore_blend_candidate_scores(
    reward: torch.Tensor,
    value: torch.Tensor,
    value_weight: float,
) -> torch.Tensor:
    _validate_score_request("zscore_blend", value_weight)
    if reward.shape != value.shape:
        raise ValueError("reward and value scores must have matching shapes")
    reward_z = _zscore_last_dim(reward)
    value_z = _zscore_last_dim(value)
    return (1.0 - value_weight) * reward_z + value_weight * value_z


def scalar_score_from_model_output(
    reward: torch.Tensor,
    aux: dict,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> torch.Tensor:
    _validate_score_request(score_mode, value_weight)

    if score_mode == "reward":
        return reward

    if "value" not in aux:
        raise ValueError("score_mode requires model aux['value']")

    value = aux["value"]
    if score_mode == "value":
        return value
    if score_mode == "zscore_blend":
        return zscore_blend_candidate_scores(
            reward.squeeze(-1), value.squeeze(-1), value_weight
        ).unsqueeze(-1)
    return (1.0 - value_weight) * reward + value_weight * value


def _can_score_geojepa_single_state(model, block_features, global_features, actions) -> bool:
    return (
        block_features.ndim == 3
        and global_features.ndim == 2
        and actions.ndim == 2
        and block_features.shape[0] == 1
        and global_features.shape[0] == 1
        and actions.shape[0] == 1
        and getattr(model, "fusion", None) is None
        and hasattr(model, "block_encoder")
        and hasattr(model, "global_encoder")
        and hasattr(model, "action_emb")
        and hasattr(model, "reward_head")
        and hasattr(model, "value_head")
        and hasattr(model, "hidden_dim")
    )


def _score_geojepa_single_state_actions(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    score_mode: str,
    value_weight: float,
) -> torch.Tensor:
    all_enc = model.block_encoder(block_features)
    mean_pool = all_enc.mean(dim=1).squeeze(0)
    flat_actions = actions.squeeze(0).long()
    selected_enc = all_enc.squeeze(0).index_select(0, flat_actions)
    action_enc = model.action_emb(flat_actions)
    global_enc = model.global_encoder(global_features).expand(flat_actions.shape[0], -1)
    mean_pool = mean_pool.expand(flat_actions.shape[0], -1)
    ctx = torch.cat([selected_enc, action_enc, global_enc, mean_pool], dim=-1)
    reward = model.reward_head(ctx)
    aux = {"value": model.value_head(ctx)}
    return scalar_score_from_model_output(
        reward,
        aux,
        score_mode=score_mode,
        value_weight=value_weight,
    ).squeeze(-1)


def score_candidate_actions(
    model,
    block_features: torch.Tensor,
    global_features: torch.Tensor,
    actions: torch.Tensor,
    max_pairs_per_forward: int = 512,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> torch.Tensor:
    if max_pairs_per_forward <= 0:
        raise ValueError("max_pairs_per_forward must be positive")
    _validate_score_request(score_mode, value_weight)

    single_state = block_features.ndim == 2
    if single_state:
        block_features = block_features.unsqueeze(0)
        global_features = global_features.unsqueeze(0)
        actions = actions.unsqueeze(0)

    if block_features.ndim != 3 or global_features.ndim != 2 or actions.ndim != 2:
        raise ValueError("expected block_features (B,N,F), global_features (B,K), actions (B,A)")
    if block_features.shape[0] != global_features.shape[0] or actions.shape[0] != block_features.shape[0]:
        raise ValueError("batch axes must match")

    batch_size, n_actions = actions.shape
    device = actions.device
    state_idx = (
        torch.arange(batch_size, device=device)
        .unsqueeze(1)
        .expand(batch_size, n_actions)
        .reshape(-1)
    )
    flat_actions = actions.reshape(-1)

    was_training = model.training
    model.eval()
    scores = []
    rewards = []
    values = []
    with torch.no_grad():
        if _can_score_geojepa_single_state(model, block_features, global_features, actions):
            out = _score_geojepa_single_state_actions(
                model,
                block_features,
                global_features,
                actions,
                score_mode=score_mode,
                value_weight=value_weight,
            )
            if was_training:
                model.train()
            if not single_state:
                return out.unsqueeze(0)
            return out

        for start in range(0, flat_actions.shape[0], max_pairs_per_forward):
            end = min(start + max_pairs_per_forward, flat_actions.shape[0])
            idx = state_idx[start:end]
            _, _, reward, aux = model(
                block_features[idx],
                global_features[idx],
                flat_actions[start:end],
            )
            if score_mode == "zscore_blend":
                if "value" not in aux:
                    raise ValueError("score_mode requires model aux['value']")
                rewards.append(reward.squeeze(-1))
                values.append(aux["value"].squeeze(-1))
                continue
            score = scalar_score_from_model_output(
                reward,
                aux,
                score_mode=score_mode,
                value_weight=value_weight,
            )
            scores.append(score.squeeze(-1))

    if was_training:
        model.train()

    if score_mode == "zscore_blend":
        reward_out = torch.cat(rewards, dim=0).reshape(batch_size, n_actions)
        value_out = torch.cat(values, dim=0).reshape(batch_size, n_actions)
        out = zscore_blend_candidate_scores(reward_out, value_out, value_weight)
    else:
        out = torch.cat(scores, dim=0).reshape(batch_size, n_actions)
    if single_state:
        return out.squeeze(0)
    return out


def select_topk_actions(
    actions: torch.Tensor,
    scores: torch.Tensor,
    k: int,
):
    k = min(k, actions.shape[-1])
    top_scores, top_idx = scores.topk(k, dim=-1)
    top_actions = actions.gather(-1, top_idx)
    return top_actions, top_scores
