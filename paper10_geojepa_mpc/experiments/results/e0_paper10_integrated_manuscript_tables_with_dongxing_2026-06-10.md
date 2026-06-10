# Paper10 Integrated Manuscript Tables with Dongxing Evidence

Date: 2026-06-10

These tables update the earlier E0 manuscript table package by adding the
Dongxing/Neijiang external-region evidence. They are intended for the
integrated scaffold:

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`

The table package keeps the main manuscript claim bounded: Paper10 demonstrates
monitor-gated value filtering and cross-region calibration, not robust
Bishan-to-Dongxing transfer superiority.

## Table 1. Bishan Monitor-Selected Training Gates

**Caption.** Monitor-gated label selection for the two Bishan value-head
training runs used as primary positive E0 evidence. Candidate regret is the
return gap under the candidate-score top-k set. Candidate overlap measures
agreement with the return-ranked top-k set. One-step regret checks whether the
multi-step label retains signal beyond immediate reward.

| run | states | candidates | horizon | selected top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `10x12/h5 seed43` | 10 | 12 | 5 | 4 | `continue` | 0.4923 | 0.5000 | 1.2916 |
| `20x16/h5 seed44` | 20 | 16 | 5 | 5 | `continue` | 0.1877 | 0.6300 | 2.4626 |

**Use in text.** Use this table to introduce the monitor gate before reporting
rollout performance. The key message is that trainable labels were selected by
diagnostic criteria, not by training on every generated label set.

## Table 2. Bishan Rollout Improvement and Stability

**Caption.** Five-seed 100-step rollout comparison between the Bishan 10x12/top4
pilot and the 20x16/top5 scale-up. Both rows used executable masks,
`selector=value_filter`, horizon 5, global top-k 50, blend candidate scoring,
and candidate value weight 0.1.

| metric | 10x12/top4 | 20x16/top5 | change |
|---|---:|---:|---:|
| Mean total reward | 65.2566 | 69.4705 | +4.2139 |
| Relative mean change | n/a | n/a | +6.46% |
| Sample std | 5.0037 | 1.0004 | -4.0034 |
| Minimum total reward | 57.9750 | 67.7135 | +9.7385 |
| Maximum total reward | 69.4293 | 70.2252 | +0.7959 |
| Mean slope change % | -1.2923 | -1.2507 | +0.0415 |
| Mean continuity change | 0.0198 | 0.0192 | -0.0006 |
| Mean baimu-area change ha | -231.3513 | -207.2639 | +24.0873 |

**Use in text.** This is the main Bishan positive result. Emphasize the
combination of higher mean reward and lower seed sensitivity rather than only
the mean reward gain.

## Table 3. Bishan 50-State Monitor-Gate Boundary

**Caption.** Default monitor outcomes for tested Bishan 50-state label sets.
None of these rows passed top-3, top-4, or top-5. The table reports the
least-bad default top-k per row, which was top-5 in each case.

| run | platform | states | candidates | frontier fraction | seed | top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| `50x24/h5 seed45` | macOS | 50 | 24 | 0.5 | 45 | 5 | `stop` | 1.0241 | 0.4160 | 3.0139 |
| `50x16/h5 seed46` | Windows | 50 | 16 | 0.5 | 46 | 5 | `stop` | 0.3840 | 0.5760 | 1.7764 |
| `50x20/h5 seed46` | Windows | 50 | 20 | 0.5 | 46 | 5 | `stop` | 0.5841 | 0.5320 | 2.6927 |
| `50x24/h5 seed46` | Windows | 50 | 24 | 0.75 | 46 | 5 | `stop` | 1.1009 | 0.2960 | 2.5471 |
| `50x24/h5 seed46` | Windows | 50 | 24 | 1.0 | 46 | 5 | `stop` | 1.3346 | 0.3240 | 2.8339 |

**Use in text.** This table is the main scale-up boundary. It prevents the
paper from claiming that larger Bishan label sets automatically improve the
value filter.

## Table 4. Dongxing Return-Label Scaling

**Caption.** Dongxing/Neijiang rollout performance as training moves from
pairwise-only labels to real-environment return labels. Each row aggregates
three initialization checkpoints and five rollout seeds per checkpoint under
the tuned Dongxing setting `candidate-value-weight=1.0`.

| label type | family | episodes | mean reward | reward sd | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---|---:|---:|---:|---:|---:|---:|
| pairwise_1000s | transfer | 15 | 37.8894 | 14.1353 | -0.3424 | 0.0172 | 5.3018 |
| pairwise_1000s | scratch | 15 | 40.2111 | 13.6595 | -0.3053 | 0.0263 | 262.0592 |
| return_20x16_h5 | transfer | 15 | 41.7733 | 10.7533 | -0.3030 | 0.0220 | 157.2120 |
| return_20x16_h5 | scratch | 15 | 43.0397 | 15.2827 | -0.2403 | 0.0304 | 460.3064 |
| return_50x16_h5 | transfer | 15 | 51.6183 | 18.0527 | -0.2905 | 0.0205 | 107.3696 |
| return_50x16_h5 | scratch | 15 | 55.7324 | 19.9278 | -0.2623 | 0.0236 | 262.3193 |

**Use in text.** This table supports the Dongxing calibration claim. Return
labels improve both families, but scratch remains higher than transfer at the
50x16 family mean.

Figure-ready source:

- `e0_dongxing_return_label_family_summary_2026-06-10.csv`

## Table 5. Dongxing Low-Label Transfer Stress Test

**Caption.** Dongxing low-label-budget comparison using the first 5, 10, or 20
states from the 50x16 return-label file. Each row aggregates three
initialization checkpoints and five rollout seeds per checkpoint.

| budget | family | episodes | reward mean | reward sd | slope pct mean | cont mean | baimu ha mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 5 | transfer | 15 | 41.6380 | 13.6197 | -0.3041 | 0.0236 | 195.4612 |
| 5 | scratch | 15 | 50.3654 | 18.2766 | -0.2679 | 0.0275 | 370.3715 |
| 10 | transfer | 15 | 44.3382 | 17.4339 | -0.3043 | 0.0217 | 117.2531 |
| 10 | scratch | 15 | 47.7970 | 12.0601 | -0.2386 | 0.0276 | 363.7489 |
| 20 | transfer | 15 | 44.7080 | 19.4261 | -0.3030 | 0.0218 | 111.3393 |
| 20 | scratch | 15 | 40.4596 | 12.4674 | -0.2418 | 0.0273 | 373.4691 |

**Use in text.** This table should be used to bound the transfer claim. Scratch
is higher at 5 and 10 labels; transfer is higher at 20 labels. Transfer has
stronger slope reduction, while scratch has stronger contiguity and baimu-area
outcomes.

Figure-ready source:

- `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`

## Table 6. Claim Boundaries for Paper10

**Caption.** Claims supported and not supported by the current integrated
evidence package. This table is not necessarily a main-text table; it is a
writing-control table for the manuscript and response package.

| claim | evidence | status |
|---|---|---|
| Monitor-gated Bishan labels train a useful value filter. | Bishan 20x16/top5 mean reward `69.4705`; sample std `1.0004`; monitor gate passed. | supported |
| Larger Bishan label sets are automatically better. | Tested 50-state label sets failed monitor gates. | not supported |
| Paper10 runs on a second real county-level environment. | Dongxing loaded 3711 blocks and completed training and rollout evaluation. | supported |
| Dongxing return labels improve rollout reward. | Transfer improved from `37.8894` to `51.6183`; scratch improved from `40.2111` to `55.7324`. | supported |
| Bishan-initialized transfer robustly beats Dongxing scratch. | Scratch remains higher at 50x16 and at 5/10 low-label budgets. | not supported |
| Dongxing transfer may help under a moderate low-label budget. | Transfer exceeds scratch at 20 labels by `4.2484`, but not at 5 or 10 labels. | partially supported |

**Use in text.** Keep this table near the writing and reviewer-response assets.
It should guide abstract, conclusion, and limitation wording.

## Placement Recommendation

Main text:

- Table 1 or a compact version in Methods/Results.
- Table 2 as the primary Bishan result.
- Table 4 as the Dongxing external-region result.

Supplementary material:

- Table 3 for 50-state monitor failures, unless the target journal values
  negative boundary results in the main text.
- Table 5 if the main text cannot accommodate the low-label transfer stress
  test.
- Table 6 as an internal claim-audit table or reviewer-response support.

Figure candidates:

- Convert Table 2 into a seed-wise reward and stability plot.
- Convert Table 4 into a grouped reward plot over label type and family.
- Convert Table 5 into a low-label-budget reward curve with transfer and
  scratch families.
