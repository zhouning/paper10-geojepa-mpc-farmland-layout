# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_10step`
Candidate: `blend_w0p10_true_reward_guard_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 14.1054 | 13.9578 | -0.1476 |
| slope_change_pct_mean | -0.1989 | -0.3709 | -0.1720 |
| cont_change_mean | 0.0017 | 0.0010 | -0.0007 |
| baimu_area_change_ha_mean | -42.4589 | -82.8632 | -40.4043 |
| mean_select_time_sec | 0.0328 | 0.0855 | 0.0527 |
| mean_score_time_sec | 0.0063 | 0.0120 | 0.0057 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 4.3255 | -0.1947 | -0.0007 | -46.3382 | 0.0708 |
| 1 | -2.2822 | -0.0994 | 0.0001 | -17.5321 | 0.0474 |
| 2 | -0.7099 | -0.1906 | -0.0019 | -42.2044 | 0.0544 |
| 3 | -1.4903 | -0.1316 | -0.0002 | -23.7834 | 0.0463 |
| 4 | -0.5809 | -0.2436 | -0.0006 | -72.1637 | 0.0448 |
