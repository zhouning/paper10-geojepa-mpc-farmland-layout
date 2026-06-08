# Value-label diagnostics

States: `10`
Candidates per state: `12`
Top-k: `4`

## Label variation

| metric | value |
|---|---:|
| return_mean | 1.4603 |
| return_std | 2.8768 |
| return_state_std_mean | 2.5591 |
| return_state_std_median | 2.1878 |
| one_step_reward_mean | 0.7381 |
| one_step_reward_std | 1.4727 |
| one_step_state_std_mean | 1.3302 |
| one_step_state_std_median | 1.0202 |
| residual_mean | 0.7223 |
| residual_std | 2.7038 |
| residual_abs_mean | 1.6619 |
| residual_state_std_mean | 2.2852 |
| residual_state_std_median | 2.3248 |
| residual_to_return_state_std_ratio | 0.8930 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.3699 |
| spearman_flat | 0.5505 |
| pearson_state_mean | 0.4072 |
| spearman_state_mean | 0.5853 |
| top1_disagreement_rate | 0.7000 |
| topk_overlap_fraction_mean | 0.6000 |
| one_step_top1_return_regret_mean | 3.3405 |
| topk_best_return_regret_mean | 1.2916 |
| pairwise_disagreement_rate_mean | 0.2758 |
| pairwise_comparable_fraction_mean | 1.0000 |

## Candidate score vs return

| metric | value |
|---|---:|
| pearson_flat | 0.3455 |
| spearman_flat | 0.4025 |
| pearson_state_mean | 0.4588 |
| spearman_state_mean | 0.4643 |
| top1_disagreement_rate | 1.0000 |
| topk_overlap_fraction_mean | 0.5000 |
| candidate_top1_return_regret_mean | 6.5656 |
| topk_best_return_regret_mean | 0.4923 |
| pairwise_disagreement_rate_mean | 0.3318 |
| pairwise_comparable_fraction_mean | 1.0000 |
