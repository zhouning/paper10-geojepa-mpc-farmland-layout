# Paper10 E0 reviewer smoke verification log

Date: 2026-06-10

This log records a local execution of
`e0_reviewer_smoke_replication_protocol_2026-06-09.md` from the tracked Paper10
repository. It is evidence that the clone-only smoke route works on the current
Windows environment. It is not a full Bishan rerun, a full-data deposit, or
evidence for a passing 50-state result.

## Repository state

| field | value |
|---|---|
| repository | `D:\test\paper10-geojepa-mpc-farmland-layout` |
| branch | `main` |
| verification commit | `534e0f8115a55d5c080bf21bb888657ccd9dd585` |
| Python | `Python 3.13.7` |
| pytest | `pytest 9.0.2` |
| protocol file | `paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_replication_protocol_2026-06-09.md` |

The run used the included small Tool2 smoke data under:

```text
arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/
```

It did not use the external full Bishan `tool2/` data or the prepared GPKG-root
geospatial inputs.

## Commands executed

### 1. Test suite

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result:

```text
108 passed in 7.16s
```

### 2. Smoke data header check

```powershell
D:\adk\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

Observed `transitions.npz` arrays:

| array | dtype | shape |
|---|---|---|
| `actions` | `int64` | `[500]` |
| `block_features` | `float32` | `[500, 30, 17]` |
| `global_features` | `float32` | `[500, 12]` |
| `next_block_features` | `float32` | `[500, 30, 17]` |
| `next_global_features` | `float32` | `[500, 12]` |
| `rewards` | `float32` | `[500]` |

Observed `pairwise.npz` arrays:

| array | dtype | shape |
|---|---|---|
| `actions` | `int64` | `[100, 10]` |
| `rewards` | `float32` | `[100, 10]` |
| `states_bf` | `float32` | `[100, 30, 17]` |
| `states_gf` | `float32` | `[100, 12]` |

### 3. Smoke-scale training

```powershell
D:\adk\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_smoke.py
```

Observed summary:

| config | n_transition_samples | n_pairwise_states | transition_loss_enabled | ranking_acc | final_loss |
|---|---:|---:|---|---:|---:|
| `mse_only` | 500 | 100 | true | 0.59375 | 56.6349983215332 |
| `rank` | 500 | 100 | true | 0.71875 | 43.432884216308594 |
| `rank_sigreg` | 500 | 100 | true | 0.71875 | 43.432952880859375 |

### 4. Optional value-head smoke

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\value_head_smoke\value_head.pt --output reviewer_outputs\value_head_smoke\metrics.json --epochs 1 --batch-size 16 --transition-samples 500 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
```

Observed summary:

| field | value |
|---|---|
| output | `reviewer_outputs\value_head_smoke\metrics.json` |
| checkpoint output | `reviewer_outputs\value_head_smoke\value_head.pt` |
| epochs | 1 |
| device | `cpu` |
| trainable_scope | `value_head` |
| transition_loss_enabled | false |
| n_transition_samples | 500 |
| n_pairwise_states | 10 |
| candidate_top_k | 4 |
| candidate_top4_hit_rate | 0.7 |
| candidate_top4_regret | 0.11092562675476074 |
| ranking_acc | 0.7714285850524902 |
| final_loss | 0.14500871300697327 |

The optional value-head outputs are under ignored `reviewer_outputs/` and are
not part of the archive unless deliberately selected and documented later.

## Interpretation

This execution confirms the reviewer smoke route for the current commit:

- the test suite runs from the packaged repository;
- the small smoke Tool2 data included in Git has the expected shapes;
- smoke-scale training executes on CPU;
- the packaged 10x12 value-label file and rank checkpoint are readable by the
  value-head training entry point.

This execution does not confirm:

- full Bishan value-label regeneration;
- full `tool2/` training or full real-environment rollouts;
- GPKG-root full-data reproduction;
- a passing 50-state result.

Full reruns still require the external data route described in
`DATA_AVAILABILITY.md`.
