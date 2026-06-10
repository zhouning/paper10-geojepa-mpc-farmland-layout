# Dongxing Low-Label-Budget Family Result

Date: 2026-06-10

This note extends the single-init low-label-budget pilot to three
initialization seeds. It tests whether Bishan-initialized transfer helps when
Dongxing real-environment return labels are scarce.

The experiment uses the existing `50x16/h5` Dongxing return-label file and
trains on the first `5`, `10`, or `20` labeled states:

- `reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_50x16_h5_seed3060.npz`

For each budget, the run compares:

- transfer init seeds: `3035`, `3036`, `3037`
- scratch init seeds: `3035`, `3036`, `3037`
- training seed: `3062`
- rollout seeds: `0-4`

All 18 rollout JSON files report `complete=true`.

## Training Setup

All low-label fine-tunes used:

- `--disable-transition-loss`
- `--trainable-scope all`
- `--n-blocks 3711`
- `--epochs 3`
- `--batch-size 4`
- `--n-pairs 8`
- `--pairwise-subsample 16`
- `--pairwise-states 5`, `10`, or `20`
- `--candidate-top-k 3`
- `--candidate-batch-states 1`
- `--candidate-max-states` equal to the budget
- `--seed 3062`
- `--eval-seed 12345`
- `--device cpu`

The transfer runs initialize from:

- `reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed<seed>_1000s_3e.pt`

The scratch runs initialize from:

- `reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed<seed>_1000s_3e.pt`

## Rollout Setup

All checkpoints were evaluated with the tuned Dongxing setting:

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

## Per-Checkpoint Rollout Results

| budget | family | init | mean reward | reward sd | slope pct | cont change | baimu ha |
|---:|---|---:|---:|---:|---:|---:|---:|
| 5 | transfer | 3035 | 54.3024 | 10.0891 | -0.3412 | 0.0251 | 185.4292 |
| 5 | transfer | 3036 | 41.6741 | 10.2477 | -0.3308 | 0.0199 | 135.4480 |
| 5 | transfer | 3037 | 28.9374 | 6.3497 | -0.2404 | 0.0259 | 265.5064 |
| 5 | scratch | 3035 | 52.2392 | 11.3586 | -0.2886 | 0.0296 | 443.4583 |
| 5 | scratch | 3036 | 68.0067 | 10.4682 | -0.2294 | 0.0295 | 435.9544 |
| 5 | scratch | 3037 | 30.8502 | 7.8142 | -0.2858 | 0.0235 | 231.7018 |
| 10 | transfer | 3035 | 56.1703 | 6.9654 | -0.3014 | 0.0207 | 99.6587 |
| 10 | transfer | 3036 | 55.2144 | 6.1096 | -0.3470 | 0.0207 | 65.9424 |
| 10 | transfer | 3037 | 21.6300 | 3.2420 | -0.2646 | 0.0238 | 186.1583 |
| 10 | scratch | 3035 | 49.6388 | 5.3163 | -0.2439 | 0.0266 | 327.3466 |
| 10 | scratch | 3036 | 57.7731 | 12.5904 | -0.2402 | 0.0271 | 351.3803 |
| 10 | scratch | 3037 | 35.9792 | 4.3662 | -0.2317 | 0.0292 | 412.5199 |
| 20 | transfer | 3035 | 58.6847 | 15.4756 | -0.3378 | 0.0223 | 95.4379 |
| 20 | transfer | 3036 | 53.4071 | 8.7870 | -0.3048 | 0.0190 | 47.3046 |
| 20 | transfer | 3037 | 22.0322 | 4.7529 | -0.2663 | 0.0241 | 191.2755 |
| 20 | scratch | 3035 | 53.4007 | 8.6252 | -0.2116 | 0.0267 | 392.0922 |
| 20 | scratch | 3036 | 40.7176 | 6.1340 | -0.2559 | 0.0290 | 401.7203 |
| 20 | scratch | 3037 | 27.2606 | 2.1944 | -0.2578 | 0.0262 | 326.5949 |

## Family-Level Comparison

Each family row aggregates 15 episodes: three init checkpoints times five
rollout seeds.

| budget | family | episodes | reward mean | reward sd | slope pct mean | cont mean | baimu ha mean | checkpoint mean rewards |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 5 | transfer | 15 | 41.6380 | 13.6197 | -0.3041 | 0.0236 | 195.4612 | 54.3024, 41.6741, 28.9374 |
| 5 | scratch | 15 | 50.3654 | 18.2766 | -0.2679 | 0.0275 | 370.3715 | 52.2392, 68.0067, 30.8502 |
| 10 | transfer | 15 | 44.3382 | 17.4339 | -0.3043 | 0.0217 | 117.2531 | 56.1703, 55.2144, 21.6300 |
| 10 | scratch | 15 | 47.7970 | 12.0601 | -0.2386 | 0.0276 | 363.7489 | 49.6388, 57.7731, 35.9792 |
| 20 | transfer | 15 | 44.7080 | 19.4261 | -0.3030 | 0.0218 | 111.3393 | 58.6847, 53.4071, 22.0322 |
| 20 | scratch | 15 | 40.4596 | 12.4674 | -0.2418 | 0.0273 | 373.4691 | 53.4007, 40.7176, 27.2606 |

Transfer minus scratch:

| budget | reward delta | slope delta | cont delta | baimu delta |
|---:|---:|---:|---:|---:|
| 5 | -8.7274 | -0.0362 | -0.0039 | -174.9103 |
| 10 | -3.4588 | -0.0657 | -0.0059 | -246.4958 |
| 20 | 4.2484 | -0.0612 | -0.0055 | -262.1298 |

## Interpretation

The single-init3035 pilot suggested a possible low-label transfer advantage,
but the family-level result is mixed:

- At `5` labels, scratch is higher on mean reward by `8.7274`.
- At `10` labels, scratch is higher on mean reward by `3.4588`.
- At `20` labels, transfer is higher on mean reward by `4.2484`.
- Transfer consistently gives stronger slope reduction.
- Scratch consistently gives stronger contiguity and baimu-area gains.
- The transfer family is highly sensitive to init seed, especially because
  init3037 remains weak across all three budgets.

The defensible conclusion is therefore not "transfer wins at low label
budget." The more accurate conclusion is:

> Low-label Dongxing adaptation exposes a tradeoff: Bishan-initialized transfer
> can improve slope-focused reward at moderate low-label budget, but the effect
> is initialization-sensitive and does not dominate scratch at 5 or 10 labels.

For Paper10, this strengthens the negative-transfer/stress-test framing. The
pipeline is useful because it can measure where transfer helps and where it
does not, not because naive Bishan initialization reliably beats local scratch
adaptation.

## Manuscript Use

This result should be used as a limitation and calibration finding:

- do cite it to show that real Dongxing data were used beyond a single run;
- do use it to explain why transfer claims are bounded;
- do not claim robust cross-region transfer superiority;
- do report that 20-label transfer was better on reward while scratch remained
  stronger at 5/10 labels and on baimu-area outcomes.
