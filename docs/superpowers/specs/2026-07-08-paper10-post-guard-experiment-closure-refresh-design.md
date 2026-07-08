# Paper10 Post-Guard Experiment Closure Refresh Design

Date: 2026-07-08

Status: design approved for specification review

Branch: `main`

Current saved commit before this design:
`c4a7451bda532e4b46568da9a92bd4b0bc03e819`
(`exp: simplify guard readiness to rewardtop7`)

## 1. Purpose

Paper10 now has a 20-seed true-reward guard readiness audit that promotes the
simplified `rewardtop7 margin=1.50` guard as the current primary
algorithm-readiness candidate. The older experiment-freeze, closure, and
submission-readiness boundary records still predate that July 8 guard update.

This design adds a small post-guard closure refresh so the bounded submission
route can absorb the new guard evidence without rewriting the historical June
decision records or broadening the scientific claim.

## 2. Current Position

The current bounded route remains:

- Bishan 20x16/top5 is the positive planning-support anchor.
- Stage 3 50-state rows remain boundary evidence, not positive scale-up
  evidence.
- Dongxing/Neijiang remains calibration and transfer stress-test evidence, not
  robust transfer superiority.
- Operational cadastral deployment remains out of scope.
- Final submission remains no-go until DOI, licence, data-access, citation,
  statistics, and export decisions are closed.

The July 8 guard update adds algorithm-readiness evidence, not final submission
readiness.

## 3. Goals

The implementation should create a machine-checkable refresh artifact that:

- records `rewardtop7 margin=1.50` as the current primary true-reward guard;
- preserves the bounded planning-support route;
- updates the experiment-closure reading without mutating historical June
  freeze records;
- links the refresh to the latest true-reward guard readiness JSON/Markdown;
- keeps the current no-go submission boundary and unresolved blocker list
  visible;
- adds a preflight gate so later changes cannot silently drop the refresh.

## 4. Non-Goals

This change must not:

- rerun training, label generation, or rollout experiments;
- modify the true-reward guard algorithm;
- claim universal fixed switch margins;
- claim direct 50-state Bishan scale-up success;
- claim robust Bishan-to-Dongxing transfer superiority;
- claim deployment-ready cadastral planning;
- declare Paper10 ready for final submission;
- resolve author-controlled DOI, licence, data-access, citation, statistics, or
  export decisions;
- rewrite the June experiment-freeze audit or closure register as if those
  records had originally included the July 8 guard.

## 5. New Artifact

Create:

```text
paper10_geojepa_mpc/experiments/results/
  e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json
  e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md
```

The JSON file is the machine-readable guard for preflight and tests. The
Markdown file is the author-facing closure refresh.

## 6. Source Basis

The refresh must cite these existing artifacts:

- `e0_paper10_true_reward_guard_readiness_2026-07-08.json`
- `e0_paper10_true_reward_guard_readiness_2026-07-08.md`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`
- `e0_paper10_experiment_freeze_audit_2026-06-27.md`
- `e0_paper10_experiment_closure_register_2026-06-27.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`

The refresh must state that it is source-derived and did not rerun experiments.

## 7. Required JSON Contract

The JSON payload should include:

- `date`: `2026-07-08`
- `status`: `post_guard_experiment_closure_refresh`
- `source_boundary.new_experimental_claim`: `false`
- `source_boundary.reran_rollouts`: `false`
- `source_boundary.reran_training`: `false`
- `primary_guard.audit_set`: `rewardtop7`
- `primary_guard.switch_margin`: `1.5`
- `primary_guard.n_seeds`: `20`
- `primary_guard.guard_mean_reward`: `72.19178534319884`
- `primary_guard.baseline_mean_reward`: `65.8876435268697`
- `primary_guard.mean_delta_vs_baseline`: `6.304141816329158`
- `primary_guard.seed_wins`: `20`
- `primary_guard.bootstrap_95ci_delta_lower`: `4.140109129548553`
- `primary_guard.mean_audit_action_count`: `7.7605`
- `primary_guard.dual7x7_mean_audit_action_count`: `8.1905`
- `closure_decision.default_next_phase`:
  `bounded_manuscript_assembly`
- `closure_decision.resume_broad_algorithm_redesign`: `false`
- `submission_boundary.status`: `not_submission_ready`
- `claim_locks.direct_50state_scaleup_supported`: `false`
- `claim_locks.robust_transfer_superiority_supported`: `false`
- `claim_locks.deployment_ready_supported`: `false`
- `claim_locks.universal_fixed_margin_supported`: `false`

## 8. Required Markdown Content

The Markdown report must include:

- title: `Paper10 post-guard experiment-closure refresh`;
- status: `post_guard_experiment_closure_refresh`;
- the exact phrase `source-derived; no rollout or training rerun`;
- the exact guard token `rewardtop7 margin=1.50`;
- guard values `72.1918`, `65.8876`, `6.3041`, `20 / 20`, `4.1401`,
  `7.7605`, and `8.1905`;
- a section explaining that the refresh is a closure update, not a new
  experiment;
- a section preserving the no-go submission boundary;
- explicit negative guardrails for universal margin, direct 50-state scale-up,
  robust transfer superiority, deployment-ready cadastral planning, and final
  submission readiness.

## 9. Preflight Check

Add a check named:

```text
paper10_post_guard_experiment_closure_refresh_current
```

The check should pass only if:

- both JSON and Markdown refresh artifacts exist;
- required source-basis filenames are present in Markdown;
- the JSON contract fields above match the latest guard values;
- Markdown contains the required numeric tokens and negative guardrails;
- the refresh references the existing no-go submission-readiness boundary;
- the check is registered in `CHECKS`.

The check should fail if the refresh contains unqualified positive wording for:

- universal fixed switch margin;
- direct 50-state Bishan scale-up success;
- robust Bishan-to-Dongxing transfer superiority;
- deployment-ready cadastral planning;
- final submission readiness.

Negative guardrail wording is allowed.

## 10. Testing Strategy

Use TDD for implementation.

Add focused tests before implementation:

- unit tests for the refresh builder to verify source-derived guard values,
  no-rerun boundaries, closure decision, no-go status, and claim locks;
- Markdown tests for required source links, numeric values, and negative
  guardrails;
- preflight tests confirming the new check is registered and fails on missing
  refresh artifacts;
- a preflight overclaim rejection test for unqualified final-submission-ready
  and 50-state/transfer/deployment claims.

## 11. Implementation Shape

Add a module:

```text
paper10_geojepa_mpc/experiments/post_guard_experiment_closure_refresh.py
```

The module should mirror the local pattern used by the true-reward guard
readiness and result-table freeze modules:

- load existing JSON and Markdown source files;
- derive a deterministic payload;
- render Markdown from the payload;
- expose a CLI that writes the JSON and Markdown artifacts;
- keep all values source-derived, with no stochastic work.

## 12. Verification

Run focused verification:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_post_guard_experiment_closure_refresh.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Then run full verification:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
git diff --check
```

Expected results:

- focused pytest passes;
- preflight prints `Paper10 preflight: PASS`;
- output includes `[ok] paper10_post_guard_experiment_closure_refresh_current`;
- full pytest passes;
- `git diff --check` exits 0.

## 13. Commit Plan

Use two commits:

1. `docs: design paper10 post-guard closure refresh`
2. `exp: add post-guard closure refresh`

The implementation commit should include only the refresh module, tests,
generated JSON/Markdown artifacts, and preflight wiring.
