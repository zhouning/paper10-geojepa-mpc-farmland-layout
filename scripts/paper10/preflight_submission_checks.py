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
INTEGRATED_MANUSCRIPT = (
    RESULTS / "e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md"
)
DATA_CODE_AVAILABILITY = RESULTS / "e0_data_code_availability_draft_2026-06-09.md"
DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
SMOKE_PROTOCOL = RESULTS / "e0_reviewer_smoke_replication_protocol_2026-06-09.md"
SMOKE_LOG = RESULTS / "e0_reviewer_smoke_verification_log_2026-06-10.md"
INTEGRATED_DONGXING_SCAFFOLD = (
    RESULTS / "e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md"
)
INTEGRATED_DONGXING_TABLES = (
    RESULTS / "e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"
)
INTEGRATED_DONGXING_FIGURE_PLAN = (
    RESULTS / "e0_integrated_dongxing_figure_plan_2026-06-11.md"
)
INTEGRATED_DONGXING_SOURCE_DATA_MAP = (
    RESULTS / "e0_source_data_map_with_dongxing_2026-06-11.md"
)
INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE = (
    RESULTS / "e0_integrated_figure_table_numbering_freeze_2026-06-11.md"
)
SUBMISSION_BLOCKER_DECISION_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST = (
    RESULTS
    / "e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md"
)
INTEGRATED_CITATION_STATISTICS_POLICY = (
    RESULTS / "e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md"
)
CEUS_REVIEWER_IMPROVEMENT_PACKET = (
    RESULTS / "e0_ceus_reviewer_improvement_packet_2026-06-12.md"
)
CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_ceus_research_article_manuscript_draft_2026-06-12.md"
)
CEUS_STAGE3_MANUSCRIPT_REFRAME = (
    RESULTS / "e0_ceus_stage3_manuscript_reframe_2026-06-18.md"
)
CEUS_STAGE3_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_ceus_stage3_manuscript_draft_2026-06-18.md"
)
PROJECT_PROPOSAL_REPORT = (
    RESULTS / "e0_paper10_project_proposal_opening_report_2026-06-18.md"
)
AUTHOR_DECISION_MATRIX = (
    RESULTS / "e0_paper10_author_decision_matrix_2026-06-18.md"
)
DONGXING_PLOT_SCRIPT = Path("scripts") / "paper10" / "plot_integrated_dongxing_figures.py"
ORIGINAL_VISION_DESIGN = (
    Path("docs")
    / "superpowers"
    / "specs"
    / "2026-06-17-paper10-original-vision-validation-design.md"
)
ORIGINAL_VISION_REGISTRY = (
    RESULTS / "e0_original_vision_validation_registry_2026-06-17.md"
)
ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET = (
    RESULTS / "e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md"
)
ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD = (
    RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md"
)
ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON = (
    RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"
)

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
    DATA_CODE_AVAILABILITY,
    DATA_ACCESS_RIGHTS_REGISTER,
    SELF_CONTAINED_MANUSCRIPT,
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
    PROJECT_PROPOSAL_REPORT,
    AUTHOR_DECISION_MATRIX,
    DONGXING_PLOT_SCRIPT,
    ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
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

PUBLIC_PLACEHOLDER_PATTERN = re.compile(
    r"\[[A-Z0-9 /_-]+(?:TO BE ADDED|TO BE ASSIGNED|TO BE SELECTED|IF AVAILABLE)\]"
)

PUBLIC_SUBMISSION_DOCS = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    Path("DATA_AVAILABILITY.md"),
    INTEGRATED_MANUSCRIPT,
    SELF_CONTAINED_MANUSCRIPT,
    CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    CEUS_STAGE3_MANUSCRIPT_REFRAME,
    CEUS_STAGE3_MANUSCRIPT_DRAFT,
    PROJECT_PROPOSAL_REPORT,
    AUTHOR_DECISION_MATRIX,
)

