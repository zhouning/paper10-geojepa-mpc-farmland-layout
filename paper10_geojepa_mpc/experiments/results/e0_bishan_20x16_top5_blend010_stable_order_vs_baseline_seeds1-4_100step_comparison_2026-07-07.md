# Multiseed rollout comparison

Baseline: `blend_w0p10_independent_seeds1-4_100step`
Candidate: `blend_w0p10_stable_order_seeds1-4_100step`

| metric | baseline | candidate | delta |
|---|---:|---:|---:|
| total_reward_mean | 69.9098 | 60.1430 | -9.7668 |
| slope_change_pct_mean | -1.2420 | -1.2241 | 0.0178 |
| cont_change_mean | 0.0185 | 0.0218 | 0.0033 |
| baimu_area_change_ha_mean | -207.8877 | -187.3337 | 20.5540 |
| mean_select_time_sec | 2.3942 | 0.0344 | -2.3598 |
| mean_score_time_sec | 0.6651 | 0.0071 | -0.6581 |

| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |
|---:|---:|---:|---:|---:|---:|
| 1 | -2.8124 | -0.0055 | 0.0050 | 29.4272 | -2.2808 |
| 2 | -12.2444 | 0.0249 | 0.0060 | 51.7445 | -2.2614 |
| 3 | -10.1717 | -0.0012 | 0.0037 | 19.9817 | -2.4291 |
| 4 | -13.8387 | 0.0530 | -0.0017 | -18.9374 | -2.4677 |
