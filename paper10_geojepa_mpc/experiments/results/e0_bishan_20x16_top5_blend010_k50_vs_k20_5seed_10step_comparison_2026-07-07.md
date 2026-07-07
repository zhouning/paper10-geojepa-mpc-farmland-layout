# Multiseed rollout comparison

Baseline: `blend_w0p10_k20_10step`
Candidate: `blend_w0p10_k50_10step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 12.5148 | 14.1054 | 1.5906 |
| slope_change_pct_mean | -0.2531 | -0.1989 | 0.0542 |
| cont_change_mean | 0.0012 | 0.0017 | 0.0004 |
| baimu_area_change_ha_mean | -65.8026 | -42.4589 | 23.3437 |
| mean_select_time_sec | 0.0166 | 0.0328 | 0.0162 |
| mean_score_time_sec | 0.0032 | 0.0063 | 0.0031 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -1.5403 | 0.0437 | 0.0004 | 2.1031 | 0.0050 |
| 1 | -0.2198 | 0.0633 | 0.0002 | 31.5495 | 0.0185 |
| 2 | 3.6651 | 0.0736 | 0.0019 | 18.5226 | 0.0162 |
| 3 | 4.6771 | 0.0745 | 0.0004 | 35.9180 | 0.0216 |
| 4 | 1.3707 | 0.0158 | -0.0006 | 28.6255 | 0.0195 |
