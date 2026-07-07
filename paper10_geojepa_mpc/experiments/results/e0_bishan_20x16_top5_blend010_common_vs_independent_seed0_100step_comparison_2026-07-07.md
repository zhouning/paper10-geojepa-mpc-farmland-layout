# Multiseed rollout comparison

Baseline: `blend_w0p10_independent_seed0_100step`
Candidate: `blend_w0p10_common_seed0_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 67.7135 | 56.4566 | -11.2569 |
| slope_change_pct_mean | -1.2858 | -1.2387 | 0.0471 |
| cont_change_mean | 0.0220 | 0.0184 | -0.0037 |
| baimu_area_change_ha_mean | -204.7689 | -195.6354 | 9.1335 |
| mean_select_time_sec | 2.5422 | 4.2466 | 1.7043 |
| mean_score_time_sec | 0.0000 | 0.0000 | 0.0000 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -11.2569 | 0.0471 | -0.0037 | 9.1335 | 1.7043 |
