# Bishan 20x16/top5 top-k capacity triage

This triage checks whether the current `top_k=50` setting for the best short-rollout
candidate policy (`candidate_score_mode=blend`, `candidate_value_weight=0.10`) is
an arbitrary historical default or a useful operating point.

## Matched setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Mask mode: `executable`
- Rollout length: 10 steps
- Seeds: 0-4
- Device: CPU
- Reward reserve: 0

## Aggregate results

| setting | total_reward_mean | mean_select_time_sec | mean_score_time_sec | slope_change_pct_mean | cont_change_mean | baimu_area_change_ha_mean |
|---|---:|---:|---:|---:|---:|---:|
| `top_k=20` | 12.5148 | 0.0166 | 0.0032 | -0.2531 | 0.0012 | -65.8026 |
| `top_k=50` | 14.1054 | 0.0328 | 0.0063 | -0.1989 | 0.0017 | -42.4589 |
| `top_k=100` | 11.3465 | 0.0481 | 0.0056 | -0.1769 | 0.0018 | -39.7942 |

## Paired comparisons

| comparison | reward mean delta | reward seed wins | select-time mean delta | interpretation |
|---|---:|---:|---:|---|
| `top_k=50` vs `top_k=20` | +1.5906 | 3/5 | +0.0162 sec | `top_k=20` is faster, but loses mean reward and has worse aggregate final slope/baimu changes. |
| `top_k=50` vs `top_k=100` | +2.7589 | 3/5 | -0.0153 sec | Expanding to `top_k=100` is slower and lowers mean reward under the current objective. |

## Decision

Keep `top_k=50` as the Bishan 20x16/top5 short-rollout escalation setting for the
current best scoring family (`blend_w0p10`). Do not shrink to `top_k=20` for the
main anchor because the reward loss is not negligible. Do not expand to `top_k=100`
because it increases selection cost and reduces mean reward, even though some final
terrain/area diagnostics are competitive.

The next useful algorithm work should not be blind candidate-pool expansion. It should
target better candidate ranking or rollout evaluation inside the existing `top_k=50`
budget, and any new candidate should beat `blend_w0p10`, `top_k=50`, reward reserve 0
on this same 5-seed, 10-step Bishan anchor before escalation.

## Evidence files

- `e0_bishan_20x16_top5_short_rollout_blend010_k20_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_short_rollout_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_short_rollout_blend010_k100_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_k50_vs_k20_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_k50_vs_k20_5seed_10step_comparison_2026-07-07.md`
- `e0_bishan_20x16_top5_blend010_k50_vs_k100_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_k50_vs_k100_5seed_10step_comparison_2026-07-07.md`
