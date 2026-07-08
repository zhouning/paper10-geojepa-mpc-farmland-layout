import argparse
import json
from pathlib import Path


DATE = "2026-06-19"


def _fmt(value: float | int | str) -> str:
    return f"{float(value):.4f}"


def _as_float(value: float | int | str) -> float:
    return float(value)


def _single_role(rows: list[dict], role: str) -> dict:
    matches = [row for row in rows if row.get("role") == role]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {role} row, found {len(matches)}")
    return matches[0]


def _selected_top_k(row: dict) -> int:
    if "selected_top_k" in row:
        return int(row["selected_top_k"])
    diagnostics = row.get("diagnostics", {})
    if "candidate_top_k" in diagnostics:
        return int(diagnostics["candidate_top_k"])
    return 0


def _row_std_sample(row: dict) -> float:
    return _as_float(row["aggregate"]["total_reward_std_sample"])


def _row_mean(row: dict) -> float:
    return _as_float(row["aggregate"]["total_reward_mean"])


def _row_delta(row: dict) -> float:
    return _as_float(row["matched_paper9_baseline_delta"]["total_reward_mean"])


def _claim_supported(payload: dict, *path: str) -> bool:
    value = payload
    for key in path:
        value = value[key]
    return bool(value["supported"])


def _anchor_table(stage3_payload: dict, anchor_raw_audit_payload: dict) -> list[dict]:
    rows = stage3_payload["rows"]
    baseline = stage3_payload["paper9_baseline"]["aggregate"]
    anchor = _single_role(rows, "frozen_anchor")
    consistency_pass = bool(anchor_raw_audit_payload["overall_consistency_pass"])
    return [
        {
            "row_id": "matched_paper9_rank_seed2028_baseline",
            "run_name": "matched_paper9_rank_seed2028",
            "states": None,
            "candidates": None,
            "selected_top_k": None,
            "mean_reward": _as_float(baseline["total_reward_mean"]),
            "std_sample": _as_float(baseline["total_reward_std_sample"]),
            "delta_vs_baseline": 0.0,
            "raw_rollout_consistency_pass": None,
            "interpretation": "matched comparator for the Stage 3 rollout protocol",
        },
        {
            "row_id": "bishan_20x16_top5_frozen_anchor",
            "run_name": anchor["run_name"],
            "states": int(anchor["n_states"]),
            "candidates": int(anchor["candidate_actions"]),
            "selected_top_k": _selected_top_k(anchor),
            "mean_reward": _row_mean(anchor),
            "std_sample": _row_std_sample(anchor),
            "delta_vs_baseline": _row_delta(anchor),
            "raw_rollout_consistency_pass": consistency_pass,
            "interpretation": "positive anchor under the matched rollout protocol",
        },
    ]


def _stage3_boundary_table(stage3_payload: dict) -> list[dict]:
    rows = [
        row
        for row in stage3_payload["rows"]
        if row.get("role") in {"confirmatory_pass", "diagnostic_near_pass"}
    ]
    result = []
    for row in rows:
        role = row["role"]
        if role == "diagnostic_near_pass":
            interpretation = "diagnostic near-pass only; must not be pooled"
        else:
            interpretation = "boundary evidence; below matched baseline"
        result.append(
            {
                "run_name": row["run_name"],
                "role": role,
                "states": int(row["n_states"]),
                "candidates": int(row["candidate_actions"]),
                "selected_top_k": _selected_top_k(row),
                "mean_reward": _row_mean(row),
                "std_sample": _row_std_sample(row),
                "delta_vs_baseline": _row_delta(row),
                "interpretation": interpretation,
            }
        )
    return result

