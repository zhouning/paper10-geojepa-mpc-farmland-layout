# Paper10 Integrated Manuscript Scaffold with Dongxing Evidence

Date: 2026-06-10

This scaffold updates the earlier E0 `frontier_random050` manuscript map with
the Dongxing/Neijiang real-environment experiments. It is intended as the
current writing spine for Paper10. It does not replace the detailed result
notes; it tells the paper-level story those notes support.

## One-Sentence Argument

In constrained farmland layout planning, we show that monitor-gated
GeoJEPA-MPC value filtering can improve real-environment rollouts and can be
calibrated in a second county-level environment, supported by the Bishan
20x16/top5 value-label result, Dongxing return-label scaling, and low-label
transfer stress tests, with the boundary that direct 50-state Bishan scale-up
and naive Bishan-to-Dongxing transfer are not robustly supported.

## Terminology Ledger

| canonical term | first-use definition | use decision |
|---|---|---|
| GeoJEPA-MPC | JEPA-regularized geospatial world-model planning with model-predictive candidate selection | Use as the method family name. |
| value label | Multi-step return label for candidate actions | Distinguish from one-step reward and pairwise labels. |
| monitor gate | Candidate-quality diagnostic rule that decides whether a label set should be trained | Use for Bishan label selection and 50-state boundary. |
| value filter | Learned scalar head used to filter candidate actions before MPC rollout scoring | Use for the learned planning module. |
| executable mask | Action mask that removes infeasible swaps before candidate selection | Use as a technical reproducibility condition. |
| Bishan E0 | Main Paper10 environment and `frontier_random050` value-label evidence | Use as the primary positive validation setting. |
| Dongxing/Neijiang | Second real county-level environment used for cross-region stress testing | Use as external-region evidence, not as a pure transfer benchmark. |
| return-label scaling | Increasing real-environment return labels from pairwise-only to 20x16 and 50x16 in Dongxing | Use for local calibration evidence. |

## Title Candidates

1. **Monitor-gated value filtering for GeoJEPA-MPC farmland layout planning**
2. GeoJEPA-MPC value filtering with cross-region calibration for farmland layout planning
3. Monitor-gated return labels calibrate GeoJEPA-MPC in real farmland planning environments
4. Bounded cross-region calibration of GeoJEPA-MPC value filtering for farmland layout planning
5. Real-environment return labels for GeoJEPA-MPC farmland layout optimization

Most defensible current title: **Monitor-gated value filtering for GeoJEPA-MPC
farmland layout planning**. It keeps the paper centered on the validated method
claim and avoids implying robust cross-region transfer superiority.

## Draft Abstract

Constrained farmland layout planning requires sequential decisions that improve
long-horizon spatial outcomes while respecting executable swap constraints.
World-model planners can score candidate actions, but one-step reward signals
do not necessarily provide the multi-step rankings needed for stable planning.
Here we evaluate a monitor-gated value-filtering workflow for GeoJEPA-MPC in
real county-level farmland environments. In the Bishan E0 environment, a
20-state, 16-candidate, five-step label set selected a top-5 training gate and
produced a five-seed 100-step mean reward of `69.4705`, improving on the
10x12/top4 pilot (`65.2566`) while reducing seed-level reward variation. Direct
50-state Bishan label extensions failed the monitor gate, defining a candidate
proposal boundary rather than a scale-up success. In the Dongxing/Neijiang
environment, the same workflow adapted to a 3711-block action space, required
planner recalibration to `candidate-value-weight=1.0`, and improved both
transfer and scratch families when real-environment return labels were scaled
to 50x16. The strongest Dongxing family result was scratch with 50x16 return
labels (`55.7324` mean reward), while low-label transfer tests were mixed.
These results support a bounded claim: monitor-gated return labels can improve
and diagnose GeoJEPA-MPC planning in real geospatial environments, but
cross-region initialization remains calibration-sensitive and should not be
claimed as robustly superior to local adaptation.

## Full Manuscript Architecture

### 1. Introduction

**Paragraph 1: field stake.** Farmland layout planning is a constrained
sequential decision problem in which local parcel or block swaps can change
slope, contiguity, and area-related outcomes over many steps.

**Paragraph 2: technical bottleneck.** A one-step world-model reward is not a
complete planning target when the planner must select actions for long-horizon
spatial outcomes under executable constraints.

