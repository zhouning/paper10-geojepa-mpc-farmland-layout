# Multiseed rollout comparison

Baseline: `blend_w0p10_independent_10step`
Candidate: `blend_w0p10_common_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 14.1054 | 17.7772 | 3.6718 |
| slope_change_pct_mean | -0.1989 | -0.3074 | -0.1085 |
| cont_change_mean | 0.0017 | 0.0013 | -0.0004 |
| baimu_area_change_ha_mean | -42.4589 | -64.6935 | -22.2346 |
| mean_select_time_sec | 0.0328 | 0.0302 | -0.0026 |
| mean_score_time_sec | 0.0063 | 0.0052 | -0.0011 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 8.0708 | -0.1324 | -0.0005 | -29.6586 | 0.0064 |
| 1 | 1.4632 | -0.0371 | 0.0003 | -0.8525 | -0.0015 |
| 2 | 3.0355 | -0.1283 | -0.0017 | -25.5249 | 0.0005 |
| 3 | 2.2551 | -0.0693 | 0.0000 | -7.1039 | -0.0097 |
| 4 | 3.5345 | -0.1756 | 0.0000 | -48.0333 | -0.0086 |
