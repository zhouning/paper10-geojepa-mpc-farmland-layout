# Paper10 10x12 Guard 20-Seed Confirmation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend Bishan 10x12/top4 `rewardtop7 margin=1.60` guard evidence from 5 matched seeds to 20 matched seeds.

**Architecture:** Keep rollout generation in the existing baseline and true-reward-audit CLIs. Add one focused builder that merges existing seeds `0-4` with new seeds `5-19`, computes paired comparison statistics, and writes bounded JSON/Markdown evidence.

**Tech Stack:** Python, pytest, existing Paper10 experiment CLIs, JSON/Markdown result artifacts.

---

## File Structure

- Create: `paper10_geojepa_mpc/experiments/guard_10x12_20seed_confirmation.py`
  - Loads baseline/guard rollout JSON files.
  - Validates exact matched seeds.
  - Produces combined payloads, comparison payload, paired stats, and triage Markdown.
- Create: `paper10_geojepa_mpc/tests/test_guard_10x12_20seed_confirmation.py`
  - Tests merge validation, paired statistics, markdown claim boundary, and output writing.
- Generate:
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_blend010_h5_k50_seeds5-19_100step_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds5-19_100step_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_blend010_h5_k50_seeds0-19_100step_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds0-19_100step_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.md`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_paired_stats_2026-07-08.json`
  - `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_confirmation_triage_2026-07-08.md`

### Task 1: Builder Red Test

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_guard_10x12_20seed_confirmation.py`

- [ ] **Step 1: Write failing tests**

```python
import json

import pytest

from paper10_geojepa_mpc.experiments.guard_10x12_20seed_confirmation import (
    build_confirmation_packet,
    markdown_report,
    write_outputs,
)


def rollout_payload(seeds, rewards):
    episodes = [
        {
            "seed": seed,
            "horizon": 5,
            "top_k": 50,
            "total_reward": reward,
            "steps": [
                {
                    "step": 1,
                    "action": seed,
                    "reward": reward,
                    "select_time_sec": 0.1,
                    "slope_change_pct": 1.0 + seed,
                    "cont_change": 0.1,
                    "baimu_area_change_ha": 2.0,
                }
            ],
        }
        for seed, reward in zip(seeds, rewards, strict=True)
    ]
    return {
        "checkpoint": "checkpoint.pt",
        "prepared_dir": "D:\\test",
        "seeds": list(seeds),
        "horizon": 5,
        "top_k": 50,
        "candidate_score_mode": "blend",
        "candidate_value_weight": 0.1,
        "random_continuation_mode": "independent",
        "stable_candidate_order": False,
        "episodes": episodes,
    }


def test_build_confirmation_packet_merges_matched_seed_batches():
    baseline_0_4 = rollout_payload([0, 1], [10.0, 20.0])
    baseline_5_19 = rollout_payload([2, 3], [30.0, 40.0])
    guard_0_4 = rollout_payload([0, 1], [11.0, 22.0])
    guard_5_19 = rollout_payload([2, 3], [33.0, 44.0])

    packet = build_confirmation_packet(
        baseline_batches=[baseline_0_4, baseline_5_19],
        guard_batches=[guard_0_4, guard_5_19],
        expected_seeds=[0, 1, 2, 3],
    )

    assert packet["status"] == "descriptive_confirmation"
    assert packet["seed_count"] == 4
    assert packet["comparison"]["aggregate_delta"]["total_reward_mean"] == pytest.approx(2.5)
    assert packet["paired_stats"]["wins"] == 4
    assert packet["paired_stats"]["losses"] == 0
    assert packet["paired_stats"]["mean_delta"] == pytest.approx(2.5)
    assert packet["small_scale_guard"]["switch_margin"] == 1.6


def test_build_confirmation_packet_rejects_unmatched_seeds():
    baseline = rollout_payload([0, 1], [10.0, 20.0])
    guard = rollout_payload([0, 2], [11.0, 22.0])

    with pytest.raises(ValueError, match="expected matched seeds"):
        build_confirmation_packet(
            baseline_batches=[baseline],
            guard_batches=[guard],
            expected_seeds=[0, 1],
        )


def test_markdown_report_preserves_setting_specific_claim_boundary():
    packet = build_confirmation_packet(
        baseline_batches=[rollout_payload([0, 1], [10.0, 20.0])],
        guard_batches=[rollout_payload([0, 1], [11.0, 22.0])],
        expected_seeds=[0, 1],
    )

    text = markdown_report(packet)

    assert "10x12/top4" in text
    assert "rewardtop7 margin=1.60" in text
    assert "setting-specific" in text
    assert "Do not claim a universal fixed switch margin." in text
    assert "Do not claim direct 50-state Bishan scale-up success." in text
    assert "final submission readiness" in text


