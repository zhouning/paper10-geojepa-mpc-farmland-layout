# E0 frontier_random050 Results and Discussion cited draft

Date: 2026-06-09

This document converts the current E0 `frontier_random050` Results and
Discussion draft into a citation-aware manuscript asset. Quantitative claims
are supported by local result artifacts in this repository, especially
`e0_frontier_random050_manuscript_tables_2026-06-09.md`, the tracked CSV source
tables, rollout summaries, monitor summaries, and reproduction-audit notes.
External citations are used only for general planning, world-model, and value
function framing. They are not used as evidence for Paper10 performance.

Citation files:

- `references/paper10_verified_references_2026-06-09.bib`
- `references/paper10_local_sources_2026-06-09.bib`

The Paper9 local key `zhou2026paper9_local` is not needed in this
Results/Discussion draft. It remains a Methods-only internal placeholder until
the Paper9 source is replaced or formalized before submission.

## One-sentence argument

In constrained farmland layout planning, we show that monitor-gated
frontier-random value labels can improve GeoJEPA-MPC rollout performance at the
validated 20x16/top5 scale, supported by five-seed reward gains, seed-stability
improvement, a GPKG reproduction audit, and negative 50-state monitor
diagnostics that define the current scale-up boundary.

## Draft: Results

### Monitor-gated labels selected trainable pilot and scale-up targets

We first evaluated whether frontier-random multi-step labels provided a usable
candidate-ranking target for value-head training. The 10x12/h5 seed43 pilot
sampled 10 labelled states and 12 candidate actions per state with executable
masks and a five-step return horizon. The monitor selected top-4 as the
training gate, with candidate regret `0.4923`, candidate overlap `0.5000`, and
one-step regret `1.2916`. The value-head-only path then trained the scalar
filter without transition-loss training.

The 10x12/top4 value filter improved the matched rollout baseline. Across
100-step rollouts for seeds 0-4, the pilot reached a mean total reward of
`65.2566` with sample standard deviation `5.0037`. The prior matched
`frontier_independent` value-head branch reached `62.0344` under the same
rollout setting. This established that frontier-random labels contained usable
multi-step ranking information, but the pilot remained small.

We next increased the label set to 20 states and 16 candidate actions per
state. The monitor selected top-5 as the passing gate, with candidate regret
`0.1877`, candidate overlap `0.6300`, and one-step regret `2.4626`. The lower
candidate regret and higher overlap indicated that the candidate-score top-k
set better preserved the return-ranked candidates, while the material one-step
regret indicated that the labels still added information beyond immediate
reward.

### The 20x16/top5 value filter improved reward and seed stability

The 20x16/top5 value filter is the main current E0 result. Under executable
masks, `selector=value_filter`, horizon 5, global top-k 50, blend candidate
scoring, candidate value weight 0.1, and 100-step rollouts for seeds 0-4, mean
total reward increased from `65.2566` for 10x12/top4 to `69.4705` for
20x16/top5. This was an absolute gain of `4.2139` and a relative gain of
`6.46%`.

The scale-up also improved the weak-seed behavior. Sample standard deviation
fell from `5.0037` to `1.0004`, and the minimum seed reward increased from
`57.9750` to `67.7135`. Seed 0 was lower under 20x16/top5, but seeds 1-4 were
higher, including an `11.7468` gain for seed 2. The result therefore reflects
a tighter reward distribution rather than a single favorable rollout seed.

### The GPKG root was required for reproducible label generation

We audited the 20x16/top5 result on a separate macOS machine after an initial
local reproduction did not match the packaged label set. The mismatch was
traced to the prepared-data root. When both shapefile and GPKG inputs were
available, the environment resolved the shapefile layer first and generated
different labels.

A GPKG-only root reproduced the packaged 20x16/h5 seed44 labels. The arrays
`actions`, `returns`, `one_step_rewards`, `n_valid_actions`, `state_steps`, and
`states_gf` matched exactly. The arrays `states_bf` and `candidate_scores`
matched within floating-point tolerance, with maximum absolute differences of
`7.424993508919897e-09` and `1.1920928955078125e-07`, respectively. The
reported E0 scale-up therefore uses the GPKG data-root convention as part of
the experimental protocol.

### Tested 50-state label sets did not pass the monitor gate

We then tested whether the same label workflow could be extended directly to
50 labelled states. The macOS `50x24/h5 seed45` label set failed the default
top-3, top-4, and top-5 monitor checks. Its least-bad default row was top-5,
with candidate regret `1.0241`, candidate overlap `0.4160`, and one-step regret
`3.0139`.

A Windows CPU ablation grid showed the same boundary. Four seed46 50-state
label sets were tested: `50x16 f0.5`, `50x20 f0.5`, `50x24 f0.75`, and
`50x24 f1.0`. All failed the default top-3, top-4, and top-5 checks. The
least-bad default row was `50x16 f0.5` at top-5, but its candidate regret was
`0.3840`, above the `0.2500` threshold.

Post-hoc larger top-k checks did not change the training decision. For the
`50x16` and `50x20` rows, larger top-k values reduced candidate regret but also
made one-step regret too small, weakening the value-filtering task. For the
`50x24` rows, candidate regret or overlap remained limiting until the selected
set became broad enough to reduce the training signal. No tested 50-state
label set therefore justified value-head training under the current monitor
policy.

## Draft: Discussion

