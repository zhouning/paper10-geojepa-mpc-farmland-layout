# Dongxing Manuscript Section Draft

Date: 2026-06-10

This document converts the Dongxing/Neijiang cross-region experiments into a
manuscript-ready Results and Discussion asset. It is a drafting document, not a
new experiment. Numeric claims are supported by local result artifacts in this
repository, especially:

- `e0_dongxing_results_synthesis_2026-06-10.md`
- `e0_dongxing_return_label_50x16_family_2026-06-10.md`
- `e0_dongxing_low_label_budget_family_2026-06-10.md`
- `e0_dongxing_planner_value_weight_sweep_2026-06-10.md`
- `e0_dongxing_pairwise_all_transfer_vs_scratch_2026-06-10.md`

## One-Sentence Argument

In cross-region farmland layout planning, we show that the GeoJEPA-MPC workflow
can be adapted to a second real county-level environment and calibrated with
real-environment return labels, supported by Dongxing rollout improvements from
pairwise-only to 50x16 return-label training and by low-label-budget stress
tests, with the boundary that Bishan-initialized transfer does not robustly
outperform Dongxing scratch adaptation.

## Terminology Ledger

| canonical term | first-use definition | use decision |
|---|---|---|
| Dongxing/Neijiang environment | Second real county-level farmland layout environment loaded through the Neijiang cross-region wrapper | Use `Dongxing/Neijiang` when naming the dataset/environment. |
| action-space adaptation | Loading compatible Bishan checkpoint tensors while adapting to Dongxing's 3711-block action space | Use for technical transfer feasibility, not for performance superiority. |
| pairwise-only training | Dongxing fine-tuning with pairwise ranking labels but no real-environment return labels | Use as the pre-return-label baseline. |
| return labels | Multi-step returns computed by real environment rollouts for candidate actions | Distinguish from one-step rewards and pairwise labels. |
| value-filter rollout | MPC rollout with `selector=value_filter` and executable action masks | Use for the evaluated planner setting. |
| `candidate-value-weight` | Weight controlling value-head contribution in candidate filtering | Report as a planner calibration parameter. |
| low-label budget | Training with the first 5, 10, or 20 states from the 50x16 return-label file | Use only for the Dongxing stress test. |

## Draft: Results

### The GeoJEPA-MPC workflow transferred technically to a second real region

We first tested whether the Paper10 workflow could run outside the Bishan
environment used for the main E0 experiments. The Dongxing/Neijiang environment
loaded 3711 blocks from 76376 parcels, with 70806 parcels assigned to blocks.
The initial state had an average farmland slope of `10.5476`, contiguity of
`2.6314`, and 384 baimu-fang patches covering `74341.9 ha`.

The Bishan checkpoint could initialize a Dongxing model despite the larger
action space. Compatible tensors were copied, while `action_emb.weight` was
reinitialized for the 3711 Dongxing actions. This established technical
cross-region reuse, but it did not by itself establish performance transfer.

### Pairwise-only adaptation did not provide a robust transfer advantage

We next compared Bishan-initialized and scratch Dongxing fine-tuning under
pairwise-only training. Both families used 1000 pairwise states, all trainable
parameters, disabled transition loss, and the same Dongxing rollout setting.
Under the tuned `candidate-value-weight=1.0` planner, the transfer family
reached a mean reward of `37.8894`, while the scratch family reached `40.2111`
across 15 rollout episodes.

The pairwise-only result therefore did not support a positive transfer claim.
It showed that cross-region initialization was technically feasible, but local
scratch adaptation remained slightly higher on primary rollout reward.

### Planner calibration was necessary in Dongxing

The Dongxing planner was sensitive to value-head candidate filtering. Reusing
the Bishan default `candidate-value-weight=0.1` was suboptimal in Dongxing.
Pure value candidate filtering with `candidate-value-weight=1.0` improved both
transfer and scratch rollout families.

This result matters for the method claim. A cross-region GeoJEPA-MPC workflow
cannot be treated as a direct checkpoint copy. Planner calibration is part of
the executable method when the action space and landscape structure change.

