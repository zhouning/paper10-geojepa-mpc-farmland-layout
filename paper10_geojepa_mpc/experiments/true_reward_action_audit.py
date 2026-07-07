import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PAPER9_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER9_DIR))

from paper10_geojepa_mpc.experiments.rollout_candidate_diagnostics import (  # noqa: E402
    _restore,
    _snapshot,
)
from paper10_geojepa_mpc.experiments.rollout_summary import (  # noqa: E402
    build_rollout_step_record,
    parse_seed_list,
    summarize_rollout,
)
from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask  # noqa: E402
from paper10_geojepa_mpc.planning.paper9_adapter import (  # noqa: E402
    TorchCheckpointMPCAdapter,
)
from paper10_geojepa_mpc.planning.scoring import score_candidate_actions  # noqa: E402
from paper10_geojepa_mpc.planning.value_filter_selector import (  # noqa: E402
    value_filter_mpc_select_action,
)


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.shape[0] < 2:
        return 0.0
    x_std = float(np.std(x))
    y_std = float(np.std(y))
    if x_std == 0.0 or y_std == 0.0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _rankdata_desc(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)[::-1]
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(values.shape[0], dtype=np.float64)
    return ranks


def build_audit_action_set(
    *,
    valid_actions: np.ndarray,
    selected_action: int,
    model_reward_scores: np.ndarray,
    candidate_scores: np.ndarray,
    top_reward_count: int,
    top_candidate_count: int,
    random_sample_count: int,
    rng,
) -> np.ndarray:
    valid_actions = np.asarray(valid_actions, dtype=np.int64)
    model_reward_scores = np.asarray(model_reward_scores, dtype=np.float64)
    candidate_scores = np.asarray(candidate_scores, dtype=np.float64)
    if valid_actions.ndim != 1:
        raise ValueError("valid_actions must be one-dimensional")
    if model_reward_scores.shape != valid_actions.shape:
        raise ValueError("model_reward_scores must match valid_actions")
    if candidate_scores.shape != valid_actions.shape:
        raise ValueError("candidate_scores must match valid_actions")
    if int(selected_action) not in set(int(action) for action in valid_actions):
        raise ValueError("selected_action must be in valid_actions")

    chosen = [int(selected_action)]
    chosen_set = {int(selected_action)}

    def add_by_order(order: np.ndarray, limit: int) -> None:
        for idx in order[: max(0, int(limit))]:
            action = int(valid_actions[int(idx)])
            if action in chosen_set:
                continue
            chosen.append(action)
            chosen_set.add(action)

    add_by_order(np.argsort(model_reward_scores)[::-1], top_reward_count)
    add_by_order(np.argsort(candidate_scores)[::-1], top_candidate_count)

    remaining = np.asarray(
        [int(action) for action in valid_actions if int(action) not in chosen_set],
        dtype=np.int64,
    )
    sample_count = min(max(0, int(random_sample_count)), remaining.shape[0])
    if sample_count > 0:
        for action in rng.choice(remaining, size=sample_count, replace=False):
            value = int(action)
            if value not in chosen_set:
                chosen.append(value)
                chosen_set.add(value)

    return np.asarray(chosen, dtype=np.int64)


