from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _condition(packet: dict[str, Any], name: str) -> dict[str, Any]:
    conditions = packet.get("condition_comparisons", {})
    if name not in conditions:
        raise ValueError(f"missing condition comparison: {name}")
    return conditions[name]


def _delta(
    left: dict[str, Any],
    right: dict[str, Any],
    key: str,
) -> float:
    return _as_float(left.get(key)) - _as_float(right.get(key))


def _status_for_positive_delta(delta: float, tolerance: float) -> str:
    if delta > tolerance:
        return "descriptive_support"
    if abs(delta) <= tolerance:
        return "not_supported_equal_reward"
    return "not_supported_negative_delta"


def _secondary_metric_tradeoffs(
    full: dict[str, Any],
    comparator: dict[str, Any],
    *,
    tolerance: float,
) -> dict[str, Any]:
    metric_specs = {
        "slope_change_pct_mean": "higher_is_better",
        "cont_change_mean": "higher_is_better",
        "baimu_area_change_ha_mean": "higher_is_better",
    }
    deltas = {
        key: _delta(full, comparator, key)
        for key in metric_specs
    }
    aligned = [
        key for key, value in deltas.items()
        if value > tolerance
    ]
    neutral = [
        key for key, value in deltas.items()
        if abs(value) <= tolerance
    ]
    tradeoffs = [
        key for key, value in deltas.items()
        if value < -tolerance
    ]
    if aligned and tradeoffs:
        classification = "mixed"
    elif tradeoffs:
        classification = "tradeoff_only"
    elif aligned:
        classification = "aligned_positive"
    else:
        classification = "neutral"
    return {
        "classification": classification,
        "deltas_vs_matched_paper9": deltas,
        "aligned_metrics": aligned,
        "neutral_metrics": neutral,
        "tradeoff_metrics": tradeoffs,
        "metric_direction": metric_specs,
    }


