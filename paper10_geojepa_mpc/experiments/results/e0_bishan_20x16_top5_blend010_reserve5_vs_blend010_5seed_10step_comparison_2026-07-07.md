# Multiseed rollout comparison

Baseline: `blend_w0p10_10step`
Candidate: `blend_w0p10_reserve5_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 14.1054 | 10.1548 | -3.9506 |
| slope_change_pct_mean | -0.1989 | -0.1894 | 0.0096 |
| cont_change_mean | 0.0017 | 0.0013 | -0.0003 |
| baimu_area_change_ha_mean | -42.4589 | -35.5687 | 6.8901 |
| mean_select_time_sec | 0.0328 | 0.0431 | 0.0103 |
| mean_score_time_sec | 0.0063 | 0.0088 | 0.0025 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.1172 | -0.0624 | -0.0016 | -15.9404 | 0.0208 |
| 1 | -7.4207 | 0.0629 | -0.0002 | 2.6609 | 0.0131 |
| 2 | -4.3328 | 0.0101 | -0.0010 | 16.6874 | 0.0071 |
| 3 | -4.1017 | 0.0629 | 0.0001 | 47.4824 | 0.0094 |
| 4 | -5.0149 | -0.0257 | 0.0011 | -16.4396 | 0.0010 |