def action_audit_metrics(
    *,
    actions: np.ndarray,
    true_rewards: np.ndarray,
    model_reward_scores: np.ndarray,
    candidate_scores: np.ndarray,
    selected_action: int,
    top_k: int,
) -> dict:
    actions = np.asarray(actions, dtype=np.int64)
    true_rewards = np.asarray(true_rewards, dtype=np.float64)
    model_reward_scores = np.asarray(model_reward_scores, dtype=np.float64)
    candidate_scores = np.asarray(candidate_scores, dtype=np.float64)
    if actions.ndim != 1:
        raise ValueError("actions must be one-dimensional")
    if true_rewards.shape != actions.shape:
        raise ValueError("true_rewards must match actions")
    if model_reward_scores.shape != actions.shape:
        raise ValueError("model_reward_scores must match actions")
    if candidate_scores.shape != actions.shape:
        raise ValueError("candidate_scores must match actions")

    matches = np.where(actions == int(selected_action))[0]
    if matches.shape[0] != 1:
        raise ValueError("selected_action must appear exactly once in actions")
    selected_idx = int(matches[0])
    best_true_idx = int(np.argmax(true_rewards))
    model_order = np.argsort(model_reward_scores)[::-1]
    candidate_order = np.argsort(candidate_scores)[::-1]
    k = min(max(1, int(top_k)), actions.shape[0])
    selected_true_reward = float(true_rewards[selected_idx])
    best_true_reward = float(true_rewards[best_true_idx])
    true_order = np.argsort(true_rewards)[::-1]
    true_rank_by_idx = np.empty_like(true_order)
    true_rank_by_idx[true_order] = np.arange(1, true_order.shape[0] + 1)

    return {
        "audit_action_count": int(actions.shape[0]),
        "selected_action": int(selected_action),
        "selected_true_reward": selected_true_reward,
        "selected_model_reward_score": float(model_reward_scores[selected_idx]),
        "selected_candidate_score": float(candidate_scores[selected_idx]),
        "selected_true_reward_rank": int(true_rank_by_idx[selected_idx]),
        "selected_true_reward_regret": float(best_true_reward - selected_true_reward),
        "selected_is_audit_true_best": float(selected_idx == best_true_idx),
        "audit_best_action": int(actions[best_true_idx]),
        "audit_best_true_reward": best_true_reward,
        "audit_best_model_reward_score": float(model_reward_scores[best_true_idx]),
        "audit_best_candidate_score": float(candidate_scores[best_true_idx]),
        "model_reward_top1_action": int(actions[int(model_order[0])]),
        "model_reward_top1_true_reward": float(true_rewards[int(model_order[0])]),
        "candidate_top1_action": int(actions[int(candidate_order[0])]),
        "candidate_top1_true_reward": float(true_rewards[int(candidate_order[0])]),
        "audit_true_best_in_model_reward_topk": float(best_true_idx in set(model_order[:k])),
        "audit_true_best_in_candidate_topk": float(best_true_idx in set(candidate_order[:k])),
        "true_reward_model_reward_pearson": _corr(true_rewards, model_reward_scores),
        "true_reward_candidate_pearson": _corr(true_rewards, candidate_scores),
        "true_reward_model_reward_spearman": _corr(
            _rankdata_desc(true_rewards),
            _rankdata_desc(model_reward_scores),
        ),
        "true_reward_candidate_spearman": _corr(
            _rankdata_desc(true_rewards),
            _rankdata_desc(candidate_scores),
        ),
    }


def choose_execution_action(
    metrics: dict,
    execution_policy: str,
    true_reward_switch_margin: float = 0.0,
) -> int:
    if execution_policy == "value_filter":
        return int(metrics["selected_action"])
    if execution_policy == "audit_true_best":
        return int(metrics["audit_best_action"])
    if execution_policy == "margin_true_reward_guard":
        improvement = (
            float(metrics["audit_best_true_reward"])
            - float(metrics["selected_true_reward"])
        )
        if improvement >= float(true_reward_switch_margin):
            return int(metrics["audit_best_action"])
        return int(metrics["selected_action"])
    raise ValueError(
        "execution_policy must be 'value_filter', 'audit_true_best', "
        "or 'margin_true_reward_guard'"
    )


def summarize_action_audit_rows(rows: list[dict]) -> dict:
    if not rows:
        return {
            "states": 0,
            "selected_true_reward_regret_mean": 0.0,
            "selected_is_audit_true_best_rate": 0.0,
            "audit_true_best_in_model_reward_topk_rate": 0.0,
            "audit_true_best_in_candidate_topk_rate": 0.0,
            "true_reward_model_reward_pearson_mean": 0.0,
            "true_reward_candidate_pearson_mean": 0.0,
        }

    def avg(key: str) -> float:
        return float(np.mean([float(row[key]) for row in rows]))

    return {
        "states": int(len(rows)),
        "selected_true_reward_regret_mean": avg("selected_true_reward_regret"),
        "selected_true_reward_regret_max": float(
            max(float(row["selected_true_reward_regret"]) for row in rows)
        ),
        "selected_is_audit_true_best_rate": avg("selected_is_audit_true_best"),
        "audit_true_best_in_model_reward_topk_rate": avg(
            "audit_true_best_in_model_reward_topk"
        ),
        "audit_true_best_in_candidate_topk_rate": avg(
            "audit_true_best_in_candidate_topk"
        ),
        "true_reward_model_reward_pearson_mean": avg(
            "true_reward_model_reward_pearson"
        ),
        "true_reward_candidate_pearson_mean": avg("true_reward_candidate_pearson"),
        "true_reward_model_reward_spearman_mean": avg(
            "true_reward_model_reward_spearman"
        ),
        "true_reward_candidate_spearman_mean": avg(
            "true_reward_candidate_spearman"
        ),
    }


