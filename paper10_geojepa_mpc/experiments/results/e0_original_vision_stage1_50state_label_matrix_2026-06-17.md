# Paper10 Original-Vision Stage 1 Monitor Matrix

Source summary: `D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation_summary.json`

## Decision Counts

| decision | count |
|---|---:|
| pass | 2 |
| near_pass | 1 |
| fail | 3 |

## Rows

| run | decision | selected top-k | near-pass top-k | best candidate regret | best candidate overlap | best one-step regret |
|---|---|---:|---|---:|---:|---:|
| frontier_random050_50x16_h5_seed47_f050 | fail | none | none | 0.0711 | 0.8050 | 2.7526 |
| frontier_random050_50x16_h5_seed48_f050 | pass | 6 | 5,8 | 0.0080 | 0.8067 | 2.5515 |
| frontier_random050_50x20_h5_seed47_f050 | fail | none | none | 0.0828 | 0.7333 | 2.8793 |
| frontier_random050_50x20_h5_seed48_f050 | fail | none | none | 0.0371 | 0.7517 | 2.1546 |
| frontier_random050_50x24_h5_seed47_f075 | pass | 12 | 10 | 0.0979 | 0.6467 | 2.6213 |
| frontier_random050_50x24_h5_seed48_f075 | near_pass | none | 12 | 0.2836 | 0.6567 | 3.5270 |

## Interpretation Lock

A `pass` row authorizes matched training and rollout follow-up. A `near_pass` row authorizes diagnostic follow-up only. A `fail` row is evidence for that predefined row, not a general rejection of the original Paper10 vision.
A row-level pass is specific to the selected top-k; follow-up training or rollout must use selected_top_k and inspect full JSON diagnostics for other top-k outcomes.
