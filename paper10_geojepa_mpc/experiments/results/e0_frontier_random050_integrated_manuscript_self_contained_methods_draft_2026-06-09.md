# E0 frontier_random050 integrated manuscript draft with self-contained Methods

Date: 2026-06-09

This document is a public-submission-oriented variant of the current integrated
Paper10 E0 manuscript draft. It keeps the same bounded `frontier_random050`
evidence claim as the earlier integrated draft, but it removes dependence on
the local-only Paper9 citation by writing the Bishan task, environment, action,
reward, and reproducibility conditions directly from packaged Paper10 code and
source-grounded Methods notes.

Source basis:

- `e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md`
- `e0_bishan_task_environment_self_contained_methods_2026-06-09.md`
- `e0_reward_and_rollout_metric_definitions_2026-06-09.md`
- `references/paper10_verified_references_2026-06-09.bib`

This variant intentionally does not cite `zhou2026paper9_local` in the
manuscript body. If the authors later publish or archive Paper9, the final
manuscript may cite that source after the citation is public and verified.

## Working title

Monitor-gated value filtering for GeoJEPA-MPC farmland layout planning

## Abstract

Constrained farmland layout planning requires search procedures that improve
long-horizon land-use outcomes while respecting executable swap constraints.
World-model planners can evaluate candidate actions over finite horizons, but a
candidate filter trained on weak multi-step labels can degrade planning rather
than improve it. Here we evaluate a monitor-gated value-filtering workflow for
GeoJEPA-MPC using frontier-random multi-step labels in a self-contained Bishan
farmland swap environment. A 10-state, 12-candidate pilot selected a top-4
training gate and reached a five-seed 100-step mean total reward of `65.2566`.
Scaling the label set to 20 states and 16 candidate actions selected a top-5
gate with candidate regret `0.1877`, candidate overlap `0.6300`, and one-step
regret `2.4626`. The resulting value filter achieved a mean total reward of
`69.4705`, a `6.46%` improvement over the 10x12/top4 pilot, and reduced sample
standard deviation from `5.0037` to `1.0004`. A macOS reproduction audit
matched the packaged 20x16 labels under a GPKG data root, establishing the
current reproducible route. Direct 50-state extensions failed the default and
post-hoc monitor gates, so they were retained as negative diagnostics rather
than training inputs. These results support a bounded claim: monitor-gated
value labels improve GeoJEPA-MPC at the validated 20x16/top5 scale and identify
candidate-proposal design as the next scale-up bottleneck.

## Introduction

Spatial land-use allocation and land-consolidation planning are commonly framed
as GIS-supported, multi-criteria optimization problems in which local parcel or
site decisions affect landscape-level objectives
[@yao2018spatial_optimization_land_use; @stewart2014multiobjective_gis_land_use;
@demetriou2012ipdss_land_consolidation]. Prior work has represented these
problems through integer programming, multiobjective land-use allocation,
parcel-exchange optimization, and parcel-shape or consolidation decision-support
systems
[@aerts2003linear_integer_land_use_allocation; @teijeiro2020parcel_exchange;
@demetriou2013parcel_shape_index;
@demetriou2014ipdss_land_consolidation_book]. Paper10 studies a related but
more sequential setting: farmland layout is improved through executable
land-use swaps, and each local swap can change slope, contiguity, connected
area, and future action availability over many planning steps.

This sequential structure creates a planning bottleneck. A candidate action that
looks attractive under an immediate score may not preserve the best
long-horizon return once subsequent swaps are considered. Model-predictive
control addresses this general problem by repeatedly using finite-horizon
predictions to choose actions under constraints
[@mayne2014mpc_future_promise; @rawlings2017model_predictive_control].
Reinforcement-learning value functions provide a complementary way to score
states or actions by expected future return, and learned value estimates have
been used to guide action selection and search in high-dimensional decision
problems [@sutton2018reinforcement_learning; @mnih2015dqn; @silver2016alphago].
For farmland swap planning, the open question is not whether long-horizon
signals are useful in principle, but whether a small and reproducible
value-label workflow can improve candidate filtering without training on
low-quality labels.

