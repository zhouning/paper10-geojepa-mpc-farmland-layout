from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


@dataclass(frozen=True)
class MonitorThresholdSet:
    name: str
    candidate_topk_regret_max: float
    candidate_topk_overlap_min: float
    one_step_topk_regret_min: float


DEFAULT_THRESHOLD_SET = MonitorThresholdSet(
    name="default",
    candidate_topk_regret_max=0.25,
    candidate_topk_overlap_min=0.50,
    one_step_topk_regret_min=0.25,
)

DEFAULT_THRESHOLD_SETS = (
    MonitorThresholdSet("strict", 0.20, 0.55, 0.50),
    DEFAULT_THRESHOLD_SET,
    MonitorThresholdSet("lenient", 0.30, 0.45, 0.10),
)


def _metric(monitor: dict[str, Any], key: str) -> float:
    metrics = monitor.get("metrics")
    if not isinstance(metrics, dict) or key not in metrics:
        raise ValueError(f"monitor metric is missing: {key}")
    value = metrics[key]
    if value is None:
        raise ValueError(f"monitor metric is missing: {key}")
    return float(value)


def _recorded_threshold_set(monitor: dict[str, Any]) -> MonitorThresholdSet | None:
    thresholds = monitor.get("thresholds")
    if not isinstance(thresholds, dict):
        return None
    required = (
        "candidate_topk_regret_max",
        "candidate_topk_overlap_min",
        "one_step_topk_regret_min",
    )
    if not all(key in thresholds for key in required):
        return None
    return MonitorThresholdSet(
        name="recorded",
        candidate_topk_regret_max=float(thresholds["candidate_topk_regret_max"]),
        candidate_topk_overlap_min=float(thresholds["candidate_topk_overlap_min"]),
        one_step_topk_regret_min=float(thresholds["one_step_topk_regret_min"]),
    )


def _same_threshold_values(
    left: MonitorThresholdSet,
    right: MonitorThresholdSet,
    *,
    tolerance: float = 1e-12,
) -> bool:
    return (
        abs(left.candidate_topk_regret_max - right.candidate_topk_regret_max)
        <= tolerance
        and abs(left.candidate_topk_overlap_min - right.candidate_topk_overlap_min)
        <= tolerance
        and abs(left.one_step_topk_regret_min - right.one_step_topk_regret_min)
        <= tolerance
    )


def _threshold_provenance(recorded: MonitorThresholdSet | None) -> str:
    if recorded is None:
        return "no_recorded_thresholds"
    if _same_threshold_values(recorded, DEFAULT_THRESHOLD_SET):
        return "default_thresholds"
    return "historical_thresholds"


def _decision_alignment(recorded_decision: str, default_pass: bool) -> str:
    decision = recorded_decision.strip().lower() or "missing"
    if decision == "continue":
        decision = "continue"
    current = "pass" if default_pass else "stop"
    return f"recorded_{decision}_current_default_{current}"


def classify_monitor_at_thresholds(
    monitor: dict[str, Any],
    thresholds: MonitorThresholdSet = DEFAULT_THRESHOLD_SET,
) -> dict[str, Any]:
    candidate_regret = _metric(monitor, "candidate_topk_regret")
    candidate_overlap = _metric(monitor, "candidate_topk_overlap")
    one_step_regret = _metric(monitor, "one_step_topk_regret")
    failed_metrics = []

    if candidate_regret > thresholds.candidate_topk_regret_max:
        failed_metrics.append("candidate_topk_regret")
    if candidate_overlap < thresholds.candidate_topk_overlap_min:
        failed_metrics.append("candidate_topk_overlap")
    if one_step_regret < thresholds.one_step_topk_regret_min:
        failed_metrics.append("one_step_topk_regret")

    return {
        "threshold_set": asdict(thresholds),
        "passes": not failed_metrics,
        "failed_metrics": failed_metrics,
        "metrics": {
            "candidate_topk_regret": candidate_regret,
            "candidate_topk_overlap": candidate_overlap,
            "one_step_topk_regret": one_step_regret,
        },
    }


