# Paper10 Submission Readiness Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a current no-go submission-readiness boundary artifact and guard it with `paper10_submission_readiness_boundary_current` in Paper10 preflight.

**Architecture:** Keep the change additive. Add one Markdown boundary file, wire it into the existing preflight checker and minimal fixture, and cross-link it from public/reproducibility docs. The check validates explicit no-go status, unresolved blockers, source-basis links, and absence of unqualified submission-ready or overclaim wording.

**Tech Stack:** Python standard library, pytest, existing `scripts/paper10/preflight_submission_checks.py`, Markdown evidence files.

---

## File Structure

Create:

- `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`
  Author-facing no-go submission-readiness boundary record.

Modify:

- `scripts/paper10/preflight_submission_checks.py`
  Add the boundary path constant, required path, public-doc list entry, forbidden wording helpers, check function, and `CHECKS` registration.
- `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  Add the new constant and check imports, fixture inclusion, current-repository assertion, and focused missing/malformed boundary tests.
- `README.md`
  Link the boundary as the current no-go submission-readiness record.
- `MANIFEST.md`
  Inventory the boundary artifact.
- `REPRODUCIBILITY.md`
  Link the boundary before interpreting preflight as submission readiness.
- `DATA_AVAILABILITY.md`
  Link the boundary from the data/code availability decision context.

Do not modify:

- Experiment, rollout, training, plotting, or model code.
- Existing result JSON files.

---

### Task 1: Add Failing Submission-Readiness Boundary Tests

**Files:**
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`

- [ ] **Step 1: Add imports for the new check and path**

Add these names to the existing import list from
`scripts.paper10.preflight_submission_checks`:

```python
    check_paper10_submission_readiness_boundary_current,
    PAPER10_SUBMISSION_READINESS_BOUNDARY,
```

Expected before implementation: pytest collection fails with an import error
because the production constant and check do not exist.

- [ ] **Step 2: Add the boundary artifact to the minimal fixture file list**

In `MINIMAL_PREFLIGHT_FIXTURE_FILES`, add the new path after
`PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE`:

```python
    PAPER10_SUBMISSION_READINESS_BOUNDARY,
```

- [ ] **Step 3: Require the check in the current-repository preflight test**

In `test_submission_preflight_cli_passes_current_repository`, add:

```python
    assert "paper10_submission_readiness_boundary_current" in payload["passed_checks"]
```

- [ ] **Step 4: Add missing-file fixture test**

Add this test near the other missing-file preflight tests:

```python
def test_submission_preflight_minimal_fixture_reports_missing_submission_readiness_boundary(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_SUBMISSION_READINESS_BOUNDARY).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_submission_readiness_boundary_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_submission_readiness_boundary_current")
    assert "missing Paper10 submission readiness boundary files" in details
    assert str(PAPER10_SUBMISSION_READINESS_BOUNDARY) in details
```

- [ ] **Step 5: Add malformed-boundary tests**

Add these focused tests after the missing-file test:

```python
def test_submission_readiness_boundary_requires_no_go_status(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    boundary = fixture / PAPER10_SUBMISSION_READINESS_BOUNDARY
    boundary.write_text(
        boundary.read_text(encoding="utf-8").replace(
            "Status: not_submission_ready",
            "Status: draft_boundary",
        ),
        encoding="utf-8",
    )

    result = check_paper10_submission_readiness_boundary_current(fixture)

    assert result.name == "paper10_submission_readiness_boundary_current"
    assert result.ok is False
    assert "Status: not_submission_ready" in result.details


def test_submission_readiness_boundary_requires_all_blockers(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    boundary = fixture / PAPER10_SUBMISSION_READINESS_BOUNDARY
    boundary.write_text(
        boundary.read_text(encoding="utf-8").replace(
            "repository DOI or anonymous reviewer link",
            "repository archive route",
        ),
        encoding="utf-8",
    )

    result = check_paper10_submission_readiness_boundary_current(fixture)

    assert result.name == "paper10_submission_readiness_boundary_current"
    assert result.ok is False
    assert "repository DOI or anonymous reviewer link" in result.details


def test_submission_readiness_boundary_rejects_submission_ready_claim(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    boundary = fixture / PAPER10_SUBMISSION_READINESS_BOUNDARY
    boundary.write_text(
        boundary.read_text(encoding="utf-8")
        + "\n\nStatus: submission_ready\nThe paper is ready for final submission.\n",
        encoding="utf-8",
    )

    result = check_paper10_submission_readiness_boundary_current(fixture)

    assert result.name == "paper10_submission_readiness_boundary_current"
    assert result.ok is False
    assert "forbidden submission-readiness wording" in result.details
    assert "Status: submission_ready" in result.details


def test_submission_readiness_boundary_allows_negative_guardrails(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    boundary = fixture / PAPER10_SUBMISSION_READINESS_BOUNDARY
    boundary.write_text(
        boundary.read_text(encoding="utf-8")
        + "\n\nDo not claim direct 50-state Bishan scale-up success.\n",
        encoding="utf-8",
    )

    result = check_paper10_submission_readiness_boundary_current(fixture)

    assert result.name == "paper10_submission_readiness_boundary_current"
    assert result.ok is True
```

