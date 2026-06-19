import argparse
import json
import re
from pathlib import Path


DATE = "2026-06-19"

UNSUPPORTED_INFERENTIAL_STATS_PATTERN = re.compile(
    r"statistically significant"
    r"|significant at"
    r"|\bp\s*[<=>]\s*\d"
    r"|p-value"
    r"|p value"
    r"|confidence interval"
    r"|formal superiority"
    r"|non[- ]inferiority"
    r"|equivalence test",
    re.IGNORECASE,
)


def _fmt(value: float | int | str) -> str:
    return f"{float(value):.4f}"


def _claim_row(result_tables: dict, claim_id: str) -> dict:
    matches = [
        row
        for row in result_tables["tables"]["table_claim_status"]
        if row["claim_id"] == claim_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one claim row for {claim_id}")
    return matches[0]


def _anchor_rows(result_tables: dict) -> tuple[dict, dict]:
    rows = result_tables["tables"]["table_bishan_anchor_vs_matched_baseline"]
    baseline = [row for row in rows if row["row_id"] == "matched_paper9_rank_seed2028_baseline"]
    anchor = [row for row in rows if row["row_id"] == "bishan_20x16_top5_frozen_anchor"]
    if len(baseline) != 1 or len(anchor) != 1:
        raise ValueError("Expected exactly one baseline row and one Bishan anchor row")
    return baseline[0], anchor[0]


def _stage3_rows(result_tables: dict) -> list[dict]:
    return result_tables["tables"]["table_stage3_boundary"]


def _source_item(source_coverage: dict, item: str) -> dict:
    matches = [row for row in source_coverage["items"] if row["item"] == item]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one source coverage row for {item}")
    return matches[0]


def _unique_ordered(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _base_packet_row(source_row: dict, *, placement: str, caption: str, allowed: list[str], forbidden: list[str]) -> dict:
    return {
        "item": source_row["item"],
        "placement": placement,
        "source_coverage_pass": bool(source_row["source_coverage_pass"]),
        "generation_status": source_row["generation_status"],
        "final_artwork_status": (
            "pending"
            if source_row["generation_status"] == "blocked_pending_artwork"
            else "preview_available"
        ),
        "source_files": list(source_row["source_files"]),
        "generation_scripts": list(source_row["generation_scripts"]),
        "draft_caption": caption,
        "allowed_claims": allowed,
        "forbidden_claims": forbidden,
        "unresolved_manuscript_fields": _unique_ordered(
            list(source_row["unresolved_fields"])
            + ["target-journal caption length"]
        ),
    }


def _build_item_rows(source_coverage: dict, result_tables: dict) -> list[dict]:
    baseline, anchor = _anchor_rows(result_tables)
    stage3 = _stage3_rows(result_tables)
    stage3_caption = "; ".join(
        f"{row['run_name']} mean {_fmt(row['mean_reward'])} "
        f"delta {_fmt(row['delta_vs_baseline'])}"
        for row in stage3
    )
    bishan_claim = _claim_row(result_tables, "bishan_anchor")
    stage3_claim = _claim_row(result_tables, "stage3_confirmatory_50state")
    diagnostic_claim = _claim_row(result_tables, "diagnostic_near_pass")
    dongxing_claim = _claim_row(result_tables, "dongxing_return_label_scaling")
    robust_transfer_claim = _claim_row(result_tables, "robust_transfer_superiority")

    return [
        _base_packet_row(
            _source_item(source_coverage, "Main Figure 1"),
            placement="main",
            caption=(
                "Journal-neutral draft caption: monitor-gated value labels pass "
                "through label generation, monitor checks, value-filter training, "
                "candidate filtering, and masked MPC rollout before manuscript "
                "claims are accepted."
            ),
            allowed=[
                "workflow schematic only; no new quantitative result",
                "monitor gates control escalation before value-filter training",
            ],
            forbidden=[
                "Do not describe the workflow schematic as experimental evidence.",
                "Do not claim irregular cadastral deployment is solved.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Figure 2"),
            placement="main",
            caption=(
                "Journal-neutral draft caption: Bishan 20x16/top5 is the "
                "positive anchor under the tested matched rollout protocol, "
                f"with mean reward {_fmt(anchor['mean_reward'])} versus "
                f"{_fmt(baseline['mean_reward'])} for the matched comparator "
                f"and sample standard deviation {_fmt(anchor['std_sample'])} "
                f"versus {_fmt(baseline['std_sample'])}."
            ),
            allowed=[
                "Bishan 20x16/top5 is the positive anchor only under the tested rollout protocol",
                bishan_claim["manuscript_boundary"],
            ],
            forbidden=[
                "Do not generalize this panel to direct 50-state Bishan scale-up success.",
                "Do not describe the difference with inferential testing language.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Figure 3"),
            placement="main_or_supplement_pending_journal_limit",
            caption=(
                "Journal-neutral draft caption: Stage 3 completed 50-state "
                "boundary rows but did not support a direct positive scale-up "
                f"claim under the matched comparator ({stage3_caption}). The "
                "diagnostic near-pass must not be pooled with confirmatory rows."
            ),
            allowed=[
                stage3_claim["manuscript_boundary"],
                diagnostic_claim["manuscript_boundary"],
                "diagnostic near-pass must not be pooled",
            ],
            forbidden=[
                "direct 50-state Bishan scale-up success",
                "Do not pool the diagnostic near-pass with confirmatory rows.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Figure 4"),
            placement="main",
            caption=(
                "Journal-neutral draft caption: Dongxing/Neijiang return-label "
                "scaling provides calibration and stress-test evidence; the "
                f"50x16 transfer-minus-scratch value is {_fmt(float(robust_transfer_claim['source_derived_basis'].split()[-1]))}, "
                "so this panel must not be written as robust transfer superiority."
            ),
            allowed=[
                dongxing_claim["manuscript_boundary"],
                "Dongxing/Neijiang supports calibration and stress-test value",
            ],
            forbidden=[
                "robust Bishan-to-Dongxing transfer superiority",
                robust_transfer_claim["manuscript_boundary"],
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Supplementary Figure S1"),
            placement="supplementary_pending_journal_limit",
            caption=(
                "Journal-neutral draft caption: Dongxing low-label stress-test "
                "results show mixed transfer behavior and should be used as "
                "boundary context rather than a robust superiority claim."
            ),
            allowed=[
                "low-label transfer behavior is mixed",
                "use as supplementary stress-test context unless journal limits require another placement",
            ],
            forbidden=[
                "Do not claim low-label transfer superiority is robust.",
                "Do not convert this supplementary stress test into a main positive result without updating the source map.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Table 1"),
            placement="main",
            caption=(
                "Journal-neutral draft caption: monitor-selected Bishan gates "
                "summarize which label settings were allowed to advance to "
                "manuscript-facing value-filter testing."
            ),
            allowed=[
                "monitor gates authorize escalation; they do not prove general scale-up",
                "use gate status as evidence-control context",
            ],
            forbidden=[
                "Do not claim monitor acceptance proves deployment readiness.",
                "Do not treat gate selection as an independent performance experiment.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Table 2"),
            placement="main",
            caption=(
                "Journal-neutral draft caption: frozen matched-baseline table "
                "reports the positive Bishan anchor and Stage 3 boundary rows "
                "using tracked Stage 3 and raw-rollout consistency evidence."
            ),
            allowed=[
                "Table 1 is the only positive Bishan performance anchor",
                "Stage 3 rows are boundary evidence",
                "diagnostic near-pass must not be pooled",
            ],
            forbidden=[
                "Do not rewrite Stage 3 boundary rows as direct 50-state Bishan scale-up success.",
                "Do not add unsupported comparison-testing wording to the frozen table.",
            ],
        ),
        _base_packet_row(
            _source_item(source_coverage, "Main Table 3"),
            placement="main_or_supplement_pending_journal_limit",
            caption=(
                "Journal-neutral draft caption: Dongxing return-label scaling "
                "summarizes descriptive calibration evidence and keeps robust "
                "transfer superiority unsupported."
            ),
            allowed=[
                "return-label scaling is descriptive calibration evidence",
                dongxing_claim["manuscript_boundary"],
            ],
            forbidden=[
                "robust Bishan-to-Dongxing transfer superiority",
                "Do not treat descriptive Dongxing scaling as a confirmatory transfer test.",
            ],
        ),
    ]


def _contains_unsupported_stats(text: str) -> bool:
    return bool(UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(text))


def build_figure_table_caption_claim_packet(
    *,
    source_coverage_audit_json: str | Path,
    result_tables_freeze_json: str | Path,
    date: str = DATE,
) -> dict:
    source_path = Path(source_coverage_audit_json)
    table_path = Path(result_tables_freeze_json)
    source_coverage = json.loads(source_path.read_text(encoding="utf-8"))
    result_tables = json.loads(table_path.read_text(encoding="utf-8"))

    item_rows = _build_item_rows(source_coverage, result_tables)
    rendered_text = "\n".join(
        " ".join(
            [
                row["draft_caption"],
                " ".join(row["allowed_claims"]),
                " ".join(row["forbidden_claims"]),
            ]
        )
        for row in item_rows
    )
    packet_pass = (
        source_coverage["overall_source_coverage_pass"] is True
        and all(row["source_coverage_pass"] for row in item_rows)
        and all(row["draft_caption"].strip() for row in item_rows)
        and all(row["allowed_claims"] for row in item_rows)
        and all(row["forbidden_claims"] for row in item_rows)
        and not _contains_unsupported_stats(rendered_text)
    )
    return {
        "date": date,
        "status": "source-derived figure/table caption-claim packet",
        "source_files": {
            "source_coverage_audit_json": source_path.as_posix(),
            "result_tables_freeze_json": table_path.as_posix(),
        },
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "interpretation": (
                "This packet converts source-covered figure/table items into "
                "journal-neutral draft captions and claim boundaries. It does "
                "not select a target journal or create final figure exports."
            ),
        },
        "items": item_rows,
        "caption_claim_packet_pass": packet_pass,
        "submission_ready": False,
        "submission_blockers": [
            "target-journal caption length",
            "final figure/table export package",
            "final schematic artwork for Main Figure 1",
            "final main-versus-supplementary placement",
        ],
    }


def _status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def markdown_report(payload: dict) -> str:
    lines = [
        "# Paper10 figure/table caption-claim packet",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived figure/table caption-claim packet.",
        "",
        "This packet provides journal-neutral draft captions and bounded claim wording for source-covered figure/table items. It does not add a new experimental claim. No rollout was rerun.",
        "",
        f"caption-claim packet: {_status(payload['caption_claim_packet_pass'])}",
        "submission-ready figure/table package: NO",
        "",
        "## Source files",
        "",
    ]
    for key, value in payload["source_files"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Journal-neutral draft captions and claim boundaries",
            "",
            "| item | placement | final artwork | draft caption | allowed claims | forbidden claims | unresolved manuscript fields |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["items"]:
        lines.append(
            "| {item} | {placement} | {artwork} | {caption} | {allowed} | {forbidden} | {unresolved} |".format(
                item=row["item"],
                placement=row["placement"],
                artwork=row["final_artwork_status"],
                caption=row["draft_caption"],
                allowed="<br>".join(row["allowed_claims"]),
                forbidden="<br>".join(row["forbidden_claims"]),
                unresolved="<br>".join(row["unresolved_manuscript_fields"]),
            )
        )

    lines.extend(
        [
            "",
            "## Submission blockers",
            "",
        ]
    )
    for blocker in payload["submission_blockers"]:
        lines.append(f"- {blocker}")

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- PASS means every source-covered figure/table item has a draft caption, allowed claims, forbidden claims, and unresolved manuscript fields.",
            "- PASS does not mean the formal manuscript is ready for submission.",
            "- Do not claim direct 50-state Bishan scale-up success.",
            "- Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "- The diagnostic near-pass must not be pooled with confirmatory rows.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.figure_table_caption_claim_packet --source-coverage-audit-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_figure_table_source_coverage_audit_2026-06-19.json --result-tables-freeze-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_figure_table_caption_claim_packet_2026-06-19.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_figure_table_caption_claim_packet_2026-06-19.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def write_figure_table_caption_claim_packet(
    *,
    source_coverage_audit_json: str | Path,
    result_tables_freeze_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict:
    payload = build_figure_table_caption_claim_packet(
        source_coverage_audit_json=source_coverage_audit_json,
        result_tables_freeze_json=result_tables_freeze_json,
        date=date,
    )

    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    output_md_path = Path(output_md)
    output_md_path.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-coverage-audit-json", required=True)
    parser.add_argument("--result-tables-freeze-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_figure_table_caption_claim_packet(
        source_coverage_audit_json=args.source_coverage_audit_json,
        result_tables_freeze_json=args.result_tables_freeze_json,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
