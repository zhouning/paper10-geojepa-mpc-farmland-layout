# Paper10 Original-Vision Stage 2 Dongxing Transfer Audit

This audit compares matched transfer and scratch rows from existing Dongxing summaries. It does not create a positive transfer claim.

| comparison | transfer reward | scratch reward | transfer minus scratch | interpretation |
|---|---:|---:|---:|---|
| low_budget_5 | 41.6380 | 50.3654 | -8.7274 | scratch_higher_reward |
| low_budget_10 | 44.3382 | 47.7970 | -3.4588 | scratch_higher_reward |
| low_budget_20 | 44.7080 | 40.4596 | 4.2484 | transfer_higher_reward |
| pairwise_1000s | 37.8894 | 40.2111 | -2.3217 | scratch_higher_reward |
| return_20x16_h5 | 41.7733 | 43.0397 | -1.2664 | scratch_higher_reward |
| return_50x16_h5 | 51.6183 | 55.7324 | -4.1141 | scratch_higher_reward |

## Claim Boundary

Rows where transfer is higher identify conditional regimes for follow-up. Rows where scratch is higher remain direct evidence against a broad transfer-win claim.
