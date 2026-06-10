# Dongxing 20x16 Return-Label Checkpoint Family

Date: 2026-06-10

This note extends the Dongxing 20x16 return-label pilot from one initialization
seed to the full available checkpoint family:

- transfer initializations: 3035, 3036, 3037
- scratch initializations: 3035, 3036, 3037

All six return-finetuned checkpoints use the same generated real-environment
label set:

- `reviewer_outputs\dongxing_value_labels\dongxing_frontier_value_20x16_h5_seed3050.npz`

The committed source table is:

- `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_20x16_family_2026-06-10.csv`

## Training Setup

All return-label fine-tunes used:

- label key: `returns`
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

Training metrics:

| family | init seed | best epoch | top3 regret | top3 hit | top1 hit | ranking acc |
|---|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 1 | 0.5632428348064422 | 0.85 | 0.10 | 0.5921052694320679 |
| transfer | 3036 | 2 | 0.5603009343147278 | 0.85 | 0.10 | 0.6315789222717285 |
| transfer | 3037 | 2 | 0.5632428348064422 | 0.85 | 0.75 | 0.6710526347160339 |
| scratch | 3035 | 2 | 0.5632428348064422 | 0.85 | 0.75 | 0.6118420958518982 |
| scratch | 3036 | 1 | 0.5632428348064422 | 0.85 | 0.75 | 0.6315789222717285 |
| scratch | 3037 | 1 | 0.5632428348064422 | 0.85 | 0.10 | 0.6315789222717285 |

## Rollout Setup

All six return-finetuned checkpoints were evaluated with:

- `--env-source neijiang`
- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--seeds 0-4`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 1.0`

This matches the tuned Dongxing planner setting from the value-weight sweep.

## Return-Finetuned Per-Checkpoint Results

| family | init seed | mean reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 51.801093870098626 | 5.79477309692342 | 46.3625936955055 | 61.479114228596 | -0.31530105237584644 | 0.02389469541260336 | 171.6780498689437 |
| transfer | 3036 | 37.571646656051335 | 11.090962049763 | 29.4931099710587 | 56.3256706083077 | -0.3014757180810414 | 0.019224209559627514 | 100.14043048475027 |
| transfer | 3037 | 35.94716073071782 | 7.6116795800306 | 28.163896423842 | 48.1620606755865 | -0.2922115892527325 | 0.02284514802991211 | 199.81751919477702 |
| scratch | 3035 | 46.36439409531053 | 13.234416852097 | 26.8685138222875 | 59.1297344130002 | -0.24284558623790822 | 0.03077797699742 | 479.52022835369587 |
| scratch | 3036 | 52.6261667172242 | 16.8582820382766 | 32.8612746302043 | 71.3540937033164 | -0.23385963249666428 | 0.030148248567805246 | 486.23868814413544 |
| scratch | 3037 | 30.12847890951744 | 4.58771278235045 | 25.4384341328677 | 36.7699750586199 | -0.2443426853169749 | 0.030174487252372463 | 415.1603449167347 |

## Family-Level Comparison

The comparison below uses the same `candidate-value-weight=1.0` rollout setting
for both pairwise-only and return-finetuned checkpoints.

| label type | family | episodes | mean reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha | checkpoint-mean reward sd |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pairwise_1000s | transfer | 15 | 37.8893925916614 | 14.1352633600858 | 20.4865954196929 | 66.2838055137831 | -0.3424219820891 | 0.0172300695325141 | 5.30178919647058 | 12.9953628799359 |
| return_20x16_h5 | transfer | 15 | 41.7733004189559 | 10.7533323718661 | 28.163896423842 | 61.479114228596 | -0.302996119903207 | 0.021988017667381 | 157.21199984949 | 8.72222561932945 |
| pairwise_1000s | scratch | 15 | 40.2110803350696 | 13.6594641971396 | 22.6068224649475 | 64.5326760839366 | -0.30525395814417 | 0.026323231439775 | 262.059208475224 | 9.41814422770678 |
| return_20x16_h5 | scratch | 15 | 43.0396799073507 | 15.2827215930085 | 25.4384341328677 | 71.3540937033164 | -0.240349301350516 | 0.0303669042725326 | 460.306420471522 | 11.6114935515193 |

Checkpoint mean rewards:

| label type | family | checkpoint mean rewards |
|---|---|---|
| pairwise_1000s | transfer | 52.4711306494865, 33.6659561685198, 27.531090956978 |
| return_20x16_h5 | transfer | 51.8010938700986, 37.5716466560513, 35.9471607307178 |
| pairwise_1000s | scratch | 47.4368950089913, 43.6367909318717, 29.5595550643458 |
| return_20x16_h5 | scratch | 46.3643940953105, 52.6261667172242, 30.1284789095174 |

## Interpretation

The 20x16 return-label family result is more informative than the single-seed
pilot:

- Return labels improve transfer mean reward from `37.8894` to `41.7733`.
- Return labels improve scratch mean reward from `40.2111` to `43.0397`.
- Scratch still has the higher family-level mean reward:
  `43.0397` vs. `41.7733`.
- The transfer-scratch reward gap narrows from `2.3217` under pairwise-only
  training to `1.2664` after 20x16 return-label fine-tuning.
- Return labels reduce transfer checkpoint-mean reward sd:
  `12.9954` to `8.7222`.
- Return labels increase final baimu area outcomes for both families, but
  especially scratch.
- Return labels weaken final slope reduction for both families.

This does not establish transfer superiority. It does show that a small
real-environment return-label set moves both families in the intended direction
for reward and baimu-area stability, while preserving a narrow scratch reward
advantage.

## Paper10 Implication

The viable claim is now sharper:

> Dongxing cross-region adaptation is sensitive to both candidate filtering and
> the label target. Under tuned value-only candidate filtering, a 20x16
> real-environment return-label fine-tune improves both transfer and scratch
> families, but scratch remains slightly ahead on primary reward.

For the next experiment, scaling the label set is justified. A `50x16/h5`
return-label set is the next reasonable size because it tests whether the
narrow scratch advantage remains after the return target has more states.
