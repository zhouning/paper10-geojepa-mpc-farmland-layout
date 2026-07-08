# Paper10 True-Reward Guard Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the 2026-07-07 true-reward margin guard evidence into a source-derived, machine-checked Paper10 algorithm-readiness boundary before manuscript work.

**Architecture:** Add one deterministic audit module that reads tracked JSON result artifacts and emits JSON/Markdown readiness artifacts. Extend submission preflight so public docs and future manuscript patches cannot silently omit or overclaim the new guard evidence.

**Tech Stack:** Python standard library, pytest, existing Paper10 result JSON/Markdown artifacts, existing `scripts/paper10/preflight_submission_checks.py`.

---

### Task 1: Audit Builder Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_true_reward_guard_readiness.py`
- Create later: `paper10_geojepa_mpc/experiments/true_reward_guard_readiness.py`

- [ ] **Step 1: Write failing tests**

```python
def test_build_readiness_audit_promotes_20x16_guard_without_universal_margin_claim():
    audit = build_true_reward_guard_readiness_audit(...)
    assert audit["claim_gates"]["primary_algorithm_candidate_supported"] is True
    assert audit["primary_guard"]["seed_wins"] == 10
    assert audit["claim_gates"]["universal_fixed_margin_supported"] is False
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_true_reward_guard_readiness.py -q -p no:cacheprovider
```

Expected: import failure for `paper10_geojepa_mpc.experiments.true_reward_guard_readiness`.

- [ ] **Step 3: Implement minimal audit module**

Create a module with:

```python
def build_true_reward_guard_readiness_audit(...): ...
def true_reward_guard_readiness_markdown(audit): ...
def write_true_reward_guard_readiness_audit(...): ...
```

- [ ] **Step 4: Verify GREEN**

Run the same focused pytest command and expect PASS.

### Task 2: Preflight Guard Tests

**Files:**
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`
- Modify later: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add failing preflight tests**

```python
def test_submission_preflight_registers_true_reward_guard_readiness():
    ...
    assert "paper10_true_reward_guard_readiness_current" in payload["passed_checks"]
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: missing check name or import failure.

- [ ] **Step 3: Implement preflight constants, check, registration, and minimal fixture inclusion**

Add `PAPER10_TRUE_REWARD_GUARD_READINESS_MD/JSON`, a check function, and register it in `CHECKS`.

- [ ] **Step 4: Verify GREEN**

Run the same focused pytest command and expect PASS.

### Task 3: Generate Readiness Artifacts and Docs

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.json`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md`
- Modify: `README.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `MANIFEST.md`
- Modify: `DATA_AVAILABILITY.md`

- [ ] **Step 1: Generate artifacts**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.true_reward_guard_readiness
```

Expected: JSON and Markdown files are written under `paper10_geojepa_mpc/experiments/results/`.

- [ ] **Step 2: Add public-doc cross-links**

Reference the new audit as the current algorithm-readiness boundary while preserving `not_submission_ready` submission blockers.

- [ ] **Step 3: Verify preflight**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected: `Paper10 preflight: PASS` and `[ok] paper10_true_reward_guard_readiness_current`.

### Task 4: Final Verification

**Files:** no new files.

- [ ] **Step 1: Run focused tests**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_true_reward_guard_readiness.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

- [ ] **Step 2: Run full test suite with longer timeout**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

- [ ] **Step 3: Run Git checks**

```powershell
git status --short --branch
git diff --check
```

Expected: only intended tracked edits plus the pre-existing untracked `2503.05774v1.pdf`.
