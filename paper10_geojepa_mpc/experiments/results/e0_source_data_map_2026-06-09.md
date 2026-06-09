# Paper10 E0 source-data map

Date: 2026-06-09

This document maps the current Paper10 E0 manuscript figures, tables, and
paper-facing claims to tracked source files. It is a source-data and archive
metadata aid, not a new experiment. It should be updated after target-journal
figure/table numbering is frozen.

## Scope and archive record

The mappings below belong to the code and packaged E0 evidence archive
described as Record 1 in
`paper10_geojepa_mpc/experiments/results/e0_archive_metadata_templates_2026-06-09.md`.
The machine-readable archive inventory is
`paper10_geojepa_mpc/experiments/results/e0_archive_manifest_2026-06-09.csv`.
Full reruns from scratch still require the external full Bishan `tool2/` data
and prepared GPKG-root geospatial inputs described in `DATA_AVAILABILITY.md`.

Do not use this map to claim 50-state scale-up. The 50-state rows are mapped
only as failed diagnostics and boundary evidence.

## Figure source-data map

| manuscript item | mapped conclusion | source files | archive record | unresolved fields |
|---|---|---|---|---|
| Figure 1. Monitor-gated GeoJEPA-MPC value filtering workflow | Value-head training is conditional on label quality and monitor-gate continuation. | `paper10_geojepa_mpc/experiments/value_label_generation.py`; `paper10_geojepa_mpc/experiments/value_label_monitor.py`; `paper10_geojepa_mpc/experiments/run_e0_value_head_train.py`; `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_figure_plan_2026-06-09.md` | Record 1 | Final schematic artwork and figure number. |
| Figure 2. Seed-wise reward comparison | 20x16/top5 increases mean reward and reduces weak-seed behavior relative to 10x12/top4. | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `scripts/paper10/plot_frontier_random050_figures.py` | Record 1 | Final figure number and whether a summary-stat inset is used. |
| Figure 3. Failed 50-state diagnostics | Post-hoc larger top-k checks did not rescue the tested Windows 50-state rows. | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`; `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `paper10_geojepa_mpc/experiments/results/e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `scripts/paper10/plot_frontier_random050_figures.py` | Record 1 | Final figure number and whether macOS 50x24 appears in a panel, caption, or supplement only. |

## Table source-data map

| manuscript item | mapped conclusion | source files | archive record | unresolved fields |
|---|---|---|---|---|
| Table E0-1. Monitor-selected training gates | 10x12/top4 and 20x16/top5 were the two monitor-passing training gates used for E0 value-head runs. | `paper10_geojepa_mpc/experiments/results/e0_value_label_monitor_frontier_random050_10x12_h5_seed43_top4.json`; `paper10_geojepa_mpc/experiments/results/e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` | Record 1 | Final table number. |
| Table E0-2. Five-seed rollout comparison | 20x16/top5 improved mean total reward by `4.2139` or `6.46%` and reduced sample standard deviation by `4.0034`. | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` | Record 1 | Final table number and rounding policy. |
| Table E0-3. Seed-wise rollout rewards | Seeds 1-4 improved under 20x16/top5 while seed0 decreased, supporting a distributional rather than single-seed framing. | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json` | Record 1 | Whether this table is main text or supplementary. |
| Table E0-4. Default-gate failures for 50-state labels | Every tested 50-state row failed default top-3/top-4/top-5 monitor checks. | `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `paper10_geojepa_mpc/experiments/results/e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` | Record 1 | Whether macOS and Windows rows are combined or separated in final layout. |
| Table E0-5. Larger top-k diagnostics for failed Windows rows | Larger top-k values still returned `stop` and did not justify value-head training. | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`; `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md` | Record 1 | Supplementary table number. |
| Table E0-S1. macOS GPKG reproduction audit | The packaged 20x16/h5 seed44 label set reproduces on the GPKG root within exact or floating-point tolerance. | `paper10_geojepa_mpc/experiments/results/e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz` | Record 1 plus external GPKG-root data access route | Supplementary table number and final full-data access route. |

## Claim-to-source map

| claim | current source files | status |
|---|---|---|
| 20x16/top5 mean total reward is `69.4705` with sample standard deviation `1.0004`. | `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `e0_frontier_random050_manuscript_tables_2026-06-09.md` | Supported. |
| 10x12/top4 baseline mean total reward is `65.2566` with sample standard deviation `5.0037`. | `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_manuscript_tables_2026-06-09.md` | Supported. |
| 20x16/top5 improves over 10x12/top4 by `4.2139` or `6.46%`. | `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; `e0_frontier_random050_results_synthesis_2026-06-09.md` | Supported. |
| 20x16/top5 passed the monitor gate at top-5 with candidate regret `0.1877`, candidate overlap `0.6300`, and one-step regret `2.4626`. | `e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json`; `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json` | Supported. |
| The GPKG root reproduces the packaged 20x16 labels. | `e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz` | Supported if the full GPKG-root data route is available. |
| Tested 50-state labels failed the monitor gate and should not be trained. | `e0_windows_frontier_random050_ablation_findings_2026-06-09.md`; `e0_macos_gpkg_reproduction_findings_2026-06-09.md`; `e0_frontier_random050_topk_diagnostics_2026-06-09.csv` | Supported as a boundary claim. |
| Paper10 generally scales to 50 states. | None; current 50-state rows failed. | Not supported; do not claim. |
| Paper9 task/reward provenance is publicly citable. | None in the public route; local placeholder is internal only. | Not supported unless a public Paper9 source becomes available. |

## File-family manifest for source data

| file family | role | archive handling |
|---|---|---|
| `e0_frontier_random050_seedwise_rewards_2026-06-09.csv` | Compact Figure 2 source data. | Include in Record 1. |
| `e0_frontier_random050_topk_diagnostics_2026-06-09.csv` | Compact Figure 3 source data. | Include in Record 1. |
| `e0_frontier_random050_value_head_*_rollout_summary.json` | Seed-level rollout metrics and aggregate reward statistics. | Include in Record 1. |
| `e0_value_label_monitor_frontier_random050_*_top*.json` | Monitor-gate diagnostics for passing and failed label sets. | Include in Record 1. |
| `e0_value_labels_frontier_random050_rank_seed2028_*.npz` | Value-label arrays used by monitor, training, and reproduction checks. | Include packaged NPZ files in Record 1; full reruns need external data. |
| `paper10_geojepa_mpc/experiments/checkpoints/` | Value-head and rank checkpoints used by packaged runs. | Include in Record 1. |
| `scripts/paper10/plot_frontier_random050_figures.py` | Rebuilds draft Figure 2 and Figure 3 previews from tracked CSVs. | Include in Record 1. |
| `e0_archive_manifest_2026-06-09.csv` | Machine-readable archive file-family checklist. | Include in Record 1. |
| `reviewer_outputs/` | Local generated previews and rerun outputs. | Exclude unless final figure exports are intentionally selected and documented. |

## Finalization checklist

- Select final figure/table numbering.
- Confirm whether Figure 1 is submitted as an editable schematic source file,
  generated figure file, or manuscript artwork.
- Decide whether Tables E0-3, E0-5, and E0-S1 are supplementary tables.
- Update this file if any final figure panels are added, removed, or merged.
- Record the final archive DOI or reviewer link in
  `e0_data_code_availability_draft_2026-06-09.md`.
- Keep the 50-state rows framed as failed diagnostics, not successful scale-up
  evidence.
