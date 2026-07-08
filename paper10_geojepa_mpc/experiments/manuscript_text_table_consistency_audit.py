import argparse
import json
import re
from pathlib import Path
from typing import Iterable


DATE = "2026-06-19"

FORBIDDEN_POSITIVE_CLAIM_PATTERNS = (
    re.compile(r"\bclaim(?:s|ed|ing)?\b.{0,80}\bdirect 50-state Bishan scale-up success\b", re.IGNORECASE),
    re.compile(r"\bprove(?:s|d|n|ing)?\b.{0,80}\brobust Bishan-to-Dongxing transfer superiority\b", re.IGNORECASE),
    re.compile(r"\bsupport(?:s|ed|ing)?\b.{0,80}\brobust Bishan-to-Dongxing transfer superiority\b", re.IGNORECASE),
    re.compile(r"\bestablish(?:es|ed|ing)?\b.{0,80}\bbroad 50-state\b", re.IGNORECASE),
)
NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not"
    r"|does not"
    r"|did not"
    r"|not supported"
    r"|not support"
    r"|cannot"
    r"|must not"
    r"|prevents?"
    r"|rather than"
    r"|not as"
    r"|no prohibited"
    r"|guardrail"
    r"|\u4e0d\u652f\u6301"
    r"|\u4e0d\u80fd"
    r"|\u4e0d\u5e94"
    r"|\u4e0d\u662f"
    r")\b",
    re.IGNORECASE,
)
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


def _anchor_rows(table_freeze_payload: dict) -> tuple[dict, dict]:
    rows = table_freeze_payload["tables"]["table_bishan_anchor_vs_matched_baseline"]
    by_id = {row["row_id"]: row for row in rows}
    return (
        by_id["matched_paper9_rank_seed2028_baseline"],
        by_id["bishan_20x16_top5_frozen_anchor"],
    )


def _stage3_rows(table_freeze_payload: dict) -> tuple[list[dict], dict]:
    rows = table_freeze_payload["tables"]["table_stage3_boundary"]
    confirmatory = [row for row in rows if row["role"] == "confirmatory_pass"]
    diagnostic = [row for row in rows if row["role"] == "diagnostic_near_pass"]
    if len(confirmatory) != 2 or len(diagnostic) != 1:
        raise ValueError("Expected two confirmatory rows and one diagnostic row")
    return confirmatory, diagnostic[0]

def _guard_addendum_tokens(table_freeze_payload: dict) -> dict:
    rows = table_freeze_payload["tables"].get("table_true_reward_guard_readiness", [])
    if len(rows) != 1:
        raise ValueError("Expected exactly one true-reward guard readiness row")
    row = rows[0]
    return {
        "guard_mean_reward": _fmt(row["guard_mean_reward"]),
        "baseline_mean_reward": _fmt(row["baseline_mean_reward"]),
        "mean_delta_vs_baseline": _fmt(row["mean_delta_vs_baseline"]),
        "seed_wins": f"{row['seed_wins']} / {row['n_seeds']}",
        "bootstrap_95ci_delta_lower": _fmt(row["bootstrap_95ci_delta_lower"]),
        "legacy_text_required": False,
    }

def expected_tokens_from_table_freeze(table_freeze_payload: dict) -> dict:
    baseline, anchor = _anchor_rows(table_freeze_payload)
    confirmatory, diagnostic = _stage3_rows(table_freeze_payload)
    guard_addendum = _guard_addendum_tokens(table_freeze_payload)
    return {
        "anchor_mean": _fmt(anchor["mean_reward"]),
        "baseline_mean": _fmt(baseline["mean_reward"]),
        "anchor_std": _fmt(anchor["std_sample"]),
        "baseline_std": _fmt(baseline["std_sample"]),
        "anchor_delta": _fmt(anchor["delta_vs_baseline"]),
        "stage3_confirmatory_means": [
            _fmt(row["mean_reward"]) for row in confirmatory
        ],
        "stage3_confirmatory_deltas": [
            _fmt(abs(float(row["delta_vs_baseline"]))) for row in confirmatory
        ],
        "diagnostic_near_pass_mean": _fmt(diagnostic["mean_reward"]),
        "diagnostic_near_pass_delta": _fmt(abs(float(diagnostic["delta_vs_baseline"]))),
        "algorithm_readiness_addendum": guard_addendum,
    }


