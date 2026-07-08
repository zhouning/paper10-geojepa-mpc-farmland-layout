# Paper10 Post-Guard Submission-Readiness Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic post-guard submission-readiness refresh that keeps Paper10 on a bounded no-go submission boundary while clearly separating algorithm closure from unresolved author submission decisions.

**Architecture:** Keep the change additive. Add one source-derived experiment module that reads the tracked post-guard closure, blocker, rights, boundary, and export artifacts and writes JSON/Markdown refresh artifacts. Extend preflight to require the refresh and reject final-submission overclaims without changing training, rollout, guard, plotting, or historical June records.

**Tech Stack:** Python standard library, pytest, existing Paper10 experiment result artifacts, existing `scripts/paper10/preflight_submission_checks.py`.

---

## File Structure

Create:

- `paper10_geojepa_mpc/experiments/post_guard_submission_readiness_refresh.py`
  Deterministic source-derived builder, Markdown renderer, writer, and CLI.
- `paper10_geojepa_mpc/tests/test_post_guard_submission_readiness_refresh.py`
  Unit tests for payload values, source boundaries, unresolved author-decision fields, claim locks, Markdown, and file writing.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json`
  Machine-readable post-guard submission-readiness refresh artifact.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md`
  Author-facing post-guard submission-readiness refresh artifact.

Modify:

- `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  Add preflight registration, minimal fixture, missing-file, malformed-payload, and overclaim tests.
- `scripts/paper10/preflight_submission_checks.py`
  Add constants, required paths, final-submission overclaim helper, refresh check, and `CHECKS` registration.

Do not modify:

- Training, rollout, label generation, plotting, true-reward guard algorithm code, or historical June source records.
- Any repository DOI, licence, data-access route, reviewer route, citation decision, statistical test decision, or journal export decision unless the author provides it explicitly.
- `2503.05774v1.pdf`.

---

### Task 1: Add Submission-Readiness Refresh Builder RED Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_post_guard_submission_readiness_refresh.py`
- Create later: `paper10_geojepa_mpc/experiments/post_guard_submission_readiness_refresh.py`

- [ ] **Step 1: Write failing builder tests**

Create `paper10_geojepa_mpc/tests/test_post_guard_submission_readiness_refresh.py`:

