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
  notebook for the next `frontier_random050` 50x24/h5 full-data run.
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

## Colab 50x24/h5 Run

The repository includes
`notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb` for running the
next `frontier_random050` 50x24/h5 experiment on Google Colab. The notebook
mounts Google Drive, clones or updates this repository, validates the full
Bishan data layout from Drive, writes long-running outputs back to Drive, and
skips steps whose final artifacts already exist.

## macOS 50x24/h5 Run

When Colab compute quota is unavailable, continue the same experiment locally
from `docs/macos_frontier_random050_50x24_h5.md`. The tracked runner
`scripts/macos/run_frontier_random050_50x24_h5.sh` validates local full-data
placement, writes outputs outside the Git checkout, and skips steps whose final
artifacts already exist.

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

Reviewers should run the relative-path command in `REPRODUCIBILITY.md` after
cloning.
