# Value-label monitor

Decision: `stop`
Top-k: `5`
Minimum states: `8`

## Metrics

| metric | value |
|---|---:|
| n_states | 8.0000 |
| one_step_topk_regret | 0.0000 |
| one_step_topk_overlap | 0.7750 |
| one_step_top1_disagreement | 0.5000 |
| candidate_topk_regret | 0.0000 |
| candidate_topk_overlap | 0.7250 |
| candidate_top1_disagreement | 1.0000 |
| candidate_pearson_flat | 0.4135 |

## Reasons

- one-step top-k regret 0.0000 is below min 0.2500; multi-step labels may not add enough filtering signal.
