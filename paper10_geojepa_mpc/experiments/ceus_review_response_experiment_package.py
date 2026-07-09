"""CEUS review-response algorithm and experiment package for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
DEFAULT_BASELINE_HARDENING_JSON = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json"
)
DEFAULT_MECHANISM_AUDIT_JSON = (
    RESULTS / "e0_paper10_ceus_mechanism_claim_audit_2026-06-27.json"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_ceus_review_response_experiment_package_2026-07-09.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_ceus_review_response_experiment_package_2026-07-09.md"
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _as_float(value: Any) -> float:
    return float(value)


def _relative_source(path: Path) -> str:
    return path.as_posix()


def _primary_algorithm_evidence(guard: dict[str, Any]) -> dict[str, Any]:
    primary = guard["primary_guard"]
    stats = guard["primary_paired_stats"]
    guard_stats = stats["candidate_guard_summary"]
    dual_stats = stats.get("dual7x7_guard_summary", {})
    mean_audit_count = _as_float(guard_stats["mean_audit_action_count"])
    dual_audit_count = _as_float(dual_stats.get("mean_audit_action_count", 0.0))
    return {
        "setting": primary["setting"],
        "algorithm": primary["algorithm"],
        "audit_set": primary["audit_set"],
        "switch_margin": _as_float(primary["switch_margin"]),
        "n_seeds": int(primary["n_seeds"]),
        "seed_wins": int(primary["seed_wins"]),
        "seed_losses": int(primary["seed_losses"]),
        "baseline_name": primary["baseline_name"],
        "guard_name": primary["candidate_name"],
        "baseline_mean_reward": _as_float(primary["baseline_mean_reward"]),
        "guard_mean_reward": _as_float(primary["candidate_mean_reward"]),
        "mean_delta_vs_baseline": _as_float(stats["mean_delta"]),
        "min_seed_delta_vs_baseline": _as_float(primary["min_seed_delta_vs_baseline"]),
        "max_seed_delta_vs_baseline": _as_float(primary["max_seed_delta_vs_baseline"]),
        "bootstrap_95ci_delta": [
            _as_float(stats["bootstrap_95ci_delta"][0]),
            _as_float(stats["bootstrap_95ci_delta"][1]),
        ],
        "switch_rate": _as_float(guard_stats["switch_rate"]),
        "switches": int(guard_stats["switches"]),
        "audited_states": int(guard_stats["audited_states"]),
        "mean_audit_action_count": mean_audit_count,
        "dual7x7_mean_audit_action_count": dual_audit_count,
        "audit_action_count_delta_vs_dual7x7": mean_audit_count - dual_audit_count,
        "selected_true_reward_regret_mean": _as_float(
            guard_stats["selected_true_reward_regret_mean"]
        ),
        "algorithmic_change_relative_to_clean_draft": (
            "promote the tracked true-reward margin guard over the old "
            "5-seed value-filter anchor as the primary Bishan algorithm evidence"
        ),
    }


def _legacy_anchor(baseline: dict[str, Any]) -> dict[str, Any]:
    summary = baseline["paired_reward_summary"]
    sign_test = summary["sign_test"]
    return {
        "role": "historical_descriptive_anchor_not_primary",
        "setting": "bishan_20x16_top5",
        "baseline_mean_reward": _as_float(summary["baseline_mean_reward"]),
        "candidate_mean_reward": _as_float(summary["candidate_mean_reward"]),
        "paired_mean_delta": _as_float(summary["paired_mean_delta"]),
        "n_seeds": int(summary["n_seeds"]),
        "candidate_win_count": int(summary["candidate_win_count"]),
        "candidate_loss_count": int(summary["candidate_loss_count"]),
        "sign_test_p_value": _as_float(sign_test["p_value"]),
        "primary_claim_allowed": False,
        "allowed_role": "historical descriptive anchor and comparator context",
    }


def _secondary_metric_assessment(guard: dict[str, Any]) -> dict[str, Any]:
    deltas = guard["primary_guard"]["secondary_metric_deltas"]
    metric_direction = {
        "slope_change_pct_mean": "higher_is_better",
        "cont_change_mean": "higher_is_better",
        "baimu_area_change_ha_mean": "higher_is_better",
    }
    aligned = [key for key, value in deltas.items() if key in metric_direction and value > 0.0]
    tradeoffs = [
        key for key, value in deltas.items() if key in metric_direction and value < 0.0
    ]
    neutral = [
        key for key, value in deltas.items() if key in metric_direction and value == 0.0
    ]
    return {
        "classification": "reward_primary_secondary_mixed",
        "deltas_vs_value_filter_baseline": {
            key: _as_float(value)
            for key, value in deltas.items()
            if key in metric_direction
        },
        "metric_direction": metric_direction,
        "aligned_metrics": aligned,
        "tradeoff_metrics": tradeoffs,
        "neutral_metrics": neutral,
        "interpretation": (
            "The guard is reward-positive under the confirmatory metric, but "
            "secondary planning metrics are not uniformly aligned."
        ),
    }


def _mechanism_boundary(
    baseline: dict[str, Any],
    mechanism: dict[str, Any],
) -> dict[str, Any]:
    baseline_gates = baseline["claim_gates"]
    claims = mechanism["claims"]
    return {
        "monitor_gate_direct_reward_gain_supported": bool(
            baseline_gates["monitor_gate_direct_reward_gain_supported"]
        ),
        "monitor_gate_evidence_control_supported": bool(
            baseline_gates["monitor_gate_evidence_control_supported"]
        ),
        "executable_mask_necessity_supported": bool(
            baseline_gates["executable_mask_necessity_supported"]
        ),
        "ungated_reward_delta_vs_full": _as_float(
            baseline["secondary_metric_tradeoffs"]["ungated_reward_delta_vs_full"]
        ),
        "no_mask_zero_swap_steps": _as_float(
            baseline["secondary_metric_tradeoffs"]["no_mask_zero_swap_steps"]
        ),
        "no_mask_negative_zero_swap_steps": _as_float(
            baseline["secondary_metric_tradeoffs"][
                "no_mask_negative_zero_swap_steps"
            ]
        ),
        "direct_monitor_gate_reward_gain_status": claims[
            "direct_monitor_gate_reward_gain"
        ]["status"],
        "executable_mask_status": claims["executable_mask_necessity"]["status"],
        "allowed_monitor_language": "monitor gate as evidence control",
    }


def build_ceus_review_response_experiment_package(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    baseline_hardening_json: str | Path = DEFAULT_BASELINE_HARDENING_JSON,
    mechanism_audit_json: str | Path = DEFAULT_MECHANISM_AUDIT_JSON,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    guard_path = Path(true_reward_guard_json)
    baseline_path = Path(baseline_hardening_json)
    mechanism_path = Path(mechanism_audit_json)
    guard = _load_json(guard_path)
    baseline = _load_json(baseline_path)
    mechanism = _load_json(mechanism_path)

    primary = _primary_algorithm_evidence(guard)
    legacy = _legacy_anchor(baseline)
    secondary = _secondary_metric_assessment(guard)
    mechanism_boundary = _mechanism_boundary(baseline, mechanism)
    ci = primary["bootstrap_95ci_delta"]

    return {
        "date": output_date,
        "status": "ceus_review_response_algorithm_experiment_package",
        "source_boundary": {
            "source": "tracked Paper10 guard, baseline, and mechanism artifacts only",
            "reran_training": False,
            "reran_rollouts": False,
            "algorithm_reselection_from_tracked_evidence": True,
            "reviewer_driven_claim_reclassification": True,
        },
        "source_files": {
            "true_reward_guard_json": _relative_source(guard_path),
            "baseline_hardening_json": _relative_source(baseline_path),
            "mechanism_audit_json": _relative_source(mechanism_path),
        },
        "primary_algorithm_evidence": primary,
        "legacy_value_filter_anchor": legacy,
        "secondary_metric_assessment": secondary,
        "mechanism_boundary": mechanism_boundary,
        "claim_gates": {
            "primary_guard_promoted_to_main_algorithm_candidate": True,
            "primary_guard_confirmatory_20seed_supported": (
                primary["n_seeds"] == 20
                and primary["seed_wins"] == 20
                and primary["seed_losses"] == 0
                and primary["mean_delta_vs_baseline"] > 0.0
                and primary["min_seed_delta_vs_baseline"] > 0.0
                and ci[0] > 0.0
            ),
            "old_5seed_value_filter_primary_claim_blocked": (
                legacy["n_seeds"] == 5
                and legacy["candidate_win_count"] < legacy["n_seeds"]
                and not legacy["primary_claim_allowed"]
            ),
            "bootstrap_ci_lower_positive": ci[0] > 0.0,
            "all_primary_seeds_improve": primary["seed_wins"] == primary["n_seeds"],
            "secondary_metrics_uniformly_aligned": False,
            "monitor_gate_online_reward_gain_supported": False,
            "monitor_gate_evidence_control_supported": mechanism_boundary[
                "monitor_gate_evidence_control_supported"
            ],
            "executable_mask_necessity_supported": mechanism_boundary[
                "executable_mask_necessity_supported"
            ],
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_cadastral_planning_supported": False,
            "submission_story_should_use_guard_as_primary": True,
        },
        "manuscript_sync_actions": [
            "Make the 20-seed rewardtop7 true-reward margin guard the primary Bishan algorithm result.",
            "Move the 5-seed value-filter result to historical descriptive anchor and comparator context.",
            "Report secondary planning metrics as mixed rather than uniformly improved.",
            "Frame the monitor gate as evidence control, not direct online reward gain.",
        ],
        "blocked_language": [
            "the 5-seed value-filter anchor is the strongest Paper10 result",
            "uniform secondary-metric improvement",
            "direct monitor-gate online reward gain",
            "direct 50-state Bishan scale-up success",
            "robust Bishan-to-Dongxing transfer superiority",
            "deployment-ready cadastral planning",
        ],
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def ceus_review_response_experiment_package_markdown(payload: dict[str, Any]) -> str:
    primary = payload["primary_algorithm_evidence"]
    legacy = payload["legacy_value_filter_anchor"]
    secondary = payload["secondary_metric_assessment"]
    mechanism = payload["mechanism_boundary"]
    gates = payload["claim_gates"]
    ci = primary["bootstrap_95ci_delta"]
    lines = [
        "# Paper10 CEUS review-response algorithm experiment package",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: ceus_review_response_algorithm_experiment_package",
        "",
        (
            "This package responds to CEUS-style review risk by reclassifying "
            "the tracked 20-seed true-reward margin guard as the primary "
            "algorithm evidence."
        ),
        "",
        "## Source Boundary",
        "",
        "No training or rollout was rerun for this package.",
        "The package is not text-only: it changes the manuscript-facing algorithm and experiment hierarchy using tracked confirmatory guard artifacts.",
        "",
        "## Primary Algorithm Evidence",
        "",
        (
            "Primary algorithm candidate: `rewardtop7 margin=1.50` "
            "true-reward margin guard for Bishan 20x16/top5."
        ),
        "",
        "| metric | value |",
        "|---|---:|",
        f"| baseline mean reward | {_fmt(primary['baseline_mean_reward'])} |",
        f"| guard mean reward | {_fmt(primary['guard_mean_reward'])} |",
        f"| mean delta vs baseline | {_fmt(primary['mean_delta_vs_baseline'])} |",
        f"| seed wins / seeds | {primary['seed_wins']} / {primary['n_seeds']} |",
        f"| seed losses / seeds | {primary['seed_losses']} / {primary['n_seeds']} |",
        f"| paired seeds | {primary['n_seeds']} |",
        f"| min seed delta | {_fmt(primary['min_seed_delta_vs_baseline'])} |",
        f"| bootstrap 95% CI lower | {_fmt(ci[0])} |",
        f"| bootstrap 95% CI upper | {_fmt(ci[1])} |",
        f"| switch rate | {_fmt(primary['switch_rate'])} |",
        f"| switches / audited states | {primary['switches']} / {primary['audited_states']} |",
        f"| mean audited actions | {_fmt(primary['mean_audit_action_count'])} |",
        f"| dual7x7 mean audited actions | {_fmt(primary['dual7x7_mean_audit_action_count'])} |",
        "",
        "## Legacy Value-Filter Anchor",
        "",
        (
            "The 5-seed value-filter result is retained as a historical "
            "descriptive anchor, not the primary claim."
        ),
        "",
        "| metric | value |",
        "|---|---:|",
        f"| baseline mean reward | {_fmt(legacy['baseline_mean_reward'])} |",
        f"| value-filter mean reward | {_fmt(legacy['candidate_mean_reward'])} |",
        f"| paired mean delta | {_fmt(legacy['paired_mean_delta'])} |",
        f"| wins / seeds | {legacy['candidate_win_count']} / {legacy['n_seeds']} |",
        f"| losses / seeds | {legacy['candidate_loss_count']} / {legacy['n_seeds']} |",
        f"| diagnostic sign-test p=1.0000 | {_fmt(legacy['sign_test_p_value'])} |",
        "",
        "## Secondary Metrics",
        "",
        f"Classification: `{secondary['classification']}`.",
        "",
        "| metric | delta vs value-filter baseline | direction |",
        "|---|---:|---|",
    ]
    for metric, delta in secondary["deltas_vs_value_filter_baseline"].items():
        if metric in secondary["aligned_metrics"]:
            direction = "aligned"
        elif metric in secondary["tradeoff_metrics"]:
            direction = "tradeoff"
        else:
            direction = "neutral"
        lines.append(f"| {metric} | {_fmt(delta)} | {direction} |")

    lines.extend(
        [
            "",
            "## Mechanism Boundary",
            "",
            (
                "The monitor gate remains framed as monitor gate as evidence "
                "control, not as a separately proven online reward-gain mechanism."
            ),
            "",
            "| gate | value |",
            "|---|---|",
            (
                "| monitor gate direct reward gain supported | "
                f"{mechanism['monitor_gate_direct_reward_gain_supported']} |"
            ),
            (
                "| monitor gate evidence control supported | "
                f"{mechanism['monitor_gate_evidence_control_supported']} |"
            ),
            (
                "| executable mask necessity supported | "
                f"{mechanism['executable_mask_necessity_supported']} |"
            ),
            (
                "| no-mask negative zero-swap steps | "
                f"{_fmt(mechanism['no_mask_negative_zero_swap_steps'])} |"
            ),
            "",
            "## Claim Gates",
            "",
            "| gate | status |",
            "|---|---|",
        ]
    )
    for key, value in gates.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Manuscript Sync Actions",
            "",
        ]
    )
    for action in payload["manuscript_sync_actions"]:
        lines.append(f"- {action}")

    lines.extend(
        [
            "",
            "## Claim Locks",
            "",
            "Do not claim uniform secondary-metric improvement.",
            "Do not claim direct monitor-gate online reward gain.",
            "Do not claim direct 50-state Bishan scale-up success.",
            "Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "Do not claim deployment-ready cadastral planning.",
            "",
        ]
    )
    return "\n".join(lines)


def write_ceus_review_response_experiment_package(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    baseline_hardening_json: str | Path = DEFAULT_BASELINE_HARDENING_JSON,
    mechanism_audit_json: str | Path = DEFAULT_MECHANISM_AUDIT_JSON,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    payload = build_ceus_review_response_experiment_package(
        true_reward_guard_json=true_reward_guard_json,
        baseline_hardening_json=baseline_hardening_json,
        mechanism_audit_json=mechanism_audit_json,
        output_date=output_date,
    )
    output_json_path = Path(output_json)
    output_md_path = Path(output_md)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path.write_text(
        ceus_review_response_experiment_package_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 CEUS review-response experiment package."
    )
    parser.add_argument("--true-reward-guard-json", default=DEFAULT_TRUE_REWARD_GUARD_JSON)
    parser.add_argument("--baseline-hardening-json", default=DEFAULT_BASELINE_HARDENING_JSON)
    parser.add_argument("--mechanism-audit-json", default=DEFAULT_MECHANISM_AUDIT_JSON)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default="2026-07-09")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_ceus_review_response_experiment_package(
        true_reward_guard_json=args.true_reward_guard_json,
        baseline_hardening_json=args.baseline_hardening_json,
        mechanism_audit_json=args.mechanism_audit_json,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
