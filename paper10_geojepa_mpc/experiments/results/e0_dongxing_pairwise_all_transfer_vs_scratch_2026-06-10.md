# Dongxing Pairwise-Only All-Parameter Transfer vs Scratch

Date: 2026-06-10

This note records a full-parameter pairwise-only diagnostic for the prepared
Neijiang Dongxing data. It follows the earlier same-scope
`value_head_action_emb` comparison and removes that comparison's main
limitation: the baseline here trains all model parameters instead of freezing
random encoders.

This is still a pairwise training diagnostic, not an MPC rollout result.

## Code Path

The value-head training entry now supports:

- `--disable-transition-loss`

This maps to `disable_transition_loss=True` in `train_e0_smoke_config`. With
this flag, transition MSE is skipped even when `trainable_scope=all`. This lets
the Windows machine train all parameters from Dongxing pairwise labels without
loading the large Dongxing transition arrays into memory. `lambda_sig` must be
zero in this mode.

## Shared Setup

Data:

- `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`
- `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`

Model/training:

| setting | value |
|---|---:|
| n blocks | 3711 |
| trainable scope | `all` |
| transition loss | disabled |
| rank score mode | `value` |
| epochs | 3 |
| batch size | 8 |
| pairwise subsample | 32 |
| n pairs | 8 |
| candidate top-k | 3 |
| eval seed | 12345 |
| device | `cpu` |
| trainable parameters | 280,831 |

Two pairwise budgets were run:

- 100 pairwise states, 3 seeds: 3035, 3036, 3037
- 1000 pairwise states, 3 seeds: 3035, 3036, 3037

Modes:

- `transfer_all`: initialize from Bishan Paper10 seed2028, copy same-shaped
  tensors, skip/reinitialize `action_emb.weight`.
- `scratch_all`: initialize a fresh 3,711-block model and train all parameters
  from Dongxing pairwise labels.

Outputs were written under:

- `reviewer_outputs\dongxing_paper10_pairwise_all_compare\`

The output directory is ignored by git.

## Command Templates

Transfer:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --allow-init-action-emb-mismatch --disable-transition-loss --trainable-scope all --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed<seed>_<states>s_3e.pt --output reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed<seed>_<states>s_3e.json --epochs 3 --batch-size 8 --n-pairs 8 --pairwise-subsample 32 --pairwise-states <states> --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states <states> --seed <seed> --eval-seed 12345 --device cpu
```

Scratch:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --no-init-checkpoint --disable-transition-loss --trainable-scope all --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed<seed>_<states>s_3e.pt --output reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed<seed>_<states>s_3e.json --epochs 3 --batch-size 8 --n-pairs 8 --pairwise-subsample 32 --pairwise-states <states> --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states <states> --seed <seed> --eval-seed 12345 --device cpu
```

## 100-State Results

Lower regret is better. Higher hit rate and ranking accuracy are better.

| mode | seed | best epoch | best top3 regret | final top3 regret | final top3 hit rate | final top1 hit rate | ranking acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| transfer_all | 3035 | 3 | 0.7744942557066679 | 0.7744942557066679 | 0.14 | 0.06 | 0.649402379989624 |
| transfer_all | 3036 | 3 | 0.9294803453981877 | 0.9294803453981877 | 0.13 | 0.03 | 0.6593625545501709 |
| transfer_all | 3037 | 3 | 0.8634465253353119 | 0.8634465253353119 | 0.09 | 0.02 | 0.6434262990951538 |
| scratch_all | 3035 | 3 | 1.003398961648345 | 1.003398961648345 | 0.04 | 0.00 | 0.5498008131980896 |
| scratch_all | 3036 | 3 | 0.9673296265304089 | 0.9673296265304089 | 0.17 | 0.08 | 0.5796812772750854 |
| scratch_all | 3037 | 2 | 0.7317677777260542 | 0.8493515886366367 | 0.12 | 0.07 | 0.5856573581695557 |

Aggregate:

| mode | mean best top3 regret | sd best top3 regret | mean final top3 regret | mean top3 hit rate | mean top1 hit rate | mean ranking acc |
|---|---:|---:|---:|---:|---:|---:|
| transfer_all | 0.8558070421467224 | 0.07777495276121042 | 0.8558070421467224 | 0.12 | 0.03666666666666667 | 0.6507304112116495 |
| scratch_all | 0.9008321219682692 | 0.14752055315955187 | 0.9400267256051302 | 0.11 | 0.05000000000000001 | 0.5717131495475769 |

At 100 states, transfer is better on mean best top3 regret, mean final top3
regret, and ranking accuracy.

## 1000-State Results

| mode | seed | best epoch | best top3 regret | final top3 regret | final top3 hit rate | final top1 hit rate | ranking acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| transfer_all | 3035 | 2 | 0.8428931967653334 | 0.8791710397563874 | 0.255 | 0.108 | 0.7290836572647095 |
| transfer_all | 3036 | 2 | 0.8960553494393826 | 0.9009274816736579 | 0.259 | 0.113 | 0.7310757040977478 |
| transfer_all | 3037 | 2 | 0.9470263436213135 | 0.9639719534739852 | 0.229 | 0.102 | 0.7490040063858032 |
| scratch_all | 3035 | 3 | 0.8499406182765961 | 0.8499406182765961 | 0.253 | 0.107 | 0.7350597381591797 |
| scratch_all | 3036 | 2 | 0.8447585606202483 | 0.8544554159492255 | 0.273 | 0.127 | 0.7211155295372009 |
| scratch_all | 3037 | 2 | 0.9434516778998077 | 0.9564085534773767 | 0.235 | 0.097 | 0.7470119595527649 |

Aggregate:

| mode | mean best top3 regret | sd best top3 regret | mean final top3 regret | mean top3 hit rate | mean top1 hit rate | mean ranking acc |
|---|---:|---:|---:|---:|---:|---:|
| transfer_all | 0.8953249632753432 | 0.05207041546304148 | 0.9146901583013435 | 0.24766666666666667 | 0.10766666666666667 | 0.7363877892494202 |
| scratch_all | 0.8793836189322173 | 0.055545031868695506 | 0.8869348625677328 | 0.25366666666666665 | 0.11033333333333334 | 0.7343957424163818 |

At 1000 states, scratch is slightly better on mean best top3 regret, mean final
top3 regret, and hit rates. Transfer is only slightly higher on ranking
accuracy.

## Interpretation

The 100-state subset suggested a transfer advantage, but the full 1000-state
pairwise diagnostic does not support a robust Dongxing transfer advantage:

- 1000-state mean best top3 regret is better for scratch:
  0.8793836189322173 vs. 0.8953249632753432.
- 1000-state mean final top3 regret is better for scratch:
  0.8869348625677328 vs. 0.9146901583013435.
- 1000-state ranking accuracy is essentially tied:
  0.7343957424163818 scratch vs. 0.7363877892494202 transfer.

The current evidence is therefore useful but negative/neutral for a strong
cross-region transfer claim. It does show that:

- the Paper10 model can be adapted to Dongxing's 3,711-block action space;
- pairwise-only all-parameter training can run on the Windows machine without
  loading Dongxing transition tensors;
- Dongxing scratch training is competitive with, and on regret slightly better
  than, Bishan-initialized transfer at the full prepared pairwise scale.

## Next Step

The next decisive experiment is Dongxing MPC rollout, not more pairwise regret
alone. Use the saved 1000-state all-parameter checkpoints from both modes and
compare rollout reward, slope change, contiguity, and baimu-area change over
multiple seeds.
