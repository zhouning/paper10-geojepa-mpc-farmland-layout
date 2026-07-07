# Multiseed rollout comparison

Baseline: `rewardtop7_m150`
Candidate: `rewardtop7_m125`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 71.8258 | 72.2180 | 0.3922 |
| slope_change_pct_mean | -1.2387 | -1.2631 | -0.0245 |
| cont_change_mean | 0.0208 | 0.0196 | -0.0012 |
| baimu_area_change_ha_mean | -210.7941 | -214.5749 | -3.7808 |
| mean_select_time_sec | 0.0287 | 0.0293 | 0.0006 |
| mean_score_time_sec | 0.0025 | 0.0027 | 0.0002 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.1472 | -0.0249 | 0.0001 | -0.2465 | 0.0028 |
| 1 | -6.6438 | 0.0051 | -0.0017 | -18.0549 | -0.0006 |
| 2 | 1.9891 | -0.0572 | -0.0007 | -8.7699 | 0.0001 |
| 3 | 1.7023 | -0.0324 | 0.0006 | 2.8522 | -0.0012 |
| 4 | 3.7661 | -0.0129 | -0.0042 | 5.3151 | 0.0019 |
