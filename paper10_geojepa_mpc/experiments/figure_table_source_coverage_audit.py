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


def _posix(path: Path) -> str:
    return path.as_posix()


def _results(*parts: str) -> str:
    return _posix(Path("paper10_geojepa_mpc") / "experiments" / "results" / Path(*parts))


def _script(*parts: str) -> str:
    return _posix(Path("scripts") / "paper10" / Path(*parts))


FIGURE_TABLE_CONTRACTS = [
    {
        "item": "Main Figure 1",
        "manuscript_job": "Explain monitor-gated value filtering workflow.",
        "source_files": [
            _posix(Path("paper10_geojepa_mpc") / "experiments" / "value_label_generation.py"),
            _posix(Path("paper10_geojepa_mpc") / "experiments" / "value_label_monitor.py"),
            _posix(Path("paper10_geojepa_mpc") / "experiments" / "run_e0_value_head_train.py"),
            _posix(Path("paper10_geojepa_mpc") / "experiments" / "run_e0_env_rollout_smoke.py"),
            _results("e0_frontier_random050_figure_plan_2026-06-09.md"),
            _results("e0_integrated_dongxing_figure_plan_2026-06-11.md"),
        ],
        "generation_scripts": [],
        "generation_status": "blocked_pending_artwork",
        "unresolved_fields": [
            "final schematic artwork",
            "journal figure dimensions",
        ],
        "claim_boundaries": [
            "workflow schematic only; no new quantitative result",
        ],
    },
    {
        "item": "Main Figure 2",
        "manuscript_job": "Show Bishan 20x16/top5 reward and stability.",
        "source_files": [
            _results("e0_frontier_random050_seedwise_rewards_2026-06-09.csv"),
            _results("e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json"),
            _results("e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json"),
        ],
        "generation_scripts": [
            _script("plot_frontier_random050_figures.py"),
        ],
        "generation_status": "scripted_preview_available",
        "unresolved_fields": [
            "final figure number",
            "inset decision",
        ],
        "claim_boundaries": [
            "Bishan 20x16/top5 is the positive anchor only under the tested rollout protocol",
        ],
    },
    {
        "item": "Main Figure 3",
        "manuscript_job": "Show Stage 3 50-state boundary.",
        "source_files": [
            _results("e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md"),
            _results("e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"),
            _results("e0_frontier_random050_topk_diagnostics_2026-06-09.csv"),
            _results("e0_windows_frontier_random050_ablation_findings_2026-06-09.md"),
            _results("e0_macos_gpkg_reproduction_findings_2026-06-09.md"),
        ],
        "generation_scripts": [
            _script("plot_frontier_random050_figures.py"),
        ],
        "generation_status": "scripted_preview_available",
        "unresolved_fields": [
            "final main-versus-supplementary placement",
        ],
        "claim_boundaries": [
            "direct 50-state Bishan scale-up success is not supported",
            "diagnostic near-pass must not be pooled",
        ],
    },
    {
        "item": "Main Figure 4",
        "manuscript_job": "Show Dongxing return-label scaling.",
        "source_files": [
            _results("e0_dongxing_return_label_family_summary_2026-06-10.csv"),
            _results("e0_dongxing_return_label_50x16_family_2026-06-10.md"),
            _results("e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"),
            _results("e0_source_data_map_with_dongxing_2026-06-11.md"),
        ],
        "generation_scripts": [
            _script("plot_integrated_dongxing_figures.py"),
        ],
        "generation_status": "scripted_preview_available",
        "unresolved_fields": [
            "final figure number",
            "metric panel placement",
        ],
        "claim_boundaries": [
            "robust Bishan-to-Dongxing transfer superiority is not supported",
            "Dongxing/Neijiang supports calibration and stress-test value",
        ],
    },
    {
        "item": "Supplementary Figure S1",
        "manuscript_job": "Show Dongxing low-label stress test.",
        "source_files": [
            _results("e0_dongxing_low_label_budget_family_summary_2026-06-10.csv"),
            _results("e0_dongxing_low_label_budget_family_2026-06-10.md"),
            _results("e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"),
            _results("e0_source_data_map_with_dongxing_2026-06-11.md"),
        ],
        "generation_scripts": [
            _script("plot_integrated_dongxing_figures.py"),
        ],
        "generation_status": "scripted_preview_available",
        "unresolved_fields": [
            "final main-versus-supplementary placement",
            "target-journal caption length",
        ],
        "claim_boundaries": [
            "low-label transfer superiority is mixed and not robustly supported",
        ],
    },
    {
        "item": "Main Table 1",
        "manuscript_job": "Summarize monitor-selected Bishan gates.",
        "source_files": [
            _results("e0_value_label_monitor_frontier_random050_10x12_h5_seed43_top4.json"),
            _results("e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json"),
            _results("e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"),
        ],
        "generation_scripts": [],
        "generation_status": "table_source_available",
        "unresolved_fields": [
            "final table number",
        ],
        "claim_boundaries": [
            "monitor gates authorize escalation; they do not prove general scale-up",
        ],
    },
    {
        "item": "Main Table 2",
        "manuscript_job": "Summarize matched-baseline rollout comparison.",
        "source_files": [
            _results("e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"),
            _results("e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"),
            _results("e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md"),
            _results("e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"),
        ],
        "generation_scripts": [],
        "generation_status": "frozen_table_available",
        "unresolved_fields": [
            "rounding",
            "main-text placement",
        ],
        "claim_boundaries": [
            "Table 1 of the freeze is the only positive Bishan performance anchor",
            "Stage 3 rows are boundary evidence",
        ],
    },
    {
        "item": "Main Table 3",
        "manuscript_job": "Summarize Dongxing return-label scaling.",
        "source_files": [
            _results("e0_dongxing_return_label_family_summary_2026-06-10.csv"),
            _results("e0_dongxing_return_label_50x16_family_2026-06-10.md"),
            _results("e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"),
        ],
        "generation_scripts": [],
        "generation_status": "table_source_available",
        "unresolved_fields": [
            "whether full metric table is main text",
        ],
        "claim_boundaries": [
            "return-label scaling is descriptive calibration evidence",
            "robust Bishan-to-Dongxing transfer superiority is not supported",
        ],
    },
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _relative_or_posix(path: Path, root: Path) -> str:
    try:
        return _posix(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _check_text_tokens(text_by_source: dict[str, str], tokens: list[str]) -> list[str]:
    combined = "\n".join(text_by_source.values())
    return [token for token in tokens if token not in combined]


def _audit_item(root: Path, item: dict) -> dict:
    source_files = list(item["source_files"])
    generation_scripts = list(item["generation_scripts"])
    paths_to_check = source_files + generation_scripts
    missing_source_files = [
        path for path in source_files if not (root / path).exists()
    ]
    missing_generation_scripts = [
        path for path in generation_scripts if not (root / path).exists()
    ]
    return {
        "item": item["item"],
        "manuscript_job": item["manuscript_job"],
        "source_files": source_files,
        "generation_scripts": generation_scripts,
        "generation_status": item["generation_status"],
        "unresolved_fields": list(item["unresolved_fields"]),
        "claim_boundaries": list(item["claim_boundaries"]),
        "missing_source_files": missing_source_files,
        "missing_generation_scripts": missing_generation_scripts,
        "checked_path_count": len(paths_to_check),
        "source_coverage_pass": not missing_source_files
        and not missing_generation_scripts,
    }


def build_figure_table_source_coverage_audit(
    *,
    root: str | Path,
    blueprint_path: str | Path,
    numbering_freeze_path: str | Path,
    source_data_map_path: str | Path,
    date: str = DATE,
) -> dict:
    root_path = Path(root)
    blueprint = Path(blueprint_path)
    numbering_freeze = Path(numbering_freeze_path)
    source_data_map = Path(source_data_map_path)
    source_texts = {
        _relative_or_posix(blueprint, root_path): _read(blueprint),
        _relative_or_posix(numbering_freeze, root_path): _read(numbering_freeze),
        _relative_or_posix(source_data_map, root_path): _read(source_data_map),
    }

    item_rows = [_audit_item(root_path, item) for item in FIGURE_TABLE_CONTRACTS]
    expected_items = [item["item"] for item in FIGURE_TABLE_CONTRACTS]
    missing_blueprint_items = [
        item for item in expected_items if item not in source_texts[_relative_or_posix(blueprint, root_path)]
    ]
    missing_freeze_items = [
        item for item in expected_items if item not in source_texts[_relative_or_posix(numbering_freeze, root_path)]
    ]
    required_boundary_tokens = [
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "derived summary CSVs can support figure/source-data review",
        "final figure/table export package",
    ]
    missing_boundary_tokens = _check_text_tokens(source_texts, required_boundary_tokens)

    overall_pass = (
        all(row["source_coverage_pass"] for row in item_rows)
        and not missing_blueprint_items
        and not missing_freeze_items
        and not missing_boundary_tokens
    )
    return {
        "date": date,
        "status": "source-derived figure/table source coverage audit",
        "source_files": {
            "blueprint": _relative_or_posix(blueprint, root_path),
            "numbering_freeze": _relative_or_posix(numbering_freeze, root_path),
            "source_data_map": _relative_or_posix(source_data_map, root_path),
        },
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "interpretation": (
                "This audit checks whether the current figure/table assembly "
                "map has tracked source data, scripts, and explicit blockers."
            ),
        },
        "items": item_rows,
        "coverage_checks": {
            "expected_items": expected_items,
            "missing_blueprint_items": missing_blueprint_items,
            "missing_numbering_freeze_items": missing_freeze_items,
            "missing_boundary_tokens": missing_boundary_tokens,
        },
        "overall_source_coverage_pass": overall_pass,
        "submission_ready": False,
        "submission_blockers": [
            "final schematic artwork for Main Figure 1",
            "target-journal figure dimensions and export formats",
            "final main-versus-supplementary placement",
            "journal-specific captions and table placement",
        ],
    }


def _status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def markdown_report(payload: dict) -> str:
    lines = [
        "# Paper10 figure/table source coverage audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived figure/table source coverage audit.",
        "",
        "This audit checks current manuscript figure/table assembly sources and does not add a new experimental claim. No rollout was rerun.",
        "",
        f"overall source coverage: {_status(payload['overall_source_coverage_pass'])}",
        "submission-ready figure/table package: NO",
        "",
        "## Source files",
        "",
    ]
    for key, path in payload["source_files"].items():
        lines.append(f"- {key}: `{path}`")

    lines.extend(
        [
            "",
            "## Figure/table source coverage",
            "",
            "| item | coverage | generation status | source files | generation scripts | unresolved fields | claim boundaries |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["items"]:
        lines.append(
            "| {item} | {coverage} | {status} | {sources} | {scripts} | {unresolved} | {boundaries} |".format(
                item=row["item"],
                coverage=_status(row["source_coverage_pass"]),
                status=row["generation_status"],
                sources=", ".join(f"`{path}`" for path in row["source_files"]),
                scripts=", ".join(f"`{path}`" for path in row["generation_scripts"])
                or "none",
                unresolved=", ".join(row["unresolved_fields"]) or "none",
                boundaries=", ".join(row["claim_boundaries"]) or "none",
            )
        )

    lines.extend(
        [
            "",
            "## Coverage checks",
            "",
            f"- Missing blueprint items: {', '.join(payload['coverage_checks']['missing_blueprint_items']) or 'none'}",
            f"- Missing numbering-freeze items: {', '.join(payload['coverage_checks']['missing_numbering_freeze_items']) or 'none'}",
            f"- Missing boundary tokens: {', '.join(payload['coverage_checks']['missing_boundary_tokens']) or 'none'}",
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
            "- PASS means the current figure/table assembly map has tracked source files and explicit unresolved export fields.",
            "- PASS does not mean the formal manuscript is ready for submission.",
            "- Main Figure 3 must not be used to claim direct 50-state Bishan scale-up success.",
            "- Main Figure 4 and Main Table 3 must not be used to claim robust Bishan-to-Dongxing transfer superiority.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.figure_table_source_coverage_audit --blueprint paper10_geojepa_mpc\\experiments\\results\\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md --numbering-freeze paper10_geojepa_mpc\\experiments\\results\\e0_integrated_figure_table_numbering_freeze_2026-06-11.md --source-data-map paper10_geojepa_mpc\\experiments\\results\\e0_source_data_map_with_dongxing_2026-06-11.md --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_figure_table_source_coverage_audit_2026-06-19.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_figure_table_source_coverage_audit_2026-06-19.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def write_figure_table_source_coverage_audit(
    *,
    root: str | Path,
    blueprint_path: str | Path,
    numbering_freeze_path: str | Path,
    source_data_map_path: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict:
    payload = build_figure_table_source_coverage_audit(
        root=root,
        blueprint_path=blueprint_path,
        numbering_freeze_path=numbering_freeze_path,
        source_data_map_path=source_data_map_path,
        date=date,
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
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2])
    parser.add_argument("--blueprint", required=True)
    parser.add_argument("--numbering-freeze", required=True)
    parser.add_argument("--source-data-map", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_figure_table_source_coverage_audit(
        root=args.root,
        blueprint_path=args.blueprint,
        numbering_freeze_path=args.numbering_freeze,
        source_data_map_path=args.source_data_map,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
