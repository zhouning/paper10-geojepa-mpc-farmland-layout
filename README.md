# Paper10 GeoJEPA-MPC Farmland Layout

Reproducibility package for Paper10:

`JEPA-Regularized Geospatial World Models for Constrained Farmland Layout Planning`

The repository packages the Paper10 code, tests, experiment outputs, saved
checkpoints, compatibility code borrowed from the Paper9 environment, and the
small smoke Tool2 dataset needed for reviewer-side verification. The full
Bishan Tool2 dataset is larger than a normal source repository and is documented
as an external data dependency in `DATA_AVAILABILITY.md`.

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

## Verification Status

The source package was copied from `D:\test\paper10_geojepa_mpc` on
2026-06-08. Before packaging, the Paper10 test suite was run with:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `87 passed in 104.91s`.

After packaging, the same test suite was run from this repository directory:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `87 passed in 94.55s`.

Reviewers should run the relative-path command in `REPRODUCIBILITY.md` after
cloning.