def audit_mechanism_claims(
    packet: dict[str, Any],
    *,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    full = _condition(packet, "full_gated_masked")
    matched_paper9 = _condition(packet, "heuristic_paper9_masked")
    no_mask = _condition(packet, "no_mask")
    ungated = _condition(packet, "ungated_top4")

    reward_delta_vs_paper9 = _delta(full, matched_paper9, "mean_reward")
    std_delta_vs_paper9 = _delta(full, matched_paper9, "std_sample")
    reward_delta_vs_ungated = _delta(full, ungated, "mean_reward")
    no_mask_zero_swaps = _as_float(no_mask.get("zero_swap_steps_sum"))
    no_mask_negative_zero_swaps = _as_float(no_mask.get("negative_zero_swap_steps_sum"))
    best_value_filter = packet.get("stage3_boundary", {}).get("best_value_filter", {})
    stage3_delta = _as_float(best_value_filter.get("delta_vs_paper9"))

    reward_stability_status = (
        "descriptive_support"
        if reward_delta_vs_paper9 > tolerance and std_delta_vs_paper9 < -tolerance
        else "not_supported"
    )
    executable_mask_status = (
        "supported"
        if no_mask_zero_swaps > tolerance or no_mask_negative_zero_swaps > tolerance
        else "not_supported"
    )
    ungated_status = _status_for_positive_delta(
        reward_delta_vs_ungated,
        tolerance=tolerance,
    )
    stage3_status = (
        "descriptive_support"
        if stage3_delta > tolerance
        else "not_supported_boundary"
    )

    return {
        "status": "ceus mechanism-claim audit",
        "audit_boundary": (
            "Source-derived claim audit only; not a new rollout, training run, "
            "or inferential statistics test."
        ),
        "baseline_policy": {
            "default_comparator": "matched_paper9_masked",
            "default_comparator_condition": "heuristic_paper9_masked",
            "pairwise_only_role": (
                "diagnostic/model-initialization evidence only; not the default "
                "performance comparator"
            ),
        },
        "claims": {
            "matched_paper9_reward_stability": {
                "status": reward_stability_status,
                "reward_delta": reward_delta_vs_paper9,
                "std_delta": std_delta_vs_paper9,
                "allowed_language": (
                    "descriptive reward and variance improvement versus the matched "
                    "Paper9 masked comparator"
                ),
            },
            "executable_mask_necessity": {
                "status": executable_mask_status,
                "zero_swap_steps": no_mask_zero_swaps,
                "negative_zero_swap_steps": no_mask_negative_zero_swaps,
                "allowed_language": (
                    "the executable mask is necessary for executable rollouts"
                ),
            },
            "value_filter_superiority_vs_ungated": {
                "status": ungated_status,
                "reward_delta": reward_delta_vs_ungated,
                "forbidden_language": (
                    "value filtering alone improves reward over the ungated top-4 "
                    "condition"
                ),
            },
            "direct_monitor_gate_reward_gain": {
                "status": ungated_status,
                "reward_delta": reward_delta_vs_ungated,
                "forbidden_language": (
                    "the monitor gate directly caused an online reward gain in the "
                    "matched top-4/top-5 ablation"
                ),
            },
            "stage3_50state_positive_scaleup": {
                "status": stage3_status,
                "delta_vs_paper9": stage3_delta,
                "forbidden_language": (
                    "the 50-state Stage 3 run demonstrates positive scale-up over "
                    "the matched Paper9 baseline"
                ),
            },
        },
        "secondary_metric_tradeoffs": _secondary_metric_tradeoffs(
            full,
            matched_paper9,
            tolerance=tolerance,
        ),
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def mechanism_claim_audit_report(audit: dict[str, Any]) -> str:
    claims = audit["claims"]
    tradeoffs = audit["secondary_metric_tradeoffs"]
    lines = [
        "# CEUS mechanism-claim audit",
        "",
        "Status: source-derived CEUS mechanism-claim audit.",
        "",
        audit["audit_boundary"],
        "",
        "## Baseline Policy",
        "",
        "- Default performance comparator: matched Paper9 masked baseline.",
        "- pairwise-only evidence is retained as diagnostic/model-initialization evidence, not as the default performance comparator.",
        "",
        "## Claim Decisions",
        "",
        "| claim | status | key delta/count | interpretation |",
        "|---|---|---:|---|",
    ]
    lines.append(
        "| matched_paper9_reward_stability | {status} | {delta} | reward/stability comparison is descriptive only |".format(
            status=claims["matched_paper9_reward_stability"]["status"],
            delta=_fmt(claims["matched_paper9_reward_stability"]["reward_delta"]),
        )
    )
    lines.append(
        "| executable_mask_necessity | {status} | {count} | no-mask failures support mask necessity, not full value-filter superiority |".format(
            status=claims["executable_mask_necessity"]["status"],
            count=_fmt(claims["executable_mask_necessity"]["negative_zero_swap_steps"]),
        )
    )
    lines.append(
        "| value_filter_superiority_vs_ungated | {status} | {delta} | equal reward blocks a standalone value-filter superiority claim |".format(
            status=claims["value_filter_superiority_vs_ungated"]["status"],
            delta=_fmt(claims["value_filter_superiority_vs_ungated"]["reward_delta"]),
        )
    )
    lines.append(
        "| direct_monitor_gate_reward_gain | {status} | {delta} | monitor gate should be framed as evidence control, not direct online reward gain |".format(
            status=claims["direct_monitor_gate_reward_gain"]["status"],
            delta=_fmt(claims["direct_monitor_gate_reward_gain"]["reward_delta"]),
        )
    )
    lines.append(
        "| stage3_50state_positive_scaleup | {status} | {delta} | 50-state rows remain boundary evidence |".format(
            status=claims["stage3_50state_positive_scaleup"]["status"],
            delta=_fmt(claims["stage3_50state_positive_scaleup"]["delta_vs_paper9"]),
        )
    )

    lines.extend(
        [
            "",
            "## Secondary Metric Tradeoffs",
            "",
            f"Classification: `{tradeoffs['classification']}`",
            "",
            "| metric | delta vs matched Paper9 | direction |",
            "|---|---:|---|",
        ]
    )
    for metric, delta in tradeoffs["deltas_vs_matched_paper9"].items():
        direction = (
            "aligned"
            if metric in tradeoffs["aligned_metrics"]
            else "tradeoff"
            if metric in tradeoffs["tradeoff_metrics"]
            else "neutral"
        )
        lines.append(f"| {metric} | {_fmt(delta)} | {direction} |")

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- Use this audit to police CEUS wording before manuscript conversion.",
            "- It does not replace new multi-region validation, real-data rollout experiments, or a predefined inferential analysis plan.",
            "- It blocks claims that the current ablation evidence does not support.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_mechanism_claim_audit(
    *,
    packet_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> dict[str, Any]:
    packet = json.loads(Path(packet_json).read_text(encoding="utf-8"))
    audit = audit_mechanism_claims(packet)
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(audit, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(mechanism_claim_audit_report(audit), encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Paper10 mechanism claims against CEUS reviewer boundaries."
    )
    parser.add_argument("--packet-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = write_mechanism_claim_audit(
        packet_json=args.packet_json,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
