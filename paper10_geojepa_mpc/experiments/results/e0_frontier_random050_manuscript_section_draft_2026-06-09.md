# E0 frontier_random050 manuscript section draft

Date: 2026-06-09

This draft converts the current E0 `frontier_random050` evidence into
manuscript-style Results and Discussion text. It should be edited after the
final paper structure, figure numbering, and target journal are fixed.

## Draft: Results

### Monitor-gated frontier-random labels trained a useful value filter

We first tested whether frontier-random value labels could provide a usable
long-horizon candidate filter for GeoJEPA-MPC. The pilot label set sampled 10
states and 12 candidate actions per state with executable masks, a five-step
label horizon, and a `frontier_random` candidate mixture. The monitor selected
top-4 as the training gate: top-3 was too restrictive, whereas top-5 was mostly
covered by the one-step reward baseline. Under the selected top-4 gate, the
value-head-only training path reached a candidate top-4 regret of `0.1109` and
completed without transition-loss training.

The trained 10x12/top4 value filter improved the matched 100-step rollout
baseline. Across seeds 0-4, the value-filter rollout achieved a mean total
reward of `65.2566` with sample standard deviation `5.0037`, compared with
`62.0344` for the prior `frontier_independent` value-head branch under the same
rollout setting. This result established that the frontier-random labels
contained usable multi-step information, but the run remained a pilot because
it used only 10 labelled states.

### Increasing label coverage improved reward stability

We next scaled the label set to 20 states and 16 candidate actions per state.
The monitor selected top-5 as the only passing gate. At top-5, candidate regret
was `0.1877`, candidate overlap was `0.6300`, and one-step regret remained high
at `2.4626`. The gate therefore retained candidate coverage while preserving
multi-step signal beyond immediate reward.

The 20x16/top5 value filter improved both mean reward and seed stability. In
the five-seed 100-step rollout, the mean total reward increased from `65.2566`
for 10x12/top4 to `69.4705` for 20x16/top5, a relative gain of `6.46%`. The
sample standard deviation decreased from `5.0037` to `1.0004`, and the minimum
seed reward increased from `57.9750` to `67.7135`. The improvement was therefore
not driven by a single high-reward seed. It reflected a tighter rollout
distribution after increasing label coverage and selecting the monitor gate
from diagnostics.

### Reproduction required the GPKG data root

We audited the 20x16/top5 result on a separate macOS machine after an initial
local reproduction failed. The failure was traced to the prepared-data root:
when both shapefile and GPKG inputs were present, the environment resolved the
shapefile layer first and generated materially different labels. A GPKG-only
root reproduced the packaged 20x16/h5 seed44 label set. The arrays `actions`,
`returns`, `one_step_rewards`, `n_valid_actions`, `state_steps`, and
`states_gf` matched exactly, while `states_bf` and `candidate_scores` matched
within small floating-point tolerance. The reproducible route for this result
therefore uses the GPKG data root.

### The tested 50-state label sets failed the monitor gate

We then tested whether the value-label workflow could be extended directly to
50 labelled states. The macOS `50x24/h5 seed45` run failed the default
top-3/top-4/top-5 monitor checks. Its top-5 candidate regret remained high at
`1.0241`, and the top-5 candidate overlap was only `0.4160`. Post-hoc larger
top-k checks also returned `stop`, because they either retained too much
candidate regret or became mostly explainable by one-step reward.

A Windows CPU ablation grid confirmed that the failure was not confined to one
machine or one seed. Four seed46 label sets were tested: `50x16 f0.5`,
`50x20 f0.5`, `50x24 f0.75`, and `50x24 f1.0`. All failed the default monitor
gate, and all post-hoc top-6/top-8/top-10/top-12 checks also returned `stop`.
The least-bad default row was `50x16 f0.5` at top-5, but its candidate regret
was still `0.3840`, above the `0.2500` threshold. These results prevented
value-head training for all tested 50-state label sets.

## Draft: Discussion

The E0 experiments show that value-head filtering can improve GeoJEPA-MPC
rollouts when the label set passes an explicit candidate-quality gate. The
strongest current evidence is the 20x16/top5 scale-up, which improved the
five-seed reward mean and reduced seed sensitivity relative to the 10x12/top4
pilot. This matters for farmland layout planning because a planning selector
should improve the distribution of outcomes, not only identify one favorable
seed.