Learned world models offer one route to this problem because they can plan in a
latent representation rather than directly in the full observation space
[@ha2018recurrent_world_models; @hafner2019planet]. Joint-embedding predictive
architectures (JEPAs) further motivate predictive representation learning in
which a model predicts target embeddings instead of reconstructing raw inputs
[@assran2023ijepa]. A recent arXiv preprint, LeWorldModel, applies a JEPA-style
world-model approach to pixel-based control and is useful as a design
comparison, but it should be cited as a 2026 preprint rather than as settled
prior art [@maes2026leworldmodel]. These sources motivate the GeoJEPA-MPC
framing, but they do not solve the Paper10-specific problem of constructing and
validating multi-step candidate labels for constrained geospatial farmland
swaps.

Here we test a monitor-gated frontier-random labeling workflow for GeoJEPA-MPC.
The method first generates multi-step return labels from candidate pools that
mix model-scored frontier actions with random exploratory actions, then permits
value-head training only when predeclared candidate-regret, candidate-overlap,
one-step-regret, and state-count gates pass. The present evidence ladder is
bounded: a 10x12/top4 pilot establishes the value-head route, a 20x16/top5 run
provides the main paper-facing result, a GPKG-root audit records the current
reproducible data condition, and tested 50-state `frontier_random050` labels
remain negative diagnostics rather than training inputs. This framing supports
a specific claim: monitor-gated value labels improve GeoJEPA-MPC at the
validated 20x16/top5 scale, while candidate-proposal redesign remains the next
step for 50-state scale-up.

## Methods

### Bishan task and data root

We formulate Bishan farmland layout optimization as a finite-horizon sequential
land-use swap task over spatial blocks. The environment loads swappable parcels
from a prepared `DLTB_with_slope` layer and retains parcels whose land-use code
belongs to either farmland or forest. Farmland parcels are identified by `DLBM`
prefixes `011`, `012`, and `013`; forest parcels are identified by prefixes
`031`, `032`, and `033`. Parcel areas are computed after projection to
`EPSG:32648`, and parcel slopes are read from the prepared `slope_mean` field.
The environment builds parcel adjacency with queen contiguity and uses the
resulting graph to compute farmland-neighbor counts, contiguity, and connected
baimu-fang patches. These task definitions are implemented in `county_env.py`
and summarized in
`e0_bishan_task_environment_self_contained_methods_2026-06-09.md`.

The planning units are blocks rather than individual parcels. For each township
listed in `townships.json`, the environment loads `block_compositions.json` to
map block identifiers to parcel indices and `block_features.json` to recover
static block compactness. A block action therefore chooses where to invest the
next local swap operation, while the environment deterministically chooses the
specific paired parcel conversion inside that block. This action-space design
keeps the planner at a block resolution while retaining parcel-level slope,
adjacency, and area effects in the transition dynamics.

The full Bishan prepared dataset is external to the Git repository and is
resolved through the repository-level data layout described in
`DATA_AVAILABILITY.md` and `REPRODUCIBILITY.md`. For the paper-facing E0
evidence, the reproducible geospatial root is the root that resolves
`DLTB_with_slope.gpkg`. A macOS audit showed that this GPKG root reproduced the
packaged 20x16/h5 seed44 labels at the array level, whereas a root that
resolved the shapefile version first produced materially different labels. We
therefore treat the GPKG root as part of the experimental condition rather
than an incidental file-format choice.

### State, action, and reward

The observation is the concatenation of a per-block feature matrix and a
county-level global feature vector. Each block has 17 features, including
normalized farmland and forest slope summaries, best local slope gain,
available farmland and forest areas, remaining swap potential, prior swaps in
the block, compactness, block area, neighboring-block investment status,
neighboring farmland area, current farmland area, and whether the block has
already received investment. The global vector has 12 features, including
remaining budget fraction, normalized global farmland slope, normalized
contiguity, step fraction, slope improvement, contiguity improvement,
baimu-fang count and area summaries, invested-block fraction, investment
entropy across townships, a placeholder cross-township baimu feature, and the
maximum single-township investment fraction.

The base action space is `Discrete(n_blocks)`: one action selects one block.
The base environment marks a block valid when the block still contains at least
one unswapped farmland parcel and one unswapped forest parcel. In the E0
paper-facing experiments, this base mask is intersected with an executable
mask before label generation and rollout evaluation. The executable mask
replicates the environment's greedy paired-swap rule and keeps only blocks for
which the best available farmland parcel has a higher slope than the best
available forest parcel.

