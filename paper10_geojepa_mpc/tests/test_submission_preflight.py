import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "paper10" / "preflight_submission_checks.py"


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
    assert payload["total_checks"] >= 8
    assert payload["failed_checks"] == []
    assert "archive_manifest_required_fields" in payload["passed_checks"]
    assert "archive_manifest_included_paths_resolve" in payload["passed_checks"]
    assert "excluded_paths_not_tracked" in payload["passed_checks"]
    assert "forbidden_50_state_claims" in payload["passed_checks"]
    assert "self_contained_manuscript_no_paper9_placeholder" in payload["passed_checks"]
    assert "reviewer_smoke_protocol_links" in payload["passed_checks"]


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
