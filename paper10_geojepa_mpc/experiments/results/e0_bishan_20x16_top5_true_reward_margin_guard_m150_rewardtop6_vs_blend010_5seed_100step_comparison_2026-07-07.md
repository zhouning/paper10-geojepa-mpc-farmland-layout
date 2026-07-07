# Multiseed rollout comparison

Baseline: `blend010_baseline`
Candidate: `rewardtop6_m150`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 69.8147 | 0.3442 |
| slope_change_pct_mean | -1.2507 | -1.2580 | -0.0073 |
| cont_change_mean | 0.0192 | 0.0198 | 0.0006 |
| baimu_area_change_ha_mean | -207.2639 | -222.3667 | -15.1028 |
| mean_select_time_sec | 2.4238 | 0.0284 | -2.3954 |
| mean_score_time_sec | 0.6817 | 0.0027 | -0.6790 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -1.9391 | 0.0192 | -0.0042 | -13.6743 | -2.5140 |
| 1 | 6.1988 | -0.0422 | 0.0020 | -10.8315 | -2.2817 |
| 2 | 5.9282 | -0.0640 | 0.0017 | -31.4423 | -2.2671 |
| 3 | -10.2268 | 0.0063 | 0.0034 | -4.5659 | -2.4330 |
| 4 | 1.7597 | 0.0441 | 0.0001 | -14.9998 | -2.4813 |