```python
import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.post_guard_submission_readiness_refresh import (
    build_post_guard_submission_readiness_refresh,
    post_guard_submission_readiness_refresh_markdown,
    write_post_guard_submission_readiness_refresh,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
POST_GUARD_CLOSURE_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
POST_GUARD_CLOSURE_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
SUBMISSION_BLOCKER_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
FINAL_EXPORT_PACKAGE = (
    RESULTS / "e0_paper10_final_figure_table_export_package_2026-06-20.md"
)


EXPECTED_FIELDS = [
    "repository_doi_or_anonymous_reviewer_link",
    "code_licence",
    "generated_data_and_checkpoint_model_weight_rights",
    "full_bishan_tool2_access_route",
    "gpkg_root_geospatial_input_access_route",
    "dongxing_neijiang_prepared_data_access_route",
    "reviewer_data_access",
    "citation_policy",
    "statistical_reporting_policy",
    "main_figure_1_and_journal_export_rules",
]


def test_build_post_guard_submission_refresh_keeps_submission_blocked():
    payload = build_post_guard_submission_readiness_refresh(output_date="2026-07-08")

    assert payload["date"] == "2026-07-08"
    assert payload["refresh_type"] == "post_guard_submission_readiness_refresh"
    assert payload["status"] == "not_submission_ready"
    assert payload["source_boundary"] == {
        "new_experimental_claim": False,
        "reran_rollouts": False,
        "reran_training": False,
        "submission_approval": False,
        "source": (
            "tracked Paper10 post-guard closure and submission blocker "
            "artifacts only"
        ),
    }
    assert payload["source_files"]["post_guard_closure_json"].endswith(
        "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
    )
    assert payload["source_files"]["submission_boundary_md"].endswith(
        "e0_paper10_submission_readiness_boundary_2026-06-26.md"
    )

    algorithm = payload["algorithm_state"]
    assert algorithm["post_guard_bounded_algorithm_closure_current"] is True
    assert algorithm["resume_broad_algorithm_redesign"] is False
    assert algorithm["primary_guard"] == {
        "audit_set": "rewardtop7",
        "switch_margin": 1.5,
        "n_seeds": 20,
        "mean_delta_vs_baseline": 6.304141816329158,
    }

    submission = payload["submission_state"]
    assert submission == {
        "final_submission_blocked": True,
        "status_reason": "author decisions unresolved",
        "preflight_pass_does_not_mean_submission_ready": True,
    }

    fields = payload["author_decision_fields"]
    assert [field["field"] for field in fields] == EXPECTED_FIELDS
    for field in fields:
        assert field["status"] == "unresolved"
        assert field["must_be_author_supplied"] is True
        assert field["closeout_required_before_submission"] is True

    assert payload["claim_locks"] == {
        "final_submission_readiness_supported": False,
        "direct_50state_scaleup_supported": False,
        "robust_transfer_superiority_supported": False,
        "deployment_ready_supported": False,
        "universal_fixed_margin_supported": False,
    }


def test_post_guard_submission_refresh_markdown_reports_unresolved_author_fields():
    payload = build_post_guard_submission_readiness_refresh(output_date="2026-07-08")
    text = post_guard_submission_readiness_refresh_markdown(payload)

    for token in [
        "# Paper10 post-guard submission-readiness refresh",
        "Status: not_submission_ready",
        "source-derived; no rollout or training rerun; no submission approval",
        "post-guard bounded algorithm closure is current",
        "rewardtop7 margin=1.50",
        "final submission remains blocked",
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data and checkpoint/model-weight rights",
        "full Bishan Tool2 route",
        "GPKG-root geospatial route",
        "Dongxing/Neijiang prepared-data route",
        "reviewer data access",
        "citation policy",
        "statistical reporting policy",
        "Main Figure 1 / journal export rules",
        "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json",
        "e0_submission_blocker_decision_packet_2026-06-11.md",
        "e0_data_access_and_rights_decision_register_2026-06-09.md",
        "e0_paper10_submission_readiness_boundary_2026-06-26.md",
        "e0_paper10_final_figure_table_export_package_2026-06-20.md",
        "not final submission readiness",
        "Do not treat this refresh as final submission readiness.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not claim a universal fixed switch margin.",
    ]:
        assert token in text


def test_write_post_guard_submission_refresh_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "submission_refresh.json"
    output_md = tmp_path / "submission_refresh.md"

    payload = write_post_guard_submission_readiness_refresh(
        post_guard_closure_json=POST_GUARD_CLOSURE_JSON,
        post_guard_closure_md=POST_GUARD_CLOSURE_MD,
        submission_blocker_packet=SUBMISSION_BLOCKER_PACKET,
        data_access_rights_register=DATA_ACCESS_RIGHTS_REGISTER,
        submission_boundary_md=SUBMISSION_BOUNDARY_MD,
        final_export_package=FINAL_EXPORT_PACKAGE,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        post_guard_submission_readiness_refresh_markdown(payload)
    )
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_submission_readiness_refresh.py -q -p no:cacheprovider
```

Expected: collection fails with `ModuleNotFoundError` for
`paper10_geojepa_mpc.experiments.post_guard_submission_readiness_refresh`.

---

### Task 2: Implement Submission-Readiness Refresh Builder GREEN

**Files:**
- Create: `paper10_geojepa_mpc/experiments/post_guard_submission_readiness_refresh.py`

- [ ] **Step 1: Add deterministic module skeleton and constants**

Create `paper10_geojepa_mpc/experiments/post_guard_submission_readiness_refresh.py`:

