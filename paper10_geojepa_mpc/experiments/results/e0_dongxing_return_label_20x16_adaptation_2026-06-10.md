# Dongxing 20x16 Return-Label Adaptation Pilot

Date: 2026-06-10

This note records the first end-to-end Dongxing return-label adaptation pilot:
generate real-environment return labels, fine-tune transfer and scratch
checkpoints, then evaluate both with tuned Dongxing rollout settings.

This is a pilot, not a final family-level result. It uses one generated label
set and one initialization seed from each family.

## Label Generation

Label command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --n-states 20 --candidate-actions 16 --label-horizon 5 --gamma 0.99 --seed 3050 --mask-mode executable --candidate-mode frontier --candidate-score-mode value --candidate-value-weight 1.0 --advance-policy random --continuation-policy random --device cpu --partial-output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_20x16_h5_seed3050.partial.npz --progress-every 5 --output reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_20x16_h5_seed3050.npz
```

Generated dataset:

| field | value |
|---|---:|
| states generated | 20 |
| candidate actions | 16 |
| label horizon | 5 |
| candidate score mode | `value` |
| candidate value weight | 1.0 |
| return mean | 1.4714958667755127 |
| return std | 2.929447650909424 |
| one-step reward mean | 0.3125666379928589 |
| one-step reward std | 1.0243629217147827 |
| return min | -1.657371997833252 |
| return max | 19.178762435913086 |
| elapsed sec | 258.9026255000208 |

The label file contains `returns`, `one_step_rewards`, and `candidate_scores`.
The return distribution is much wider than the one-step reward distribution,
so this label set captures multi-step real-environment reward information.

## Fine-Tuning

Both runs used:

- `--disable-transition-loss`
- `--trainable-scope all`
- `--epochs 3`
- `--batch-size 4`
- `--n-pairs 8`
- `--pairwise-subsample 16`
- `--pairwise-states 20`
- `--candidate-top-k 3`
- `--candidate-max-states 20`
- `--seed 3051`

Initial checkpoints:

| run | init checkpoint |
|---|---|
| return transfer | `transfer_all_seed3035_1000s_3e.pt` |
| return scratch | `scratch_all_seed3035_1000s_3e.pt` |

Training metrics:

| run | label key | best epoch | top3 regret | top3 hit | top1 hit | ranking acc | elapsed sec |
|---|---|---:|---:|---:|---:|---:|---:|
| return transfer | `returns` | 1 | 0.5632428348064422 | 0.85 | 0.10 | 0.5921052694320679 | 2.8856965000159107 |
| return scratch | `returns` | 2 | 0.5632428348064422 | 0.85 | 0.75 | 0.6118420958518982 | 2.9532315999967977 |

## Rollout Evaluation

Both return-finetuned checkpoints were evaluated with the tuned Dongxing
rollout setting:

- `--env-source neijiang`
- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--seeds 0-4`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 1.0`

The table also includes the corresponding seed3035 pairwise checkpoints under
the same rollout setting for context.

| run | mean reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|
| pairwise transfer3035 w100 | 52.47113064948655 | 14.674065792341 | 35.9202801885486 | 66.2838055137831 | -0.3928646459340194 | 0.014632439760353399 | -129.63938243141413 |
| return transfer3051 w100 | 51.801093870098626 | 5.79477309692342 | 46.3625936955055 | 61.479114228596 | -0.31530105237584644 | 0.02389469541260336 | 171.6780498689437 |
| pairwise scratch3035 w100 | 47.43689500899132 | 12.4597842074668 | 35.1939335673135 | 64.5326760839366 | -0.36418402869515426 | 0.024664363493243524 | 102.9601026052928 |
| return scratch3051 w100 | 46.36439409531053 | 13.234416852097 | 26.8685138222875 | 59.1297344130002 | -0.24284558623790822 | 0.03077797699742 | 479.52022835369587 |

Per-seed rewards:

| run | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---:|---:|---:|---:|---:|
| pairwise transfer3035 w100 | 35.9202801885486 | 66.2838055137831 | 37.3183136719915 | 63.2794902739126 | 59.553763599197 |
| return transfer3051 w100 | 51.0708634743785 | 51.5272300083016 | 46.3625936955055 | 48.5656679437115 | 61.479114228596 |
| pairwise scratch3035 w100 | 38.0131815744769 | 56.0301206230252 | 64.5326760839366 | 35.1939335673135 | 43.4145631962044 |
| return scratch3051 w100 | 52.7585777055128 | 59.1297344130002 | 38.8966785815626 | 54.1684659541895 | 26.8685138222875 |

## Interpretation

The 20x16 return-label pilot does not improve mean reward over the best
seed3035 pairwise-transfer checkpoint, but it changes the behavior in a useful
way.

For transfer:

- mean reward is nearly preserved: `52.4711` to `51.8011`;
- reward sd drops strongly: `14.6741` to `5.7948`;
- final baimu area changes from `-129.6394 ha` to `171.6780 ha`;
- final contiguity improves from `0.0146` to `0.0239`;
- final slope reduction weakens from `-0.3929` to `-0.3153`.

For scratch:

- mean reward decreases slightly: `47.4369` to `46.3644`;
- final baimu area improves strongly: `102.9601 ha` to `479.5202 ha`;
- final contiguity improves from `0.0247` to `0.0308`;
- final slope reduction weakens from `-0.3642` to `-0.2428`.

Within this pilot, return-finetuned transfer outperforms return-finetuned
scratch on mean reward (`51.8011` vs. `46.3644`) and reward stability. Scratch
has stronger final baimu and contiguity outcomes, while transfer has stronger
final slope reduction.

## Paper10 Implication

The return-label route is now technically viable and produces different
planning behavior from pairwise-only training. The result is not yet a final
positive transfer claim because it is only one label set and one initialization
seed. It does, however, justify scaling the return-label experiment:

1. generate a larger Dongxing value-label set, at least `50x16/h5`;
2. train all three transfer and scratch seeds on return labels;
3. evaluate all checkpoints under `candidate-value-weight=1.0`;
4. report reward and final physical metrics separately, because return labels
   trade slope, contiguity, and baimu outcomes differently.
