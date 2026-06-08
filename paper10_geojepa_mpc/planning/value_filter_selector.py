import numpy as np
import torch
from time import perf_counter

from paper10_geojepa_mpc.planning.scoring import score_candidate_actions


def _compute_slope_signal(cur_gf: np.ndarray, next_gf: np.ndarray) -> np.ndarray:
    return next_gf[:, 4] - cur_gf[:, 4]


def _greedy_1step_actions(adapter, cur_bf, cur_gf, valid_actions, n_sample, rng):
    k = cur_bf.shape[0]
    if len(valid_actions) <= n_sample:
        sample_actions = valid_actions
    else:
        sample_actions = rng.choice(valid_actions, n_sample, replace=False)
    n_s = len(sample_actions)

    bf_exp = np.repeat(cur_bf, n_s, axis=0)
    gf_exp = np.repeat(cur_gf, n_s, axis=0)
    a_exp = np.tile(sample_actions, k)
    _, _, r_exp, _ = adapter.batch_predict(bf_exp, gf_exp, a_exp)
    r_matrix = r_exp.reshape(k, n_s)
    best_local = r_matrix.argmax(axis=1)
    return sample_actions[best_local]


def _score_valid_actions(
    adapter,
    block_features: np.ndarray,
    global_features: np.ndarray,
    valid_actions: np.ndarray,
    candidate_score_mode: str,
    candidate_value_weight: float,
) -> np.ndarray:
    if not hasattr(adapter, "model") or not hasattr(adapter, "device"):
        raise ValueError("value_filter selector requires an adapter with model and device")
    with torch.no_grad():
        scores = score_candidate_actions(
            adapter.model,
            torch.tensor(block_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(global_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(valid_actions, dtype=torch.long, device=adapter.device),
            score_mode=candidate_score_mode,
            value_weight=candidate_value_weight,
        )
    return scores.detach().cpu().numpy().astype(np.float64)


def _can_use_geojepa_state_rollout(adapter, continuation: str) -> bool:
    if continuation != "random":
        return False
    if getattr(adapter, "score_mode", "reward") != "reward":
        return False
    if not hasattr(adapter, "model") or not hasattr(adapter, "device"):
        return False
    model = adapter.model
    return (
        getattr(model, "fusion", None) is None
        and hasattr(model, "block_encoder")
        and hasattr(model, "global_encoder")
        and hasattr(model, "action_emb")
        and hasattr(model, "block_delta_head")
        and hasattr(model, "global_delta_head")
        and hasattr(model, "reward_head")
        and hasattr(model, "hidden_dim")
    )


def _geojepa_step_from_encoded(
    model,
    block_state: torch.Tensor,
    global_state: torch.Tensor,
    encoded_state: torch.Tensor,
    mean_pool: torch.Tensor,
    actions: torch.Tensor,
):
    batch_size, n_blocks, _ = block_state.shape
    actions = actions.long().view(batch_size)
    rows = torch.arange(batch_size, device=block_state.device)

    selected_idx = actions.unsqueeze(-1).unsqueeze(-1).expand(
        batch_size, 1, model.hidden_dim
    )
    selected_enc = encoded_state.gather(1, selected_idx).squeeze(1)
    action_enc = model.action_emb(actions)
    global_enc = model.global_encoder(global_state)
    ctx = torch.cat([selected_enc, action_enc, global_enc, mean_pool], dim=-1)

    block_delta = model.block_delta_head(ctx)
    global_delta = model.global_delta_head(ctx)
    reward = model.reward_head(ctx).squeeze(-1)

    next_block = block_state.clone()
    next_selected_block = next_block[rows, actions] + block_delta
    next_block[rows, actions] = next_selected_block
    next_global = global_state + global_delta

    updated_selected_enc = model.block_encoder(next_selected_block.unsqueeze(1)).squeeze(1)
    next_encoded = encoded_state.clone()
    next_encoded[rows, actions] = updated_selected_enc
    next_mean = mean_pool + (updated_selected_enc - selected_enc) / float(n_blocks)
    return next_block, next_global, reward, next_encoded, next_mean


def _geojepa_rollout_candidate_scores(
    adapter,
    block_features: np.ndarray,
    global_features: np.ndarray,
    candidates: np.ndarray,
    valid_actions: np.ndarray,
    horizon: int,
    gamma: float,
    n_rollouts: int,
    scoring: str,
    random_continuation_mode: str,
    rng,
):
    model = adapter.model
    was_training = model.training
    model.eval()
    device = adapter.device
    k = len(candidates)

    with torch.no_grad():
        base_block = torch.tensor(
            block_features, dtype=torch.float32, device=device
        ).unsqueeze(0)
        base_global = torch.tensor(
            global_features, dtype=torch.float32, device=device
        ).unsqueeze(0)
        base_encoded = model.block_encoder(base_block)

        block_state = base_block.expand(k, -1, -1).clone()
        global_state = base_global.expand(k, -1).clone()
        encoded_state = base_encoded.expand(k, -1, -1).clone()
        mean_pool = base_encoded.mean(dim=1).expand(k, -1).clone()
        action_tensor = torch.tensor(candidates, dtype=torch.long, device=device)

        first_step_started = perf_counter()
        next_block, next_global, first_reward, next_encoded, next_mean = (
            _geojepa_step_from_encoded(
                model,
                block_state,
                global_state,
                encoded_state,
                mean_pool,
                action_tensor,
            )
        )
        first_step_time_sec = perf_counter() - first_step_started
        if scoring == "slope":
            first_score = next_global[:, 4] - global_state[:, 4]
        else:
            first_score = first_reward

        cand_cumrew = first_score.to(torch.float64)
        rollout_rewards = torch.zeros(k, dtype=torch.float64, device=device)

        rollout_started = perf_counter()
        for _ in range(n_rollouts):
            cur_block = next_block.clone()
            cur_global = next_global.clone()
            cur_encoded = next_encoded.clone()
            cur_mean = next_mean.clone()
            prev_global = next_global.clone()
            discount = gamma
            for _step in range(1, horizon):
                if random_continuation_mode == "common":
                    action = int(rng.choice(valid_actions))
                    actions = np.full(k, action, dtype=np.int64)
                else:
                    actions = rng.choice(valid_actions, size=k)
                action_tensor = torch.tensor(actions, dtype=torch.long, device=device)
                nb, ng, reward, nenc, nmean = _geojepa_step_from_encoded(
                    model,
                    cur_block,
                    cur_global,
                    cur_encoded,
                    cur_mean,
                    action_tensor,
                )
                step_score = ng[:, 4] - prev_global[:, 4] if scoring == "slope" else reward
                rollout_rewards += discount * step_score.to(torch.float64)
                discount *= gamma
                prev_global = cur_global.clone()
                cur_block = nb
                cur_global = ng
                cur_encoded = nenc
                cur_mean = nmean
        rollout_time_sec = perf_counter() - rollout_started
        cand_cumrew += rollout_rewards / n_rollouts

    if was_training:
        model.train()
    return (
        cand_cumrew.detach().cpu().numpy().astype(np.float64),
        float(first_step_time_sec),
        float(rollout_time_sec),
    )


def value_filter_mpc_select_action(
    adapter,
    block_features,
    global_features,
    action_mask,
    horizon=5,
    top_k=50,
    gamma=0.99,
    n_rollouts=1,
    continuation="random",
    greedy_sample=50,
    scoring="reward",
    candidate_score_mode="value",
    candidate_value_weight=0.5,
    use_geojepa_fast_path=True,
    stable_candidate_order=False,
    random_continuation_mode="independent",
    rng=None,
):
    """Select candidates with value/blend scores, then roll them out with reward.

    This avoids treating a short-horizon value label as a per-step reward during
    MPC rollout. The adapter's batch_predict output is assumed to be the reward
    objective for the rollout stage.
    """

    if scoring not in {"reward", "slope"}:
        raise ValueError("scoring must be 'reward' or 'slope'")
    if continuation not in {"random", "greedy"}:
        raise ValueError("continuation must be 'random' or 'greedy'")
    if random_continuation_mode not in {"independent", "common"}:
        raise ValueError("random_continuation_mode must be 'independent' or 'common'")

    rng = rng or np.random.default_rng()
    valid_actions = np.where(action_mask)[0]
    if len(valid_actions) == 0:
        return 0, {}

    score_started = perf_counter()
    candidate_scores = _score_valid_actions(
        adapter,
        np.asarray(block_features, dtype=np.float32),
        np.asarray(global_features, dtype=np.float32),
        valid_actions.astype(np.int64),
        candidate_score_mode,
        candidate_value_weight,
    )
    score_time_sec = perf_counter() - score_started

    n_valid = len(valid_actions)
    k = min(top_k, n_valid)
    top_idx = np.argsort(candidate_scores)[-k:]
    candidates = valid_actions[top_idx]
    selected_candidate_scores = candidate_scores[top_idx]
    if stable_candidate_order:
        order = np.argsort(candidates)
        candidates = candidates[order]
        selected_candidate_scores = selected_candidate_scores[order]

    fast_path = "adapter_batch_predict"
    if use_geojepa_fast_path and _can_use_geojepa_state_rollout(adapter, continuation):
        cand_cumrew, first_step_time_sec, rollout_time_sec = _geojepa_rollout_candidate_scores(
            adapter,
            np.asarray(block_features, dtype=np.float32),
            np.asarray(global_features, dtype=np.float32),
            candidates.astype(np.int64),
            valid_actions.astype(np.int64),
            horizon,
            gamma,
            n_rollouts,
            scoring,
            random_continuation_mode,
            rng,
        )
        fast_path = "geojepa_state_rollout"
    else:
        bf_batch = np.tile(np.asarray(block_features, dtype=np.float32)[np.newaxis], (k, 1, 1))
        gf_batch = np.tile(np.asarray(global_features, dtype=np.float32)[np.newaxis], (k, 1))
        first_step_started = perf_counter()
        next_bf, next_gf, r1, _ = adapter.batch_predict(bf_batch, gf_batch, candidates)
        first_step_time_sec = perf_counter() - first_step_started

        if scoring == "slope":
            score1 = _compute_slope_signal(gf_batch, next_gf)
        else:
            score1 = r1

        cand_cumrew = score1.copy().astype(np.float64)
        rollout_rewards = np.zeros(k, dtype=np.float64)
        rollout_started = perf_counter()
        for _ in range(n_rollouts):
            cur_bf = next_bf.copy()
            cur_gf = next_gf.copy()
            prev_gf = next_gf.copy()
            discount = gamma
            for _step in range(1, horizon):
                if continuation == "greedy":
                    actions = _greedy_1step_actions(
                        adapter, cur_bf, cur_gf, valid_actions, greedy_sample, rng
                    )
                elif random_continuation_mode == "common":
                    action = int(rng.choice(valid_actions))
                    actions = np.full(k, action, dtype=np.int64)
                else:
                    actions = rng.choice(valid_actions, size=k)
                nb, ng, r_step, _ = adapter.batch_predict(cur_bf, cur_gf, actions)
                step_score = _compute_slope_signal(prev_gf, ng) if scoring == "slope" else r_step
                rollout_rewards += discount * step_score
                discount *= gamma
                prev_gf = cur_gf.copy()
                cur_bf = nb
                cur_gf = ng
        cand_cumrew += rollout_rewards / n_rollouts
        rollout_time_sec = perf_counter() - rollout_started

    best = int(np.argmax(cand_cumrew))
    chosen = int(candidates[best])
    info = {
        "selector": "value_filter",
        "n_valid": int(n_valid),
        "n_candidates": int(k),
        "best_cumrew": float(cand_cumrew[best]),
        "mean_cumrew": float(cand_cumrew.mean()),
        "best_candidate_score": float(selected_candidate_scores[best]),
        "mean_candidate_score": float(selected_candidate_scores.mean()),
        "horizon": int(horizon),
        "continuation": continuation,
        "scoring": scoring,
        "candidate_score_mode": candidate_score_mode,
        "candidate_value_weight": float(candidate_value_weight),
        "stable_candidate_order": bool(stable_candidate_order),
        "random_continuation_mode": random_continuation_mode,
        "fast_path": fast_path,
        "score_time_sec": float(score_time_sec),
        "first_step_time_sec": float(first_step_time_sec),
        "rollout_time_sec": float(rollout_time_sec),
    }
    return chosen, info
