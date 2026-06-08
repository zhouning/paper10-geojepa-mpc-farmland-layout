# Multiseed rollout comparison

Baseline: `original_h5_k50_reward`
Candidate: `independent_value_filter_blend010_h5_k50`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 67.5437 | 62.0344 | -5.5092 |
| slope_change_pct_mean | -1.2645 | -1.2602 | 0.0043 |
| cont_change_mean | 0.0195 | 0.0200 | 0.0005 |
| baimu_area_change_ha_mean | -211.8544 | -201.9226 | 9.9318 |
| mean_select_time_sec | 1.2406 | 3.3124 | 2.0717 |
| mean_score_time_sec | 0.0000 | 0.9835 | 0.9835 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.0458 | -0.0180 | 0.0008 | 13.8871 | 3.0641 |
| 1 | -4.3576 | 0.0754 | 0.0004 | 56.4732 | 2.7365 |
| 2 | -3.6178 | -0.0322 | 0.0017 | -5.2948 | 1.5819 |
| 3 | 1.6140 | -0.0349 | 0.0010 | -0.9590 | 0.8371 |
| 4 | -22.2305 | 0.0309 | -0.0015 | -14.4474 | 2.1390 |
