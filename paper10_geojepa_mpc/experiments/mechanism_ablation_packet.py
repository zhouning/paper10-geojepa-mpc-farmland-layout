import argparse
import json
import math
from pathlib import Path
from typing import Any


PASS_THRESHOLDS = {
    "candidate_topk_regret": 0.25,
    "candidate_topk_overlap": 0.50,
    "one_step_topk_regret": 0.25,
}


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _as_float(value: Any) -> float:
    return float(value)


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def _reward_std_sample(payload: dict[str, Any]) -> float:
    aggregate = payload.get("aggregate", {})
    if "total_reward_std_sample" in aggregate:
        return _as_float(aggregate["total_reward_std_sample"])
    rewards = [
        _as_float(summary["total_reward"])
        for summary in payload.get("episode_summaries", [])
        if "total_reward" in summary
    ]
    return _sample_std(rewards)


def _aggregate(payload: dict[str, Any]) -> dict[str, float]:
    aggregate = payload.get("aggregate", {})
    return {
        "mean_reward": _as_float(
            aggregate.get("total_reward_mean", payload.get("total_reward", 0.0))
        ),
        "std_sample": _reward_std_sample(payload),
        "slope_change_pct_mean": _as_float(
            aggregate.get("slope_change_pct_mean", 0.0)
        ),
        "cont_change_mean": _as_float(aggregate.get("cont_change_mean", 0.0)),
        "baimu_area_change_ha_mean": _as_float(
            aggregate.get("baimu_area_change_ha_mean", 0.0)
        ),
        "zero_swap_steps_sum": _as_float(aggregate.get("zero_swap_steps_sum", 0.0)),
        "negative_zero_swap_steps_sum": _as_float(
            aggregate.get("negative_zero_swap_steps_sum", 0.0)
        ),
    }


def classify_monitor_gate(monitor: dict[str, Any]) -> dict[str, Any]:
    metrics = monitor.get("metrics", {})
    failed = []
    if (
        _as_float(metrics.get("candidate_topk_regret", 999.0))
        > PASS_THRESHOLDS["candidate_topk_regret"]
    ):
        failed.append("candidate_topk_regret")
    if (
        _as_float(metrics.get("candidate_topk_overlap", -999.0))
        < PASS_THRESHOLDS["candidate_topk_overlap"]
    ):
        failed.append("candidate_topk_overlap")
    if (
        _as_float(metrics.get("one_step_topk_regret", -999.0))
        < PASS_THRESHOLDS["one_step_topk_regret"]
    ):
        failed.append("one_step_topk_regret")

    gate_class = "pass" if monitor.get("decision") == "continue" and not failed else "stop"
    return {
        "top_k": int(monitor.get("top_k", 0)),
        "decision": str(monitor.get("decision", "")),
        "gate_class": gate_class,
        "failed_metrics": failed,
        "candidate_topk_regret": _as_float(metrics.get("candidate_topk_regret", 0.0)),
        "candidate_topk_overlap": _as_float(
            metrics.get("candidate_topk_overlap", 0.0)
        ),
        "one_step_topk_regret": _as_float(metrics.get("one_step_topk_regret", 0.0)),
    }


def compare_conditions(
    baseline_name: str,
    condition_payloads: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float | str]]:
    if baseline_name not in condition_payloads:
        raise ValueError(f"missing baseline condition: {baseline_name}")
    baseline = _aggregate(condition_payloads[baseline_name])
    rows = {}
    for name, payload in condition_payloads.items():
        agg = _aggregate(payload)
        rows[name] = {
            "condition": name,
            "mean_reward": agg["mean_reward"],
            "std_sample": agg["std_sample"],
            "slope_change_pct_mean": agg["slope_change_pct_mean"],
            "cont_change_mean": agg["cont_change_mean"],
            "baimu_area_change_ha_mean": agg["baimu_area_change_ha_mean"],
            "zero_swap_steps_sum": agg["zero_swap_steps_sum"],
            "negative_zero_swap_steps_sum": agg["negative_zero_swap_steps_sum"],
            "delta_vs_baseline_reward": agg["mean_reward"] - baseline["mean_reward"],
            "delta_vs_baseline_std_sample": agg["std_sample"] - baseline["std_sample"],
        }
    return rows