def _true_reward_guard_table(true_reward_guard_payload: dict) -> list[dict]:
    primary = true_reward_guard_payload["primary_guard"]
    stats = true_reward_guard_payload["primary_paired_stats"]
    guard_stats = stats["candidate_guard_summary"]
    return [
        {
            "row_id": "true_reward_margin_guard_m150_audit7x7_20seed",
            "setting": primary["setting"],
            "audit_set": primary["audit_set"],
            "switch_margin": _as_float(primary["switch_margin"]),
            "baseline_mean_reward": _as_float(primary["baseline_mean_reward"]),
            "guard_mean_reward": _as_float(primary["candidate_mean_reward"]),
            "mean_delta_vs_baseline": _as_float(stats["mean_delta"]),
            "seed_wins": int(stats["wins"]),
            "n_seeds": int(stats["n"]),
            "bootstrap_95ci_delta_lower": _as_float(stats["bootstrap_95ci_delta"][0]),
            "bootstrap_95ci_delta_upper": _as_float(stats["bootstrap_95ci_delta"][1]),
            "switch_rate": _as_float(guard_stats["switch_rate"]),
            "interpretation": (
                "current primary algorithm-readiness candidate; "
                "setting-specific guard only"
            ),
        }
    ]

def _claim_status_table(claim_audit_payload: dict) -> list[dict]:
    stage3 = claim_audit_payload["stage3"]
    dongxing = claim_audit_payload["dongxing"]
    anchor_supported = _claim_supported(
        stage3,
        "claims",
        "bishan_anchor_improves_reward_and_stability",
    )
    confirmatory_supported = _claim_supported(
        stage3,
        "claims",
        "confirmatory_50state_rows_beat_baseline",
    )
    transfer_scaling_supported = _claim_supported(
        dongxing,
        "claims",
        "return_label_scaling_improves_transfer_family",
    )
    scratch_scaling_supported = _claim_supported(
        dongxing,
        "claims",
        "return_label_scaling_improves_scratch_family",
    )
    robust_transfer_supported = _claim_supported(
        dongxing,
        "claims",
        "robust_transfer_superiority",
    )
    return [
        {
            "claim_id": "bishan_anchor",
            "claim": "Bishan 20x16/top5 reward and stability anchor",
            "status": "supported" if anchor_supported else "not supported",
            "source_derived_basis": (
                f"mean {_fmt(stage3['anchor']['mean_reward'])} versus baseline "
                f"{_fmt(stage3['baseline_reward_mean'])}; sample std "
                f"{_fmt(stage3['anchor']['std_sample'])} versus "
                f"{_fmt(stage3['baseline_reward_std_sample'])}"
            ),
            "manuscript_boundary": "Use as the positive Bishan anchor only.",
        },
        {
            "claim_id": "stage3_confirmatory_50state",
            "claim": "Stage 3 confirmatory 50-state rows beat the matched baseline",
            "status": "supported" if confirmatory_supported else "not supported",
            "source_derived_basis": "; ".join(
                f"{row['run_name']} delta {_fmt(row['reward_delta_vs_baseline'])}"
                for row in stage3["confirmatory_rows"]
            ),
            "manuscript_boundary": "Use as Stage 3 boundary evidence.",
        },
        {
            "claim_id": "diagnostic_near_pass",
            "claim": "Diagnostic near-pass row",
            "status": "not pooled",
            "source_derived_basis": (
                f"{stage3['diagnostic_near_pass']['run_name']} mean "
                f"{_fmt(stage3['diagnostic_near_pass']['mean_reward'])}, delta "
                f"{_fmt(stage3['diagnostic_near_pass']['reward_delta_vs_baseline'])}"
            ),
            "manuscript_boundary": "Report separately; must not be pooled.",
        },
        {
            "claim_id": "dongxing_return_label_scaling",
            "claim": "Dongxing/Neijiang return-label scaling",
            "status": (
                "supported descriptively"
                if transfer_scaling_supported and scratch_scaling_supported
                else "not supported"
            ),
            "source_derived_basis": (
                "transfer gain "
                f"{_fmt(dongxing['return_50x16']['transfer_gain_vs_pairwise'])}; "
                "scratch gain "
                f"{_fmt(dongxing['return_50x16']['scratch_gain_vs_pairwise'])}"
            ),
            "manuscript_boundary": "Use as calibration or stress-test evidence.",
        },
        {
            "claim_id": "robust_transfer_superiority",
            "claim": "robust transfer superiority",
            "status": "supported" if robust_transfer_supported else "not supported",
            "source_derived_basis": (
                "50x16 transfer minus scratch "
                f"{_fmt(dongxing['return_50x16']['transfer_minus_scratch'])}"
            ),
            "manuscript_boundary": "Do not use as a positive transfer claim.",
        },
    ]


