import argparse
import json
from pathlib import Path
from typing import Any


THRESHOLDS = {
    "candidate_topk_regret": 0.25,
    "candidate_topk_overlap": 0.50,
    "one_step_topk_regret": 0.25,
}

NEAR_PASS_MARGIN = 0.20


def _as_float(value: Any) -> float:
    if value is None:
        raise ValueError("monitor metric is missing")
    return float(value)


def _failed_metrics(metrics: dict[str, Any]) -> list[str]:
    failed = []
    if _as_float(metrics.get("candidate_topk_regret")) > THRESHOLDS["candidate_topk_regret"]:
        failed.append("candidate_topk_regret")
    if _as_float(metrics.get("candidate_topk_overlap")) < THRESHOLDS["candidate_topk_overlap"]:
        failed.append("candidate_topk_overlap")
    if _as_float(metrics.get("one_step_topk_regret")) < THRESHOLDS["one_step_topk_regret"]:
        failed.append("one_step_topk_regret")
    return failed


def _within_near_pass(metrics: dict[str, Any], failed: list[str]) -> bool:
    if len(failed) != 1:
        return False
    if _as_float(metrics.get("one_step_topk_regret")) <= 0.0:
        return False

    metric = failed[0]
    if metric == "candidate_topk_regret":
        return _as_float(metrics[metric]) <= THRESHOLDS[metric] * (1.0 + NEAR_PASS_MARGIN)
    if metric == "candidate_topk_overlap":
        return _as_float(metrics[metric]) >= THRESHOLDS[metric] * (1.0 - NEAR_PASS_MARGIN)
    if metric == "one_step_topk_regret":
        return _as_float(metrics[metric]) >= THRESHOLDS[metric] * (1.0 - NEAR_PASS_MARGIN)
    return False


def classify_monitor(monitor: dict[str, Any]) -> dict[str, Any]:
    metrics = monitor.get("metrics", {})
    failed = _failed_metrics(metrics)
    if monitor.get("decision") == "continue" and not failed:
        decision_class = "pass"
    elif _within_near_pass(metrics, failed):
        decision_class = "near_pass"
    else:
        decision_class = "fail"

    return {
        "top_k": int(monitor["top_k"]),
        "monitor_decision": monitor.get("decision"),
        "decision_class": decision_class,
        "failed_metrics": failed,
        "candidate_topk_regret": _as_float(metrics.get("candidate_topk_regret")),
        "candidate_topk_overlap": _as_float(metrics.get("candidate_topk_overlap")),
        "one_step_topk_regret": _as_float(metrics.get("one_step_topk_regret")),
    }


def _best_regret(monitors: list[dict[str, Any]]) -> float:
    return min(float(item["candidate_topk_regret"]) for item in monitors)


def _best_overlap(monitors: list[dict[str, Any]]) -> float:
    return max(float(item["candidate_topk_overlap"]) for item in monitors)


def _best_one_step(monitors: list[dict[str, Any]]) -> float:
    return max(float(item["one_step_topk_regret"]) for item in monitors)


def classify_run(run: dict[str, Any]) -> dict[str, Any]:
    monitors = [classify_monitor(item) for item in run.get("monitors", [])]
    if not monitors:
        raise ValueError(f"run {run.get('run_name')} has no monitor rows")

    pass_topks = [item["top_k"] for item in monitors if item["decision_class"] == "pass"]
    near_topks = [item["top_k"] for item in monitors if item["decision_class"] == "near_pass"]
    if pass_topks:
        row_decision = "pass"
        selected_top_k = min(pass_topks)
    elif near_topks:
        row_decision = "near_pass"
        selected_top_k = None
    else:
        row_decision = "fail"
        selected_top_k = None

    return {
        "run_name": str(run["run_name"]),
        "n_states": int(run["n_states"]),
        "candidate_actions": int(run["candidate_actions"]),
        "label_horizon": int(run["label_horizon"]),
        "frontier_fraction": float(run["frontier_fraction"]),
        "label_seed": int(run["label_seed"]),
        "row_decision": row_decision,
        "selected_top_k": selected_top_k,
        "pass_top_ks": pass_topks,
        "near_pass_top_ks": near_topks,
        "best_candidate_topk_regret": _best_regret(monitors),
        "best_candidate_topk_overlap": _best_overlap(monitors),
        "best_one_step_topk_regret": _best_one_step(monitors),
        "monitors": monitors,
    }


def decision_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "pass": sum(1 for row in rows if row["row_decision"] == "pass"),
        "near_pass": sum(1 for row in rows if row["row_decision"] == "near_pass"),
        "fail": sum(1 for row in rows if row["row_decision"] == "fail"),
    }


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Paper10 Original-Vision Stage 1 Monitor Matrix",
        "",
        f"Source summary: `{payload['source_summary']}`",
        "",
        "## Decision Counts",
        "",
        "| decision | count |",
        "|---|---:|",
    ]
    for key in ("pass", "near_pass", "fail"):
        lines.append(f"| {key} | {payload['decision_counts'].get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| run | decision | selected top-k | near-pass top-k | best candidate regret | best candidate overlap | best one-step regret |",
            "|---|---|---:|---|---:|---:|---:|",
        ]
    )
    for row in payload["runs"]:
        selected = row["selected_top_k"] if row["selected_top_k"] is not None else "none"
        near = ",".join(str(item) for item in row["near_pass_top_ks"]) or "none"
        lines.append(
            "| {run} | {decision} | {selected} | {near} | {regret:.4f} | {overlap:.4f} | {one_step:.4f} |".format(
                run=row["run_name"],
                decision=row["row_decision"],
                selected=selected,
                near=near,
                regret=float(row["best_candidate_topk_regret"]),
                overlap=float(row["best_candidate_topk_overlap"]),
                one_step=float(row["best_one_step_topk_regret"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation Lock",
            "",
            "A `pass` row authorizes matched training and rollout follow-up. A `near_pass` row authorizes diagnostic follow-up only. A `fail` row is evidence for that predefined row, not a general rejection of the original Paper10 vision.",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_ablation(
    summary_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> dict[str, Any]:
    summary_json = Path(summary_json)
    output_json = Path(output_json)
    output_md = Path(output_md)
    source = json.loads(summary_json.read_text(encoding="utf-8"))
    rows = [classify_run(run) for run in source.get("runs", [])]
    payload = {
        "source_summary": str(summary_json),
        "thresholds": THRESHOLDS,
        "near_pass_margin": NEAR_PASS_MARGIN,
        "gate_topks": source.get("gate_topks", []),
        "decision_counts": decision_counts(rows),
        "runs": rows,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = summarize_ablation(args.summary_json, args.output_json, args.output_md)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
