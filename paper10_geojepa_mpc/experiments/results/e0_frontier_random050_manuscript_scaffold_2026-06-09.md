# E0 frontier_random050 manuscript scaffold

Date: 2026-06-09

This scaffold turns the current Paper10 E0 `frontier_random050` evidence into a
full-paper writing map. It is a drafting scaffold, not a new experiment. It
uses the validated 10x12/top4 pilot, the reproducible 20x16/top5 scale-up, the
macOS GPKG audit, and the failed 50-state diagnostics.

## One-sentence argument

In constrained farmland layout planning, we show that monitor-gated
frontier-random value labels can train a GeoJEPA-MPC value filter that improves
and stabilizes long-horizon rollouts, supported by 10x12 and 20x16 value-head
experiments, with the present boundary that all tested 50-state label sets fail
the current monitor gate.

## Terminology ledger

| canonical term | first-use definition | use decision |
|---|---|---|
| GeoJEPA-MPC | JEPA-regularized geospatial world-model planning with model-predictive candidate selection | Use as the method family name. |
| `frontier_random050` | Candidate-label proposal with `candidate_mode=frontier_random` and `frontier_fraction=0.5` | Use exactly for the E0 run family. |
| value label | Multi-step return label for candidate actions | Distinguish from one-step reward. |
| value head | Scalar value-ranking head trained from value labels | State that transition loss is disabled in value-head-only runs. |
| monitor gate | Diagnostic rule that decides whether a label set is usable for training | Use before any training claim. |
| candidate regret | Mean return gap under candidate-score-selected top-k actions | Lower is better. |
| candidate overlap | Fractional agreement between candidate-score top-k and return-ranked top-k actions | Higher is better. |
| one-step regret | Return gap under one-step-reward top-k action selection | Must remain material for labels to add multi-step signal. |
| GPKG root | Prepared-data root that resolves `DLTB_with_slope.gpkg` | Use as the reproducible data-root convention. |

## Title candidates

1. Monitor-gated value filtering for GeoJEPA-MPC farmland layout planning
2. Frontier-random value labels stabilize GeoJEPA-MPC rollouts in constrained farmland layout
3. Bounded scale-up of learned value filtering for geospatial farmland planning
4. GeoJEPA-MPC value filtering improves rollout stability under monitor-gated labels

Most defensible current title: **Monitor-gated value filtering for GeoJEPA-MPC
farmland layout planning**. It avoids claiming 50-state scale-up while naming
the method, mechanism, and application.

## Draft abstract

Constrained farmland layout planning requires search procedures that improve
long-horizon land-use outcomes while respecting executable swap constraints.
World-model planners can score candidate actions, but a one-step reward signal
does not necessarily provide the multi-step ranking needed for stable planning.
Here we evaluate a monitor-gated value-filtering route for GeoJEPA-MPC using
frontier-random multi-step labels. A 10-state, 12-candidate pilot selected a
top-4 training gate and reached a five-seed 100-step mean total reward of
`65.2566`. Scaling the label set to 20 states and 16 candidate actions selected
a top-5 gate with candidate regret `0.1877`, candidate overlap `0.6300`, and
one-step regret `2.4626`. The resulting value filter achieved a mean total
reward of `69.4705`, a `6.46%` improvement over the 10x12/top4 pilot, and
reduced sample standard deviation from `5.0037` to `1.0004`. A macOS audit
reproduced the packaged 20x16 labels under the GPKG data root, establishing the
current reproducible route. Direct 50-state extensions failed the default and
post-hoc monitor gates, indicating that the present candidate proposal does not
support unmodified 50-state value-head training. These results support a
bounded claim: monitor-gated value labels improve GeoJEPA-MPC at the validated
20x16 scale and identify candidate-proposal design as the next scale-up
bottleneck.

## Full manuscript architecture

### 1. Introduction

**Paragraph 1: field stake.** Open with farmland layout as a constrained
sequential planning problem where local land-use swaps affect slope,
continuity, and area-related objectives over many steps.

**Paragraph 2: bottleneck.** Explain that one-step world-model predictions are
not enough for planning if candidate ranking fails to preserve long-horizon
returns. This sets up why value filtering is needed.

**Paragraph 3: prior attempts and gap.** Position the prior
`frontier_independent` and one-step ranking branches as useful but incomplete:
they can support candidate scoring, but they do not by themselves establish a
trainable multi-step candidate gate.

**Paragraph 4: present study.** State that this paper tests a monitor-gated
frontier-random labeling workflow for GeoJEPA-MPC, then preview the evidence
ladder: 10x12 pilot, 20x16 scale-up, GPKG reproduction, and 50-state boundary
diagnostics.

### 2. Methods

**Task formulation.** Define the planning state, executable action mask,
candidate action set, label horizon, and 100-step rollout evaluation.

**GeoJEPA-MPC base model.** Summarize the rank-seed checkpoint and the planning
adapter only to the level needed to understand candidate scoring.

**Frontier-random value labels.** Define `frontier_random050`, candidate
scores, multi-step returns, one-step rewards, and label generation with random
advance and continuation policies.

**Monitor gate.** Specify default top-k checks, thresholds, and the rule that
training proceeds only after `decision=continue`.

**Value-head training.** State that the value-head-only path trains 8,321
parameters, disables transition MSE training, and selects checkpoints by the
candidate top-k metric.

