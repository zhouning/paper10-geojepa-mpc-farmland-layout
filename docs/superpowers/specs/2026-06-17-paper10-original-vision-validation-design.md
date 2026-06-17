# Paper10 Original-Vision Validation Design Spec

**Date:** 2026-06-17
**Status:** preregistered validation design for review
**Primary predecessor:** `docs/superpowers/notes/2026-06-12-paper10-original-vision-validation-handoff.md`
**Current saved commit:** `de3c170 docs: add CEUS draft and validation handoff`

## 1. Purpose

This spec defines the next Paper10 validation program. Its purpose is to test
the original strong Paper10 vision rigorously before narrowing or strengthening
the manuscript claim.

The current evidence is not sufficient to claim strong 50-state Bishan scale-up
or robust Bishan-to-Dongxing transfer superiority. It also does not disprove
those possibilities. The next work must therefore be a staged validation
matrix with predefined gates, matched baselines, and explicit stop/go rules.

## 2. Claim Discipline

All conclusions from this validation program must follow these rules.

Allowed before new experiments:

- The 20x16/h5 seed44 top-5 Bishan value-label route is reproducible and
  currently supports the main positive value-head result.
- The tested 50-state seed46 rows failed the predefined monitor gate and are
  boundary diagnostics for those rows only.
- Dongxing/Neijiang currently supports method portability, planner calibration,
  and return-label scaling, but not broad transfer superiority.

Not allowed before new experiments:

- Do not claim direct 50-state Bishan success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not say the original Paper10 vision cannot land.
- Do not relax monitor thresholds after seeing a failed label file unless the
  run is explicitly declared as a new ablation rather than confirmatory
  validation.
- Do not report only favorable seeds, top-k settings, or label budgets.

## 3. Frozen Evidence Base

The validation program starts from the following frozen evidence.

### 3.1 Reproducible Bishan Positive Result

The current main positive result is:

- candidate family: `frontier_random050`
- label setting: `20x16/h5`
- label seed: `44`
- monitor top-k: `5`
- monitor decision: `continue`
- candidate top-k regret: `0.18767197132110597`
- candidate top-k overlap: `0.6300000000000001`
- one-step top-k regret: `2.462647271156311`
- five-seed 100-step mean total reward: `69.47054604253474`
- five-seed sample standard deviation: `1.0003610285842477`

The Windows rerun reproduced the label arrays, monitor decision, checkpoint
hash, and five-seed rollout aggregate exactly.

### 3.2 Current 50-State Boundary Diagnostics

The completed Windows seed46 50-state rows all failed monitor gating:

| run | states | candidates | frontier fraction | seed | passing top-k |
|---|---:|---:|---:|---:|---|
| `frontier_random050_50x16_h5_seed46_f050` | 50 | 16 | 0.50 | 46 | none |
| `frontier_random050_50x20_h5_seed46_f050` | 50 | 20 | 0.50 | 46 | none |
| `frontier_random050_50x24_h5_seed46_f075` | 50 | 24 | 0.75 | 46 | none |
| `frontier_random050_50x24_h5_seed46_f100` | 50 | 24 | 1.00 | 46 | none |

These rows do not support a 50-state claim. They also do not reject all
50-state candidate proposals, seeds, or calibration regimes.

### 3.3 Current Dongxing/Neijiang Evidence

The current Dongxing synthesis supports:

- local data loading and environment construction;
- action-space adaptation from Bishan checkpoints to Dongxing;
- planner sensitivity to candidate-value weight;
- improvement from pairwise-only labels to real-environment return labels;
- improvement from 20x16 to 50x16 return labels for both transfer and scratch.

It does not support a broad transfer-win claim. In the current 50x16 return
label family, scratch has the stronger mean reward.

## 4. Predefined Monitor Gate

For confirmatory validation, a value-label file passes only if all default
monitor thresholds are satisfied:

| metric | pass threshold |
|---|---:|
| candidate top-k regret | `<= 0.25` |
| candidate top-k overlap | `>= 0.50` |
| one-step top-k regret | `>= 0.25` |

The default monitor top-k set is:

- top-k `3`, `4`, and `5` for 20-state rows;
- top-k `5`, `6`, `8`, `10`, and `12` for 50-state diagnostic rows.

Top-k values above `12` are exploratory unless preregistered in a later spec,
because broad top-k settings can hide the candidate-selection problem rather
than solving it.

## 5. Hypotheses

### H1: 50-State Label Validity

Larger value-label settings can pass the monitor gate under some candidate
proposal, seed, or top-k setting.

Primary test:

- Run label-only 50-state rescue candidates before training any new value
  head.
- Treat each row as passing, near-passing, or failing using the predefined
  monitor gate.

Primary outcome:

- number and fraction of predefined 50-state rows that pass;
- distribution of candidate regret, candidate overlap, and one-step regret by
  seed and candidate proposal.

### H2: Value-Label Scaling Improves Rollouts

Monitor-gated value-label scaling improves rollouts beyond matched baselines.

Primary test:

