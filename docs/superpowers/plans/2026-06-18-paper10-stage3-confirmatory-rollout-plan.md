# Paper10 Stage 3 Confirmatory Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare and run the Stage 3 Colab Pro+ confirmatory rollout pass only for rows authorized by the Stage 1-2 decision packet.

**Architecture:** Keep Stage 3 as a compute handoff and evidence-generation pass. Reuse existing value-head training, rollout, and multiseed comparison scripts; write small run manifests and summary evidence files rather than changing model architecture. Every row must be matched against baselines before any manuscript claim changes.

**Tech Stack:** Python standard library, existing Paper10 experiment modules, Colab Pro+ runtime, local evidence files under `paper10_geojepa_mpc/experiments/results/`, and local-only raw outputs under `D:\test\paper10_original_vision_validation\stage3_colab_handoff\`.

---

## Decision Basis

- Decision packet:
  `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md`
- Decision: `proceed_to_stage3_confirmatory_rollouts`
- Stage 1 counts: `pass=2`, `near_pass=1`, `fail=3`
- Stage 2 audit: mixed transfer-minus-scratch effects; only `low_budget_20`
  is transfer-higher on reward in the existing matched audit.

This is a compute handoff plan, not a manuscript conclusion.

## Authorized Bishan Rows

| role | run | selected top-k | label seed | states | candidates | horizon | frontier fraction |
|---|---|---:|---:|---:|---:|---:|---:|
| frozen anchor | `frontier_random050_20x16_h5_seed44_f050` | 5 | 44 | 20 | 16 | 5 | 0.50 |
| confirmatory pass | `frontier_random050_50x16_h5_seed48_f050` | 6 | 48 | 50 | 16 | 5 | 0.50 |
| confirmatory pass | `frontier_random050_50x24_h5_seed47_f075` | 12 | 47 | 50 | 24 | 5 | 0.75 |
| diagnostic near-pass | `frontier_random050_50x24_h5_seed48_f075` | 12 | 48 | 50 | 24 | 5 | 0.75 |

The diagnostic near-pass row may be trained and rolled out only as diagnostic
evidence. It must not be pooled with confirmatory pass rows.

## Excluded Stage 1 Rows

The following Stage 1 rows failed the row-level monitor gate and must not enter
Stage 3 training or rollout in this pass:

- `frontier_random050_50x16_h5_seed47_f050`
- `frontier_random050_50x20_h5_seed47_f050`
- `frontier_random050_50x20_h5_seed48_f050`

## Matched Bishan Rollout Matrix

Run each authorized Bishan row with rollout seeds `0, 1, 2, 3, 4`, 100 rollout
steps, horizon `5`, and matched data roots/checkpoints.

| family | selector | candidate score mode | candidate-value weight | top-k source |
|---|---|---|---:|---|
| value head | `value_filter` | `blend` | 0.1 | selected row top-k |
| no value filter | matched baseline selector | matched | 0.0 | matched selected top-k |
| pairwise-only | matched checkpoint | matched | 0.1 | matched selected top-k |

The frozen 20x16 anchor uses top-k `5`; the two pass rows use top-k `6` and
`12`; the diagnostic near-pass row uses top-k `12`.

## Dongxing Follow-Up Scope

Stage 2 found mixed Dongxing transfer-minus-scratch effects. The only positive
matched reward effect was `low_budget_20` (`+4.2484`), while
`return_50x16_h5` was scratch-higher (`-4.1141`). Dongxing Stage 3 work should
therefore be limited to matched transfer/scratch checks for the low-budget
conditional regime, not a broad transfer-win claim.

---

### Task 1: Create Colab Handoff Manifest

**Files:**
- Create local-only: `D:\test\paper10_original_vision_validation\stage3_colab_handoff\stage3_authorized_rows_2026-06-18.json`
- Create local-only: `D:\test\paper10_original_vision_validation\stage3_colab_handoff\stage3_colab_commands_2026-06-18.md`

- [ ] **Step 1: Create the handoff directory**

Run:

```powershell
New-Item -ItemType Directory -Force -Path D:\test\paper10_original_vision_validation\stage3_colab_handoff
```

Expected: directory exists.

- [ ] **Step 2: Write the authorized-row manifest**

Create JSON with exactly these row records:

```json
[
  {
    "role": "frozen_anchor",
    "run_name": "frontier_random050_20x16_h5_seed44_f050",
    "selected_top_k": 5,
    "label_seed": 44,
    "n_states": 20,
    "candidate_actions": 16,
    "label_horizon": 5,
    "frontier_fraction": 0.5,
    "claim_role": "anchor_reproduction"
  },
  {
    "role": "confirmatory_pass",
    "run_name": "frontier_random050_50x16_h5_seed48_f050",
    "selected_top_k": 6,
    "label_seed": 48,
    "n_states": 50,
    "candidate_actions": 16,
    "label_horizon": 5,
    "frontier_fraction": 0.5,
    "claim_role": "stage1_pass_followup"
  },
  {
    "role": "confirmatory_pass",
    "run_name": "frontier_random050_50x24_h5_seed47_f075",
    "selected_top_k": 12,
    "label_seed": 47,
    "n_states": 50,
    "candidate_actions": 24,
    "label_horizon": 5,
    "frontier_fraction": 0.75,
    "claim_role": "stage1_pass_followup"
  },
  {
    "role": "diagnostic_near_pass",
    "run_name": "frontier_random050_50x24_h5_seed48_f075",
    "selected_top_k": 12,
    "label_seed": 48,
    "n_states": 50,
    "candidate_actions": 24,
    "label_horizon": 5,
    "frontier_fraction": 0.75,
    "claim_role": "diagnostic_only"
  }
]
```

- [ ] **Step 3: Write command notes**

Record that Colab must use:

```text
rollout_seeds = 0,1,2,3,4
rollout_steps = 100
mask_mode = executable
value_head_selector = value_filter
candidate_score_mode = blend
candidate_value_weight = 0.1
baseline_selector = paper9
```

Expected: local-only command notes exist and include the commit SHA used for
execution.

### Task 2: Run Matched Bishan Training and Rollouts

**Files:**
- Read local-only Stage 1 label files under `D:\test\paper10_original_vision_validation\stage1_label_only\`
- Create local-only checkpoints and raw rollout JSON under `D:\test\paper10_original_vision_validation\stage3_colab_handoff\`

- [ ] **Step 1: Verify required Stage 1 label files**

For each authorized Stage 1 row, verify that its `.npz` label file exists under
the Stage 1 run directory. The frozen anchor may use the existing tracked
20x16/top5 evidence path documented in the validation registry.

Expected: all required label files exist before training.

- [ ] **Step 2: Train value heads only for authorized rows**

Use `paper10_geojepa_mpc.experiments.run_e0_value_head_train` with the selected
top-k for each row. Do not train excluded Stage 1 rows.

Expected: one checkpoint and one metrics JSON per authorized value-head row.

- [ ] **Step 3: Run five-seed value-filter rollouts**

Use `paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke` with:

```text
--selector value_filter
--candidate-score-mode blend
--candidate-value-weight 0.1
--rollout-steps 100
--seeds 0 1 2 3 4
```

Expected: one multiseed raw rollout JSON per authorized row.

- [ ] **Step 4: Run matched baselines**

For each authorized row, run matched no-value-filter and pairwise-only baselines
with the same rollout seeds, horizon, top-k, data root, and rollout-step budget.

Expected: baseline JSON files are present for every confirmatory value-filter
row.

### Task 3: Summarize Stage 3 Evidence

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`

