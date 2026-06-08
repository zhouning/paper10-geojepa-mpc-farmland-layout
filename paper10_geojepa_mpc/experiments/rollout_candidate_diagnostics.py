import argparse
import importlib.util
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

from paper10_geojepa_mpc.experiments.rollout_summary import build_rollout_step_record
from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
from paper10_geojepa_mpc.planning.scoring import score_candidate_actions


STATE_ATTRS = [
    "land_use",
    "swapped",
    "budget_used",
    "step_count",
    "swaps_in_block",
    "n_farmland",
    "n_forest",
    "total_weighted_slope",
    "total_farm_area",
    "farmland_nbr_count",
    "total_farmland_adj",
    "_block_farm_avail",
    "_block_forest_avail",
    "baimu_count",
    "baimu_total_area",
    "prev_slope",
    "prev_cont",
    "prev_baimu_count",
    "prev_baimu_area",
]


def _snapshot(env) -> dict:
    snap = {}
    for attr in STATE_ATTRS:
        value = getattr(env, attr)
        snap[attr] = value.copy() if isinstance(value, np.ndarray) else value
    return snap


def _restore(env, snap: dict) -> None:
    for attr, value in snap.items():
        if isinstance(value, np.ndarray):
            getattr(env, attr)[:] = value
        else:
            setattr(env, attr, value)


def _load_paper9_mpc_select_action():
    path = PAPER9_DIR / "private_source" / "mpc_plan.py"
    spec = importlib.util.spec_from_file_location("paper9_private_mpc_plan", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mpc_select_action


def topk_metrics_from_scores(true_rewards: np.ndarray, pred_scores: np.ndarray, top_k: int) -> dict:
    true_rewards = np.asarray(true_rewards, dtype=np.float64)
    pred_scores = np.asarray(pred_scores, dtype=np.float64)
    top_k = min(int(top_k), true_rewards.shape[0])
    true_best_idx = int(np.argmax(true_rewards))
    true_best_reward = float(true_rewards[true_best_idx])
    pred_order = np.argsort(pred_scores)[::-1]
    pred_top1_idx = int(pred_order[0])
    pred_topk_idx = pred_order[:top_k]
    topk_true_best = float(true_rewards[pred_topk_idx].max())
    return {
        "top1_hit": float(pred_top1_idx == true_best_idx),
        "top1_regret": float(true_best_reward - true_rewards[pred_top1_idx]),
        f"top{top_k}_hit": float(true_best_idx in set(int(x) for x in pred_topk_idx)),
        f"top{top_k}_regret": float(true_best_reward - topk_true_best),
        "true_best_reward": true_best_reward,
        "pred_top1_true_reward": float(true_rewards[pred_top1_idx]),
        "negative_reward_fraction": float((true_rewards < 0.0).mean()),
    }


def summarize_candidate_diagnostics(rows: list[dict], top_k: int) -> dict:
    key_hit = f"top{top_k}_hit"
    key_regret = f"top{top_k}_regret"
    if not rows:
        return {
            "states": 0,
            "top1_hit_rate": 0.0,
            "top1_regret_mean": 0.0,
            f"top{top_k}_hit_rate": 0.0,
            f"top{top_k}_regret_mean": 0.0,
            "negative_reward_fraction_mean": 0.0,
        }
    return {
        "states": len(rows),
        "top1_hit_rate": float(np.mean([row["top1_hit"] for row in rows])),
        "top1_regret_mean": float(np.mean([row["top1_regret"] for row in rows])),
        f"top{top_k}_hit_rate": float(np.mean([row[key_hit] for row in rows])),
        f"top{top_k}_regret_mean": float(np.mean([row[key_regret] for row in rows])),
        "negative_reward_fraction_mean": float(
            np.mean([row["negative_reward_fraction"] for row in rows])
        ),
    }


def _score_candidates(adapter, block_features, global_features, actions) -> np.ndarray:
    with torch.no_grad():
        scores = score_candidate_actions(
            adapter.model,
            torch.tensor(block_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(global_features, dtype=torch.float32, device=adapter.device),
            torch.tensor(actions, dtype=torch.long, device=adapter.device),
        )
    return scores.squeeze(0).detach().cpu().numpy()


def _candidate_true_rewards(env, actions: np.ndarray) -> np.ndarray:
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
            / "e0_bishan_rank_seed2028"
            / "rank_seed2028.pt"
        ),
    )
    parser.add_argument("--prepared-dir", default=str(ROOT))
    parser.add_argument("--rollout-steps", type=int, default=20)
    parser.add_argument("--horizon", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--candidate-actions", type=int, default=50)
    parser.add_argument("--metric-top-k", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = perf_counter()

    from private_source.blocks_env import make_env

    env = make_env(prepared_dir=args.prepared_dir)
    adapter = TorchCheckpointMPCAdapter.from_checkpoint(args.checkpoint, device=args.device)
    adapter.assert_compatible(env.n_blocks)
    mpc_select_action = _load_paper9_mpc_select_action()

    env.reset(seed=args.seed)
    rng = np.random.default_rng(args.seed)
    rollout_steps = []
    diagnostics = []
    total_reward = 0.0
    terminated = False
    truncated = False

    for step_idx in range(args.rollout_steps):
        block_features = env._get_block_features()
        global_features = env._get_global_features()
        base_mask = env.action_masks()
        action_mask = base_mask & executable_swap_mask(env)
        valid = np.where(action_mask)[0]
        if len(valid) == 0:
            break
        if len(valid) <= args.candidate_actions:
            candidate_actions = valid
        else:
            candidate_actions = rng.choice(valid, size=args.candidate_actions, replace=False)

        true_rewards = _candidate_true_rewards(env, candidate_actions)
        pred_scores = _score_candidates(
            adapter,
            block_features[np.newaxis],
            global_features[np.newaxis],
            candidate_actions[np.newaxis],
        )
        row = topk_metrics_from_scores(true_rewards, pred_scores, args.metric_top_k)
        row["step"] = step_idx + 1
        row["n_valid"] = int(len(valid))
        row["n_candidates"] = int(len(candidate_actions))
        diagnostics.append(row)

        selected_at = perf_counter()
        action, mpc_info = mpc_select_action(
            adapter,
            block_features,
            global_features,
            action_mask,
            horizon=args.horizon,
            top_k=args.top_k,
            gamma=0.99,
            n_rollouts=1,
            continuation="random",
            scoring="reward",
            rng=rng,
        )
        mpc_info["n_base_valid"] = int(base_mask.sum())
        mpc_info["n_executable_valid"] = int(action_mask.sum())
        select_time = perf_counter() - selected_at
        _, reward, terminated, truncated, info = env.step(action)
        total_reward += float(reward)
        rollout_steps.append(
            build_rollout_step_record(
                step_idx=step_idx,
                action=action,
                reward=reward,
                mpc_info=mpc_info,
                select_time_sec=select_time,
                env_info=info,
            )
        )
        if terminated or truncated:
            break

    result = {
        "checkpoint": str(args.checkpoint),
        "prepared_dir": str(args.prepared_dir),
        "seed": int(args.seed),
        "rollout_steps": int(args.rollout_steps),
        "horizon": int(args.horizon),
        "top_k": int(args.top_k),
        "candidate_actions": int(args.candidate_actions),
        "metric_top_k": int(args.metric_top_k),
        "elapsed_sec": perf_counter() - started,
        "total_reward": total_reward,
        "steps_run": len(rollout_steps),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "diagnostics": diagnostics,
        "summary": summarize_candidate_diagnostics(diagnostics, args.metric_top_k),
        "steps": rollout_steps,
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
