import json
from pathlib import Path

from paper10_geojepa_mpc.experiments.figure_table_source_coverage_audit import (
    DATE,
    build_figure_table_source_coverage_audit,
    markdown_report,
    parse_args,
    write_figure_table_source_coverage_audit,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
BLUEPRINT = RESULTS / "e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md"
NUMBERING_FREEZE = RESULTS / "e0_integrated_figure_table_numbering_freeze_2026-06-11.md"
SOURCE_DATA_MAP = RESULTS / "e0_source_data_map_with_dongxing_2026-06-11.md"
FRONTIER_PLOT_SCRIPT = ROOT / "scripts" / "paper10" / "plot_frontier_random050_figures.py"
DONGXING_PLOT_SCRIPT = ROOT / "scripts" / "paper10" / "plot_integrated_dongxing_figures.py"


def _build_payload() -> dict:
    return build_figure_table_source_coverage_audit(
        root=ROOT,
        blueprint_path=BLUEPRINT,
        numbering_freeze_path=NUMBERING_FREEZE,
        source_data_map_path=SOURCE_DATA_MAP,
        date=DATE,
    )


def test_build_figure_table_source_coverage_audit_maps_all_blueprint_items():
    payload = _build_payload()

    assert payload["date"] == "2026-06-19"
    assert payload["status"] == "source-derived figure/table source coverage audit"
    assert payload["source_boundary"]["new_experimental_claim"] is False
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert payload["overall_source_coverage_pass"] is True
    assert payload["submission_ready"] is False

    items = {row["item"]: row for row in payload["items"]}
    assert list(items) == [
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
    ]

    assert items["Main Figure 1"]["source_coverage_pass"] is True
    assert items["Main Figure 1"]["generation_status"] == "blocked_pending_artwork"
    assert "final schematic artwork" in items["Main Figure 1"]["unresolved_fields"]

    assert items["Main Figure 2"]["source_coverage_pass"] is True
    assert FRONTIER_PLOT_SCRIPT.relative_to(ROOT).as_posix() in items["Main Figure 2"]["generation_scripts"]
    assert (RESULTS / "e0_frontier_random050_seedwise_rewards_2026-06-09.csv").relative_to(ROOT).as_posix() in items["Main Figure 2"]["source_files"]

    assert not any(
        "true_reward_guard_readiness" in source
        for source in items["Main Figure 3"]["source_files"]
    )

    assert items["Main Figure 4"]["source_coverage_pass"] is True
    assert DONGXING_PLOT_SCRIPT.relative_to(ROOT).as_posix() in items["Main Figure 4"]["generation_scripts"]
    assert "robust Bishan-to-Dongxing transfer superiority" in " ".join(
        items["Main Figure 4"]["claim_boundaries"]
    )

    assert items["Main Table 2"]["source_coverage_pass"] is True
    assert (RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md").relative_to(ROOT).as_posix() in items["Main Table 2"]["source_files"]
    assert (RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md").relative_to(ROOT).as_posix() in items["Main Table 2"]["source_files"]
    assert (RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json").relative_to(ROOT).as_posix() in items["Main Table 2"]["source_files"]
    assert "matched-baseline rollout comparison" in items["Main Table 2"]["manuscript_job"]
    assert "Algorithm-readiness addendum" in " ".join(items["Main Table 2"]["claim_boundaries"])
    assert "setting-specific guard only" in " ".join(items["Main Table 2"]["claim_boundaries"])

    assert all(row["missing_source_files"] == [] for row in payload["items"])
    assert all(row["source_coverage_pass"] is True for row in payload["items"])


def test_markdown_report_records_figure_table_blockers_without_overclaiming():
    payload = _build_payload()
    text = markdown_report(payload)

    assert "Paper10 figure/table source coverage audit" in text
    assert "does not add a new experimental claim" in text
    assert "No rollout was rerun" in text
    assert "overall source coverage: PASS" in text
    assert "submission-ready figure/table package: NO" in text
    assert "Main Figure 1" in text
    assert "blocked_pending_artwork" in text
    assert "Main Figure 4" in text
    assert "robust Bishan-to-Dongxing transfer superiority is not supported" in text
    assert "direct 50-state Bishan scale-up success" in text
    assert "Algorithm-readiness addendum" in text
    assert "setting-specific guard only" in text
    assert "e0_paper10_true_reward_guard_readiness_2026-07-08.json" in text
    assert "statistically significant" not in text.lower()
    assert "p value" not in text.lower()


def test_write_figure_table_source_coverage_audit_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "figure_table_audit.json"
    output_md = tmp_path / "figure_table_audit.md"

    payload = write_figure_table_source_coverage_audit(
        root=ROOT,
        blueprint_path=BLUEPRINT,
        numbering_freeze_path=NUMBERING_FREEZE,
        source_data_map_path=SOURCE_DATA_MAP,
        output_json=output_json,
        output_md=output_md,
        date=DATE,
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)
    assert payload["source_files"]["blueprint"] == BLUEPRINT.relative_to(ROOT).as_posix()
    assert payload["source_files"]["numbering_freeze"] == NUMBERING_FREEZE.relative_to(ROOT).as_posix()
    assert payload["source_files"]["source_data_map"] == SOURCE_DATA_MAP.relative_to(ROOT).as_posix()


def test_cli_accepts_figure_table_source_coverage_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "figure_table_source_coverage_audit",
            "--blueprint",
            "blueprint.md",
            "--numbering-freeze",
            "freeze.md",
            "--source-data-map",
            "source-data.md",
            "--output-json",
            "audit.json",
            "--output-md",
            "audit.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.blueprint == "blueprint.md"
    assert args.numbering_freeze == "freeze.md"
    assert args.source_data_map == "source-data.md"
    assert args.output_json == "audit.json"
    assert args.output_md == "audit.md"
    assert args.date == "2026-06-19"