```python
"""Source-derived post-guard submission-readiness refresh for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_POST_GUARD_CLOSURE_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
DEFAULT_POST_GUARD_CLOSURE_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
DEFAULT_SUBMISSION_BLOCKER_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
DEFAULT_DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
DEFAULT_SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
DEFAULT_FINAL_EXPORT_PACKAGE = (
    RESULTS / "e0_paper10_final_figure_table_export_package_2026-06-20.md"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md"
)


AUTHOR_DECISION_FIELDS = [
    {
        "field": "repository_doi_or_anonymous_reviewer_link",
        "label": "repository DOI or anonymous reviewer link",
        "required_input": (
            "Archive platform, persistent identifier or anonymous reviewer link, "
            "version, access timing, and anonymity status."
        ),
    },
    {
        "field": "code_licence",
        "label": "code licence",
        "required_input": (
            "Named software licence or institutional restriction covering only "
            "licensable code and scripts."
        ),
    },
    {
        "field": "generated_data_and_checkpoint_model_weight_rights",
        "label": "generated-data and checkpoint/model-weight rights",
        "required_input": (
            "Rights terms for generated JSON, Markdown, CSV, NPZ labels, "
            "checkpoints, model weights, and shareable source-data files."
        ),
    },
    {
        "field": "full_bishan_tool2_access_route",
        "label": "full Bishan Tool2 route",
        "required_input": (
            "Public DOI or controlled-access route for full transitions and "
            "pairwise files, including owner, eligibility, and reviewer route."
        ),
    },
    {
        "field": "gpkg_root_geospatial_input_access_route",
        "label": "GPKG-root geospatial route",
        "required_input": (
            "Public DOI or controlled-access route for GPKG-root geospatial "
            "inputs, block products, and township inputs."
        ),
    },
    {
        "field": "dongxing_neijiang_prepared_data_access_route",
        "label": "Dongxing/Neijiang prepared-data route",
        "required_input": (
            "Public DOI or controlled-access route for prepared external-region "
            "products, parcel assignments, environment files, and slope-enriched "
            "inputs."
        ),
    },
    {
        "field": "reviewer_data_access",
        "label": "reviewer data access",
        "required_input": (
            "Whether reviewers receive public downloads, private links, or "
            "controlled-access credentials."
        ),
    },
    {
        "field": "citation_policy",
        "label": "citation policy",
        "required_input": (
            "Acceptable source types, local-only source replacement route, "
            "preprint policy, and final reference style."
        ),
    },
    {
        "field": "statistical_reporting_policy",
        "label": "statistical reporting policy",
        "required_input": (
            "Descriptive-only reporting decision or defined tests, comparison "
            "groups, multiplicity handling, and precision policy."
        ),
    },
    {
        "field": "main_figure_1_and_journal_export_rules",
        "label": "Main Figure 1 / journal export rules",
        "required_input": (
            "Final schematic artwork and journal-specific figure/table count, "
            "source-data naming, and PDF/SVG/raster export rules."
        ),
    },
]
```

- [ ] **Step 2: Add loading helpers and field builder**

Add:

```python
def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _require_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _author_decision_fields() -> list[dict[str, Any]]:
    return [
        {
            **field,
            "status": "unresolved",
            "must_be_author_supplied": True,
            "closeout_required_before_submission": True,
        }
        for field in AUTHOR_DECISION_FIELDS
    ]
```

- [ ] **Step 3: Add payload builder**

Add:

```python
def build_post_guard_submission_readiness_refresh(
    *,
    post_guard_closure_json: str | Path = DEFAULT_POST_GUARD_CLOSURE_JSON,
    post_guard_closure_md: str | Path = DEFAULT_POST_GUARD_CLOSURE_MD,
    submission_blocker_packet: str | Path = DEFAULT_SUBMISSION_BLOCKER_PACKET,
    data_access_rights_register: str | Path = DEFAULT_DATA_ACCESS_RIGHTS_REGISTER,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    final_export_package: str | Path = DEFAULT_FINAL_EXPORT_PACKAGE,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    closure_json_path = Path(post_guard_closure_json)
    closure_md_path = Path(post_guard_closure_md)
    blocker_path = Path(submission_blocker_packet)
    rights_path = Path(data_access_rights_register)
    boundary_path = Path(submission_boundary_md)
    export_path = Path(final_export_package)

    closure = _load_json(closure_json_path)
    for path in (
        closure_md_path,
        blocker_path,
        rights_path,
        boundary_path,
        export_path,
    ):
        _require_text(path)

    guard = closure["primary_guard"]
    return {
        "date": output_date,
        "refresh_type": "post_guard_submission_readiness_refresh",
        "status": "not_submission_ready",
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "reran_training": False,
            "submission_approval": False,
            "source": (
                "tracked Paper10 post-guard closure and submission blocker "
                "artifacts only"
            ),
        },
        "source_files": {
            "post_guard_closure_json": closure_json_path.as_posix(),
            "post_guard_closure_md": closure_md_path.as_posix(),
            "submission_blocker_packet": blocker_path.as_posix(),
            "data_access_rights_register": rights_path.as_posix(),
            "submission_boundary_md": boundary_path.as_posix(),
            "final_export_package": export_path.as_posix(),
        },
        "algorithm_state": {
            "post_guard_bounded_algorithm_closure_current": True,
            "resume_broad_algorithm_redesign": False,
            "primary_guard": {
                "audit_set": guard["audit_set"],
                "switch_margin": float(guard["switch_margin"]),
                "n_seeds": int(guard["n_seeds"]),
                "mean_delta_vs_baseline": float(guard["mean_delta_vs_baseline"]),
            },
        },
        "submission_state": {
            "final_submission_blocked": True,
            "status_reason": "author decisions unresolved",
            "preflight_pass_does_not_mean_submission_ready": True,
        },
        "author_decision_fields": _author_decision_fields(),
        "claim_locks": {
            "final_submission_readiness_supported": False,
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_supported": False,
            "universal_fixed_margin_supported": False,
        },
    }
```

