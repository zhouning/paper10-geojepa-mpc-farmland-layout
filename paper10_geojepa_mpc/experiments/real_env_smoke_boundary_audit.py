import argparse
import json
from pathlib import Path
from typing import Iterable


DATE = "2026-06-19"
CONFIG_FIELDS_FOR_BOUNDARY = (
    "checkpoint",
    "selector",
    "horizon",
    "top_k",
    "candidate_score_mode",
    "candidate_value_weight",
)


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def _step_trace_signature(payload: dict) -> list[dict]:
    signature = []
    for step in payload.get("steps", []):
        signature.append(
            {
                "step": int(step.get("step", len(signature) + 1)),
                "action": int(step.get("action", -1)),
                "reward": round(float(step.get("reward", 0.0)), 12),
            }
        )
    return signature


def _smoke_row(name: str, source_report: str, payload: dict) -> dict:
    config = payload.get("configuration", {})
    outcome = payload.get("outcome", {})
    metrics = payload.get("final_metrics", {})
    return {
        "name": name,
        "source_report": source_report,
        "date": payload.get("date"),
        "command": payload.get("command"),
        "raw_output": payload.get("raw_output"),
        "checkpoint": config.get("checkpoint"),
        "prepared_dir": config.get("prepared_dir"),
        "env_source": config.get("env_source"),
        "seed": config.get("seed"),
        "horizon": config.get("horizon"),
        "top_k": config.get("top_k"),
        "rollout_steps": config.get("rollout_steps"),
        "mask_mode": config.get("mask_mode"),
        "selector": config.get("selector"),
        "candidate_score_mode": config.get("candidate_score_mode"),
        "candidate_value_weight": config.get("candidate_value_weight"),
        "random_continuation_mode": config.get("random_continuation_mode"),
        "stable_candidate_order": config.get("stable_candidate_order"),
        "steps_run": outcome.get("steps_run"),
        "total_reward": float(outcome.get("total_reward", 0.0)),
        "positive_reward_steps": int(outcome.get("positive_reward_steps", 0)),
        "negative_reward_steps": int(outcome.get("negative_reward_steps", 0)),
        "min_base_valid": int(outcome.get("min_base_valid", 0)),
        "min_executable_valid": int(outcome.get("min_executable_valid", 0)),
        "terminated": bool(outcome.get("terminated", False)),
        "truncated": bool(outcome.get("truncated", False)),
        "final_metrics": {
            "slope_change_pct": float(metrics.get("slope_change_pct", 0.0)),
            "cont_change": float(metrics.get("cont_change", 0.0)),
            "baimu_area_change_ha": float(metrics.get("baimu_area_change_ha", 0.0)),
        },
        "step_trace_signature": _step_trace_signature(payload),
    }


def _different_fields(smokes: list[dict]) -> list[str]:
    different = []
    for field in CONFIG_FIELDS_FOR_BOUNDARY:
        values = {json.dumps(smoke.get(field), sort_keys=True) for smoke in smokes}
        if len(values) > 1:
            different.append(field)
    return different


def _same_step_trace(smokes: list[dict]) -> bool:
    if len(smokes) < 2:
        return False
    signatures = [smoke.get("step_trace_signature", []) for smoke in smokes]
    if not signatures[0]:
        return False
    return all(signature == signatures[0] for signature in signatures[1:])


def _comparability_reasons(
    smokes: list[dict],
    different_fields: list[str],
    *,
    same_step_trace: bool,
) -> list[str]:
    reasons = []
    if different_fields:
        reasons.append(
            "different checkpoint, selector, horizon, and top_k settings"
            if {"checkpoint", "selector", "horizon", "top_k"}.issubset(
                set(different_fields)
            )
            else "configuration settings differ across smoke reports"
        )
    if {smoke.get("seed") for smoke in smokes} == {0} and {
        smoke.get("steps_run") for smoke in smokes
    } == {5}:
        reasons.append("single seed and five executed steps")
    if same_step_trace:
        reasons.append("matched smoke reports have identical action/reward traces")
    if any(
        smoke.get("selector") == "value_filter"
        and smoke.get("negative_reward_steps", 0)
        for smoke in smokes
    ):
        reasons.append("value-filter run includes one negative reward step")
    elif any(smoke.get("negative_reward_steps", 0) for smoke in smokes):
        reasons.append("at least one smoke report includes a negative reward step")
    return reasons


