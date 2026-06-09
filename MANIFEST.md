# Manifest

This repository is a Paper10 reproducibility package. It intentionally includes
source code, tests, result evidence, checkpoints, compatibility code, and small
data needed for smoke verification.

## Included

- `paper10_geojepa_mpc/`: 222 non-cache files copied from the active Paper10
  workspace, including 53 Python files, 101 JSON files, 33 Markdown files,
  9 NPZ files, 10 PyTorch checkpoint files, and 16 log files.
- `arcgis_toolbox_paper9/private_source/`: 10 Paper9 compatibility source files
  used by Paper10's real-environment rollout and value-label workflows.
- `county_env.py`: Paper9 county-level environment implementation used by
  `private_source.blocks_env`.
- `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`: 4 small smoke
  Tool2 files used by tests and smoke commands.
- `paper7/data/`: GeoFM embedding array and metadata used by optional fusion
  paths.
- `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`: Google Colab
  notebook retained for 50x24/h5 diagnostic reproduction or re-parameterized
  future runs.
- `docs/macos_frontier_random050_50x24_h5.md`: macOS continuation guide for the
  superseded `frontier_random050` 50x24/h5 diagnostic run.
- `scripts/macos/run_frontier_random050_50x24_h5.sh`: resumable macOS local
  runner for the same experiment.
- `scripts/macos/frontier_random050_50x24_h5.env.example`: local path and device
  configuration template for the macOS runner.
- `docs/windows_frontier_random050_ablation.md`: Windows CPU continuation guide
  for the next `frontier_random050` 50-state ablation grid.
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`: resumable Windows
  PowerShell runner for label generation, diagnostics, monitor gates, and
  optional value-head training after a passing gate.
- `scripts/windows/frontier_random050_ablation.env.example.ps1`: local path,
  device, and ablation-grid configuration template for the Windows runner.
- `docs/superpowers/specs/2026-06-07-paper10-geojepa-mpc-design.md`: design
  specification.
- `docs/superpowers/plans/2026-06-07-paper10-geojepa-mpc.md`: implementation
  plan.
- `docs/superpowers/plans/2026-06-07-paper10-e0-smoke-training.md`: smoke
  training plan.
- `docs/superpowers/notes/2026-06-09-paper10-50state-redesign-handoff.md`:
  current continuation decision for Paper10 after the failed 50-state
  `frontier_random050` diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_10x12_h5_seed43_pilot_report_2026-06-08.md`:
  `frontier_random050` value-head 10x12/h5 pilot report.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`:
  five-seed 100-step rollout summary for the 10x12/h5 pilot.
- `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt`:
  checkpoint used by the 10x12/h5 pilot rollouts.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_20x16_h5_seed44_top5_report_2026-06-08.md`:
  latest `frontier_random050` value-head 20x16/h5 scale-up report.
- `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md`:
  Windows CPU 50-state ablation findings for the next `frontier_random050`
  candidate-grid diagnosis.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_synthesis_2026-06-09.md`:
  paper-facing synthesis of the E0 `frontier_random050` pilot, scale-up,
  reproduction audit, and 50-state boundary diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_section_draft_2026-06-09.md`:
  manuscript-style Results and Discussion draft for the E0 `frontier_random050`
  evidence package.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md`:
  manuscript-ready E0 `frontier_random050` tables, captions, and placement
  recommendations.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`:
  figure-ready seed-wise reward comparison for 10x12/top4 vs 20x16/top5.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`:
  figure-ready post-hoc top-k diagnostics for failed Windows 50-state labels.
- `scripts/paper10/plot_frontier_random050_figures.py`:
  offline plotting script for the seed-wise reward and top-k diagnostic figures;
  writes generated figure files under ignored `reviewer_outputs/` by default.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`:
  five-seed 100-step rollout summary for the 20x16/h5 scale-up.
- `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt`:
  checkpoint used by the 20x16/h5 scale-up rollouts.
- Root reproducibility documents:
  - `README.md`
  - `REPRODUCIBILITY.md`
  - `DATA_AVAILABILITY.md`
  - `requirements.txt`
  - `.gitignore`
  - `references/README.md`

## Excluded Intentionally

- Python caches: `__pycache__/`, `.pytest_cache/`, `*.pyc`.
- Local virtual environments.
- Full Bishan Tool2 data under `tool2/`, because it is approximately 1.65 GB.
- Full prepared geospatial inputs under `dem_slope_analysis/` and
  `results_real/`, because they should be supplied through the project data
  archive or generated by the upstream preparation pipeline.
- Third-party paper PDFs. The LE-WM paper and upstream GitHub project are listed
  in `references/README.md` instead.

## Large File Check

At packaging time, no included file was larger than 100 MB.