- [ ] **Step 6: Run the focused test and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: collection fails because
`PAPER10_SUBMISSION_READINESS_BOUNDARY` or
`check_paper10_submission_readiness_boundary_current` cannot be imported.

- [ ] **Step 7: Commit the red tests**

Do not commit red tests alone. Keep them unstaged until Task 3 turns them
green.

---

### Task 2: Add the Boundary Artifact and Public Cross-Links

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`
- Modify: `README.md`
- Modify: `MANIFEST.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `DATA_AVAILABILITY.md`

- [ ] **Step 1: Create the boundary artifact**

Create `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`:

```markdown
# Paper10 submission-readiness boundary

Date: 2026-06-26

Status: not_submission_ready

This boundary records the current no-go submission status for the CEUS
Research Article route. The current repository preflight can pass while final
submission remains blocked. Preflight passing means this boundary is tracked
and cross-linked; it does not mean final submission readiness.

## Source basis

- `e0_paper10_formal_manuscript_draft_2026-06-20.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`

## Allowed next actions

- Continue CEUS manuscript conversion.
- Edit the formal manuscript draft within the current claim boundary.
- Prepare figure/table exports under the frozen export contract.
- Close author decisions for DOI, licence, data access, citation policy,
  statistical reporting, and journal-specific export rules.

## Submission blockers

1. repository DOI or anonymous reviewer link;
2. code licence;
3. generated-data rights and checkpoint or model-weight rights;
4. full Bishan Tool2 data access route;
5. GPKG-root geospatial input access route;
6. Dongxing/Neijiang prepared-data access route;
7. citation policy for local-only sources, preprints, and final reference style;
8. statistical reporting policy for descriptive results versus hypothesis
   tests;
9. Main Figure 1 final schematic artwork and journal-specific figure/table
   export rules.

## Claim locks

- Do not claim direct 50-state Bishan scale-up success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim solved irregular cadastral parcel deployment.
- Do not claim a full Constrained MDP, CPO, or RCPO solver.
- Do not claim Paper10 invented GeoJEPA.

## Preflight meaning

Passing preflight with this file means the current no-go submission boundary is
explicitly tracked, cross-linked, and guarded. It does not mean the paper is
ready to submit, and it does not close any author decision listed above.
```

- [ ] **Step 2: Add README cross-link**

Add one bullet to the current evidence list near the formal manuscript/final
export package entries:

```markdown
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`
```

Add one short paragraph near the current submission/preflight notes:

```markdown
Use `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`
as the current no-go submission-readiness boundary. It records that preflight
passing does not mean final submission readiness.
```

- [ ] **Step 3: Add MANIFEST entry**

Add this entry near the other current paper-facing control documents:

```markdown
- `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`:
  current no-go submission-readiness boundary for the CEUS route, preserving
  unresolved DOI, licence, data-access, citation, statistical-reporting, and
  final figure/export blockers.
```

- [ ] **Step 4: Add REPRODUCIBILITY cross-link**

Add:

```markdown
Use the current no-go submission-readiness boundary before interpreting
preflight as submission readiness:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md
```
```

- [ ] **Step 5: Add DATA_AVAILABILITY cross-link**

Add:

```markdown
For the current no-go submission-readiness boundary and unresolved repository,
licence, data-access, citation, statistics, and final export decisions, see:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md
```
```

---

### Task 3: Implement the Preflight Guard

**Files:**
- Modify: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add the path constant**

After `PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE`, add:

```python
PAPER10_SUBMISSION_READINESS_BOUNDARY = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
```

- [ ] **Step 2: Add the boundary to required path and public-doc lists**

Add `PAPER10_SUBMISSION_READINESS_BOUNDARY` to `REQUIRED_PATHS` after
`PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE`.

Add `PAPER10_SUBMISSION_READINESS_BOUNDARY` to `PUBLIC_SUBMISSION_DOCS` after
`PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE`.

- [ ] **Step 3: Add forbidden wording helpers**

Place this helper block near the original-vision guardrail helpers:

```python
SUBMISSION_READINESS_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"not|no-go|blocked|unresolved|pending|does not mean|do not|must not|cannot"
    r")\b",
    re.IGNORECASE,
)
SUBMISSION_READINESS_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
SUBMISSION_READINESS_FORBIDDEN_TARGETS = (
    re.compile(r"\bStatus:\s*submission_ready\b", re.IGNORECASE),
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\ball blockers closed\b", re.IGNORECASE),
    re.compile(
        r"\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bscale[- ]?up\b.{0,80}\bsuccess\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\brobust\b.{0,80}\bbishan[- ]to[- ]dongxing\b.{0,80}\btransfer\b.{0,80}\bsuperiority\b",
        re.IGNORECASE,
    ),
)