- [ ] **Step 1: Build aggregate tables**

Use `paper10_geojepa_mpc.experiments.compare_multiseed_rollouts` or a small
standard-library summarizer to record, for each row and family:

```text
command
data_root
checkpoint_path
code_commit
runtime
seed_level_reward
seed_level_secondary_metrics
mean
sample_standard_deviation
min
max
matched_value_minus_baseline_effect
```

Expected: JSON contains per-seed rows and aggregate rows.

- [ ] **Step 2: Render Markdown**

The Markdown summary must include:

- row role (`frozen_anchor`, `confirmatory_pass`, or `diagnostic_near_pass`);
- selected top-k;
- seed list;
- value-filter aggregate;
- matched baseline aggregates;
- matched effects;
- slope, contiguity, and baimu-area secondary outcomes;
- explicit note that diagnostic rows are not confirmatory rows.

Expected: Markdown can be read without opening raw rollout logs.

- [ ] **Step 3: Guard claim boundaries**

Run:

```powershell
$pattern = "direct 50-state " + "success|robust transfer " + "superiority|proves " + "scale-up"
rg -n $pattern paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md
```

Expected: no output and exit code `1`.

- [ ] **Step 4: Commit Stage 3 summaries only**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md
git diff --cached --check
git commit -m "docs: add original vision stage3 confirmatory rollouts"
```

Expected: tracked summaries are committed; raw logs and checkpoints remain
outside git.

## Claim Boundary

Stage 3 can only support a claim after matched rollout evidence exists. A
Stage 1 pass authorizes follow-up compute; it is not final scale-up evidence.
A Dongxing positive low-budget row authorizes a conditional transfer follow-up;
it is not evidence for a broad transfer-win conclusion.

## Self-Review Notes

- Spec coverage: the authorized rows follow the Stage 1-2 decision packet and
  Stage 3 design spec.
- Scope: this plan prepares Stage 3; it does not report Stage 3 results.
- Claim discipline: failed Stage 1 rows are excluded, near-pass rows are marked
  diagnostic, and no manuscript claim changes before matched rollout evidence.