- [ ] **Step 4: Add Markdown renderer**

Add:

```python
def post_guard_submission_readiness_refresh_markdown(payload: dict[str, Any]) -> str:
    guard = payload["algorithm_state"]["primary_guard"]
    lines = [
        "# Paper10 post-guard submission-readiness refresh",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: not_submission_ready",
        "",
        (
            "Status note: source-derived; no rollout or training rerun; "
            "no submission approval."
        ),
        "",
        "This refresh is not final submission readiness.",
        (
            "It records that post-guard bounded algorithm closure is current, "
            "while final submission remains blocked by unresolved author "
            "decisions."
        ),
        "",
        "## Source basis",
        "",
    ]
    for source in payload["source_files"].values():
        lines.append(f"- `{Path(source).name}`")
    lines.extend(
        [
            "",
            "## Algorithm state",
            "",
            (
                "The post-guard bounded algorithm closure is current under "
                f"`{guard['audit_set']} margin={guard['switch_margin']:.2f}`."
            ),
            f"- seeds: {guard['n_seeds']}",
            f"- mean delta vs baseline: {guard['mean_delta_vs_baseline']:.4f}",
            "- broad algorithm redesign: not resumed for the bounded route",
            "",
            "## Submission state",
            "",
            "The final submission remains blocked.",
            (
                "Passing repository preflight means the no-go boundary is "
                "tracked and guarded; it does not mean the paper is ready to "
                "submit."
            ),
            "",
            "## Author-decision intake",
            "",
            "| field | status | required author input |",
            "|---|---|---|",
        ]
    )
    for field in payload["author_decision_fields"]:
        lines.append(
            f"| {field['label']} | {field['status']} | "
            f"{field['required_input']} |"
        )
    lines.extend(
        [
            "",
            "## Claim locks",
            "",
            "Do not treat this refresh as final submission readiness.",
            "Do not claim direct 50-state Bishan scale-up success.",
            "Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "Do not claim deployment-ready cadastral planning.",
            "Do not claim a universal fixed switch margin.",
            "",
        ]
    )
    return "\n".join(lines)
```

- [ ] **Step 5: Add writer and CLI**

Add:

```python
def write_post_guard_submission_readiness_refresh(
    *,
    post_guard_closure_json: str | Path = DEFAULT_POST_GUARD_CLOSURE_JSON,
    post_guard_closure_md: str | Path = DEFAULT_POST_GUARD_CLOSURE_MD,
    submission_blocker_packet: str | Path = DEFAULT_SUBMISSION_BLOCKER_PACKET,
    data_access_rights_register: str | Path = DEFAULT_DATA_ACCESS_RIGHTS_REGISTER,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    final_export_package: str | Path = DEFAULT_FINAL_EXPORT_PACKAGE,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    payload = build_post_guard_submission_readiness_refresh(
        post_guard_closure_json=post_guard_closure_json,
        post_guard_closure_md=post_guard_closure_md,
        submission_blocker_packet=submission_blocker_packet,
        data_access_rights_register=data_access_rights_register,
        submission_boundary_md=submission_boundary_md,
        final_export_package=final_export_package,
        output_date=output_date,
    )
    output_json_path = Path(output_json)
    output_md_path = Path(output_md)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path.write_text(
        post_guard_submission_readiness_refresh_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 post-guard submission-readiness refresh."
    )
    parser.add_argument(
        "--post-guard-closure-json",
        default=str(DEFAULT_POST_GUARD_CLOSURE_JSON),
    )
    parser.add_argument(
        "--post-guard-closure-md",
        default=str(DEFAULT_POST_GUARD_CLOSURE_MD),
    )
    parser.add_argument(
        "--submission-blocker-packet",
        default=str(DEFAULT_SUBMISSION_BLOCKER_PACKET),
    )
    parser.add_argument(
        "--data-access-rights-register",
        default=str(DEFAULT_DATA_ACCESS_RIGHTS_REGISTER),
    )
    parser.add_argument(
        "--submission-boundary-md",
        default=str(DEFAULT_SUBMISSION_BOUNDARY_MD),
    )
    parser.add_argument(
        "--final-export-package",
        default=str(DEFAULT_FINAL_EXPORT_PACKAGE),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-08")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_post_guard_submission_readiness_refresh(
        post_guard_closure_json=args.post_guard_closure_json,
        post_guard_closure_md=args.post_guard_closure_md,
        submission_blocker_packet=args.submission_blocker_packet,
        data_access_rights_register=args.data_access_rights_register,
        submission_boundary_md=args.submission_boundary_md,
        final_export_package=args.final_export_package,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run focused test and verify GREEN**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_submission_readiness_refresh.py -q -p no:cacheprovider
```

