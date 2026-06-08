# Value-label monitor

Decision: `stop`
Top-k: `3`
Minimum states: `10`

## Metrics

| metric | value |
|---|---:|
| n_states | 20.0000 |
| one_step_topk_regret | 2.6006 |
| one_step_topk_overlap | 0.5000 |
| one_step_top1_disagreement | 0.7500 |
| candidate_topk_regret | 0.6507 |
| candidate_topk_overlap | 0.3667 |
| candidate_top1_disagreement | 1.0000 |
| candidate_pearson_flat | 0.3170 |

## Reasons

- candidate top-k regret 0.6507 exceeds max 0.2500.
- candidate top-k overlap 0.3667 is below min 0.5000.
