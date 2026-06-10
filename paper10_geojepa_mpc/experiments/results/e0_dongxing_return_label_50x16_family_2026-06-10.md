# Dongxing 50x16 Return-Label Checkpoint Family

Date: 2026-06-10

This note records the scaled Dongxing return-label experiment requested after
the 20x16 family result. It uses a larger `50x16/h5` real-environment return
label set, fine-tunes all available transfer and scratch initialization seeds,
and evaluates all checkpoints under the tuned Dongxing planner setting.

## Label Generation

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --n-states 50 --candidate-actions 16 --label-horizon 5 --gamma 0.99 --seed 3060 --mask-mode executable --candidate-mode frontier --candidate-score-mode value --candidate-value-weight 1.0 --advance-policy random --continuation-policy random --device cpu --partial-output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.partial.npz --progress-every 5 --output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.npz
```

Generated dataset:

| field | value |
|---|---:|
| states generated | 50 |
| candidate actions | 16 |
| label horizon | 5 |
| candidate score mode | `value` |
| candidate value weight | 1.0 |
| return mean | 1.3721753358840942 |
| return std | 2.4902429580688477 |
| one-step reward mean | 0.27822238206863403 |
| one-step reward std | 0.9816058874130249 |
| return min | -1.5596991777420044 |
| return max | 14.376729011535645 |
| elapsed sec | 587.0558025999926 |

The output file is ignored by git:

- `reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.npz`

## Training

All six fine-tunes used:

- label key: `returns`
- `--disable-transition-loss`
- `--trainable-scope all`
- `--epochs 3`
- `--batch-size 4`
- `--n-pairs 8`
- `--pairwise-subsample 16`
- `--pairwise-states 50`
- `--candidate-top-k 3`
- `--candidate-max-states 50`
- `--seed 3061`

Training diagnostics:

| family | init seed | best epoch | top3 regret | top3 hit | top1 hit | ranking acc |
|---|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 3 | 0.4326827821135521 | 0.80 | 0.28 | 0.747989296913147 |
| transfer | 3036 | 2 | 0.44645790338516234 | 0.76 | 0.28 | 0.7345844507217407 |
| transfer | 3037 | 3 | 0.3175979536771774 | 0.84 | 0.28 | 0.747989296913147 |
| scratch | 3035 | 2 | 0.4326827821135521 | 0.80 | 0.28 | 0.7426273226737976 |
| scratch | 3036 | 2 | 0.4326827821135521 | 0.80 | 0.28 | 0.7399463653564453 |
| scratch | 3037 | 1 | 0.4326827821135521 | 0.80 | 0.28 | 0.737265408039093 |

## Rollout Setup

All six 50x16 return-finetuned checkpoints were evaluated with:

- `--env-source neijiang`
- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--seeds 0-4`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 1.0`

## 50x16 Per-Checkpoint Results

| family | init seed | mean reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 42.2029624356773 | 8.29694003784071 | 30.135791532693 | 52.4728340400537 | -0.265781125444384 | 0.0249180041107273 | 191.877984245307 |
| transfer | 3036 | 73.7477548120498 | 10.0632311480472 | 62.1669493215593 | 88.1624127305843 | -0.334825616900676 | 0.0165391175055758 | 35.3861099617934 |
| transfer | 3037 | 38.9041502576063 | 6.7471787069926 | 28.1151579152552 | 44.6535541703198 | -0.27083289386552 | 0.0200201163248349 | 94.8447519612241 |
| scratch | 3035 | 45.9160068559545 | 8.14641629665818 | 38.4910972411155 | 56.9959817920927 | -0.224619960797872 | 0.0255389863121531 | 327.363996467974 |
| scratch | 3036 | 80.6124862663891 | 9.36573968128097 | 68.067599763707 | 89.6966039939054 | -0.315501083429972 | 0.0206585909826388 | 183.420326726675 |
| scratch | 3037 | 40.6688213499367 | 7.61331690054364 | 33.0814266059665 | 48.9017480939156 | -0.246845524965647 | 0.0244894389294617 | 276.173714952016 |

## Family-Level Comparison

The comparison below uses the same tuned rollout setting,
`candidate-value-weight=1.0`, for all rows.

| label type | family | episodes | mean reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha | checkpoint-mean reward sd |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pairwise_1000s | transfer | 15 | 37.8893925916614 | 14.1352633600858 | 20.4865954196929 | 66.2838055137831 | -0.3424219820891 | 0.0172300695325141 | 5.30178919647058 | 12.9953628799359 |
| return_20x16_h5 | transfer | 15 | 41.7733004189559 | 10.7533323718661 | 28.163896423842 | 61.479114228596 | -0.302996119903207 | 0.021988017667381 | 157.21199984949 | 8.72222561932945 |
| return_50x16_h5 | transfer | 15 | 51.6182891684444 | 18.0526685790304 | 28.1151579152552 | 88.1624127305843 | -0.29047987873686 | 0.020492412647046 | 107.369615389442 | 19.2355264471805 |
| pairwise_1000s | scratch | 15 | 40.2110803350696 | 13.6594641971396 | 22.6068224649475 | 64.5326760839366 | -0.30525395814417 | 0.026323231439775 | 262.059208475224 | 9.41814422770678 |
| return_20x16_h5 | scratch | 15 | 43.0396799073507 | 15.2827215930085 | 25.4384341328677 | 71.3540937033164 | -0.240349301350516 | 0.0303669042725326 | 460.306420471522 | 11.6114935515193 |
| return_50x16_h5 | scratch | 15 | 55.7324381574268 | 19.9277864758067 | 33.0814266059665 | 89.6966039939054 | -0.262322189731164 | 0.0235623387414179 | 262.319346048888 | 21.7058940005209 |

Checkpoint mean rewards:

| label type | family | checkpoint mean rewards |
|---|---|---|
| pairwise_1000s | transfer | 52.4711306494865, 33.6659561685198, 27.531090956978 |
| return_20x16_h5 | transfer | 51.8010938700986, 37.5716466560513, 35.9471607307178 |
| return_50x16_h5 | transfer | 42.2029624356773, 73.7477548120498, 38.9041502576063 |
| pairwise_1000s | scratch | 47.4368950089913, 43.6367909318717, 29.5595550643458 |
| return_20x16_h5 | scratch | 46.3643940953105, 52.6261667172242, 30.1284789095174 |
| return_50x16_h5 | scratch | 45.9160068559545, 80.6124862663891, 40.6688213499367 |

## Interpretation

The larger return-label set substantially improves primary reward for both
families:

- transfer: `37.8894` pairwise -> `41.7733` at 20x16 -> `51.6183` at 50x16;
- scratch: `40.2111` pairwise -> `43.0397` at 20x16 -> `55.7324` at 50x16.

However, the result still does not support transfer superiority:

- scratch remains higher on family mean reward at 50x16:
  `55.7324` vs. transfer `51.6183`;
- the scratch-transfer reward gap grows from `1.2664` at 20x16 to `4.1141` at
  50x16;
- both families become more initialization-sensitive at 50x16, driven by strong
  init3036 results;
- transfer keeps stronger final slope reduction, while scratch keeps stronger
  baimu-area outcomes.

The strongest single run is scratch init3036 after 50x16 return-label
fine-tuning: mean reward `80.6125` over five rollout seeds.

## Paper10 Implication

The most defensible Paper10 Dongxing conclusion is now:

> Scaling real-environment return labels improves Dongxing rollout reward much
> more than pairwise-only training. Under tuned value-only candidate filtering,
> the 50x16 return-label checkpoints are the strongest Dongxing results so far,
> but scratch still outperforms Bishan-initialized transfer on mean reward.

This is a useful result even without a positive transfer claim. It indicates
that Paper10's value-label method has cross-region utility, while naive
Bishan-to-Dongxing initialization is not sufficient to beat Dongxing-specific
training. The next scientific question is whether transfer helps at lower label
budgets or with stronger regularization, not whether the current transfer
checkpoint already wins at 50x16.