**Rollout evaluation.** Define the shared rollout setting: executable masks,
`selector=value_filter`, horizon 5, global top-k 50, blend candidate-score
mode, candidate value weight 0.1, and seeds 0-4.

**Reproducibility convention.** State the GPKG data-root requirement and the
reason for avoiding roots that resolve shapefiles first.

### 3. Results / experiments

**Result 1: workflow validation.** The value-head-only training path no longer
trains transition MSE when `lambda_sig=0`, and both 10x12 and 20x16 runs train
only the value head.

**Result 2: 10x12/top4 pilot.** The 10x12 label set selected top-4 and reached
mean total reward `65.2566` with sample standard deviation `5.0037`. It
improved over the prior matched `frontier_independent` mean of `62.0344`.

**Result 3: 20x16/top5 main result.** The 20x16 label set selected top-5 with
candidate regret `0.1877`, candidate overlap `0.6300`, and one-step regret
`2.4626`. Its five-seed mean total reward was `69.4705`, with sample standard
deviation `1.0004`.

**Result 4: rollout stability.** Relative to 10x12/top4, 20x16/top5 improved
mean reward by `4.2139` (`6.46%`), reduced sample standard deviation by
`4.0034`, and increased the minimum seed reward from `57.9750` to `67.7135`.

**Result 5: GPKG reproduction.** The macOS GPKG audit reproduced `actions`,
`returns`, `one_step_rewards`, `n_valid_actions`, `state_steps`, and
`states_gf` exactly, with only small floating-point differences in `states_bf`
and `candidate_scores`.

**Result 6: 50-state boundary.** The macOS `50x24/h5 seed45` run and Windows
seed46 rows all failed default gates. Post-hoc larger top-k checks also
returned `stop`; larger top-k values either became too close to one-step reward
or retained excessive candidate regret / weak overlap.

### 4. Discussion

**Central advance.** Interpret the 20x16/top5 result as evidence that learned
value filtering helps when the label set passes a candidate-quality gate.

**Why the gate matters.** Explain that top-k is not a fixed hyperparameter: the
usable gate changed from top-4 to top-5 as label coverage and candidate count
changed.

**Rival explanation.** Address the possibility that the gain is only a one-step
reward effect. The monitor counters this for 20x16/top5 because one-step regret
remained `2.4626`; failed larger top-k 50-state checks show what happens when
one-step regret becomes too small.

**Reproducibility boundary.** Explain that the shapefile/GPKG discrepancy is a
data-resolution boundary, not a model effect.

**Scale-up boundary.** State that the paper does not demonstrate 50-state
value-head scale-up. The current 50-state evidence motivates a redesigned
candidate proposal or pre-registered monitor change.

### 5. Conclusion

Monitor-gated frontier-random value labels improved GeoJEPA-MPC rollouts at
the validated 20x16/top5 scale, increasing mean reward and reducing seed
sensitivity relative to the 10x12/top4 pilot. The same evidence defines the
current boundary: direct 50-state extensions should not be trained until a
pre-declared monitor gate passes.

## Figure and table plan

| item | source artifact | manuscript role |
|---|---|---|
| Figure 1 | method schematic to be drawn | GeoJEPA-MPC value-label and monitor-gate workflow |
| Figure 2 | `e0_frontier_random050_seedwise_rewards_2026-06-09.csv` | Seed-wise 10x12/top4 vs 20x16/top5 reward comparison |
| Figure 3 | `e0_frontier_random050_topk_diagnostics_2026-06-09.csv` | 50-state top-k failure modes |
| Table 1 | `e0_frontier_random050_manuscript_tables_2026-06-09.md`, Table E0-1 | Monitor-selected training gates |
| Table 2 | same, Table E0-2 | Five-seed rollout comparison |
| Supplementary Table S1 | same, Table E0-S1 | macOS GPKG reproduction audit |

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| Frontier-random labels can train a useful value filter at pilot scale. | 10x12/top4 rollout mean `65.2566`, above prior matched `frontier_independent` mean `62.0344`. | supported |
| 20x16/top5 is the current main E0 result. | Mean reward `69.4705`, sample std `1.0004`, selected top-5 monitor gate passed. | supported |
| The 20x16/top5 result improves stability, not only best-case reward. | Sample std fell from `5.0037` to `1.0004`; minimum seed reward rose from `57.9750` to `67.7135`. | supported |
| The 20x16/top5 labels are reproducible under the GPKG data root. | macOS reproduction matched arrays exactly or within floating-point tolerance. | supported |
| Existing 50-state labels should not be trained. | macOS seed45 and Windows seed46 rows failed default and post-hoc monitor checks. | supported |
| Direct value-head training is supported for the tested 50-state labels. | No 50-state label set passed the monitor gate. | not supported |

## Assumptions or missing inputs

- Target journal, word limits, and required abstract structure are not fixed.
- The introduction still needs literature citations and a final related-work
  scope.
- A method schematic is not yet drawn.
- Full paper figures need final styling after the target venue is selected.
- Additional 50-state experiments should be label-only until a monitor gate
  passes.

## Author notes

- Keep the manuscript centered on 20x16/top5 rather than failed 50-state
  training.
- Present 50-state results as a boundary / stress test, not as scale-up
  success.
- Preserve the scope limit in the abstract and conclusion: validated 20x16
  scale, failed 50-state gates.
- The next writing tasks are the method schematic and citations, not training
  failed labels.
