# Reproducibility Guide

This guide separates smoke verification, which runs from files included in the
repository, from full Bishan experiments, which require the external prepared
dataset described in `DATA_AVAILABILITY.md`.

## Environment

Tested locally with Python 3.13.7 on Windows. CPU execution is sufficient for
the smoke tests and short probes. CUDA or Colab Pro+ is recommended for longer
training sweeps.

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Smoke Verification Included in Git

Run all Paper10 tests:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Run the smoke dataset header summary:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

Run smoke-scale training:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_smoke.py
```

Run value-label training smoke:

```powershell
.\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\transitions.npz --pairwise-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\pairwise.npz --epochs 1 --batch-size 8 --device cpu --output paper10_geojepa_mpc\experiments\results\reviewer_value_head_smoke.json
```

## Full Bishan Dataset Setup

Place the full prepared data under the repository root:

```text
tool2/transitions.npz
tool2/pairwise.npz
dem_slope_analysis/output/DLTB_with_slope.shp
dem_slope_analysis/output/DLTB_with_slope.dbf
dem_slope_analysis/output/DLTB_with_slope.shx
dem_slope_analysis/output/DLTB_with_slope.prj
results_real/blocks/
townships.json
```

`DLTB_with_slope.gpkg` may be used instead of the shapefile set. The full
Tool2 files are intentionally not committed to Git because they are about
1.65 GB together.

## Full Bishan Training Probe

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_bishan_probe.py --config rank --epochs 1 --batch-size 16 --transition-samples 6000 --pairwise-states 1000 --pairwise-subsample 16 --n-pairs 4 --device cpu
```

## Checkpoint Scoring

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_score_checkpoint.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --pairwise tool2\pairwise.npz --top-k 5 --batch-states 4 --max-states 1000 --device cpu --output paper10_geojepa_mpc\experiments\results\reviewer_checkpoint_scoring.json
```

## Real-Environment Rollout

Short rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 3 --horizon 3 --top-k 20 --seed 0 --device cpu --output paper10_geojepa_mpc\experiments\results\reviewer_env_rollout_smoke_3step_h3_k20.json
```

Matched five-seed rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --output paper10_geojepa_mpc\experiments\results\reviewer_env_rollout_5seed_h5_k50_executable_mask.json
```

## Expected Packaged Evidence

The repository already includes the recorded Paper10 result artifacts under
`paper10_geojepa_mpc/experiments/results/` and checkpoints under
`paper10_geojepa_mpc/experiments/checkpoints/`. Re-running the full commands
with the same data should reproduce the reported result structure and metrics,
subject to normal CPU/GPU floating-point and library-version variation.
