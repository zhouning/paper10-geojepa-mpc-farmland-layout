"""Preflight checks for the Paper10 submission/reviewer archive package."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"

ARCHIVE_MANIFEST = RESULTS / "e0_archive_manifest_2026-06-09.csv"
SELF_CONTAINED_MANUSCRIPT = (
    RESULTS
    / "e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md"
)
SMOKE_PROTOCOL = RESULTS / "e0_reviewer_smoke_replication_protocol_2026-06-09.md"
SMOKE_LOG = RESULTS / "e0_reviewer_smoke_verification_log_2026-06-10.md"

REQUIRED_PATHS = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    Path("DATA_AVAILABILITY.md"),
    Path("requirements.txt"),
    Path("county_env.py"),
    Path("paper10_geojepa_mpc"),
    Path("arcgis_toolbox_paper9") / "private_source",
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
    ARCHIVE_MANIFEST,
    SELF_CONTAINED_MANUSCRIPT,
    SMOKE_PROTOCOL,
    SMOKE_LOG,
    Path("references") / "paper10_verified_references_2026-06-09.bib",
    Path("references") / "paper10_local_sources_2026-06-09.bib",
    Path("references") / "paper10_citation_map_2026-06-09.md",
)

FORBIDDEN_50_STATE_PATTERNS = (
    r"generally scales to 50 states",
    r"scales to 50 states",
    r"50-state success",
    r"successful 50-state",
    r"successful scale-up evidence",
    r"successful scale-up",
)

ARCHIVE_REQUIRED_FIELDS = (
    "record_id",
    "path_or_pattern",
    "access_route",
    "archive_action",
    "status",
)

INCLUDED_ARCHIVE_ACTIONS = {"include", "include_after_rights_check"}
EXCLUDED_ARCHIVE_ACTIONS = {"exclude", "exclude_unless_selected", "exclude_from_git"}
ALLOWED_TRACKED_EXCLUDED_PATHS = {
    "tool2/README.md",
    "dem_slope_analysis/output/README.md",
    "results_real/blocks/README.md",
}

SMOKE_LINK_DOCS = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    RESULTS / "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
    RESULTS / "e0_submission_readiness_checklist_2026-06-09.md",
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_markdown_files(root: Path) -> list[Path]:
    targets = [
        root / "README.md",
        root / "MANIFEST.md",
        root / "DATA_AVAILABILITY.md",
        root / "REPRODUCIBILITY.md",
    ]
    result_dir = root / RESULTS
    if result_dir.exists():
        targets.extend(sorted(result_dir.glob("*.md")))
    return [path for path in targets if path.exists()]


def check_required_paths_exist(root: Path) -> CheckResult:
    missing = [str(path) for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        return CheckResult(
            "required_paths_exist",
            False,
            "missing required paths: " + ", ".join(missing),
        )
    return CheckResult(
        "required_paths_exist",
        True,
        f"{len(REQUIRED_PATHS)} required paths found",
    )


def check_archive_manifest_required_fields(root: Path) -> CheckResult:
    path = root / ARCHIVE_MANIFEST
    if not path.exists():
        return CheckResult(
            "archive_manifest_required_fields",
            False,
            f"missing archive manifest: {ARCHIVE_MANIFEST}",
        )

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    missing_rows = []
    for index, row in enumerate(rows, start=2):
        missing_fields = [field for field in ARCHIVE_REQUIRED_FIELDS if not row.get(field)]
        if missing_fields:
            missing_rows.append(f"line {index}: {','.join(missing_fields)}")

    if missing_rows:
        return CheckResult(
            "archive_manifest_required_fields",
            False,
            "; ".join(missing_rows),
        )
    return CheckResult(
        "archive_manifest_required_fields",
        True,
        f"{len(rows)} rows contain required fields",
    )


def read_archive_manifest_rows(root: Path) -> tuple[list[dict[str, str]], str | None]:
    path = root / ARCHIVE_MANIFEST
    if not path.exists():
        return [], f"missing archive manifest: {ARCHIVE_MANIFEST}"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle)), None


def normalize_manifest_pattern(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def has_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[")


def manifest_path_matches(root: Path, pattern: str) -> list[Path]:
    normalized = normalize_manifest_pattern(pattern)
    if not normalized:
        return []
    if has_glob(normalized):
        return [path for path in root.glob(normalized) if path.exists()]
    candidate = root / normalized.rstrip("/")
    return [candidate] if candidate.exists() else []


def check_archive_manifest_included_paths_resolve(root: Path) -> CheckResult:
    rows, error = read_archive_manifest_rows(root)
    if error:
        return CheckResult("archive_manifest_included_paths_resolve", False, error)

    missing = []
    checked = 0
    for index, row in enumerate(rows, start=2):
        if row.get("record_id") != "record1_code_evidence":
            continue
        if row.get("archive_action") not in INCLUDED_ARCHIVE_ACTIONS:
            continue

        checked += 1
        pattern = row.get("path_or_pattern", "")
        if not manifest_path_matches(root, pattern):
            missing.append(f"line {index}: {pattern}")

    if missing:
        return CheckResult(
            "archive_manifest_included_paths_resolve",
            False,
            "included paths do not resolve: " + "; ".join(missing),
        )
    return CheckResult(
        "archive_manifest_included_paths_resolve",
        True,
        f"{checked} Record 1 include/include_after_rights_check paths resolve",
    )


def git_tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def tracked_file_matches_pattern(tracked_path: str, pattern: str) -> bool:
    normalized = normalize_manifest_pattern(pattern)
    if not normalized:
        return False
    if has_glob(normalized):
        return PurePosixPath(tracked_path).match(normalized)
    prefix = normalized.rstrip("/")
    return tracked_path == prefix or tracked_path.startswith(prefix + "/")


def check_excluded_paths_not_tracked(root: Path) -> CheckResult:
    rows, error = read_archive_manifest_rows(root)
    if error:
        return CheckResult("excluded_paths_not_tracked", False, error)

    tracked = git_tracked_files(root)
    violations = []
    checked = 0
    for index, row in enumerate(rows, start=2):
        if row.get("record_id") != "excluded_or_local":
            continue
        if row.get("archive_action") not in EXCLUDED_ARCHIVE_ACTIONS:
            continue

        checked += 1
        pattern = row.get("path_or_pattern", "")
        for tracked_path in tracked:
            if tracked_path in ALLOWED_TRACKED_EXCLUDED_PATHS:
                continue
            if tracked_file_matches_pattern(tracked_path, pattern):
                violations.append(f"line {index}: {tracked_path}")

    if violations:
        return CheckResult(
            "excluded_paths_not_tracked",
            False,
            "excluded/local paths tracked by Git: " + "; ".join(violations),
        )
    return CheckResult(
        "excluded_paths_not_tracked",
        True,
        f"{checked} excluded/local manifest patterns have no tracked payload files",
    )


def check_forbidden_50_state_claims(root: Path) -> CheckResult:
    pattern = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    hits = []
    for path in iter_markdown_files(root):
        rel = path.relative_to(root)
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            if pattern.search(line):
                hits.append(f"{rel}:{line_no}: {line.strip()}")

    if hits:
        return CheckResult(
            "forbidden_50_state_claims",
            False,
            "forbidden wording found: " + " | ".join(hits),
        )
    return CheckResult(
        "forbidden_50_state_claims",
        True,
        "no prohibited positive 50-state wording found",
    )


def check_self_contained_manuscript_no_paper9_placeholder(root: Path) -> CheckResult:
    path = root / SELF_CONTAINED_MANUSCRIPT
    if not path.exists():
        return CheckResult(
            "self_contained_manuscript_no_paper9_placeholder",
            False,
            f"missing manuscript: {SELF_CONTAINED_MANUSCRIPT}",
        )

    text = read_text(path)
    if "@zhou2026paper9_local" in text:
        return CheckResult(
            "self_contained_manuscript_no_paper9_placeholder",
            False,
            "self-contained manuscript body still cites @zhou2026paper9_local",
        )
    return CheckResult(
        "self_contained_manuscript_no_paper9_placeholder",
        True,
        "self-contained manuscript has no @zhou2026paper9_local citation",
    )


def bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,\s]+)", text))


def cited_keys(text: str) -> set[str]:
    return set(re.findall(r"@([A-Za-z0-9_:-]+)", text))


def check_citation_keys_resolve(root: Path) -> CheckResult:
    bib_paths = [
        root / "references" / "paper10_verified_references_2026-06-09.bib",
        root / "references" / "paper10_local_sources_2026-06-09.bib",
    ]
    keys: set[str] = set()
    for path in bib_paths:
        if not path.exists():
            return CheckResult(
                "citation_keys_resolve",
                False,
                f"missing bibliography: {path.relative_to(root)}",
            )
        keys.update(bib_keys(read_text(path)))

    cite_paths = [
        root / RESULTS / "e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md",
        root
        / RESULTS
        / "e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md",
        root / "references" / "paper10_citation_map_2026-06-09.md",
        root / RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
    ]
    cited: set[str] = set()
    for path in cite_paths:
        if path.exists():
            cited.update(cited_keys(read_text(path)))

    missing = sorted(key for key in cited if key not in keys)
    if missing:
        return CheckResult(
            "citation_keys_resolve",
            False,
            "missing bibliography keys: " + ", ".join(missing),
        )
    return CheckResult(
        "citation_keys_resolve",
        True,
        f"{len(cited)} cited keys resolve against {len(keys)} bibliography keys",
    )


def check_reviewer_smoke_protocol_links(root: Path) -> CheckResult:
    missing = []
    protocol_name = SMOKE_PROTOCOL.name
    log_name = SMOKE_LOG.name
    for rel_path in SMOKE_LINK_DOCS:
        path = root / rel_path
        if not path.exists():
            missing.append(f"{rel_path}: missing file")
            continue
        text = read_text(path)
        if protocol_name not in text:
            missing.append(f"{rel_path}: missing {protocol_name}")
        if log_name not in text:
            missing.append(f"{rel_path}: missing {log_name}")

    if missing:
        return CheckResult(
            "reviewer_smoke_protocol_links",
            False,
            "; ".join(missing),
        )
    return CheckResult(
        "reviewer_smoke_protocol_links",
        True,
        f"{len(SMOKE_LINK_DOCS)} docs link smoke protocol and verification log",
    )


CHECKS: tuple[Callable[[Path], CheckResult], ...] = (
    check_required_paths_exist,
    check_archive_manifest_required_fields,
    check_archive_manifest_included_paths_resolve,
    check_excluded_paths_not_tracked,
    check_forbidden_50_state_claims,
    check_self_contained_manuscript_no_paper9_placeholder,
    check_citation_keys_resolve,
    check_reviewer_smoke_protocol_links,
)


def run_checks(root: Path) -> list[CheckResult]:
    return [check(root) for check in CHECKS]


def to_payload(results: list[CheckResult]) -> dict:
    failed = [result.name for result in results if not result.ok]
    passed = [result.name for result in results if result.ok]
    return {
        "ok": not failed,
        "total_checks": len(results),
        "passed_checks": passed,
        "failed_checks": failed,
        "checks": [
            {"name": result.name, "ok": result.ok, "details": result.details}
            for result in results
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Paper10 submission preflight checks."
    )
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="Repository root to check.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a text summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    payload = to_payload(run_checks(root))

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        status = "PASS" if payload["ok"] else "FAIL"
        print(f"Paper10 preflight: {status}")
        for item in payload["checks"]:
            prefix = "ok" if item["ok"] else "fail"
            print(f"[{prefix}] {item['name']}: {item['details']}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
