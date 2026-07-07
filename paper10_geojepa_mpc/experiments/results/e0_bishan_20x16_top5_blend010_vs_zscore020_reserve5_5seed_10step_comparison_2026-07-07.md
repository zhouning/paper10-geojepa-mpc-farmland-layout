# Multiseed rollout comparison

Baseline: `zscore_blend_w0p20_reserve5_10step`
Candidate: `blend_w0p10_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 10.8361 | 14.1054 | 3.2693 |
| slope_change_pct_mean | -0.2087 | -0.1989 | 0.0097 |
| cont_change_mean | 0.0021 | 0.0017 | -0.0004 |
| baimu_area_change_ha_mean | -38.0557 | -42.4589 | -4.4032 |
| mean_select_time_sec | 0.0370 | 0.0328 | -0.0043 |
| mean_score_time_sec | 0.0068 | 0.0063 | -0.0005 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.8669 | 0.0324 | -0.0017 | -8.1945 | -0.0095 |
| 1 | 4.1043 | -0.0333 | -0.0016 | -29.1555 | -0.0024 |
| 2 | -6.1151 | 0.0768 | 0.0031 | 20.9703 | 0.0003 |
| 3 | 11.3612 | -0.0694 | -0.0016 | -16.3464 | -0.0085 |
| 4 | 4.1293 | 0.0421 | -0.0002 | 10.7104 | -0.0013 |
