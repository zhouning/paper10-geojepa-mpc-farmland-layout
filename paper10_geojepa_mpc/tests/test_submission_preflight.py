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
    assert payload["total_checks"] >= 6
    assert payload["failed_checks"] == []
    assert "archive_manifest_required_fields" in payload["passed_checks"]
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