For a selected block, the greedy execution rule attempts at most
`swaps_per_step=5` paired swaps. At each paired swap, the environment scores
candidate farmland parcels by slope minus `delta_conn` times the current
farmland-neighbor count, and scores candidate forest parcels by slope minus
`gamma_conn` times the current farmland-neighbor count. The highest-scored
farmland parcel is converted to forest, and the lowest-scored forest parcel is
converted to farmland, only if the farmland parcel has higher slope than the
forest parcel. Converted parcels are marked as swapped and cannot be used again
in the same episode. If no qualifying pair remains, block execution stops
before the five-swap maximum.

The default episode budget is 500 paired swaps, with at most five paired swaps
per environment action, giving a maximum of 100 planning steps. After each
block action, the reward combines normalized stepwise reduction in
area-weighted farmland slope, normalized stepwise change in contiguity,
normalized stepwise change in connected baimu-fang area, and a bonus for newly
counted baimu-fang patches. The environment adds an asymmetric penalty when
baimu-fang area decreases and a `-1.0` penalty when the selected block executes
zero swaps. The exact formula and reporting metrics are recorded in
`e0_reward_and_rollout_metric_definitions_2026-06-09.md`. The environment
terminates when the step count reaches `max_steps`, or earlier if no base-valid
block remains.

### GeoJEPA-MPC base planner

The value-filtering workflow starts from the packaged GeoJEPA-MPC rank
checkpoint `rank_seed2028.pt`. The checkpoint is wrapped by the packaged
environment adapter so that it can score executable actions in the farmland
environment and support model-predictive candidate selection. Candidate actions
are scored from the current state and evaluated over a finite planning horizon.
The E0 experiments do not claim a new transition model; they test whether a
separately trained value head can improve candidate filtering on top of this
existing rank checkpoint.

### Frontier-random value-label generation

For each sampled state, `frontier_random050` constructs a candidate set by
combining model-scored frontier actions with random exploratory actions. The
frontier fraction is fixed at `0.5`, so half of the requested candidate budget
is allocated to the highest-scored valid actions when enough valid actions are
available, and the remaining budget is sampled from valid actions outside that
frontier set. This design keeps the candidate pool close enough to the rank
checkpoint to test value filtering while preserving exploratory alternatives
that can reveal multi-step returns missed by immediate model scores.

Each candidate action is labeled by applying the action and then rolling out a
random continuation policy for a fixed label horizon. The packaged E0 value
labels use horizon `5`, discount factor `0.99`, executable masks, random state
advance, and random continuation. The label file stores candidate actions,
discounted returns, one-step rewards, candidate scores, valid-action counts,
state-step indices, block features, and geospatial features. The 10x12 pilot
uses 10 sampled states and 12 candidate actions per state. The main packaged
scale-up uses 20 sampled states and 16 candidate actions per state.

### Monitor-gated label selection

Value-head training is conditional on a monitor gate rather than triggered
automatically after label generation. For a candidate top-k value, the monitor
compares three diagnostics: candidate regret, candidate overlap, and one-step
regret. Candidate regret is the mean return gap induced by selecting actions
from the candidate-score top-k set; it must not exceed `0.25`. Candidate
overlap is the mean overlap between the candidate-score top-k set and the
return-ranked top-k set; it must be at least `0.5`. One-step regret measures
the return gap under one-step-reward top-k selection; it must remain at least
`0.25`, otherwise the multi-step labels add little beyond immediate reward.
The monitor also requires at least 10 labeled states.

The gate is evaluated over alternative top-k values and the selected top-k is
then used for value-head training. In the packaged 10x12 pilot, top-4 is the
usable gate. In the packaged 20x16 scale-up, top-5 is the usable gate, with
candidate regret `0.1877`, candidate overlap `0.6300`, and one-step regret
`2.4626`. Label sets returning `decision=stop` are retained as diagnostics but
are not used as training inputs.

### Value-head-only training

