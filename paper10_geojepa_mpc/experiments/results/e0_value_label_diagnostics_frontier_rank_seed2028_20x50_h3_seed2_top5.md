# Value-label diagnostics

States: `20`
Candidates per state: `50`
Top-k: `5`

## Label variation

| metric | value |
|---|---:|
| return_mean | 0.7861 |
| return_std | 2.3252 |
| return_state_std_mean | 1.6725 |
| return_state_std_median | 1.6226 |
| one_step_reward_mean | 0.7323 |
| one_step_reward_std | 1.1285 |
| one_step_state_std_mean | 0.6601 |
| one_step_state_std_median | 0.4093 |
| residual_mean | 0.0537 |
| residual_std | 2.0930 |
| residual_abs_mean | 1.1444 |
| residual_state_std_mean | 1.4479 |
| residual_state_std_median | 1.4750 |
| residual_to_return_state_std_ratio | 0.8657 |

## One-step reward vs return

| metric | value |
|---|---:|
| pearson_flat | 0.4381 |
| spearman_flat | 0.4065 |
| pearson_state_mean | 0.2489 |
| spearman_state_mean | 0.4258 |
| top1_disagreement_rate | 0.7000 |
| topk_overlap_fraction_mean | 0.4400 |
| one_step_top1_return_regret_mean | 2.4966 |
| topk_best_return_regret_mean | 1.6319 |
| pairwise_disagreement_rate_mean | 0.3304 |
| pairwise_comparable_fraction_mean | 1.0000 |

## Candidate score vs return

| metric | value |
|---|---:|
| pearson_flat | 0.0556 |
| spearman_flat | 0.0467 |
| pearson_state_mean | 0.1293 |
| spearman_state_mean | 0.1272 |
| top1_disagreement_rate | 0.9000 |
| topk_overlap_fraction_mean | 0.1900 |
| candidate_top1_return_regret_mean | 3.8031 |
| topk_best_return_regret_mean | 0.9834 |
| pairwise_disagreement_rate_mean | 0.4550 |
| pairwise_comparable_fraction_mean | 1.0000 |
