# Bishan 20x16/top5 stable-order long-horizon triage

This triage tests whether `stable_candidate_order=True` should be promoted for the
current long-horizon value-filter MPC setting. The knob keeps the selected candidate
set fixed but sorts candidate action ids before rollout. Under independent random
continuations, that changes which candidate receives which sampled continuation path,
so it must be tested as an algorithmic setting rather than treated as a harmless
implementation detail.

## Matched setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Mask mode: `executable`
- Candidate scoring: `candidate_score_mode=blend`, `candidate_value_weight=0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Random continuation mode: `independent`
- Rollout length: 100 steps
- Seeds: 0-4
- Device: CPU

Seed0 stable-order 100-step evidence already existed. Seeds1-4 were run under the
same locked configuration to complete the matched 5-seed gate.

## 100-step aggregate result

| setting | stable_candidate_order | total_reward_mean | slope_change_pct_mean | cont_change_mean | baimu_area_change_ha_mean |
|---|---:|---:|---:|---:|---:|
| baseline | `False` | 69.4705 | -1.2507 | 0.0192 | -207.2639 |
| candidate | `True` | 61.7235 | -1.2336 | 0.0215 | -190.0865 |
| delta | `True - False` | -7.7470 | +0.0172 | +0.0023 | +17.1774 |

Seed-level reward deltas for `stable_candidate_order=True` relative to baseline were
`+0.3322`, `-2.8124`, `-12.2444`, `-10.1717`, and `-13.8387`; stable order won 1/5
seeds and lost the 5-seed reward mean.

The seed0 pilot was therefore a false-positive escalation signal. The candidate
preserved slightly more baimu area and improved contiguity in the aggregate, but the
current primary objective is long-horizon total reward, where the loss is material.

Timing is not used as a decision metric here because the historical baseline files and
the newly generated stable-order files differ in recorded timing fields and likely
execution path. The decision is based on matched reward and final-state diagnostics.

## Related non-escalated pilot

An existing seed0 20-step pilot for `n_rollouts=3` produced reward `17.5703`, below
the matched 20-step baseline reward `23.5299`. This was not escalated because it
already failed the cheap pilot gate.

## Decision

Do not promote `stable_candidate_order=True` to the main algorithm. Keep
`stable_candidate_order=False`, `random_continuation_mode=independent`, `top_k=50`,
and reward reserve 0 as the long-horizon reference for `blend_w0p10`.

The next algorithm work should not alter random-continuation bookkeeping. It should
target the learned/action scoring side more directly, with any pilot required to pass
the same 100-step matched-seed gate before promotion.

## Evidence files

- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json`
- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json`
- `e0_env_rollout_value_filter_blend010_h5_k50_stable_order_seed0_100step.json`
- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_stable_order_seeds1-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_stable_order_vs_baseline_seed0_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_stable_order_vs_baseline_seed0_100step_comparison_2026-07-07.md`
- `e0_bishan_20x16_top5_blend010_stable_order_vs_baseline_seeds1-4_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_stable_order_vs_baseline_seeds1-4_100step_comparison_2026-07-07.md`
