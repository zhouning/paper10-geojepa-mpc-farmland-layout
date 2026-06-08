# Value-label diagnostics

States: `8`
Candidates per state: `12`
Top-k: `5`

## Label variation

| metric | value |
|---|---:|
| return_mean | 0.8895 |
| return_std | 1.7671 |
| return_state_std_mean | 1.6667 |
| return_state_std_median | 1.6050 |
| one_step_reward_mean | 0.7660 |
| one_step_reward_std | 1.1549 |
| one_step_state_std_mean | 1.1318 |
| one_step_state_std_median | 1.0465 |
| residual_mean | 0.1236 |
| residual_std | 1.5719 |
| residual_abs_mean | 0.7657 |
| residual_state_std_mean | 1.2004 |
| residual_state_std_median | 0.8950 |
| residual_to_return_state_std_ratio | 0.7203 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.4865 |
| spearman_flat | 0.6690 |
| pearson_state_mean | 0.5990 |
| spearman_state_mean | 0.6879 |
| top1_disagreement_rate | 0.5000 |
| topk_overlap_fraction_mean | 0.7750 |
| one_step_top1_return_regret_mean | 1.6023 |
| topk_best_return_regret_mean | 0.0000 |
| pairwise_disagreement_rate_mean | 0.2045 |
| pairwise_comparable_fraction_mean | 1.0000 |

## Candidate score vs return

| metric | value |
|---|---:|
| pearson_flat | 0.4135 |
| spearman_flat | 0.5546 |
| pearson_state_mean | 0.5248 |
| spearman_state_mean | 0.5970 |
| top1_disagreement_rate | 1.0000 |
| topk_overlap_fraction_mean | 0.7250 |
| candidate_top1_return_regret_mean | 3.0167 |
| topk_best_return_regret_mean | 0.0000 |
| pairwise_disagreement_rate_mean | 0.2595 |
| pairwise_comparable_fraction_mean | 1.0000 |