### Real-environment return labels improved Dongxing rollout reward

We then generated Dongxing return labels directly from the real environment and
used them for value-head fine-tuning. Moving from pairwise-only training to
20x16/h5 and 50x16/h5 return labels improved mean reward for both transfer and
scratch families.

| label type | family | episodes | mean reward | reward sd | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---|---:|---:|---:|---:|---:|---:|
| pairwise_1000s | transfer | 15 | 37.8894 | 14.1353 | -0.3424 | 0.0172 | 5.3018 |
| return_20x16_h5 | transfer | 15 | 41.7733 | 10.7533 | -0.3030 | 0.0220 | 157.2120 |
| return_50x16_h5 | transfer | 15 | 51.6183 | 18.0527 | -0.2905 | 0.0205 | 107.3696 |
| pairwise_1000s | scratch | 15 | 40.2111 | 13.6595 | -0.3053 | 0.0263 | 262.0592 |
| return_20x16_h5 | scratch | 15 | 43.0397 | 15.2827 | -0.2403 | 0.0304 | 460.3064 |
| return_50x16_h5 | scratch | 15 | 55.7324 | 19.9278 | -0.2623 | 0.0236 | 262.3193 |

The largest label set produced the strongest Dongxing family result so far.
The 50x16 return-label checkpoints raised transfer mean reward to `51.6183`
and scratch mean reward to `55.7324`. Scratch still remained higher on the
primary reward metric, so the result supports return-label utility rather than
transfer superiority.

### Low-label-budget tests exposed mixed transfer behavior

Because transfer may be most useful when local labels are scarce, we trained on
the first 5, 10, and 20 states from the existing 50x16 return-label file. Each
family row aggregates three initialization checkpoints and five rollout seeds
per checkpoint.

| budget | family | episodes | reward mean | reward sd | slope pct mean | cont mean | baimu ha mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 5 | transfer | 15 | 41.6380 | 13.6197 | -0.3041 | 0.0236 | 195.4612 |
| 5 | scratch | 15 | 50.3654 | 18.2766 | -0.2679 | 0.0275 | 370.3715 |
| 10 | transfer | 15 | 44.3382 | 17.4339 | -0.3043 | 0.0217 | 117.2531 |
| 10 | scratch | 15 | 47.7970 | 12.0601 | -0.2386 | 0.0276 | 363.7489 |
| 20 | transfer | 15 | 44.7080 | 19.4261 | -0.3030 | 0.0218 | 111.3393 |
| 20 | scratch | 15 | 40.4596 | 12.4674 | -0.2418 | 0.0273 | 373.4691 |

Scratch was higher at 5 and 10 labels, whereas transfer was higher at 20
labels. Transfer consistently produced stronger slope reduction, while scratch
produced stronger contiguity and baimu-area gains. The low-label result is
therefore best interpreted as a stress test showing where transfer may help and
where it does not.

## Draft: Discussion

The Dongxing experiments broaden the Paper10 evidence from a single-region
value-filtering study to a cross-region calibration test. The same code path
loaded a second real environment, adapted the action space, applied executable
action masks, generated real-environment return labels, and evaluated
multi-seed rollouts. This supports the claim that GeoJEPA-MPC is an executable
workflow for real geospatial planning environments, not only a Bishan-specific
script.

The experiments also limit the transfer claim. Bishan-initialized transfer was
technically feasible, but it did not robustly outperform Dongxing scratch
adaptation. Pairwise-only training favored scratch, the 50x16 return-label
family still favored scratch on mean reward, and the low-label-budget test was
mixed. These findings rule out a broad statement that Bishan weights directly
transfer to Dongxing with superior reward.

The more useful interpretation is that Dongxing separates three method
components that would otherwise be conflated. First, action-space adaptation
tests whether checkpoint reuse is technically possible. Second, planner
calibration tests whether value-head filtering remains useful after the
environment changes. Third, return-label generation tests whether local
real-environment supervision improves rollout quality. The positive evidence
is strongest for the second and third components, not for naive initialization
reuse.

