import argparse
from dataclasses import dataclass
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

from paper10_geojepa_mpc.experiments.value_filter_candidate_overlap import (
    _score_valid_actions,
    candidate_overlap_metrics,
    summarize_overlap_rows,
)
from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
from paper10_geojepa_mpc.planning.scoring import SCORE_MODES


DEFAULT_SCORE_CONFIG_SPECS = (
    "value:0.50",
    "blend:0.10",
    "zscore_blend:0.20",
    "zscore_blend:0.50",
    "zscore_blend:0.80",
)


def _weight_key(value_weight: float) -> str:
    return f"{float(value_weight):.2f}".replace(".", "p")


@dataclass(frozen=True)
class CandidateScoreConfig:
    mode: str
    value_weight: float

    def __post_init__(self) -> None:
        if self.mode not in SCORE_MODES:
            raise ValueError(
                "candidate score mode must be one of: "
                + ", ".join(sorted(SCORE_MODES))
            )
        if not 0.0 <= float(self.value_weight) <= 1.0:
            raise ValueError("value_weight must be in [0, 1]")

    @property
    def key(self) -> str:
        return f"{self.mode}_w{_weight_key(self.value_weight)}"

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "mode": self.mode,
            "value_weight": float(self.value_weight),
        }


def parse_score_config_specs(specs: list[str] | tuple[str, ...]) -> list[CandidateScoreConfig]:
    configs = []
    for spec in specs:
        parts = str(spec).split(":")
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            raise ValueError("score config must use mode:weight format")
        mode = parts[0].strip()
        try:
            value_weight = float(parts[1])
        except ValueError as exc:
            raise ValueError("score config weight must be numeric") from exc
        configs.append(CandidateScoreConfig(mode, value_weight))
    if not configs:
        raise ValueError("at least one score config is required")
    keys = [config.key for config in configs]
    if len(set(keys)) != len(keys):
        raise ValueError("score config keys must be unique")
    return configs


def _rank_summaries(configs: list[CandidateScoreConfig], summaries: dict[str, dict]) -> list[dict]:
    ranking = []
    for config in configs:
        summary = summaries[config.key]
        ranking.append({**config.as_dict(), **summary})
    return sorted(
        ranking,
        key=lambda row: (
            float(row["candidate_top1_reward_regret_mean"]),
            float(row["candidate_topk_best_reward_regret_mean"]),
            -float(row["topk_overlap_fraction_mean"]),
            -float(row["score_spearman_mean"]),
            row["key"],
        ),
    )


def _short_rollout_command(
    *,
    checkpoint: str,
    prepared_dir: str,
    seed: int,
    top_k: int,
    config: dict,
    rollout_steps: int,
) -> str:
    return (
        "python -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke "
        f"--checkpoint {checkpoint} "
        f"--prepared-dir {prepared_dir} "
        "--selector value_filter "
        "--mask-mode executable "
        "--horizon 5 "
        f"--top-k {int(top_k)} "
        f"--rollout-steps {int(rollout_steps)} "
        f"--seed {int(seed)} "
        f"--candidate-score-mode {config['mode']} "
        f"--candidate-value-weight {float(config['value_weight']):.2f}"
    )