The value head is initialized from the GeoJEPA-MPC rank checkpoint and trained
from the monitor-approved value labels. The training entry point is
`run_e0_value_head_train`, with `lambda_rank=1.0` and `lambda_sig=0.0`. This
configuration disables transition mean-squared-error training and restricts the
trainable scope to the value head, which contains 8,321 trainable parameters in
the packaged runs. The checkpoint metric is selected from the candidate top-k
diagnostic, so the 20x16/top5 run selects the best checkpoint by
`candidate_top5_regret`.

For the main 20x16/top5 experiment, value-head training uses 20 pairwise label
states, candidate top-k `5`, pairwise subsample `16`, 8 pairs per batch item,
batch size `16`, learning rate `1e-3`, and CPU execution. The packaged best
checkpoint is epoch 2, with `candidate_top5_regret=0.1877`,
`candidate_top5_hit_rate=0.9000`, and `transition_loss_enabled=false`. These
metrics define the trained value filter used in the subsequent rollout
evaluation.

### Rollout evaluation and statistics

The trained value head is evaluated in 100-step GeoJEPA-MPC rollouts with
executable masks, `selector=value_filter`, horizon `5`, global top-k `50`,
candidate score mode `blend`, candidate value weight `0.1`, independent random
continuation, and seeds 0-4. The same rollout configuration is used for the
10x12/top4 pilot and the 20x16/top5 scale-up so that the comparison isolates
the monitor-gated label and value-head setting rather than evaluation
parameters.

The primary rollout metric is total reward over 100 environment steps. We also
report the sample standard deviation across the five seeds, the minimum and
maximum seed reward, mean slope-change percentage, mean continuity change, and
mean baimu-area change. Rollout total reward is the un-discounted sum of the
per-step environment rewards. Value-label returns use the same environment
reward but apply the label horizon and discount factor configured in the
value-label generator.

### Reproducibility and negative-label boundary

The package includes compact source artifacts for reproducing the paper-facing
E0 evidence: value-label files, monitor JSON/Markdown outputs, value-head
metrics, trained checkpoints, rollout summaries, figure-ready CSV files, and
the plotting script for quantitative draft figures. Generated PNG/SVG previews
are written under ignored `reviewer_outputs/` by default and are not required
for source-control verification.

The tested 50-state `frontier_random050` label sets define the current
candidate-proposal boundary. The macOS `50x24/h5 seed45` run and the Windows
seed46 ablation rows all failed the default monitor checks, and post-hoc larger
top-k checks did not change the decision to train. These label sets should
therefore be described as negative diagnostics, not as failed value-head
training. A future 50-state experiment should first pass a pre-declared monitor
gate or use a redesigned candidate proposal before value-head training is
attempted.

## Results

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
higher, including an `11.7468` gain for seed 2. The result therefore reflects a
tighter reward distribution rather than a single favorable rollout seed.

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
set became broad enough to reduce the training signal. No tested 50-state label
set therefore justified value-head training under the current monitor policy.

## Discussion

The E0 experiments support a bounded value-filtering claim for GeoJEPA-MPC.
Learned value functions are widely used to score candidate states or actions in
reinforcement learning and search, and model-predictive planners rely on
finite-horizon evaluations to select constrained actions. In Paper10, this
general idea becomes useful only after the label set passes a candidate-quality
monitor. The strongest current evidence is the 20x16/top5 run, which improved
five-seed mean reward and reduced seed sensitivity relative to the 10x12/top4
pilot.

The monitor gate was central to interpreting the result. A value head trained
on weak labels would only add noise to the planning selector, even if the base
world-model planner is useful. The change from top-4 in the 10x12 pilot to
top-5 in the 20x16 scale-up shows that the usable target was not a fixed
hyperparameter. It depended on candidate coverage, candidate ranking quality,
and whether the multi-step label retained information beyond one-step reward.

The main rival explanation is that the value filter simply reproduced one-step
reward ranking. The 20x16/top5 monitor argues against that interpretation
because one-step regret remained `2.4626` at the selected gate. The failed
50-state post-hoc checks show the opposite failure mode. Some larger top-k
settings reduced candidate regret, but one-step regret collapsed enough to make
the target mostly explainable by immediate reward. This contrast is why the
50-state diagnostics should be reported as boundary evidence rather than hidden
as failed runs.

The reproduction audit also affects the paper's methodological claim. The
GPKG/shapefile discrepancy shows that geospatial data resolution is part of the
experimental protocol, not a cosmetic file-format choice. A paper-facing E0
claim should therefore name the GPKG root convention, and supplementary material
should include the array-level reproduction audit. Without that protocol
detail, an independent rerun could generate different labels before model
training begins.

