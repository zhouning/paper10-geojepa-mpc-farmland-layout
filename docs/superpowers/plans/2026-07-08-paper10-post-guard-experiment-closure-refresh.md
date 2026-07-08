# Paper10 Post-Guard Experiment Closure Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a source-derived post-guard closure refresh that makes the July 8 `rewardtop7 margin=1.50` primary guard visible in Paper10 experiment-closure and submission-boundary checks.

**Architecture:** Keep the change additive. Add one deterministic experiment module that reads existing JSON/Markdown artifacts and writes a JSON/Markdown refresh packet; extend preflight to require the packet and reject overclaim wording; add tests before each production change.

**Tech Stack:** Python standard library, pytest, existing Paper10 experiment result artifacts, existing `scripts/paper10/preflight_submission_checks.py`.

---

## File Structure

Create:

- `paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py`
  Deterministic source-derived builder, Markdown renderer, writer, and CLI.
- `paper10_geojepa_mpc/tests/test_post_guard_experiment_closure_refresh.py`
  Unit tests for payload values, claim locks, source boundaries, Markdown, and file writing.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json`
  Machine-readable closure refresh artifact.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md`
  Author-facing closure refresh artifact.

Modify:

- `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  Add preflight registration, minimal fixture, missing-file, malformed-payload, and overclaim tests.
- `scripts/paper10/preflight_submission_checks.py`
  Add constants, required paths, overclaim helper, refresh check, and `CHECKS` registration.

Do not modify:

- Training, rollout, label generation, plotting, or true-reward guard algorithm code.
- Historical June experiment-freeze or closure-register artifacts.
- `2503.05774v1.pdf`.

---

### Task 1: Add Refresh Builder RED Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_post_guard_experiment_closure_refresh.py`
- Create later: `paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py`

- [ ] **Step 1: Write failing builder tests**

Create `paper10_geojepa_mpc/tests/test_post_guard_experiment_closure_refresh.py`:

```python
import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.post_guard_experiment_closure_refresh import (
    build_post_guard_experiment_closure_refresh,
    post_guard_experiment_closure_refresh_markdown,
    write_post_guard_experiment_closure_refresh,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
TRUE_REWARD_GUARD_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)
TABLE_FREEZE_JSON = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)
TABLE_FREEZE_MD = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"
)
EXPERIMENT_FREEZE_MD = (
    RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md"
)
CLOSURE_REGISTER_MD = (
    RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md"
)
SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)


def test_build_post_guard_refresh_derives_guard_values_and_locks_claims():
    payload = build_post_guard_experiment_closure_refresh(output_date="2026-07-08")

    assert payload["date"] == "2026-07-08"
    assert payload["status"] == "post_guard_experiment_closure_refresh"
    assert payload["source_boundary"] == {
        "new_experimental_claim": False,
        "reran_rollouts": False,
        "reran_training": False,
        "source": "tracked Paper10 guard and closure artifacts only",
    }
    assert payload["source_files"]["true_reward_guard_json"].endswith(
        "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
    )

    guard = payload["primary_guard"]
    assert guard["audit_set"] == "rewardtop7"
    assert guard["switch_margin"] == pytest.approx(1.5)
    assert guard["n_seeds"] == 20
    assert guard["guard_mean_reward"] == pytest.approx(72.19178534319884)
    assert guard["baseline_mean_reward"] == pytest.approx(65.8876435268697)
    assert guard["mean_delta_vs_baseline"] == pytest.approx(6.304141816329158)
    assert guard["seed_wins"] == 20
    assert guard["bootstrap_95ci_delta_lower"] == pytest.approx(4.140109129548553)
    assert guard["mean_audit_action_count"] == pytest.approx(7.7605)
    assert guard["dual7x7_mean_audit_action_count"] == pytest.approx(8.1905)

    assert payload["closure_decision"] == {
        "default_next_phase": "bounded_manuscript_assembly",
        "resume_broad_algorithm_redesign": False,
        "historical_june_records_mutated": False,
    }
    assert payload["submission_boundary"]["status"] == "not_submission_ready"
    assert "repository DOI or anonymous reviewer link" in payload["submission_boundary"]["open_blockers"]
    assert payload["claim_locks"] == {
        "direct_50state_scaleup_supported": False,
        "robust_transfer_superiority_supported": False,
        "deployment_ready_supported": False,
        "universal_fixed_margin_supported": False,
        "final_submission_readiness_supported": False,
    }


def test_post_guard_refresh_markdown_reports_sources_values_and_negative_guardrails():
    payload = build_post_guard_experiment_closure_refresh(output_date="2026-07-08")
    text = post_guard_experiment_closure_refresh_markdown(payload)

    for token in [
        "# Paper10 post-guard experiment-closure refresh",
        "Status: post_guard_experiment_closure_refresh",
        "source-derived; no rollout or training rerun",
        "rewardtop7 margin=1.50",
        "72.1918",
        "65.8876",
        "6.3041",
        "20 / 20",
        "4.1401",
        "7.7605",
        "8.1905",
        "e0_paper10_true_reward_guard_readiness_2026-07-08.json",
        "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        "e0_paper10_experiment_closure_register_2026-06-27.md",
        "e0_paper10_submission_readiness_boundary_2026-06-26.md",
        "closure update, not a new experiment",
        "not final submission readiness",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
    ]:
        assert token in text


def test_write_post_guard_refresh_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "refresh.json"
    output_md = tmp_path / "refresh.md"

    payload = write_post_guard_experiment_closure_refresh(
        true_reward_guard_json=TRUE_REWARD_GUARD_JSON,
        true_reward_guard_md=TRUE_REWARD_GUARD_MD,
        table_freeze_json=TABLE_FREEZE_JSON,
        table_freeze_md=TABLE_FREEZE_MD,
        experiment_freeze_md=EXPERIMENT_FREEZE_MD,
        closure_register_md=CLOSURE_REGISTER_MD,
        submission_boundary_md=SUBMISSION_BOUNDARY_MD,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        post_guard_experiment_closure_refresh_markdown(payload)
    )
```

