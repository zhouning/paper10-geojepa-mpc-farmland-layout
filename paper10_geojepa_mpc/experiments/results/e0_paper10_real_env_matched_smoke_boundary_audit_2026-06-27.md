# Paper10 real-environment smoke boundary audit

Date: 2026-06-27

Status: execution-chain boundary audit for the current full-Bishan real-environment smoke reports.

## Boundary

This audit is not a planning-quality result and not a short-horizon performance comparison. It only records that the tracked real-environment smoke reports exercise the full Bishan execution path.

Same action/reward trace: `true`

Reasons:
- configuration settings differ across smoke reports
- single seed and five executed steps
- matched smoke reports have identical action/reward traces
- value-filter run includes one negative reward step

Different configuration fields: `checkpoint`, `selector`, `candidate_score_mode`, `candidate_value_weight`

## Smoke Rows

| smoke | selector | horizon | top_k | steps | total reward | positive steps | negative steps | min executable-valid actions |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| matched_paper9 | `paper9` | 5 | 50 | 5 | 2.4254 | 4 | 1 | 2312 |
| matched_value_filter | `value_filter` | 5 | 50 | 5 | 2.4254 | 4 | 1 | 2312 |

## Source Reports

- `matched_paper9`: `paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_matched_paper9_smoke_5step_h5_k50_seed0_2026-06-27.json`
- `matched_value_filter`: `paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_matched_value_filter_smoke_5step_h5_k50_seed0_2026-06-27.json`

## Interpretation Boundary

These smoke reports confirm execution-chain reachability only. They are not a planning-quality result, not a short-horizon performance comparison, and not support for a new scale-up claim.

A negative reward step keeps the current real-environment evidence in smoke-test territory and prevents treating the row as performance evidence.
