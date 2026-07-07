# Multiseed rollout comparison

Baseline: `blend_w0p10_independent_seeds1-4_100step`
Candidate: `blend_w0p10_common_seeds1-4_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.9098 | 56.6297 | -13.2801 |
| slope_change_pct_mean | -1.2420 | -1.2387 | 0.0032 |
| cont_change_mean | 0.0185 | 0.0184 | -0.0002 |
| baimu_area_change_ha_mean | -207.8877 | -195.6354 | 12.2523 |
| mean_select_time_sec | 2.3942 | 0.0368 | -2.3574 |
| mean_score_time_sec | 0.6651 | 0.0087 | -0.6564 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 1 | -13.5824 | -0.0309 | 0.0008 | 0.1259 | -2.2739 |
| 2 | -13.0790 | -0.0100 | 0.0008 | 21.9384 | -2.2612 |
| 3 | -13.1817 | -0.0240 | 0.0015 | 11.3436 | -2.4266 |
| 4 | -13.2774 | 0.0778 | -0.0038 | 15.6013 | -2.4680 |
