# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_100step`
Candidate: `blend_w0p10_margin_guard_m100_audit7x7_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 74.1137 | 4.6431 |
| slope_change_pct_mean | -1.2507 | -1.2759 | -0.0252 |
| cont_change_mean | 0.0192 | 0.0207 | 0.0015 |
| baimu_area_change_ha_mean | -207.2639 | -205.5800 | 1.6839 |
| mean_select_time_sec | 2.4238 | 0.0855 | -2.3383 |
| mean_score_time_sec | 0.6817 | 0.0146 | -0.6671 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -0.0827 | -0.0228 | -0.0020 | -19.6743 | -2.5092 |
| 1 | 6.2767 | -0.0302 | 0.0033 | 2.6703 | -2.2849 |
| 2 | 6.6293 | -0.0628 | 0.0029 | 6.5056 | -2.2643 |
| 3 | 2.7359 | -0.0462 | 0.0042 | 13.1592 | -2.3903 |
| 4 | 7.6562 | 0.0360 | -0.0011 | 5.7587 | -2.2426 |
