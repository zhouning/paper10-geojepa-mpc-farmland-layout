# Paper10 claim-source consistency audit

Date: 2026-06-18

Status: source-derived audit of the current Paper10 manuscript-facing claims. This file checks key numbers against tracked JSON/CSV evidence and does not add new experimental claims.

## Source files

- stage3_json: `paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- dongxing_return_label_csv: `paper10_geojepa_mpc\experiments\results\e0_dongxing_return_label_family_summary_2026-06-10.csv`
- dongxing_low_budget_csv: `paper10_geojepa_mpc\experiments\results\e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`

## Bishan and Stage 3 checks

| claim | source-derived result | status |
|---|---|---|
| Bishan 20x16/top5 anchor improves reward and stability | mean 69.4705 versus baseline 67.5437; sample std 1.0004 versus 7.2246 | True |
| Stage 3 confirmatory 50-state rows beat the matched baseline | frontier_random050_50x16_h5_seed48_f050 delta -3.2477; frontier_random050_50x24_h5_seed47_f075 delta -1.2893 | False |
| Diagnostic near-pass can strengthen the confirmatory claim | frontier_random050_50x24_h5_seed48_f075 mean 67.4913, delta -0.0524; must not be pooled | False |

Interpretation: the Bishan anchor is source-supported, while confirmatory 50-state rows do not beat the matched baseline.

## Dongxing/Neijiang checks

| claim | source-derived result | status |
|---|---|---|
| Return-label scaling improves transfer family | gain versus pairwise 13.7289 | True |
| Return-label scaling improves scratch family | gain versus pairwise 15.5214 | True |
| Robust Bishan-to-Dongxing transfer superiority | 50x16 transfer minus scratch -4.1141; low-label effects budget 5: -8.7274; budget 10: -3.4588; budget 20: 4.2484 | False |

## Claim boundary

- Supported: Bishan 20x16/top5 reward and stability improvement under the matched rollout protocol.
- Supported descriptively: Dongxing/Neijiang return-label scaling improves transfer and scratch families versus their pairwise rows.
- Not supported: broad confirmatory 50-state baseline beating.
- Not supported: robust Bishan-to-Dongxing transfer superiority.
- Not supported: direct positive scale-up under the 50-state confirmatory protocol or operational irregular-parcel deployment.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.paper10_claim_source_audit --stage3-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --dongxing-return-label-csv paper10_geojepa_mpc\experiments\results\e0_dongxing_return_label_family_summary_2026-06-10.csv --dongxing-low-budget-csv paper10_geojepa_mpc\experiments\results\e0_dongxing_low_label_budget_family_summary_2026-06-10.csv --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_claim_source_consistency_audit_2026-06-18.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_claim_source_consistency_audit_2026-06-18.md
```
