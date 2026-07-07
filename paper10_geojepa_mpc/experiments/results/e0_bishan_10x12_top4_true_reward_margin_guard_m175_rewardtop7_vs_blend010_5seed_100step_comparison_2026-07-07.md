# Multiseed rollout comparison

Baseline: `10x12_top4_blend010_baseline`
Candidate: `10x12_top4_rewardtop7_m175`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 65.2566 | 70.1005 | 4.8439 |
| slope_change_pct_mean | -1.2923 | -1.2444 | 0.0478 |
| cont_change_mean | 0.0198 | 0.0199 | 0.0001 |
| baimu_area_change_ha_mean | -231.3513 | -199.7872 | 31.5640 |
| mean_select_time_sec | 2.5709 | 0.0305 | -2.5405 |
| mean_score_time_sec | 0.7330 | 0.0024 | -0.7306 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | -4.0277 | 0.1198 | 0.0038 | 82.5950 | -2.3984 |
| 1 | 1.8882 | -0.0377 | 0.0015 | 18.9224 | -2.5722 |
| 2 | 14.5352 | 0.1064 | -0.0015 | 47.1889 | -2.8220 |
| 3 | 8.6658 | 0.0030 | -0.0002 | -13.0755 | -2.6763 |
| 4 | 3.1579 | 0.0475 | -0.0032 | 22.1895 | -2.2334 |
