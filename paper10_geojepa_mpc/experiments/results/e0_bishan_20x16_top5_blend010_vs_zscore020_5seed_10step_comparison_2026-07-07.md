# Multiseed rollout comparison

Baseline: `zscore_blend_w0p20_10step`
Candidate: `blend_w0p10_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 8.8671 | 14.1054 | 5.2383 |
| slope_change_pct_mean | -0.2036 | -0.1989 | 0.0046 |
| cont_change_mean | 0.0014 | 0.0017 | 0.0003 |
| baimu_area_change_ha_mean | -47.6782 | -42.4589 | 5.2193 |
| mean_select_time_sec | 0.0273 | 0.0328 | 0.0055 |
| mean_score_time_sec | 0.0058 | 0.0063 | 0.0005 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.4706 | -0.0739 | 0.0003 | -21.0408 | -0.0081 |
| 1 | 4.4951 | 0.0091 | 0.0001 | -2.1602 | 0.0080 |
| 2 | 4.2801 | 0.0555 | 0.0012 | 18.3030 | 0.0095 |
| 3 | 5.2930 | 0.0474 | 0.0005 | 29.1591 | 0.0051 |
| 4 | 10.6529 | -0.0149 | -0.0007 | 1.8357 | 0.0131 |
