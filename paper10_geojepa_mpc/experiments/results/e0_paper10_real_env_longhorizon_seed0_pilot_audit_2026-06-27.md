# Paper10 real-data long-horizon seed0 pilot audit

Date: 2026-06-27

Status: locked seed0 pilot; not final planning-quality evidence.

## Boundary

The value-filter candidate did not beat matched Paper9 on this seed0 pilot; value-filter superiority is not supported.

The next confirmatory step remains the same matched protocol on matched seeds `0-4`. Do not tune thresholds, top_k, horizon, or candidate weight to rescue this seed0 result.

## Sources

- `matched_paper9`: `reviewer_outputs\paper10_real_env_matched_paper9_100step_h5_k50_seed0_2026-06-27.json`
- `matched_value_filter`: `reviewer_outputs\paper10_real_env_matched_value_filter_100step_h5_k50_seed0_2026-06-27.json`

## Run Outcomes

| metric | matched Paper9 | value-filter | delta candidate-baseline |
|---|---:|---:|---:|
| total reward | 70.9543 | 67.7135 | -3.2408 |
| final slope change pct | -1.2933 | -1.2858 | 0.0075 |
| final contiguity change | 0.0185 | 0.0220 | 0.0036 |
| final baimu area change ha | -234.3689 | -204.7689 | 29.6000 |
| negative reward steps | 13 | 6 | -7 |

## Trace Diagnostics

| diagnostic | value |
|---|---:|
| first action divergence step | 9 |
| shared prefix steps | 8 |
| position action overlap count | 9 |
| unique action overlap count | 74 |

## Evidence Boundary

- Single seed only; descriptive pilot evidence only.
- No inferential statistics or significance claims are introduced.
- No broad scale-up or cross-region superiority claim is supported.
