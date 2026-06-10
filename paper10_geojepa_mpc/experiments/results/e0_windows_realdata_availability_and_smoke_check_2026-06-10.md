# Windows Real-Data Availability and Smoke Check

Date: 2026-06-10

This note corrects the earlier working assumption that the Windows machine did
not have full Paper10 real-data inputs available. The Paper10 repository root
does not contain the full data, but usable Bishan real-data inputs are present
under the shared workspace root `D:\test` and can be passed into Paper10 scripts
with absolute paths.

## Local Data Inventory

Usable Bishan prepared inputs:

- `D:\test\tool2\transitions.npz`
  - Size: 1,522,832,889 bytes.
  - Arrays:
    - `block_features`: `(6000, 2600, 17)`, `float32`
    - `global_features`: `(6000, 12)`, `float32`
    - `actions`: `(6000,)`, `int64`
    - `rewards`: `(6000,)`, `float32`
    - `next_block_features`: `(6000, 2600, 17)`, `float32`
    - `next_global_features`: `(6000, 12)`, `float32`
- `D:\test\tool2\pairwise.npz`
  - Size: 127,198,041 bytes.
  - Arrays:
    - `states_bf`: `(1000, 2600, 17)`, `float32`
    - `states_gf`: `(1000, 12)`, `float32`
    - `actions`: `(1000, 50)`, `int64`
    - `rewards`: `(1000, 50)`, `float32`
- `D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg`
  - Layer: `DLTB`
  - Features: 101,657
  - CRS: `EPSG:4326`
  - Geometry: `MultiPolygon`
  - Key fields include `DLBM`, `category`, `slope_mean`, `slope_max`,
    and `slope_pixel_count`.
- `D:\test\townships.json`
  - 13 Bishan township codes.
- `D:\test\results_real\blocks`
  - Contains all 13 township directories referenced by `townships.json`.
  - Each township directory contains `block_features.json`,
    `block_compositions.json`, and `parcel_block_mapping.csv`.

Raw DLTB files found:

- `D:\test\bishan.shp`
  - Features: 101,657
  - CRS: `EPSG:4610`
  - Has `DLBM`; does not have `slope_mean`.
- `D:\test\dongxing.shp`
  - Features: 134,369
  - CRS: `EPSG:2359`
  - Has `DLBM`; does not have `slope_mean`.

Interpretation:

- Bishan is immediately usable for Paper10 real-data validation through
  `--prepared-dir D:\test` and the existing `tool2` `.npz` files.
- Dongxing raw DLTB exists locally, but it is not yet a drop-in Paper10
  prepared root because the local raw shapefile lacks slope fields and block
  preprocessing products. It can support a cross-region experiment after the
  same slope-enrichment and block-preparation pipeline is run for Dongxing.

## Script Compatibility

The following Paper10 entry points expose the needed path overrides:

- `paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke`
  - supports `--prepared-dir`.
- `paper10_geojepa_mpc.experiments.value_label_generation`
  - supports `--prepared-dir`.
- `paper10_geojepa_mpc.experiments.run_e0_value_head_train`
  - supports `--transition-path` and `--pairwise-path`.
- `paper10_geojepa_mpc.experiments.run_e0_score_checkpoint`
  - supports `--pairwise`.

## Smoke Checks Run on Real Bishan Data

### 1. Environment rollout smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --rollout-steps 3 --horizon 3 --top-k 20 --seed 0 --device cpu --mask-mode executable --output reviewer_outputs\realdata_env_rollout_smoke_dtest_seed0.json
```

Result:

- Loaded 52,515 swappable parcels.
- Loaded 13 Bishan townships and 2,600 blocks.
- Built 3,290 cross-township parcel adjacency edges and 511 cross-township
  block edges.
- Completed 3 rollout steps.
- `steps_run`: 3
- `total_reward`: 1.612087030846898
- `terminated`: false
- `truncated`: false

### 2. Value-label generation smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --n-states 2 --candidate-actions 4 --label-horizon 2 --gamma 0.99 --seed 9001 --mask-mode executable --candidate-mode frontier_random --frontier-fraction 0.5 --advance-policy random --continuation-policy random --progress-every 1 --partial-output reviewer_outputs\realdata_label_smoke_seed9001.partial.npz --output reviewer_outputs\realdata_label_smoke_seed9001.npz
```

