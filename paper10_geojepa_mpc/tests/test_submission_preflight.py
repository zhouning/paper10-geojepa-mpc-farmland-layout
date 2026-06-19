import json
import subprocess
import sys
from pathlib import Path

from scripts.paper10.preflight_submission_checks import (
    ARCHIVE_MANIFEST,
    AUTHOR_DECISION_MATRIX,
    CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    CEUS_REVIEWER_IMPROVEMENT_PACKET,
    CEUS_STAGE3_MANUSCRIPT_DRAFT,
    CEUS_STAGE3_MANUSCRIPT_REFRAME,
    check_original_vision_validation_registry_current,
    DATA_ACCESS_RIGHTS_REGISTER,
    DATA_CODE_AVAILABILITY,
    DONGXING_PLOT_SCRIPT,
    FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    INTEGRATED_CITATION_STATISTICS_POLICY,
    INTEGRATED_DONGXING_FIGURE_PLAN,
    INTEGRATED_DONGXING_SCAFFOLD,
    INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    INTEGRATED_DONGXING_TABLES,
    INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
    ORIGINAL_VISION_DESIGN,
    ORIGINAL_VISION_REGISTRY,
    ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD,
    PAPER10_CLAIM_SOURCE_AUDIT_JSON,
    PAPER10_CLAIM_SOURCE_AUDIT_MD,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD,
    PAPER10_REAL_ENV_SMOKE_JSON,
    PAPER10_REAL_ENV_SMOKE_MD,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
    PROJECT_PROPOSAL_REPORT,
    RESULTS,
    SELF_CONTAINED_MANUSCRIPT,
    SMOKE_LOG,
    SMOKE_PROTOCOL,
    SUBMISSION_BLOCKER_DECISION_PACKET,
)


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "paper10" / "preflight_submission_checks.py"
MINIMAL_PREFLIGHT_FIXTURE_FILES = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    Path("DATA_AVAILABILITY.md"),
    Path("requirements.txt"),
    Path("county_env.py"),
    ARCHIVE_MANIFEST,
    AUTHOR_DECISION_MATRIX,
    DATA_CODE_AVAILABILITY,
    DATA_ACCESS_RIGHTS_REGISTER,
    SELF_CONTAINED_MANUSCRIPT,
    RESULTS / "e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md",
    SMOKE_PROTOCOL,
    SMOKE_LOG,
    INTEGRATED_DONGXING_SCAFFOLD,
    INTEGRATED_DONGXING_TABLES,
    INTEGRATED_DONGXING_FIGURE_PLAN,
    INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    SUBMISSION_BLOCKER_DECISION_PACKET,
    INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
    INTEGRATED_CITATION_STATISTICS_POLICY,
    CEUS_REVIEWER_IMPROVEMENT_PACKET,
    CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    CEUS_STAGE3_MANUSCRIPT_REFRAME,
    CEUS_STAGE3_MANUSCRIPT_DRAFT,
    FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    PROJECT_PROPOSAL_REPORT,
    DONGXING_PLOT_SCRIPT,
    ORIGINAL_VISION_DESIGN,
    ORIGINAL_VISION_REGISTRY,
    ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON,
    PAPER10_CLAIM_SOURCE_AUDIT_MD,
    PAPER10_CLAIM_SOURCE_AUDIT_JSON,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON,
    PAPER10_REAL_ENV_SMOKE_MD,
    PAPER10_REAL_ENV_SMOKE_JSON,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON,
    RESULTS / "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
    RESULTS / "e0_submission_readiness_checklist_2026-06-09.md",
    RESULTS / "e0_dongxing_return_label_family_summary_2026-06-10.csv",
    RESULTS / "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    RESULTS / "e0_dongxing_local_data_cross_region_audit_2026-06-10.md",
    RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
    RESULTS / "e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md",
    RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
    Path("references") / "paper10_verified_references_2026-06-09.bib",
    Path("references") / "paper10_local_sources_2026-06-09.bib",
    Path("references") / "paper10_citation_map_2026-06-09.md",
    Path("references") / "paper10_paper9_local_source_status_2026-06-09.md",
)

