# Value-label diagnostics

States: `20`
Candidates per state: `16`
Top-k: `5`

## Label variation

| metric | value |
|---|---:|
| return_mean | 1.4419 |
| return_std | 4.1646 |
| return_state_std_mean | 3.0226 |
| return_state_std_median | 2.5590 |
| one_step_reward_mean | 0.9854 |
| one_step_reward_std | 2.9745 |
| one_step_state_std_mean | 1.6783 |
| one_step_state_std_median | 1.1934 |
| residual_mean | 0.4566 |
| residual_std | 3.4724 |
| residual_abs_mean | 1.8903 |
| residual_state_std_mean | 2.8046 |
| residual_state_std_median | 2.2330 |
| residual_to_return_state_std_ratio | 0.9279 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.5705 |
| spearman_flat | 0.4975 |
| pearson_state_mean | 0.4126 |
| spearman_state_mean | 0.4996 |
| top1_disagreement_rate | 0.7500 |
| topk_overlap_fraction_mean | 0.5600 |
| one_step_top1_return_regret_mean | 3.0059 |
| topk_best_return_regret_mean | 2.4626 |
| pairwise_disagreement_rate_mean | 0.3133 |
| pairwise_comparable_fraction_mean | 1.0000 |

## Candidate score vs return

| metric | value |
|---|---:|
| pearson_flat | 0.3170 |
| spearman_flat | 0.3599 |
| pearson_state_mean | 0.4046 |
| spearman_state_mean | 0.4790 |
| top1_disagreement_rate | 1.0000 |
| topk_overlap_fraction_mean | 0.6300 |
| candidate_top1_return_regret_mean | 5.9676 |
| topk_best_return_regret_mean | 0.1877 |
| pairwise_disagreement_rate_mean | 0.3129 |
| pairwise_comparable_fraction_mean | 1.0000 |