def _score_valid_actions(
    adapter,
    block_features: np.ndarray,
    global_features: np.ndarray,
    valid_actions: np.ndarray,
    score_mode: str,
    value_weight: float,
) -> np.ndarray:
    with torch.no_grad():
        scores = score_candidate_actions(
            adapter.model,
            torch.tensor(block_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(global_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(valid_actions, dtype=torch.long, device=adapter.device),
            score_mode=score_mode,
            value_weight=value_weight,
        )
    return scores.detach().cpu().numpy().astype(np.float64)


def _true_rewards_for_actions(env, actions: np.ndarray) -> np.ndarray:
    snap = _snapshot(env)
    rewards = []
    for action in actions:
        _, reward, _, _, _ = env.step(int(action))
        rewards.append(float(reward))
        _restore(env, snap)
    return np.asarray(rewards, dtype=np.float64)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "checkpoints"
            / "e0_frontier_random050_value_head_20x16_h5_seed44_top5"
            / "value_head_seed3044.pt"
        ),
    )
    parser.add_argument("--prepared-dir", default=str(ROOT))
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--horizon", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--metric-top-k", type=int, default=10)
    parser.add_argument("--audit-random-sample", type=int, default=100)
    parser.add_argument("--audit-top-reward", type=int, default=25)
    parser.add_argument("--audit-top-candidate", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--candidate-score-mode", default="blend")
    parser.add_argument("--candidate-value-weight", type=float, default=0.1)
    parser.add_argument("--candidate-reward-reserve", type=int, default=0)
    parser.add_argument(
        "--execution-policy",
        choices=("value_filter", "audit_true_best", "margin_true_reward_guard"),
        default="value_filter",
    )
    parser.add_argument("--true-reward-switch-margin", type=float, default=0.0)
    parser.add_argument(
        "--random-continuation-mode",
        choices=("independent", "common"),
        default="independent",
    )
    parser.add_argument("--stable-candidate-order", action="store_true")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def _run_seed(env, adapter, args, seed: int) -> dict:
    env.reset(seed=seed)
    policy_rng = np.random.default_rng(seed)
    audit_rng = np.random.default_rng(seed + 1_000_003)
    rows = []
    steps = []
    total_reward = 0.0
    terminated = False
    truncated = False

    for step_idx in range(int(args.steps)):
        block_features = env._get_block_features()
        global_features = env._get_global_features()
        base_mask = env.action_masks()
        action_mask = base_mask & executable_swap_mask(env)
        valid_actions = np.where(action_mask)[0].astype(np.int64)
        if valid_actions.shape[0] == 0:
            break

        scored_at = perf_counter()
        model_reward_scores = _score_valid_actions(
            adapter,
            block_features,
            global_features,
            valid_actions,
            "reward",
            0.5,
        )
        candidate_scores = _score_valid_actions(
            adapter,
            block_features,
            global_features,
            valid_actions,
            args.candidate_score_mode,
            float(args.candidate_value_weight),
        )
        score_time_sec = perf_counter() - scored_at

        selected_at = perf_counter()
        selected_action, mpc_info = value_filter_mpc_select_action(
            adapter,
            block_features,
            global_features,
            action_mask,
            horizon=int(args.horizon),
            top_k=int(args.top_k),
            gamma=0.99,
            n_rollouts=1,
            continuation="random",
            scoring="reward",
            candidate_score_mode=args.candidate_score_mode,
            candidate_value_weight=float(args.candidate_value_weight),
            candidate_reward_reserve=int(args.candidate_reward_reserve),
            random_continuation_mode=args.random_continuation_mode,
            stable_candidate_order=bool(args.stable_candidate_order),
            rng=policy_rng,
        )
        select_time_sec = perf_counter() - selected_at

        audit_actions = build_audit_action_set(
            valid_actions=valid_actions,
            selected_action=int(selected_action),
            model_reward_scores=model_reward_scores,
            candidate_scores=candidate_scores,
            top_reward_count=int(args.audit_top_reward),
            top_candidate_count=int(args.audit_top_candidate),
            random_sample_count=int(args.audit_random_sample),
            rng=audit_rng,
        )
        action_to_valid_idx = {int(action): idx for idx, action in enumerate(valid_actions)}
        audit_indices = np.asarray(
            [action_to_valid_idx[int(action)] for action in audit_actions],
            dtype=np.int64,
        )
        true_started = perf_counter()
        true_rewards = _true_rewards_for_actions(env, audit_actions)
        true_reward_time_sec = perf_counter() - true_started
        audit_row = action_audit_metrics(
            actions=audit_actions,
            true_rewards=true_rewards,
            model_reward_scores=model_reward_scores[audit_indices],
            candidate_scores=candidate_scores[audit_indices],
            selected_action=int(selected_action),
            top_k=int(args.metric_top_k),
        )
        audit_row.update(
            {
                "step": int(step_idx + 1),
                "seed": int(seed),
                "n_valid": int(valid_actions.shape[0]),
                "score_time_sec": float(score_time_sec),
                "select_time_sec": float(select_time_sec),
                "true_reward_time_sec": float(true_reward_time_sec),
            }
        )
        rows.append(audit_row)

        execution_action = choose_execution_action(
            audit_row,
            args.execution_policy,
            true_reward_switch_margin=float(args.true_reward_switch_margin),
        )
        audit_row["execution_action"] = int(execution_action)
        audit_row["execution_policy"] = args.execution_policy
        audit_row["true_reward_switch_margin"] = float(args.true_reward_switch_margin)
        _, reward, terminated, truncated, info = env.step(int(execution_action))
        total_reward += float(reward)
        mpc_info["n_base_valid"] = int(base_mask.sum())
        mpc_info["n_executable_valid"] = int(action_mask.sum())
        steps.append(
            build_rollout_step_record(
                step_idx=step_idx,
                action=int(execution_action),
                reward=reward,
                mpc_info=mpc_info,
                select_time_sec=select_time_sec,
                env_info=info,
            )
        )
        if terminated or truncated:
            break

    episode = {
        "seed": int(seed),
        "steps_run": len(steps),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "total_reward": float(total_reward),
        "steps": steps,
        "audit_rows": rows,
        "audit_summary": summarize_action_audit_rows(rows),
    }
    episode["rollout_summary"] = summarize_rollout(episode)
    return episode


def main() -> None:
    args = parse_args()
    started = perf_counter()

    from private_source.blocks_env import make_env

    env = make_env(prepared_dir=args.prepared_dir)
    adapter = TorchCheckpointMPCAdapter.from_checkpoint(args.checkpoint, device=args.device)
    adapter.assert_compatible(env.n_blocks)
    seeds = parse_seed_list(args.seeds) if args.seeds else [int(args.seed)]
    episodes = [_run_seed(env, adapter, args, int(seed)) for seed in seeds]
    all_rows = [
        row
        for episode in episodes
        for row in episode.get("audit_rows", [])
    ]
    result = {
        "checkpoint": str(args.checkpoint),
        "prepared_dir": str(args.prepared_dir),
        "seeds": [int(seed) for seed in seeds],
        "steps": int(args.steps),
        "horizon": int(args.horizon),
        "top_k": int(args.top_k),
        "metric_top_k": int(args.metric_top_k),
        "audit_random_sample": int(args.audit_random_sample),
        "audit_top_reward": int(args.audit_top_reward),
        "audit_top_candidate": int(args.audit_top_candidate),
        "candidate_score_mode": args.candidate_score_mode,
        "candidate_value_weight": float(args.candidate_value_weight),
        "candidate_reward_reserve": int(args.candidate_reward_reserve),
        "execution_policy": args.execution_policy,
        "true_reward_switch_margin": float(args.true_reward_switch_margin),
        "random_continuation_mode": args.random_continuation_mode,
        "stable_candidate_order": bool(args.stable_candidate_order),
        "elapsed_sec": perf_counter() - started,
        "episodes": episodes,
        "summary": summarize_action_audit_rows(all_rows),
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