- Train value heads only for passing or near-passing rows.
- Compare value-filter rollouts against matched no-value-filter and
  pairwise-only baselines under the same horizon, top-k, rollout steps, seeds,
  executable mask, and environment root.

Primary outcome:

- five-seed mean total reward;
- sample standard deviation;
- per-seed paired reward difference where the same rollout seeds are available;
- slope, contiguity, and baimu-area changes as secondary metrics.

### H3: Cross-Region Transfer Is Conditional

Bishan initialization helps Dongxing only under specific label-budget or
planner-calibration regimes, rather than robustly dominating local scratch.

Primary test:

- Reanalyze existing Dongxing transfer/scratch rows with unified effect-size
  reporting.
- Add matched transfer-versus-scratch rows only if they close a predefined
  budget or calibration gap.

Primary outcome:

- family-level mean reward difference: transfer minus scratch;
- paired or seed-aligned differences when available;
- label-budget-specific direction of effect;
- slope, contiguity, and baimu-area trade-offs.

## 6. Validation Stages

### Stage 0: Repository and Evidence Sanity Check

Run before any new experiment:

```powershell
git status --short --branch
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected result:

- clean or intentionally documented working tree;
- `Paper10 preflight: PASS`.

If preflight fails, stop and repair the documentation or guard failure before
running new experiments.

### Stage 1: Windows Label-Only Rescue Matrix

Purpose: test H1 cheaply before spending compute on training and rollouts.

Initial confirmatory matrix:

| row id | states | candidates | horizon | frontier fraction | label seeds | train on pass |
|---|---:|---:|---:|---:|---|---|
| `50x16_h5_f050_seed47_48` | 50 | 16 | 5 | 0.50 | 47, 48 | no |
| `50x20_h5_f050_seed47_48` | 50 | 20 | 5 | 0.50 | 47, 48 | no |
| `50x24_h5_f075_seed47_48` | 50 | 24 | 5 | 0.75 | 47, 48 | no |

Optional expansion, run only if the first matrix contains a pass or a
near-pass:

| row id | states | candidates | horizon | frontier fraction | label seeds | train on pass |
|---|---:|---:|---:|---:|---|---|
| `50x16_h5_f050_seed49_50` | 50 | 16 | 5 | 0.50 | 49, 50 | no |
| `50x20_h5_f050_seed49_50` | 50 | 20 | 5 | 0.50 | 49, 50 | no |

Near-pass definition:

- exactly one monitor metric misses the default threshold by no more than 20%
  of the threshold scale, and the one-step regret remains positive; or
- a row passes at one predefined top-k but fails another, making it plausible
  enough for sensitivity analysis.

Near-pass rows are not positive evidence. They only justify a limited rollout
or proposal-design diagnostic.

Stage 1 output:

- machine-readable JSON summary;
- Markdown summary table;
- exact command log;
- decision column: `pass`, `near_pass`, or `fail`.

### Stage 2: Existing Dongxing Evidence Audit

Purpose: test H3 using already generated results before adding new compute.

Inputs:

- `e0_dongxing_results_synthesis_2026-06-10.md`
- `e0_dongxing_return_label_20x16_family_2026-06-10.csv`
- `e0_dongxing_return_label_50x16_family_2026-06-10.csv`
- `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`
- `e0_dongxing_planner_value_weight_sweep_2026-06-10.csv`
- related JSON rollout outputs where available.

Audit outputs:

- one unified table with transfer, scratch, label type, label budget,
  candidate-value weight, mean reward, reward standard deviation, and episode
  count;
- transfer-minus-scratch effect by matched family;
- explicit marking of unmatched rows that cannot support a transfer claim;
- list of the smallest additional rows needed for a fair transfer/scratch
  comparison, if any.

### Stage 3: Colab Pro+ Confirmatory Rollouts

Purpose: test H2 and any H1 pass rows under matched rollout budgets.

Only these rows may enter Stage 3:

- the frozen Bishan 20x16/top5 row, as the positive anchor;
- any Stage 1 50-state row with `decision=pass`;
- at most two Stage 1 near-pass rows, clearly labeled as diagnostics;
- Dongxing transfer/scratch rows needed to close an audit-identified matched
  comparison gap.

Bishan matched rollout matrix:

| family | selector | candidate score mode | candidate-value weight | seeds | rollout steps | horizon | top-k |
|---|---|---|---:|---|---:|---:|---:|
| value head | `value_filter` | `blend` | 0.1 | 0-4 | 100 | 5 | 50 |
| no value filter | baseline selector | matched | 0.0 | 0-4 | 100 | 5 | 50 |
| pairwise-only | matched checkpoint | matched | 0.1 | 0-4 | 100 | 5 | 50 |

Dongxing matched rollout matrix:

| family | init | label budget | candidate-value weight | seeds | rollout steps | horizon | top-k |
|---|---|---:|---:|---|---:|---:|---:|
| transfer | Bishan init | matched | 1.0 | 0-4 | 100 | 5 | 50 |
| scratch | local scratch | matched | 1.0 | 0-4 | 100 | 5 | 50 |

All Stage 3 rows must record:

- command;
- data root;
- checkpoint path;
- code commit;
- runtime;
- seed-level metrics;
- aggregate mean, sample standard deviation, min, and max.

### Stage 4: Independent Reproduction

Purpose: prevent a platform-specific or path-specific artifact from controlling
the conclusion.

Minimum reproduction targets:

- one positive Bishan row;
- one negative or near-pass 50-state row;
- one selected Dongxing row if data transfer is practical.

Acceptable platforms:

- Windows local machine for CPU reproducibility and evidence packaging;
- macOS for independent path/platform checks;
- Colab Pro+ for batch compute.

## 7. Stop/Go Rules

### Keep the Original Strong Theme

The original strong theme remains viable only if all conditions hold:

- at least one predefined 50-state row passes the monitor gate;
- the corresponding rollout improves over matched no-value-filter or
  pairwise-only baselines on five-seed mean reward;
- seed-level results do not show that the improvement is caused by a single
  outlier seed;
- secondary metrics do not reveal unacceptable degradation of slope,
  contiguity, or baimu-area objectives.

### Use a Conditional Mechanism Theme

Use a conditional mechanism theme if:

- some 50-state or transfer rows pass only under specific seeds, label budgets,
  or planner calibration;
- rollouts improve one primary metric but trade off another important metric;
- Dongxing transfer helps in low-label or slope-specific regimes but does not
  dominate scratch on primary reward.

The manuscript may then claim a conditional mechanism, not robust scale-up or
robust transfer superiority.

### Use the Conservative CEUS Theme

Use the conservative CEUS theme if:

- Stage 1 finds no pass and no scientifically meaningful near-pass;
- Stage 3 rollouts do not improve over matched baselines;
- transfer remains neutral or negative versus scratch after matched audit;
- reproduction fails for a claimed positive row.

This outcome still supports a defensible paper about monitor-gated value-label
generation, calibration, and external-region stress testing.

## 8. Statistical Reporting

Each confirmatory rollout table must include:

- number of episodes;
- seed list;
- mean reward;
- sample standard deviation;
- min and max reward;
- per-seed results;
- transfer-minus-scratch or value-minus-baseline differences where matched;
- slope, contiguity, and baimu-area secondary outcomes.

Do not use p-values as the only basis for claims. The primary evidence should
be effect direction, effect size, seed stability, and whether the experiment
passed the predefined monitor gate.

## 9. File and Naming Plan

Recommended new evidence files:

```text
paper10_geojepa_mpc/experiments/results/
  e0_original_vision_validation_registry_2026-06-17.md
  e0_original_vision_stage1_50state_label_matrix_2026-06-17.json
  e0_original_vision_stage1_50state_label_matrix_2026-06-17.md
  e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv
  e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md
  e0_original_vision_stage3_confirmatory_rollouts_YYYY-MM-DD.json
  e0_original_vision_stage3_confirmatory_rollouts_YYYY-MM-DD.md