The low-label-budget experiment suggests a narrower transfer hypothesis for
future work. Transfer was not better at 5 or 10 labels, but it exceeded scratch
at 20 labels and consistently improved slope reduction. This pattern may
reflect a tradeoff between slope-oriented reward components and area-oriented
baimu outcomes. It should not be generalized without additional regions or
pre-registered label-budget experiments.

For the manuscript, Dongxing should be presented as an external-region stress
test and calibration study. This framing is stronger than a forced positive
transfer narrative because it explains both success and failure. The method can
be moved to a second real environment and improved with local return labels,
but cross-region initialization remains initialization-sensitive and
objective-dependent.

## Section Outline

- Result 1: Dongxing/Neijiang data and action-space adaptation establish
  technical cross-region execution.
- Result 2: pairwise-only transfer does not beat scratch, so initialization
  reuse alone is insufficient.
- Result 3: Dongxing requires planner calibration, with
  `candidate-value-weight=1.0` outperforming the Bishan default.
- Result 4: real-environment return labels improve both transfer and scratch
  rollouts, with 50x16 as the strongest Dongxing family result.
- Result 5: low-label-budget tests are mixed, with scratch higher at 5/10
  labels and transfer higher at 20 labels.
- Discussion: Dongxing supports method portability and calibration value, but
  not robust cross-region transfer superiority.

## Claim-Evidence Map

| claim | evidence | status |
|---|---|---|
| Paper10 runs on a second real region. | Dongxing/Neijiang environment loaded 3711 blocks and 76376 parcels; rollout scripts completed real environment evaluation. | supported |
| Bishan checkpoints can be adapted to Dongxing's action space. | Compatible tensors loaded and `action_emb.weight` was reinitialized for 3711 actions. | supported |
| Pairwise-only transfer is not sufficient. | Pairwise-only transfer mean reward `37.8894`; scratch mean reward `40.2111`. | supported |
| Dongxing planner calibration matters. | `candidate-value-weight=1.0` improved Dongxing rollouts over Bishan default `0.1`. | supported |
| Return labels improve Dongxing rollout reward. | Transfer improved from `37.8894` to `51.6183`; scratch improved from `40.2111` to `55.7324`. | supported |
| Bishan-initialized transfer robustly beats scratch. | Scratch remains higher at 50x16 and at 5/10 low-label budgets. | not supported |
| Transfer may help under some low-label conditions. | Transfer exceeds scratch at 20 labels by `4.2484`, but not at 5 or 10 labels. | partially supported |

## Assumptions or Missing Inputs

- Final figure and table numbering is not fixed.
- These results are descriptive; no formal statistical test has been run.
- Dongxing is one external region. Claims about general cross-region transfer
  require additional regions or a pre-registered multi-region protocol.
- The final manuscript must decide how much Dongxing evidence belongs in the
  main text versus supplementary material.

## Recommended Figure and Table Placement

| item | source artifact | manuscript role |
|---|---|---|
| Table D1 | `e0_dongxing_return_label_50x16_family_2026-06-10.md` | Pairwise-only vs 20x16 vs 50x16 return-label family comparison |
| Table D2 | `e0_dongxing_low_label_budget_family_2026-06-10.md` | Low-label-budget transfer stress test |
| Figure D1 | derived from Table D1 | Reward response to return-label scaling |
| Figure D2 | derived from Table D2 | Label-budget curve for transfer and scratch |
| Supplementary Table D-S1 | `e0_dongxing_pairwise_all_transfer_vs_scratch_2026-06-10.md` | Pairwise-only diagnostics and checkpoint-level metrics |

## Why This Structure

- The Results section follows an evidence ladder: feasibility, baseline,
  calibration, return-label scaling, and transfer-boundary stress test.
- The Discussion addresses the rival interpretation that Dongxing proves
  positive transfer, then replaces it with a bounded calibration claim.
- Numeric claims stay near the local artifacts that support them, and the text
  explicitly marks unsupported transfer-superiority claims.
