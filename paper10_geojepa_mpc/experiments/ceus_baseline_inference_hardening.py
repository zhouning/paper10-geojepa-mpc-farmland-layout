from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any


DATE = "2026-07-06"
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
DEFAULT_MATCHED_5SEED_JSON = (
    RESULTS / "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
)
DEFAULT_MECHANISM_PACKET_JSON = (
    RESULTS / "e0_paper10_mechanism_ablation_packet_2026-06-20.json"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md"
)


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _sample_std(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def _relative_to_root(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def two_sided_sign_test_pvalue(wins: int, losses: int) -> float:
    n_trials = wins + losses
    if n_trials == 0:
        return 1.0
    lower_tail = min(wins, losses)
    tail_probability = sum(comb(n_trials, k) for k in range(lower_tail + 1)) / (
        2**n_trials
    )
    return min(1.0, 2.0 * tail_probability)


def paired_reward_summary(matched_5seed: dict[str, Any]) -> dict[str, Any]:
    paired = matched_5seed["paired_comparison"]
    seed_rows = []
    deltas = []
    wins = 0
    losses = 0
    ties = 0

    for row in paired["per_seed"]:
        delta = _as_float(row["total_reward_delta_candidate_minus_baseline"])
        if delta > 0.0:
            outcome = "win"
            wins += 1
        elif delta < 0.0:
            outcome = "loss"
            losses += 1
        else:
            outcome = "tie"
            ties += 1
        deltas.append(delta)
        seed_rows.append(
            {
                "seed": row["seed"],
                "baseline_total_reward": _as_float(row["baseline_total_reward"]),
                "candidate_total_reward": _as_float(row["candidate_total_reward"]),
                "delta": delta,
                "outcome": outcome,
                "final_metric_deltas": row.get("final_metric_deltas", {}),
            }
        )

    baseline_aggregate = matched_5seed["policies"]["baseline"]["aggregate"]
    candidate_aggregate = matched_5seed["policies"]["candidate"]["aggregate"]
    baseline_mean = _as_float(baseline_aggregate["total_reward_mean"])
    candidate_mean = _as_float(candidate_aggregate["total_reward_mean"])
    sign_test_p = two_sided_sign_test_pvalue(wins, losses)

    return {
        "n_seeds": len(seed_rows),
        "seed_rows": seed_rows,
        "baseline_mean_reward": baseline_mean,
        "candidate_mean_reward": candidate_mean,
        "baseline_sample_std": _as_float(
            baseline_aggregate.get("total_reward_std_sample")
        ),
        "candidate_sample_std": _as_float(
            candidate_aggregate.get("total_reward_std_sample")
        ),
        "candidate_win_count": wins,
        "candidate_loss_count": losses,
        "tie_count": ties,
        "paired_mean_delta": mean(deltas) if deltas else 0.0,
        "paired_median_delta": median(deltas) if deltas else 0.0,
        "paired_std_delta": _sample_std(deltas),
        "paired_min_delta": min(deltas) if deltas else 0.0,
        "paired_max_delta": max(deltas) if deltas else 0.0,
        "all_seeds_improve": wins == len(seed_rows) and bool(seed_rows),
        "uniform_superiority_supported": wins == len(seed_rows) and bool(seed_rows),
        "inferential_superiority_supported": False,
        "descriptive_mean_reward_anchor_supported": candidate_mean > baseline_mean,
        "sign_test": {
            "wins": wins,
            "losses": losses,
            "ties_excluded": ties,
            "p_value": sign_test_p,
            "classification": "diagnostic_only",
            "interpretation": (
                "Small-sample diagnostic only; current CEUS wording remains "
                "descriptive because no inferential plan was predefined."
            ),
        },
    }


def _condition(packet: dict[str, Any], name: str) -> dict[str, Any]:
    conditions = packet.get("condition_comparisons", {})
    if name not in conditions:
        raise ValueError(f"missing condition comparison: {name}")
    return conditions[name]


def _delta(left: dict[str, Any], right: dict[str, Any], key: str) -> float:
    return _as_float(left.get(key)) - _as_float(right.get(key))


def classify_secondary_tradeoffs(mechanism_packet: dict[str, Any]) -> dict[str, Any]:
    full = _condition(mechanism_packet, "full_gated_masked")
    matched_paper9 = _condition(mechanism_packet, "heuristic_paper9_masked")
    no_mask = _condition(mechanism_packet, "no_mask")
    ungated = _condition(mechanism_packet, "ungated_top4")
    metric_deltas = {
        "slope_change_pct_mean": _delta(full, matched_paper9, "slope_change_pct_mean"),
        "cont_change_mean": _delta(full, matched_paper9, "cont_change_mean"),
        "baimu_area_change_ha_mean": _delta(
            full,
            matched_paper9,
            "baimu_area_change_ha_mean",
        ),
    }
    aligned = [key for key, value in metric_deltas.items() if value > 0.0]
    tradeoffs = [key for key, value in metric_deltas.items() if value < 0.0]
    neutral = [key for key, value in metric_deltas.items() if value == 0.0]
    reward_delta = _delta(full, matched_paper9, "mean_reward")
    std_delta = _delta(full, matched_paper9, "std_sample")
    no_mask_negative_zero_swaps = _as_float(no_mask.get("negative_zero_swap_steps_sum"))
    no_mask_zero_swaps = _as_float(no_mask.get("zero_swap_steps_sum"))
    ungated_reward_delta = _delta(ungated, full, "mean_reward")

    if reward_delta > 0.0 and tradeoffs:
        classification = "reward_descriptive_secondary_mixed"
    elif reward_delta > 0.0:
        classification = "reward_descriptive_secondary_aligned"
    else:
        classification = "not_supported"

    return {
        "classification": classification,
        "reward_delta_vs_matched_paper9": reward_delta,
        "std_delta_vs_matched_paper9": std_delta,
        "deltas_vs_matched_paper9": metric_deltas,
        "aligned_metrics": aligned,
        "tradeoff_metrics": tradeoffs,
        "neutral_metrics": neutral,
        "metric_direction": {
            "slope_change_pct_mean": "higher_is_better",
            "cont_change_mean": "higher_is_better",
            "baimu_area_change_ha_mean": "higher_is_better",
        },
        "no_mask_zero_swap_steps": no_mask_zero_swaps,
        "no_mask_negative_zero_swap_steps": no_mask_negative_zero_swaps,
        "ungated_reward_delta_vs_full": ungated_reward_delta,
        "executable_mask_necessity_supported": no_mask_negative_zero_swaps > 0.0,
        "monitor_gate_direct_reward_gain_supported": ungated_reward_delta > 0.0,
    }


def build_baseline_hardening_audit(
    *,
    matched_5seed: dict[str, Any],
    mechanism_packet: dict[str, Any],
    matched_5seed_source: str,
    mechanism_packet_source: str,
    date: str = DATE,
) -> dict[str, Any]:
    summary = paired_reward_summary(matched_5seed)
    tradeoffs = classify_secondary_tradeoffs(mechanism_packet)
    return {
        "date": date,
        "status": "source-derived CEUS baseline and inference hardening audit",
        "source_boundary": {
            "source": "tracked JSON audit artifacts only",
            "reran_training": False,
            "reran_rollouts": False,
            "post_hoc_tuning_allowed": False,
            "algorithm_redesign_performed": False,
        },
        "source_provenance": {
            "matched_5seed_audit": matched_5seed_source,
            "mechanism_ablation_packet": mechanism_packet_source,
        },
        "paired_reward_summary": summary,
        "secondary_metric_tradeoffs": tradeoffs,
        "claim_gates": {
            "descriptive_mean_reward_anchor_supported": summary[
                "descriptive_mean_reward_anchor_supported"
            ],
            "mixed_seedwise_outcome_required": not summary["all_seeds_improve"],
            "uniform_superiority_supported": False,
            "inferential_superiority_supported": False,
            "executable_mask_necessity_supported": tradeoffs[
                "executable_mask_necessity_supported"
            ],
            "monitor_gate_direct_reward_gain_supported": False,
            "monitor_gate_evidence_control_supported": True,
            "stage3_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "irregular_cadastral_deployment_supported": False,
        },
        "allowed_language": [
            "descriptive matched 5-seed reward anchor",
            "mixed seed-wise outcome",
            "diagnostic-only two-sided sign test",
            "executable-mask necessity",
            "monitor gate as evidence control",
            "Stage 3 boundary evidence",
            "Dongxing/Neijiang calibration evidence",
        ],
        "blocked_language": [
            "uniform superiority",
            "inferential superiority",
            "direct 50-state Bishan scale-up success",
            "robust Bishan-to-Dongxing transfer superiority",
            "deployment-ready irregular cadastral planning",
        ],
    }


def hardening_markdown_report(audit: dict[str, Any]) -> str:
    summary = audit["paired_reward_summary"]
    tradeoffs = audit["secondary_metric_tradeoffs"]
    gates = audit["claim_gates"]
    lines = [
        "# Paper10 CEUS baseline and inference hardening audit",
        "",
        f"Date: {audit['date']}",
        "",
        "Status: source-derived CEUS baseline and inference hardening audit.",
        "",
        "No training, rollout, algorithm redesign, or post-hoc tuning was performed.",
        "",
        "## Source Provenance",
        "",
        f"- Matched 5-seed audit: `{audit['source_provenance']['matched_5seed_audit']}`",
        f"- Mechanism ablation packet: `{audit['source_provenance']['mechanism_ablation_packet']}`",
        "",
        "## Paired Reward Boundary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| matched seeds | {summary['n_seeds']} |",
        f"| baseline mean reward | {_fmt(summary['baseline_mean_reward'])} |",
        f"| value-filter mean reward | {_fmt(summary['candidate_mean_reward'])} |",
        f"| paired mean delta | {_fmt(summary['paired_mean_delta'])} |",
        f"| paired median delta | {_fmt(summary['paired_median_delta'])} |",
        f"| paired min delta | {_fmt(summary['paired_min_delta'])} |",
        f"| paired max delta | {_fmt(summary['paired_max_delta'])} |",
        f"| candidate wins | {summary['candidate_win_count']} |",
        f"| candidate losses | {summary['candidate_loss_count']} |",
        f"| ties | {summary['tie_count']} |",
        f"| diagnostic sign-test p | {_fmt(summary['sign_test']['p_value'])} |",
        "",
        f"Sign-test classification: `{summary['sign_test']['classification']}`.",
        "",
        "This is a mixed seed-wise outcome. The descriptive mean reward anchor is supported for Bishan 20x16/top5, but uniform superiority is not supported and inferential superiority is not supported.",
        "",
        "## Seed-Level Rows",
        "",
        "| seed | baseline reward | value-filter reward | delta | outcome |",
        "|---:|---:|---:|---:|---|",
    ]
    for row in summary["seed_rows"]:
        lines.append(
            "| {seed} | {base} | {cand} | {delta} | {outcome} |".format(
                seed=row["seed"],
                base=_fmt(row["baseline_total_reward"]),
                cand=_fmt(row["candidate_total_reward"]),
                delta=_fmt(row["delta"]),
                outcome=row["outcome"],
            )
        )

    lines.extend(
        [
            "",
            "## Secondary Metric Tradeoffs",
            "",
            f"Classification: `{tradeoffs['classification']}`.",
            "",
            "| metric | delta vs matched Paper9 | direction |",
            "|---|---:|---|",
        ]
    )
    for metric, delta in tradeoffs["deltas_vs_matched_paper9"].items():
        if metric in tradeoffs["aligned_metrics"]:
            direction = "aligned"
        elif metric in tradeoffs["tradeoff_metrics"]:
            direction = "tradeoff"
        else:
            direction = "neutral"
        lines.append(f"| {metric} | {_fmt(delta)} | {direction} |")

    lines.extend(
        [
            "",
            "## Claim Gates",
            "",
            "| claim gate | status | manuscript wording |",
            "|---|---|---|",
            "| descriptive mean reward anchor | {status} | descriptive matched 5-seed reward anchor |".format(
                status=gates["descriptive_mean_reward_anchor_supported"],
            ),
            "| mixed seed-wise outcome | {status} | mixed seed-wise outcome |".format(
                status=gates["mixed_seedwise_outcome_required"],
            ),
            "| uniform superiority | {status} | uniform superiority is not supported |".format(
                status=gates["uniform_superiority_supported"],
            ),
            "| inferential superiority | {status} | inferential superiority is not supported |".format(
                status=gates["inferential_superiority_supported"],
            ),
            "| executable-mask necessity | {status} | executable-mask necessity |".format(
                status=gates["executable_mask_necessity_supported"],
            ),
            "| monitor gate reward gain | {status} | monitor gate as evidence control |".format(
                status=gates["monitor_gate_direct_reward_gain_supported"],
            ),
            "| Stage 3 50-state scale-up | {status} | Stage 3 boundary evidence |".format(
                status=gates["stage3_50state_scaleup_supported"],
            ),
            "| transfer superiority | {status} | Dongxing/Neijiang calibration evidence |".format(
                status=gates["robust_transfer_superiority_supported"],
            ),
            "",
            "## Interpretation Boundary",
            "",
            "Use this audit to harden CEUS manuscript language. It supports a bounded descriptive Bishan 20x16/top5 mean-reward statement, documents executable-mask necessity, and treats the monitor gate as evidence control rather than as a separately proven online reward-gain mechanism.",
            "",
            "The current evidence does not support broad scale-up, transfer superiority, or cadastral deployment claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_baseline_hardening_audit(
    *,
    matched_5seed_json: str | Path,
    mechanism_packet_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict[str, Any]:
    matched_path = Path(matched_5seed_json)
    mechanism_path = Path(mechanism_packet_json)
    audit = build_baseline_hardening_audit(
        matched_5seed=json.loads(matched_path.read_text(encoding="utf-8")),
        mechanism_packet=json.loads(mechanism_path.read_text(encoding="utf-8")),
        matched_5seed_source=_relative_to_root(matched_path),
        mechanism_packet_source=_relative_to_root(mechanism_path),
        date=date,
    )
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(audit, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(hardening_markdown_report(audit), encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 CEUS baseline and inference hardening audit."
    )
    parser.add_argument("--matched-5seed-json", default=DEFAULT_MATCHED_5SEED_JSON)
    parser.add_argument("--mechanism-packet-json", default=DEFAULT_MECHANISM_PACKET_JSON)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = write_baseline_hardening_audit(
        matched_5seed_json=args.matched_5seed_json,
        mechanism_packet_json=args.mechanism_packet_json,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
