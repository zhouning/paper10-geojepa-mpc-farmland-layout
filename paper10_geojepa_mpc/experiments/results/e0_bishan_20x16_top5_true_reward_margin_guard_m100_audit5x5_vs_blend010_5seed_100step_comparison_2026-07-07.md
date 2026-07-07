# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_100step`
Candidate: `blend_w0p10_margin_guard_m100_audit5x5_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.4705 | 72.9160 | 3.4455 |
| slope_change_pct_mean | -1.2507 | -1.2834 | -0.0327 |
| cont_change_mean | 0.0192 | 0.0211 | 0.0018 |
| baimu_area_change_ha_mean | -207.2639 | -203.2705 | 3.9934 |
| mean_select_time_sec | 2.4238 | 0.0294 | -2.3944 |
| mean_score_time_sec | 0.6817 | 0.0029 | -0.6788 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 4.9785 | 0.0271 | -0.0002 | 17.1244 | -2.5093 |
| 1 | 6.2296 | -0.0915 | 0.0027 | -35.7710 | -2.2868 |
| 2 | 10.1166 | -0.1096 | 0.0045 | 1.5300 | -2.2715 |
| 3 | -6.7481 | -0.0498 | 0.0024 | 10.2311 | -2.4282 |
| 4 | 2.6508 | 0.0603 | -0.0003 | 26.8527 | -2.4764 |