PUBLIC_VAGUE_DATA_ROUTE_PATTERN = re.compile(
    r"available upon(?: reasonable)? request"
    r"|temporary cloud"
    r"|personal web(?:site| link)"
    r"|drive link"
    r"|cloud link",
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


def check_public_submission_placeholders_absent(root: Path) -> CheckResult:
    hits = []
    checked = 0
    for rel_path in PUBLIC_SUBMISSION_DOCS:
        path = root / rel_path
        if not path.exists():
            continue

        checked += 1
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            for match in PUBLIC_PLACEHOLDER_PATTERN.finditer(line):
                hits.append(f"{rel_path}:{line_no}: {match.group(0)}")

    if hits:
        return CheckResult(
            "public_submission_placeholders_absent",
            False,
            "public-facing placeholder tokens found: " + " | ".join(hits),
        )
    return CheckResult(
        "public_submission_placeholders_absent",
        True,
        f"{checked} public-facing docs contain no unresolved bracket placeholders",
    )


def check_public_data_route_wording_specific(root: Path) -> CheckResult:
    hits = []
    checked = 0
    for rel_path in PUBLIC_SUBMISSION_DOCS:
        path = root / rel_path
        if not path.exists():
            continue

        checked += 1
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            match = PUBLIC_VAGUE_DATA_ROUTE_PATTERN.search(line)
            if match:
                hits.append(f"{rel_path}:{line_no}: {match.group(0)}")

    if hits:
        return CheckResult(
            "public_data_route_wording_specific",
            False,
            "vague public data-route wording found: " + " | ".join(hits),
        )
    return CheckResult(
        "public_data_route_wording_specific",
        True,
        f"{checked} public-facing docs use specific data/access-route wording",
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


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    heading_level = len(heading) - len(heading.lstrip("#"))
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""

    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if not line.startswith("#"):
            continue
        level = len(line) - len(line.lstrip("#"))
        if level <= heading_level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def markdown_section_outside_code_fences(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    heading_level = len(heading) - len(heading.lstrip("#"))
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == heading:
            start = index + 1
            break
    if start is None:
        return ""

    end = len(lines)
    in_fence = False
    for index in range(start, len(lines)):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level <= heading_level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def has_markdown_heading_outside_code_fences(text: str, heading: str) -> bool:
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence and stripped == heading:
            return True
    return False


def markdown_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


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
        root / CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
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


def check_integrated_dongxing_source_data_links(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        DONGXING_PLOT_SCRIPT,
        RESULTS / "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        RESULTS / "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_dongxing_source_data_links",
            False,
            "missing Dongxing source-data files: " + ", ".join(missing),
        )

    figure_plan = read_text(root / INTEGRATED_DONGXING_FIGURE_PLAN)
    source_map = read_text(root / INTEGRATED_DONGXING_SOURCE_DATA_MAP)
    plot_script = read_text(root / DONGXING_PLOT_SCRIPT)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    tables = read_text(root / INTEGRATED_DONGXING_TABLES)

    source_tokens = [
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing_tokens = []
    for label, text in [
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_SCAFFOLD), scaffold),
        (str(INTEGRATED_DONGXING_TABLES), tables),
    ]:
        for token in source_tokens:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    for label, text in [
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_SCAFFOLD), scaffold),
    ]:
        for token in ["Figure 4", "Figure 5"]:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    script_tokens = [
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "dongxing_return_label_scaling",
        "dongxing_low_label_budget_stress_test",
    ]
    for token in script_tokens:
        if token not in plot_script:
            missing_tokens.append(f"{DONGXING_PLOT_SCRIPT}: {token}")

    for token in [
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        str(DONGXING_PLOT_SCRIPT).replace("\\", "/"),
        "not robustly supported",
    ]:
        if token not in source_map.replace("\\", "/"):
            missing_tokens.append(f"{INTEGRATED_DONGXING_SOURCE_DATA_MAP}: {token}")
        if token not in figure_plan.replace("\\", "/"):
            missing_tokens.append(f"{INTEGRATED_DONGXING_FIGURE_PLAN}: {token}")

    if missing_tokens:
        return CheckResult(
            "integrated_dongxing_source_data_links",
            False,
            "missing Dongxing cross-links: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_dongxing_source_data_links",
        True,
        "Dongxing figure plan, source-data map, scaffold, tables, and plotting script are cross-linked",
    )


