# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m150`
Candidate: `10x12_top4_rewardtop7_m160`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.2652 | 72.2820 | 3.0167 |
| slope_change_pct_mean | -1.2778 | -1.2484 | 0.0294 |
| cont_change_mean | 0.0193 | 0.0201 | 0.0009 |
| baimu_area_change_ha_mean | -226.1877 | -202.5699 | 23.6177 |
| mean_select_time_sec | 0.0289 | 0.0284 | -0.0005 |
| mean_score_time_sec | 0.0023 | 0.0025 | 0.0002 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0011 |
| 1 | 16.5241 | 0.1047 | 0.0028 | 108.3805 | -0.0012 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0015 |
| 3 | -1.4405 | 0.0423 | 0.0014 | 9.7082 | 0.0001 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0009 |