```

Recommended local-only run directory:

```text
D:\test\paper10_original_vision_validation\
  stage1_label_only\
  stage2_dongxing_audit\
  stage3_colab_handoff\
  logs\
```

Large raw data, checkpoints, and untracked review outputs must remain outside
git unless they are already part of the tracked evidence package.

## 10. Implementation Boundaries

This spec does not require new model architecture. The first implementation
should reuse existing Paper10 scripts wherever possible:

- `paper10_geojepa_mpc/experiments/value_label_generation.py`
- `paper10_geojepa_mpc/experiments/value_label_monitor.py`
- `paper10_geojepa_mpc/experiments/value_label_diagnostics.py`
- `paper10_geojepa_mpc/experiments/run_e0_value_head_train.py`
- `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py`
- `paper10_geojepa_mpc/experiments/compare_multiseed_rollouts.py`
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`

New code should be limited to orchestration, summarization, and audit helpers
unless the Stage 1 results show that the candidate proposal itself needs a
separate redesign.

## 11. Review Risks and Mitigations

| risk | mitigation |
|---|---|
| Selection bias from trying many seeds | Predefine row families, report all rows, and separate confirmatory rows from exploratory ablations. |
| Monitor overfitting | Keep default thresholds fixed and report failures rather than relaxing gates. |
| Expensive rollouts on invalid labels | Run label-only gates first; train only passing or near-passing rows. |
| Transfer claim unsupported by unmatched rows | Audit matching before new Dongxing runs; label unmatched rows as calibration evidence only. |
| Negative result seen as paper failure | Preserve the CEUS conservative route and frame negative transfer/scale boundaries as evidence. |
| Platform-specific artifact | Reproduce one positive and one negative or near-pass row across platforms when practical. |

## 12. Immediate Next Step After Spec Approval

Create an implementation plan that:

1. writes a validation registry file;
2. creates or configures the Stage 1 label-only matrix;
3. runs the first Windows label-only rescue rows with `TrainOnPass = 0`;
4. summarizes Stage 1 monitor outcomes;
5. audits existing Dongxing transfer/scratch results;
6. defines the minimal Colab handoff for Stage 3 only after Stage 1 and Stage 2
   decisions are available.

No new scientific conclusion should be written until Stage 1 and Stage 2
outputs exist and are compared against this spec.