def _stability_class(default_pass: bool, pass_count: int, threshold_count: int) -> str:
    if default_pass and pass_count == threshold_count:
        return "robust_pass"
    if default_pass:
        return "threshold_sensitive_pass"
    if pass_count == 0:
        return "robust_stop"
    return "threshold_sensitive_stop"


def summarize_monitor_sensitivity(
    monitors: Sequence[dict[str, Any]],
    threshold_sets: Iterable[MonitorThresholdSet] = DEFAULT_THRESHOLD_SETS,
) -> dict[str, Any]:
    thresholds = list(threshold_sets)
    if not thresholds:
        raise ValueError("at least one threshold set is required")

    rows = []
    for index, monitor in enumerate(monitors):
        name = str(monitor.get("name") or monitor.get("input") or f"monitor_{index}")
        classifications = [
            classify_monitor_at_thresholds(monitor, threshold) for threshold in thresholds
        ]
        pass_count = sum(1 for item in classifications if item["passes"])
        threshold_count = len(classifications)
        default_result = classify_monitor_at_thresholds(monitor, DEFAULT_THRESHOLD_SET)
        default_pass = bool(default_result["passes"])
        metrics = default_result["metrics"]
        recorded_threshold = _recorded_threshold_set(monitor)
        recorded_result = (
            classify_monitor_at_thresholds(monitor, recorded_threshold)
            if recorded_threshold is not None
            else None
        )
        recorded_decision = str(monitor.get("decision", ""))
        rows.append(
            {
                "name": name,
                "top_k": int(monitor.get("top_k", 0)),
                "recorded_decision": recorded_decision,
                "recorded_thresholds": (
                    asdict(recorded_threshold) if recorded_threshold is not None else None
                ),
                "recorded_threshold_pass": (
                    bool(recorded_result["passes"])
                    if recorded_result is not None
                    else None
                ),
                "threshold_provenance": _threshold_provenance(recorded_threshold),
                "decision_alignment": _decision_alignment(
                    recorded_decision=recorded_decision,
                    default_pass=default_pass,
                ),
                "default_pass": default_pass,
                "default_failed_metrics": default_result["failed_metrics"],
                "pass_count": pass_count,
                "threshold_count": threshold_count,
                "pass_fraction": pass_count / threshold_count,
                "stability_class": _stability_class(
                    default_pass=default_pass,
                    pass_count=pass_count,
                    threshold_count=threshold_count,
                ),
                "metrics": metrics,
                "classifications": classifications,
            }
        )

    summary_counts: dict[str, int] = {}
    for row in rows:
        key = row["stability_class"]
        summary_counts[key] = summary_counts.get(key, 0) + 1

    return {
        "status": "monitor-threshold sensitivity audit",
        "threshold_sets": [asdict(threshold) for threshold in thresholds],
        "rows": rows,
        "summary_counts": summary_counts,
    }