def _required_tokens(expected: dict) -> list[str]:
    return [
        expected["anchor_mean"],
        expected["baseline_mean"],
        expected["anchor_std"],
        expected["baseline_std"],
        *expected["stage3_confirmatory_means"],
        expected["diagnostic_near_pass_mean"],
    ]


def _boundary_tokens() -> list[str]:
    return [
        "must not be pooled",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
    ]


def _line_hits(pattern: re.Pattern, text: str) -> list[dict]:
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            hits.append(
                {
                    "line": line_no,
                    "match": match.group(0),
                    "text": line.strip(),
                }
            )
    return hits


def _positive_claim_hits(text: str) -> list[dict]:
    hits = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        context = " ".join(lines[max(0, index - 1) : min(len(lines), index + 2)])
        if NEGATIVE_GUARDRAIL.search(context):
            continue
        for pattern in FORBIDDEN_POSITIVE_CLAIM_PATTERNS:
            match = pattern.search(line)
            if match:
                hits.append(
                    {
                        "line": index + 1,
                        "match": match.group(0),
                        "text": line.strip(),
                    }
                )
    return hits


def _document_audit(document: str, text: str, expected: dict) -> dict:
    required = _required_tokens(expected)
    boundaries = _boundary_tokens()
    missing_required = [token for token in required if token not in text]
    matched_boundaries = [token for token in boundaries if token in text]
    missing_boundaries = [token for token in boundaries if token not in text]
    positive_hits = _positive_claim_hits(text)
    inferential_hits = _line_hits(UNSUPPORTED_INFERENTIAL_STATS_PATTERN, text)
    return {
        "document": document,
        "required_numeric_tokens": required,
        "missing_required_tokens": missing_required,
        "matched_boundary_tokens": matched_boundaries,
        "missing_boundary_tokens": missing_boundaries,
        "forbidden_positive_claim_hits": positive_hits,
        "unsupported_inferential_hits": inferential_hits,
        "consistent_with_table_freeze": not missing_required
        and not missing_boundaries
        and not positive_hits
        and not inferential_hits,
    }


def build_manuscript_text_table_consistency_audit(
    table_freeze_payload: dict,
    document_payloads: Iterable[tuple[str, str]],
    *,
    date: str = DATE,
    source_files: dict | None = None,
) -> dict:
    expected = expected_tokens_from_table_freeze(table_freeze_payload)
    documents = [
        _document_audit(document, text, expected)
        for document, text in document_payloads
    ]
    return {
        "date": date,
        "status": "source-derived manuscript text/table consistency audit",
        "source_files": source_files or {},
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "interpretation": (
                "This audit checks manuscript/proposal text against the frozen "
                "source-derived result tables. It reports consistency only."
            ),
        },
        "expected_tokens": expected,
        "documents": documents,
        "overall_consistency_pass": all(
            row["consistent_with_table_freeze"] for row in documents
        ),
    }