**Paragraph 3: method gap.** Prior learned planning routes can score
candidates, but they need a mechanism for deciding whether multi-step labels
are trainable and whether learned value filtering remains useful after the
environment changes.

**Paragraph 4: present study.** This paper tests monitor-gated value labels for
GeoJEPA-MPC, first in Bishan as the main validation environment and then in
Dongxing/Neijiang as an external-region calibration and transfer stress test.

Chosen introduction variant: **pipeline-version**. The contribution is a
workflow with several dependent modules: value-label generation, monitor gate,
value-head training, executable masks, and external-region calibration.

### 2. Methods

**Task formulation.** Define state features, global features, block-level
actions, executable masks, candidate sets, return horizon, and 100-step rollout
evaluation.

**GeoJEPA-MPC model and planner.** Describe the transition model, reward/value
heads, checkpoint loading, candidate filtering, and MPC rollout scoring.

**Monitor-gated value-label generation.** Define candidate actions, returns,
one-step rewards, candidate regret, candidate overlap, one-step regret, and the
rule that training proceeds only when the monitor gate passes.

**Bishan E0 protocol.** Specify `frontier_random050`, the 10x12/top4 pilot, the
20x16/top5 scale-up, the GPKG reproduction route, and the 50-state monitor
diagnostics.

**Dongxing/Neijiang protocol.** Specify the Neijiang cross-region wrapper,
3711-action model adaptation, pairwise-only baselines, planner value-weight
sweep, return-label generation, and low-label-budget tests.

**Evaluation and reporting.** Report rollout mean reward, reward standard
deviation, final slope change, contiguity change, baimu-area change, and
checkpoint-level variability.

### 3. Results

**Result 1: Bishan monitor gate selected trainable value-label targets.**
The 10x12/h5 pilot selected top-4, and the 20x16/h5 scale-up selected top-5.
The 20x16/top5 labels had candidate regret `0.1877`, candidate overlap
`0.6300`, and one-step regret `2.4626`.

**Result 2: Bishan 20x16/top5 improved reward and rollout stability.**
Under executable masks and value-filter planning, mean reward increased from
`65.2566` at 10x12/top4 to `69.4705` at 20x16/top5. Sample standard deviation
fell from `5.0037` to `1.0004`, and the minimum seed reward increased from
`57.9750` to `67.7135`.

**Result 3: Bishan 50-state labels defined a scale-up boundary.**
The macOS `50x24/h5 seed45` and Windows seed46 50-state label sets failed
default and post-hoc monitor checks. These rows should be reported as boundary
evidence, not trained as positive scale-up evidence.

**Result 4: Dongxing established cross-region execution and planner
calibration.** The Dongxing/Neijiang environment loaded 3711 blocks from 76376
parcels. Bishan checkpoints could initialize Dongxing models by copying
compatible tensors and reinitializing the action embedding. Dongxing rollouts
required `candidate-value-weight=1.0`, not the Bishan default `0.1`.

**Result 5: Dongxing return labels improved both transfer and scratch
families.** In Dongxing, pairwise-only transfer reached `37.8894` mean reward
and pairwise-only scratch reached `40.2111`. Scaling real-environment return
labels to 50x16 increased these means to `51.6183` and `55.7324`,
respectively.

**Result 6: Dongxing low-label transfer was mixed.** With 5, 10, and 20 label
states, scratch was higher at 5 and 10 labels, whereas transfer was higher at
20 labels. Transfer consistently gave stronger slope reduction, while scratch
gave stronger contiguity and baimu-area gains.

### 4. Discussion

**Central advance.** The strongest paper-level contribution is not a universal
transfer claim. It is a monitor-gated workflow for training and auditing a
GeoJEPA-MPC value filter in real constrained farmland planning environments.

**Why the monitor matters.** The Bishan 50-state failures show that larger
label sets are not automatically better. A candidate-quality gate prevents
training on labels that do not preserve useful multi-step ranking information.

**Why Dongxing matters.** Dongxing demonstrates that the workflow can move to a
second real environment and can diagnose which parts generalize. The data
pipeline, executable masks, action-space adaptation, planner calibration, and
return-label training were all executable; naive initialization superiority was
not.