def build_score_sweep_packet(
    *,
    configs: list[CandidateScoreConfig],
    rows_by_config: dict[str, list[dict]],
    checkpoint: str,
    prepared_dir: str,
    seed: int,
    steps_requested: int,
    steps_run: int,
    top_k: int,
    reward_top1_policy_total_reward: float,
    elapsed_sec: float,
    short_rollout_steps: int = 10,
) -> dict:
    if not configs:
        raise ValueError("configs must not be empty")
    missing = [config.key for config in configs if config.key not in rows_by_config]
    if missing:
        raise ValueError(f"rows missing for score configs: {missing}")

    summaries = {
        config.key: summarize_overlap_rows(rows_by_config[config.key])
        for config in configs
    }
    ranking = _rank_summaries(configs, summaries)
    recommended = ranking[0]
    commands = {
        row["key"]: _short_rollout_command(
            checkpoint=checkpoint,
            prepared_dir=prepared_dir,
            seed=seed,
            top_k=top_k,
            config=row,
            rollout_steps=short_rollout_steps,
        )
        for row in ranking
    }

    return {
        "checkpoint": str(checkpoint),
        "prepared_dir": str(prepared_dir),
        "seed": int(seed),
        "steps_requested": int(steps_requested),
        "steps_run": int(steps_run),
        "top_k": int(top_k),
        "reward_top1_policy_total_reward": float(reward_top1_policy_total_reward),
        "elapsed_sec": float(elapsed_sec),
        "configs": [config.as_dict() for config in configs],
        "summaries": summaries,
        "ranking": ranking,
        "recommended_config": recommended,
        "short_rollout_steps": int(short_rollout_steps),
        "short_rollout_commands": commands,
        "recommended_short_rollout_command": commands[recommended["key"]],
        "rows_by_config": rows_by_config,
        "source_boundary": {
            "diagnostic_type": "candidate_score_sweep",
            "reran_rollouts": False,
            "reran_training": False,
            "interpretation": (
                "Candidate-score overlap diagnostic on reward-top1 states; "
                "use the recommended command for a separate short rollout "
                "before any confirmatory 100-step or 50-state run."
            ),
        },
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def render_score_sweep_markdown(packet: dict) -> str:
    lines = [
        "# Candidate score sweep diagnostic",
        "",
        "This diagnostic compares candidate filter scoring modes on the same reward-top1 state path. It is not a confirmatory rollout.",
        "",
        f"- checkpoint: `{packet['checkpoint']}`",
        f"- prepared_dir: `{packet['prepared_dir']}`",
        f"- seed: `{packet['seed']}`",
        f"- steps: `{packet['steps_run']}/{packet['steps_requested']}`",
        f"- top_k: `{packet['top_k']}`",
        "",
        "| key | mode | value_weight | topk_overlap | top1_regret | topk_best_regret | spearman |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in packet["ranking"]:
        lines.append(
            "| {key} | {mode} | {weight} | {overlap} | {top1_regret} | {topk_regret} | {spearman} |".format(
                key=row["key"],
                mode=row["mode"],
                weight=_fmt(row["value_weight"]),
                overlap=_fmt(row["topk_overlap_fraction_mean"]),
                top1_regret=_fmt(row["candidate_top1_reward_regret_mean"]),
                topk_regret=_fmt(row["candidate_topk_best_reward_regret_mean"]),
                spearman=_fmt(row["score_spearman_mean"]),
            )
        )
    recommended = packet["recommended_config"]
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            f"Promote `{recommended['key']}` to short rollout first.",
            "",
            "```powershell",
            packet["recommended_short_rollout_command"],
            "```",
            "",
            "## Boundary",
            "",
            "- No training was rerun.",
            "- No confirmatory rollout was rerun inside this diagnostic.",
            "- Escalate only if the short rollout improves or preserves reward with acceptable variance.",
            "",
        ]
    )
    return "\n".join(lines)


def run_candidate_score_sweep(
    *,
    checkpoint: str,
    prepared_dir: str,
    steps: int,
    top_k: int,
    seed: int,
    device: str,
    configs: list[CandidateScoreConfig],
    short_rollout_steps: int = 10,
) -> dict:
    started = perf_counter()

    from private_source.blocks_env import make_env

    env = make_env(prepared_dir=prepared_dir)
    adapter = TorchCheckpointMPCAdapter.from_checkpoint(checkpoint, device=device)
    adapter.assert_compatible(env.n_blocks)

    env.reset(seed=seed)
    rows_by_config = {config.key: [] for config in configs}
    total_reward = 0.0
    steps_run = 0

    for step_idx in range(int(steps)):
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
        score_time_sec = float(perf_counter() - scored_at)
        for config in configs:
            config_scored_at = perf_counter()
            candidate_scores = _score_valid_actions(
                adapter,
                block_features,
                global_features,
                valid_actions,
                config.mode,
                config.value_weight,
            )
            row = candidate_overlap_metrics(
                reward_scores,
                candidate_scores,
                top_k,
                actions=valid_actions,
            )
            row["step"] = int(step_idx + 1)
            row["n_valid"] = int(valid_actions.shape[0])
            row["reward_score_time_sec"] = score_time_sec
            row["candidate_score_time_sec"] = float(perf_counter() - config_scored_at)
            rows_by_config[config.key].append(row)

        reward_top1_idx = int(np.argsort(reward_scores)[::-1][0])
        action = int(valid_actions[reward_top1_idx])
        _, reward, terminated, truncated, _ = env.step(action)
        total_reward += float(reward)
        steps_run += 1
        if terminated or truncated:
            break

    return build_score_sweep_packet(
        configs=configs,
        rows_by_config=rows_by_config,
        checkpoint=checkpoint,
        prepared_dir=prepared_dir,
        seed=seed,
        steps_requested=steps,
        steps_run=steps_run,
        top_k=top_k,
        reward_top1_policy_total_reward=total_reward,
        elapsed_sec=perf_counter() - started,
        short_rollout_steps=short_rollout_steps,
    )


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
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--score-config",
        action="append",
        default=None,
        help="Candidate score config in mode:weight format. Repeatable.",
    )
    parser.add_argument("--short-rollout-steps", type=int, default=10)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configs = parse_score_config_specs(
        args.score_config if args.score_config else DEFAULT_SCORE_CONFIG_SPECS
    )
    packet = run_candidate_score_sweep(
        checkpoint=args.checkpoint,
        prepared_dir=args.prepared_dir,
        steps=args.steps,
        top_k=args.top_k,
        seed=args.seed,
        device=args.device,
        configs=configs,
        short_rollout_steps=args.short_rollout_steps,
    )

    json_text = json.dumps(packet, indent=2, sort_keys=True)
    print(json_text)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json_text, encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(render_score_sweep_markdown(packet), encoding="utf-8")


if __name__ == "__main__":
    main()