def build_packet(
    *,
    monitors: dict[str, dict[str, Any]],
    condition_payloads: dict[str, dict[str, Any]],
    stage3_boundary: dict[str, Any],
    training_metrics: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "packet": "paper10_mechanism_ablation",
        "baseline_condition": "full_gated_masked",
        "claim_boundary": {
            "geo_jepa_prior_art_guard": True,
            "do_not_claim_geo_jepa_invention": True,
            "do_not_claim_direct_50_state_success": True,
            "do_not_claim_robust_transfer_superiority": True,
        },
        "monitor_gates": {
            name: classify_monitor_gate(payload) for name, payload in monitors.items()
        },
        "condition_comparisons": compare_conditions(
            "full_gated_masked",
            condition_payloads,
        ),
        "training_metrics": training_metrics,
        "stage3_boundary": stage3_boundary,
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def markdown_report(packet: dict[str, Any]) -> str:
    lines = [
        "# Paper10 mechanism ablation evidence packet",
        "",
        "Status: mechanism experiment evidence packet, not a manuscript claim.",
        "",
        "## Claim Boundary",
        "",
        "- GeoJEPA itself is prior art and is not claimed as the Paper10 invention.",
        "- Paper10's tested mechanism is monitor-gated value labels plus executable masks plus value-filtered MPC.",
        "- The 50-state evidence remains boundary evidence unless matched rollouts beat the predefined comparator.",
        "",
        "## Monitor Gates",
        "",
        "| gate | top-k | decision | class | candidate regret | candidate overlap | one-step regret | failed metrics |",
        "|---|---:|---|---|---:|---:|---:|---|",
    ]
    for name, row in packet["monitor_gates"].items():
        lines.append(
            "| {name} | {top_k} | {decision} | {klass} | {regret} | {overlap} | {one_step} | {failed} |".format(
                name=name,
                top_k=row["top_k"],
                decision=row["decision"],
                klass=row["gate_class"],
                regret=_fmt(row["candidate_topk_regret"]),
                overlap=_fmt(row["candidate_topk_overlap"]),
                one_step=_fmt(row["one_step_topk_regret"]),
                failed=",".join(row["failed_metrics"]) or "none",
            )
        )

    lines.extend(
        [
            "",
            "## Matched Bishan Mechanism Conditions",
            "",
            "| condition | mean reward | std sample | reward delta vs full | std delta vs full | slope pct | cont | baimu ha | zero swaps | negative zero swaps |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, row in packet["condition_comparisons"].items():
        lines.append(
            "| {condition} | {reward} | {std} | {delta_reward} | {delta_std} | {slope} | {cont} | {baimu} | {zero_swaps} | {negative_zero_swaps} |".format(
                condition=name,
                reward=_fmt(row["mean_reward"]),
                std=_fmt(row["std_sample"]),
                delta_reward=_fmt(row["delta_vs_baseline_reward"]),
                delta_std=_fmt(row["delta_vs_baseline_std_sample"]),
                slope=_fmt(row["slope_change_pct_mean"]),
                cont=_fmt(row["cont_change_mean"]),
                baimu=_fmt(row["baimu_area_change_ha_mean"]),
                zero_swaps=_fmt(row["zero_swap_steps_sum"]),
                negative_zero_swaps=_fmt(row["negative_zero_swap_steps_sum"]),
            )
        )

    lines.extend(
        [
            "",
            "## Stage 3 Boundary Link",
            "",
            "The Stage 3 50-state sweep is included only to keep the mechanism result bounded. It must not be written as positive 50-state scale-up evidence unless a matched 50-state condition beats the predefined comparator.",
            "",
            "## Interpretation",
            "",
            "A useful mechanism claim requires the full gated and masked condition to outperform one or more matched ablations without relying on forbidden broad GeoJEPA, direct 50-state, or robust transfer claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_packet(
    *,
    monitor_jsons: dict[str, str | Path],
    condition_jsons: dict[str, str | Path],
    stage3_boundary_json: str | Path,
    training_metric_jsons: dict[str, str | Path],
    output_json: str | Path,
    output_md: str | Path,
) -> dict[str, Any]:
    packet = build_packet(
        monitors={name: _read_json(path) for name, path in monitor_jsons.items()},
        condition_payloads={
            name: _read_json(path) for name, path in condition_jsons.items()
        },
        stage3_boundary=_read_json(stage3_boundary_json),
        training_metrics={
            name: _read_json(path) for name, path in training_metric_jsons.items()
        },
    )
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(packet, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(markdown_report(packet), encoding="utf-8")
    return packet


def _parse_named_paths(items: list[str]) -> dict[str, Path]:
    parsed = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"expected NAME=PATH, got {item}")
        name, path = item.split("=", 1)
        parsed[name] = Path(path)
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--monitor-json", action="append", default=[], help="NAME=PATH")
    parser.add_argument("--condition-json", action="append", default=[], help="NAME=PATH")
    parser.add_argument(
        "--training-metric-json",
        action="append",
        default=[],
        help="NAME=PATH",
    )
    parser.add_argument("--stage3-boundary-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    packet = write_packet(
        monitor_jsons=_parse_named_paths(args.monitor_json),
        condition_jsons=_parse_named_paths(args.condition_json),
        stage3_boundary_json=args.stage3_boundary_json,
        training_metric_jsons=_parse_named_paths(args.training_metric_json),
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
