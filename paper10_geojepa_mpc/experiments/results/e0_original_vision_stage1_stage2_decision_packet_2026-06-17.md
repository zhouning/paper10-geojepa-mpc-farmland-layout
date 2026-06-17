# Paper10 Original-Vision Stage 1-2 Decision Packet

Date: 2026-06-17

## Inputs

- Stage 1 monitor matrix: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md`
- Stage 2 Dongxing audit: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`
- Design spec: `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`

## Stage 1 Summary

| decision | count |
|---|---:|
| pass | 2 |
| near_pass | 1 |
| fail | 3 |

## Stage 2 Summary

| comparison | transfer minus scratch reward | interpretation |
|---|---:|---|
| low_budget_5 | -8.7274 | scratch_higher_reward |
| low_budget_10 | -3.4588 | scratch_higher_reward |
| low_budget_20 | 4.2484 | transfer_higher_reward |
| pairwise_1000s | -2.3217 | scratch_higher_reward |
| return_20x16_h5 | -1.2664 | scratch_higher_reward |
| return_50x16_h5 | -4.1141 | scratch_higher_reward |

## Stop/Go Decision

Decision: proceed_to_stage3_confirmatory_rollouts

## Rationale

At least one predefined Stage 1 row passed the monitor gate. Stage 3 may train and roll out only the passing rows, with matched baselines.

This packet is a stop/go control document. It does not change the manuscript claim by itself.
