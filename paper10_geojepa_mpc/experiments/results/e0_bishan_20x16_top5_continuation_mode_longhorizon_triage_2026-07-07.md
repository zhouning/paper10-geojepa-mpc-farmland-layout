# Bishan 20x16/top5 continuation-mode long-horizon triage

This triage follows the 10-step continuation-mode result with a 100-step check. The
purpose is to test whether `random_continuation_mode=common`, which won the short
rollout, remains useful at the full Bishan E0 episode length.

## Matched setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Mask mode: `executable`
- Candidate scoring: `candidate_score_mode=blend`, `candidate_value_weight=0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Rollout length: 100 steps
- Seeds: 0-4
- Device: CPU

The `independent` baseline was already available as one seed0 file plus one seeds1-4
file. The missing `common` seeds1-4 result was run under the same locked configuration
to complete the matched 5-seed check.

## Short-rollout result for context

At 10 steps, `common` beat `independent` on matched seeds 0-4:

| rollout length | comparison | reward mean delta | reward seed wins |
|---:|---|---:|---:|
| 10 | `common - independent` | +3.6718 | 5/5 |

That short-rollout result was treated as an escalation candidate, not as a final
algorithm default.

## 100-step aggregate result

| setting | random_continuation_mode | total_reward_mean | slope_change_pct_mean | cont_change_mean | baimu_area_change_ha_mean |
|---|---|---:|---:|---:|---:|
| baseline | `independent` | 69.4705 | -1.2507 | 0.0192 | -207.2639 |
| candidate | `common` | 56.5950 | -1.2387 | 0.0184 | -195.6354 |
| delta | `common - independent` | -12.8755 | +0.0120 | -0.0009 | +11.6285 |

Seed-level reward deltas for `common - independent` were `-11.2569`, `-13.5824`,
`-13.0790`, `-13.1817`, and `-13.2774`; `common` won 0/5 seeds on the 100-step reward
objective.

Timing is not used as a decision metric here because the historical `independent`
100-step files and the newly generated `common` files differ in recorded timing fields
and likely execution path. The decision is based on matched reward and final-state
diagnostics.

## Interpretation

The continuation-mode effect is horizon-dependent. `common` reduces short-rollout
comparison noise and improves the 10-step reward, but it fails the 100-step matched
check. In long episodes, the deterministic/common continuation trajectory appears to
over-commit to an early action pattern that produces lower accumulated reward than
the independent-continuation baseline.

This is useful negative evidence: the robust algorithm setting for the main Bishan
20x16/top5 anchor remains `random_continuation_mode=independent` for long-horizon
evaluation. The short-rollout `common` result should be documented as a triage finding,
not promoted to a manuscript-level performance claim.

## Decision

Do not promote `random_continuation_mode=common` to the main algorithm or default
setting. Keep `independent` as the long-horizon reference for `blend_w0p10`, `top_k=50`,
reward reserve 0.

The next algorithm work should target long-horizon robustness directly. Candidate
directions should be screened with a short rollout only as a triage step, then must
pass this same 100-step matched-seed gate before any claim escalation.

## Evidence files

- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json`
- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json`
- `e0_env_rollout_value_filter_blend010_h5_k50_common_cont_seed0_100step.json`
- `e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_common_cont_seeds1-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_seed0_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_seed0_100step_comparison_2026-07-07.md`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_seeds1-4_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_seeds1-4_100step_comparison_2026-07-07.md`
