# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_100step`
Candidate: `blend_w0p10_margin_true_reward_guard_m100_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 71.8745 | 2.4040 |
| slope_change_pct_mean | -1.2507 | -1.2888 | -0.0381 |
| cont_change_mean | 0.0192 | 0.0200 | 0.0007 |
| baimu_area_change_ha_mean | -207.2639 | -206.4647 | 0.7993 |
| mean_select_time_sec | 2.4238 | 0.0276 | -2.3962 |
| mean_score_time_sec | 0.6817 | 0.0022 | -0.6795 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 1.9400 | -0.0009 | -0.0025 | 19.9400 | -2.5164 |
| 1 | -3.8901 | -0.0480 | 0.0016 | -0.0033 | -2.2841 |
| 2 | 9.2646 | -0.1102 | 0.0025 | -3.2972 | -2.2695 |
| 3 | 2.4374 | -0.0442 | 0.0042 | -0.4254 | -2.4323 |
| 4 | 2.2681 | 0.0128 | -0.0022 | -12.2177 | -2.4786 |
