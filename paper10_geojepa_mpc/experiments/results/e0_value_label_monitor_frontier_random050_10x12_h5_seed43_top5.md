# Value-label monitor

Decision: `stop`
Top-k: `5`
Minimum states: `10`

## Metrics

| metric | value |
|---|---:|
| n_states | 10.0000 |
| one_step_topk_regret | 0.0000 |
| one_step_topk_overlap | 0.7800 |
| one_step_top1_disagreement | 0.7000 |
| candidate_topk_regret | 0.1023 |
| candidate_topk_overlap | 0.6400 |
| candidate_top1_disagreement | 1.0000 |
| candidate_pearson_flat | 0.3455 |

## Reasons

- one-step top-k regret 0.0000 is below min 0.5000; multi-step labels may not add enough filtering signal.
