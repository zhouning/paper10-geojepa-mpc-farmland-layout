import argparse
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PAPER9_DIR) not in sys.path:
    sys.path.insert(0, str(PAPER9_DIR))

from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
from paper10_geojepa_mpc.experiments.rollout_summary import (
    aggregate_rollout_summaries,
    build_rollout_step_record,
    parse_seed_list,
    resolve_rollout_limit,
    summarize_rollout,
)
from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
from paper10_geojepa_mpc.planning.value_filter_selector import (
    value_filter_mpc_select_action,
)


def _load_paper9_mpc_select_action():
    path = PAPER9_DIR / "private_source" / "mpc_plan.py"
    spec = importlib.util.spec_from_file_location("paper9_private_mpc_plan", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mpc_select_action


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
    parser.add_argument(
        "--env-source",
        choices=("paper9", "neijiang"),
        default="paper9",
        help="Environment factory: paper9 prepared layout or Neijiang cross-region wrapper.",
    )
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--rollout-steps", type=int, default=3)
    parser.add_argument("--horizon", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--n-rollouts", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--mask-mode", choices=("base", "executable"), default="base")
    parser.add_argument("--scoring", choices=("reward", "slope"), default="reward")
    parser.add_argument("--selector", choices=("paper9", "value_filter"), default="paper9")
    parser.add_argument(
        "--model-score-mode",
        choices=("reward", "value", "blend"),
        default="reward",
        help="Scalar returned by the Paper10 adapter when Paper9 MPC scoring='reward'.",
    )
    parser.add_argument("--model-value-weight", type=float, default=0.5)
    parser.add_argument(
        "--candidate-score-mode",
        choices=("reward", "value", "blend"),
        default="value",
        help="Candidate filter score used only by selector=value_filter.",
    )
    parser.add_argument("--candidate-value-weight", type=float, default=0.5)
    parser.add_argument(
        "--random-continuation-mode",
        choices=("independent", "common"),
        default="independent",
        help="Random continuation mode used only by selector=value_filter.",
    )
    parser.add_argument("--stable-candidate-order", action="store_true")
    parser.add_argument("--progress-interval", type=int, default=10)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def _make_rollout_env(args):
    env_source = getattr(args, "env_source", "paper9")
    if env_source == "paper9":
        from private_source.blocks_env import make_env

        return make_env(prepared_dir=args.prepared_dir)

    if env_source == "neijiang":
        env_script = Path(args.prepared_dir) / "county_env_neijiang.py"
        if not env_script.exists():
            raise FileNotFoundError(f"Neijiang env wrapper not found: {env_script}")
        spec = importlib.util.spec_from_file_location(
            "neijiang_cross_region_county_env",
            env_script,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.make_neijiang_env()

    raise ValueError(f"Unsupported env_source: {env_source}")


def _run_episode(
    env,
    adapter,
    mpc_select_action,
    args,
    seed: int,
    rollout_limit: int,
    progress_callback=None,
    progress_interval: int = 10,
) -> dict:
    episode_started = perf_counter()
    env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    steps = []
    total_reward = 0.0
    terminated = False
    truncated = False

    for step_idx in range(rollout_limit):
        block_features = env._get_block_features()
        global_features = env._get_global_features()
        base_action_mask = env.action_masks()
        executable_mask = executable_swap_mask(env) if args.mask_mode == "executable" else base_action_mask
        action_mask = base_action_mask & executable_mask
        selected_at = perf_counter()
        selector = getattr(args, "selector", "paper9")
        if selector == "value_filter":
            action, mpc_info = mpc_select_action(
                adapter,
                block_features,
                global_features,
                action_mask,
                horizon=args.horizon,
                top_k=args.top_k,
                gamma=args.gamma,
                n_rollouts=int(getattr(args, "n_rollouts", 1)),
                continuation="random",
                scoring=args.scoring,
                candidate_score_mode=args.candidate_score_mode,
                candidate_value_weight=args.candidate_value_weight,
                random_continuation_mode=getattr(
                    args, "random_continuation_mode", "independent"
                ),
                stable_candidate_order=bool(
                    getattr(args, "stable_candidate_order", False)
                ),
                rng=rng,
            )
        else:
            action, mpc_info = mpc_select_action(
                adapter,
                block_features,
                global_features,
                action_mask,
                horizon=args.horizon,
                top_k=args.top_k,
                gamma=args.gamma,
                n_rollouts=int(getattr(args, "n_rollouts", 1)),
                continuation="random",
                scoring=args.scoring,
                rng=rng,
            )
        mpc_info["n_base_valid"] = int(base_action_mask.sum())
        mpc_info["n_executable_valid"] = int(action_mask.sum())
        select_time = perf_counter() - selected_at
        _, reward, terminated, truncated, info = env.step(action)
        total_reward += float(reward)
        steps.append(
            build_rollout_step_record(
                step_idx=step_idx,
                action=action,
                reward=reward,
                mpc_info=mpc_info,
                select_time_sec=select_time,
                env_info=info,
            )
        )
        step_number = step_idx + 1
        finished = terminated or truncated or step_number >= rollout_limit
        if progress_callback is not None and (
            finished or (progress_interval > 0 and step_number % progress_interval == 0)
        ):
            progress_callback(
                {
                    "seed": int(seed),
                    "step": int(step_number),
                    "rollout_limit": int(rollout_limit),
                    "total_reward": float(total_reward),
                    "elapsed_sec": perf_counter() - episode_started,
                    "select_time_sec": float(select_time),
                    "n_valid": int(mpc_info.get("n_valid", 0)),
                    "n_candidates": int(mpc_info.get("n_candidates", 0)),
                }
            )
        if terminated or truncated:
            break

    return {
        "checkpoint": str(args.checkpoint),
        "prepared_dir": str(args.prepared_dir),
        "env_source": getattr(args, "env_source", "paper9"),
        "seed": int(seed),
        "horizon": args.horizon,
        "top_k": args.top_k,
        "n_rollouts": int(getattr(args, "n_rollouts", 1)),
        "mask_mode": args.mask_mode,
        "scoring": args.scoring,
        "selector": getattr(args, "selector", "paper9"),
        "model_score_mode": args.model_score_mode,
        "model_value_weight": float(args.model_value_weight),
        "candidate_score_mode": getattr(args, "candidate_score_mode", None),
        "candidate_value_weight": (
            float(args.candidate_value_weight)
            if hasattr(args, "candidate_value_weight")
            else None
        ),
        "random_continuation_mode": getattr(
            args, "random_continuation_mode", "independent"
        ),
        "stable_candidate_order": bool(
            getattr(args, "stable_candidate_order", False)
        ),
        "env_max_steps": int(env.max_steps),
        "rollout_steps": int(rollout_limit),
        "steps_run": len(steps),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "total_reward": total_reward,
        "elapsed_sec": perf_counter() - episode_started,
        "steps": steps,
    }


def _partial_output_path(output: str | None) -> Path | None:
    if not output:
        return None
    output_path = Path(output)
    if output_path.suffix:
        return output_path.with_name(f"{output_path.stem}.partial{output_path.suffix}")
    return output_path.with_name(f"{output_path.name}.partial.json")


def _build_multiseed_result(
    args,
    *,
    seeds: list[int],
    rollout_limit: int,
    env_max_steps: int,
    episodes: list[dict],
    started_at: float,
    complete: bool,
) -> dict:
    summaries = [summarize_rollout(ep) for ep in episodes]
    completed_seeds = [int(ep["seed"]) for ep in episodes]
    completed_set = set(completed_seeds)
    pending_seeds = [int(seed) for seed in seeds if int(seed) not in completed_set]
    return {
        "checkpoint": str(args.checkpoint),
        "prepared_dir": str(args.prepared_dir),
        "env_source": getattr(args, "env_source", "paper9"),
        "seeds": [int(seed) for seed in seeds],
        "completed_seeds": completed_seeds,
        "pending_seeds": pending_seeds,
        "complete": bool(complete),
        "horizon": args.horizon,
        "top_k": args.top_k,
        "n_rollouts": int(getattr(args, "n_rollouts", 1)),
        "mask_mode": args.mask_mode,
        "scoring": args.scoring,
        "selector": args.selector,
        "model_score_mode": args.model_score_mode,
        "model_value_weight": float(args.model_value_weight),
        "candidate_score_mode": args.candidate_score_mode,
        "candidate_value_weight": float(args.candidate_value_weight),
        "random_continuation_mode": getattr(
            args, "random_continuation_mode", "independent"
        ),
        "stable_candidate_order": bool(
            getattr(args, "stable_candidate_order", False)
        ),
        "env_max_steps": int(env_max_steps),
        "rollout_steps": int(rollout_limit),
        "elapsed_sec": perf_counter() - started_at,
        "episodes": episodes,
        "episode_summaries": summaries,
        "aggregate": aggregate_rollout_summaries(summaries),
    }


def _write_multiseed_progress(
    args,
    *,
    seeds: list[int],
    rollout_limit: int,
    env_max_steps: int,
    episodes: list[dict],
    started_at: float,
    complete: bool,
) -> Path | None:
    partial_path = _partial_output_path(args.output)
    if partial_path is None:
        return None
    result = _build_multiseed_result(
        args,
        seeds=seeds,
        rollout_limit=rollout_limit,
        env_max_steps=env_max_steps,
        episodes=episodes,
        started_at=started_at,
        complete=complete,
    )
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return partial_path


def main() -> None:
    args = parse_args()
    started = perf_counter()

    env = _make_rollout_env(args)
    rollout_limit = resolve_rollout_limit(env, args.max_steps, args.rollout_steps)
    adapter_score_mode = args.model_score_mode
    adapter_value_weight = args.model_value_weight
    if args.selector == "value_filter":
        adapter_score_mode = "reward"
        adapter_value_weight = 0.5

    adapter = TorchCheckpointMPCAdapter.from_checkpoint(
        args.checkpoint,
        device=args.device,
        score_mode=adapter_score_mode,
        value_weight=adapter_value_weight,
    )
    adapter.assert_compatible(env.n_blocks)
    mpc_select_action = (
        value_filter_mpc_select_action
        if args.selector == "value_filter"
        else _load_paper9_mpc_select_action()
    )

    seeds = parse_seed_list(args.seeds) if args.seeds else [int(args.seed)]
    episodes = []

    def print_progress(progress: dict) -> None:
        print(
            "[rollout] seed {seed} step {step}/{limit} reward={reward:.4f} "
            "elapsed={elapsed:.2f}s select={select:.3f}s valid={valid} candidates={candidates}".format(
                seed=progress["seed"],
                step=progress["step"],
                limit=progress["rollout_limit"],
                reward=progress["total_reward"],
                elapsed=progress["elapsed_sec"],
                select=progress["select_time_sec"],
                valid=progress["n_valid"],
                candidates=progress["n_candidates"],
            ),
            file=sys.stderr,
            flush=True,
        )

    for index, seed in enumerate(seeds, start=1):
        if len(seeds) > 1:
            print(
                f"[rollout] seed {seed} ({index}/{len(seeds)}) starting",
                file=sys.stderr,
                flush=True,
            )
        episode = _run_episode(
            env,
            adapter,
            mpc_select_action,
            args,
            seed,
            rollout_limit,
            progress_callback=print_progress,
            progress_interval=int(args.progress_interval),
        )
        episodes.append(episode)
        if len(seeds) > 1:
            partial_path = _write_multiseed_progress(
                args,
                seeds=seeds,
                rollout_limit=rollout_limit,
                env_max_steps=int(env.max_steps),
                episodes=episodes,
                started_at=started,
                complete=False,
            )
            print(
                "[rollout] seed {seed} done in {elapsed:.2f}s; partial={partial}".format(
                    seed=seed,
                    elapsed=float(episode.get("elapsed_sec", 0.0)),
                    partial=str(partial_path) if partial_path else "",
                ),
                file=sys.stderr,
                flush=True,
            )

    if len(episodes) == 1:
        result = episodes[0]
    else:
        result = _build_multiseed_result(
            args,
            seeds=seeds,
            rollout_limit=rollout_limit,
            env_max_steps=int(env.max_steps),
            episodes=episodes,
            started_at=started,
            complete=True,
        )
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
