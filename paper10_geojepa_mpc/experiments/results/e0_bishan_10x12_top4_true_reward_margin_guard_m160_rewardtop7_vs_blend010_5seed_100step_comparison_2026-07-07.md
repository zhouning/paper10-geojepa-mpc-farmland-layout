# Multiseed rollout comparison

Baseline: `10x12_top4_blend010_baseline`
Candidate: `10x12_top4_rewardtop7_m160`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 65.2566 | 72.2820 | 7.0253 |
| slope_change_pct_mean | -1.2923 | -1.2484 | 0.0439 |
| cont_change_mean | 0.0198 | 0.0201 | 0.0003 |
| baimu_area_change_ha_mean | -231.3513 | -202.5699 | 28.7813 |
| mean_select_time_sec | 2.5709 | 0.0284 | -2.5426 |
| mean_score_time_sec | 0.7330 | 0.0025 | -0.7305 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 2.1341 | 0.0722 | 0.0027 | 69.1377 | -2.3968 |
| 1 | 2.7673 | -0.0805 | -0.0015 | 18.5229 | -2.5724 |
| 2 | 13.9032 | 0.1254 | 0.0018 | 41.2328 | -2.8230 |
| 3 | 3.6924 | 0.0353 | 0.0002 | 4.4191 | -2.6782 |
| 4 | 12.6297 | 0.0670 | -0.0014 | 10.5940 | -2.2426 |
