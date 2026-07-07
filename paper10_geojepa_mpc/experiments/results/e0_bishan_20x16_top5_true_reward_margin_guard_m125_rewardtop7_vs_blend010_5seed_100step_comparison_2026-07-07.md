# Multiseed rollout comparison

Baseline: `blend010_baseline`
Candidate: `rewardtop7_m125`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 72.2180 | 2.7475 |
| slope_change_pct_mean | -1.2507 | -1.2631 | -0.0124 |
| cont_change_mean | 0.0192 | 0.0196 | 0.0004 |
| baimu_area_change_ha_mean | -207.2639 | -214.5749 | -7.3110 |
| mean_select_time_sec | 2.4238 | 0.0293 | -2.3945 |
| mean_score_time_sec | 0.6817 | 0.0027 | -0.6790 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.7297 | -0.0174 | -0.0001 | 12.0393 | -2.5153 |
| 1 | -0.6291 | -0.0082 | 0.0008 | -14.7649 | -2.2792 |
| 2 | 5.1756 | -0.0395 | -0.0001 | -21.9883 | -2.2695 |
| 3 | 1.9353 | -0.0283 | 0.0053 | -2.1564 | -2.4327 |
| 4 | 5.5258 | 0.0312 | -0.0042 | -9.6847 | -2.4758 |
