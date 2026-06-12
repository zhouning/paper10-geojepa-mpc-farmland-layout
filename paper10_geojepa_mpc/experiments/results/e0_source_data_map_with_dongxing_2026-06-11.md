# Paper10 source-data map with Dongxing evidence

Date: 2026-06-11

This document extends `e0_source_data_map_2026-06-09.md` for the integrated
Paper10 manuscript route that includes Dongxing/Neijiang evidence. It maps the
current Figure 4 and Figure 5 candidates to tracked source files and to the
with-Dongxing writing spine:

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_dongxing_figure_plan_2026-06-11.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`

The map does not assign final figure numbers for a target journal and does not
turn ignored preview files into submission assets. It exists to keep source
data, captions, and bounded claims aligned before final manuscript conversion.

Numbering note: the current generic manuscript-conversion freeze maps Dongxing
return-label scaling to Main Figure 4 and Main Table 3, and maps the Dongxing
low-label transfer stress test to Supplementary Figure S1 and Supplementary
Table S2.

## Figure source-data map

| manuscript item | mapped conclusion | source files | archive record | unresolved fields |
|---|---|---|---|---|
| Figure 1. Monitor-gated value filtering workflow | Value-head training is conditional on label quality and monitor-gate continuation. | `paper10_geojepa_mpc/experiments/value_label_generation.py`; `paper10_geojepa_mpc/experiments/value_label_monitor.py`; `paper10_geojepa_mpc/experiments/run_e0_value_head_train.py`; `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py`; `e0_frontier_random050_figure_plan_2026-06-09.md`; `e0_integrated_dongxing_figure_plan_2026-06-11.md` | Record 1 | Final schematic artwork and journal figure dimensions. |
| Figure 2. Bishan seed-wise reward comparison | Bishan 20x16/top5 improves mean reward and weak-seed behavior relative to 10x12/top4. | `e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `scripts/paper10/plot_frontier_random050_figures.py` | Record 1 | Final figure number and inset decision. |
| Figure 3. Bishan 50-state monitor diagnostics | Tested 50-state label rows failed monitor checks and define a candidate-proposal boundary. | `e0_frontier_random050_topk_diagnostics_2026-06-09.csv`; `e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `scripts/paper10/plot_frontier_random050_figures.py` | Record 1 | Final main-versus-supplementary placement. |
| Figure 4. Dongxing return-label scaling | Dongxing return labels improve reward for both transfer and scratch families from pairwise-only to 50x16 labels. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_return_label_50x16_family_2026-06-10.md`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`; `scripts/paper10/plot_integrated_dongxing_figures.py` | Record 1 plus Dongxing data route | Final figure number and whether slope/contiguity/baimu metrics stay in the main figure or supplementary table. |
| Figure 5. Dongxing low-label transfer stress test | Low-label transfer is mixed: scratch is higher at 5 and 10 labels, while transfer is higher at 20 labels. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_2026-06-10.md`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`; `scripts/paper10/plot_integrated_dongxing_figures.py` | Record 1 plus Dongxing data route | Final main-versus-supplementary placement and target-journal caption length. |

## Table source-data map

| manuscript item | mapped conclusion | source files | archive record | unresolved fields |
|---|---|---|---|---|
| Table 1. Bishan monitor-selected gates | The 10x12/top4 and 20x16/top5 rows were selected by monitor diagnostics before training. | `e0_value_label_monitor_frontier_random050_10x12_h5_seed43_top4.json`; `e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Record 1 | Final table number. |
| Table 2. Bishan rollout improvement and stability | 20x16/top5 improves mean reward and lowers seed-level variation. | `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Record 1 | Rounding and main-text placement. |
| Table 3. Bishan 50-state monitor-gate boundary | The tested 50-state label sets should not be trained or claimed as positive scale-up evidence. | `e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Record 1 | Main or supplementary placement. |
| Table 4. Dongxing return-label scaling | Return labels improve both transfer and scratch families, but scratch remains higher at 50x16. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_return_label_50x16_family_2026-06-10.md`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Record 1 plus Dongxing data route | Whether full metric table is main text. |
| Table 5. Dongxing low-label transfer stress test | Transfer is not robustly supported as superior under low labels; it is higher only at the 20-label budget. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_2026-06-10.md`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Record 1 plus Dongxing data route | Main or supplementary placement. |

## Claim-to-source map

| claim | current source files | status |
|---|---|---|
| Dongxing/Neijiang loaded 3711 blocks from 76376 parcels and completed real-environment rollout evaluation. | `e0_dongxing_local_data_cross_region_audit_2026-06-10.md`; `e0_dongxing_results_synthesis_2026-06-10.md`; `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md` | Supported if the Dongxing data route is disclosed or controlled. |
| Dongxing return-label scaling improves transfer from `37.8894` to `51.6183` and scratch from `40.2111` to `55.7324`. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | Supported. |
| Bishan-initialized transfer robustly beats Dongxing scratch adaptation. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv` | Not supported; do not claim. |
| Dongxing low-label transfer may help at a moderate budget. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_2026-06-10.md` | Partially supported at 20 labels only. |
| Paper10 provides a monitor-gated calibration workflow rather than a fixed transferable checkpoint. | Bishan monitor files; Dongxing planner value-weight sweep; Dongxing return-label and low-label family summaries; `e0_post_dongxing_submission_gap_audit_2026-06-10.md` | Supported as the current integrated manuscript framing. |

## File-family manifest for Dongxing source data

| file family | role | archive handling |
|---|---|---|
| `e0_dongxing_return_label_family_summary_2026-06-10.csv` | Compact Figure 4 source data. | Include in Record 1. |
| `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv` | Compact Figure 5 source data. | Include in Record 1. |
| `e0_dongxing_return_label_*_2026-06-10.md` | Detailed Dongxing return-label result notes. | Include in Record 1. |
| `e0_dongxing_low_label_budget*_2026-06-10.md` | Detailed low-label budget result notes. | Include in Record 1. |
| `scripts/paper10/plot_integrated_dongxing_figures.py` | Rebuilds draft Figure 4 and Figure 5 previews from tracked CSVs. | Include in Record 1. |
| `reviewer_outputs/paper10_integrated_dongxing_figures/` | Local generated PNG/SVG previews. | Exclude unless final exports are intentionally selected and documented. |

## Finalization checklist

- Freeze final main and supplementary figure/table numbering.
- Decide whether Dongxing Figure 5 is main text or supplementary.
- Backfill Dongxing/Neijiang data access route in the final Data and Code
  Availability statement.
- Keep Figure 4 and Figure 5 captions explicit that robust Bishan-to-Dongxing
  transfer superiority is not robustly supported.
- Regenerate final exports only after journal dimensions and file formats are
  selected.