Expected: `3 passed`.

---

### Task 3: Generate Submission-Readiness Refresh Artifacts

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md`

- [ ] **Step 1: Run the refresh module CLI**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.post_guard_submission_readiness_refresh
```

Expected: the command prints the JSON payload and writes both refresh artifacts
under `paper10_geojepa_mpc/experiments/results/`.

- [ ] **Step 2: Inspect generated Markdown for required tokens**

Run:

```powershell
rg -n "not_submission_ready|source-derived; no rollout or training rerun; no submission approval|rewardtop7 margin=1.50|final submission remains blocked|repository DOI or anonymous reviewer link|code licence|generated-data and checkpoint/model-weight rights|GPKG-root geospatial route|Do not treat this refresh as final submission readiness" paper10_geojepa_mpc\experiments\results\e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md
```

Expected: each token appears at least once.

- [ ] **Step 3: Re-run builder tests against generated artifacts**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_submission_readiness_refresh.py -q -p no:cacheprovider
```

Expected: `3 passed`.

---

### Task 4: Add Submission-Readiness Preflight RED Tests

**Files:**
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`
- Modify later: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add imports for the new check and paths**

In the import list from `scripts.paper10.preflight_submission_checks`, add:

```python
    check_paper10_post_guard_submission_readiness_refresh_current,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
```

Expected before implementation: pytest collection fails with an import error.

- [ ] **Step 2: Add refresh artifacts to the minimal fixture file list**

In `MINIMAL_PREFLIGHT_FIXTURE_FILES`, add these paths after
`PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON`:

```python
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
```

- [ ] **Step 3: Require the check in the current-repository preflight test**

In `test_submission_preflight_cli_passes_current_repository`, add:

```python
    assert "paper10_post_guard_submission_readiness_refresh_current" in payload["passed_checks"]
```

- [ ] **Step 4: Add missing-file preflight test**

Add near the post-guard closure refresh missing-file test:

```python
def test_submission_preflight_minimal_fixture_reports_missing_post_guard_submission_refresh(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_post_guard_submission_readiness_refresh_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_post_guard_submission_readiness_refresh_current")
    assert "missing Paper10 post-guard submission-readiness refresh files" in details
    assert str(PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD) in details
```

- [ ] **Step 5: Add malformed-payload and overclaim tests**

Add:

```python
def test_post_guard_submission_refresh_preflight_requires_no_go_status(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    payload_path = fixture / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["status"] = "submission_ready"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = check_paper10_post_guard_submission_readiness_refresh_current(fixture)

    assert result.name == "paper10_post_guard_submission_readiness_refresh_current"
    assert result.ok is False
    assert "status=submission_ready" in result.details


def test_post_guard_submission_refresh_preflight_rejects_ready_to_submit_claim(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    refresh = fixture / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD
    refresh.write_text(
        refresh.read_text(encoding="utf-8")
        + "\n\nThe paper is ready to submit.\n",
        encoding="utf-8",
    )

    result = check_paper10_post_guard_submission_readiness_refresh_current(fixture)

    assert result.name == "paper10_post_guard_submission_readiness_refresh_current"
    assert result.ok is False
    assert "forbidden post-guard submission-readiness wording" in result.details
    assert "ready to submit" in result.details


def test_post_guard_submission_refresh_preflight_allows_negative_guardrails(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    refresh = fixture / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD
    refresh.write_text(
        refresh.read_text(encoding="utf-8")
        + "\n\nDo not treat this refresh as final submission readiness.\n",
        encoding="utf-8",
    )

    result = check_paper10_post_guard_submission_readiness_refresh_current(fixture)

    assert result.name == "paper10_post_guard_submission_readiness_refresh_current"
    assert result.ok is True
```

