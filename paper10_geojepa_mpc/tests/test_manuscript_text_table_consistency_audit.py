import json
from pathlib import Path

from paper10_geojepa_mpc.experiments.manuscript_text_table_consistency_audit import (
    DATE,
    build_manuscript_text_table_consistency_audit,
    markdown_report,
    parse_args,
    write_manuscript_text_table_consistency_audit,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
TABLE_FREEZE = RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
DOCUMENTS = [
    RESULTS / "e0_ceus_stage3_manuscript_draft_2026-06-18.md",
    RESULTS / "e0_ceus_stage3_manuscript_reframe_2026-06-18.md",
    RESULTS / "e0_paper10_project_proposal_opening_report_2026-06-18.md",
    RESULTS / "e0_paper10_author_decision_matrix_2026-06-18.md",
    RESULTS / "e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _doc_payloads() -> list[tuple[str, str]]:
    return [(str(path), path.read_text(encoding="utf-8")) for path in DOCUMENTS]


def test_build_manuscript_text_table_consistency_audit_checks_core_documents():
    payload = build_manuscript_text_table_consistency_audit(
        table_freeze_payload=_load(TABLE_FREEZE),
        document_payloads=_doc_payloads(),
        date=DATE,
    )

    assert payload["date"] == "2026-06-19"
    assert payload["status"] == "source-derived manuscript text/table consistency audit"
    assert payload["source_boundary"]["new_experimental_claim"] is False
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert payload["overall_consistency_pass"] is True
    assert payload["expected_tokens"]["anchor_mean"] == "69.4705"
    assert payload["expected_tokens"]["baseline_mean"] == "67.5437"
    assert payload["expected_tokens"]["anchor_std"] == "1.0004"
    assert payload["expected_tokens"]["baseline_std"] == "7.2246"
    assert payload["expected_tokens"]["stage3_confirmatory_means"] == [
        "64.2960",
        "66.2544",
    ]
    assert payload["expected_tokens"]["diagnostic_near_pass_mean"] == "67.4913"
    guard = payload["expected_tokens"]["algorithm_readiness_addendum"]
    assert guard["guard_mean_reward"] == "72.1773"
    assert guard["baseline_mean_reward"] == "65.8876"
    assert guard["mean_delta_vs_baseline"] == "6.2897"
    assert guard["seed_wins"] == "20 / 20"
    assert guard["bootstrap_95ci_delta_lower"] == "4.1643"
    assert guard["legacy_text_required"] is False

    assert [row["document"] for row in payload["documents"]] == [
        str(path) for path in DOCUMENTS
    ]
    for row in payload["documents"]:
        assert row["consistent_with_table_freeze"] is True
        assert row["missing_required_tokens"] == []
        assert row["forbidden_positive_claim_hits"] == []
        assert row["unsupported_inferential_hits"] == []

    draft = payload["documents"][0]
    assert "must not be pooled" in draft["matched_boundary_tokens"]
    assert "robust Bishan-to-Dongxing transfer superiority" in draft["matched_boundary_tokens"]


def test_markdown_report_summarizes_pass_and_claim_boundaries():
    payload = build_manuscript_text_table_consistency_audit(
        table_freeze_payload=_load(TABLE_FREEZE),
        document_payloads=_doc_payloads(),
        date=DATE,
    )

    text = markdown_report(payload)

    assert "Paper10 manuscript text/table consistency audit" in text
    assert "source-derived manuscript text/table consistency audit" in text
    assert "does not add a new experimental claim" in text
    assert "overall consistency: PASS" in text
    for token in [
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "64.2960",
        "66.2544",
        "67.4913",
        "must not be pooled",
        "robust Bishan-to-Dongxing transfer superiority",
        "direct 50-state Bishan scale-up success",
        "72.1773",
        "65.8876",
        "6.2897",
        "20 / 20",
        "4.1643",
        "algorithm-readiness addendum",
    ]:
        assert token in text
    assert "paper10_geojepa_mpc.experiments.manuscript_text_table_consistency_audit" in text
    assert "statistically significant" not in text.lower()
    assert "p value" not in text.lower()


def test_write_manuscript_text_table_consistency_audit_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "text_audit.json"
    output_md = tmp_path / "text_audit.md"

    payload = write_manuscript_text_table_consistency_audit(
        table_freeze_json=TABLE_FREEZE,
        document_paths=DOCUMENTS,
        output_json=output_json,
        output_md=output_md,
        date=DATE,
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)
    assert payload["source_files"]["table_freeze_json"] == str(TABLE_FREEZE)
    assert payload["source_files"]["documents"] == [str(path) for path in DOCUMENTS]


def test_cli_accepts_text_table_audit_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "manuscript_text_table_consistency_audit",
            "--table-freeze-json",
            "tables.json",
            "--document",
            "draft.md",
            "--document",
            "blueprint.md",
            "--output-json",
            "audit.json",
            "--output-md",
            "audit.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.table_freeze_json == "tables.json"
    assert args.document == ["draft.md", "blueprint.md"]
    assert args.output_json == "audit.json"
    assert args.output_md == "audit.md"
    assert args.date == "2026-06-19"
