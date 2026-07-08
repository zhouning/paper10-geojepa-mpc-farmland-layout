import json
from pathlib import Path

from paper10_geojepa_mpc.experiments.figure_table_caption_claim_packet import (
    DATE,
    build_figure_table_caption_claim_packet,
    markdown_report,
    parse_args,
    write_figure_table_caption_claim_packet,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
SOURCE_COVERAGE_AUDIT = (
    RESULTS / "e0_paper10_figure_table_source_coverage_audit_2026-06-19.json"
)
RESULT_TABLES_FREEZE = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)


def _build_payload() -> dict:
    return build_figure_table_caption_claim_packet(
        source_coverage_audit_json=SOURCE_COVERAGE_AUDIT,
        result_tables_freeze_json=RESULT_TABLES_FREEZE,
        date=DATE,
    )


def test_build_caption_claim_packet_maps_all_items_with_bounded_claims():
    payload = _build_payload()

    assert payload["date"] == "2026-06-19"
    assert payload["status"] == "source-derived figure/table caption-claim packet"
    assert payload["source_boundary"]["new_experimental_claim"] is False
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert payload["caption_claim_packet_pass"] is True
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

    assert items["Main Figure 1"]["final_artwork_status"] == "pending"
    assert "workflow schematic only" in " ".join(
        items["Main Figure 1"]["allowed_claims"]
    )
    assert "final schematic artwork" in items["Main Figure 1"][
        "unresolved_manuscript_fields"
    ]

    assert "69.4705" in items["Main Figure 2"]["draft_caption"]
    assert "67.5437" in items["Main Figure 2"]["draft_caption"]
    assert "Bishan 20x16/top5" in " ".join(
        items["Main Figure 2"]["allowed_claims"]
    )

    assert "direct 50-state Bishan scale-up success" in " ".join(
        items["Main Figure 3"]["forbidden_claims"]
    )
    assert "diagnostic near-pass must not be pooled" in " ".join(
        items["Main Figure 3"]["allowed_claims"]
    )

    assert "robust Bishan-to-Dongxing transfer superiority" in " ".join(
        items["Main Figure 4"]["forbidden_claims"]
    )
    assert "calibration" in items["Main Figure 4"]["draft_caption"]

    assert "Table 1 is the only positive Bishan performance anchor" in " ".join(
        items["Main Table 2"]["allowed_claims"]
    )
    assert "Stage 3 rows are boundary evidence" in " ".join(
        items["Main Table 2"]["allowed_claims"]
    )
    assert "Algorithm-readiness addendum" in items["Main Table 2"]["draft_caption"]
    assert "72.1918" in items["Main Table 2"]["draft_caption"]
    assert "65.8876" in items["Main Table 2"]["draft_caption"]
    assert "6.3041" in items["Main Table 2"]["draft_caption"]
    assert "20 / 20" in items["Main Table 2"]["draft_caption"]
    assert "4.1401" in items["Main Table 2"]["draft_caption"]
    assert "7.7605" in items["Main Table 2"]["draft_caption"]
    assert "setting-specific guard only" in " ".join(
        items["Main Table 2"]["allowed_claims"]
    )
    assert "Do not treat the guard addendum as final submission readiness." in " ".join(
        items["Main Table 2"]["forbidden_claims"]
    )

    assert all(row["source_coverage_pass"] is True for row in payload["items"])
    assert all(row["draft_caption"].strip() for row in payload["items"])
    assert all(row["allowed_claims"] for row in payload["items"])
    assert all(row["forbidden_claims"] for row in payload["items"])
    assert all(
        len(row["unresolved_manuscript_fields"])
        == len(set(row["unresolved_manuscript_fields"]))
        for row in payload["items"]
    )


def test_caption_claim_packet_keeps_journal_and_submission_boundaries():
    payload = _build_payload()
    text = markdown_report(payload)

    assert "Paper10 figure/table caption-claim packet" in text
    assert "does not add a new experimental claim" in text
    assert "No rollout was rerun" in text
    assert "caption-claim packet: PASS" in text
    assert "submission-ready figure/table package: NO" in text
    assert "journal-neutral draft captions" in text
    assert "target-journal caption length" in text
    assert "direct 50-state Bishan scale-up success" in text
    assert "robust Bishan-to-Dongxing transfer superiority" in text
    assert "diagnostic near-pass must not be pooled" in text
    assert "Algorithm-readiness addendum" in text
    assert "72.1918" in text
    assert "20 / 20" in text
    assert "setting-specific guard only" in text
    assert "statistically significant" not in text.lower()
    assert "p value" not in text.lower()
    assert "p-value" not in text.lower()


def test_write_caption_claim_packet_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "caption_claim_packet.json"
    output_md = tmp_path / "caption_claim_packet.md"

    payload = write_figure_table_caption_claim_packet(
        source_coverage_audit_json=SOURCE_COVERAGE_AUDIT,
        result_tables_freeze_json=RESULT_TABLES_FREEZE,
        output_json=output_json,
        output_md=output_md,
        date=DATE,
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)
    assert payload["source_files"]["source_coverage_audit_json"].endswith(
        "e0_paper10_figure_table_source_coverage_audit_2026-06-19.json"
    )
    assert payload["source_files"]["result_tables_freeze_json"].endswith(
        "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
    )


def test_cli_accepts_caption_claim_packet_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "figure_table_caption_claim_packet",
            "--source-coverage-audit-json",
            "source-coverage.json",
            "--result-tables-freeze-json",
            "tables-freeze.json",
            "--output-json",
            "packet.json",
            "--output-md",
            "packet.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.source_coverage_audit_json == "source-coverage.json"
    assert args.result_tables_freeze_json == "tables-freeze.json"
    assert args.output_json == "packet.json"
    assert args.output_md == "packet.md"
    assert args.date == "2026-06-19"