def build_manuscript_result_tables_freeze(
    stage3_payload: dict,
    claim_audit_payload: dict,
    anchor_raw_audit_payload: dict,
    true_reward_guard_payload: dict,
    *,
    date: str = DATE,
    source_files: dict | None = None,
) -> dict:
    return {
        "date": date,
        "status": "source-derived table freeze",
        "source_files": source_files or {},
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "interpretation": (
                "This file freezes manuscript-facing result tables from tracked "
                "Stage 3, claim-audit, raw-rollout consistency, and true-reward guard readiness evidence."
            ),
        },
        "raw_rollout_consistency": {
            "overall_consistency_pass": bool(
                anchor_raw_audit_payload["overall_consistency_pass"]
            ),
            "summary_matches_raw": bool(
                anchor_raw_audit_payload["summary_consistency"]["matches_raw"]
            ),
            "stage3_anchor_matches_raw": bool(
                anchor_raw_audit_payload["stage3_consistency"]["matches_raw"]
            ),
        },
        "tables": {
            "table_bishan_anchor_vs_matched_baseline": _anchor_table(
                stage3_payload,
                anchor_raw_audit_payload,
            ),
            "table_stage3_boundary": _stage3_boundary_table(stage3_payload),
            "table_claim_status": _claim_status_table(claim_audit_payload),
            "table_true_reward_guard_readiness": _true_reward_guard_table(
                true_reward_guard_payload
            ),
        },
    }