def check_dongxing_data_availability_routes(root: Path) -> CheckResult:
    required_files = [
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        RESULTS / "e0_dongxing_local_data_cross_region_audit_2026-06-10.md",
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "dongxing_data_availability_routes",
            False,
            "missing Dongxing availability files: " + ", ".join(missing),
        )

    availability = read_text(root / DATA_CODE_AVAILABILITY)
    rights_register = read_text(root / DATA_ACCESS_RIGHTS_REGISTER)

    required_tokens = [
        "Dongxing/Neijiang",
        "e0_source_data_map_with_dongxing_2026-06-11.md",
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "3711-block",
        "76,376",
        "public deposit",
        "controlled-access",
        "[DONGXING/NEIJIANG DATA DOI TO BE ADDED]",
        "[DONGXING/NEIJIANG CONTROLLED-ACCESS RECORD TO BE ADDED]",
    ]
    missing_tokens = []
    for label, text in [
        (str(DATA_CODE_AVAILABILITY), availability),
        (str(DATA_ACCESS_RIGHTS_REGISTER), rights_register),
    ]:
        for token in required_tokens:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    local_path_patterns = [
        r"D:\\test\\neijiang_cross_region",
        r"D:\\test\\dongxing",
    ]
    for pattern in local_path_patterns:
        if re.search(pattern, availability):
            missing_tokens.append(f"{DATA_CODE_AVAILABILITY}: public statement leaks {pattern}")

    if missing_tokens:
        return CheckResult(
            "dongxing_data_availability_routes",
            False,
            "Dongxing availability route gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "dongxing_data_availability_routes",
        True,
        "Data/Code Availability and rights register cover Dongxing public/control access routes",
    )


def check_integrated_figure_table_numbering_frozen(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_figure_table_numbering_frozen",
            False,
            "missing integrated numbering files: " + ", ".join(missing),
        )

    freeze = read_text(root / INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    tables = read_text(root / INTEGRATED_DONGXING_TABLES)
    figure_plan = read_text(root / INTEGRATED_DONGXING_FIGURE_PLAN)
    source_map = read_text(root / INTEGRATED_DONGXING_SOURCE_DATA_MAP)

    freeze_tokens = [
        "not a target-journal final layout",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_DONGXING_FIGURE_PLAN.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
        "Supplementary Table S1",
        "Supplementary Table S2",
        "Internal Control Table C1",
        "failed monitor gates",
        "do not support robust Bishan-to-Dongxing transfer superiority",
        "e0_frontier_random050_seedwise_rewards_2026-06-09.csv",
        "e0_frontier_random050_topk_diagnostics_2026-06-09.csv",
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing_tokens = []
    for token in freeze_tokens:
        if token not in freeze:
            missing_tokens.append(f"{INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE}: {token}")

    freeze_name = INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name
    linked_docs = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    doc_text = {
        str(INTEGRATED_DONGXING_SCAFFOLD): scaffold,
        str(INTEGRATED_DONGXING_TABLES): tables,
        str(INTEGRATED_DONGXING_FIGURE_PLAN): figure_plan,
        str(INTEGRATED_DONGXING_SOURCE_DATA_MAP): source_map,
    }
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        text = doc_text.get(str(rel_path), read_text(path))
        if freeze_name not in text:
            missing_tokens.append(f"{rel_path}: {freeze_name}")

    for label, text in [
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_TABLES), tables),
    ]:
        for token in ["Main Figure 4", "Supplementary Figure S1", "Main Table 3"]:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    if missing_tokens:
        return CheckResult(
            "integrated_figure_table_numbering_frozen",
            False,
            "figure/table numbering freeze gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_figure_table_numbering_frozen",
        True,
        "integrated main/supplementary figure and table numbering is frozen and cross-linked",
    )


