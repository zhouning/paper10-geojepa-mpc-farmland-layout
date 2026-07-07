# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m150`
Candidate: `10x12_top4_rewardtop7_m200`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.2652 | 72.1585 | 2.8933 |
| slope_change_pct_mean | -1.2778 | -1.2622 | 0.0156 |
| cont_change_mean | 0.0193 | 0.0188 | -0.0005 |
| baimu_area_change_ha_mean | -226.1877 | -208.0559 | 18.1318 |
| mean_select_time_sec | 0.0289 | 0.0259 | -0.0030 |
| mean_score_time_sec | 0.0023 | 0.0023 | 0.0000 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -6.1618 | 0.0476 | 0.0011 | 13.4573 | -0.0012 |
| 1 | 20.4697 | 0.0801 | -0.0001 | 61.6615 | -0.0002 |
| 2 | 3.1304 | -0.0260 | -0.0040 | -2.9036 | -0.0048 |
| 3 | 5.7036 | 0.0590 | 0.0013 | 35.4030 | -0.0045 |
| 4 | -8.6757 | -0.0825 | -0.0011 | -16.9591 | -0.0043 |
