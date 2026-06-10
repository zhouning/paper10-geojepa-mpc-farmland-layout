# Dongxing Low-Label-Budget Transfer Pilot

Date: 2026-06-10

This note records a single-initialization low-label-budget pilot for Paper10's
Dongxing/Neijiang external-region experiment. It uses the already generated
real-environment `50x16/h5` return-label file and trains on only the first
`5`, `10`, `20`, or `50` labeled states.

The purpose is narrow: test whether Bishan-initialized transfer may be useful
when Dongxing return labels are scarce. This is not a multi-seed transfer
claim.

## Inputs

Label file:

- `reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.npz`

Initial checkpoints:

- transfer: `reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt`
- scratch: `reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed3035_1000s_3e.pt`

The training script loads the first `--pairwise-states N` rows from the NPZ, so
no new real-environment label generation was needed.

## Training Setup

All runs used:

- `--disable-transition-loss`
- `--trainable-scope all`
- `--n-blocks 3711`
- `--epochs 3`
- `--batch-size 4`
- `--n-pairs 8`
- `--pairwise-subsample 16`
- `--candidate-top-k 3`
- `--candidate-batch-states 1`
- `--seed 3062`
- `--eval-seed 12345`
- `--device cpu`

Command template:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.npz --init-checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\<family>_all_seed3035_1000s_3e.pt --disable-transition-loss --trainable-scope all --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_low_label_budget\return50_budget<N>_<family>_init3035_train3062_3e.pt --output reviewer_outputs\dongxing_low_label_budget\return50_budget<N>_<family>_init3035_train3062_3e.json --epochs 3 --batch-size 4 --n-pairs 8 --pairwise-subsample 16 --pairwise-states <N> --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states <N> --seed 3062 --eval-seed 12345 --device cpu
```

## Rollout Setup

All checkpoints were evaluated with the tuned Dongxing rollout setting:

- `--env-source neijiang`
- `--prepared-dir D:\test\neijiang_cross_region`
- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--seeds 0-4`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 1.0`

All final rollout JSON files report `complete=true`.

## Results

| budget | family | train top3 regret | train top3 hit | ranking acc | mean reward | reward sd | mean slope change pct | mean cont change | mean baimu area change ha |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | transfer | 0.2982 | 0.80 | 0.6944 | 54.3024 | 10.0891 | -0.3412 | 0.0251 | 185.4292 |
| 5 | scratch | 0.5872 | 0.60 | 0.6389 | 52.2392 | 11.3586 | -0.2886 | 0.0296 | 443.4583 |
| 10 | transfer | 0.0000 | 1.00 | 0.6232 | 56.1703 | 6.9654 | -0.3014 | 0.0207 | 99.6587 |
| 10 | scratch | 0.1491 | 0.90 | 0.6377 | 49.6388 | 5.3163 | -0.2439 | 0.0266 | 327.3466 |
| 20 | transfer | 0.2379 | 0.95 | 0.6908 | 58.6847 | 15.4756 | -0.3378 | 0.0223 | 95.4379 |
| 20 | scratch | 0.2379 | 0.95 | 0.6908 | 53.4007 | 8.6252 | -0.2116 | 0.0267 | 392.0922 |
| 50 | transfer | 0.3245 | 0.80 | 0.7587 | 46.5174 | 6.7512 | -0.3073 | 0.0231 | 77.4760 |
| 50 | scratch | 0.6860 | 0.72 | 0.7480 | 51.4072 | 6.3174 | -0.2527 | 0.0247 | 283.8418 |

Transfer minus scratch:

| budget | reward delta | slope delta | cont delta | baimu delta |
|---:|---:|---:|---:|---:|
| 5 | 2.0632 | -0.0525 | -0.0045 | -258.0291 |
| 10 | 6.5314 | -0.0575 | -0.0059 | -227.6879 |
| 20 | 5.2840 | -0.1262 | -0.0044 | -296.6543 |
| 50 | -4.8898 | -0.0546 | -0.0015 | -206.3658 |

## Interpretation

For this single init seed, transfer has higher mean reward than scratch at
`5`, `10`, and `20` return-label states. At `50` states, scratch becomes higher
again. Transfer also consistently achieves stronger slope reduction, while
scratch consistently produces stronger contiguity and baimu-area gains.

This supports a limited hypothesis:

> Bishan-initialized transfer may help Dongxing reward under very small
> return-label budgets, but the advantage is not monotonic and is not yet a
> family-level conclusion.

This does not overturn the broader Dongxing family result, where scratch still
beats transfer at the 50x16 family mean. It instead identifies a sharper next
experiment: repeat the `5/10/20` low-label-budget grid for init seeds `3036`
and `3037`, then compare family means.

## Operational Note

The 10-label rollout commands were first run with native stderr redirection in
PowerShell. In this harness that wraps native stderr as `NativeCommandError`
even when Python writes the final JSON. The final output files were complete
and were accepted only after checking `complete=true`. Later rollouts used
`-W ignore` and `| Out-Null` to suppress third-party warning and full JSON
stdout noise while preserving progress lines.
