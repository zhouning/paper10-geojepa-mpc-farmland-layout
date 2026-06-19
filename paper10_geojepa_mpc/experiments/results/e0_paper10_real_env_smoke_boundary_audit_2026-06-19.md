# Paper10 real-environment smoke boundary audit

Date: 2026-06-19

Status: execution-chain boundary audit for the current full-Bishan real-environment smoke reports.

## Boundary

This audit is not a planning-quality result and not a short-horizon performance comparison. It only records that the two tracked real-environment smoke reports exercise the full Bishan execution path.

Reasons:
- different checkpoint, selector, horizon, and top_k settings
- single seed and five executed steps
- value-filter run includes one negative reward step

Different configuration fields: `checkpoint`, `selector`, `horizon`, `top_k`, `candidate_score_mode`, `candidate_value_weight`

## Smoke Rows

| smoke | selector | horizon | top_k | steps | total reward | positive steps | negative steps | min executable-valid actions |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| paper9_selector | `paper9` | 3 | 20 | 5 | 7.6466 | 5 | 0 | 2313 |
| value_filter_selector | `value_filter` | 5 | 50 | 5 | 2.4254 | 4 | 1 | 2312 |

## Source Reports

- `paper9_selector`: `paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.json`
- `value_filter_selector`: `paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.json`

## Interpretation Boundary

These smoke reports confirm execution-chain reachability only. They are not a planning-quality result, not a short-horizon performance comparison, and not support for a new scale-up claim.

The value-filter row contains one negative reward step. That observation keeps the current real-environment evidence in smoke-test territory and prevents treating the row as performance evidence.
