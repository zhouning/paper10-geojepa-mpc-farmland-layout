# Multiseed rollout comparison

Baseline: `blend_w0p10_independent_seed0_100step`
Candidate: `blend_w0p10_stable_order_seed0_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 67.7135 | 68.0457 | 0.3322 |
| slope_change_pct_mean | -1.2858 | -1.2712 | 0.0146 |
| cont_change_mean | 0.0220 | 0.0205 | -0.0015 |
| baimu_area_change_ha_mean | -204.7689 | -201.0977 | 3.6712 |
| mean_select_time_sec | 2.5422 | 3.4500 | 0.9078 |
| mean_score_time_sec | 0.0000 | 0.0000 | 0.0000 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.3322 | 0.0146 | -0.0015 | 3.6712 | 0.9078 |
