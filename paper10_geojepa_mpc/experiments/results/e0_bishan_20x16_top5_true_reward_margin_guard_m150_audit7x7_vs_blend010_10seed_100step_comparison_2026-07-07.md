# Multiseed rollout comparison

Baseline: `blend_w0p10_value_filter_selectedaudit_100step_seeds0-9`
Candidate: `blend_w0p10_margin_guard_m150_audit7x7_100step_seeds0-9`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 68.8015 | 73.0649 | 4.2634 |
| slope_change_pct_mean | -1.2517 | -1.2555 | -0.0038 |
| cont_change_mean | 0.0189 | 0.0201 | 0.0012 |
| baimu_area_change_ha_mean | -208.8650 | -212.1697 | -3.3047 |
| mean_select_time_sec | 0.0287 | 0.0296 | 0.0009 |
| mean_score_time_sec | 0.0031 | 0.0026 | -0.0005 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.5825 | 0.0075 | -0.0002 | 12.2858 | 0.0020 |
| 1 | 6.0147 | -0.0133 | 0.0025 | 3.2900 | -0.0006 |
| 2 | 3.1866 | 0.0177 | 0.0006 | -13.2184 | 0.0001 |
| 3 | 0.7158 | -0.0439 | 0.0039 | -26.5750 | -0.0001 |
| 4 | 1.7597 | 0.0441 | 0.0001 | -14.9998 | 0.0048 |
| 5 | 0.0029 | 0.0663 | 0.0056 | 57.0171 | -0.0030 |
| 6 | 0.8565 | -0.0022 | -0.0002 | 7.8931 | -0.0032 |
| 7 | 13.6481 | -0.0111 | -0.0023 | -36.6457 | -0.0060 |
| 8 | 10.8797 | -0.1117 | -0.0012 | -49.2934 | 0.0078 |
| 9 | 4.9877 | 0.0089 | 0.0035 | 27.1997 | 0.0070 |
