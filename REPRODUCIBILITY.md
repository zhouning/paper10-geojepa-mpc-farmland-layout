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

Run the packaged value-label training smoke. This uses the included
`frontier_random050` value-label dataset and the included smoke transition file
only for transition sample-count metadata; the value-head-only path does not
train from transition MSE when `lambda_sig=0`.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\value_head_smoke\value_head.pt --output reviewer_outputs\value_head_smoke\metrics.json --epochs 1 --batch-size 16 --transition-samples 500 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
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
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_score_checkpoint.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --pairwise tool2\pairwise.npz --top-k 5 --batch-states 4 --max-states 1000 --device cpu --output reviewer_outputs\checkpoint_scoring.json
```

## Real-Environment Rollout

Short rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 3 --horizon 3 --top-k 20 --seed 0 --device cpu --output reviewer_outputs\env_rollout_smoke_3step_h3_k20.json
```

Matched five-seed rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --output reviewer_outputs\env_rollout_5seed_h5_k50_executable_mask.json
```

## Packaged Frontier-Random Value-Head Pilot

The repository includes the 2026-06-08 `frontier_random050` pilot artifacts:

```text
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_10x12_h5_seed43_pilot_report_2026-06-08.md
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json
paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt
```

Re-run the included value-head training step from the packaged label dataset:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\frontier_random050_value_head_top4\value_head.pt --output reviewer_outputs\frontier_random050_value_head_top4\metrics.json --epochs 3 --batch-size 16 --transition-samples 6000 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
```

Expected key fields are `transition_loss_enabled=false`,
`ranking_acc` near `0.8143`, and `candidate_top4_regret` near `0.1109`.

Re-running the recorded 100-step rollout requires the full Bishan data:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --output reviewer_outputs\frontier_random050_value_head_top4_5seed_rollout.json
```

The packaged five-seed summary reports mean total reward `65.2566` and sample
standard deviation `5.0037`.

## Expected Packaged Evidence

The repository already includes the recorded Paper10 result artifacts under
`paper10_geojepa_mpc/experiments/results/` and checkpoints under
`paper10_geojepa_mpc/experiments/checkpoints/`. Re-running the full commands
with the same data should reproduce the reported result structure and metrics,
subject to normal CPU/GPU floating-point and library-version variation.
