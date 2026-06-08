# Value-label diagnostics

States: `5`
Candidates per state: `8`
Top-k: `3`

## Label variation

| metric | value |
|---|---:|
| return_mean | 0.6865 |
| return_std | 1.7700 |
| return_state_std_mean | 1.6276 |
| return_state_std_median | 1.8391 |
| one_step_reward_mean | 0.8003 |
| one_step_reward_std | 1.5112 |
| one_step_state_std_mean | 1.4155 |
| one_step_state_std_median | 1.1534 |
| residual_mean | -0.1138 |
| residual_std | 1.2897 |
| residual_abs_mean | 0.6685 |
| residual_state_std_mean | 1.0372 |
| residual_state_std_median | 0.9279 |
| residual_to_return_state_std_ratio | 0.6372 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.7016 |
| spearman_flat | 0.6996 |
| pearson_state_mean | 0.6168 |
| spearman_state_mean | 0.7429 |
| top1_disagreement_rate | 0.6000 |
| topk_overlap_fraction_mean | 0.7333 |
| one_step_top1_return_regret_mean | 0.9149 |
| topk_best_return_regret_mean | 0.0000 |
| pairwise_disagreement_rate_mean | 0.2000 |
| pairwise_comparable_fraction_mean | 1.0000 |

## Candidate score vs return

| metric | value |
|---|---:|
| pearson_flat | 0.5496 |
| spearman_flat | 0.5343 |
| pearson_state_mean | 0.4560 |
| spearman_state_mean | 0.4762 |
| top1_disagreement_rate | 0.8000 |
| topk_overlap_fraction_mean | 0.5333 |
| candidate_top1_return_regret_mean | 3.0140 |
| topk_best_return_regret_mean | 1.2916 |
| pairwise_disagreement_rate_mean | 0.3071 |
| pairwise_comparable_fraction_mean | 1.0000 |
