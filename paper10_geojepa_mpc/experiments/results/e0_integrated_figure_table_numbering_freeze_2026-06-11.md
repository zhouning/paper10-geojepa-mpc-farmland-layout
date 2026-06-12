# Paper10 integrated figure and table numbering freeze

Date: 2026-06-11

This is a submission-control freeze for the current generic integrated draft,
not a target-journal final layout. It freezes the conversion rule that should
be used when the with-Dongxing scaffold is turned into a manuscript file:

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_dongxing_figure_plan_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`

Do not use this file to infer a target journal, final figure dimensions, DOI,
reviewer link, data licence, or restricted-data access route. Those fields are
still blocked by the post-Dongxing submission audit and are consolidated in
`e0_submission_blocker_decision_packet_2026-06-11.md`.

## Authority order

1. This freeze controls the next manuscript-conversion pass.
2. The integrated table package remains the source of table values, captions,
   and internal package numbering.
3. The integrated scaffold remains the writing spine and argument map.
4. The figure plan and source-data map remain the artwork/source-data contracts.

If a quick map in the scaffold conflicts with this file, use this file for
main-versus-supplementary placement and final conversion numbering.

## Main figure freeze

| frozen manuscript item | source-package item | role | placement decision |
|---|---|---|---|
| Main Figure 1 | Figure 1. Monitor-gated value filtering workflow | Method workflow and claim boundary. | Main text. |
| Main Figure 2 | Figure 2. Bishan 20x16/top5 reward and stability | Primary Bishan positive result. | Main text. |
| Main Figure 3 | Figure 3. Bishan 50-state monitor boundary | Scale-up boundary and overclaim control. | Main text. |
| Main Figure 4 | Figure 4. Dongxing return-label scaling | External-region calibration result. | Main text. |
| Supplementary Figure S1 | Figure 5. Dongxing low-label transfer stress test | Transfer stress-test boundary. | Supplementary by default. |

The low-label stress test must remain visible in the manuscript package, but it
should not displace the primary Bishan result or the Dongxing return-label
scaling panel in the main figure sequence unless a target journal explicitly
requires all stress tests in the main text.

## Main table freeze

| frozen manuscript item | source-package item | role | placement decision |
|---|---|---|---|
| Main Table 1 | Table 1. Bishan Monitor-Selected Training Gates | Monitor-gate decision evidence. | Main text or compact main-text table. |
| Main Table 2 | Table 2. Bishan Rollout Improvement and Stability | Primary Bishan rollout result. | Main text. |
| Main Table 3 | Table 4. Dongxing Return-Label Scaling | Dongxing calibration result. | Main text. |
| Supplementary Table S1 | Table 3. Bishan 50-State Monitor-Gate Boundary | Detailed failed 50-state diagnostics. | Supplementary by default if Main Figure 3 carries the visual boundary. |
| Supplementary Table S2 | Table 5. Dongxing Low-Label Transfer Stress Test | Detailed low-label transfer boundary. | Supplementary by default. |
| Internal Control Table C1 | Table 6. Claim Boundaries for Paper10 | Claim-audit and reviewer-response support. | Not a manuscript table unless requested by the target venue. |

The source table package's internal numbering is intentionally preserved for
traceability. During manuscript conversion, cite the frozen manuscript item
names above, not the package-only table numbers.

## Caption and claim locks

- Main Figure 3 and Supplementary Table S1 must state that tested 50-state
  Bishan labels failed monitor gates; they must not be written as successful
  scale-up evidence.
- Main Figure 4 and Main Table 3 support Dongxing calibration through
  return-label scaling; they do not support robust Bishan-to-Dongxing transfer
  superiority.
- Main Figure 4 and Main Table 3 do not support robust Bishan-to-Dongxing transfer superiority.
- Supplementary Figure S1 and Supplementary Table S2 must preserve the 5-label
  and 10-label scratch advantage and the 20-label transfer advantage.
- The title, abstract, captions, conclusion, and response package should use
  bounded language: monitor-gated value filtering and calibration, not broad
  cross-region transfer superiority.

## Source-data crosswalk

| frozen item | source data |
|---|---|
| Main Figure 2 | `e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json` |
| Main Figure 3 | `e0_frontier_random050_topk_diagnostics_2026-06-09.csv`; `e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `e0_macos_gpkg_reproduction_findings_2026-06-09.md` |
| Main Figure 4 | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_return_label_50x16_family_2026-06-10.md` |
| Supplementary Figure S1 | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_2026-06-10.md` |
| Main Table 1 | `e0_value_label_monitor_frontier_random050_10x12_h5_seed43_top4.json`; `e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json` |
| Main Table 2 | `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json` |
| Main Table 3 | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_return_label_50x16_family_2026-06-10.md` |
| Supplementary Table S1 | `e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `e0_macos_gpkg_reproduction_findings_2026-06-09.md` |
| Supplementary Table S2 | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_2026-06-10.md` |

## Open fields before journal submission

- Target journal and article type.
- Journal-specific figure count, table count, supplementary naming, and export
  formats.
- Final artwork for Main Figure 1.
- Repository DOI or reviewer link.
- Code and data licences.
- Full Bishan, Dongxing/Neijiang, and GPKG-root data access routes.
- Citation placement and statistical-reporting policy.
