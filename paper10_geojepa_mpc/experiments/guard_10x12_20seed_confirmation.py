import argparse
import json
from pathlib import Path
from statistics import mean, median
from typing import Any

import numpy as np

from paper10_geojepa_mpc.experiments.compare_multiseed_rollouts import (
    compare_rollout_runs,
    markdown_report as comparison_markdown_report,
)
from paper10_geojepa_mpc.experiments.rollout_summary import (
    aggregate_rollout_summaries,
    summarize_rollout,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"

BASELINE_0_4_JSON = (
    RESULTS / "e0_bishan_10x12_top4_blend010_h5_k50_seeds0-4_100step_consolidated_2026-07-07.json"
)
BASELINE_5_19_JSON = (
    RESULTS / "e0_bishan_10x12_top4_blend010_h5_k50_seeds5-19_100step_2026-07-08.json"
)
GUARD_0_4_JSON = (
    RESULTS
    / "e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json"
)
GUARD_5_19_JSON = (
    RESULTS
    / "e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds5-19_100step_2026-07-08.json"
)

BASELINE_COMBINED_JSON = (
    "e0_bishan_10x12_top4_blend010_h5_k50_seeds0-19_100step_2026-07-08.json"
)
GUARD_COMBINED_JSON = (
    "e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds0-19_100step_2026-07-08.json"
)
COMPARISON_JSON = (
    "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.json"
)
COMPARISON_MD = (
    "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.md"
)
PAIRED_STATS_JSON = (
    "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_paired_stats_2026-07-08.json"
)
TRIAGE_MD = (
    "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_confirmation_triage_2026-07-08.md"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _episodes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "episodes" in payload:
        return list(payload["episodes"])
    if "steps" in payload:
        return [payload]
    raise ValueError("rollout payload must contain episodes or steps")


def _seed_to_episode(payloads: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    by_seed: dict[int, dict[str, Any]] = {}
    for payload in payloads:
        for episode in _episodes(payload):
            seed = int(episode["seed"])
            if seed in by_seed:
                raise ValueError(f"duplicate seed {seed}")
            by_seed[seed] = dict(episode)
    return by_seed


def _merge_batches(
    batches: list[dict[str, Any]],
    expected_seeds: list[int],
    *,
    label: str,
) -> dict[str, Any]:
    by_seed = _seed_to_episode(batches)
    observed = sorted(by_seed)
    expected = [int(seed) for seed in expected_seeds]
    if observed != expected:
        raise ValueError(
            f"{label} expected matched seeds {expected}, observed {observed}"
        )

    template = dict(batches[0])
    for key in (
        "episodes",
        "episode_summaries",
        "aggregate",
        "completed_seeds",
        "pending_seeds",
        "complete",
        "elapsed_sec",
    ):
        template.pop(key, None)
    episodes = [by_seed[seed] for seed in expected]
    summaries = [summarize_rollout(episode) for episode in episodes]
    template.update(
        {
            "seeds": expected,
            "completed_seeds": expected,
            "pending_seeds": [],
            "complete": True,
            "episodes": episodes,
            "episode_summaries": summaries,
            "aggregate": aggregate_rollout_summaries(summaries),
        }
    )
    return template


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return float((sum((value - avg) ** 2 for value in values) / (len(values) - 1)) ** 0.5)


def _bootstrap_ci(
    values: list[float],
    *,
    seed: int = 20260708,
    draws: int = 10000,
) -> list[float]:
    if not values:
        return [0.0, 0.0]
    arr = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    samples = rng.choice(arr, size=(draws, arr.shape[0]), replace=True)
    means = samples.mean(axis=1)
    return [
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    ]


def _episode_rewards(payload: dict[str, Any]) -> dict[int, float]:
    return {
        int(episode["seed"]): float(episode.get("total_reward", 0.0))
        for episode in _episodes(payload)
    }


def _audit_summary(guard_payload: dict[str, Any]) -> dict[str, Any]:
    rows = [
        row
        for episode in _episodes(guard_payload)
        for row in episode.get("audit_rows", [])
    ]
    if not rows:
        return {
            "audited_states": 0,
            "switches": 0,
            "switch_rate": 0.0,
            "mean_audit_action_count": 0.0,
            "mean_true_reward_time_sec": 0.0,
            "selected_true_reward_regret_mean": 0.0,
        }
    switches = sum(
        1
        for row in rows
        if int(row.get("execution_action", row.get("selected_action", -1)))
        != int(row.get("selected_action", -1))
    )
    return {
        "audited_states": int(len(rows)),
        "switches": int(switches),
        "switch_rate": float(switches / len(rows)),
        "mean_audit_action_count": float(
            mean(float(row["audit_action_count"]) for row in rows)
        ),
        "mean_true_reward_time_sec": float(
            mean(float(row.get("true_reward_time_sec", 0.0)) for row in rows)
        ),
        "selected_true_reward_regret_mean": float(
            mean(float(row.get("selected_true_reward_regret", 0.0)) for row in rows)
        ),
    }


def _paired_stats(
    baseline_payload: dict[str, Any],
    guard_payload: dict[str, Any],
    expected_seeds: list[int],
) -> dict[str, Any]:
    baseline_rewards = _episode_rewards(baseline_payload)
    guard_rewards = _episode_rewards(guard_payload)
    rows = []
    deltas = []
    for seed in expected_seeds:
        baseline = float(baseline_rewards[int(seed)])
        guard = float(guard_rewards[int(seed)])
        delta = guard - baseline
        deltas.append(delta)
        rows.append(
            {
                "seed": int(seed),
                "baseline_reward": baseline,
                "candidate_reward": guard,
                "delta_vs_baseline": float(delta),
            }
        )

    std = _sample_std(deltas)
    sem = float(std / (len(deltas) ** 0.5)) if deltas else 0.0
    avg = float(mean(deltas)) if deltas else 0.0
    ci = _bootstrap_ci(deltas)
    return {
        "n": int(len(deltas)),
        "baseline_mean_reward": float(mean(baseline_rewards.values())),
        "candidate_mean_reward": float(mean(guard_rewards.values())),
        "mean_delta": avg,
        "median_delta": float(median(deltas)) if deltas else 0.0,
        "min_delta": float(min(deltas)) if deltas else 0.0,
        "max_delta": float(max(deltas)) if deltas else 0.0,
        "wins": int(sum(delta > 0.0 for delta in deltas)),
        "losses": int(sum(delta < 0.0 for delta in deltas)),
        "ties": int(sum(delta == 0.0 for delta in deltas)),
        "sample_std_delta": std,
        "standard_error_delta": sem,
        "bootstrap_95ci_delta": ci,
        "normal_approx_95ci_delta": [float(avg - 1.96 * sem), float(avg + 1.96 * sem)],
        "seed_deltas": rows,
        "candidate_guard_summary": _audit_summary(guard_payload),
    }


def build_confirmation_packet(
    *,
    baseline_batches: list[dict[str, Any]],
    guard_batches: list[dict[str, Any]],
    expected_seeds: list[int],
) -> dict[str, Any]:
    expected = [int(seed) for seed in expected_seeds]
    baseline_combined = _merge_batches(
        baseline_batches,
        expected,
        label="baseline",
    )
    guard_combined = _merge_batches(guard_batches, expected, label="guard")
    comparison = compare_rollout_runs(
        "10x12_top4_blend010",
        baseline_combined,
        "10x12_top4_rewardtop7_m160",
        guard_combined,
    )
    stats = _paired_stats(baseline_combined, guard_combined, expected)
    return {
        "date": "2026-07-08",
        "status": "descriptive_confirmation",
        "setting": "bishan_10x12_top4",
        "seed_count": int(len(expected)),
        "expected_seeds": expected,
        "protocol": {
            "baseline": "blend_w0p10_value_filter",
            "candidate": "true_reward_margin_guard",
            "audit_set": "rewardtop7",
            "switch_margin": 1.6,
            "horizon": 5,
            "top_k": 50,
            "rollout_steps": 100,
            "candidate_score_mode": "blend",
            "candidate_value_weight": 0.1,
            "random_continuation_mode": "independent",
        },
        "small_scale_guard": {
            "algorithm": "true_reward_margin_guard",
            "audit_set": "rewardtop7",
            "switch_margin": 1.6,
            "n_seeds": int(len(expected)),
            "baseline_mean_reward": float(stats["baseline_mean_reward"]),
            "candidate_mean_reward": float(stats["candidate_mean_reward"]),
            "mean_delta_vs_baseline": float(stats["mean_delta"]),
            "median_delta_vs_baseline": float(stats["median_delta"]),
            "min_seed_delta_vs_baseline": float(stats["min_delta"]),
            "max_seed_delta_vs_baseline": float(stats["max_delta"]),
            "seed_wins": int(stats["wins"]),
            "seed_losses": int(stats["losses"]),
            "bootstrap_95ci_delta": list(stats["bootstrap_95ci_delta"]),
        },
        "claim_locks": {
            "universal_fixed_margin_supported": False,
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_supported": False,
            "final_submission_readiness_supported": False,
        },
        "source_boundary": {
            "new_rollout_batches": "seeds5-19 baseline and guard",
            "post_hoc_margin_tuning": False,
            "submission_approval": False,
        },
        "baseline_combined": baseline_combined,
        "guard_combined": guard_combined,
        "comparison": comparison,
        "paired_stats": stats,
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def markdown_report(packet: dict[str, Any]) -> str:
    guard = packet["small_scale_guard"]
    stats = packet["paired_stats"]
    lines = [
        "# Bishan 10x12/top4 rewardtop7 20-seed confirmation",
        "",
        "Date: 2026-07-08",
        "",
        "Status: descriptive_confirmation",
        "",
        "This packet extends the small-scale `rewardtop7 margin=1.60` guard from 5 to 20 matched seeds.",
        "It is not final submission readiness.",
        "",
        "## Protocol",
        "",
        "- setting: `10x12/top4`",
        "- baseline: `blend_w0p10`, horizon 5, top-k 50, 100-step rollouts",
        "- guard: `rewardtop7 margin=1.60`",
        "- audit set: selected action plus model-reward top7 actions",
        "- seeds: 20 matched seeds",
        "- post-hoc margin tuning in this task: false",
        "",
        "## Result",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| baseline mean reward | {_fmt(guard['baseline_mean_reward'])} |",
        f"| guard mean reward | {_fmt(guard['candidate_mean_reward'])} |",
        f"| mean delta vs baseline | {_fmt(guard['mean_delta_vs_baseline'])} |",
        f"| median delta vs baseline | {_fmt(guard['median_delta_vs_baseline'])} |",
        f"| seed wins | {guard['seed_wins']} / {guard['n_seeds']} |",
        f"| seed losses | {guard['seed_losses']} / {guard['n_seeds']} |",
        f"| min seed delta | {_fmt(guard['min_seed_delta_vs_baseline'])} |",
        f"| max seed delta | {_fmt(guard['max_seed_delta_vs_baseline'])} |",
        f"| bootstrap 95% CI lower | {_fmt(stats['bootstrap_95ci_delta'][0])} |",
        f"| bootstrap 95% CI upper | {_fmt(stats['bootstrap_95ci_delta'][1])} |",
        "",
        "## Interpretation",
        "",
        "Use this as a 10x12/top4 setting-specific guard confirmation only.",
        "It supports the transferable rewardtop7 guard mechanism only within the tested small-scale setting and calibrated margin.",
        "It does not make `1.60` a universal fixed switch margin.",
        "",
        "## Claim locks",
        "",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not treat this as final submission readiness.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(packet: dict[str, Any], output_dir: Path | str) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "baseline_combined_json": output_dir / BASELINE_COMBINED_JSON,
        "guard_combined_json": output_dir / GUARD_COMBINED_JSON,
        "comparison_json": output_dir / COMPARISON_JSON,
        "comparison_md": output_dir / COMPARISON_MD,
        "paired_stats_json": output_dir / PAIRED_STATS_JSON,
        "triage_md": output_dir / TRIAGE_MD,
    }
    paths["baseline_combined_json"].write_text(
        json.dumps(packet["baseline_combined"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    paths["guard_combined_json"].write_text(
        json.dumps(packet["guard_combined"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    paths["comparison_json"].write_text(
        json.dumps(packet["comparison"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    paths["comparison_md"].write_text(
        comparison_markdown_report(packet["comparison"]),
        encoding="utf-8",
    )
    paths["paired_stats_json"].write_text(
        json.dumps(packet["paired_stats"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    paths["triage_md"].write_text(markdown_report(packet), encoding="utf-8")
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-0-4", default=str(BASELINE_0_4_JSON))
    parser.add_argument("--baseline-5-19", default=str(BASELINE_5_19_JSON))
    parser.add_argument("--guard-0-4", default=str(GUARD_0_4_JSON))
    parser.add_argument("--guard-5-19", default=str(GUARD_5_19_JSON))
    parser.add_argument("--output-dir", default=str(RESULTS))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = build_confirmation_packet(
        baseline_batches=[
            _load_json(Path(args.baseline_0_4)),
            _load_json(Path(args.baseline_5_19)),
        ],
        guard_batches=[
            _load_json(Path(args.guard_0_4)),
            _load_json(Path(args.guard_5_19)),
        ],
        expected_seeds=list(range(20)),
    )
    paths = write_outputs(packet, Path(args.output_dir))
    summary = {
        "status": packet["status"],
        "seed_count": packet["seed_count"],
        "mean_delta": packet["paired_stats"]["mean_delta"],
        "wins": packet["paired_stats"]["wins"],
        "losses": packet["paired_stats"]["losses"],
        "outputs": {key: str(path) for key, path in paths.items()},
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
