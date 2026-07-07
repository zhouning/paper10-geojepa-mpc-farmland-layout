# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m150`
Candidate: `10x12_top4_rewardtop7_m175`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.2652 | 70.1005 | 0.8353 |
| slope_change_pct_mean | -1.2778 | -1.2444 | 0.0334 |
| cont_change_mean | 0.0193 | 0.0199 | 0.0006 |
| baimu_area_change_ha_mean | -226.1877 | -199.7872 | 26.4005 |
| mean_select_time_sec | 0.0289 | 0.0305 | 0.0016 |
| mean_score_time_sec | 0.0023 | 0.0024 | 0.0001 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -6.1618 | 0.0476 | 0.0011 | 13.4573 | -0.0005 |
| 1 | 15.6450 | 0.1475 | 0.0058 | 108.7800 | -0.0011 |
| 2 | 0.6320 | -0.0189 | -0.0033 | 5.9560 | -0.0006 |
| 3 | 3.5329 | 0.0100 | 0.0011 | -7.7864 | 0.0019 |
| 4 | -9.4718 | -0.0194 | -0.0018 | 11.5954 | 0.0083 |