**Rival explanation and limitation.** A reviewer may ask whether the method is
only fitting one-step reward or whether transfer simply reflects copied Bishan
weights. The monitor diagnostics and Dongxing scratch comparisons argue
against these simplified interpretations. The remaining limitation is that
evidence is still two-region and descriptive; broader transfer claims require a
pre-registered multi-region protocol.

**Future route.** The next technical work should focus on candidate proposal
design and pre-declared monitor thresholds for larger labels, plus additional
external regions if cross-region transfer is to become a primary claim.

### 5. Conclusion

Monitor-gated value labels improved GeoJEPA-MPC rollouts at the validated
Bishan 20x16/top5 scale and enabled a second-region Dongxing calibration study.
The same experiments define the boundary of the current claim: direct 50-state
label scale-up failed the monitor gate, and Bishan-initialized transfer did not
robustly outperform Dongxing scratch adaptation. Paper10 should therefore
claim a reproducible, monitor-gated calibration workflow for real geospatial
planning, not broad transfer superiority.

## Figure and Table Plan

| item | source artifact | manuscript role |
|---|---|---|
| Figure 1 | schematic to draw | GeoJEPA-MPC value-label generation, monitor gate, value-head training, and value-filter MPC |
| Figure 2 | `e0_frontier_random050_seedwise_rewards_2026-06-09.csv` | Bishan 10x12/top4 vs 20x16/top5 reward and stability |
| Figure 3 | `e0_frontier_random050_topk_diagnostics_2026-06-09.csv` | Bishan 50-state monitor-gate failure modes |
| Figure 4 | `e0_dongxing_return_label_family_summary_2026-06-10.csv` | Dongxing pairwise-only to 20x16/50x16 return-label scaling |
| Figure 5 | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv` | Dongxing low-label transfer stress test |
| Table 1 | `e0_frontier_random050_manuscript_tables_2026-06-09.md` | Bishan monitor-selected gates and main rollout comparison |
| Table 2 | `e0_dongxing_return_label_50x16_family_2026-06-10.md` | Dongxing return-label family comparison |
| Table 3 | `e0_dongxing_low_label_budget_family_2026-06-10.md` | Dongxing low-label transfer family comparison |

## Claim-Evidence Map

| claim | evidence | status |
|---|---|---|
| Monitor-gated value labels can train a useful GeoJEPA-MPC value filter in Bishan. | 20x16/top5 mean reward `69.4705`; sample standard deviation `1.0004`; monitor gate passed. | supported |
| Bigger Bishan labels are automatically better. | 50-state label sets failed default and post-hoc monitor checks. | not supported |
| Paper10 can run on a second real county-level environment. | Dongxing/Neijiang environment loaded 3711 blocks and completed return-label training and real rollouts. | supported |
| Dongxing return labels improve rollout reward. | Transfer improved from `37.8894` pairwise-only to `51.6183` at 50x16; scratch improved from `40.2111` to `55.7324`. | supported |
| Bishan-initialized transfer robustly beats Dongxing scratch adaptation. | Scratch remains higher at 50x16 and at 5/10 low-label budgets. | not supported |
| Low-label transfer may help at moderate label budget. | Transfer exceeds scratch at 20 labels by `4.2484`, but not at 5 or 10 labels. | partially supported |
| GeoJEPA-MPC provides a calibration workflow rather than a single fixed checkpoint. | Bishan monitor-gate selection, Dongxing planner weight sweep, return-label scaling, and low-label stress test. | supported |

## Assumptions or Missing Inputs

- Target journal and word limits remain unset.
- Citations still need final verification and placement for the Introduction
  and Methods.
- Figures 1, 4, and 5 still need plotting or drawing.
- Formal statistical tests have not been run; current tables report descriptive
  means and standard deviations.
- The final manuscript must decide whether Dongxing belongs in the main text
  as a full Results subsection or as a shorter external-validation section with
  supplementary tables.

## Why This Structure

- The paper now has one positive method validation setting (Bishan 20x16/top5)
  and one external-region calibration setting (Dongxing).
- The sequence prevents overclaiming: Bishan establishes the value-label
  workflow, and Dongxing tests portability and transfer boundaries.
- Negative results are treated as evidence: Bishan 50-state monitor failures
  and Dongxing scratch superiority both define where the method currently
  stops.
