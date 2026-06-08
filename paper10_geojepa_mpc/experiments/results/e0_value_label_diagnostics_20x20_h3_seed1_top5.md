# Value-label diagnostics

States: `20`
Candidates per state: `20`
Top-k: `5`

## Label variation

| metric | value |
|---|---:|
| return_mean | 0.3277 |
| return_std | 2.1986 |
| return_state_std_mean | 1.4195 |
| return_state_std_median | 1.2045 |
| one_step_reward_mean | 0.3347 |
| one_step_reward_std | 1.4892 |
| one_step_state_std_mean | 0.5250 |
| one_step_state_std_median | 0.3590 |
| residual_mean | -0.0070 |
| residual_std | 1.6914 |
| residual_abs_mean | 0.7129 |
| residual_state_std_mean | 1.3276 |
| residual_state_std_median | 1.0927 |
| residual_to_return_state_std_ratio | 0.9353 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.6399 |
| spearman_flat | 0.4974 |
| pearson_state_mean | 0.3567 |
| spearman_state_mean | 0.4383 |
| top1_disagreement_rate | 0.8000 |
| topk_overlap_fraction_mean | 0.5600 |
| one_step_top1_return_regret_mean | 1.0642 |
| topk_best_return_regret_mean | 0.4706 |
| pairwise_disagreement_rate_mean | 0.3358 |
| pairwise_comparable_fraction_mean | 1.0000 |
