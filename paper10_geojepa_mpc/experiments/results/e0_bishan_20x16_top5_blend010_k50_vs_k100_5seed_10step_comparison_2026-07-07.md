# Multiseed rollout comparison

Baseline: `blend_w0p10_k100_10step`
Candidate: `blend_w0p10_k50_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 11.3465 | 14.1054 | 2.7589 |
| slope_change_pct_mean | -0.1769 | -0.1989 | -0.0220 |
| cont_change_mean | 0.0018 | 0.0017 | -0.0002 |
| baimu_area_change_ha_mean | -39.7942 | -42.4589 | -2.6647 |
| mean_select_time_sec | 0.0481 | 0.0328 | -0.0153 |
| mean_score_time_sec | 0.0056 | 0.0063 | 0.0007 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -0.9397 | -0.0015 | -0.0005 | -12.7761 | -0.0214 |
| 1 | 0.9904 | -0.0332 | -0.0011 | -2.4990 | -0.0123 |
| 2 | 5.2699 | 0.0293 | 0.0021 | 15.7445 | -0.0136 |
| 3 | -3.1806 | -0.1232 | -0.0009 | -47.5993 | -0.0141 |
| 4 | 11.6543 | 0.0186 | -0.0004 | 33.8062 | -0.0150 |
