# Multiseed rollout comparison

Baseline: `blend_w0p10_margin_guard_m100_audit5x5_100step`
Candidate: `blend_w0p10_margin_guard_m100_audit7x7_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 72.9160 | 74.1137 | 1.1976 |
| slope_change_pct_mean | -1.2834 | -1.2759 | 0.0075 |
| cont_change_mean | 0.0211 | 0.0207 | -0.0004 |
| baimu_area_change_ha_mean | -203.2705 | -205.5800 | -2.3095 |
| mean_select_time_sec | 0.0294 | 0.0855 | 0.0562 |
| mean_score_time_sec | 0.0029 | 0.0146 | 0.0116 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -5.0612 | -0.0499 | -0.0018 | -36.7987 | 0.0001 |
| 1 | 0.0471 | 0.0613 | 0.0005 | 38.4413 | 0.0020 |
| 2 | -3.4873 | 0.0468 | -0.0016 | 4.9757 | 0.0071 |
| 3 | 9.4841 | 0.0036 | 0.0018 | 2.9281 | 0.0379 |
| 4 | 5.0054 | -0.0243 | -0.0008 | -21.0940 | 0.2338 |