- [ ] **Step 6: Run focused preflight tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: collection fails because the new preflight constants and check cannot
be imported.

---

### Task 5: Implement Submission-Readiness Preflight GREEN

**Files:**
- Modify: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add refresh path constants**

After `PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON`, add:

```python
PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md"
)
PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json"
)
```

- [ ] **Step 2: Add refresh artifacts to required paths**

In `REQUIRED_PATHS`, add after
`PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON`:

```python
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
```

- [ ] **Step 3: Add final-submission overclaim helpers**

Place this helper block near the other submission/guard overclaim helpers:

```python
POST_GUARD_SUBMISSION_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not"
    r"|not final|false|no-go|not_submission_ready|blocked|unresolved"
    r"|remains blocked|does not mean"
    r")\b",
    re.IGNORECASE,
)
POST_GUARD_SUBMISSION_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
POST_GUARD_SUBMISSION_FORBIDDEN_TARGETS = (
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\bready to submit\b", re.IGNORECASE),
    re.compile(r"\ball blockers closed\b", re.IGNORECASE),
    re.compile(r"\bsubmission_ready\b", re.IGNORECASE),
)


def is_post_guard_submission_readiness_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in POST_GUARD_SUBMISSION_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if POST_GUARD_SUBMISSION_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(
            target.search(clause)
            for target in POST_GUARD_SUBMISSION_FORBIDDEN_TARGETS
        ):
            return True
    return False
```

- [ ] **Step 4: Reuse `nested_value`**

Confirm `nested_value` already exists:

```powershell
rg -n "def nested_value" scripts\paper10\preflight_submission_checks.py
```

Expected: one existing helper. If it is absent, add:

```python
def nested_value(payload: dict, keys: tuple[str, ...]):
    value = payload
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value
```

- [ ] **Step 5: Add the post-guard submission-readiness preflight check**

Place before `check_paper10_post_guard_experiment_closure_refresh_current` or
immediately after it:

```python
def check_paper10_post_guard_submission_readiness_refresh_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        DATA_ACCESS_RIGHTS_REGISTER,
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "missing Paper10 post-guard submission-readiness refresh files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    required_tokens = [
        "Paper10 post-guard submission-readiness refresh",
        "Status: not_submission_ready",
        "source-derived; no rollout or training rerun; no submission approval",
        "post-guard bounded algorithm closure is current",
        "rewardtop7 margin=1.50",
        "final submission remains blocked",
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data and checkpoint/model-weight rights",
        "full Bishan Tool2 route",
        "GPKG-root geospatial route",
        "Dongxing/Neijiang prepared-data route",
        "reviewer data access",
        "citation policy",
        "statistical reporting policy",
        "Main Figure 1 / journal export rules",
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON.name,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        DATA_ACCESS_RIGHTS_REGISTER.name,
        PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
        "not final submission readiness",
        "Do not treat this refresh as final submission readiness.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not claim a universal fixed switch margin.",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-07-08",
        ("refresh_type",): "post_guard_submission_readiness_refresh",
        ("status",): "not_submission_ready",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("algorithm_state", "post_guard_bounded_algorithm_closure_current"): True,
        ("algorithm_state", "resume_broad_algorithm_redesign"): False,
        ("algorithm_state", "primary_guard", "audit_set"): "rewardtop7",
        ("algorithm_state", "primary_guard", "switch_margin"): 1.5,
        ("algorithm_state", "primary_guard", "n_seeds"): 20,
        ("algorithm_state", "primary_guard", "mean_delta_vs_baseline"): 6.304141816329158,
        ("submission_state", "final_submission_blocked"): True,
        ("submission_state", "status_reason"): "author decisions unresolved",
        ("submission_state", "preflight_pass_does_not_mean_submission_ready"): True,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("claim_locks", "direct_50state_scaleup_supported"): False,
        ("claim_locks", "robust_transfer_superiority_supported"): False,
        ("claim_locks", "deployment_ready_supported"): False,
        ("claim_locks", "universal_fixed_margin_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    expected_fields = [
        "repository_doi_or_anonymous_reviewer_link",
        "code_licence",
        "generated_data_and_checkpoint_model_weight_rights",
        "full_bishan_tool2_access_route",
        "gpkg_root_geospatial_input_access_route",
        "dongxing_neijiang_prepared_data_access_route",
        "reviewer_data_access",
        "citation_policy",
        "statistical_reporting_policy",
        "main_figure_1_and_journal_export_rules",
    ]
    fields = payload.get("author_decision_fields")
    if not isinstance(fields, list):
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
            "author_decision_fields"
        )
        fields = []
    observed_fields = [
        field.get("field") for field in fields if isinstance(field, dict)
    ]
    if observed_fields != expected_fields:
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
            f"author_decision_fields={observed_fields}"
        )
    for field in fields:
        if not isinstance(field, dict):
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                "non-dict author_decision_fields row"
            )
            continue
        name = field.get("field")
        for key, expected in (
            ("status", "unresolved"),
            ("must_be_author_supplied", True),
            ("closeout_required_before_submission", True),
        ):
            if field.get(key) != expected:
                missing_tokens.append(
                    f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                    f"author_decision_fields.{name}.{key}={field.get(key)}"
                )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD}:{line_no}: "
                f"{line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "forbidden post-guard submission-readiness wording: "
            + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "Paper10 post-guard submission-readiness refresh gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_post_guard_submission_readiness_refresh_current",
        True,
        "Paper10 post-guard submission-readiness refresh is current and no-go guarded",
    )
```

