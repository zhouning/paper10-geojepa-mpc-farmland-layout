# Multiseed rollout comparison

Baseline: `zscore_blend_w0p20_10step`
Candidate: `zscore_blend_w0p20_reserve5_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 8.8671 | 10.8361 | 1.9690 |
| slope_change_pct_mean | -0.2036 | -0.2087 | -0.0051 |
| cont_change_mean | 0.0014 | 0.0021 | 0.0007 |
| baimu_area_change_ha_mean | -47.6782 | -38.0557 | 9.6225 |
| mean_select_time_sec | 0.0273 | 0.0370 | 0.0098 |
| mean_score_time_sec | 0.0058 | 0.0068 | 0.0010 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -1.3963 | -0.1063 | 0.0020 | -12.8463 | 0.0013 |
| 1 | 0.3908 | 0.0424 | 0.0017 | 26.9953 | 0.0104 |
| 2 | 10.3951 | -0.0213 | -0.0019 | -2.6672 | 0.0091 |
| 3 | -6.0682 | 0.1168 | 0.0021 | 45.5054 | 0.0136 |
| 4 | 6.5236 | -0.0571 | -0.0005 | -8.8747 | 0.0144 |
