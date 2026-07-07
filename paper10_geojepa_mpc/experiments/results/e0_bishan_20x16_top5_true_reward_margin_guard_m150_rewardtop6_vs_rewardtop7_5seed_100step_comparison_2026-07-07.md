# Multiseed rollout comparison

Baseline: `rewardtop7_m150`
Candidate: `rewardtop6_m150`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 71.8258 | 69.8147 | -2.0111 |
| slope_change_pct_mean | -1.2387 | -1.2580 | -0.0194 |
| cont_change_mean | 0.0208 | 0.0198 | -0.0010 |
| baimu_area_change_ha_mean | -210.7941 | -222.3667 | -11.5725 |
| mean_select_time_sec | 0.0287 | 0.0284 | -0.0003 |
| mean_score_time_sec | 0.0025 | 0.0027 | 0.0002 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -2.5215 | 0.0117 | -0.0041 | -25.9601 | 0.0041 |
| 1 | 0.1841 | -0.0289 | -0.0005 | -14.1214 | -0.0031 |
| 2 | 2.7417 | -0.0817 | 0.0011 | -18.2240 | 0.0025 |
| 3 | -10.4598 | 0.0022 | -0.0013 | 0.4428 | -0.0014 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | -0.0035 |
