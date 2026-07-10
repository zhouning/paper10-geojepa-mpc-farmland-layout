import numpy as np


def _compute_slope_signal(cur_gf: np.ndarray, next_gf: np.ndarray) -> np.ndarray:
    return next_gf[:, 4] - cur_gf[:, 4]


def _greedy_1step_actions(
    adapter,
    cur_bf: np.ndarray,
    cur_gf: np.ndarray,
    valid_actions: np.ndarray,
    n_sample: int,
    rng: np.random.Generator,
) -> np.ndarray:
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


def memory_efficient_mpc_select_action(
    adapter,
    block_features,
    global_features,
    action_mask,
    horizon: int = 5,
    top_k: int = 50,
    gamma: float = 0.99,
    n_rollouts: int = 1,
    continuation: str = "random",
    greedy_sample: int = 50,
    scoring: str = "reward",
    screening_batch_size: int = 64,
    rng: np.random.Generator | None = None,
):
    """Select the same action as Paper9 MPC without materializing every state."""
    screening_batch_size = int(screening_batch_size)
    if screening_batch_size <= 0:
        raise ValueError("screening_batch_size must be positive")

    rng = rng or np.random.default_rng()
    block_features = np.asarray(block_features)
    global_features = np.asarray(global_features)
    valid_actions = np.where(np.asarray(action_mask, dtype=bool))[0]
    if len(valid_actions) == 0:
        return 0, {}

    score_chunks = []
    for start in range(0, len(valid_actions), screening_batch_size):
        actions = valid_actions[start : start + screening_batch_size]
        batch_size = len(actions)
        bf_batch = np.repeat(block_features[np.newaxis], batch_size, axis=0)
        gf_batch = np.repeat(global_features[np.newaxis], batch_size, axis=0)
        _, next_gf, rewards, _ = adapter.batch_predict(
            bf_batch,
            gf_batch,
            actions,
        )
        scores = (
            _compute_slope_signal(gf_batch, next_gf)
            if scoring == "slope"
            else rewards
        )
        score_chunks.append(np.asarray(scores))

    score1 = np.concatenate(score_chunks)
    n_valid = len(valid_actions)
    k = min(int(top_k), n_valid)
    top_idx = np.argsort(score1)[-k:]
    candidates = valid_actions[top_idx]
    cand_cumrew = score1[top_idx].copy().astype(np.float64)

    bf_batch = np.repeat(block_features[np.newaxis], k, axis=0)
    gf_batch = np.repeat(global_features[np.newaxis], k, axis=0)
    next_bf, next_gf, _, _ = adapter.batch_predict(
        bf_batch,
        gf_batch,
        candidates,
    )

    rollout_rewards = np.zeros(k, dtype=np.float64)
    for _ in range(int(n_rollouts)):
        cur_bf = next_bf.copy()
        cur_gf = next_gf.copy()
        prev_gf = next_gf.copy()
        discount = float(gamma)
        for _step in range(1, int(horizon)):
            if continuation == "greedy":
                actions = _greedy_1step_actions(
                    adapter,
                    cur_bf,
                    cur_gf,
                    valid_actions,
                    int(greedy_sample),
                    rng,
                )
            else:
                actions = rng.choice(valid_actions, size=k)
            nb, ng, r_step, _ = adapter.batch_predict(cur_bf, cur_gf, actions)
            step_score = (
                _compute_slope_signal(prev_gf, ng)
                if scoring == "slope"
                else r_step
            )
            rollout_rewards += discount * step_score
            discount *= float(gamma)
            prev_gf = cur_gf.copy()
            cur_bf = nb
            cur_gf = ng
    cand_cumrew += rollout_rewards / int(n_rollouts)

    best = int(np.argmax(cand_cumrew))
    chosen = int(candidates[best])
    info = {
        "n_valid": int(n_valid),
        "n_candidates": int(k),
        "best_cumrew": float(cand_cumrew[best]),
        "mean_cumrew": float(cand_cumrew.mean()),
        "horizon": int(horizon),
        "continuation": continuation,
        "scoring": scoring,
        "screening_batch_size": screening_batch_size,
    }
    return chosen, info
