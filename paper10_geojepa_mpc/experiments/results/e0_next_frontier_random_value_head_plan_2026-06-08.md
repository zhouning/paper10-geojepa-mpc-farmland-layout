# E0 next frontier_random value-head plan

Date: 2026-06-08

## Goal

Build the next Paper10 value-head experiment around `frontier_random` labels, partial diagnostics, and top-k filtering. Do not scale the old frontier-only value-head branch.

## Local smoke checks

Run these before any long experiment:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Generate a tiny `frontier_random` label set:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --n-states 5 --candidate-actions 8 --label-horizon 3 --gamma 0.99 --seed 31 --mask-mode executable --candidate-mode frontier_random --frontier-fraction 0.5 --advance-policy random --continuation-policy random --output paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_5x8_h3_seed31.npz
```

Diagnose the tiny label set:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_diagnostics --input paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_5x8_h3_seed31.npz --top-k 3 --output-json paper10_geojepa_mpc\experiments\results\e0_value_label_diagnostics_frontier_random050_rank_seed2028_5x8_h3_seed31_top3.json --output-md paper10_geojepa_mpc\experiments\results\e0_value_label_diagnostics_frontier_random050_rank_seed2028_5x8_h3_seed31_top3.md
```

## Main label generation

Use partial output. On local Windows, this can still be slow because the bottleneck is environment rollback and rollout simulation. Colab Pro+ helps only if the full Paper9 environment and data load there.

Recommended main label run:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --n-states 50 --candidate-actions 24 --label-horizon 5 --gamma 0.99 --seed 41 --mask-mode executable --candidate-mode frontier_random --frontier-fraction 0.5 --advance-policy random --continuation-policy random --progress-every 2 --partial-output paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_50x24_h5_seed41.partial.npz --output paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_50x24_h5_seed41.npz
```

Monitor the partial file every 10 generated states. Use top-3 as the primary continuation rule because top-5 can be too permissive for 12-24 candidates and may already be solved by one-step reward:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_monitor --input paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_50x24_h5_seed41.partial.npz --top-k 3 --min-states 10 --candidate-topk-regret-max 0.75 --candidate-topk-overlap-min 0.40 --one-step-topk-regret-min 0.50 --output-json paper10_geojepa_mpc\experiments\results\e0_value_label_monitor_frontier_random050_50x24_h5_seed41partial_top3.json --output-md paper10_geojepa_mpc\experiments\results\e0_value_label_monitor_frontier_random050_50x24_h5_seed41partial_top3.md
```

Stop or redesign labels if this monitor returns `stop` after at least 10 states. Continue if it returns `continue`. If it returns `wait_more_states`, keep generating.

## Value-head training

Train only `value_head`, initialized from the existing reward-ranking checkpoint. Optimize value ranking and select the checkpoint by candidate top-3 regret:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_50x24_h5_seed41.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_50x24_h5_seed41\value_head_seed3035.pt --output paper10_geojepa_mpc\experiments\results\e0_frontier_random050_value_head_50x24_h5_seed41.json --epochs 10 --batch-size 16 --transition-samples 6000 --pairwise-states 50 --pairwise-subsample 32 --n-pairs 8 --candidate-top-k 3 --candidate-max-states 50 --checkpoint-metric auto --checkpoint-mode min --seed 3035 --device cpu
```

On Colab Pro+, change only `--device cuda` after confirming CUDA is available and the prepared data/checkpoints are present.

## Planner gate

Do not run a five-seed rollout first. Run a single-seed 100-step candidate-filter rollout:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_50x24_h5_seed41\value_head_seed3035.pt --prepared-dir D:\test --rollout-steps 100 --horizon 5 --top-k 50 --seed 0 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.05 --output paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_50x24_h5_seed41_blend005_h5_k50_seed0.json
```

Scale to five seeds only if seed 0 beats:

- Original Paper10 seed0: total reward `70.9543`, slope `-1.2933%`.
- Previous unstable value-filter seed0: total reward `72.0001`.

## Compute note

Local Windows is enough for code tests, label diagnostics, partial monitoring, and small smoke runs. Larger label generation is slow locally and not purely GPU-bound. Colab Pro+ is best used for value-head training and batched scoring once labels exist; use it for label generation only if the Paper9 environment and data can be reproduced there.
