# Value-label monitor

Decision: `stop`
Top-k: `4`
Minimum states: `10`

## Metrics

| metric | value |
|---|---:|
| n_states | 20.0000 |
| one_step_topk_regret | 2.4626 |
| one_step_topk_overlap | 0.5500 |
| one_step_top1_disagreement | 0.7500 |
| candidate_topk_regret | 0.4680 |
| candidate_topk_overlap | 0.4875 |
| candidate_top1_disagreement | 1.0000 |
| candidate_pearson_flat | 0.3170 |

## Reasons

- candidate top-k regret 0.4680 exceeds max 0.2500.
- candidate top-k overlap 0.4875 is below min 0.5000.
