# Bishan 20x16/top5 continuation-mode triage

This triage tests whether random continuation inside the value-filter MPC rollout
should compare candidates with independent random continuations or with common random
continuations. The latter uses the same continuation action at each rollout step for
all candidates, reducing candidate-to-candidate Monte Carlo noise while leaving the
candidate pool, scoring family, and downstream environment unchanged.

## Matched setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Mask mode: `executable`
- Candidate scoring: `candidate_score_mode=blend`, `candidate_value_weight=0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Rollout length: 10 steps
- Seeds: 0-4
- Device: CPU

## Aggregate comparison

| setting | random_continuation_mode | total_reward_mean | mean_select_time_sec | mean_score_time_sec | slope_change_pct_mean | cont_change_mean | baimu_area_change_ha_mean |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline | `independent` | 14.1054 | 0.0328 | 0.0063 | -0.1989 | 0.0017 | -42.4589 |
| candidate | `common` | 17.7772 | 0.0302 | 0.0052 | -0.3074 | 0.0013 | -64.6935 |

## Paired outcome

| comparison | reward mean delta | reward seed wins | select-time mean delta | notes |
|---|---:|---:|---:|---|
| `common` vs `independent` | +3.6718 | 5/5 | -0.0026 sec | `common` improves the short-rollout reward without increasing mean selection time. |

Seed-level reward deltas for `common - independent` were `+8.0708`, `+1.4632`,
`+3.0355`, `+2.2551`, and `+3.5345`.

## Interpretation

`common` continuation is the strongest short-rollout candidate on the current Bishan
20x16/top5 anchor. The result is algorithmically meaningful because it changes only
the rollout comparison noise structure inside the fixed `top_k=50` budget; it does not
increase the candidate pool or relax the executable mask.

The five `common` seeds produced the same 10-step action trajectory and reward. This
is a useful stability signal for this anchor, but it also means the result should not
be over-interpreted as broad stochastic robustness. It should be escalated before any
final manuscript-level claim.

## Decision

Promote `random_continuation_mode=common` as the next algorithm setting to escalate
against the previous `independent` baseline. Do not yet change publication claims or
global defaults until a longer rollout confirms the gain under the same locked
configuration.

Recommended next gate:

- Bishan E0, 20x16/top5, `blend_w0p10`, `top_k=50`, reward reserve 0
- Compare `common` against the existing `independent` setting on matched seeds 0-4
- Increase rollout length beyond the 10-step triage, without retuning `top_k`,
  candidate weight, or reserve after seeing these results

## Evidence files

- `e0_bishan_20x16_top5_short_rollout_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_short_rollout_blend010_common_continuation_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_blend010_common_vs_independent_5seed_10step_comparison_2026-07-07.md`
