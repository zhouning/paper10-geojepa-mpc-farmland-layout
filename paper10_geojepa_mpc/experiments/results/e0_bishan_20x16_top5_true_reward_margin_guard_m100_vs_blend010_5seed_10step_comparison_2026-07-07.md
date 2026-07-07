# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_10step`
Candidate: `blend_w0p10_margin_true_reward_guard_m100_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 14.1054 | 19.4160 | 5.3106 |
| slope_change_pct_mean | -0.1989 | -0.3379 | -0.1390 |
| cont_change_mean | 0.0017 | -0.0002 | -0.0018 |
| baimu_area_change_ha_mean | -42.4589 | -96.5324 | -54.0735 |
| mean_select_time_sec | 0.0328 | 0.0292 | -0.0036 |
| mean_score_time_sec | 0.0063 | 0.0027 | -0.0036 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 12.2382 | -0.1752 | -0.0013 | -63.1375 | -0.0042 |
| 1 | 4.5415 | -0.0702 | -0.0018 | -41.4532 | -0.0078 |
| 2 | 6.7558 | -0.1704 | -0.0033 | -63.4375 | -0.0112 |
| 3 | 1.2524 | -0.0927 | -0.0012 | -26.9188 | 0.0053 |
| 4 | 1.7651 | -0.1864 | -0.0015 | -75.4206 | 0.0002 |
