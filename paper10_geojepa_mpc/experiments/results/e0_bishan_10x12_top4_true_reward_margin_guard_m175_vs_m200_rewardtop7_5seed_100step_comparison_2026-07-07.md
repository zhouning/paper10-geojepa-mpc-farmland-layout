# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m200`
Candidate: `10x12_top4_rewardtop7_m175`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 72.1585 | 70.1005 | -2.0580 |
| slope_change_pct_mean | -1.2622 | -1.2444 | 0.0177 |
| cont_change_mean | 0.0188 | 0.0199 | 0.0011 |
| baimu_area_change_ha_mean | -208.0559 | -199.7872 | 8.2687 |
| mean_select_time_sec | 0.0259 | 0.0305 | 0.0046 |
| mean_score_time_sec | 0.0023 | 0.0024 | 0.0001 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0007 |
| 1 | -4.8247 | 0.0674 | 0.0059 | 47.1185 | -0.0009 |
| 2 | -2.4985 | 0.0071 | 0.0007 | 8.8596 | 0.0042 |
| 3 | -2.1707 | -0.0490 | -0.0002 | -43.1894 | 0.0064 |
| 4 | -0.7961 | 0.0631 | -0.0007 | 28.5546 | 0.0125 |
