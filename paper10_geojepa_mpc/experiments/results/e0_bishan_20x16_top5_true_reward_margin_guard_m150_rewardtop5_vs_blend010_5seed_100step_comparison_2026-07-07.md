# Multiseed rollout comparison

Baseline: `blend010_baseline`
Candidate: `rewardtop5_m150`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 67.4133 | -2.0573 |
| slope_change_pct_mean | -1.2507 | -1.2441 | 0.0066 |
| cont_change_mean | 0.0192 | 0.0184 | -0.0008 |
| baimu_area_change_ha_mean | -207.2639 | -213.8448 | -6.5808 |
| mean_select_time_sec | 2.4238 | 0.0292 | -2.3946 |
| mean_score_time_sec | 0.6817 | 0.0029 | -0.6788 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.6879 | -0.0265 | -0.0028 | -48.2766 | -2.5180 |
| 1 | -3.6843 | -0.0396 | 0.0006 | 5.7432 | -2.2892 |
| 2 | 6.2453 | 0.0393 | 0.0012 | 40.8906 | -2.2688 |
| 3 | -10.2268 | 0.0063 | 0.0034 | -4.5659 | -2.4290 |
| 4 | -5.3084 | 0.0534 | -0.0064 | -26.6955 | -2.4679 |
