import json
import subprocess
import sys
from pathlib import Path

from scripts.paper10.preflight_submission_checks import (
    check_original_vision_validation_registry_current,
)


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "paper10" / "preflight_submission_checks.py"
ORIGINAL_VISION_DESIGN = (
    Path("docs")
    / "superpowers"
    / "specs"
    / "2026-06-17-paper10-original-vision-validation-design.md"
)
ORIGINAL_VISION_REGISTRY = (
    Path("paper10_geojepa_mpc")
    / "experiments"
    / "results"
    / "e0_original_vision_validation_registry_2026-06-17.md"
)


def write_original_vision_files(root: Path, design: str, registry: str) -> None:
    design_path = root / ORIGINAL_VISION_DESIGN
    registry_path = root / ORIGINAL_VISION_REGISTRY
    design_path.parent.mkdir(parents=True)
    registry_path.parent.mkdir(parents=True)
    design_path.write_text(design, encoding="utf-8")
    registry_path.write_text(registry, encoding="utf-8")


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