MINIMAL_PREFLIGHT_FIXTURE_EMPTY_PATHS = (
    Path("arcgis_toolbox_paper9") / "private_source" / ".keep",
    Path("arcgis_toolbox_paper9")
    / "_scratch"
    / "tool1_smoke"
    / "prepared"
    / "tool2"
    / "transitions.npz",
    Path("arcgis_toolbox_paper9")
    / "_scratch"
    / "tool1_smoke"
    / "prepared"
    / "tool2"
    / "pairwise.npz",
    Path("notebooks") / "paper10_frontier_random050_50x24_h5_colab.ipynb",
    Path("paper7") / "data" / "block_geofm_embeddings.npy",
    Path("paper7") / "data" / "geofm_metadata.json",
    Path("paper10_geojepa_mpc") / "__init__.py",
    Path("paper10_geojepa_mpc") / "minimal_fixture.py",
    RESULTS / "minimal_fixture.json",
    RESULTS / "minimal_fixture.npz",
    RESULTS / "minimal_fixture.log",
    Path("paper10_geojepa_mpc") / "experiments" / "checkpoints" / ".keep",
)


def write_original_vision_files(root: Path, design: str, registry: str) -> None:
    design_path = root / ORIGINAL_VISION_DESIGN
    registry_path = root / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text(design, encoding="utf-8")
    registry_path.write_text(
        "\n".join(
            [
                registry,
                "",
                "## Design Spec",
                "",
                f"- `{ORIGINAL_VISION_DESIGN.as_posix()}`",
                "",
                "## Claim Lock",
                "",
                "Current evidence is not sufficient to claim strong 50-state scale-up.",
            ]
        ),
        encoding="utf-8",
    )


def copy_minimal_preflight_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    copied_paths = []
    for rel_path in MINIMAL_PREFLIGHT_FIXTURE_FILES:
        source = ROOT / rel_path
        destination = repo / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        copied_paths.append(rel_path.as_posix())
    for rel_path in MINIMAL_PREFLIGHT_FIXTURE_EMPTY_PATHS:
        destination = repo / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"")
        copied_paths.append(rel_path.as_posix())

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", *copied_paths], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def run_submission_preflight_json(root: Path) -> tuple[subprocess.CompletedProcess, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result, json.loads(result.stdout)


def check_details(payload: dict, name: str) -> str:
    return {
        item["name"]: item["details"]
        for item in payload["checks"]
    }[name]


def test_submission_preflight_cli_passes_current_repository():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["total_checks"] >= 10
    assert payload["failed_checks"] == []
    assert "archive_manifest_required_fields" in payload["passed_checks"]
    assert "archive_manifest_included_paths_resolve" in payload["passed_checks"]
    assert "excluded_paths_not_tracked" in payload["passed_checks"]
    assert "public_submission_placeholders_absent" in payload["passed_checks"]
    assert "public_data_route_wording_specific" in payload["passed_checks"]
    assert "forbidden_50_state_claims" in payload["passed_checks"]
    assert "self_contained_manuscript_no_paper9_placeholder" in payload["passed_checks"]
    assert "reviewer_smoke_protocol_links" in payload["passed_checks"]
    assert "integrated_dongxing_source_data_links" in payload["passed_checks"]
    assert "dongxing_data_availability_routes" in payload["passed_checks"]
    assert "integrated_figure_table_numbering_frozen" in payload["passed_checks"]
    assert "submission_blocker_decision_packet_current" in payload["passed_checks"]
    assert "integrated_target_venue_conversion_checklist_current" in payload["passed_checks"]
    assert "integrated_citation_statistics_policy_current" in payload["passed_checks"]
    assert "ceus_reviewer_improvement_packet_current" in payload["passed_checks"]
    assert "ceus_research_article_manuscript_draft_current" in payload["passed_checks"]
    assert "ceus_stage3_manuscript_reframe_current" in payload["passed_checks"]
    assert "ceus_stage3_manuscript_draft_current" in payload["passed_checks"]
    assert "paper10_project_proposal_report_current" in payload["passed_checks"]
    assert "paper10_author_decision_matrix_current" in payload["passed_checks"]
    assert "paper10_formal_manuscript_blueprint_current" in payload["passed_checks"]
    assert "paper10_claim_source_audit_current" in payload["passed_checks"]
    assert "paper10_figure_table_source_coverage_audit_current" in payload["passed_checks"]
    assert "paper10_manuscript_result_tables_freeze_current" in payload["passed_checks"]
    assert "paper10_manuscript_text_table_consistency_audit_current" in payload["passed_checks"]
    assert "paper10_real_data_availability_audit_current" in payload["passed_checks"]
    assert "paper10_real_data_integrity_smoke_current" in payload["passed_checks"]
    assert "paper10_real_env_smoke_current" in payload["passed_checks"]
    assert "paper10_real_env_value_filter_smoke_current" in payload["passed_checks"]
    assert "paper10_real_env_smoke_boundary_audit_current" in payload["passed_checks"]
    assert "paper10_anchor_raw_rollout_consistency_audit_current" in payload["passed_checks"]
    assert "original_vision_validation_registry_current" in payload["passed_checks"]


