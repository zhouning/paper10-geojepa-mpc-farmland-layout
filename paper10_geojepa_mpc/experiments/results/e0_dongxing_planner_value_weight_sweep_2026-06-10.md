# Dongxing Planner Value-Weight Sweep

Date: 2026-06-10

This note tests whether the Dongxing transfer rollout weakness was partly a
planner candidate-filter issue rather than only a training issue. The earlier
Dongxing rollouts reused the Bishan candidate filter setting:

- `--candidate-score-mode blend`
- `--candidate-value-weight 0.1`

In the current implementation, `candidate-value-weight` affects only the
candidate filtering stage that chooses the top-k actions for MPC evaluation.
The final selected action is still chosen by the horizon-5 reward rollout among
those candidates. A weight of `1.0` is therefore equivalent to using the value
head for candidate filtering, while still using reward rollout for final
selection.

## Source Data

Committed summary table:

- `paper10_geojepa_mpc/experiments/results/e0_dongxing_planner_value_weight_sweep_2026-06-10.csv`

Ignored rollout JSONs:

- `reviewer_outputs\dongxing_rollout_compare\*_w100_seeds0-4_100step.json`
- `reviewer_outputs\dongxing_rollout_compare\transfer_all_seed3036_1000s_h5_k50_w*_seeds0-4_100step.json`

All runs used:

| setting | value |
|---|---:|
| environment source | `neijiang` |
| prepared dir | `D:\test\neijiang_cross_region` |
| rollout seeds | `0-4` |
| rollout steps | 100 |
| horizon | 5 |
| top-k | 50 |
| mask mode | `executable` |
| selector | `value_filter` |
| candidate score mode | `blend` |
| device | `cpu` |

## Single-Checkpoint Sweep

First, transfer checkpoint seed3036 was evaluated across six candidate
value-weight settings. The default `0.1` result is the previously saved family
rollout; the other rows are new runs.

| weight | mean total reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 28.752348764799535 | 14.1435372544487 | 11.8927419230942 | 44.1330120216875 | -0.25683233697344093 | 0.0164254165391176 | 23.214975095307828 |
| 0.05 | 29.38897056789618 | 5.32582426149014 | 21.3602066005101 | 35.8874993207169 | -0.2644062783252611 | 0.016530371277386723 | 22.231742775771618 |
| 0.10 | 29.048102448774028 | 7.41676836077866 | 21.8594603432674 | 41.067889805979 | -0.2639458570124734 | 0.01644290899549574 | 36.47001914041758 |
| 0.20 | 28.173194502774486 | 4.34263458874127 | 20.4833168422822 | 31.0582914607742 | -0.2739895218747146 | 0.016407924082739368 | -24.511338355433942 |
| 0.50 | 28.162343889912314 | 6.03414554975051 | 17.5876993923432 | 32.7205330626602 | -0.29276346431156375 | 0.01679275812305949 | 32.70400013199091 |
| 1.00 | 33.66595616851978 | 5.16688423991419 | 27.7427268611503 | 37.940218035623 | -0.36303966796332154 | 0.01402020378711688 | -4.100173184013367 |

For transfer seed3036, pure value filtering (`w=1.0`) is the best setting in
this sweep by mean reward and by final slope reduction.

## Family-Level Default vs Pure Value

The `w=1.0` setting was then run for all three transfer checkpoints and all
three scratch checkpoints. This gives a fair family-level comparison against
the default `w=0.1` setting.

| mode | weight | episodes | mean total reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha | checkpoint-mean reward sd |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| transfer | 0.10 | 15 | 28.2480931304568 | 7.10161345954682 | 17.3266016889803 | 41.067889805979 | -0.267894266792148 | 0.0141980437602952 | -66.8369450434486 | 6.07911428724422 |
| transfer | 1.00 | 15 | 37.8893925916614 | 14.1352633600858 | 20.4865954196929 | 66.2838055137831 | -0.3424219820891 | 0.0172300695325141 | 5.30178919647057 | 12.9953628799359 |
| scratch | 0.10 | 15 | 35.7007239415846 | 21.897540980278 | 7.13375489766855 | 70.7277540677464 | -0.142499942211908 | 0.0076325417996823 | -100.190494961416 | 24.5270763765022 |
| scratch | 1.00 | 15 | 40.2110803350696 | 13.6594641971396 | 22.6068224649475 | 64.5326760839366 | -0.30525395814417 | 0.026323231439775 | 262.059208475224 | 9.41814422770678 |

Checkpoint mean rewards:

| mode | weight | checkpoint mean rewards |
|---|---:|---|
| transfer | 0.10 | 33.8875933628709, 29.048102448774, 21.8085835797255 |
| transfer | 1.00 | 52.4711306494865, 33.6659561685198, 27.531090956978 |
| scratch | 0.10 | 60.8587691682365, 34.3858944133879, 11.8575082431294 |
| scratch | 1.00 | 47.4368950089913, 43.6367909318717, 29.5595550643458 |

## Interpretation

The default Bishan candidate filter setting was not optimal for Dongxing.

Changing only the candidate filter from `w=0.1` to `w=1.0` improved transfer:

- mean total reward: `28.2481` to `37.8894`;
- final slope change: `-0.2679` to `-0.3424`;
- final contiguity change: `0.0142` to `0.0172`;
- final baimu area change: `-66.8369 ha` to `5.3018 ha`.

The same change also improved scratch:

- mean total reward: `35.7007` to `40.2111`;
- final slope change: `-0.1425` to `-0.3053`;
- final contiguity change: `0.0076` to `0.0263`;
- final baimu area change: `-100.1905 ha` to `262.0592 ha`.

After tuning both sides with `w=1.0`, scratch still has the higher primary
reward (`40.2111` vs. `37.8894`), but the gap is much smaller than under the
default setting (`2.3217` vs. `7.4526`). Transfer has the stronger final slope
reduction, while scratch has stronger final contiguity and baimu-area outcomes.

## Paper10 Implication

This changes the Dongxing story from a simple negative transfer result to a
more useful systems finding:

1. Cross-region performance is sensitive to planner candidate filtering, not
   only to checkpoint initialization.
2. The Bishan-tuned `candidate-value-weight=0.1` should not be reused as a
   default Dongxing setting.
3. Value-head-only candidate filtering is a strong Dongxing baseline for both
   transfer and scratch.
4. Transfer is not yet better than tuned scratch on primary reward, so the
   paper should not claim transfer superiority.

The next technical step should be a Dongxing adaptation target that is aligned
with the real environment reward, followed by evaluation under `w=1.0`. A
baimu-aware value target is more likely to matter now than another
pairwise-only checkpoint at the old planner setting.
