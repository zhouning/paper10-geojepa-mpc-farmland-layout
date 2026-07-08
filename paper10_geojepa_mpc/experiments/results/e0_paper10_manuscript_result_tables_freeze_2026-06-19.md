# Paper10 manuscript result tables freeze

Date: 2026-06-19

Status: source-derived table freeze for the current Paper10 manuscript result tables.

This file is derived from audited JSON evidence and does not add a new experimental claim. No rollout was rerun.

raw-rollout consistency: PASS

## Source files

- stage3_json: `paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- claim_audit_json: `paper10_geojepa_mpc\experiments\results\e0_paper10_claim_source_consistency_audit_2026-06-18.json`
- anchor_raw_audit_json: `paper10_geojepa_mpc\experiments\results\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json`
- true_reward_guard_json: `paper10_geojepa_mpc\experiments\results\e0_paper10_true_reward_guard_readiness_2026-07-08.json`

## Table 1. Bishan anchor versus matched baseline

| row | mean reward | sample std | delta vs baseline | raw-rollout consistency | interpretation |
|---|---:|---:|---:|---|---|
| matched_paper9_rank_seed2028_baseline | 67.5437 | 7.2246 | 0.0000 | n/a | matched comparator for the Stage 3 rollout protocol |
| bishan_20x16_top5_frozen_anchor | 69.4705 | 1.0004 | 1.9269 | PASS | positive anchor under the matched rollout protocol |

## Table 2. Stage 3 boundary rows

| run | role | states | candidates | selected top_k | mean reward | sample std | delta vs baseline | interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| frontier_random050_50x16_h5_seed48_f050 | confirmatory_pass | 50 | 16 | 6 | 64.2960 | 4.2503 | -3.2477 | boundary evidence; below matched baseline |
| frontier_random050_50x24_h5_seed47_f075 | confirmatory_pass | 50 | 24 | 12 | 66.2544 | 4.8565 | -1.2893 | boundary evidence; below matched baseline |
| frontier_random050_50x24_h5_seed48_f075 | diagnostic_near_pass | 50 | 24 | 12 | 67.4913 | 4.5711 | -0.0524 | diagnostic near-pass only; must not be pooled |

## Table 3. Claim status for manuscript conversion

| claim | status | source-derived basis | manuscript boundary |
|---|---|---|---|
| Bishan 20x16/top5 reward and stability anchor | supported | mean 69.4705 versus baseline 67.5437; sample std 1.0004 versus 7.2246 | Use as the positive Bishan anchor only. |
| Stage 3 confirmatory 50-state rows beat the matched baseline | not supported | frontier_random050_50x16_h5_seed48_f050 delta -3.2477; frontier_random050_50x24_h5_seed47_f075 delta -1.2893 | Use as Stage 3 boundary evidence. |
| Diagnostic near-pass row | not pooled | frontier_random050_50x24_h5_seed48_f075 mean 67.4913, delta -0.0524 | Report separately; must not be pooled. |
| Dongxing/Neijiang return-label scaling | supported descriptively | transfer gain 13.7289; scratch gain 15.5214 | Use as calibration or stress-test evidence. |
| robust transfer superiority | not supported | 50x16 transfer minus scratch -4.1141 | Do not use as a positive transfer claim. |

## Algorithm-readiness addendum: current true-reward guard

| row | baseline mean | guard mean | mean delta | seed wins | bootstrap 95% CI lower | switch rate | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| true_reward_margin_guard_m150_audit7x7_20seed | 65.8876 | 72.1773 | 6.2897 | 20 / 20 | 4.1643 | 0.0855 | current primary algorithm-readiness candidate; setting-specific guard only |

## Interpretation boundary

- Table 1 is the only positive Bishan performance anchor in this freeze.
- Table 2 is boundary evidence under the matched comparator; the diagnostic near-pass remains separate.
- Table 3 preserves the claim-source audit boundary for Dongxing/Neijiang calibration and transfer wording.
- The algorithm-readiness addendum is current primary guard evidence and remains a setting-specific guard only.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.manuscript_result_tables_freeze --stage3-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --claim-audit-json paper10_geojepa_mpc\experiments\results\e0_paper10_claim_source_consistency_audit_2026-06-18.json --anchor-raw-audit-json paper10_geojepa_mpc\experiments\results\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json --true-reward-guard-json paper10_geojepa_mpc\experiments\results\e0_paper10_true_reward_guard_readiness_2026-07-08.json --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_result_tables_freeze_2026-06-19.md
```
