# E0 frontier-random value-head 20x16 scale-up

Date: 2026-06-08

This report records the 20-state, 16-candidate scale-up of the Paper10 E0 `frontier_random` value-label experiment on the Bishan full environment. It follows the 10x12/h5 pilot but lets the value-label monitor select the training top-k.

## Configuration

Label generation used `candidate_mode=frontier_random`, `frontier_fraction=0.5`, executable masks, 20 states, 16 candidate actions per state, horizon 5, gamma 0.99, and seed 44. The run completed in `843.5874` seconds and wrote:

- `paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`
- `paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.partial.npz`

Value-head training initialized from `e0_bishan_rank_seed2028/rank_seed2028.pt`, trained only `value_head`, used 3 epochs, and selected checkpoints by `candidate_top5_regret`.

## Label diagnostics

The monitor result changed relative to the 10x12 pilot: top-5 is now the only gate that passes the default thresholds.

| monitor | decision | candidate top-k regret | candidate top-k overlap | one-step top-k regret |
|---|---|---:|---:|---:|
| top-3 | stop | 0.6507 | 0.3667 | 2.6006 |
| top-4 | stop | 0.4680 | 0.4875 | 2.4626 |
| top-5 | continue | 0.1877 | 0.6300 | 2.4626 |

Top-4 narrowly fails because overlap is `0.4875` and regret is `0.4680`; top-5 passes with overlap `0.6300` and regret `0.1877` while one-step top-k regret remains material at `2.4626`.

| diagnostic | value |
|---|---:|
| residual-to-return state std ratio | 0.9279 |
| one-step top-1 disagreement | 0.7500 |
| candidate top-1 disagreement | 1.0000 |
| candidate Pearson flat | 0.3170 |

## Training result

| metric | value |
|---|---:|
| elapsed sec | 55.6884 |
| transition loss enabled | false |
| trainable parameters | 8,321 |
| ranking accuracy | 0.6382 |
| candidate top-1 hit rate | 0.7500 |
| candidate top-1 regret | 0.5390 |
| candidate top-5 hit rate | 0.9000 |
| candidate top-5 regret | 0.1877 |
| final rank loss | 0.1310 |

Although pointwise ranking accuracy is lower than in the 10x12 run, the top-5 candidate coverage is stronger and rollout behavior is more stable across seeds.

## Rollout gates

20-step seed0 gates used executable masks, `selector=value_filter`, `H=5`, `K=50`, candidate score `blend`, and random independent continuation.

| gate | total reward |
|---|---:|
| blend0.05 seed0 20-step | 22.8675 |
| blend0.10 seed0 20-step | 23.5299 |

Blend0.10 was retained for the 100-step seed set.

## 100-step results

| seed | total reward | slope change % | cont change | baimu ha | elapsed sec |
|---:|---:|---:|---:|---:|---:|
| 0 | 67.7135 | -1.2858 | 0.0220 | -204.7689 | 290.2433 |
| 1 | 70.2252 | -1.2078 | 0.0175 | -195.7613 | 269.5106 |
| 2 | 69.7218 | -1.2288 | 0.0176 | -217.5738 | 266.1078 |
| 3 | 69.8245 | -1.2147 | 0.0168 | -206.9790 | 283.7184 |
| 4 | 69.8677 | -1.3165 | 0.0222 | -211.2367 | 288.8039 |

Aggregate:

| metric | value |
|---|---:|
| total reward mean | 69.4705 |
| total reward std, sample | 1.0004 |
| total reward min | 67.7135 |
| total reward max | 70.2252 |
| slope change mean % | -1.2507 |
| cont change mean | 0.0192 |
| baimu ha mean | -207.2639 |
| mean elapsed sec | 279.6768 |

## Comparison with 10x12/top4

| metric | 10x12/top4 | 20x16/top5 | delta |
|---|---:|---:|---:|
| total reward mean | 65.2566 | 69.4705 | 4.2139 |
| total reward std, sample | 5.0037 | 1.0004 | -4.0034 |
| slope change mean % | -1.2923 | -1.2507 | 0.0415 |
| cont change mean | 0.0198 | 0.0192 | -0.0006 |
| baimu ha mean | -231.3513 | -207.2639 | 24.0873 |

The 20x16/top5 run improves mean total reward by `4.2139` (`6.46%`) and reduces sample standard deviation from `5.0037` to `1.0004`. Seed0 alone is lower than 10x12/top4 by `-1.7158`, but seeds1-4 are substantially more stable.

## Interpretation

This scale-up is stronger than the 10x12 pilot as a reviewer-facing Paper10 experiment because the five-seed rollout is much less seed-sensitive. The key finding is not a larger seed0 maximum; it is a higher and tighter seeds0-4 distribution after increasing label coverage and moving the monitor gate to top-5.

The remaining limitation is label-set size. Twenty states are still a pilot scale, but the run gives a clear design rule for the next experiment: when candidate count increases to 16 or more under `frontier_random0.5`, monitor top-k should be selected from diagnostics rather than fixed at top-4. The next target should be 50x24/h5 on Colab Pro+ or a longer local run, using top-5 or a diagnostics-selected gate.
