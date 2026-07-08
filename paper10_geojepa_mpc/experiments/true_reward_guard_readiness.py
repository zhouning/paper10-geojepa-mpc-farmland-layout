"""Source-derived readiness audit for the Paper10 true-reward guard evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_PRIMARY_COMPARISON = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-07.json"
)
DEFAULT_PRIMARY_STATS = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_20seed_paired_stats_2026-07-07.json"
)
DEFAULT_SMALL_SCALE_STATS = (
    RESULTS
    / "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_paired_stats_2026-07-08.json"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _audit_set_from_name(name: str) -> str:
    if "rewardtop7" in name:
        return "rewardtop7"
    if "audit7x7" in name:
        return "audit7x7"
    if "audit5x5" in name:
        return "audit5x5"
    return "unknown"


def _primary_guard_summary(payload: dict[str, Any]) -> dict[str, Any]:
    seed_rows = payload["seed_deltas"]
    seed_deltas = [float(row["total_reward_delta"]) for row in seed_rows]
    baseline = payload["baseline"]["aggregate"]
    candidate = payload["candidate"]["aggregate"]
    n_seeds = int(baseline["n_episodes"])
    seed_wins = sum(1 for delta in seed_deltas if delta > 0.0)
    seed_losses = sum(1 for delta in seed_deltas if delta < 0.0)

    return {
        "setting": "bishan_20x16_top5",
        "algorithm": "true_reward_margin_guard",
        "audit_set": _audit_set_from_name(payload["candidate"]["name"]),
        "switch_margin": 1.5,
        "baseline_name": payload["baseline"]["name"],
        "candidate_name": payload["candidate"]["name"],
        "n_seeds": n_seeds,
        "seed_wins": int(seed_wins),
        "seed_losses": int(seed_losses),
        "baseline_mean_reward": float(baseline["total_reward_mean"]),
        "candidate_mean_reward": float(candidate["total_reward_mean"]),
        "mean_delta_vs_baseline": float(
            payload["aggregate_delta"]["total_reward_mean"]
        ),
        "min_seed_delta_vs_baseline": float(min(seed_deltas)),
        "max_seed_delta_vs_baseline": float(max(seed_deltas)),
        "secondary_metric_deltas": {
            key: float(value)
            for key, value in payload["aggregate_delta"].items()
            if key != "total_reward_mean"
        },
        "seed_deltas": [
            {
                "seed": int(row["seed"]),
                "total_reward_delta": float(row["total_reward_delta"]),
                "slope_change_pct_delta": float(row["slope_change_pct_delta"]),
                "cont_change_delta": float(row["cont_change_delta"]),
                "baimu_area_change_ha_delta": float(
                    row["baimu_area_change_ha_delta"]
                ),
            }
            for row in seed_rows
        ],
    }

def _guard_stats_summary(guard_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "audited_states": int(guard_summary["audited_states"]),
        "switches": int(guard_summary["switches"]),
        "switch_rate": float(guard_summary["switch_rate"]),
        "mean_audit_action_count": float(guard_summary["mean_audit_action_count"]),
        "selected_is_audit_true_best_rate": float(
            guard_summary["selected_is_audit_true_best_rate"]
        ),
        "selected_true_reward_regret_mean": float(
            guard_summary["selected_true_reward_regret_mean"]
        ),
        "mean_true_reward_time_sec": float(
            guard_summary["mean_true_reward_time_sec"]
        ),
    }


def _primary_paired_stats_summary(payload: dict[str, Any]) -> dict[str, Any]:
    n = int(payload["n"])
    wins = int(payload.get("wins", payload.get("wins_vs_baseline")))
    losses = int(payload.get("losses", payload.get("losses_vs_baseline")))
    ties = int(payload.get("ties", payload.get("ties_vs_baseline", n - wins - losses)))
    result = {
        "n": n,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "baseline_mean_reward": float(payload["baseline_mean_reward"]),
        "candidate_mean_reward": float(payload["candidate_mean_reward"]),
        "mean_delta": float(
            payload["mean_delta"]
            if "mean_delta" in payload
            else payload["mean_delta_vs_baseline"]
        ),
        "median_delta": float(
            payload["median_delta"]
            if "median_delta" in payload
            else payload["median_delta_vs_baseline"]
        ),
        "min_delta": float(
            payload["min_delta"]
            if "min_delta" in payload
            else payload["min_delta_vs_baseline"]
        ),
        "max_delta": float(
            payload["max_delta"]
            if "max_delta" in payload
            else payload["max_delta_vs_baseline"]
        ),
        "sample_std_delta": float(payload["sample_std_delta"]),
        "standard_error_delta": float(payload["standard_error_delta"]),
        "bootstrap_95ci_delta": [
            float(payload["bootstrap_95ci_delta"][0]),
            float(payload["bootstrap_95ci_delta"][1]),
        ],
        "normal_approx_95ci_delta": [
            float(payload["normal_approx_95ci_delta"][0]),
            float(payload["normal_approx_95ci_delta"][1]),
        ],
        "candidate_guard_summary": _guard_stats_summary(
            payload["candidate_guard_summary"]
        ),
    }
    if "dual7x7_guard_summary" in payload:
        result.update(
            {
                "dual7x7_mean_reward": float(payload["dual7x7_mean_reward"]),
                "mean_delta_vs_dual7x7": float(payload["mean_delta_vs_dual7x7"]),
                "wins_vs_dual7x7": int(payload["wins_vs_dual7x7"]),
                "losses_vs_dual7x7": int(payload["losses_vs_dual7x7"]),
                "ties_vs_dual7x7": int(payload["ties_vs_dual7x7"]),
                "dual7x7_guard_summary": _guard_stats_summary(
                    payload["dual7x7_guard_summary"]
                ),
            }
        )
    return result

def _small_scale_value(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    raise KeyError(keys[0])


def _small_scale_guard_summary(payload: dict[str, Any]) -> dict[str, Any]:
    seed_rows = payload["seed_deltas"]
    seed_deltas = []
    for row in seed_rows:
        if "delta_vs_baseline" in row:
            seed_deltas.append(float(row["delta_vs_baseline"]))
        else:
            seed_deltas.append(float(row["total_reward_delta"]))
    return {
        "setting": "bishan_10x12_top4",
        "algorithm": "true_reward_margin_guard",
        "audit_set": "rewardtop7",
        "switch_margin": 1.6,
        "n_seeds": int(payload["n"]),
        "seed_wins": int(_small_scale_value(payload, "wins_vs_baseline", "wins")),
        "seed_losses": int(_small_scale_value(payload, "losses_vs_baseline", "losses")),
        "baseline_mean_reward": float(payload["baseline_mean_reward"]),
        "candidate_mean_reward": float(payload["candidate_mean_reward"]),
        "mean_delta_vs_baseline": float(
            _small_scale_value(payload, "mean_delta_vs_baseline", "mean_delta")
        ),
        "median_delta_vs_baseline": float(
            _small_scale_value(payload, "median_delta_vs_baseline", "median_delta")
        ),
        "min_seed_delta_vs_baseline": float(
            _small_scale_value(payload, "min_delta_vs_baseline", "min_delta")
            if "min_delta_vs_baseline" in payload or "min_delta" in payload
            else min(seed_deltas)
        ),
        "max_seed_delta_vs_baseline": float(
            _small_scale_value(payload, "max_delta_vs_baseline", "max_delta")
            if "max_delta_vs_baseline" in payload or "max_delta" in payload
            else max(seed_deltas)
        ),
        "bootstrap_95ci_delta": [
            float(payload["bootstrap_95ci_delta"][0]),
            float(payload["bootstrap_95ci_delta"][1]),
        ],
        "seed_deltas": [
            {
                "seed": int(row["seed"]),
                "baseline_reward": float(row["baseline_reward"]),
                "candidate_reward": float(row["candidate_reward"]),
                "delta_vs_baseline": float(
                    row["delta_vs_baseline"]
                    if "delta_vs_baseline" in row
                    else row["total_reward_delta"]
                ),
            }
            for row in seed_rows
        ],
    }

def build_true_reward_guard_readiness_audit(
    *,
    primary_comparison_path: str | Path = DEFAULT_PRIMARY_COMPARISON,
    primary_stats_path: str | Path = DEFAULT_PRIMARY_STATS,
    small_scale_stats_path: str | Path = DEFAULT_SMALL_SCALE_STATS,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    primary_path = Path(primary_comparison_path)
    primary_stats_source = Path(primary_stats_path)
    small_path = Path(small_scale_stats_path)
    primary = _primary_guard_summary(_load_json(primary_path))
    primary_stats = _primary_paired_stats_summary(_load_json(primary_stats_source))
    small = _small_scale_guard_summary(_load_json(small_path))

    primary_supported = (
        primary["candidate_mean_reward"] > primary["baseline_mean_reward"]
        and primary["seed_wins"] == primary["n_seeds"]
        and primary["min_seed_delta_vs_baseline"] > 0.0
    )
    small_supported = (
        small["candidate_mean_reward"] > small["baseline_mean_reward"]
        and small["mean_delta_vs_baseline"] > 0.0
        and small["seed_wins"] > small["seed_losses"]
        and small["bootstrap_95ci_delta"][0] > 0.0
    )
    primary_stats_supported = (
        primary_stats["wins"] == primary_stats["n"]
        and primary_stats["losses"] == 0
        and primary_stats["min_delta"] > 0.0
        and primary_stats["bootstrap_95ci_delta"][0] > 0.0
    )

    return {
        "status": "source-derived true-reward guard readiness audit",
        "date": output_date,
        "source_boundary": {
            "reran_training": False,
            "reran_rollouts": False,
            "algorithm_redesign_performed": False,
            "source": "tracked JSON result artifacts only",
        },
        "source_provenance": {
            "primary_20x16_comparison": primary_path.as_posix(),
            "primary_20x16_paired_stats": primary_stats_source.as_posix(),
            "small_scale_10x12_stats": small_path.as_posix(),
        },
        "primary_guard": primary,
        "primary_paired_stats": primary_stats,
        "small_scale_guard": small,
        "claim_gates": {
            "primary_algorithm_candidate_supported": bool(primary_supported),
            "primary_paired_statistics_supported": bool(primary_stats_supported),
            "small_scale_consistency_supported": bool(small_supported),
            "setting_specific_margin_required": True,
            "universal_fixed_margin_supported": False,
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_cadastral_planning_supported": False,
            "final_submission_readiness_supported": False,
        },
        "allowed_language": [
            "source-derived true-reward guard readiness audit",
            "primary 20x16/top5 simplified rewardtop7 guard candidate",
            "setting-specific switch margin",
            "reward-only top7 simplification",
            "20-seed paired bootstrap CI lower above zero",
            "10x12/top4 20-seed positive descriptive support",
            "not final submission readiness",
        ],
        "blocked_language": [
            "universal fixed switch margin",
            "direct 50-state Bishan scale-up success",
            "robust Bishan-to-Dongxing transfer superiority",
            "deployment-ready cadastral planning",
            "final submission-ready",
        ],
    }


def true_reward_guard_readiness_markdown(audit: dict[str, Any]) -> str:
    primary = audit["primary_guard"]
    small = audit["small_scale_guard"]
    stats = audit["primary_paired_stats"]
    guard_stats = stats["candidate_guard_summary"]
    gates = audit["claim_gates"]
    lines = [
        "# Paper10 true-reward guard readiness audit",
        "",
        f"Date: {audit['date']}",
        "",
        "Status: source-derived true-reward guard readiness audit.",
        "",
        "No training, rollout, algorithm redesign, or post-hoc experiment rerun was performed.",
        "This is an algorithm-readiness evidence boundary, not final submission readiness.",
        "",
        "## Source Provenance",
        "",
        f"- Primary 20x16/top5 comparison: `{audit['source_provenance']['primary_20x16_comparison']}`",
        f"- Primary 20x16/top5 paired statistics: `{audit['source_provenance']['primary_20x16_paired_stats']}`",
        f"- Small-scale 10x12/top4 statistics: `{audit['source_provenance']['small_scale_10x12_stats']}`",
        "",
        "## Primary Guard Candidate",
        "",
        f"The current Paper10 primary algorithm candidate is `rewardtop7 margin=1.50` for Bishan 20x16/top5.",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| baseline mean reward | {primary['baseline_mean_reward']:.4f} |",
        f"| guard mean reward | {primary['candidate_mean_reward']:.4f} |",
        f"| mean delta vs baseline | {primary['mean_delta_vs_baseline']:.4f} |",
        f"| seed wins | {primary['seed_wins']} / {primary['n_seeds']} |",
        f"| min seed delta | {primary['min_seed_delta_vs_baseline']:.4f} |",
        f"| max seed delta | {primary['max_seed_delta_vs_baseline']:.4f} |",
        "",
        "## Primary Paired Statistics",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| paired seeds | {stats['n']} |",
        f"| wins / losses / ties | {stats['wins']} / {stats['losses']} / {stats['ties']} |",
        f"| mean delta | {stats['mean_delta']:.4f} |",
        f"| median delta | {stats['median_delta']:.4f} |",
        f"| bootstrap 95% CI lower | {stats['bootstrap_95ci_delta'][0]:.4f} |",
        f"| bootstrap 95% CI upper | {stats['bootstrap_95ci_delta'][1]:.4f} |",
        f"| switch rate | {guard_stats['switch_rate']:.4f} |",
        f"| selected true-reward regret mean | {guard_stats['selected_true_reward_regret_mean']:.4f} |",
        "",
        "## Rewardtop7 Simplification Boundary",
        "",
        "The primary guard is the simplified robust default: it audits the rollout-selected action plus model-reward top7 actions, not the extra blend-top7 path.",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| mean audited actions | {guard_stats['mean_audit_action_count']:.4f} |",
        f"| dual7x7 mean audited actions | {stats.get('dual7x7_guard_summary', {}).get('mean_audit_action_count', 0.0):.4f} |",
        f"| mean delta vs dual7x7 | {stats.get('mean_delta_vs_dual7x7', 0.0):.4f} |",
        f"| wins / losses / ties vs dual7x7 | {stats.get('wins_vs_dual7x7', 0)} / {stats.get('losses_vs_dual7x7', 0)} / {stats.get('ties_vs_dual7x7', 0)} |",
        "",
        "## Small-Scale Consistency Guard",
        "",
        f"The supporting small-scale guard is `rewardtop7 margin=1.60` for Bishan 10x12/top4.",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| baseline mean reward | {small['baseline_mean_reward']:.4f} |",
        f"| guard mean reward | {small['candidate_mean_reward']:.4f} |",
        f"| mean delta vs baseline | {small['mean_delta_vs_baseline']:.4f} |",
        f"| seed wins | {small['seed_wins']} / {small['n_seeds']} |",
        f"| seed losses | {small['seed_losses']} / {small['n_seeds']} |",
        f"| min seed delta | {small['min_seed_delta_vs_baseline']:.4f} |",
        f"| bootstrap 95% CI lower | {small['bootstrap_95ci_delta'][0]:.4f} |",
        "",
        "## Claim Gates",
        "",
        "| gate | status |",
        "|---|---|",
        f"| primary algorithm candidate supported | {gates['primary_algorithm_candidate_supported']} |",
        f"| primary paired statistics supported | {gates['primary_paired_statistics_supported']} |",
        f"| small-scale consistency supported | {gates['small_scale_consistency_supported']} |",
        f"| setting-specific margin required | {gates['setting_specific_margin_required']} |",
        f"| universal fixed margin supported | {gates['universal_fixed_margin_supported']} |",
        f"| direct 50-state scale-up supported | {gates['direct_50state_scaleup_supported']} |",
        f"| robust transfer superiority supported | {gates['robust_transfer_superiority_supported']} |",
        f"| deployment-ready cadastral planning supported | {gates['deployment_ready_cadastral_planning_supported']} |",
        "",
        "## Interpretation Boundary",
        "",
        "Use this audit to treat the 2026-07-07 reward-only top7 true-reward margin guard as the current simplified robust default for Paper10 Bishan experiments.",
        "The evidence supports a setting-specific guard, not a universal margin or a general scale-up result.",
        "The 10x12/top4 extension is positive descriptive support with reported seed losses, not every-seed dominance.",
        "",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not treat this as final submission readiness.",
        "",
    ]
    return "\n".join(lines)


def write_true_reward_guard_readiness_audit(
    *,
    primary_comparison_path: str | Path = DEFAULT_PRIMARY_COMPARISON,
    primary_stats_path: str | Path = DEFAULT_PRIMARY_STATS,
    small_scale_stats_path: str | Path = DEFAULT_SMALL_SCALE_STATS,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    audit = build_true_reward_guard_readiness_audit(
        primary_comparison_path=primary_comparison_path,
        primary_stats_path=primary_stats_path,
        small_scale_stats_path=small_scale_stats_path,
        output_date=output_date,
    )
    output_json_path = Path(output_json)
    output_md_path = Path(output_md)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(audit, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path.write_text(
        true_reward_guard_readiness_markdown(audit),
        encoding="utf-8",
    )
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 true-reward guard readiness audit."
    )
    parser.add_argument("--primary-comparison", default=str(DEFAULT_PRIMARY_COMPARISON))
    parser.add_argument("--primary-stats", default=str(DEFAULT_PRIMARY_STATS))
    parser.add_argument("--small-scale-stats", default=str(DEFAULT_SMALL_SCALE_STATS))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-08")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = write_true_reward_guard_readiness_audit(
        primary_comparison_path=args.primary_comparison,
        primary_stats_path=args.primary_stats,
        small_scale_stats_path=args.small_scale_stats,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
