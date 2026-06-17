# Paper10 Original-Vision Validation Handoff

Date: 2026-06-18

Branch: `paper10-original-vision-validation`

Current save point before handoff note:
`d4403f5c5d43bf651cf5763f284c3564965e3d2b`
(`docs: add original vision stage3 rollout plan`)

## Completed Work

- Stage 0 registry added and guarded by preflight.
- Stage 1 Windows label-only matrix completed with `TrainOnPass=0`.
- Stage 2 Dongxing transfer audit generated from existing matched summaries.
- Stage 1-2 stop/go decision packet generated.
- Stage 3 Colab rollout implementation plan written but not executed.

## Key Evidence Files

- `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.json`
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md`
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv`
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md`
- `docs/superpowers/plans/2026-06-18-paper10-stage3-confirmatory-rollout-plan.md`

## Stage 1 Result

The Stage 1 monitor matrix used top-k `5, 6, 8, 10, 12` and produced:

| decision | count |
|---|---:|
| pass | 2 |
| near_pass | 1 |
| fail | 3 |

Authorized Stage 3 Bishan rows:

- frozen anchor: `frontier_random050_20x16_h5_seed44_f050`, top-k `5`;
- confirmatory pass: `frontier_random050_50x16_h5_seed48_f050`, top-k `6`;
- confirmatory pass: `frontier_random050_50x24_h5_seed47_f075`, top-k `12`;
- diagnostic near-pass: `frontier_random050_50x24_h5_seed48_f075`, top-k `12`.

Excluded from Stage 3 in this pass:

- `frontier_random050_50x16_h5_seed47_f050`;
- `frontier_random050_50x20_h5_seed47_f050`;
- `frontier_random050_50x20_h5_seed48_f050`.

## Stage 2 Result

The Dongxing audit contains six matched comparisons. The most relevant rows:

- `return_50x16_h5`: transfer minus scratch reward `-4.1141`,
  interpretation `scratch_higher_reward`.
- `low_budget_20`: transfer minus scratch reward `4.2484`,
  interpretation `transfer_higher_reward`.

This supports only conditional follow-up, not a broad transfer-win conclusion.

## Decision Packet

Decision:
`proceed_to_stage3_confirmatory_rollouts`

Meaning: Stage 3 may train and roll out only the authorized passing rows, with
matched baselines. Diagnostic near-pass rows must stay diagnostic.

## Last Verification

Run from:
`D:\test\paper10-geojepa-mpc-farmland-layout\.worktrees\paper10-original-vision-validation`

Commands passed:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_monitor_matrix.py paper10_geojepa_mpc\tests\test_dongxing_transfer_audit.py paper10_geojepa_mpc\tests\test_original_vision_decision_packet.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
$pattern = "direct 50-state " + "success|robust transfer " + "superiority|proves " + "scale-up"
rg -n $pattern docs\superpowers\plans\2026-06-18-paper10-stage3-confirmatory-rollout-plan.md paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_50state_label_matrix_2026-06-17.md paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md
```

Observed results:

- `42 passed`
- `Paper10 preflight: PASS`
- claim-boundary grep returned no matches
- working tree was clean at `d4403f5`

## Next Step

Execute the Stage 3 plan in:
`docs/superpowers/plans/2026-06-18-paper10-stage3-confirmatory-rollout-plan.md`

Do not claim final 50-state rollout success or a broad transfer-win conclusion
before matched Stage 3 rollout evidence exists and is summarized.