The current evidence does not support direct value-head training for the tested
50-state labels. All tested 50-state labels failed the monitor gate before
training, and larger top-k diagnostics did not produce a pre-declared passing
condition. The next scale-up attempt should therefore change the candidate
proposal strategy, the label-generation budget, or the monitor design before
training. Until such a label set passes, the defensible manuscript claim is that
monitor-gated frontier-random labels improved GeoJEPA-MPC at the validated
20x16/top5 scale and revealed candidate proposal design as the next bottleneck.

## Conclusion

Monitor-gated frontier-random value labels improved GeoJEPA-MPC rollouts at the
validated 20x16/top5 scale. The value filter increased the five-seed mean total
reward from `65.2566` to `69.4705` relative to the 10x12/top4 pilot and reduced
sample standard deviation from `5.0037` to `1.0004`. The same evidence defines
the present boundary: tested 50-state label sets did not pass the monitor gate
and should not be described as a passing scale-up result. Paper10 should therefore
present 20x16/top5 as the current positive result and treat candidate-proposal
redesign as the next step for 50-state value-head training.

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| Land-use allocation and land consolidation can be framed as spatial multi-criteria optimization or decision support. | `yao2018spatial_optimization_land_use`; `stewart2014multiobjective_gis_land_use`; `demetriou2012ipdss_land_consolidation`; `demetriou2014ipdss_land_consolidation_book` | supported by external literature |
| The Bishan task/environment can be described without a local Paper9 citation. | `county_env.py`; `arcgis_toolbox_paper9/private_source/blocks_env.py`; self-contained Bishan task/environment note; reward-definition note | supported as code-derived Paper10 Methods material |
| Long-horizon action choice can be framed through MPC and value functions. | `mayne2014mpc_future_promise`; `rawlings2017model_predictive_control`; `sutton2018reinforcement_learning`; `mnih2015dqn`; `silver2016alphago` | supported by external literature |
| Learned world models and JEPA-style representation learning motivate the GeoJEPA-MPC framing. | `ha2018recurrent_world_models`; `hafner2019planet`; `assran2023ijepa`; `maes2026leworldmodel` | supported, with LeWM marked as preprint |
| 20x16/top5 is the current main E0 positive result. | Mean reward `69.4705`, sample std `1.0004`, selected top-5 monitor gate passed. | supported |
| The 20x16/top5 result improves stability, not only best-case reward. | Sample std fell from `5.0037` to `1.0004`; minimum seed reward rose from `57.9750` to `67.7135`. | supported |
| The 20x16/top5 labels are reproducible under the GPKG root. | macOS GPKG reproduction matched key arrays exactly or within floating-point tolerance. | supported |
| Existing 50-state labels should not be trained. | macOS seed45 and Windows seed46 rows failed default and post-hoc monitor checks. | supported |
| Direct value-head training is supported for the tested 50-state labels. | No 50-state label set passed the monitor gate. | not supported |

## Submission blockers

- Select the target journal and convert Pandoc-style citation keys to the
  required reference format.
- Decide whether the target journal permits citation to the 2026 LeWM arXiv
  preprint; if not, cite `assran2023ijepa` for JEPA and keep LeWM as an
  unsubmitted related-work note.
- Finalize Data and Code Availability: archive the repository, add repository
  and dataset DOI or reviewer-access links, choose code/data licences, and
  define the access route for full Bishan Tool2 and GPKG-root geospatial data.
- Decide whether the self-contained Bishan task/environment Methods material
  belongs in the main Methods section, supplementary Methods, or a citable
  code/data supplement.
- Fix figure and table numbering after final figure selection.
- Decide whether China-specific farmland or land-consolidation policy
  citations are needed in the Introduction.

## Chinese author notes

- This variant is the current no-local-Paper9 manuscript route: it does not
  cite `zhou2026paper9_local` in the manuscript body.
- The positive claim is still 20x16/top5 only. The 50-state rows remain boundary
  diagnostics and should not be written as a passing scale-up result.
- This draft still needs target-journal formatting, repository/data DOI links,
  figure/table numbering, and a final data-access route before submission.
