# Multiseed rollout comparison

Baseline: `original_seed0_from_5seed`
Candidate: `value_filter_blend010_common_cont_seed0`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 67.5437 | 56.4566 | -11.0871 |
| slope_change_pct_mean | -1.2645 | -1.2387 | 0.0258 |
| cont_change_mean | 0.0195 | 0.0184 | -0.0011 |
| baimu_area_change_ha_mean | -211.8544 | -195.6354 | 16.2190 |
| mean_select_time_sec | 1.2406 | 4.2466 | 3.0059 |
| mean_score_time_sec | 0.0000 | 0.0000 | 0.0000 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -14.4978 | 0.0546 | -0.0001 | 38.7335 | 3.1625 |
