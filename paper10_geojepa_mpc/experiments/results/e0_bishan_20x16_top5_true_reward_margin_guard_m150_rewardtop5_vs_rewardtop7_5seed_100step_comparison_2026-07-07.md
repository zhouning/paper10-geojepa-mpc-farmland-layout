# Multiseed rollout comparison

Baseline: `rewardtop7_m150`
Candidate: `rewardtop5_m150`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 71.8258 | 67.4133 | -4.4125 |
| slope_change_pct_mean | -1.2387 | -1.2441 | -0.0055 |
| cont_change_mean | 0.0208 | 0.0184 | -0.0023 |
| baimu_area_change_ha_mean | -210.7941 | -213.8448 | -3.0506 |
| mean_select_time_sec | 0.0287 | 0.0292 | 0.0006 |
| mean_score_time_sec | 0.0025 | 0.0029 | 0.0004 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.1054 | -0.0340 | -0.0026 | -60.5625 | 0.0001 |
| 1 | -9.6990 | -0.0263 | -0.0019 | 2.4533 | -0.0106 |
| 2 | 3.0588 | 0.0216 | 0.0006 | 54.1090 | 0.0008 |
| 3 | -10.4598 | 0.0022 | -0.0013 | 0.4428 | 0.0026 |
| 4 | -7.0681 | 0.0093 | -0.0064 | -11.6957 | 0.0099 |