def _status(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "PASS" if value else "FAIL"


def markdown_report(payload: dict) -> str:
    consistency = payload["raw_rollout_consistency"]
    consistency_status = _status(consistency["overall_consistency_pass"])
    anchor_table = payload["tables"]["table_bishan_anchor_vs_matched_baseline"]
    stage3_table = payload["tables"]["table_stage3_boundary"]
    claim_table = payload["tables"]["table_claim_status"]
    guard_table = payload["tables"]["table_true_reward_guard_readiness"]
    lines = [
        "# Paper10 manuscript result tables freeze",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived table freeze for the current Paper10 manuscript result tables.",
        "",
        "This file is derived from audited JSON evidence and does not add a new experimental claim. No rollout was rerun.",
        "",
        f"raw-rollout consistency: {consistency_status}",
        "",
        "## Source files",
        "",
    ]
    if payload["source_files"]:
        for key, value in payload["source_files"].items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- Source paths are recorded by the writer entry point.")

    lines.extend(
        [
            "",
            "## Table 1. Bishan anchor versus matched baseline",
            "",
            "| row | mean reward | sample std | delta vs baseline | raw-rollout consistency | interpretation |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for row in anchor_table:
        lines.append(
            "| {row} | {mean} | {std} | {delta} | {consistency} | {interpretation} |".format(
                row=row["row_id"],
                mean=_fmt(row["mean_reward"]),
                std=_fmt(row["std_sample"]),
                delta=_fmt(row["delta_vs_baseline"]),
                consistency=_status(row["raw_rollout_consistency_pass"]),
                interpretation=row["interpretation"],
            )
        )

    lines.extend(
        [
            "",
            "## Table 2. Stage 3 boundary rows",
            "",
            "| run | role | states | candidates | selected top_k | mean reward | sample std | delta vs baseline | interpretation |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in stage3_table:
        lines.append(
            "| {run} | {role} | {states} | {candidates} | {top_k} | {mean} | {std} | {delta} | {interpretation} |".format(
                run=row["run_name"],
                role=row["role"],
                states=row["states"],
                candidates=row["candidates"],
                top_k=row["selected_top_k"],
                mean=_fmt(row["mean_reward"]),
                std=_fmt(row["std_sample"]),
                delta=_fmt(row["delta_vs_baseline"]),
                interpretation=row["interpretation"],
            )
        )

    lines.extend(
        [
            "",
            "## Table 3. Claim status for manuscript conversion",
            "",
            "| claim | status | source-derived basis | manuscript boundary |",
            "|---|---|---|---|",
        ]
    )
    for row in claim_table:
        lines.append(
            "| {claim} | {status} | {basis} | {boundary} |".format(
                claim=row["claim"],
                status=row["status"],
                basis=row["source_derived_basis"],
                boundary=row["manuscript_boundary"],
            )
        )

    lines.extend(
        [
            "",
            "## Algorithm-readiness addendum: current true-reward guard",
            "",
            "| row | baseline mean | guard mean | mean delta | seed wins | bootstrap 95% CI lower | switch rate | interpretation |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in guard_table:
        lines.append(
            "| {row_id} | {baseline} | {guard} | {delta} | {wins} / {n} | {ci_lower} | {switch_rate} | {interpretation} |".format(
                row_id=row["row_id"],
                baseline=_fmt(row["baseline_mean_reward"]),
                guard=_fmt(row["guard_mean_reward"]),
                delta=_fmt(row["mean_delta_vs_baseline"]),
                wins=row["seed_wins"],
                n=row["n_seeds"],
                ci_lower=_fmt(row["bootstrap_95ci_delta_lower"]),
                switch_rate=_fmt(row["switch_rate"]),
                interpretation=row["interpretation"],
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- Table 1 is the only positive Bishan performance anchor in this freeze.",
            "- Table 2 is boundary evidence under the matched comparator; the diagnostic near-pass remains separate.",
            "- Table 3 preserves the claim-source audit boundary for Dongxing/Neijiang calibration and transfer wording.",
            "- The algorithm-readiness addendum is current primary guard evidence and remains a setting-specific guard only.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.manuscript_result_tables_freeze --stage3-json paper10_geojepa_mpc\\experiments\\results\\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --claim-audit-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_claim_source_consistency_audit_2026-06-18.json --anchor-raw-audit-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json --true-reward-guard-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_true_reward_guard_readiness_2026-07-08.json --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_result_tables_freeze_2026-06-19.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def write_manuscript_result_tables_freeze(
    stage3_json: str | Path,
    claim_audit_json: str | Path,
    anchor_raw_audit_json: str | Path,
    true_reward_guard_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    *,
    date: str = DATE,
) -> dict:
    stage3_path = Path(stage3_json)
    claim_path = Path(claim_audit_json)
    anchor_path = Path(anchor_raw_audit_json)
    true_reward_guard_path = Path(true_reward_guard_json)
    payload = build_manuscript_result_tables_freeze(
        stage3_payload=json.loads(stage3_path.read_text(encoding="utf-8")),
        claim_audit_payload=json.loads(claim_path.read_text(encoding="utf-8")),
        anchor_raw_audit_payload=json.loads(anchor_path.read_text(encoding="utf-8")),
        true_reward_guard_payload=json.loads(
            true_reward_guard_path.read_text(encoding="utf-8")
        ),
        date=date,
        source_files={
            "stage3_json": str(stage3_path),
            "claim_audit_json": str(claim_path),
            "anchor_raw_audit_json": str(anchor_path),
            "true_reward_guard_json": str(true_reward_guard_path),
        },
    )

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
    parser.add_argument("--stage3-json", required=True)
    parser.add_argument("--claim-audit-json", required=True)
    parser.add_argument("--anchor-raw-audit-json", required=True)
    parser.add_argument("--true-reward-guard-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_manuscript_result_tables_freeze(
        args.stage3_json,
        args.claim_audit_json,
        args.anchor_raw_audit_json,
        args.true_reward_guard_json,
        args.output_json,
        args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
