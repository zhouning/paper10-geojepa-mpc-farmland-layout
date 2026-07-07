# Bishan 20x16/top5 reward-reserve triage

This packet evaluates the reward-reserve candidate-pool algorithm added to `value_filter_mpc_select_action`. The algorithm reserves a fixed number of candidate slots for reward-top actions before filling the remaining slots by the configured candidate score.

## Algorithm knob

- parameter: `candidate_reward_reserve`
- default: `0`, preserving the previous selector behavior
- tested value: `5` reserved reward-top slots out of `top_k=50`
- checkpoint: `e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt`
- rollout protocol: Bishan, executable mask, `horizon=5`, `top_k=50`, `rollout_steps=10`, seeds `0-4`

## 5-seed short-rollout results

| candidate pool | score mode | reserve | total_reward_mean | delta vs no-reserve peer | mean_select_time_sec |
| --- | --- | ---: | ---: | ---: | ---: |
| blend_w0p10 | blend | 0 | 14.1054 | 0.0000 | 0.0328 |
| blend_w0p10_reserve5 | blend | 5 | 10.1548 | -3.9506 | 0.0431 |
| zscore_blend_w0p20 | zscore_blend | 0 | 8.8671 | 0.0000 | 0.0273 |
| zscore_blend_w0p20_reserve5 | zscore_blend | 5 | 10.8361 | 1.9690 | 0.0370 |

## Pairwise evidence

- `blend_w0p10_reserve5` vs `blend_w0p10`: mean reward delta `-3.9506`; reserve wins only seed 0 and loses seeds 1-4.
- `zscore_blend_w0p20_reserve5` vs `zscore_blend_w0p20`: mean reward delta `+1.9690`, but seed deltas are unstable: `-1.3963`, `+0.3908`, `+10.3951`, `-6.0682`, `+6.5236`.
- `blend_w0p10` vs `zscore_blend_w0p20_reserve5`: mean reward delta `+3.2693`; blend still wins 4/5 seeds.

## Decision

Do not promote reward-reserve to the current Bishan 20x16/top5 escalation path. It is a useful algorithmic branch because it can improve the weaker z-score selector, but it degrades the current best blend selector and increases selection time.

The current best short-rollout configuration remains `candidate_score_mode=blend`, `candidate_value_weight=0.10`, `candidate_reward_reserve=0`.

## Boundary

- No training was rerun.
- These are 10-step, 5-seed diagnostic rollouts, not confirmatory 100-step results.
- Reward-reserve should remain available as an explicit selector knob for future low-top-k, value-heavy, or cross-region diagnostics, but it should not be silently enabled by default.