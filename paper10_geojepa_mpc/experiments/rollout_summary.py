from collections import Counter
import argparse
import json
from pathlib import Path
from statistics import mean


def parse_seed_list(value: str) -> list[int]:
    seeds = []
    for part in value.split(","):
        item = part.strip()
        if not item:
            continue
        if "-" in item:
            start_text, end_text = item.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            step = 1 if end >= start else -1
            seeds.extend(range(start, end + step, step))
        else:
            seeds.append(int(item))
    return seeds


def resolve_rollout_limit(env, env_max_steps: int | None, rollout_steps: int | None) -> int:
    if env_max_steps is not None:
        env.max_steps = int(env_max_steps)
    limit = int(rollout_steps) if rollout_steps is not None else int(env.max_steps)
    return min(limit, int(env.max_steps))


def build_rollout_step_record(
    *,
    step_idx: int,
    action: int,
    reward: float,
    mpc_info: dict,
    select_time_sec: float,
    env_info: dict,
) -> dict:
    record = {
        "step": int(step_idx) + 1,
        "action": int(action),
        "reward": float(reward),
        "completed_swaps": int(env_info.get("completed_swaps", -1)),
        "n_valid": int(mpc_info.get("n_valid", 0)),
        "n_candidates": int(mpc_info.get("n_candidates", 0)),
        "n_base_valid": int(mpc_info.get("n_base_valid", mpc_info.get("n_valid", 0))),
        "n_executable_valid": int(
            mpc_info.get("n_executable_valid", mpc_info.get("n_valid", 0))
        ),
        "best_cumrew": float(mpc_info.get("best_cumrew", 0.0)),
        "select_time_sec": float(select_time_sec),
        "slope_change_pct": float(env_info.get("slope_change_pct", 0.0)),
        "cont_change": float(env_info.get("cont_change", 0.0)),
        "baimu_area_change_ha": float(env_info.get("baimu_area_change_ha", 0.0)),
    }
    for key in ("score_time_sec", "first_step_time_sec", "rollout_time_sec"):
        if key in mpc_info:
            record[key] = float(mpc_info[key])
    return record


def summarize_rollout(result: dict) -> dict:
    steps = result.get("steps", [])
    actions = [int(step["action"]) for step in steps]
    rewards = [float(step["reward"]) for step in steps]
    action_counts = Counter(actions)
    repeated = [
        {"action": int(action), "count": int(count)}
        for action, count in action_counts.most_common()
        if count > 1
    ]

    completed_values = [
        int(step["completed_swaps"])
        for step in steps
        if "completed_swaps" in step and int(step["completed_swaps"]) >= 0
    ]
    has_completed_swaps = len(completed_values) == len(steps) and len(steps) > 0
    zero_swap_steps = None
    negative_zero_swap_steps = None
    if has_completed_swaps:
        zero_swap_steps = sum(1 for step in steps if int(step["completed_swaps"]) == 0)
        negative_zero_swap_steps = sum(
            1
            for step in steps
            if int(step["completed_swaps"]) == 0 and float(step["reward"]) < 0.0
        )

    final_step = steps[-1] if steps else {}
    select_times = [float(step["select_time_sec"]) for step in steps if "select_time_sec" in step]
    return {
        "seed": result.get("seed"),
        "horizon": result.get("horizon"),
        "top_k": result.get("top_k"),
        "steps_run": len(steps),
        "total_reward": float(result.get("total_reward", sum(rewards))),
        "elapsed_sec": float(result.get("elapsed_sec", 0.0)),
        "unique_actions": len(action_counts),
        "repeated_action_count": len(repeated),
        "max_action_repeat": max(action_counts.values(), default=0),
        "top_repeated_actions": repeated[:10],
        "negative_reward_steps": sum(1 for reward in rewards if reward < 0.0),
        "positive_reward_steps": sum(1 for reward in rewards if reward > 0.0),
        "zero_reward_steps": sum(1 for reward in rewards if reward == 0.0),
        "zero_swap_steps": zero_swap_steps,
        "negative_zero_swap_steps": negative_zero_swap_steps,
        "mean_select_time_sec": mean(select_times) if select_times else 0.0,
        "final_metrics": {
            "slope_change_pct": float(final_step.get("slope_change_pct", 0.0)),
            "cont_change": float(final_step.get("cont_change", 0.0)),
            "baimu_area_change_ha": float(final_step.get("baimu_area_change_ha", 0.0)),
        },
    }


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def aggregate_rollout_summaries(summaries: list[dict]) -> dict:
    slopes = [float(s["final_metrics"]["slope_change_pct"]) for s in summaries]
    conts = [float(s["final_metrics"]["cont_change"]) for s in summaries]
    baimu = [float(s["final_metrics"]["baimu_area_change_ha"]) for s in summaries]
    rewards = [float(s["total_reward"]) for s in summaries]
    zero_swaps = [
        int(s["zero_swap_steps"]) for s in summaries if s.get("zero_swap_steps") is not None
    ]
    neg_zero_swaps = [
        int(s["negative_zero_swap_steps"])
        for s in summaries
        if s.get("negative_zero_swap_steps") is not None
    ]
    return {
        "n_episodes": len(summaries),
        "total_reward_mean": _mean(rewards),
        "slope_change_pct_mean": _mean(slopes),
        "cont_change_mean": _mean(conts),
        "baimu_area_change_ha_mean": _mean(baimu),
        "zero_swap_steps_sum": sum(zero_swaps) if zero_swaps else None,
        "negative_zero_swap_steps_sum": sum(neg_zero_swaps) if neg_zero_swaps else None,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Rollout JSON produced by run_e0_env_rollout_smoke.py")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    result = json.loads(input_path.read_text(encoding="utf-8"))
    summary = summarize_rollout(result)
    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
