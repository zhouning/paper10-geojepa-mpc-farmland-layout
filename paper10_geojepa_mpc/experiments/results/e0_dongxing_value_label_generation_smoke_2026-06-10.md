# Dongxing Value-Label Generation Smoke

Date: 2026-06-10

This note records the code path needed for the next Paper10 Dongxing adaptation
step: generating real-environment return labels on the Dongxing/Neijiang
environment using value-head candidate filtering.

## Why This Was Needed

The prepared Dongxing pairwise file contains:

- `states_bf`
- `states_gf`
- `actions`
- `rewards`

It does not contain rollout `returns` or baimu-specific decomposed targets. The
existing pairwise-only experiments therefore trained against one-step reward
labels. To train a Dongxing target aligned with the real environment reward, we
need to generate value-label datasets whose `returns` are computed by actual
environment rollouts.

## Code Changes

`value_label_generation.py` now supports:

- `--env-source neijiang`, loading `county_env_neijiang.py` from
  `--prepared-dir`.
- `--candidate-score-mode reward|value|blend`.
- `--candidate-value-weight`.

The adapter candidate selector can now score candidates by reward, value, or a
blend. `TorchModelMPCAdapter.batch_predict()` also exposes raw `aux["value"]`
when the model provides a value head, so generation can use value-head scores
without changing the final environment-return labels.

The ranking loss was also made robust to all-tie mini-batches by returning a
zero loss that preserves the autograd path. This prevents tiny smoke datasets
from crashing when a sampled pair batch has no non-tie comparisons.

## Real Dongxing Label Smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --n-states 3 --candidate-actions 5 --label-horizon 3 --gamma 0.99 --seed 0 --mask-mode executable --candidate-mode frontier --candidate-score-mode value --candidate-value-weight 1.0 --advance-policy random --continuation-policy random --device cpu --output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_smoke_3x5_h3_seed0.npz
```

Output summary:

| field | value |
|---|---:|
| env source | `neijiang` |
| states generated | 3 |
| candidate actions | 5 |
| label horizon | 3 |
| candidate score mode | `value` |
| candidate value weight | 1.0 |
| return mean | 0.3684900403022766 |
| return std | 1.1936028003692627 |
| one-step reward mean | 0.10371958464384079 |
| one-step reward std | 0.056177251040935516 |
| candidate score mean | 0.5260650515556335 |
| elapsed sec | 44.94182340000407 |

Generated NPZ schema:

| key | shape | dtype |
|---|---:|---|
| `states_bf` | `(3, 3711, 17)` | `float32` |
| `states_gf` | `(3, 12)` | `float32` |
| `actions` | `(3, 5)` | `int64` |
| `returns` | `(3, 5)` | `float32` |
| `one_step_rewards` | `(3, 5)` | `float32` |
| `state_steps` | `(3,)` | `int64` |
| `n_valid_actions` | `(3,)` | `int64` |
| `candidate_scores` | `(3, 5)` | `float32` |

The return mean differs from the one-step reward mean, confirming that the
dataset contains rollout-return labels rather than only one-step reward labels.

## Training Smoke

The generated NPZ was then passed into the existing value-head training entry:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_smoke_3x5_h3_seed0.npz --init-checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --disable-transition-loss --trainable-scope all --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_smoke_train_seed3040.pt --output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_smoke_train_seed3040.json --epochs 1 --batch-size 2 --n-pairs 2 --pairwise-subsample 3 --pairwise-states 3 --candidate-top-k 2 --candidate-batch-states 1 --candidate-max-states 3 --seed 3040 --eval-seed 12345 --device cpu
```

Key result:

| field | value |
|---|---:|
| pairwise label key | `returns` |
| transition loss enabled | `false` |
| trainable scope | `all` |
| n pairwise states | 3 |
| candidate top2 regret | 0.08147652943929036 |
| ranking acc | 0.4000000059604645 |
| elapsed sec | 1.4430252999882214 |

This confirms that Dongxing real-environment return labels can be generated and
consumed by the existing training entry.

## Next Step

The next meaningful experiment is a small but real Dongxing return-label run,
for example `20x16/h5` or `50x16/h5`, using:

- `--env-source neijiang`
- `--candidate-mode frontier`
- `--candidate-score-mode value`
- `--candidate-value-weight 1.0`
- `--mask-mode executable`

Then train transfer and scratch checkpoints on the generated `returns` labels
and evaluate both under the tuned rollout setting `candidate-value-weight=1.0`.