The E0 experiments support a bounded value-filtering claim for GeoJEPA-MPC.
Learned value functions are widely used to score candidate states or actions in
reinforcement learning and search, and model-predictive planners rely on
finite-horizon evaluations to select constrained actions [@sutton2018reinforcement_learning;
@mnih2015dqn; @silver2016alphago; @mayne2014mpc_future_promise;
@rawlings2017model_predictive_control]. In Paper10, this general idea becomes
useful only after the label set passes a candidate-quality monitor. The
strongest current evidence is the 20x16/top5 run, which improved five-seed mean
reward and reduced seed sensitivity relative to the 10x12/top4 pilot.

The monitor gate was central to interpreting the result. Learned world models
and predictive latent representations can support planning by evaluating
candidate futures in a learned representation [@ha2018recurrent_world_models;
@hafner2019planet; @assran2023ijepa]. The LeWM 2026 arXiv preprint provides a
direct design comparison for JEPA-style world-model planning
[@maes2026leworldmodel], but a value head trained on weak labels would only add
noise to the planning selector. The change from top-4 in the 10x12 pilot to
top-5 in the 20x16 scale-up shows that the usable target was not a fixed
hyperparameter. It depended on candidate coverage, candidate ranking quality,
and whether the multi-step label retained information beyond one-step reward.

The main rival explanation is that the value filter simply reproduced
one-step reward ranking. The 20x16/top5 monitor argues against that
interpretation because one-step regret remained `2.4626` at the selected gate.
The failed 50-state post-hoc checks show the opposite failure mode. Some larger
top-k settings reduced candidate regret, but one-step regret collapsed enough
to make the target mostly explainable by immediate reward. This contrast is why
the 50-state diagnostics should be reported as boundary evidence rather than
hidden as failed runs.

The reproduction audit also affects the paper's methodological claim. The
GPKG/shapefile discrepancy shows that geospatial data resolution is part of the
experimental protocol, not a cosmetic file-format choice. A paper-facing E0
claim should therefore name the GPKG root convention, and supplementary
material should include the array-level reproduction audit. Without that
protocol detail, an independent rerun could generate different labels before
model training begins.

The current evidence does not support direct value-head training for the tested
50-state labels. All tested 50-state labels failed the monitor gate before
training, and larger top-k diagnostics did not produce a pre-declared passing
condition. The next scale-up attempt should therefore change the candidate
proposal strategy, the label-generation budget, or the monitor design before
training. Until such a label set passes, the defensible manuscript claim is that
monitor-gated frontier-random labels improved GeoJEPA-MPC at the validated
20x16/top5 scale and revealed candidate proposal design as the next bottleneck.

## Section outline

- Result 1: monitor-selected 10x12/top4 and 20x16/top5 gates define which
  value-label sets were trainable.
- Result 2: 20x16/top5 improved five-seed mean reward from `65.2566` to
  `69.4705` and reduced sample standard deviation from `5.0037` to `1.0004`.
- Result 3: the macOS GPKG audit establishes the data-root convention required
  to reproduce the packaged 20x16 labels.
- Result 4: macOS and Windows 50-state diagnostics failed default and post-hoc
  gates, so value-head training was not justified for tested 50-state labels.
- Discussion: value scoring is useful only under monitor-gated labels; the
  current boundary is candidate-proposal design for 50-state scale-up.

## Claim-evidence map

| Claim | Evidence | Status |
|---|---|---|
| Frontier-random labels trained a useful pilot value filter. | 10x12/top4 mean reward `65.2566` exceeded matched `frontier_independent` mean `62.0344`. | supported |
| 20x16/top5 is the current main E0 positive result. | Mean reward `69.4705`, sample std `1.0004`, and monitor-selected top-5 gate passed. | supported |
| The 20x16/top5 gain improved stability, not only best-case reward. | Sample std fell by `4.0034`; minimum seed reward rose from `57.9750` to `67.7135`. | supported |
| The 20x16/top5 labels are reproducible under the GPKG root. | macOS GPKG reproduction matched key arrays exactly or within floating-point tolerance. | supported |
| Tested 50-state labels should not be trained under the current policy. | macOS seed45 and Windows seed46 rows failed default and post-hoc monitor checks. | supported |
| Direct value-head training is supported for the tested 50-state labels. | No tested 50-state label set passed the monitor gate. | not supported |

## Citation-use note

- Use value-function citations only to explain the general idea of learned
  value scoring, not to validate Paper10's measured reward gains.
- Use MPC and world-model citations only to frame finite-horizon candidate
  evaluation and predictive latent representations.
- Do not add external citations to numeric E0 result claims. Those claims are
  supported by local result artifacts and should be tied to tables, figures, and
  reproducibility files in the final manuscript package.

## Assumptions or missing inputs

- Final figure and table numbers are not fixed.
- The target journal and section length are not fixed.
- The final manuscript still needs a decision on whether LeWM is acceptable as
  a cited 2026 arXiv preprint.
- The Paper9 local-source key remains Methods-only and must be replaced or
  formalized before submission.

## Why this structure

- The Results section follows the evidence ladder: pilot gate, main scale-up,
  reproducibility audit, and 50-state stress-test boundary.
- The Discussion interprets why the monitor gate matters and addresses the
  one-step-reward rival explanation before discussing scale-up.
- The draft keeps 20x16/top5 as the paper-facing positive claim and uses the
  failed 50-state rows as explicit boundary evidence.
