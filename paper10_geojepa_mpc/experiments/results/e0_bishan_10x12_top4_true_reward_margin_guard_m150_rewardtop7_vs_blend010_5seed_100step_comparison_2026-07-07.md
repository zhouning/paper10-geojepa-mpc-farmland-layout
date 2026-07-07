# Multiseed rollout comparison

Baseline: `10x12_top4_blend010_baseline`
Candidate: `10x12_top4_rewardtop7_m150`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 65.2566 | 69.2652 | 4.0086 |
| slope_change_pct_mean | -1.2923 | -1.2778 | 0.0145 |
| cont_change_mean | 0.0198 | 0.0193 | -0.0005 |
| baimu_area_change_ha_mean | -231.3513 | -226.1877 | 5.1636 |
| mean_select_time_sec | 2.5709 | 0.0289 | -2.5421 |
| mean_score_time_sec | 0.7330 | 0.0023 | -0.7307 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.1341 | 0.0722 | 0.0027 | 69.1377 | -2.3979 |
| 1 | -13.7568 | -0.1852 | -0.0044 | -89.8576 | -2.5712 |
| 2 | 13.9032 | 0.1254 | 0.0018 | 41.2328 | -2.8215 |
| 3 | 5.1330 | -0.0070 | -0.0013 | -5.2891 | -2.6783 |
| 4 | 12.6297 | 0.0670 | -0.0014 | 10.5940 | -2.2416 |