Result:

- `n_states_generated`: 2
- `candidate_actions`: 4
- `return_mean`: 0.4502553343772888
- `one_step_reward_mean`: 0.34728261828422546
- Output arrays:
  - `states_bf`: `(2, 2600, 17)`, `float32`
  - `states_gf`: `(2, 12)`, `float32`
  - `actions`: `(2, 4)`, `int64`
  - `returns`: `(2, 4)`, `float32`
  - `one_step_rewards`: `(2, 4)`, `float32`
  - `candidate_scores`: `(2, 4)`, `float32`

### 3. Pairwise score smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_score_checkpoint --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --pairwise D:\test\tool2\pairwise.npz --top-k 10 --batch-states 2 --max-states 5 --device cpu --output reviewer_outputs\realdata_pairwise_score_seed2028_max5.json
```

Result:

- `candidate_states`: 5
- `candidate_actions`: 50
- `candidate_top1_hit_rate`: 0.2
- `candidate_top10_hit_rate`: 0.6
- `candidate_top1_regret`: 0.2842618703842163
- `candidate_top10_regret`: 0.08131864070892333

### 4. Minimal value-head training smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\tool2\transitions.npz --pairwise-path D:\test\tool2\pairwise.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\realdata_value_head_train_smoke_seed9101.pt --output reviewer_outputs\realdata_value_head_train_smoke_seed9101.json --epochs 1 --batch-size 2 --n-pairs 2 --pairwise-subsample 4 --pairwise-states 5 --candidate-top-k 3 --candidate-batch-states 2 --candidate-max-states 5 --seed 9101 --eval-seed 9102 --device cpu
```

Result:

- `elapsed_sec`: 2.304683299997123
- `transition_loss_enabled`: false
- `n_pairwise_states`: 5
- `n_transition_samples`: 6000
- `n_trainable_parameters`: 8321
- `ranking_acc`: 0.699999988079071
- `candidate_top3_hit_rate`: 0.4
- `candidate_top3_regret`: 0.19167616367340087

## Warnings Observed

The real-data environment emitted the known spatial-contiguity warning that the
weights matrix is not fully connected and contains disconnected components and
islands. The rollout and label-generation commands still completed. This should
be treated as a dataset/topology property to document, not as evidence that the
real-data pipeline is unavailable.

Several `RuntimeWarning: invalid value encountered in divide` messages also
appeared in `county_env.py` feature construction where zero denominators are
then guarded by `np.where`. The commands completed successfully; these warnings
are worth cleaning up before a polished release log, but they do not block the
real-data smoke runs.

## Conclusion

The Windows machine can run Paper10 real-data experiments using the local
Bishan inputs already present under `D:\test`. The correct operational statement
is:

- Full data is not tracked in the Paper10 git repository.
- Full Bishan real-data inputs are available in the local workspace root.
- Paper10 scripts can consume those inputs without copying them into the repo.
- Dongxing raw DLTB is present, but it still needs Paper10-compatible slope and
  block preprocessing before it can be used as a comparable prepared experiment.

Immediate next experiment:

1. Run the real-data 20x16/h5 value-label generation with `--prepared-dir D:\test`
   and compare it against the packaged `e0_value_labels_frontier_random050_*`
   artifact.
2. If that matches, run the 20x16 value-head training and 100-step rollout from
   the Windows machine as a real-data reproduction, then record seedwise metrics.
3. Start a Dongxing preprocessing task only after the Bishan reproduction path is
   stable, because Dongxing is currently raw DLTB rather than a prepared Paper10
   environment.
