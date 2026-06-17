import argparse
import csv
import json
from pathlib import Path
from typing import Any


def choose_decision(counts: dict[str, int]) -> str:
    if int(counts.get("pass", 0)) > 0:
        return "proceed_to_stage3_confirmatory_rollouts"
    if int(counts.get("near_pass", 0)) > 0:
        return "run_stage1_optional_seed49_50_expansion"
    return "keep_conservative_ceus_theme"


def _rationale(decision: str) -> str:
    if decision == "proceed_to_stage3_confirmatory_rollouts":
        return (
            "At least one predefined Stage 1 row passed the monitor gate. "
            "Stage 3 may train and roll out only the passing rows, with matched baselines."
        )
    if decision == "run_stage1_optional_seed49_50_expansion":
        return (
            "No predefined Stage 1 row passed, but at least one row was near-pass. "
            "The optional seed49-50 label-only expansion is justified before any training."
        )
    return (
        "No predefined Stage 1 row passed or reached near-pass status. "
        "The validation program should keep the conservative CEUS theme for now."
    )


def _counts(stage1_payload: dict[str, Any]) -> dict[str, int]:
    raw = stage1_payload.get("decision_counts", {})
    return {
        "pass": int(raw.get("pass", 0)),
        "near_pass": int(raw.get("near_pass", 0)),
        "fail": int(raw.get("fail", 0)),
    }


def _comparison_rows(stage2_comparisons: list[dict[str, Any]]) -> list[str]:
    lines = []
    for row in stage2_comparisons:
        effect = float(row["reward_effect_transfer_minus_scratch"])
        lines.append(
            "| {key} | {effect:.4f} | {interpretation} |".format(
                key=row["comparison_key"],
                effect=effect,
                interpretation=row["interpretation"],
            )
        )
    if not lines:
        lines.append("| none | 0.0000 | no_matched_comparison |")
    return lines


def build_packet(
    stage1_payload: dict[str, Any],
    stage2_comparisons: list[dict[str, Any]],
) -> str:
    counts = _counts(stage1_payload)
    decision = choose_decision(counts)
    lines = [
        "# Paper10 Original-Vision Stage 1-2 Decision Packet",
        "",
        "Date: 2026-06-17",
        "",
        "## Inputs",
        "",
        "- Stage 1 monitor matrix: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md`",
        "- Stage 2 Dongxing audit: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`",
        "- Design spec: `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`",
        "",
        "## Stage 1 Summary",
        "",
        "| decision | count |",
        "|---|---:|",
        f"| pass | {counts['pass']} |",
        f"| near_pass | {counts['near_pass']} |",
        f"| fail | {counts['fail']} |",
        "",
        "## Stage 2 Summary",
        "",
        "| comparison | transfer minus scratch reward | interpretation |",
        "|---|---:|---|",
    ]
    lines.extend(_comparison_rows(stage2_comparisons))
    lines.extend(
        [
            "",
            "## Stop/Go Decision",
            "",
            f"Decision: {decision}",
            "",
            "## Rationale",
            "",
            _rationale(decision),
            "",
            "This packet is a stop/go control document. It does not change the manuscript claim by itself.",
        ]
    )
    return "\n".join(lines) + "\n"


def _read_stage2_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_decision_packet(
    stage1_json: str | Path,
    stage2_csv: str | Path,
    output_md: str | Path,
) -> str:
    stage1_path = Path(stage1_json)
    stage2_path = Path(stage2_csv)
    output_path = Path(output_md)
    stage1_payload = json.loads(stage1_path.read_text(encoding="utf-8"))
    stage2_comparisons = _read_stage2_csv(stage2_path)
    text = build_packet(stage1_payload, stage2_comparisons)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-json", required=True)
    parser.add_argument("--stage2-csv", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(write_decision_packet(args.stage1_json, args.stage2_csv, args.output_md))


if __name__ == "__main__":
    main()
