# Paper10 GeoJEPA-MPC Farmland Layout

Reproducibility package for Paper10:

`JEPA-Regularized Geospatial World Models for Constrained Farmland Layout Planning`

The repository packages the Paper10 code, tests, experiment outputs, saved
checkpoints, compatibility code borrowed from the Paper9 environment, and the
small smoke Tool2 dataset needed for reviewer-side verification. The full
Bishan Tool2 dataset is larger than a normal source repository and is documented
as an external data dependency in `DATA_AVAILABILITY.md`.

## Latest Packaged Experiment

This package now includes the 2026-06-08 `frontier_random050` value-head
20x16/h5 scale-up:

- value labels: `paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`
- trained checkpoint: `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt`
- scale-up report: `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_20x16_h5_seed44_top5_report_2026-06-08.md`
- five-seed rollout summary: `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`

The scale-up uses `selector=value_filter`, executable masks, `H=5`, `K=50`,
candidate blend weight `0.1`, and the diagnostics-selected top-5 value-head
gate. The recorded 100-step seeds 0-4 mean total reward is `69.4705` with sample
standard deviation `1.0004`.

The previous 10x12/h5 top-4 pilot remains packaged as the direct baseline. Its
recorded 100-step seeds 0-4 mean total reward is `65.2566` with sample standard
deviation `5.0037`.

The tested 50-state `frontier_random050` label sets are negative diagnostics,
not training inputs. The macOS `50x24/h5 seed45` run and the Windows seed46
ablation grid failed the monitor gates, so the current paper-facing claim stays
anchored on the reproducible 20x16/top5 result.

Paper-facing writing assets are tracked under
`paper10_geojepa_mpc/experiments/results/`:

- `e0_frontier_random050_results_synthesis_2026-06-09.md`
- `e0_frontier_random050_manuscript_section_draft_2026-06-09.md`
- `e0_frontier_random050_manuscript_tables_2026-06-09.md`
- `e0_frontier_random050_manuscript_scaffold_2026-06-09.md`
- `e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md`
- `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`
- `e0_frontier_random050_introduction_cited_draft_2026-06-09.md`
- `e0_frontier_random050_methods_draft_2026-06-09.md`
- `e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_submission_readiness_checklist_2026-06-09.md`
- `e0_bishan_task_environment_self_contained_methods_2026-06-09.md`
- `e0_reward_and_rollout_metric_definitions_2026-06-09.md`
- `e0_citation_and_claim_checklist_2026-06-09.md`
- `e0_frontier_random050_figure_plan_2026-06-09.md`

Verified citation assets are tracked under `references/`:

- `paper10_verified_references_2026-06-09.bib`
- `paper10_local_sources_2026-06-09.bib`
- `paper10_citation_map_2026-06-09.md`
- `paper10_paper9_local_source_status_2026-06-09.md`

## Repository Layout

- `paper10_geojepa_mpc/`: Paper10 models, planning utilities, training helpers,
  experiments, tests, checkpoints, and recorded result artifacts.
- `arcgis_toolbox_paper9/private_source/`: Paper9 compatibility code used by
  Paper10 real-environment rollouts.
- `county_env.py`: Paper9 `CountyLevelEnv` environment required by the bundled
  compatibility layer.
- `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`: small smoke
  Tool2 dataset included in Git.
- `paper7/data/`: small GeoFM embedding asset used by optional fusion tests and
  ablations.
- `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`: Google Colab
  notebook retained for 50x24/h5 diagnostic reproduction or re-parameterized
  future runs.
- `docs/windows_frontier_random050_ablation.md`: Windows CPU guide for
  reproducing or editing the `frontier_random050` 50-state label-only ablation
  grid.
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`: resumable Windows
  PowerShell runner for that ablation grid.
- `docs/superpowers/`: Paper10 design and implementation planning notes.
- `DATA_AVAILABILITY.md`: full-data layout and large-file policy.
- `REPRODUCIBILITY.md`: commands for tests, smoke runs, and full-data runs.
- `MANIFEST.md`: inventory of included and intentionally externalized assets.

## Quick Start

Create and activate an environment, then install the Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the reviewer smoke verification:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Run the included smoke data summary:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

## Full Experiments

Full Bishan training and real-environment rollout commands require the external
prepared data under the repository root:

- `tool2/transitions.npz`
- `tool2/pairwise.npz`
- `dem_slope_analysis/output/DLTB_with_slope.shp` or `.gpkg`
- `results_real/blocks/`
- `townships.json`

See `DATA_AVAILABILITY.md` for exact placement and `REPRODUCIBILITY.md` for
the command sequence.

## Colab 50x24/h5 Diagnostic

The repository includes
`notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`. Its original
50x24/h5 seed45 target has since failed the monitor gate on macOS, so the
notebook should be treated as a diagnostic/reproduction template unless its
parameters are deliberately changed.

## macOS 50x24/h5 Diagnostic

When Colab compute quota is unavailable, the same diagnostic can be reproduced
locally from `docs/macos_frontier_random050_50x24_h5.md`. The tracked runner
`scripts/macos/run_frontier_random050_50x24_h5.sh` validates local full-data
placement, writes outputs outside the Git checkout, and skips steps whose final
artifacts already exist.

## Windows 50-State Ablation

The Windows workstation can run Paper10 on CPU with the full data rooted at
`D:\test`. Use `docs/windows_frontier_random050_ablation.md` and
`scripts/windows/run_frontier_random050_ablation_grid.ps1` for reproducing or
editing the `frontier_random050` 50-state label-only ablation grid. The packaged
seed46 grid failed all default and post-hoc checks; reuse the runner only for
reproduction or after editing the local ignored grid. The runner defaults to
monitor-only mode and trains only when a gate passes and local config explicitly
sets `TrainOnPass = 1`.

For the current continuation decision, see
`docs/superpowers/notes/2026-06-09-paper10-50state-redesign-handoff.md`.

## Verification Status

The source package was copied from the active Paper10 workspace on 2026-06-08.
Before packaging, the Paper10 test suite was run with:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `88 passed in 49.97s`.

After packaging, the same test suite was run from this repository directory:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `88 passed in 43.25s`.

After adding the Windows ablation package on 2026-06-09, the suite was rerun
from this repository directory with the same Python executable.

Result: `105 passed in 3.74s`.

After adding manuscript tables, figure assets, the 50-state redesign handoff,
the manuscript scaffold, and the figure plan on 2026-06-09, the suite was rerun
again from this repository directory with the same Python executable.

Result: `108 passed in 3.75s`.

After adding the paper-facing Methods draft on 2026-06-09, the suite was rerun
again from this repository directory with the same Python executable.

Result: `108 passed in 4.68s`.

After adding the reward and rollout metric definitions note on 2026-06-09, the
suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After adding the submission-readiness checklist on 2026-06-09, the suite was
rerun again from this repository directory with the same Python executable.

Result: `108 passed`.

After adding the self-contained Bishan task/environment Methods note on
2026-06-09, the suite was rerun again from this repository directory with the
same Python executable.

Result: `108 passed`.

After adding the self-contained integrated manuscript variant on 2026-06-09,
the suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

Reviewers should run the relative-path command in `REPRODUCIBILITY.md` after
cloning.
