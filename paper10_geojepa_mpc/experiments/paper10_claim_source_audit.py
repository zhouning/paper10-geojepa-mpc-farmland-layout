import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(value: str | int | float) -> float:
    return float(value)


def _round(value: float) -> float:
    return round(value, 10)


def _row_mean(row: dict[str, str]) -> float:
    if "mean_reward" in row:
        return _float(row["mean_reward"])
    return _float(row["reward_mean"])


def _by_family(rows: Iterable[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    result = {}
    for row in rows:
        if row.get("label_type") == key:
            result[row["family"]] = row
    return result


def _low_budget_by_budget(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    result: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        result.setdefault(row["budget"], {})[row["family"]] = row
    return result


def _single_row(rows: list[dict], role: str) -> dict:
    matches = [row for row in rows if row.get("role") == role]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {role} row, found {len(matches)}")
    return matches[0]


def build_stage3_claim_audit(stage3_payload: dict) -> dict:
    baseline = stage3_payload["paper9_baseline"]["aggregate"]
    rows = stage3_payload["rows"]
    anchor = _single_row(rows, "frozen_anchor")
    confirmatory = [row for row in rows if row.get("role") == "confirmatory_pass"]
    diagnostic = _single_row(rows, "diagnostic_near_pass")

    baseline_mean = _float(baseline["total_reward_mean"])
    baseline_std = _float(baseline["total_reward_std_sample"])
    anchor_mean = _float(anchor["aggregate"]["total_reward_mean"])
    anchor_std = _float(anchor["aggregate"]["total_reward_std_sample"])
    anchor_delta = _float(anchor["matched_paper9_baseline_delta"]["total_reward_mean"])

    confirmatory_rows = []
    for row in confirmatory:
        delta = _float(row["matched_paper9_baseline_delta"]["total_reward_mean"])
        confirmatory_rows.append(
            {
                "run_name": row["run_name"],
                "mean_reward": _float(row["aggregate"]["total_reward_mean"]),
                "reward_delta_vs_baseline": delta,
                "beats_baseline": delta > 0,
            }
        )

    diagnostic_delta = _float(diagnostic["matched_paper9_baseline_delta"]["total_reward_mean"])
    return {
        "baseline_reward_mean": baseline_mean,
        "baseline_reward_std_sample": baseline_std,
        "anchor": {
            "run_name": anchor["run_name"],
            "mean_reward": anchor_mean,
            "reward_delta_vs_baseline": anchor_delta,
            "std_sample": anchor_std,
            "std_delta_vs_baseline": _round(anchor_std - baseline_std),
        },
        "confirmatory_rows": confirmatory_rows,
        "diagnostic_near_pass": {
            "run_name": diagnostic["run_name"],
            "mean_reward": _float(diagnostic["aggregate"]["total_reward_mean"]),
            "reward_delta_vs_baseline": diagnostic_delta,
            "pooled_with_confirmatory": False,
        },
        "claims": {
            "bishan_anchor_improves_reward_and_stability": {
                "supported": anchor_delta > 0 and anchor_std < baseline_std,
                "basis": "anchor reward delta is positive and anchor sample standard deviation is below baseline",
            },
            "confirmatory_50state_rows_beat_baseline": {
                "supported": all(row["beats_baseline"] for row in confirmatory_rows),
                "basis": "all confirmatory rows would need positive reward deltas versus baseline",
            },
            "diagnostic_near_pass_strengthens_confirmatory_claim": {
                "supported": False,
                "basis": "diagnostic row is not pooled with confirmatory rows",
            },
        },
    }


def build_dongxing_claim_audit(
    return_label_rows: Iterable[dict[str, str]],
    low_budget_rows: Iterable[dict[str, str]],
) -> dict:
    return_rows = list(return_label_rows)
    pairwise = _by_family(return_rows, "pairwise_1000s")
    return_50x16 = _by_family(return_rows, "return_50x16_h5")
    if not {"transfer", "scratch"} <= set(pairwise) or not {"transfer", "scratch"} <= set(return_50x16):
        raise ValueError("Dongxing return-label rows must include transfer and scratch pairwise/50x16 rows")

    transfer_gain = _round(_row_mean(return_50x16["transfer"]) - _row_mean(pairwise["transfer"]))
    scratch_gain = _round(_row_mean(return_50x16["scratch"]) - _row_mean(pairwise["scratch"]))
    transfer_minus_scratch_50x16 = _round(
        _row_mean(return_50x16["transfer"]) - _row_mean(return_50x16["scratch"])
    )

    low_budget_comparisons = {}
    for budget, families in sorted(_low_budget_by_budget(low_budget_rows).items(), key=lambda item: int(item[0])):
        if not {"transfer", "scratch"} <= set(families):
            continue
        effect = _round(_row_mean(families["transfer"]) - _row_mean(families["scratch"]))
        low_budget_comparisons[budget] = {
            "transfer_reward_mean": _row_mean(families["transfer"]),
            "scratch_reward_mean": _row_mean(families["scratch"]),
            "reward_effect_transfer_minus_scratch": effect,
            "transfer_higher": effect > 0,
        }

    low_budget_all_transfer_higher = (
        bool(low_budget_comparisons)
        and all(row["transfer_higher"] for row in low_budget_comparisons.values())
    )

    return {
        "return_50x16": {
            "transfer_reward_mean": _row_mean(return_50x16["transfer"]),
            "scratch_reward_mean": _row_mean(return_50x16["scratch"]),
            "transfer_gain_vs_pairwise": transfer_gain,
            "scratch_gain_vs_pairwise": scratch_gain,
            "transfer_minus_scratch": transfer_minus_scratch_50x16,
        },
        "low_budget_comparisons": low_budget_comparisons,
        "claims": {
            "return_label_scaling_improves_transfer_family": {
                "supported": transfer_gain > 0,
                "basis": "return_50x16_h5 transfer mean reward exceeds pairwise transfer",
            },
            "return_label_scaling_improves_scratch_family": {
                "supported": scratch_gain > 0,
                "basis": "return_50x16_h5 scratch mean reward exceeds pairwise scratch",
            },
            "robust_transfer_superiority": {
                "supported": transfer_minus_scratch_50x16 > 0 and low_budget_all_transfer_higher,
                "basis": "transfer would need to exceed scratch at 50x16 and all low-label budgets",
            },
        },
    }


def markdown_report(payload: dict) -> str:
    stage3 = payload["stage3"]
    dongxing = payload["dongxing"]
    lines = [
        "# Paper10 claim-source consistency audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived audit of the current Paper10 manuscript-facing claims. This file checks key numbers against tracked JSON/CSV evidence and does not add new experimental claims.",
        "",
        "## Source files",
        "",
    ]
    for key, value in payload["source_files"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Bishan and Stage 3 checks",
            "",
            "| claim | source-derived result | status |",
            "|---|---|---|",
        ]
    )
    anchor = stage3["anchor"]
    lines.append(
        "| Bishan 20x16/top5 anchor improves reward and stability | "
        f"mean {anchor['mean_reward']:.4f} versus baseline {stage3['baseline_reward_mean']:.4f}; "
        f"sample std {anchor['std_sample']:.4f} versus {stage3['baseline_reward_std_sample']:.4f} | "
        f"{stage3['claims']['bishan_anchor_improves_reward_and_stability']['supported']} |"
    )
    confirmatory_summary = "; ".join(
        f"{row['run_name']} delta {row['reward_delta_vs_baseline']:.4f}"
        for row in stage3["confirmatory_rows"]
    )
    lines.append(
        "| Stage 3 confirmatory 50-state rows beat the matched baseline | "
        f"{confirmatory_summary} | "
        f"{stage3['claims']['confirmatory_50state_rows_beat_baseline']['supported']} |"
    )
    diagnostic = stage3["diagnostic_near_pass"]
    lines.append(
        "| Diagnostic near-pass can strengthen the confirmatory claim | "
        f"{diagnostic['run_name']} mean {diagnostic['mean_reward']:.4f}, "
        f"delta {diagnostic['reward_delta_vs_baseline']:.4f}; must not be pooled | "
        f"{stage3['claims']['diagnostic_near_pass_strengthens_confirmatory_claim']['supported']} |"
    )

    lines.extend(
        [
            "",
            "Interpretation: the Bishan anchor is source-supported, while confirmatory 50-state rows do not beat the matched baseline.",
            "",
            "## Dongxing/Neijiang checks",
            "",
            "| claim | source-derived result | status |",
            "|---|---|---|",
        ]
    )
    return_50x16 = dongxing["return_50x16"]
    lines.append(
        "| Return-label scaling improves transfer family | "
        f"gain versus pairwise {return_50x16['transfer_gain_vs_pairwise']:.4f} | "
        f"{dongxing['claims']['return_label_scaling_improves_transfer_family']['supported']} |"
    )
    lines.append(
        "| Return-label scaling improves scratch family | "
        f"gain versus pairwise {return_50x16['scratch_gain_vs_pairwise']:.4f} | "
        f"{dongxing['claims']['return_label_scaling_improves_scratch_family']['supported']} |"
    )
    low_budget_summary = "; ".join(
        f"budget {budget}: {row['reward_effect_transfer_minus_scratch']:.4f}"
        for budget, row in dongxing["low_budget_comparisons"].items()
    )
    lines.append(
        "| Robust Bishan-to-Dongxing transfer superiority | "
        f"50x16 transfer minus scratch {return_50x16['transfer_minus_scratch']:.4f}; "
        f"low-label effects {low_budget_summary} | "
        f"{dongxing['claims']['robust_transfer_superiority']['supported']} |"
    )

    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "- Supported: Bishan 20x16/top5 reward and stability improvement under the matched rollout protocol.",
            "- Supported descriptively: Dongxing/Neijiang return-label scaling improves transfer and scratch families versus their pairwise rows.",
            "- Not supported: broad confirmatory 50-state baseline beating.",
            "- Not supported: robust Bishan-to-Dongxing transfer superiority.",
            "- Not supported: direct positive scale-up under the 50-state confirmatory protocol or operational irregular-parcel deployment.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.paper10_claim_source_audit --stage3-json paper10_geojepa_mpc\\experiments\\results\\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --dongxing-return-label-csv paper10_geojepa_mpc\\experiments\\results\\e0_dongxing_return_label_family_summary_2026-06-10.csv --dongxing-low-budget-csv paper10_geojepa_mpc\\experiments\\results\\e0_dongxing_low_label_budget_family_summary_2026-06-10.csv --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_claim_source_consistency_audit_2026-06-18.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_claim_source_consistency_audit_2026-06-18.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_paper10_claim_sources(
    stage3_json: str | Path,
    dongxing_return_label_csv: str | Path,
    dongxing_low_budget_csv: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> dict:
    stage3_path = Path(stage3_json)
    return_csv_path = Path(dongxing_return_label_csv)
    low_csv_path = Path(dongxing_low_budget_csv)
    payload = {
        "date": "2026-06-18",
        "source_files": {
            "stage3_json": str(stage3_path),
            "dongxing_return_label_csv": str(return_csv_path),
            "dongxing_low_budget_csv": str(low_csv_path),
        },
        "stage3": build_stage3_claim_audit(json.loads(stage3_path.read_text(encoding="utf-8"))),
        "dongxing": build_dongxing_claim_audit(
            _read_csv(return_csv_path),
            _read_csv(low_csv_path),
        ),
    }

    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    output_md_path = Path(output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage3-json", required=True)
    parser.add_argument("--dongxing-return-label-csv", required=True)
    parser.add_argument("--dongxing-low-budget-csv", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_paper10_claim_sources(
        args.stage3_json,
        args.dongxing_return_label_csv,
        args.dongxing_low_budget_csv,
        args.output_json,
        args.output_md,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
