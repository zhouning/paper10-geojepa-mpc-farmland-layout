# E0 frontier-random value-head pilot

Date: 2026-06-08

This report records the medium E0 value-head pilot using `frontier_random`
candidate labels on the Bishan full environment. The goal was to test whether a
mixed frontier/random label set can provide a useful long-horizon candidate
filter for Paper10 GeoJEPA-MPC.

## Configuration

Label generation:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation `
  --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt `
  --n-states 10 --candidate-actions 12 --label-horizon 5 --gamma 0.99 `
  --seed 43 --mask-mode executable --candidate-mode frontier_random --frontier-fraction 0.5 `
  --advance-policy random --continuation-policy random --progress-every 1 `
  --partial-output paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.partial.npz `
  --output paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz
```

Value-head training:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train `
  --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz `
  --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt `
  --checkpoint-path paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt `
  --output paper10_geojepa_mpc\experiments\results\e0_frontier_random050_value_head_10x12_h5_seed43_top4.json `
  --epochs 3 --batch-size 16 --transition-samples 6000 --pairwise-states 10 `
  --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 `
  --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min `
  --seed 3043 --device cpu
```

Rollout gate:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke `
  --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt `
  --prepared-dir D:\test --rollout-steps 100 --horizon 5 --top-k 50 `
  --seed 0 --device cpu --mask-mode executable --selector value_filter `
  --candidate-score-mode blend --candidate-value-weight 0.1 `
  --output paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_10x12_h5_seed43_top4_blend010_h5_k50_seed0_100step.json
```

The same rollout configuration was then run for `--seeds 1-4`.

## Label diagnostics

The useful monitor gate for this label set was `top_k=4`.

| monitor | decision | candidate top-k regret | candidate top-k overlap | one-step top-k regret |
|---|---|---:|---:|---:|
| top-3 | stop | 0.4923 | 0.3333 | 2.1758 |
| top-4 | continue | 0.4923 | 0.5000 | 1.2916 |
| top-5 | stop | 0.1023 | 0.6400 | 0.0000 |

The top-4 monitor is the best compromise: top-3 is too strict for the current
candidate distribution, while top-5 is too permissive because the one-step
baseline already covers the best return action.

Additional diagnostics show material long-horizon information:

| metric | value |
|---|---:|
| residual-to-return state std ratio | 0.8930 |
| one-step top-1 disagreement | 0.7000 |
| candidate top-1 disagreement | 1.0000 |
| candidate Pearson flat | 0.3455 |

## Training result

The value-head-only training path was fixed before this run. When
`trainable_scope=value_head` and `lambda_sig=0`, the training loop now skips the
transition MSE path and trains from value labels only.

| metric | value |
|---|---:|
| elapsed sec | 26.2719 |
| transition loss enabled | false |
| trainable parameters | 8,321 |
| ranking accuracy | 0.8143 |
| candidate top-1 hit rate | 0.5000 |
| candidate top-4 hit rate | 0.7000 |
| candidate top-4 regret | 0.1109 |
| final rank loss | 0.1052 |

The previous attempt with the old training loop timed out after 900 seconds,
because it repeatedly computed transition MSE even though the value head was the
only trainable module and `lambda_sig=0`.

## Rollout results

All rollouts use executable masks, `selector=value_filter`, `H=5`, `K=50`,
candidate score `blend`, and candidate value weight `0.1`.

| seed | total reward | slope change % | cont change | baimu ha | elapsed sec |
|---:|---:|---:|---:|---:|---:|
| 0 | 69.4293 | -1.3164 | 0.0163 | -267.7441 | 283.0647 |
| 1 | 69.1794 | -1.1503 | 0.0215 | -181.1339 | 299.2397 |
| 2 | 57.9750 | -1.3425 | 0.0213 | -238.5900 | 324.1292 |
| 3 | 67.4951 | -1.3287 | 0.0197 | -224.3452 | 311.8411 |
| 4 | 62.2042 | -1.3234 | 0.0203 | -244.9431 | 263.6414 |

Aggregate:

| metric | value |
|---|---:|
| total reward mean | 65.2566 |
| total reward std, sample | 5.0037 |
| total reward min | 57.9750 |
| total reward max | 69.4293 |
| slope change mean % | -1.2923 |
| cont change mean | 0.0198 |
| baimu ha mean | -231.3513 |
| mean elapsed sec | 296.3832 |
| zero-swap steps | 0 |
| negative zero-swap steps | 0 |

Compared with the prior `frontier_independent` value-head branch
(`20x50_h3_seed2`, value-filter blend0.1, seeds 0-4), the mean total reward
improved from `62.0344` to `65.2566` on the same 100-step seed set.

## Interpretation

This pilot supports scaling `frontier_random` labels rather than continuing the
old frontier-only value-head branch. The main evidence is:

- the top-4 label monitor passes while preserving nontrivial one-step regret;
- value-head-only training is now fast enough to iterate locally;
- the 100-step seed0 rollout reaches `69.4293`, slightly above the previous
  best seed0 value-filter record of `68.0457`;
- the five-seed mean is higher than the prior `frontier_independent` value-head
  branch under the same value-filter blend0.1 gate.

This remains a pilot, not the final Paper10 main experiment. The label dataset
contains only 10 states and 12 candidates per state. The next scale-up should
increase state coverage and candidate diversity before using the result as a
paper-level claim.

## Next scale-up

Recommended next run:

- keep `candidate_mode=frontier_random` and `frontier_fraction=0.5`;
- keep label horizon at 5 and monitor with `top_k=4`;
- expand to at least 30-50 states and 16-24 candidate actions if local time
  permits;
- use the fixed value-head-only training path;
- run the same 100-step seeds 0-4 gate before any larger claim.

The 10x12 label run took about 472 seconds on local Windows CPU. A 50x24 run is
therefore better suited to Colab Pro+ or another GPU/CPU instance with longer
wall-time tolerance, although value-head training itself is no longer the
bottleneck.