- [ ] **Step 6: Register the check**

In `CHECKS`, add after
`check_paper10_post_guard_experiment_closure_refresh_current`:

```python
    check_paper10_post_guard_submission_readiness_refresh_current,
```

- [ ] **Step 7: Run focused preflight tests and verify GREEN**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: all tests in `test_submission_preflight.py` pass.

---

### Task 6: Final Verification and Commit

**Files:**
- No additional files.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_submission_readiness_refresh.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: focused tests pass.

- [ ] **Step 2: Run Paper10 preflight**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected:

- `Paper10 preflight: PASS`
- output includes `[ok] paper10_post_guard_submission_readiness_refresh_current`

- [ ] **Step 3: Run full pytest**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 4: Run Git checks**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected:

- `git diff --check` exits 0.
- Status shows only intended tracked edits plus the pre-existing untracked
  `2503.05774v1.pdf`.

- [ ] **Step 5: Commit implementation**

Stage only:

```powershell
git add paper10_geojepa_mpc/experiments/post_guard_submission_readiness_refresh.py `
  paper10_geojepa_mpc/tests/test_post_guard_submission_readiness_refresh.py `
  paper10_geojepa_mpc/tests/test_submission_preflight.py `
  scripts/paper10/preflight_submission_checks.py `
  paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json `
  paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md
git diff --cached --check
git commit -m "exp: add post-guard submission refresh"
```

Expected: commit succeeds and does not stage `2503.05774v1.pdf`.

- [ ] **Step 6: Push**

Run:

```powershell
git push
```

Expected: `main -> main` updates on `origin`.

---

## Self-Review Notes

Spec coverage:

- Required JSON/Markdown artifact maps to Tasks 2 and 3.
- Source-derived no-go submission boundary maps to Tasks 2 and 5.
- Data-availability discipline maps to the unresolved author-decision field
  contract in Tasks 1, 2, and 5.
- Preflight gate maps to Tasks 4 and 5.
- TDD RED/GREEN cycles map to Tasks 1, 2, 4, and 5.
- Final verification maps to Task 6.

Scope check:

- The plan is one additive artifact plus one preflight gate. It does not touch
  independent training, rollout, plotting, manuscript rewriting, or archive
  release subsystems.

Placeholder scan:

- The plan contains no unresolved marker text, generic test instructions, or
  unstated implementation decisions. Author-facing unresolved submission fields
  are part of the required artifact contract, not plan gaps.

Type consistency:

- Module name is consistently `post_guard_submission_readiness_refresh`.
- Builder function is consistently `build_post_guard_submission_readiness_refresh`.
- Markdown renderer is consistently `post_guard_submission_readiness_refresh_markdown`.
- Writer is consistently `write_post_guard_submission_readiness_refresh`.
- Preflight check name is consistently
  `paper10_post_guard_submission_readiness_refresh_current`.
- Artifact constants are consistently
  `PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD` and
  `PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON`.
