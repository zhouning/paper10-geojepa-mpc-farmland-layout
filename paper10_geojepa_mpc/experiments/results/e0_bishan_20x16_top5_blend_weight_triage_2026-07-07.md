# Bishan 20x16/top5 blend-weight triage

This triage checks whether the current `candidate_value_weight=0.10` remains the
best working point for the `blend` candidate-scoring family after the long-horizon
continuation and ordering checks ruled out random-continuation bookkeeping changes.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Mask mode: `executable`
- Candidate score mode: `blend`
- Top-k capacity: 50
- Reward reserve: 0
- Random continuation mode: `independent`
- Stable candidate order: `False`
- Device: CPU

## Existing left-side pilot

An existing seed0 20-step pilot showed that moving left from `0.10` to `0.05` reduced
reward:

| setting | seed | rollout steps | total reward |
|---|---:|---:|---:|
| `blend_w0p05` | 0 | 20 | 22.8675 |
| `blend_w0p10` | 0 | 20 | 23.5299 |

Because `0.05` already failed this cheap pilot, it was not escalated to a 5-seed or
100-step check.

## New right-side pilot

The missing right-side check was run as a matched 5-seed, 10-step pilot for
`candidate_value_weight=0.15`.

| setting | total_reward_mean | slope_change_pct_mean | cont_change_mean | baimu_area_change_ha_mean |
|---|---:|---:|---:|---:|
| `blend_w0p10` | 14.1054 | -0.1989 | 0.0017 | -42.4589 |
| `blend_w0p15` | 9.2518 | -0.1954 | 0.0021 | -37.2325 |
| delta, `0.15 - 0.10` | -4.8536 | +0.0036 | +0.0004 | +5.2264 |

Seed-level reward deltas for `blend_w0p15 - blend_w0p10` were `-1.2255`,
`-4.7745`, `+1.1952`, `-10.2655`, and `-9.1977`; `0.15` won 1/5 seeds and lost the
mean reward.

## Decision

Do not promote `candidate_value_weight=0.15` to long-horizon testing. Keep
`candidate_value_weight=0.10` as the active `blend` weight for Bishan 20x16/top5.

This closes the immediate left/right local weight check around `0.10`: `0.05` was
worse on the seed0 20-step pilot, while `0.15` was worse on the stronger matched
5-seed 10-step pilot. The next algorithm work should not be a blind scalar-weight
sweep. It should examine the value/reward ranking failure modes directly.

## Evidence files

- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend005_h5_k50_seed0_20step.json`
- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_20step.json`
- `e0_bishan_20x16_top5_short_rollout_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_short_rollout_blend015_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_blend015_vs_blend010_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend015_vs_blend010_5seed_10step_comparison_2026-07-07.md`