def test_write_outputs_creates_json_and_markdown_files(tmp_path):
    packet = build_confirmation_packet(
        baseline_batches=[rollout_payload([0, 1], [10.0, 20.0])],
        guard_batches=[rollout_payload([0, 1], [11.0, 22.0])],
        expected_seeds=[0, 1],
    )

    paths = write_outputs(packet, tmp_path)

    for key in (
        "baseline_combined_json",
        "guard_combined_json",
        "comparison_json",
        "comparison_md",
        "paired_stats_json",
        "triage_md",
    ):
        assert paths[key].exists()
    assert json.loads(paths["paired_stats_json"].read_text(encoding="utf-8"))["n"] == 2
```

- [ ] **Step 2: Run red test**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_guard_10x12_20seed_confirmation.py -q -p no:cacheprovider
```

Expected: fail with missing module `paper10_geojepa_mpc.experiments.guard_10x12_20seed_confirmation`.

### Task 2: Builder Green Implementation

**Files:**
- Create: `paper10_geojepa_mpc/experiments/guard_10x12_20seed_confirmation.py`

- [ ] **Step 1: Implement minimal builder**

The module must expose:

```python
def build_confirmation_packet(*, baseline_batches, guard_batches, expected_seeds): ...
def markdown_report(packet): ...
def write_outputs(packet, output_dir): ...
```

Implementation rules:

- use existing `compare_multiseed_rollouts.compare_rollout_runs` and `markdown_report` for comparison;
- preserve exact seed order from `expected_seeds`;
- compute paired deltas from matched seed rewards;
- compute bootstrap CI deterministically with NumPy RNG seed `20260708`;
- include negative claim locks in JSON and Markdown.

- [ ] **Step 2: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_guard_10x12_20seed_confirmation.py -q -p no:cacheprovider
```

Expected: all tests pass.

### Task 3: Run Baseline Seeds 5-19

**Files:**
- Generate baseline raw JSON.

- [ ] **Step 1: Run matched baseline**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt --prepared-dir D:\test --rollout-steps 100 --horizon 5 --top-k 50 --seeds 5-19 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --progress-interval 20 --output paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_blend010_h5_k50_seeds5-19_100step_2026-07-08.json
```

Expected: output JSON has `complete=true`, `completed_seeds=[5..19]`, and `pending_seeds=[]`.

### Task 4: Run Guard Seeds 5-19

**Files:**
- Generate guard raw JSON.

- [ ] **Step 1: Run matched guard**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.true_reward_action_audit --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt --prepared-dir D:\test --steps 100 --horizon 5 --top-k 50 --metric-top-k 10 --audit-random-sample 0 --audit-top-reward 7 --audit-top-candidate 0 --seeds 5-19 --device cpu --candidate-score-mode blend --candidate-value-weight 0.1 --execution-policy margin_true_reward_guard --true-reward-switch-margin 1.6 --random-continuation-mode independent --output paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds5-19_100step_2026-07-08.json
```

Expected: output JSON has `seeds=[5..19]`, `steps=100`, `execution_policy=margin_true_reward_guard`, `true_reward_switch_margin=1.6`, `audit_top_reward=7`, and `audit_top_candidate=0`.

### Task 5: Generate 20-Seed Confirmation Packet

**Files:**
- Generate combined JSON/Markdown artifacts.

- [ ] **Step 1: Run builder**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.guard_10x12_20seed_confirmation
```

Expected: all six confirmation outputs are written under `paper10_geojepa_mpc\experiments\results`.

- [ ] **Step 2: Check tokens**

Run:

```powershell
rg -n "10x12/top4|rewardtop7 margin=1.60|20 matched seeds|setting-specific|Do not claim a universal fixed switch margin|Do not claim direct 50-state Bishan scale-up success|not final submission readiness" paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_confirmation_triage_2026-07-08.md
```

Expected: all terms are present.

### Task 6: Verification and Commit

**Files:**
- Add implementation, tests, generated result artifacts, spec, and plan.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_guard_10x12_20seed_confirmation.py paper10_geojepa_mpc\tests\test_true_reward_guard_readiness.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 2: Run full verification**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
git diff --check
```

Expected: pytest passes, Paper10 preflight passes, and `git diff --check` has no whitespace errors.

- [ ] **Step 3: Commit and push**

Run:

```powershell
git add docs\superpowers\specs\2026-07-08-paper10-10x12-guard-20seed-confirmation-design.md docs\superpowers\plans\2026-07-08-paper10-10x12-guard-20seed-confirmation.md paper10_geojepa_mpc\experiments\guard_10x12_20seed_confirmation.py paper10_geojepa_mpc\tests\test_guard_10x12_20seed_confirmation.py paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_blend010_h5_k50_seeds5-19_100step_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds5-19_100step_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_blend010_h5_k50_seeds0-19_100step_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds0-19_100step_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-08.md paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_paired_stats_2026-07-08.json paper10_geojepa_mpc\experiments\results\e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_confirmation_triage_2026-07-08.md
git commit -m "exp: confirm 10x12 guard across 20 seeds"
git push
```

Expected: commit is pushed to `origin/main`; `2503.05774v1.pdf` remains untracked and unstaged.