def check_submission_blocker_decision_packet_current(root: Path) -> CheckResult:
    required_files = [
        SUBMISSION_BLOCKER_DECISION_PACKET,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "submission_blocker_decision_packet_current",
            False,
            "missing submission blocker decision files: " + ", ".join(missing),
        )

    packet = read_text(root / SUBMISSION_BLOCKER_DECISION_PACKET)
    required_tokens = [
        "not a final manuscript",
        "Do not submit until",
        "Target journal and article type",
        "Repository DOI or reviewer link",
        "Code licence",
        "Generated-data rights",
        "Full Bishan Tool2 data access route",
        "GPKG-root geospatial inputs access route",
        "Dongxing/Neijiang prepared data access route",
        "Citation policy",
        "Statistical reporting policy",
        "Current status: unresolved",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        "e0_integrated_figure_table_numbering_freeze_2026-06-11.md",
        "e0_data_code_availability_draft_2026-06-09.md",
        "e0_data_access_and_rights_decision_register_2026-06-09.md",
        "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
        "e0_source_data_map_with_dongxing_2026-06-11.md",
    ]
    missing_tokens = []
    for token in required_tokens:
        if token not in packet:
            missing_tokens.append(f"{SUBMISSION_BLOCKER_DECISION_PACKET}: {token}")

    packet_name = SUBMISSION_BLOCKER_DECISION_PACKET.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    if missing_tokens:
        return CheckResult(
            "submission_blocker_decision_packet_current",
            False,
            "submission blocker decision packet gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "submission_blocker_decision_packet_current",
        True,
        "submission blocker decision packet is current and cross-linked",
    )


def check_integrated_target_venue_conversion_checklist_current(
    root: Path,
) -> CheckResult:
    required_files = [
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_target_venue_conversion_checklist_current",
            False,
            "missing integrated target-venue conversion files: " + ", ".join(missing),
        )

    checklist = read_text(root / INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST)
    required_tokens = [
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        "Dongxing/Neijiang",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        "Target journal and article type",
        "Repository DOI or reviewer link",
        "Dongxing/Neijiang prepared data access route",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in checklist:
            missing_tokens.append(f"{INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST}: {token}")

    checklist_name = INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md",
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if checklist_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {checklist_name}")

    if missing_tokens:
        return CheckResult(
            "integrated_target_venue_conversion_checklist_current",
            False,
            "integrated target-venue checklist gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_target_venue_conversion_checklist_current",
        True,
        "integrated target-venue/manuscript conversion checklist is current and cross-linked",
    )


def check_integrated_citation_statistics_policy_current(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_CITATION_STATISTICS_POLICY,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
        Path("references") / "paper10_citation_map_2026-06-09.md",
        Path("references") / "paper10_verified_references_2026-06-09.bib",
        Path("references") / "paper10_local_sources_2026-06-09.bib",
        Path("references") / "paper10_paper9_local_source_status_2026-06-09.md",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_citation_statistics_policy_current",
            False,
            "missing citation/statistics policy files: " + ", ".join(missing),
        )

    policy = read_text(root / INTEGRATED_CITATION_STATISTICS_POLICY)
    required_tokens = [
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "not a final reference style",
        "not a target-journal statistical-analysis plan",
        "references/paper10_citation_map_2026-06-09.md",
        "references/paper10_verified_references_2026-06-09.bib",
        "references/paper10_local_sources_2026-06-09.bib",
        "references/paper10_paper9_local_source_status_2026-06-09.md",
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        "Target journal and article type",
        "Citation policy",
        "Statistical reporting policy",
        "zhou2026paper9_local",
        "local-only",
        "self-contained Paper10 Methods route",
        "maes2026leworldmodel",
        "2026 arXiv preprint",
        "No formal hypothesis tests have been run",
        "Do not use `statistically significant`",
        "p-values",
        "descriptive means",
        "sample standard deviations",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in policy:
            missing_tokens.append(f"{INTEGRATED_CITATION_STATISTICS_POLICY}: {token}")

    policy_name = INTEGRATED_CITATION_STATISTICS_POLICY.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        Path("references") / "paper10_citation_map_2026-06-09.md",
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if policy_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {policy_name}")

    inferential_docs = [
        SELF_CONTAINED_MANUSCRIPT,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    ]
    for rel_path in inferential_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
            if match:
                missing_tokens.append(
                    f"{rel_path}:{line_no}: unsupported inferential wording "
                    f"{match.group(0)}"
                )

    if missing_tokens:
        return CheckResult(
            "integrated_citation_statistics_policy_current",
            False,
            "citation/statistical reporting policy gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_citation_statistics_policy_current",
        True,
        "citation and statistical-reporting policy is current and cross-linked",
    )


def check_ceus_reviewer_improvement_packet_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_reviewer_improvement_packet_current",
            False,
            "missing CEUS reviewer-improvement files: " + ", ".join(missing),
        )

    packet = read_text(root / CEUS_REVIEWER_IMPROVEMENT_PACKET)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    target_checklist = read_text(root / INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST)

    packet_tokens = [
        "CEUS Research Article candidate",
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        "D:\\test\\tool2\\transitions.npz",
        "D:\\test\\dem_slope_analysis\\output\\DLTB_with_slope.gpkg",
        "D:\\test\\results_real\\blocks",
        "D:\\test\\neijiang_cross_region",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP",
        "candidate-value-weight=1.0",
        "external optimizer baseline",
        "No new full Bishan rerun was run in this pass",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    scaffold_tokens = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "candidate-value-weight=1.0",
        "Constrained MDP, CPO, or RCPO",
    ]
    checklist_tokens = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "CEUS Research Article candidate route",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "Soft training and hard inference",
        "candidate-value-weight=1.0",
    ]

    missing_tokens = []
    for token in packet_tokens:
        if token not in packet:
            missing_tokens.append(f"{CEUS_REVIEWER_IMPROVEMENT_PACKET}: {token}")
    for token in scaffold_tokens:
        if token not in scaffold:
            missing_tokens.append(f"{INTEGRATED_DONGXING_SCAFFOLD}: {token}")
    for token in checklist_tokens:
        if token not in target_checklist:
            missing_tokens.append(
                f"{INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST}: {token}"
            )

    packet_name = CEUS_REVIEWER_IMPROVEMENT_PACKET.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_DONGXING_SCAFFOLD,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    if missing_tokens:
        return CheckResult(
            "ceus_reviewer_improvement_packet_current",
            False,
            "CEUS reviewer-improvement packet gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_reviewer_improvement_packet_current",
        True,
        "CEUS reviewer-improvement packet is current and cross-linked",
    )


