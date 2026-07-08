# Paper10 figure/table source coverage audit

Date: 2026-06-19

Status: source-derived figure/table source coverage audit.

This audit checks current manuscript figure/table assembly sources and does not add a new experimental claim. No rollout was rerun.

overall source coverage: PASS
submission-ready figure/table package: NO

## Source files

- blueprint: `paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`
- numbering_freeze: `paper10_geojepa_mpc/experiments/results/e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- source_data_map: `paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md`

## Figure/table source coverage

| item | coverage | generation status | source files | generation scripts | unresolved fields | claim boundaries |
|---|---|---|---|---|---|---|
| Main Figure 1 | PASS | blocked_pending_artwork | `paper10_geojepa_mpc/experiments/value_label_generation.py`, `paper10_geojepa_mpc/experiments/value_label_monitor.py`, `paper10_geojepa_mpc/experiments/run_e0_value_head_train.py`, `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py`, `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_figure_plan_2026-06-09.md`, `paper10_geojepa_mpc/experiments/results/e0_integrated_dongxing_figure_plan_2026-06-11.md` | none | final schematic artwork, journal figure dimensions | workflow schematic only; no new quantitative result |
| Main Figure 2 | PASS | scripted_preview_available | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`, `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`, `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json` | `scripts/paper10/plot_frontier_random050_figures.py` | final figure number, inset decision | Bishan 20x16/top5 is the positive anchor only under the tested rollout protocol |
| Main Figure 3 | PASS | scripted_preview_available | `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`, `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`, `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`, `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md`, `paper10_geojepa_mpc/experiments/results/e0_macos_gpkg_reproduction_findings_2026-06-09.md` | `scripts/paper10/plot_frontier_random050_figures.py` | final main-versus-supplementary placement | direct 50-state Bishan scale-up success is not supported, diagnostic near-pass must not be pooled |
| Main Figure 4 | PASS | scripted_preview_available | `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_family_summary_2026-06-10.csv`, `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_50x16_family_2026-06-10.md`, `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`, `paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md` | `scripts/paper10/plot_integrated_dongxing_figures.py` | final figure number, metric panel placement | robust Bishan-to-Dongxing transfer superiority is not supported, Dongxing/Neijiang supports calibration and stress-test value |
| Supplementary Figure S1 | PASS | scripted_preview_available | `paper10_geojepa_mpc/experiments/results/e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`, `paper10_geojepa_mpc/experiments/results/e0_dongxing_low_label_budget_family_2026-06-10.md`, `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`, `paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md` | `scripts/paper10/plot_integrated_dongxing_figures.py` | final main-versus-supplementary placement, target-journal caption length | low-label transfer superiority is mixed and not robustly supported |
| Main Table 1 | PASS | table_source_available | `paper10_geojepa_mpc/experiments/results/e0_value_label_monitor_frontier_random050_10x12_h5_seed43_top4.json`, `paper10_geojepa_mpc/experiments/results/e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json`, `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | none | final table number | monitor gates authorize escalation; they do not prove general scale-up |
| Main Table 2 | PASS | frozen_table_available | `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`, `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`, `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`, `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`, `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md`, `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.json` | none | rounding, main-text placement | Table 1 of the freeze is the only positive Bishan performance anchor, Stage 3 rows are boundary evidence, Algorithm-readiness addendum records the current true-reward guard evidence, setting-specific guard only; not final submission readiness |
| Main Table 3 | PASS | table_source_available | `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_family_summary_2026-06-10.csv`, `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_50x16_family_2026-06-10.md`, `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md` | none | whether full metric table is main text | return-label scaling is descriptive calibration evidence, robust Bishan-to-Dongxing transfer superiority is not supported |

## Coverage checks

- Missing blueprint items: none
- Missing numbering-freeze items: none
- Missing boundary tokens: none

## Submission blockers

- final schematic artwork for Main Figure 1
- target-journal figure dimensions and export formats
- final main-versus-supplementary placement
- journal-specific captions and table placement

## Interpretation boundary

- PASS means the current figure/table assembly map has tracked source files and explicit unresolved export fields.
- PASS does not mean the formal manuscript is ready for submission.
- Main Figure 3 must not be used to claim direct 50-state Bishan scale-up success.
- Main Figure 4 and Main Table 3 must not be used to claim robust Bishan-to-Dongxing transfer superiority.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.figure_table_source_coverage_audit --blueprint paper10_geojepa_mpc\experiments\results\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md --numbering-freeze paper10_geojepa_mpc\experiments\results\e0_integrated_figure_table_numbering_freeze_2026-06-11.md --source-data-map paper10_geojepa_mpc\experiments\results\e0_source_data_map_with_dongxing_2026-06-11.md --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_figure_table_source_coverage_audit_2026-06-19.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_figure_table_source_coverage_audit_2026-06-19.md
```
