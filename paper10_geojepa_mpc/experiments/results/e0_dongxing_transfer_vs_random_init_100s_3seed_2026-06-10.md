# Dongxing Transfer vs Random-Init Control, 100-State Diagnostic

Date: 2026-06-10

This note records a small real-data diagnostic experiment on the prepared
Neijiang Dongxing pairwise file. It extends the earlier 5-state transfer smoke
to 100 pairwise states and 3 training seeds.

This is still not a full Paper10 Dongxing result. It is a controlled diagnostic
for the current value-head/action-embedding transfer path.

## Purpose

The comparison asks whether Bishan-initialized Paper10 weights help the
Dongxing value-head/action-embedding training path when the Dongxing action
space has 3,711 blocks.

Two settings were run with the same training/evaluation budget:

- `transfer`: initialize from the Bishan Paper10 seed2028 checkpoint, copy
  same-shaped weights, and reinitialize only the mismatched
  `action_emb.weight`.
- `random_init`: instantiate a fresh 3,711-block `GeoJEPATransitionModel` and
  train the same parameter subset.

Both settings use `trainable_scope=value_head_action_emb`; therefore both train
only `value_head.*` and `action_emb.*`. The random-init control is not a full
all-parameter from-scratch baseline.

## Shared Configuration

Input data:

- Transition header/source count:
  `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`
- Pairwise labels:
  `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`

Training/evaluation:

| setting | value |
|---|---:|
| n blocks | 3711 |
| pairwise states | 100 |
| candidate actions per state | 50 |
| epochs | 3 |
| batch size | 8 |
| pairwise subsample | 32 |
| n pairs | 8 |
| candidate top-k | 3 |
| candidate max states | 100 |
| eval seed | 12345 |
| device | `cpu` |
| transition loss | disabled |

Seeds: 3035, 3036, 3037.

Outputs were written under
`reviewer_outputs\dongxing_paper10_transfer_compare\`, which is ignored by git.

## Commands

Transfer command template:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --allow-init-action-emb-mismatch --trainable-scope value_head_action_emb --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_paper10_transfer_compare\transfer_value_head_action_seed<seed>_100s_3e.pt --output reviewer_outputs\dongxing_paper10_transfer_compare\transfer_value_head_action_seed<seed>_100s_3e.json --epochs 3 --batch-size 8 --n-pairs 8 --pairwise-subsample 32 --pairwise-states 100 --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states 100 --seed <seed> --eval-seed 12345 --device cpu
```

Random-init control command template:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --no-init-checkpoint --trainable-scope value_head_action_emb --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_paper10_transfer_compare\random_init_value_head_action_seed<seed>_100s_3e.pt --output reviewer_outputs\dongxing_paper10_transfer_compare\random_init_value_head_action_seed<seed>_100s_3e.json --epochs 3 --batch-size 8 --n-pairs 8 --pairwise-subsample 32 --pairwise-states 100 --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states 100 --seed <seed> --eval-seed 12345 --device cpu
```

## Per-Seed Results

Lower regret is better. Higher hit rate and ranking accuracy are better.

| mode | seed | best epoch | best top3 regret | final top3 regret | final top3 hit rate | ranking acc | final rank loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 2 | 0.8203738135099411 | 0.923442152440548 | 0.13 | 0.6115537881851196 | 0.0880676805973053 |
| transfer | 3036 | 1 | 0.9550471837818623 | 1.0281497148424388 | 0.07 | 0.6474103331565857 | 0.09186354279518127 |
| transfer | 3037 | 1 | 0.8425589047372342 | 0.9263275222480297 | 0.09 | 0.649402379989624 | 0.1190543919801712 |
| random_init | 3035 | 1 | 1.0294390115886927 | 1.055918530970812 | 0.04 | 0.5398406386375427 | 0.11077816784381866 |
| random_init | 3036 | 3 | 0.9598211069405079 | 0.9598211069405079 | 0.14 | 0.56175297498703 | 0.09276045113801956 |
| random_init | 3037 | 2 | 0.7453986147791147 | 0.810794432759285 | 0.13 | 0.5756971836090088 | 0.07274412363767624 |

## Aggregate Results

| mode | mean best top3 regret | sd best top3 regret | mean final top3 regret | mean final top3 hit rate | mean ranking acc | mean final rank loss |
|---|---:|---:|---:|---:|---:|---:|
| transfer | 0.8726599673430124 | 0.07220654154989861 | 0.9593064631770055 | 0.09666666666666668 | 0.6361221671104431 | 0.09966187179088593 |
| random_init | 0.9115529111027718 | 0.14804425285031553 | 0.9421780235568683 | 0.10333333333333333 | 0.5590969324111938 | 0.09209424753983815 |

## Interpretation

The transfer path has better mean best-checkpoint top3 regret:

- transfer mean best top3 regret: 0.8726599673430124
- random-init mean best top3 regret: 0.9115529111027718
- absolute improvement: 0.0388929437597594

The transfer path also has higher mean ranking accuracy:

- transfer mean ranking accuracy: 0.6361221671104431
- random-init mean ranking accuracy: 0.5590969324111938
- absolute improvement: 0.0770252346992493

However, this is not a clean positive result:

- Random-init seed3037 beats all transfer seeds on best top3 regret.
- Mean final-epoch top3 regret is slightly better for random-init than transfer.
- Top3 hit rates are low in both settings.
- The control is same-scope random initialization, not a full all-parameter
  from-scratch baseline.

The current evidence supports a narrow claim only: the Bishan transfer path is
dimension-compatible with Dongxing and shows a modest average advantage on the
selected best-checkpoint metric in this 100-state diagnostic. It does not yet
support a full Dongxing Paper10 cross-region transfer claim.

## Next Required Evidence

Before this can be used as a paper claim, Paper10 needs:

1. A larger Dongxing pairwise run, preferably all 1,000 prepared pairwise
   states if CPU/memory permits.
2. A true all-parameter Dongxing baseline or an explicitly pairwise-only
   all-parameter training mode.
3. Dongxing MPC rollout evaluation using 3,711-block checkpoints.
4. Multi-seed rollout summaries for transfer and the selected baseline.
