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

from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
from paper10_geojepa_mpc.planning.scoring import score_candidate_actions


def _rankdata_desc(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)[::-1]
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(values.shape[0], dtype=np.float64)
    return ranks


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.shape[0] < 2:
        return 0.0
    x_std = float(np.std(x))
    y_std = float(np.std(y))
    if x_std == 0.0 or y_std == 0.0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def candidate_overlap_metrics(
    reward_scores,
    candidate_scores,
    top_k: int,
    actions=None,
) -> dict:
    reward_scores = np.asarray(reward_scores, dtype=np.float64)
    candidate_scores = np.asarray(candidate_scores, dtype=np.float64)
    if reward_scores.shape != candidate_scores.shape:
        raise ValueError("reward_scores and candidate_scores must have the same shape")
    if reward_scores.ndim != 1:
        raise ValueError("scores must be one-dimensional")
    if reward_scores.shape[0] == 0:
        raise ValueError("scores must not be empty")

    n_actions = reward_scores.shape[0]
    k = min(int(top_k), n_actions)
    if k <= 0:
        raise ValueError("top_k must be positive")

    if actions is None:
        action_values = np.arange(n_actions, dtype=np.int64)
    else:
        action_values = np.asarray(actions, dtype=np.int64)
        if action_values.shape[0] != n_actions:
            raise ValueError("actions must have the same length as scores")

    reward_order = np.argsort(reward_scores)[::-1]
    candidate_order = np.argsort(candidate_scores)[::-1]
    reward_topk = reward_order[:k]
    candidate_topk = candidate_order[:k]
    reward_set = set(int(x) for x in reward_topk)
    candidate_set = set(int(x) for x in candidate_topk)
    overlap_count = len(reward_set & candidate_set)
    union_count = len(reward_set | candidate_set)

    reward_top1 = int(reward_order[0])
    candidate_top1 = int(candidate_order[0])
    reward_best = float(reward_scores[reward_top1])
    candidate_top1_reward = float(reward_scores[candidate_top1])
    candidate_topk_best_reward = float(reward_scores[candidate_topk].max())

    return {
        "n_actions": int(n_actions),
        "top_k": int(k),
        "topk_overlap_count": int(overlap_count),
        "topk_overlap_fraction": float(overlap_count / k),
        "topk_jaccard": float(overlap_count / union_count) if union_count else 0.0,
        "reward_top1_in_candidate_topk": float(reward_top1 in candidate_set),
        "candidate_top1_in_reward_topk": float(candidate_top1 in reward_set),
        "candidate_top1_reward_regret": float(reward_best - candidate_top1_reward),
        "candidate_topk_best_reward_regret": float(
            reward_best - candidate_topk_best_reward
        ),
        "reward_top1_action": int(action_values[reward_top1]),
        "candidate_top1_action": int(action_values[candidate_top1]),
        "reward_top1_score": reward_best,
        "candidate_top1_reward_score": candidate_top1_reward,
        "candidate_top1_candidate_score": float(candidate_scores[candidate_top1]),
        "candidate_topk_best_reward_score": candidate_topk_best_reward,
        "score_pearson": _corr(reward_scores, candidate_scores),
        "score_spearman": _corr(
            _rankdata_desc(reward_scores), _rankdata_desc(candidate_scores)
        ),
    }


def summarize_overlap_rows(rows: list[dict]) -> dict:
    if not rows:
        return {
            "states": 0,
            "topk_overlap_fraction_mean": 0.0,
            "topk_jaccard_mean": 0.0,
            "reward_top1_in_candidate_topk_rate": 0.0,
            "candidate_top1_in_reward_topk_rate": 0.0,
            "candidate_top1_reward_regret_mean": 0.0,
            "candidate_topk_best_reward_regret_mean": 0.0,
            "score_pearson_mean": 0.0,
            "score_spearman_mean": 0.0,
        }

    def avg(key: str) -> float:
        return float(np.mean([float(row[key]) for row in rows]))

    return {
        "states": len(rows),
        "topk_overlap_fraction_mean": avg("topk_overlap_fraction"),
        "topk_jaccard_mean": avg("topk_jaccard"),
        "reward_top1_in_candidate_topk_rate": avg("reward_top1_in_candidate_topk"),
        "candidate_top1_in_reward_topk_rate": avg("candidate_top1_in_reward_topk"),
        "candidate_top1_reward_regret_mean": avg("candidate_top1_reward_regret"),
        "candidate_topk_best_reward_regret_mean": avg(
            "candidate_topk_best_reward_regret"
        ),
        "score_pearson_mean": avg("score_pearson"),
        "score_spearman_mean": avg("score_spearman"),
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "checkpoints"
            / "e0_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2"
            / "independent_value_head_seed3034.pt"
        ),
    )
    parser.add_argument("--prepared-dir", default=str(ROOT))
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--candidate-score-mode",
        choices=("value", "blend", "zscore_blend"),
        default="blend",
    )
    parser.add_argument("--candidate-value-weight", type=float, default=0.1)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = perf_counter()

    from private_source.blocks_env import make_env

    env = make_env(prepared_dir=args.prepared_dir)
    adapter = TorchCheckpointMPCAdapter.from_checkpoint(args.checkpoint, device=args.device)
    adapter.assert_compatible(env.n_blocks)

    env.reset(seed=args.seed)
    rows = []
    total_reward = 0.0

    for step_idx in range(args.steps):
        block_features = env._get_block_features()
        global_features = env._get_global_features()
        action_mask = env.action_masks() & executable_swap_mask(env)
        valid_actions = np.where(action_mask)[0]
        if valid_actions.shape[0] == 0:
            break

        scored_at = perf_counter()
        reward_scores = _score_valid_actions(
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
            args.candidate_value_weight,
        )
        row = candidate_overlap_metrics(
            reward_scores,
            candidate_scores,
            args.top_k,
            actions=valid_actions,
        )
        row["step"] = int(step_idx + 1)
        row["n_valid"] = int(valid_actions.shape[0])
        row["score_time_sec"] = float(perf_counter() - scored_at)
        rows.append(row)

        action = int(row["reward_top1_action"])
        _, reward, terminated, truncated, _ = env.step(action)
        total_reward += float(reward)
        if terminated or truncated:
            break

    result = {
        "checkpoint": str(args.checkpoint),
        "prepared_dir": str(args.prepared_dir),
        "seed": int(args.seed),
        "steps_requested": int(args.steps),
        "steps_run": len(rows),
        "top_k": int(args.top_k),
        "candidate_score_mode": args.candidate_score_mode,
        "candidate_value_weight": float(args.candidate_value_weight),
        "elapsed_sec": perf_counter() - started,
        "reward_top1_policy_total_reward": float(total_reward),
        "summary": summarize_overlap_rows(rows),
        "rows": rows,
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