The monitor gate was necessary for interpreting the value-head results. In the
pilot, top-4 provided the best compromise between candidate coverage and
one-step reward redundancy. In the 20x16 scale-up, top-5 became the passing
gate. This shift indicates that the usable training target depends on the
candidate distribution and label-set size. A fixed top-k rule would have either
discarded a usable label set or accepted a label set with insufficient
multi-step signal.

The 50-state diagnostics define the present boundary of the method. Directly
increasing state coverage and candidate count did not produce trainable labels
under the current frontier-random proposal. Larger top-k values sometimes
reduced candidate regret, but they also reduced one-step regret enough to weaken
the value-filtering task. This pattern suggests that the next 50-state attempt
should change the candidate proposal strategy or pre-register a different
monitor design, rather than training a value head after a failed gate.

The reproducibility audit also shows that geospatial data resolution is part of
the experimental protocol. The same logical prepared-data directory can produce
different labels if the environment resolves a shapefile rather than the GPKG
layer. The paper should therefore state the GPKG root convention for the
reported E0 scale-up and treat the shapefile/GPKG discrepancy as a
reproducibility boundary, not as a model effect.

Overall, the evidence supports a bounded claim: monitor-gated frontier-random
value labels improved GeoJEPA-MPC rollouts at the validated 20x16 scale, but
the tested 50-state label sets did not support value-head training. The paper
should present 20x16/top5 as the main E0 value-filter result and frame the
50-state runs as stress tests that motivate better candidate proposal design.

## Section outline

- Result 1: 10x12/top4 pilot showed frontier-random labels can train a value
  filter and improve over the prior frontier-independent branch.
- Result 2: 20x16/top5 improved five-seed mean reward and reduced seed
  sensitivity.
- Result 3: macOS reproduction established the GPKG data root as the
  reproducible route for the packaged 20x16 labels.
- Result 4: macOS and Windows 50-state diagnostics failed default and post-hoc
  monitor gates, so no 50-state value head was trained.
- Discussion: the result supports monitor-gated value filtering at 20x16 and
  sets a clear boundary for future 50-state candidate proposal work.

## Figure and table placeholders

- Table E0-1: monitor decisions for 10x12/top4, 20x16/top5, and failed 50-state
  rows.
- Table E0-2: five-seed rollout metrics comparing 10x12/top4 and 20x16/top5.
- Figure E0-1: seed-wise total reward distribution for 10x12/top4 versus
  20x16/top5.
- Figure E0-2: candidate regret and one-step regret across top-k values for the
  50-state diagnostics.
- Supplementary Table E0-S1: macOS GPKG array-level reproduction audit.

## Claim-evidence map

| Claim | Evidence | Status |
|---|---|---|
| Frontier-random labels trained a useful value filter at pilot scale. | 10x12/top4 rollout mean `65.2566`, above prior matched `frontier_independent` mean `62.0344`. | Supported. |
| 20x16/top5 is the current main E0 result. | Mean reward `69.4705`, sample std `1.0004`, selected top-5 monitor gate passed. | Supported. |
| The 20x16/top5 result is reproducible under the GPKG root. | macOS GPKG reproduction matched packaged arrays exactly or within floating-point tolerance. | Supported. |
| 50-state value-head training is not justified by current labels. | macOS seed45 and Windows seed46 default and post-hoc monitors all returned `stop`. | Supported. |
| Direct value-head training is supported for the tested 50-state labels. | No 50-state label set passed the monitor gate. | Not supported. |

## Assumptions or missing inputs

- The final manuscript has not yet fixed figure numbers, table numbers, or
  target journal formatting.
- The prior `frontier_independent` branch can be included either in the main
  text or supplementary comparison, depending on the final narrative scope.
- The paper should not claim 50-state value-head performance until a future
  label set passes the monitor before training.

## Why this structure

- The Results section moves from validation to main result, then to
  reproducibility and stress-test boundary.
- The Discussion interprets the monitor gate and the failed 50-state scale-up
  rather than repeating every metric.
- The draft keeps claims close to measured evidence and explicitly labels the
  unsupported 50-state scale-up claim as out of scope.