def build_boundary_audit(
    smoke_reports: Iterable[tuple[str, str, dict]],
    *,
    date: str = DATE,
) -> dict:
    smokes = [
        _smoke_row(name=name, source_report=source_report, payload=payload)
        for name, source_report, payload in smoke_reports
    ]
    different_fields = _different_fields(smokes)
    same_trace = _same_step_trace(smokes)
    return {
        "date": date,
        "status": "execution-chain boundary audit",
        "smokes": smokes,
        "comparability": {
            "performance_comparison_valid": False,
            "planning_quality_result": False,
            "short_horizon_performance_comparison": False,
            "same_step_trace": same_trace,
            "different_fields": different_fields,
            "reasons": _comparability_reasons(
                smokes,
                different_fields,
                same_step_trace=same_trace,
            ),
        },
        "interpretation_boundary": (
            "These smoke reports confirm execution-chain reachability only. "
            "They are not a planning-quality result, not a short-horizon "
            "performance comparison, and not support for a new scale-up claim."
        ),
    }


def markdown_report(payload: dict) -> str:
    comparability = payload["comparability"]
    lines = [
        "# Paper10 real-environment smoke boundary audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: execution-chain boundary audit for the current full-Bishan real-environment smoke reports.",
        "",
        "## Boundary",
        "",
        "This audit is not a planning-quality result and not a short-horizon performance comparison. It only records that the tracked real-environment smoke reports exercise the full Bishan execution path.",
        "",
        f"Same action/reward trace: `{str(comparability.get('same_step_trace', False)).lower()}`",
        "",
        "Reasons:",
    ]
    for reason in comparability["reasons"]:
        lines.append(f"- {reason}")

    lines.extend(
        [
            "",
            "Different configuration fields: "
            + ", ".join(f"`{field}`" for field in comparability["different_fields"]),
            "",
            "## Smoke Rows",
            "",
            "| smoke | selector | horizon | top_k | steps | total reward | positive steps | negative steps | min executable-valid actions |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for smoke in payload["smokes"]:
        lines.append(
            "| {name} | `{selector}` | {horizon} | {top_k} | {steps} | {reward} | {positive} | {negative} | {valid} |".format(
                name=smoke["name"],
                selector=smoke["selector"],
                horizon=smoke["horizon"],
                top_k=smoke["top_k"],
                steps=smoke["steps_run"],
                reward=_fmt(smoke["total_reward"]),
                positive=smoke["positive_reward_steps"],
                negative=smoke["negative_reward_steps"],
                valid=smoke["min_executable_valid"],
            )
        )

    lines.extend(
        [
            "",
            "## Source Reports",
            "",
        ]
    )
    for smoke in payload["smokes"]:
        lines.append(f"- `{smoke['name']}`: `{smoke['source_report']}`")

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            payload["interpretation_boundary"],
            "",
            "A negative reward step keeps the current real-environment evidence in smoke-test territory and prevents treating the row as performance evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


def _parse_smoke_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "--smoke values must use the form name=path"
        )
    name, path = value.split("=", 1)
    if not name.strip() or not path.strip():
        raise argparse.ArgumentTypeError(
            "--smoke values must include both a name and path"
        )
    return name.strip(), Path(path.strip())


def write_boundary_audit(
    smoke_reports: Iterable[tuple[str, str | Path]],
    output_json: str | Path,
    output_md: str | Path,
    *,
    date: str = DATE,
) -> dict:
    loaded = []
    for name, path_value in smoke_reports:
        path = Path(path_value)
        loaded.append((name, str(path), json.loads(path.read_text(encoding="utf-8"))))

    payload = build_boundary_audit(loaded, date=date)

    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    output_md_path = Path(output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke",
        action="append",
        required=True,
        help="Named smoke report JSON in the form name=path. Repeat for each report.",
    )
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_boundary_audit(
        [_parse_smoke_arg(item) for item in args.smoke],
        args.output_json,
        args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()