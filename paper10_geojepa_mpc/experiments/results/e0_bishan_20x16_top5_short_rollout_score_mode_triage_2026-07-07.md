# Bishan 20x16/top5 score-mode triage

This packet records a low-cost candidate-score triage before any longer 100-step or 50-state escalation.

## Candidate-score sweep

Source: `e0_bishan_20x16_top5_candidate_score_sweep_zscore_blend_2026-07-07.json`

| rank | key | topk_overlap | top1_regret | spearman |
| ---: | --- | ---: | ---: | ---: |
| 1 | blend_w0p10 | 0.9760 | 0.0018 | 0.9998 |
| 2 | zscore_blend_w0p20 | 0.9460 | 0.0074 | 0.9993 |
| 3 | zscore_blend_w0p50 | 0.8640 | 0.0389 | 0.9955 |
| 4 | zscore_blend_w0p80 | 0.8220 | 0.0389 | 0.9887 |
| 5 | value_w0p50 | 0.7660 | 0.0389 | 0.9824 |

## Single-seed 10-step short rollout check

All rows use the same Bishan 20x16/top5 checkpoint, `seed=0`, `horizon=5`, `top_k=50`, executable mask, and `rollout_steps=10`.

| key | total_reward | positive_steps | negative_steps | final_slope_change_pct | final_cont_change | final_baimu_area_change_ha |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| blend_w0p10 | 9.7064 | 9 | 1 | -0.1751 | 0.0018 | -35.0349 |
| zscore_blend_w0p20 | 8.2358 | 10 | 0 | -0.1012 | 0.0015 | -13.9941 |
| value_w0p50 | 6.4019 | 8 | 2 | -0.2446 | 0.0006 | -47.6333 |

## Matched 5-seed 10-step short rollout check

Source: `e0_bishan_20x16_top5_blend010_vs_zscore020_5seed_10step_comparison_2026-07-07.json`

| metric | zscore_blend_w0p20 | blend_w0p10 | delta |
| --- | ---: | ---: | ---: |
| total_reward_mean | 8.8671 | 14.1054 | 5.2383 |
| slope_change_pct_mean | -0.2036 | -0.1989 | 0.0046 |
| cont_change_mean | 0.0014 | 0.0017 | 0.0003 |
| baimu_area_change_ha_mean | -47.6782 | -42.4589 | 5.2193 |
| mean_select_time_sec | 0.0273 | 0.0328 | 0.0055 |

| seed | zscore_blend_w0p20 reward | blend_w0p10 reward | delta |
| ---: | ---: | ---: | ---: |
| 0 | 8.2358 | 9.7064 | 1.4706 |
| 1 | 11.8189 | 16.3140 | 4.4951 |
| 2 | 10.4617 | 14.7417 | 4.2801 |
| 3 | 10.2292 | 15.5221 | 5.2930 |
| 4 | 3.5898 | 14.2427 | 10.6529 |

## Decision

Keep `blend_w0p10` as the current Bishan 20x16/top5 escalation candidate. The z-score blend variant is not justified for escalation on this anchor: `zscore_blend_w0p20` is close in the candidate-overlap diagnostic but loses on all five matched 10-step seeds, with mean reward delta `+5.2383` in favor of `blend_w0p10`; higher z-score weights diverge more in the sweep.

The next experiment should keep `blend_w0p10` fixed and move to a 100-step, 5-seed confirmation only if the goal is to strengthen the Bishan anchor. If the goal is algorithm invention rather than confirmation, the next algorithmic branch should not be higher-weight z-score blending; it should target value calibration or candidate-generation diversity.

## Boundary

- No training was rerun.
- These are low-cost diagnostics and 10-step smoke rollouts, not confirmatory evidence.
- The result weakens the immediate case for z-score blend on Bishan 20x16/top5, but it does not rule out z-score blend under different checkpoints, regions, or candidate-generation regimes.