- [ ] **Step 2: Run focused test and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_experiment_closure_refresh.py -q -p no:cacheprovider
```

Expected: collection fails with `ModuleNotFoundError` for
`paper10_geojepa_mpc.experiments.post_guard_experiment_closure_refresh`.

---

### Task 2: Implement Refresh Builder GREEN

**Files:**
- Create: `paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py`

- [ ] **Step 1: Add the deterministic module skeleton and constants**

Create `paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py`:

```python
"""Source-derived post-guard closure refresh for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
DEFAULT_TRUE_REWARD_GUARD_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)
DEFAULT_TABLE_FREEZE_JSON = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)
DEFAULT_TABLE_FREEZE_MD = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"
)
DEFAULT_EXPERIMENT_FREEZE_MD = (
    RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md"
)
DEFAULT_CLOSURE_REGISTER_MD = (
    RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md"
)
DEFAULT_SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)


OPEN_SUBMISSION_BLOCKERS = [
    "repository DOI or anonymous reviewer link",
    "code licence",
    "generated-data rights and checkpoint or model-weight rights",
    "full Bishan Tool2 data access route",
    "GPKG-root geospatial input access route",
    "Dongxing/Neijiang prepared-data access route",
    "citation policy for local-only sources, preprints, and final reference style",
    "statistical reporting policy for descriptive results versus hypothesis tests",
    "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
]
```

- [ ] **Step 2: Add JSON loading and guard extraction helpers**

Add:

```python
def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _require_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _guard_values(true_reward_guard: dict[str, Any], table_freeze: dict[str, Any]) -> dict[str, Any]:
    primary = true_reward_guard["primary_guard"]
    stats = true_reward_guard["primary_paired_stats"]
    guard_stats = stats["candidate_guard_summary"]
    table_rows = table_freeze["tables"]["table_true_reward_guard_readiness"]
    table_row = table_rows[0]
    return {
        "audit_set": primary["audit_set"],
        "switch_margin": float(primary["switch_margin"]),
        "n_seeds": int(primary["n_seeds"]),
        "guard_mean_reward": float(primary["candidate_mean_reward"]),
        "baseline_mean_reward": float(primary["baseline_mean_reward"]),
        "mean_delta_vs_baseline": float(primary["mean_delta_vs_baseline"]),
        "seed_wins": int(primary["seed_wins"]),
        "bootstrap_95ci_delta_lower": float(stats["bootstrap_95ci_delta"][0]),
        "mean_audit_action_count": float(guard_stats["mean_audit_action_count"]),
        "dual7x7_mean_audit_action_count": float(
            table_row["dual7x7_mean_audit_action_count"]
        ),
    }
```

- [ ] **Step 3: Add payload builder**

Add:

```python
def build_post_guard_experiment_closure_refresh(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    true_reward_guard_md: str | Path = DEFAULT_TRUE_REWARD_GUARD_MD,
    table_freeze_json: str | Path = DEFAULT_TABLE_FREEZE_JSON,
    table_freeze_md: str | Path = DEFAULT_TABLE_FREEZE_MD,
    experiment_freeze_md: str | Path = DEFAULT_EXPERIMENT_FREEZE_MD,
    closure_register_md: str | Path = DEFAULT_CLOSURE_REGISTER_MD,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    true_reward_guard_path = Path(true_reward_guard_json)
    true_reward_guard_md_path = Path(true_reward_guard_md)
    table_freeze_json_path = Path(table_freeze_json)
    table_freeze_md_path = Path(table_freeze_md)
    experiment_freeze_path = Path(experiment_freeze_md)
    closure_register_path = Path(closure_register_md)
    submission_boundary_path = Path(submission_boundary_md)

    true_reward_guard = _load_json(true_reward_guard_path)
    table_freeze = _load_json(table_freeze_json_path)
    for path in (
        true_reward_guard_md_path,
        table_freeze_md_path,
        experiment_freeze_path,
        closure_register_path,
        submission_boundary_path,
    ):
        _require_text(path)

    return {
        "date": output_date,
        "status": "post_guard_experiment_closure_refresh",
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "reran_training": False,
            "source": "tracked Paper10 guard and closure artifacts only",
        },
        "source_files": {
            "true_reward_guard_json": true_reward_guard_path.as_posix(),
            "true_reward_guard_md": true_reward_guard_md_path.as_posix(),
            "table_freeze_json": table_freeze_json_path.as_posix(),
            "table_freeze_md": table_freeze_md_path.as_posix(),
            "experiment_freeze_md": experiment_freeze_path.as_posix(),
            "closure_register_md": closure_register_path.as_posix(),
            "submission_boundary_md": submission_boundary_path.as_posix(),
        },
        "primary_guard": _guard_values(true_reward_guard, table_freeze),
        "closure_decision": {
            "default_next_phase": "bounded_manuscript_assembly",
            "resume_broad_algorithm_redesign": False,
            "historical_june_records_mutated": False,
        },
        "submission_boundary": {
            "status": "not_submission_ready",
            "open_blockers": OPEN_SUBMISSION_BLOCKERS,
        },
        "claim_locks": {
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_supported": False,
            "universal_fixed_margin_supported": False,
            "final_submission_readiness_supported": False,
        },
    }
```

- [ ] **Step 4: Add Markdown renderer**

Add:

```python
def post_guard_experiment_closure_refresh_markdown(payload: dict[str, Any]) -> str:
    guard = payload["primary_guard"]
    lines = [
        "# Paper10 post-guard experiment-closure refresh",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: post_guard_experiment_closure_refresh",
        "",
        "Status note: source-derived; no rollout or training rerun.",
        "",
        "This refresh is a closure update, not a new experiment.",
        "It records how the July 8 true-reward guard readiness evidence changes the bounded Paper10 experiment-closure reading without mutating historical June records.",
        "",
        "## Source basis",
        "",
    ]
    for source in payload["source_files"].values():
        lines.append(f"- `{Path(source).name}`")
    lines.extend(
        [
            "",
            "## Current primary guard",
            "",
            "The current primary true-reward guard is `rewardtop7 margin=1.50` for Bishan 20x16/top5.",
            "",
            "| metric | value |",
            "|---|---:|",
            f"| baseline mean reward | {guard['baseline_mean_reward']:.4f} |",
            f"| guard mean reward | {guard['guard_mean_reward']:.4f} |",
            f"| mean delta vs baseline | {guard['mean_delta_vs_baseline']:.4f} |",
            f"| seed wins | {guard['seed_wins']} / {guard['n_seeds']} |",
            f"| bootstrap 95% CI lower | {guard['bootstrap_95ci_delta_lower']:.4f} |",
            f"| mean audited actions | {guard['mean_audit_action_count']:.4f} |",
            f"| dual7x7 mean audited actions | {guard['dual7x7_mean_audit_action_count']:.4f} |",
            "",
            "## Closure decision",
            "",
            "Default next phase: `bounded_manuscript_assembly`.",
            "",
            "Do not resume broad algorithm redesign for the bounded route.",
            "Do not rewrite the June experiment-freeze audit or closure register as if those records originally included this July 8 guard.",
            "",
            "## Submission boundary",
            "",
            "Submission status remains `not_submission_ready`; this is not final submission readiness.",
            "",
            "Open blockers remain:",
        ]
    )
    for blocker in payload["submission_boundary"]["open_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## Claim locks",
            "",
            "Do not claim a universal fixed switch margin.",
            "Do not claim direct 50-state Bishan scale-up success.",
            "Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "Do not claim deployment-ready cadastral planning.",
            "Do not treat this refresh as final submission readiness.",
            "",
        ]
    )
    return "\n".join(lines)
```

- [ ] **Step 5: Add writer, CLI parser, and main**

Add:

```python
def write_post_guard_experiment_closure_refresh(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    true_reward_guard_md: str | Path = DEFAULT_TRUE_REWARD_GUARD_MD,
    table_freeze_json: str | Path = DEFAULT_TABLE_FREEZE_JSON,
    table_freeze_md: str | Path = DEFAULT_TABLE_FREEZE_MD,
    experiment_freeze_md: str | Path = DEFAULT_EXPERIMENT_FREEZE_MD,
    closure_register_md: str | Path = DEFAULT_CLOSURE_REGISTER_MD,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    payload = build_post_guard_experiment_closure_refresh(
        true_reward_guard_json=true_reward_guard_json,
        true_reward_guard_md=true_reward_guard_md,
        table_freeze_json=table_freeze_json,
        table_freeze_md=table_freeze_md,
        experiment_freeze_md=experiment_freeze_md,
        closure_register_md=closure_register_md,
        submission_boundary_md=submission_boundary_md,
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
        post_guard_experiment_closure_refresh_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 post-guard experiment-closure refresh."
    )
    parser.add_argument("--true-reward-guard-json", default=str(DEFAULT_TRUE_REWARD_GUARD_JSON))
    parser.add_argument("--true-reward-guard-md", default=str(DEFAULT_TRUE_REWARD_GUARD_MD))
    parser.add_argument("--table-freeze-json", default=str(DEFAULT_TABLE_FREEZE_JSON))
    parser.add_argument("--table-freeze-md", default=str(DEFAULT_TABLE_FREEZE_MD))
    parser.add_argument("--experiment-freeze-md", default=str(DEFAULT_EXPERIMENT_FREEZE_MD))
    parser.add_argument("--closure-register-md", default=str(DEFAULT_CLOSURE_REGISTER_MD))
    parser.add_argument("--submission-boundary-md", default=str(DEFAULT_SUBMISSION_BOUNDARY_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-08")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_post_guard_experiment_closure_refresh(
        true_reward_guard_json=args.true_reward_guard_json,
        true_reward_guard_md=args.true_reward_guard_md,
        table_freeze_json=args.table_freeze_json,
        table_freeze_md=args.table_freeze_md,
        experiment_freeze_md=args.experiment_freeze_md,
        closure_register_md=args.closure_register_md,
        submission_boundary_md=args.submission_boundary_md,
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
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_experiment_closure_refresh.py -q -p no:cacheprovider
```

Expected: `3 passed`.

---

### Task 3: Generate Refresh Artifacts

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md`

- [ ] **Step 1: Run the refresh module CLI**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.post_guard_experiment_closure_refresh
```

Expected: the command prints the JSON payload and writes both refresh artifacts
under `paper10_geojepa_mpc/experiments/results/`.

- [ ] **Step 2: Inspect the generated Markdown for required tokens**

Run:

```powershell
rg -n "rewardtop7 margin=1.50|72.1918|65.8876|6.3041|20 / 20|4.1401|7.7605|8.1905|not_submission_ready|Do not claim" paper10_geojepa_mpc\experiments\results\e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md
```

Expected: each token appears at least once.

- [ ] **Step 3: Re-run builder tests against generated artifacts**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_experiment_closure_refresh.py -q -p no:cacheprovider
```

Expected: `3 passed`.

---

### Task 4: Add Preflight RED Tests

**Files:**
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`
- Modify later: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add imports for the new check and paths**

In the existing import list from `scripts.paper10.preflight_submission_checks`,
add:

```python
    check_paper10_post_guard_experiment_closure_refresh_current,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
```

Expected before implementation: pytest collection fails with an import error.

- [ ] **Step 2: Add refresh artifacts to the minimal fixture file list**

In `MINIMAL_PREFLIGHT_FIXTURE_FILES`, add these paths after
`PAPER10_TRUE_REWARD_GUARD_READINESS_JSON`:

```python
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
```

- [ ] **Step 3: Require the check in the current-repository preflight test**

In `test_submission_preflight_cli_passes_current_repository`, add:

```python
    assert "paper10_post_guard_experiment_closure_refresh_current" in payload["passed_checks"]
```

- [ ] **Step 4: Add missing-file preflight test**

Add near the true-reward guard readiness missing-file test:

```python
def test_submission_preflight_minimal_fixture_reports_missing_post_guard_closure_refresh(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_post_guard_experiment_closure_refresh_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_post_guard_experiment_closure_refresh_current")
    assert "missing Paper10 post-guard experiment-closure refresh files" in details
    assert str(PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD) in details
```

- [ ] **Step 5: Add malformed JSON and overclaim tests**

Add:

```python
def test_post_guard_closure_refresh_preflight_requires_rewardtop7_guard(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    payload_path = fixture / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["primary_guard"]["audit_set"] = "audit7x7"
    payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = check_paper10_post_guard_experiment_closure_refresh_current(fixture)

    assert result.name == "paper10_post_guard_experiment_closure_refresh_current"
    assert result.ok is False
    assert "primary_guard.audit_set=audit7x7" in result.details


def test_post_guard_closure_refresh_preflight_rejects_final_submission_ready_claim(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    refresh = fixture / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD
    refresh.write_text(
        refresh.read_text(encoding="utf-8")
        + "\n\nThe paper is ready for final submission.\n",
        encoding="utf-8",
    )

    result = check_paper10_post_guard_experiment_closure_refresh_current(fixture)

    assert result.name == "paper10_post_guard_experiment_closure_refresh_current"
    assert result.ok is False
    assert "forbidden post-guard closure refresh wording" in result.details
    assert "ready for final submission" in result.details


def test_post_guard_closure_refresh_preflight_allows_negative_guardrails(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    refresh = fixture / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD
    refresh.write_text(
        refresh.read_text(encoding="utf-8")
        + "\n\nDo not claim direct 50-state Bishan scale-up success.\n",
        encoding="utf-8",
    )

    result = check_paper10_post_guard_experiment_closure_refresh_current(fixture)

    assert result.name == "paper10_post_guard_experiment_closure_refresh_current"
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

### Task 5: Implement Preflight GREEN

**Files:**
- Modify: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add refresh path constants**

After `PAPER10_TRUE_REWARD_GUARD_READINESS_JSON`, add:

```python
PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
```

- [ ] **Step 2: Add refresh artifacts to required paths**

In `REQUIRED_PATHS`, add after `PAPER10_TRUE_REWARD_GUARD_READINESS_JSON`:

```python
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
```

- [ ] **Step 3: Add post-guard overclaim helpers**

Place this helper block near the true-reward guard helper:

```python
POST_GUARD_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not"
    r"|not final|false|no-go|not_submission_ready|blocked|unresolved"
    r")\b",
    re.IGNORECASE,
)
POST_GUARD_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
POST_GUARD_FORBIDDEN_TARGETS = (
    re.compile(r"\buniversal fixed switch margin\b", re.IGNORECASE),
    re.compile(r"\bdirect 50[- ]state Bishan scale[- ]up success\b", re.IGNORECASE),
    re.compile(
        r"\brobust Bishan[- ]to[- ]Dongxing transfer superiority\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdeployment-ready cadastral planning\b", re.IGNORECASE),
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\bready to submit\b", re.IGNORECASE),
)


def is_post_guard_closure_refresh_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in POST_GUARD_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if POST_GUARD_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in POST_GUARD_FORBIDDEN_TARGETS):
            return True
    return False
```

- [ ] **Step 4: Add a nested value helper**

Place near other small preflight helpers:

```python
def nested_value(payload: dict, keys: tuple[str, ...]):
    value = payload
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value
```

If `nested_value` already exists when executing this plan, reuse the existing
helper and do not add a duplicate.

- [ ] **Step 5: Add the post-guard preflight check**

Place before `check_paper10_true_reward_guard_readiness_current`:

```python
def check_paper10_post_guard_experiment_closure_refresh_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
        RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md",
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "missing Paper10 post-guard experiment-closure refresh files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    required_tokens = [
        "Paper10 post-guard experiment-closure refresh",
        "Status: post_guard_experiment_closure_refresh",
        "source-derived; no rollout or training rerun",
        "rewardtop7 margin=1.50",
        "72.1918",
        "65.8876",
        "6.3041",
        "20 / 20",
        "4.1401",
        "7.7605",
        "8.1905",
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON.name,
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD.name,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON.name,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD.name,
        "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        "e0_paper10_experiment_closure_register_2026-06-27.md",
        PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        "closure update, not a new experiment",
        "not final submission readiness",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-07-08",
        ("status",): "post_guard_experiment_closure_refresh",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("primary_guard", "audit_set"): "rewardtop7",
        ("primary_guard", "switch_margin"): 1.5,
        ("primary_guard", "n_seeds"): 20,
        ("primary_guard", "guard_mean_reward"): 72.19178534319884,
        ("primary_guard", "baseline_mean_reward"): 65.8876435268697,
        ("primary_guard", "mean_delta_vs_baseline"): 6.304141816329158,
        ("primary_guard", "seed_wins"): 20,
        ("primary_guard", "bootstrap_95ci_delta_lower"): 4.140109129548553,
        ("primary_guard", "mean_audit_action_count"): 7.7605,
        ("primary_guard", "dual7x7_mean_audit_action_count"): 8.1905,
        ("closure_decision", "default_next_phase"): "bounded_manuscript_assembly",
        ("closure_decision", "resume_broad_algorithm_redesign"): False,
        ("submission_boundary", "status"): "not_submission_ready",
        ("claim_locks", "direct_50state_scaleup_supported"): False,
        ("claim_locks", "robust_transfer_superiority_supported"): False,
        ("claim_locks", "deployment_ready_supported"): False,
        ("claim_locks", "universal_fixed_margin_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    blockers = nested_value(payload, ("submission_boundary", "open_blockers"))
    if not isinstance(blockers, list):
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
            "submission_boundary.open_blockers"
        )
        blockers = []
    for blocker in (
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data rights and checkpoint or model-weight rights",
        "full Bishan Tool2 data access route",
        "GPKG-root geospatial input access route",
        "Dongxing/Neijiang prepared-data access route",
        "citation policy for local-only sources, preprints, and final reference style",
        "statistical reporting policy for descriptive results versus hypothesis tests",
        "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
    ):
        if blocker not in blockers:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
                f"submission_boundary.open_blockers.{blocker}"
            )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_closure_refresh_positive_overclaim(line):
            hits.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD}:{line_no}: "
                f"{line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "forbidden post-guard closure refresh wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "Paper10 post-guard experiment-closure refresh gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_post_guard_experiment_closure_refresh_current",
        True,
        "Paper10 post-guard experiment-closure refresh is current and bounded",
    )
```

- [ ] **Step 6: Register the check**

In `CHECKS`, add after `check_paper10_true_reward_guard_readiness_current`:

```python
    check_paper10_post_guard_experiment_closure_refresh_current,
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
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_experiment_closure_refresh.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: focused tests pass.

- [ ] **Step 2: Run Paper10 preflight**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected:

- `Paper10 preflight: PASS`
- output includes `[ok] paper10_post_guard_experiment_closure_refresh_current`

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
- Status shows only intended tracked edits plus the pre-existing untracked `2503.05774v1.pdf`.

- [ ] **Step 5: Commit implementation**

Stage only:

```powershell
git add paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py `
  paper10_geojepa_mpc/tests/test_post_guard_experiment_closure_refresh.py `
  paper10_geojepa_mpc/tests/test_submission_preflight.py `
  scripts/paper10/preflight_submission_checks.py `
  paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json `
  paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md
git diff --cached --check
git commit -m "exp: add post-guard closure refresh"
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

- New JSON/Markdown artifact maps to Tasks 2 and 3.
- Source basis maps to Tasks 2 and 5.
- JSON contract maps to Task 1 and Task 5.
- Markdown contract maps to Task 1 and Task 5.
- Preflight gate maps to Tasks 4 and 5.
- TDD RED/GREEN cycles map to Tasks 1, 2, 4, and 5.
- Final verification maps to Task 6.

Placeholder scan:

- The plan contains no unresolved marker text, generic test requests, or unresolved decisions.
- Each test and production step names exact files, functions, commands, and expected results.

Type consistency:

- Module name is consistently `post_guard_experiment_closure_refresh`.
- Builder function is consistently `build_post_guard_experiment_closure_refresh`.
- Markdown renderer is consistently `post_guard_experiment_closure_refresh_markdown`.
- Writer is consistently `write_post_guard_experiment_closure_refresh`.
- Preflight check name is consistently `paper10_post_guard_experiment_closure_refresh_current`.
- Artifact constants are consistently `PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD` and `PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON`.
