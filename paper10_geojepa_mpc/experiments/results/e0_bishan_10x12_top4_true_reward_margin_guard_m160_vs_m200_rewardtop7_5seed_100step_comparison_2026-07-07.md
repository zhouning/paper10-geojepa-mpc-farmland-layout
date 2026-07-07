# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m200`
Candidate: `10x12_top4_rewardtop7_m160`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 72.1585 | 72.2820 | 0.1235 |
| slope_change_pct_mean | -1.2622 | -1.2484 | 0.0138 |
| cont_change_mean | 0.0188 | 0.0201 | 0.0014 |
| baimu_area_change_ha_mean | -208.0559 | -202.5699 | 5.4859 |
| mean_select_time_sec | 0.0259 | 0.0284 | 0.0025 |
| mean_score_time_sec | 0.0023 | 0.0025 | 0.0002 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 6.1618 | -0.0476 | -0.0011 | -13.4573 | 0.0023 |
| 1 | -3.9456 | 0.0246 | 0.0029 | 46.7190 | -0.0010 |
| 2 | -3.1304 | 0.0260 | 0.0040 | 2.9036 | 0.0033 |
| 3 | -7.1441 | -0.0167 | 0.0002 | -25.6949 | 0.0045 |
| 4 | 8.6757 | 0.0825 | 0.0011 | 16.9591 | 0.0033 |