def is_submission_readiness_positive_claim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in SUBMISSION_READINESS_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if SUBMISSION_READINESS_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in SUBMISSION_READINESS_FORBIDDEN_TARGETS):
            return True
    return False
```

- [ ] **Step 4: Add the check function**

Place this function before `check_original_vision_validation_registry_current`:

```python
def check_paper10_submission_readiness_boundary_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
        PAPER10_FORMAL_MANUSCRIPT_DRAFT,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
        PAPER10_MECHANISM_ABLATION_PACKET_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "missing Paper10 submission readiness boundary files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_SUBMISSION_READINESS_BOUNDARY)
    normalized_text = " ".join(text.split())
    missing_tokens = []
    required_tokens = [
        "Paper10 submission-readiness boundary",
        "Status: not_submission_ready",
        "preflight passing does not mean final submission readiness",
        PAPER10_FORMAL_MANUSCRIPT_DRAFT.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
        PAPER10_MECHANISM_ABLATION_PACKET_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD.name,
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data rights and checkpoint or model-weight rights",
        "full Bishan Tool2 data access route",
        "GPKG-root geospatial input access route",
        "Dongxing/Neijiang prepared-data access route",
        "citation policy for local-only sources, preprints, and final reference style",
        "statistical reporting policy for descriptive results versus hypothesis tests",
        "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
        "Do not claim direct 50-state Bishan scale-up success",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "does not mean the paper is ready to submit",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_SUBMISSION_READINESS_BOUNDARY}: {token}"
            )

    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        if PAPER10_SUBMISSION_READINESS_BOUNDARY.name not in read_text(root / doc):
            missing_tokens.append(f"{doc}: {PAPER10_SUBMISSION_READINESS_BOUNDARY.name}")

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_submission_readiness_positive_claim(line):
            hits.append(
                f"{PAPER10_SUBMISSION_READINESS_BOUNDARY}:{line_no}: {line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "forbidden submission-readiness wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "Paper10 submission readiness boundary gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_submission_readiness_boundary_current",
        True,
        "Paper10 submission-readiness boundary is current and no-go guarded",
    )
```

- [ ] **Step 5: Register the check**

Add `check_paper10_submission_readiness_boundary_current` to `CHECKS` after
`check_paper10_final_figure_table_export_package_current`.

- [ ] **Step 6: Run tests and verify GREEN**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: all tests in `test_submission_preflight.py` pass.

If a test fails because the exact normalized token wraps across lines, adjust
only the boundary file wording or the required token to use a stable phrase.
Do not remove the required blocker from the check.

---

### Task 4: Run Preflight and Diff Verification

**Files:**
- No new files.

- [ ] **Step 1: Run preflight**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected:

- `Paper10 preflight: PASS`
- output includes `[ok] paper10_submission_readiness_boundary_current`

- [ ] **Step 2: Check formatting**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected:

- `git diff --check` has no output.
- Status shows only the intended implementation files modified or added.

- [ ] **Step 3: Commit implementation**

Stage only:

```powershell
git add scripts/paper10/preflight_submission_checks.py `
  paper10_geojepa_mpc/tests/test_submission_preflight.py `
  paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md `
  README.md `
  MANIFEST.md `
  REPRODUCIBILITY.md `
  DATA_AVAILABILITY.md
git diff --cached --check
git commit -m "docs: guard paper10 submission readiness boundary"
```

Expected: commit succeeds.

---

## Self-Review Notes

Spec coverage:

- Boundary artifact maps to Task 2.
- Preflight guard maps to Task 3.
- Public-document cross-links map to Task 2.
- TDD red/green cycle maps to Task 1 and Task 3.
- Verification and commit map to Task 4.

Placeholder scan:

- The plan contains no placeholder sections, no unresolved fields, and no task
  that says to add generic tests without exact behavior.

Type consistency:

- Check name is consistently `paper10_submission_readiness_boundary_current`.
- Path constant is consistently `PAPER10_SUBMISSION_READINESS_BOUNDARY`.
- Artifact path is consistently
  `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`.
