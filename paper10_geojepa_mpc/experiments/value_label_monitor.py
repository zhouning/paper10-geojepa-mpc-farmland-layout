import argparse
import json
from pathlib import Path
from typing import Mapping

import numpy as np

from paper10_geojepa_mpc.experiments.value_label_diagnostics import (
    value_label_diagnostics,
)


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def _monitor_metrics(diagnostics: dict) -> dict[str, float | None]:
    one_step = diagnostics["one_step_vs_return"]
    candidate = diagnostics.get("candidate_score_vs_return")
    return {
        "n_states": float(diagnostics["n_states"]),
        "one_step_topk_regret": float(one_step["topk_best_return_regret_mean"]),
        "one_step_topk_overlap": float(one_step["topk_overlap_fraction_mean"]),
        "one_step_top1_disagreement": float(one_step["top1_disagreement_rate"]),
        "candidate_topk_regret": (
            float(candidate["topk_best_return_regret_mean"]) if candidate else None
        ),
        "candidate_topk_overlap": (
            float(candidate["topk_overlap_fraction_mean"]) if candidate else None
        ),
        "candidate_top1_disagreement": (
            float(candidate["top1_disagreement_rate"]) if candidate else None
        ),
        "candidate_pearson_flat": float(candidate["pearson_flat"]) if candidate else None,
    }


def monitor_value_labels(
    dataset: Mapping[str, np.ndarray],
    top_k: int = 5,
    min_states: int = 10,
    candidate_topk_regret_max: float = 0.25,
    candidate_topk_overlap_min: float = 0.5,
    one_step_topk_regret_min: float = 0.25,
) -> dict:
    diagnostics = value_label_diagnostics(dataset, top_k=top_k)
    metrics = _monitor_metrics(diagnostics)
    reasons = []

    n_states = int(diagnostics["n_states"])
    if n_states < min_states:
        reasons.append(f"Need at least {min_states} states; found {n_states}.")
        decision = "wait_more_states"
    elif "candidate_score_vs_return" not in diagnostics:
        reasons.append("candidate_scores are missing; cannot monitor frontier quality.")
        decision = "stop"
    else:
        candidate_topk_regret = float(metrics["candidate_topk_regret"])
        candidate_topk_overlap = float(metrics["candidate_topk_overlap"])
        one_step_topk_regret = float(metrics["one_step_topk_regret"])

        if candidate_topk_regret > candidate_topk_regret_max:
            reasons.append(
                "candidate top-k regret "
                f"{candidate_topk_regret:.4f} exceeds max {candidate_topk_regret_max:.4f}."
            )
        if candidate_topk_overlap < candidate_topk_overlap_min:
            reasons.append(
                "candidate top-k overlap "
                f"{candidate_topk_overlap:.4f} is below min {candidate_topk_overlap_min:.4f}."
            )
        if one_step_topk_regret < one_step_topk_regret_min:
            reasons.append(
                "one-step top-k regret "
                f"{one_step_topk_regret:.4f} is below min {one_step_topk_regret_min:.4f}; "
                "multi-step labels may not add enough filtering signal."
            )

        decision = "stop" if reasons else "continue"
        if decision == "continue":
            reasons.append("Candidate top-k coverage is usable and one-step regret remains material.")

    return {
        "decision": decision,
        "top_k": int(diagnostics["top_k"]),
        "min_states": int(min_states),
        "thresholds": {
            "candidate_topk_regret_max": float(candidate_topk_regret_max),
            "candidate_topk_overlap_min": float(candidate_topk_overlap_min),
            "one_step_topk_regret_min": float(one_step_topk_regret_min),
        },
        "metrics": metrics,
        "reasons": reasons,
        "diagnostics": diagnostics,
    }


def monitor_markdown_report(result: dict) -> str:
    lines = [
        "# Value-label monitor",
        "",
        f"Decision: `{result['decision']}`",
        f"Top-k: `{result['top_k']}`",
        f"Minimum states: `{result['min_states']}`",
        "",
        "## Metrics",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for key, value in result["metrics"].items():
        lines.append(f"| {key} | {'n/a' if value is None else _fmt(value)} |")
    lines.extend(["", "## Reasons", ""])
    for reason in result["reasons"]:
        lines.append(f"- {reason}")
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-states", type=int, default=10)
    parser.add_argument("--candidate-topk-regret-max", type=float, default=0.25)
    parser.add_argument("--candidate-topk-overlap-min", type=float, default=0.5)
    parser.add_argument("--one-step-topk-regret-min", type=float, default=0.25)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    result = monitor_value_labels(
        _load_npz(input_path),
        top_k=args.top_k,
        min_states=args.min_states,
        candidate_topk_regret_max=args.candidate_topk_regret_max,
        candidate_topk_overlap_min=args.candidate_topk_overlap_min,
        one_step_topk_regret_min=args.one_step_topk_regret_min,
    )
    result["input"] = str(input_path)
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text, encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(monitor_markdown_report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