def _status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def markdown_report(payload: dict) -> str:
    expected = payload["expected_tokens"]
    lines = [
        "# Paper10 manuscript text/table consistency audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived manuscript text/table consistency audit.",
        "",
        "This audit checks current manuscript-facing text against the frozen result tables and does not add a new experimental claim. No rollout was rerun.",
        "",
        f"overall consistency: {_status(payload['overall_consistency_pass'])}",
        "",
        "## Source files",
        "",
    ]
    if payload["source_files"]:
        lines.append(
            f"- table freeze JSON: `{payload['source_files'].get('table_freeze_json', '')}`"
        )
        for document in payload["source_files"].get("documents", []):
            lines.append(f"- document: `{document}`")
    else:
        lines.append("- Source paths are recorded by the writer entry point.")

    lines.extend(
        [
            "",
            "## Frozen tokens checked",
            "",
            "| item | token |",
            "|---|---|",
            f"| Bishan anchor mean | {expected['anchor_mean']} |",
            f"| matched baseline mean | {expected['baseline_mean']} |",
            f"| Bishan anchor sample std | {expected['anchor_std']} |",
            f"| matched baseline sample std | {expected['baseline_std']} |",
            f"| Stage 3 confirmatory means | {', '.join(expected['stage3_confirmatory_means'])} |",
            f"| diagnostic near-pass mean | {expected['diagnostic_near_pass_mean']} |",
            (
                "| algorithm-readiness addendum | guard "
                f"{expected['algorithm_readiness_addendum']['guard_mean_reward']} "
                "vs baseline "
                f"{expected['algorithm_readiness_addendum']['baseline_mean_reward']}; "
                "delta "
                f"{expected['algorithm_readiness_addendum']['mean_delta_vs_baseline']}; "
                "seed wins "
                f"{expected['algorithm_readiness_addendum']['seed_wins']}; "
                "bootstrap 95% CI lower "
                f"{expected['algorithm_readiness_addendum']['bootstrap_95ci_delta_lower']}; "
                "not required in legacy text until manuscript refresh |"
            ),
            f"| boundary guardrails | {', '.join(_boundary_tokens())} |",
            "",
            "## Document audit",
            "",
            "| document | status | missing numeric tokens | missing boundary tokens | forbidden positive hits | unsupported inferential hits |",
            "|---|---|---|---|---:|---:|",
        ]
    )
    for row in payload["documents"]:
        lines.append(
            "| {document} | {status} | {missing_numbers} | {missing_boundaries} | {positive} | {inferential} |".format(
                document=row["document"],
                status=_status(row["consistent_with_table_freeze"]),
                missing_numbers=", ".join(row["missing_required_tokens"]) or "none",
                missing_boundaries=", ".join(row["missing_boundary_tokens"]) or "none",
                positive=len(row["forbidden_positive_claim_hits"]),
                inferential=len(row["unsupported_inferential_hits"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- PASS means the checked manuscript-facing text contains the frozen table numbers and required boundary guardrails.",
            "- PASS does not mean the formal manuscript is ready for submission.",
            "- Any future text edit that changes these numbers or turns a boundary into a positive claim should update the freeze or fail preflight.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.manuscript_text_table_consistency_audit --table-freeze-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --document paper10_geojepa_mpc\\experiments\\results\\e0_ceus_stage3_manuscript_draft_2026-06-18.md --document paper10_geojepa_mpc\\experiments\\results\\e0_ceus_stage3_manuscript_reframe_2026-06-18.md --document paper10_geojepa_mpc\\experiments\\results\\e0_paper10_project_proposal_opening_report_2026-06-18.md --document paper10_geojepa_mpc\\experiments\\results\\e0_paper10_author_decision_matrix_2026-06-18.md --document paper10_geojepa_mpc\\experiments\\results\\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def write_manuscript_text_table_consistency_audit(
    table_freeze_json: str | Path,
    document_paths: Iterable[str | Path],
    output_json: str | Path,
    output_md: str | Path,
    *,
    date: str = DATE,
) -> dict:
    table_path = Path(table_freeze_json)
    document_path_values = [Path(path) for path in document_paths]
    payload = build_manuscript_text_table_consistency_audit(
        table_freeze_payload=json.loads(table_path.read_text(encoding="utf-8")),
        document_payloads=[
            (str(path), path.read_text(encoding="utf-8"))
            for path in document_path_values
        ],
        date=date,
        source_files={
            "table_freeze_json": str(table_path),
            "documents": [str(path) for path in document_path_values],
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
    parser.add_argument("--table-freeze-json", required=True)
    parser.add_argument("--document", action="append", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_manuscript_text_table_consistency_audit(
        args.table_freeze_json,
        args.document,
        args.output_json,
        args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