def check_ceus_research_article_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_research_article_manuscript_draft_current",
            False,
            "missing CEUS manuscript draft files: " + ", ".join(missing),
        )

    path = root / CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT
    text = read_text(path)
    missing_tokens = []

    required_tokens = [
        "CEUS Research Article candidate",
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "Title",
        "Highlights",
        "Abstract",
        "Keywords",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and Table List",
        "Claim-Evidence and Unresolved Blockers",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP, CPO, or RCPO",
        "candidate-value-weight=1.0",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: @zhou2026paper9_local"
        )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: missing ## Abstract section"
        )
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: abstract has "
            f"{abstract_words} words"
        )

    highlights = [
        line[2:].strip()
        for line in markdown_section(text, "## Highlights").splitlines()
        if line.startswith("- ")
    ]
    if not 3 <= len(highlights) <= 5:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: "
            f"{len(highlights)} highlight bullets"
        )
    long_highlights = [
        item
        for item in highlights
        if len(item) > 85
    ]
    if long_highlights:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: highlights over 85 chars: "
            + " | ".join(long_highlights)
        )

    if missing_tokens:
        return CheckResult(
            "ceus_research_article_manuscript_draft_current",
            False,
            "CEUS manuscript draft gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_research_article_manuscript_draft_current",
        True,
        (
            "CEUS manuscript draft is current, abstract/highlights fit limits, "
            "and claim boundaries are guarded"
        ),
    )


