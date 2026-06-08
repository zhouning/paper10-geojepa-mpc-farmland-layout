# Multiseed rollout comparison

Baseline: `original_seed0_from_5seed`
Candidate: `value_filter_blend010_stable_order_seed0`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 67.5437 | 68.0457 | 0.5020 |
| slope_change_pct_mean | -1.2645 | -1.2712 | -0.0067 |
| cont_change_mean | 0.0195 | 0.0205 | 0.0010 |
| baimu_area_change_ha_mean | -211.8544 | -201.0977 | 10.7567 |
| mean_select_time_sec | 1.2406 | 3.4500 | 2.2094 |
| mean_score_time_sec | 0.0000 | 0.0000 | 0.0000 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -2.9087 | 0.0221 | 0.0020 | 33.2712 | 2.3660 |
