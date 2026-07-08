# Paper10 post-guard experiment-closure refresh

Date: 2026-07-08

Status: post_guard_experiment_closure_refresh

Status note: source-derived; no rollout or training rerun.

This refresh is a closure update, not a new experiment.
It records how the July 8 true-reward guard readiness evidence changes the bounded Paper10 experiment-closure reading without mutating historical June records.

## Source basis

- `e0_paper10_true_reward_guard_readiness_2026-07-08.json`
- `e0_paper10_true_reward_guard_readiness_2026-07-08.md`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`
- `e0_paper10_experiment_freeze_audit_2026-06-27.md`
- `e0_paper10_experiment_closure_register_2026-06-27.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`

## Current primary guard

The current primary true-reward guard is `rewardtop7 margin=1.50` for Bishan 20x16/top5.

| metric | value |
|---|---:|
| baseline mean reward | 65.8876 |
| guard mean reward | 72.1918 |
| mean delta vs baseline | 6.3041 |
| seed wins | 20 / 20 |
| bootstrap 95% CI lower | 4.1401 |
| mean audited actions | 7.7605 |
| dual7x7 mean audited actions | 8.1905 |

## Closure decision

Default next phase: `bounded_manuscript_assembly`.

Do not resume broad algorithm redesign for the bounded route.
Do not rewrite the June experiment-freeze audit or closure register as if those records originally included this July 8 guard.

## Submission boundary

Submission status remains `not_submission_ready`; this is not final submission readiness.

Open blockers remain:
- repository DOI or anonymous reviewer link
- code licence
- generated-data rights and checkpoint or model-weight rights
- full Bishan Tool2 data access route
- GPKG-root geospatial input access route
- Dongxing/Neijiang prepared-data access route
- citation policy for local-only sources, preprints, and final reference style
- statistical reporting policy for descriptive results versus hypothesis tests
- Main Figure 1 final schematic artwork and journal-specific figure/table export rules

## Claim locks

Do not claim a universal fixed switch margin.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not treat this refresh as final submission readiness.