def test_submission_preflight_reports_missing_required_path(tmp_path):
    fixture = tmp_path / "repo"
    fixture.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "required_paths_exist" in payload["failed_checks"]


def test_submission_preflight_minimal_fixture_reports_missing_original_vision_registry(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / ORIGINAL_VISION_REGISTRY).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "original_vision_validation_registry_current" in payload["failed_checks"]
    details = check_details(payload, "original_vision_validation_registry_current")
    assert "missing:" in details
    assert str(ORIGINAL_VISION_REGISTRY) in details


def test_submission_preflight_minimal_fixture_reports_missing_project_proposal(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PROJECT_PROPOSAL_REPORT).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_project_proposal_report_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_project_proposal_report_current")
    assert "missing Paper10 project proposal report files" in details
    assert str(PROJECT_PROPOSAL_REPORT) in details


def test_submission_preflight_minimal_fixture_reports_missing_author_decision_matrix(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / AUTHOR_DECISION_MATRIX).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_author_decision_matrix_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_author_decision_matrix_current")
    assert "missing Paper10 author decision matrix files" in details
    assert str(AUTHOR_DECISION_MATRIX) in details


def test_submission_preflight_minimal_fixture_reports_missing_formal_manuscript_blueprint(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_formal_manuscript_blueprint_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_formal_manuscript_blueprint_current")
    assert "missing Paper10 formal manuscript blueprint files" in details
    assert str(FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT) in details


def test_submission_preflight_minimal_fixture_reports_missing_claim_source_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_CLAIM_SOURCE_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_claim_source_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_claim_source_audit_current")
    assert "missing Paper10 claim-source audit files" in details
    assert str(PAPER10_CLAIM_SOURCE_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_figure_table_source_coverage_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_figure_table_source_coverage_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_figure_table_source_coverage_audit_current")
    assert "missing Paper10 figure/table source coverage audit files" in details
    assert str(PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_manuscript_result_tables_freeze(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_manuscript_result_tables_freeze_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_manuscript_result_tables_freeze_current")
    assert "missing Paper10 manuscript result tables freeze files" in details
    assert str(PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_manuscript_text_table_consistency_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_manuscript_text_table_consistency_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_manuscript_text_table_consistency_audit_current")
    assert "missing Paper10 manuscript text/table consistency audit files" in details
    assert str(PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_real_data_availability_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_real_data_availability_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_real_data_availability_audit_current")
    assert "missing Paper10 real-data availability audit files" in details
    assert str(PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_real_data_integrity_smoke(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_real_data_integrity_smoke_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_real_data_integrity_smoke_current")
    assert "missing Paper10 real-data integrity smoke files" in details
    assert str(PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_real_env_smoke(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_REAL_ENV_SMOKE_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_real_env_smoke_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_real_env_smoke_current")
    assert "missing Paper10 real-environment smoke files" in details
    assert str(PAPER10_REAL_ENV_SMOKE_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_real_env_value_filter_smoke(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_real_env_value_filter_smoke_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_real_env_value_filter_smoke_current")
    assert "missing Paper10 real-environment value-filter smoke files" in details
    assert str(PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_real_env_smoke_boundary_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_real_env_smoke_boundary_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_real_env_smoke_boundary_audit_current")
    assert "missing Paper10 real-environment smoke boundary audit files" in details
    assert str(PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_reports_missing_anchor_raw_rollout_consistency_audit(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_anchor_raw_rollout_consistency_audit_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_anchor_raw_rollout_consistency_audit_current")
    assert "missing Paper10 anchor raw-rollout consistency audit files" in details
    assert str(PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD) in details


def test_submission_preflight_minimal_fixture_rejects_original_vision_registry_positive_claim(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    registry = fixture / ORIGINAL_VISION_REGISTRY
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n\ndirect 50-state success is confirmed\n",
        encoding="utf-8",
    )

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "original_vision_validation_registry_current" in payload["failed_checks"]
    details = check_details(payload, "original_vision_validation_registry_current")
    assert "forbidden validation wording" in details
    assert "direct 50-state success is confirmed" in details


def test_repository_docs_reference_submission_preflight_command():
    command = "scripts/paper10/preflight_submission_checks.py"
    docs = [
        ROOT / "README.md",
        ROOT / "REPRODUCIBILITY.md",
        ROOT / "MANIFEST.md",
        ROOT
        / "paper10_geojepa_mpc"
        / "experiments"
        / "results"
        / "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
    ]

    for path in docs:
        assert command in path.read_text(encoding="utf-8")


def test_original_vision_validation_registry_reports_missing_files(tmp_path):
    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "missing:" in result.details
    assert str(ORIGINAL_VISION_DESIGN) in result.details
    assert str(ORIGINAL_VISION_REGISTRY) in result.details


def test_original_vision_validation_registry_rejects_positive_claims(tmp_path):
    write_original_vision_files(
        tmp_path,
        "\n".join(
            [
                "We claim direct 50-state Bishan success.",
                "This proves 50-state scale-up.",
            ]
        ),
        "Robust Bishan-to-Dongxing transfer superiority is supported.",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "forbidden validation wording" in result.details
    assert "We claim direct 50-state Bishan success." in result.details
    assert "This proves 50-state scale-up." in result.details
    assert (
        "Robust Bishan-to-Dongxing transfer superiority is supported."
        in result.details
    )


def test_original_vision_validation_registry_requires_design_spec_reference(tmp_path):
    design_path = tmp_path / ORIGINAL_VISION_DESIGN
    registry_path = tmp_path / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text("Current evidence is not sufficient.", encoding="utf-8")
    registry_path.write_text("## Claim Lock\n", encoding="utf-8")

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "## Design Spec" in result.details
    assert ORIGINAL_VISION_DESIGN.as_posix() in result.details


def test_original_vision_validation_registry_requires_design_spec_section(tmp_path):
    design_path = tmp_path / ORIGINAL_VISION_DESIGN
    registry_path = tmp_path / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text("Current evidence is not sufficient.", encoding="utf-8")
    registry_path.write_text(
        "\n".join(
            [
                "## Notes",
                "",
                f"See `{ORIGINAL_VISION_DESIGN.as_posix()}` for context.",
                "",
                "## Claim Lock",
            ]
        ),
        encoding="utf-8",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "## Design Spec" in result.details
    assert ORIGINAL_VISION_DESIGN.as_posix() in result.details


def test_original_vision_validation_registry_requires_claim_lock(tmp_path):
    design_path = tmp_path / ORIGINAL_VISION_DESIGN
    registry_path = tmp_path / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text("Current evidence is not sufficient.", encoding="utf-8")
    registry_path.write_text(
        "\n".join(
            [
                "## Design Spec",
                "",
                f"`{ORIGINAL_VISION_DESIGN.as_posix()}`",
            ]
        ),
        encoding="utf-8",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "missing registry section: ## Claim Lock" in result.details


def test_original_vision_validation_registry_requires_claim_lock_heading(tmp_path):
    design_path = tmp_path / ORIGINAL_VISION_DESIGN
    registry_path = tmp_path / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text("Current evidence is not sufficient.", encoding="utf-8")
    registry_path.write_text(
        "\n".join(
            [
                "## Design Spec",
                "",
                f"- `{ORIGINAL_VISION_DESIGN.as_posix()}`",
                "",
                "The phrase ## Claim Lock appears here but is not a heading.",
                "",
                "```",
                "## Claim Lock",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "## Claim Lock" in result.details


def test_original_vision_validation_registry_allows_negative_guardrails(tmp_path):
    write_original_vision_files(
        tmp_path,
        "Do not claim direct 50-state Bishan success.",
        "Current evidence is not sufficient to claim strong 50-state scale-up.",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is True
    assert (
        result.details
        == "original-vision validation design and registry are current and guarded"
    )


def test_original_vision_validation_registry_rejects_mixed_clause_claims(tmp_path):
    write_original_vision_files(
        tmp_path,
        "Do not claim direct 50-state Bishan success; this experiment demonstrates direct 50-state Bishan success.",
        "Current evidence is not sufficient to claim strong 50-state scale-up.",
    )

    result = check_original_vision_validation_registry_current(tmp_path)

    assert result.name == "original_vision_validation_registry_current"
    assert result.ok is False
    assert "forbidden validation wording" in result.details
    assert (
        "Do not claim direct 50-state Bishan success; this experiment demonstrates direct 50-state Bishan success."
        in result.details
    )


def test_submission_preflight_reports_missing_included_archive_manifest_path(tmp_path):
    fixture = tmp_path / "repo"
    manifest_dir = fixture / "paper10_geojepa_mpc" / "experiments" / "results"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "e0_archive_manifest_2026-06-09.csv").write_text(
        "\n".join(
            [
                "record_id,bucket,path_or_pattern,artifact_type,manuscript_role,access_route,archive_action,external_dependency,status,notes",
                "record1_code_evidence,source_code,missing_package/**/*.py,software,main_implementation,public_repository_archive,include,no,ready_pending_identifier,missing path must fail",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "archive_manifest_included_paths_resolve" in payload["failed_checks"]
    details = {
        item["name"]: item["details"]
        for item in payload["checks"]
    }["archive_manifest_included_paths_resolve"]
    assert "missing_package/**/*.py" in details


def test_submission_preflight_reports_tracked_excluded_archive_path(tmp_path):
    fixture = tmp_path / "repo"
    manifest_dir = fixture / "paper10_geojepa_mpc" / "experiments" / "results"
    tracked_cache = fixture / "__pycache__" / "leaked.pyc"
    manifest_dir.mkdir(parents=True)
    tracked_cache.parent.mkdir()
    tracked_cache.write_bytes(b"cache")
    (manifest_dir / "e0_archive_manifest_2026-06-09.csv").write_text(
        "\n".join(
            [
                "record_id,bucket,path_or_pattern,artifact_type,manuscript_role,access_route,archive_action,external_dependency,status,notes",
                "excluded_or_local,cache,__pycache__/,cache,none,not_applicable,exclude,no,excluded,Python cache",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=fixture, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "add", "__pycache__/leaked.pyc"],
        cwd=fixture,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "excluded_paths_not_tracked" in payload["failed_checks"]
    details = {
        item["name"]: item["details"]
        for item in payload["checks"]
    }["excluded_paths_not_tracked"]
    assert "__pycache__/leaked.pyc" in details


def test_submission_preflight_reports_tracked_dot_prefixed_excluded_path(tmp_path):
    fixture = tmp_path / "repo"
    manifest_dir = fixture / "paper10_geojepa_mpc" / "experiments" / "results"
    tracked_cache = fixture / ".pytest_cache" / "README.md"
    manifest_dir.mkdir(parents=True)
    tracked_cache.parent.mkdir()
    tracked_cache.write_text("cache", encoding="utf-8")
    (manifest_dir / "e0_archive_manifest_2026-06-09.csv").write_text(
        "\n".join(
            [
                "record_id,bucket,path_or_pattern,artifact_type,manuscript_role,access_route,archive_action,external_dependency,status,notes",
                "excluded_or_local,cache,.pytest_cache/,cache,none,not_applicable,exclude,no,excluded,pytest cache",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=fixture, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "add", ".pytest_cache/README.md"],
        cwd=fixture,
        check=True,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "excluded_paths_not_tracked" in payload["failed_checks"]
    details = {
        item["name"]: item["details"]
        for item in payload["checks"]
    }["excluded_paths_not_tracked"]
    assert ".pytest_cache/README.md" in details


def test_submission_preflight_reports_public_placeholder_leakage(tmp_path):
    fixture = tmp_path / "repo"
    fixture.mkdir()
    (fixture / "README.md").write_text(
        "Archive record: [REPOSITORY/DOI TO BE ADDED]\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "public_submission_placeholders_absent" in payload["failed_checks"]
    details = {
        item["name"]: item["details"]
        for item in payload["checks"]
    }["public_submission_placeholders_absent"]
    assert "README.md:1" in details
    assert "[REPOSITORY/DOI TO BE ADDED]" in details


def test_submission_preflight_reports_vague_public_data_route_wording(tmp_path):
    fixture = tmp_path / "repo"
    fixture.mkdir()
    (fixture / "README.md").write_text(
        "Full data are available upon reasonable request.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(fixture), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert "public_data_route_wording_specific" in payload["failed_checks"]
    details = {
        item["name"]: item["details"]
        for item in payload["checks"]
    }["public_data_route_wording_specific"]
    assert "README.md:1" in details
    assert "available upon reasonable request" in details
