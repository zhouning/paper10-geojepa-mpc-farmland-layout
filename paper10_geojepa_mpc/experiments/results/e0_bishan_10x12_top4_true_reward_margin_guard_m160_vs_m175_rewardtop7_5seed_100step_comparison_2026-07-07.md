# Multiseed rollout comparison

Baseline: `10x12_top4_rewardtop7_m175`
Candidate: `10x12_top4_rewardtop7_m160`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 70.1005 | 72.2820 | 2.1815 |
| slope_change_pct_mean | -1.2444 | -1.2484 | -0.0040 |
| cont_change_mean | 0.0199 | 0.0201 | 0.0003 |
| baimu_area_change_ha_mean | -199.7872 | -202.5699 | -2.7827 |
| mean_select_time_sec | 0.0305 | 0.0284 | -0.0021 |
| mean_score_time_sec | 0.0024 | 0.0025 | 0.0001 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 0 | 6.1618 | -0.0476 | -0.0011 | -13.4573 | 0.0016 |
| 1 | 0.8791 | -0.0428 | -0.0030 | -0.3995 | -0.0001 |
| 2 | -0.6320 | 0.0189 | 0.0033 | -5.9560 | -0.0009 |
| 3 | -4.9734 | 0.0323 | 0.0004 | 17.4946 | -0.0019 |
| 4 | 9.4718 | 0.0194 | 0.0018 | -11.5954 | -0.0092 |
