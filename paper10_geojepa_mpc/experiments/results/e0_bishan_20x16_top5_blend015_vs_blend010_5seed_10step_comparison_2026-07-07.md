# Multiseed rollout comparison

Baseline: `blend_w0p10_10step`
Candidate: `blend_w0p15_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 14.1054 | 9.2518 | -4.8536 |
| slope_change_pct_mean | -0.1989 | -0.1954 | 0.0036 |
| cont_change_mean | 0.0017 | 0.0021 | 0.0004 |
| baimu_area_change_ha_mean | -42.4589 | -37.2325 | 5.2264 |
| mean_select_time_sec | 0.0328 | 0.0269 | -0.0059 |
| mean_score_time_sec | 0.0063 | 0.0060 | -0.0003 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -1.2255 | 0.0042 | -0.0016 | -11.4186 | -0.0025 |
| 1 | -4.7745 | 0.0674 | 0.0023 | 45.8322 | -0.0115 |
| 2 | 1.1952 | -0.0314 | -0.0011 | 1.2405 | -0.0075 |
| 3 | -10.2655 | -0.0274 | 0.0000 | -18.7244 | -0.0000 |
| 4 | -9.1977 | 0.0050 | 0.0024 | 9.2023 | -0.0078 |