def check_ceus_stage3_manuscript_reframe_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_stage3_manuscript_reframe_current",
            False,
            "missing CEUS Stage 3 manuscript reframe files: " + ", ".join(missing),
        )

    text = read_text(root / CEUS_STAGE3_MANUSCRIPT_REFRAME)
    missing_tokens = []
    reframe_name = CEUS_STAGE3_MANUSCRIPT_REFRAME.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if reframe_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {reframe_name}")

    required_tokens = [
        "CEUS Stage 3 manuscript reframe",
        "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md",
        "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json",
        "e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md",
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "Paper10 now solves",
        "monitor-gated value labels",
        "Bishan 20x16/top5",
        "69.4705",
        "matched Paper9 baseline",
        "67.5437",
        "Stage 3 confirmatory 50-state rows did not beat the matched Paper9 baseline",
        "frontier_random050_50x16_h5_seed48_f050",
        "64.2960",
        "frontier_random050_50x24_h5_seed47_f075",
        "66.2544",
        "diagnostic_near_pass",
        "67.4913",
        "must not be pooled",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "Title replacement",
        "Abstract replacement",
        "Results replacement",
        "Discussion replacement",
        "Conclusion replacement",
        "Claim-evidence map",
        "Current blockers before final submission",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: {token}")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract replacement")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: missing ## Abstract replacement section"
        )
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: abstract replacement has "
            f"{abstract_words} words"
        )

    if missing_tokens:
        return CheckResult(
            "ceus_stage3_manuscript_reframe_current",
            False,
            "CEUS Stage 3 manuscript reframe gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_stage3_manuscript_reframe_current",
        True,
        "CEUS Stage 3 manuscript reframe is current and claim-bounded",
    )


def check_ceus_stage3_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_stage3_manuscript_draft_current",
            False,
            "missing CEUS Stage 3 manuscript draft files: " + ", ".join(missing),
        )

    text = read_text(root / CEUS_STAGE3_MANUSCRIPT_DRAFT)
    missing_tokens = []
    draft_name = CEUS_STAGE3_MANUSCRIPT_DRAFT.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if draft_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {draft_name}")

    required_tokens = [
        "CEUS Stage 3 manuscript draft",
        "not a final submission package",
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        "One-Sentence Argument",
        "Terminology Ledger",
        "Title",
        "Highlights",
        "Abstract",
        "Keywords",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and Table List",
        "Claim-Evidence and Unresolved Blockers",
        "Bishan 20x16/top5",
        "69.4705",
        "matched Paper9 baseline",
        "67.5437",
        "frontier_random050_50x16_h5_seed48_f050",
        "64.2960",
        "frontier_random050_50x24_h5_seed47_f075",
        "66.2544",
        "diagnostic_near_pass",
        "67.4913",
        "must not be pooled",
        "pairwise-only baseline policy remains unresolved",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP, CPO, or RCPO",
        "candidate-value-weight=1.0",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: missing ## Abstract")
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: abstract has {abstract_words} words"
        )

    highlights = [
        line[2:].strip()
        for line in markdown_section(text, "## Highlights").splitlines()
        if line.startswith("- ")
    ]
    if not 3 <= len(highlights) <= 5:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: {len(highlights)} highlight bullets"
        )
    long_highlights = [item for item in highlights if len(item) > 85]
    if long_highlights:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: highlights over 85 chars: "
            + " | ".join(long_highlights)
        )

    if missing_tokens:
        return CheckResult(
            "ceus_stage3_manuscript_draft_current",
            False,
            "CEUS Stage 3 manuscript draft gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_stage3_manuscript_draft_current",
        True,
        "CEUS Stage 3 manuscript draft is current and claim-bounded",
    )