def _yn(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


def monitor_threshold_sensitivity_report(result: dict[str, Any]) -> str:
    lines = [
        "# Monitor-threshold sensitivity audit",
        "",
        "Status: monitor-threshold sensitivity audit.",
        "",
        "This audit reruns gate classification only; it does not train models "
        "or add rollout results.",
        "",
        "## Threshold sets",
        "",
        "| name | candidate regret max | candidate overlap min | one-step regret min |",
        "|---|---:|---:|---:|",
    ]
    for threshold in result["threshold_sets"]:
        lines.append(
            "| {name} | {candidate_topk_regret_max:.4f} | "
            "{candidate_topk_overlap_min:.4f} | {one_step_topk_regret_min:.4f} |".format(
                **threshold
            )
        )

    lines.extend(
        [
            "",
            "## Monitor sensitivity rows",
            "",
            "| monitor | current default pass | pass fraction | stability class |",
            "|---|---|---:|---|",
        ]
    )
    for row in result["rows"]:
        default_pass = "yes" if row["default_pass"] else "no"
        lines.append(
            f"| {row['name']} | {default_pass} | "
            f"{float(row['pass_fraction']):.3f} | {row['stability_class']} |"
        )

    lines.extend(
        [
            "",
            "## Recorded-decision provenance",
            "",
            "| monitor | recorded decision | recorded-threshold pass | threshold provenance | decision alignment |",
            "|---|---|---|---|---|",
        ]
    )
    for row in result["rows"]:
        lines.append(
            "| {name} | {decision} | {recorded_pass} | {provenance} | {alignment} |".format(
                name=row["name"],
                decision=row["recorded_decision"] or "n/a",
                recorded_pass=_yn(row["recorded_threshold_pass"]),
                provenance=row["threshold_provenance"],
                alignment=row["decision_alignment"],
            )
        )

    lines.extend(["", "## Interpretation boundary", ""])
    lines.append(
        "- `robust_pass` means the row passes strict, default and lenient thresholds."
    )
    lines.append(
        "- `threshold_sensitive_pass` means the row passes the default gate but "
        "not every stricter threshold."
    )
    lines.append("- `robust_stop` means the row fails every tested threshold set.")
    lines.append(
        "- `historical_thresholds` means the recorded monitor used thresholds that "
        "differ from the current CEUS audit default; the recorded decision is "
        "preserved but not treated as a current-threshold pass."
    )
    lines.append(
        "- This audit supports threshold transparency only; it is not new "
        "training or rollout evidence."
    )
    return "\n".join(lines) + "\n"


def monitors_from_stage1_matrix(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    monitors = []
    for run in matrix.get("runs", []):
        run_name = str(run.get("run_name", "run"))
        for monitor in run.get("monitors", []):
            top_k = int(monitor["top_k"])
            metrics = monitor.get("metrics") or monitor
            monitors.append(
                {
                    "name": f"{run_name}_top{top_k}",
                    "decision": str(
                        monitor.get("monitor_decision") or monitor.get("decision", "")
                    ),
                    "top_k": top_k,
                    "metrics": {
                        "candidate_topk_regret": float(metrics["candidate_topk_regret"]),
                        "candidate_topk_overlap": float(metrics["candidate_topk_overlap"]),
                        "one_step_topk_regret": float(metrics["one_step_topk_regret"]),
                    },
                }
            )
    return monitors


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_named_monitor(value: str) -> tuple[str, Path]:
    if "=" not in value:
        path = Path(value)
        return path.stem, path
    name, path = value.split("=", 1)
    if not name:
        raise ValueError("monitor name must not be empty")
    return name, Path(path)


def _load_named_monitors(values: Sequence[str]) -> list[dict[str, Any]]:
    monitors = []
    for value in values:
        name, path = _parse_named_monitor(value)
        monitor = _read_json(path)
        monitor["name"] = name
        monitor["input"] = str(path)
        monitors.append(monitor)
    return monitors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Paper10 monitor decisions against strict/default/lenient thresholds."
    )
    parser.add_argument(
        "--monitor-json",
        action="append",
        default=[],
        help="Monitor JSON path or NAME=PATH. May be passed multiple times.",
    )
    parser.add_argument(
        "--stage1-matrix-json",
        action="append",
        default=[],
        help="Stage 1 monitor matrix JSON path. May be passed multiple times.",
    )
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    monitors = _load_named_monitors(args.monitor_json)
    for matrix_path in args.stage1_matrix_json:
        monitors.extend(monitors_from_stage1_matrix(_read_json(Path(matrix_path))))
    if not monitors:
        raise SystemExit("at least one --monitor-json or --stage1-matrix-json is required")
    result = summarize_monitor_sensitivity(monitors)
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text, encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(monitor_threshold_sensitivity_report(result), encoding="utf-8")


if __name__ == "__main__":
    main()