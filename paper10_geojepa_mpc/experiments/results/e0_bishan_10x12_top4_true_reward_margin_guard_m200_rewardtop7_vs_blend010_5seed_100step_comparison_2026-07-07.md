# Multiseed rollout comparison

Baseline: `10x12_top4_blend010_baseline`
Candidate: `10x12_top4_rewardtop7_m200`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 65.2566 | 72.1585 | 6.9019 |
| slope_change_pct_mean | -1.2923 | -1.2622 | 0.0301 |
| cont_change_mean | 0.0198 | 0.0188 | -0.0011 |
| baimu_area_change_ha_mean | -231.3513 | -208.0559 | 23.2954 |
| mean_select_time_sec | 2.5709 | 0.0259 | -2.5451 |
| mean_score_time_sec | 0.7330 | 0.0023 | -0.7307 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -4.0277 | 0.1198 | 0.0038 | 82.5950 | -2.3991 |
| 1 | 6.7129 | -0.1051 | -0.0044 | -28.1961 | -2.5714 |
| 2 | 17.0337 | 0.0994 | -0.0022 | 38.3292 | -2.8262 |
| 3 | 10.8365 | 0.0520 | 0.0000 | 30.1140 | -2.6827 |
| 4 | 3.9540 | -0.0156 | -0.0025 | -6.3651 | -2.2459 |