def check_paper10_project_proposal_report_current(root: Path) -> CheckResult:
    required_files = [
        PROJECT_PROPOSAL_REPORT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_CITATION_STATISTICS_POLICY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_project_proposal_report_current",
            False,
            "missing Paper10 project proposal report files: " + ", ".join(missing),
        )

    text = read_text(root / PROJECT_PROPOSAL_REPORT)
    missing_tokens = []
    report_name = PROJECT_PROPOSAL_REPORT.name
    linked_docs = [Path("README.md"), Path("MANIFEST.md")]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if report_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {report_name}")

    required_tokens = [
        "Paper10 课题立项/开题报告替代稿",
        "课题立项临时材料",
        "不是正式投稿论文",
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "基于 monitor-gated value labels 的 GeoJEPA-MPC 农田布局规划方法研究",
        "拟解决的核心问题",
        "研究目标",
        "研究内容与技术路线",
        "已有工作基础与阶段性结果",
        "初步结论",
        "创新点",
        "可行性基础",
        "后续研究计划",
        "预期成果",
        "风险、边界与待决事项",
        "Bishan 20x16/top5",
        "69.4705",
        "67.5437",
        "1.9269",
        "64.2960",
        "66.2544",
        "67.4913",
        "must not be pooled",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "pairwise-only baseline policy",
        "repository DOI",
        "statistical reporting policy",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{PROJECT_PROPOSAL_REPORT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{PROJECT_PROPOSAL_REPORT}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PROJECT_PROPOSAL_REPORT}:{line_no}: positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PROJECT_PROPOSAL_REPORT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    section_count = sum(1 for line in text.splitlines() if line.startswith("## "))
    if section_count < 10:
        missing_tokens.append(
            f"{PROJECT_PROPOSAL_REPORT}: only {section_count} level-2 sections"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_project_proposal_report_current",
            False,
            "Paper10 project proposal report gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_project_proposal_report_current",
        True,
        "Paper10 project proposal report is current and claim-bounded",
    )


def check_paper10_author_decision_matrix_current(root: Path) -> CheckResult:
    required_files = [
        AUTHOR_DECISION_MATRIX,
        PROJECT_PROPOSAL_REPORT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_author_decision_matrix_current",
            False,
            "missing Paper10 author decision matrix files: " + ", ".join(missing),
        )

    text = read_text(root / AUTHOR_DECISION_MATRIX)
    missing_tokens = []
    matrix_name = AUTHOR_DECISION_MATRIX.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if matrix_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {matrix_name}")

    required_tokens = [
        "Paper10 author decision and formal-submission conversion matrix",
        "author-decision control document",
        "not a final manuscript",
        PROJECT_PROPOSAL_REPORT.name,
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "One-sentence conversion argument",
        "Decision matrix",
        "Recommended decision order",
        "Default manuscript route if no new author decision arrives",
        "Claim-evidence locks for conversion",
        "Completion checklist",
        "Target venue and article type",
        "Comparator and pairwise-only baseline policy",
        "Repository DOI or reviewer link",
        "Code licence",
        "Generated-output and checkpoint rights",
        "Full Bishan Tool2 access route",
        "GPKG-root geospatial input route",
        "Dongxing/Neijiang prepared-data route",
        "Citation policy",
        "Statistical reporting policy",
        "Final figure/table export package",
        "Claim boundary",
        "matched Paper9 `rank_seed2028`",
        "self-contained Paper10 Methods route",
        "20x16/top5 mean reward `69.4705`",
        "matched Paper9 baseline `67.5437`",
        "`64.2960` and `66.2544`",
        "`67.4913`",
        "must not be pooled",
        "Do not claim direct 50-state Bishan scale-up success",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "Constrained MDP/CPO/RCPO",
        "does not mean the paper is ready for final submission",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{AUTHOR_DECISION_MATRIX}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{AUTHOR_DECISION_MATRIX}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{AUTHOR_DECISION_MATRIX}:{line_no}: positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{AUTHOR_DECISION_MATRIX}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    checklist_items = [
        line
        for line in markdown_section(text, "## Completion checklist").splitlines()
        if line.startswith("- [ ]")
    ]
    if len(checklist_items) < 12:
        missing_tokens.append(
            f"{AUTHOR_DECISION_MATRIX}: {len(checklist_items)} checklist items"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_author_decision_matrix_current",
            False,
            "Paper10 author decision matrix gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_author_decision_matrix_current",
        True,
        "Paper10 author decision matrix is current and claim-bounded",
    )


ORIGINAL_VISION_POSITIVE_CLAIM_CUE = re.compile(
    r"\b("
    r"claim(?:s|ed|ing)?"
    r"|prove(?:s|d|n|ing)?"
    r"|support(?:s|ed|ing)?"
    r"|show(?:s|ed|ing)?"
    r"|demonstrate(?:s|d|ing)?"
    r"|validate(?:s|d|ing)?"
    r"|establish(?:es|ed|ing)?"
    r"|confirm(?:s|ed|ing)?"
    r")\b",
    re.IGNORECASE,
)
ORIGINAL_VISION_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not"
    r"|don't"
    r"|must not"
    r"|should not"
    r"|may not"
    r"|cannot"
    r"|can't"
    r"|not sufficient"
    r"|insufficient"
    r"|does not"
    r"|do not support"
    r"|not supported"
    r"|unsupported"
    r"|no new conclusion"
    r")\b",
    re.IGNORECASE,
)
ORIGINAL_VISION_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
ORIGINAL_VISION_PROHIBITED_CLAIM_TARGETS = (
    re.compile(
        r"\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bsuccess\b"
        r"|\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bsuccess\b"
        r"|\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bsuccess\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b50[- ]state\b.{0,80}\bscale[- ]?up\b"
        r"|\bscale[- ]?up\b.{0,80}\b50[- ]state\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bbishan[- ]to[- ]dongxing\b.{0,120}\btransfer\b.{0,80}\bsuperiority\b"
        r"|\bbishan[- ]to[- ]dongxing\b.{0,120}\bsuperiority\b"
        r"|\btransfer\b.{0,80}\bsuperiority\b.{0,120}\bbishan[- ]to[- ]dongxing\b",
        re.IGNORECASE,
    ),
)


def is_original_vision_positive_claim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in ORIGINAL_VISION_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if ORIGINAL_VISION_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if not ORIGINAL_VISION_POSITIVE_CLAIM_CUE.search(clause):
            continue
        if any(
            target.search(clause)
            for target in ORIGINAL_VISION_PROHIBITED_CLAIM_TARGETS
        ):
            return True
    return False


def check_original_vision_validation_registry_current(root: Path) -> CheckResult:
    paths = [
        root / ORIGINAL_VISION_DESIGN,
        root / ORIGINAL_VISION_REGISTRY,
    ]
    missing = [path for path in paths if not path.exists()]
    if missing:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing: " + ", ".join(str(path.relative_to(root)) for path in missing),
        )

    hits = []
    for path in paths:
        rel_path = path.relative_to(root)
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            if is_original_vision_positive_claim(line):
                hits.append(f"{rel_path}:{line_no}: {line.strip()}")
    if hits:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "forbidden validation wording: " + " | ".join(hits),
        )

    registry_text = read_text(root / ORIGINAL_VISION_REGISTRY)
    required_reference = ORIGINAL_VISION_DESIGN.as_posix()
    design_spec = markdown_section_outside_code_fences(registry_text, "## Design Spec")
    if required_reference not in design_spec:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing registry ## Design Spec reference: " + required_reference,
        )
    if not has_markdown_heading_outside_code_fences(registry_text, "## Claim Lock"):
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing registry section: ## Claim Lock",
        )

    return CheckResult(
        "original_vision_validation_registry_current",
        True,
        "original-vision validation design and registry are current and guarded",
    )


CHECKS: tuple[Callable[[Path], CheckResult], ...] = (
    check_required_paths_exist,
    check_archive_manifest_required_fields,
    check_archive_manifest_included_paths_resolve,
    check_excluded_paths_not_tracked,
    check_public_submission_placeholders_absent,
    check_public_data_route_wording_specific,
    check_forbidden_50_state_claims,
    check_self_contained_manuscript_no_paper9_placeholder,
    check_citation_keys_resolve,
    check_reviewer_smoke_protocol_links,
    check_integrated_dongxing_source_data_links,
    check_dongxing_data_availability_routes,
    check_integrated_figure_table_numbering_frozen,
    check_submission_blocker_decision_packet_current,
    check_integrated_target_venue_conversion_checklist_current,
    check_integrated_citation_statistics_policy_current,
    check_ceus_reviewer_improvement_packet_current,
    check_ceus_research_article_manuscript_draft_current,
    check_ceus_stage3_manuscript_reframe_current,
    check_ceus_stage3_manuscript_draft_current,
    check_paper10_project_proposal_report_current,
    check_paper10_author_decision_matrix_current,
    check_original_vision_validation_registry_current,
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
