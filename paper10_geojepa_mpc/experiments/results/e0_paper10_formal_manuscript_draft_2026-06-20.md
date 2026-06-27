# Paper10 formal manuscript draft

Date: 2026-06-20

Status: formal manuscript draft. This file updates the CEUS Stage 3 draft with
the later 2026-06-20 candidate-score sweep on the 50x24/f075 line. It is not a
final submission package. Repository DOI, licence, full-data access,
citation-policy, statistical-policy and final figure-export decisions remain
open in `e0_submission_blocker_decision_packet_2026-06-11.md`.

Source controls used for this draft:

- `e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- `e0_ceus_research_article_manuscript_draft_2026-06-12.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.json`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.md`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.json`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_ceus_reviewer_improvement_packet_2026-06-12.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`

Paper9 has not been formally submitted. This draft therefore uses the
self-contained Paper10 Methods route and does not cite the local Paper9
placeholder in public manuscript text.

## One-Sentence Argument

In constrained farmland layout planning, we show that monitor-gated value
labels and executable masks can improve and stabilize GeoJEPA-MPC rollouts at
the validated Bishan 20x16/top5 scale, supported by five-seed reward and
matched-baseline checks, while Stage 3 confirmatory rollouts show that the
tested 50-state value-label rows did not beat the matched Paper9 baseline and
therefore bound the method as a calibrated planning-support workflow rather
than a broad scale-up result; a later 50x24 candidate-score sweep did not
change that boundary. A mechanism ablation further showed that removing the
executable mask sharply degraded reward, while an ungated top-4 control did
not separate from the gated anchor under the same rollout protocol.

## Terminology Ledger

| canonical term | first-use definition | conversion rule |
|---|---|---|
| GeoJEPA-MPC | A geospatial JEPA and model-predictive planning workflow for constrained farmland layout planning. | Use as the method name throughout the draft. |
| monitor-gated value labels | Finite-horizon return labels accepted only after candidate-regret, overlap and one-step-regret checks. | Present as the quality-control mechanism that decides whether value-head training is manuscript-facing. |
| value filter | The trained scalar value head used to filter candidate swaps before rollout scoring. | Report label scale, top-k, horizon, baseline and rollout seeds with each performance claim. |
| matched Paper9 baseline | The `paper9 rank_seed2028` checkpoint rolled out under the same Stage 3 horizon, top-k, mask and seed protocol. | Use as the Stage 3 comparator unless the author explicitly freezes a separate pairwise-only baseline. |
| executable mask | A hard action mask that removes infeasible block swaps before candidate selection. | Use for inference and rollout enforcement. |
| diagnostic_near_pass | A Stage 1 near-pass row rolled out for diagnostic context. | It must not be pooled with confirmatory rows or used to strengthen the 50-state claim. |
| block-level planning-unit abstraction | The implemented planning abstraction in which actions select blocks rather than arbitrary individual parcels. | State as a current boundary for CEUS readers. |
| soft training and hard inference | Reward and count penalties guide training labels, while executable masks and paired inference enforce rollout feasibility. | Do not describe the implementation as a Constrained MDP, CPO, or RCPO solver. |
| Dongxing/Neijiang | The external-region package with 3711 blocks and 76,376 parcel assignments. | Use as calibration and stress-test evidence, not as robust transfer proof. |

## Title

Monitor-gated value labels bound GeoJEPA-MPC farmland layout planning

## Highlights

- Monitor gates control GeoJEPA-MPC value-label escalation.
- Executable masks are rollout-critical.
- Bishan 20x16/top5 exceeded the matched Paper9 baseline in mean reward.
- Stage 3 50-state rows did not exceed that baseline.
- The later 50x24 candidate-score sweep did not recover the baseline.
- Dongxing evidence supports calibration, not transfer superiority.
- The draft preserves explicit data and deployment boundaries.

## Abstract

Constrained farmland layout planning requires sequential spatial decisions
whose long-horizon value can diverge from immediate reward. We present a
monitor-gated GeoJEPA-MPC workflow that generates finite-horizon value labels,
checks label quality before value-head training, and applies executable masks
during rollout. In Bishan, the validated 20x16/top5 value filter reached
69.4705 mean reward across five 100-step seeds, compared with 67.5437 for the
matched Paper9 baseline and 65.2566 for the earlier 10x12/top4 pilot; the
post-CEUS seed audit is mixed seed-wise and therefore supports a descriptive
mean-reward claim rather than uniform per-seed superiority. A mechanism ablation
further showed that removing the executable mask sharply
reduced reward, while an ungated top-4 negative control did not separate from
the gated anchor under the same rollout protocol. Stage 3 confirmatory tests
then evaluated the two passing 50-state rows under matched rollout settings.
The 50x16/top6 row reached 64.2960 mean reward and the 50x24/top12 row
reached 66.2544, both below the matched Paper9 baseline; a diagnostic
near-pass row reached 67.4913 and must not be pooled with confirmatory rows.
A later candidate-score sweep on the same 50x24/f075 checkpoint varied
`candidate-score-mode` across `blend` (0.05, 0.10, 0.15, 0.25) and `value`;
`blend0.10` remained the best variant, but it still fell short of the matched
Paper9 baseline, and pure `value` filtering was materially worse.
Dongxing/Neijiang evidence remains useful as a calibration and stress-test
package, but it does not support robust Bishan-to-Dongxing transfer
superiority. These results support monitor-gated value filtering and
executable masking as a reproducible evidence-control workflow for constrained
geospatial planning, while bounding claims about broad 50-state scaling,
arbitrary cadastral parcel deployment and cross-region transfer superiority.

## Keywords

Farmland layout planning; land-use optimization; GeoJEPA-MPC; value labels;
model-predictive planning; geospatial decision support; monitor gates.

## 1. Introduction

Farmland layout planning is a spatial optimization problem in which local
land-use changes must be evaluated against slope, contiguity, parcel shape,
area and administrative constraints. GIS-based land-use allocation and land
consolidation systems have long treated land management as a multi-criteria
planning task rather than as a purely local classification problem
[@aerts2003linear_integer_land_use_allocation;
@stewart2014multiobjective_gis_land_use;
@demetriou2012ipdss_land_consolidation;
@yao2018spatial_optimization_land_use]. Parcel exchange and parcel-shape
studies further show why the geometry of planning units matters for practical
land-consolidation decisions [@demetriou2013parcel_shape_index;
@teijeiro2020parcel_exchange].

The difficulty for learned planning is that the value of a local swap is not
fully determined by its immediate reward. A block exchange can alter later
connectivity, slope reduction opportunities and area aggregation, so a planner
must repeatedly evaluate finite-horizon candidate futures under executable
constraints. Model-predictive control provides a natural template for rolling
finite-horizon decision making [@mayne2014mpc_future_promise;
@rawlings2017model_predictive_control], while learned world models show how
latent dynamics can support candidate rollout and search
[@ha2018recurrent_world_models; @hafner2019planet].

Value functions can improve candidate selection, but using value labels in
geospatial planning creates an additional quality-control problem. A larger
label set is useful only if generated returns preserve meaningful candidate
rankings and if the resulting value filter remains compatible with hard
feasibility masks during rollout. JEPA-style predictive representations
motivate learning in an embedding space rather than reconstructing raw inputs
[@assran2023ijepa], but the manuscript-facing claim in this paper is not that
representation learning alone solves farmland planning. The claim is that
value labels need explicit monitoring before they are used to train a
planner-facing value head.

We therefore evaluate a monitor-gated GeoJEPA-MPC workflow for constrained
farmland layout planning. The workflow generates finite-horizon return labels
for candidate block actions, applies monitor gates to check candidate regret,
candidate overlap and one-step reward alignment, trains a value filter only
for accepted label sets, and enforces feasibility with executable masks and
paired inference during rollout. This is a soft training and hard inference
design: reward and count penalties shape rankings during training, while hard
masks and deterministic paired swaps enforce executable actions. The
implementation should not be described as a Constrained MDP, CPO, or RCPO
solver.

The evidence ladder is deliberately bounded. Bishan provides the primary
positive result: a monitor-selected 20x16/top5 value-label setting exceeded
the matched Paper9 baseline and reduced seed-level variation. Stage 3 then
tested whether two authorized 50-state value-label rows could support a
stronger scale claim. They completed value-filter rollouts, but neither
exceeded the matched Paper9 baseline. Dongxing/Neijiang remains a second
real-environment calibration and stress-test package, but mixed
transfer-versus-scratch outcomes prevent a robust transfer-superiority claim.

## 2. Methods

### 2.1 Task Formulation and Planning Units

We model farmland layout planning as a finite-horizon sequential swap task
over spatial blocks. At each environment step, the planner selects one block,
and the environment executes up to five paired farmland-forest swaps inside
that block. The execution rule converts a higher-slope unswapped farmland
parcel to forest and a lower-slope unswapped forest parcel to farmland when
the slope condition is satisfied. The default episode budget is 500 paired
swaps, giving a maximum of 100 planning steps at five swaps per action.

The implemented action is block-level rather than arbitrary parcel-level. A
block action identifies where a local swap should be attempted; the
environment then chooses the specific parcel pair through the deterministic
greedy execution rule. This block-level planning-unit abstraction is the
current paper-facing evidence boundary. Deployment on irregular cadastral
parcels would require area-tolerance matching between candidate exchange
units, parcel geometry features and explicit shape constraints; those
extensions are not implemented in the current experiments.

The environment represents topology with queen contiguity. This abstraction
supports reproducible block and parcel adjacency in the current code path, but
it is not a final engineering definition for irregular parcel deployment.
Shared-perimeter-weighted contiguity and compactness features should be added
before claiming operational parcel-exchange suitability.

### 2.2 State, Action Masks and Reward

The observation concatenates a per-block feature matrix with a county-level
global feature vector. Block features include normalized farmland and forest
slope summaries, available farmland and forest areas, remaining swap
potential, compactness, current farmland area and investment status. Global
features include remaining budget fraction, global farmland slope, contiguity,
step fraction, slope and contiguity changes, baimu-fang count and area
summaries, investment entropy across townships and the maximum single-township
investment fraction.

The base action mask keeps blocks with at least one unswapped farmland parcel
and one unswapped forest parcel. Paper-facing value-label generation and
rollout evaluation intersect this base mask with an executable mask. For each
block, the executable mask checks whether the best available farmland parcel
has higher slope than the best available forest parcel under the same
connectivity-adjusted scoring rule used by the environment. This prevents the
planner from selecting blocks that would satisfy the coarse availability mask
but execute no useful paired swap.

The per-step reward combines normalized stepwise reduction in area-weighted
farmland slope, normalized stepwise contiguity change, normalized stepwise
change in connected baimu-fang area, a bonus for newly counted baimu-fang
patches, an asymmetric penalty when baimu-fang area decreases and a penalty
for zero-swap actions. Rollout total reward is the undiscounted sum of
per-step rewards over the 100-step episode. Final slope change, contiguity
change and baimu-area change are final-step episode metrics averaged across
rollout seeds when aggregated.

### 2.3 GeoJEPA-MPC and Value Filtering

GeoJEPA-MPC combines a geospatial predictive representation, candidate action
generation, finite-horizon rollout scoring and a learned scalar value filter.
The planner samples candidate block actions under the executable mask, scores
candidate futures, blends model-predictive rollout scores with value-head
outputs, and selects actions for environment execution. In Bishan rollouts,
the value-filter setting used `selector=value_filter`, horizon 5, global
top-k 50, blend candidate scoring and candidate-value-weight 0.1. In the
Dongxing calibration experiments, the planner required
candidate-value-weight=1.0.

The value filter is trained from generated value labels rather than from an
uncontrolled collection of all candidate returns. For a selected state and
candidate action set, the label generator applies each candidate action, rolls
out a configured continuation policy for a finite horizon and stores both the
one-step reward and the discounted multi-step return. The packaged Bishan
positive labels use horizon 5 and discount factor 0.99.

### 2.4 Monitor-Gated Value-Label Selection

The monitor gate checks whether a generated label set is suitable for
value-head training and manuscript-facing escalation. For each candidate
top-k, the monitor reports candidate regret, candidate overlap and one-step
regret. Candidate regret measures the return gap under the candidate-score
top-k set. Candidate overlap measures agreement with the return-ranked top-k
set. One-step regret checks whether multi-step returns retain information
beyond immediate reward.

Training proceeds only for label sets that pass the monitor gate. This design
is central to the paper because it treats failed labels as diagnostic evidence
rather than silently converting them into model checkpoints. The Stage 3
protocol applied this rule to authorized 50-state rows and then compared the
resulting rollouts with a matched Paper9 baseline.

### 2.5 Bishan and Stage 3 Protocol

Bishan is the primary validation environment for the current draft. The
paper-facing route uses the GPKG-root prepared-data convention that resolves
`dem_slope_analysis/output/DLTB_with_slope.gpkg`, because the local
reproduction audit matched the packaged 20x16/horizon-5 seed44 label arrays
under that root. Full reruns require the external full Bishan Tool2 transition
and pairwise data plus prepared geospatial inputs; the Git repository includes
smoke data, generated value labels, monitor outputs, checkpoints, rollout
summaries and figure-ready source data.

The original Bishan evidence compared a 10-state, 12-candidate, horizon-5
pilot with a 20-state, 16-candidate, horizon-5 scale-up. Stage 3 then trained
and rolled out only the two Stage 1 pass rows:
`frontier_random050_50x16_h5_seed48_f050` with top-k 6 and
`frontier_random050_50x24_h5_seed47_f075` with top-k 12. A near-pass 50x24/top12
seed48 row was reported only as diagnostic_near_pass. All Stage 3 rollouts
used five seeds, 100 steps, horizon 5, global top-k 50, executable masks,
blend candidate scoring and candidate-value-weight 0.1. The later 2026-06-20
candidate-score sweep on `frontier_random050_50x24_h5_seed48_f075` tested
blend weights `0.05`, `0.10`, `0.15`, `0.25` and pure `value` filtering; the
best variant remained `blend0.10`, but it still failed to beat the matched
Paper9 baseline. The matched Paper9 baseline used the `rank_seed2028`
checkpoint under the same rollout settings. The pairwise-only baseline policy
remains unresolved unless the author explicitly accepts the matched Paper9
baseline as that comparator.

### 2.6 Dongxing/Neijiang Protocol

Dongxing/Neijiang is used as an external-region calibration and transfer
stress test. The environment loaded 3711 blocks from 76,376 parcel
assignments. Bishan checkpoints could initialize compatible Dongxing model
tensors while reinitializing action-space-specific embeddings. The experiments
then compared pairwise-only training with real-environment return-label
scaling at 20x16 and 50x16, and also tested low-label budgets of 5, 10 and 20
states.

The Dongxing design is not a pure transfer-superiority benchmark. It is a
stress test of whether the workflow can run in a second real environment,
whether local return labels improve planning, and whether Bishan initialization
is useful under constrained label budgets. The current evidence shows return
label scaling helps both transfer and scratch families, while low-label and
50x16 comparisons remain mixed between transfer and scratch.

### 2.7 Evaluation and Reporting Policy

The primary reported outcome is 100-step rollout total reward. Secondary
reported outcomes are final slope change, final contiguity change and final
baimu-area change. Bishan rows are reported over five rollout seeds. Dongxing
family rows aggregate three initialization checkpoints and five rollout seeds
per checkpoint. All current results are descriptive: means, sample standard
deviations, minima, maxima and condition-specific comparisons are reported
without formal hypothesis-test wording.

## 3. Results

### 3.1 Monitor Gates Selected the Bishan Value-Label Targets

The monitor gate selected trainable Bishan value-label targets before
value-head training. The 10x12/horizon-5 seed43 pilot selected top-4, with
candidate regret 0.4923, candidate overlap 0.5000 and one-step regret 1.2916.
The 20x16/horizon-5 seed44 row selected top-5, with candidate regret 0.1877,
candidate overlap 0.6300 and one-step regret 2.4626. These diagnostics support
using the 20x16/top5 labels for the primary Bishan value-filter test.

### 3.2 Bishan 20x16/top5 Exceeded the Matched Paper9 Baseline

The validated Bishan 20x16/top5 value-filter anchor remains the primary
positive result. Across five 100-step rollout seeds, the 20x16/top5 value
filter reached 69.4705 mean reward with sample standard deviation 1.0004. In
the Stage 3 matched comparison, the Paper9 `rank_seed2028` baseline reached
67.5437 mean reward with sample standard deviation 7.2246. The post-CEUS
matched 5-seed audit (`e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md`)
links these summary values to tracked raw rollout files and the seed0 pilot
audit. The anchor therefore exceeded the matched Paper9 baseline by 1.9269
reward units and showed lower seed-level variation under the tested rollout
protocol, while seed-level deltas remained mixed: value-filter won seeds 1-3
and lost seeds 0 and 4.

Relative to the earlier 10x12/top4 pilot, the 20x16/top5 value filter also
improved five-seed mean reward from 65.2566 to 69.4705 and reduced sample
standard deviation from 5.0037 to 1.0004. The mean slope, contiguity and
baimu-area metrics did not all move in the same direction, so the safest
interpretation is improved reward and weak-seed behavior under the implemented
reward definition rather than universal improvement across every planning
indicator.

### 3.3 Stage 3 Did Not Support Broad 50-State Scale-Up

Stage 3 trained and rolled out only the authorized Bishan rows from the
original-vision validation pass. The confirmatory 50-state row
`frontier_random050_50x16_h5_seed48_f050` selected top-k 6 and reached 64.2960
mean reward, 3.2477 below the matched Paper9 baseline. The confirmatory row
`frontier_random050_50x24_h5_seed47_f075` selected top-k 12 and reached
66.2544 mean reward, 1.2893 below the matched baseline. These confirmatory
rows completed value-filter rollout but did not improve on the comparator.
They should therefore be reported as a scale boundary, not as a positive
50-state result.

A later 2026-06-20 candidate-score sweep on the same
`frontier_random050_50x24_h5_seed48_f075` checkpoint varied
`candidate-score-mode` across `blend` weights `0.05`, `0.10`, `0.15`, `0.25`
and pure `value`. `blend0.10` remained the best candidate-filter variant at
67.4913 mean reward, but it still remained below the matched Paper9 baseline;
pure `value` filtering was materially worse. Candidate-score tuning therefore
reinforced the boundary interpretation rather than rescuing the 50x24/f075
line.

### 3.4 Diagnostic Near-Pass Evidence Remained Separate

The diagnostic_near_pass row `frontier_random050_50x24_h5_seed48_f075`
selected top-k 12 and reached 67.4913 mean reward, 0.0524 below the matched
Paper9 baseline. This row is useful because it shows a near-baseline failure
mode under the same rollout settings. It must not be pooled with the
confirmatory rows or used to imply that Stage 3 established a broad 50-state
claim. The later candidate-score sweep reached the same best mean reward at
`blend0.10`, confirming that the near-pass remains a boundary case rather than
confirmatory success.

### 3.5 Mechanism Ablation Identified Executable Masks as Rollout-Critical

The mechanism packet compared four matched Bishan rollout conditions under the
same 20x16/top5 protocol. The full gated masked condition reached 69.4705 mean
reward with sample standard deviation 1.0004, exceeding the heuristic Paper9
masked reference at 67.5437 with sample standard deviation 7.2246. Removing
the executable mask collapsed mean reward to 40.3515 and produced 100 zero-
swap steps and 98 negative-zero-swap steps, which indicates that the planner
repeatedly chose blocks that did not execute useful paired swaps. The ungated
top-4 control recorded the same mean reward and sample standard deviation as
the full gated masked anchor, so the monitor gate should be framed as
upstream label-quality control and escalation filtering rather than as an
independent source of online rollout gain. Supplementary Table S3 records this
four-condition packet.

### 3.6 Dongxing Required Planner Calibration

The Dongxing/Neijiang package established that the workflow could execute in a
second real county-level environment. The action space contained 3711 blocks
from 76,376 parcel assignments, requiring action-space adaptation when loading
Bishan-initialized checkpoints. The planner did not reuse the Bishan
candidate-value-weight setting unchanged. Dongxing return-label rollouts used
candidate-value-weight=1.0, compared with the Bishan default 0.1, supporting
the interpretation that value filtering is a calibratable component in a
planning-support workflow.

### 3.7 Dongxing Return Labels Improved Transfer and Scratch Families

In Dongxing, real-environment return-label scaling improved both
Bishan-initialized transfer and Dongxing scratch families relative to
pairwise-only labels. Pairwise-only transfer reached 37.8894 mean reward, and
pairwise-only scratch reached 40.2111. With 50x16 return labels, transfer
increased to 51.6183 and scratch increased to 55.7324. The strongest family
mean in this comparison was scratch 50x16, not transfer 50x16, so the result
supports local calibration and return-label scaling rather than robust
transfer superiority.

### 3.8 Low-Label Dongxing Transfer Was Mixed

The Dongxing low-label stress test further bounds the transfer claim. At 5
labels, scratch had higher mean reward than transfer (50.3654 versus
41.6380). At 10 labels, scratch again had higher mean reward (47.7970 versus
44.3382). At 20 labels, transfer had higher mean reward than scratch (44.7080
versus 40.4596). Transfer showed stronger slope reduction, while scratch
showed stronger contiguity and baimu-area outcomes. These mixed outcomes
should remain visible in the manuscript package.

## 4. Discussion

The Stage 3 evidence changes the manuscript from a scale-up story into a
claim-boundary story. The strongest supported contribution is not that larger
value-label sets automatically improve GeoJEPA-MPC planning. It is that
monitor gates can separate a useful value-label scale from label sets that
remain unsuitable for manuscript-facing escalation.

This interpretation also clarifies why the failed 50-state results strengthen
the paper rather than merely weaken it. The 20x16/top5 anchor beat the matched
Paper9 baseline and stabilized five-seed rollout rewards, while the
confirmatory 50-state rows failed to beat that comparator. The later
candidate-score sweep on the same 50x24/f075 checkpoint did not rescue the
boundary. The monitor-gated workflow therefore functions as an evidence-control
layer: it tells the user when value filtering is useful under a particular
data, candidate and rollout configuration, and when additional label scale is
not enough.

The mechanism packet sharpens the causal reading of that positive anchor. The
executable mask is rollout-critical: removing it dropped mean reward from
69.4705 to 40.3515 and produced 100 zero-swap and 98 negative-zero-swap
steps. By contrast, the ungated top-4 control did not produce a distinct
online improvement over the gated anchor under the same rollout protocol. The
monitor gate therefore belongs in the paper as a label-quality and
evidence-control mechanism, not as the direct source of the reward gain.

The Dongxing results add planning-support relevance because they show that the
workflow can be adapted to a second real environment and can identify where
local calibration is needed. Return-label scaling improved both transfer and
scratch families, but scratch remained stronger in the 50x16 family mean and
at the 5-label and 10-label budgets. This pattern argues against a simplified
interpretation in which copied Bishan weights alone explain the result. It also
prevents the stronger claim that Bishan-initialized transfer is robustly
superior to local scratch adaptation.

The current spatial abstraction is a practical limitation for CEUS readers.
The experiments optimize a block-level planning-unit abstraction under queen
contiguity, not arbitrary irregular cadastral parcel exchange. Operational
deployment would need area-tolerance matching, shared-perimeter-weighted
contiguity, shape compactness and explicit parcel-geometry constraints. The
local Bishan and Dongxing shapefile/GPKG roots found under `D:\test` make such
audits feasible after data rights are clarified, but the present draft should
not claim that those extensions have already been evaluated.

The soft training and hard inference design should also be stated plainly.
Reward and count penalties shape value labels and learned rankings, while
executable masks and paired inference enforce rollout feasibility. This design
is consistent with a planning-support workflow that uses learned scores as a
filtered recommendation layer. It is not evidence that the implementation is a
full constrained reinforcement-learning solver or that it implements
Constrained MDP, CPO, or RCPO algorithms.

Several limitations remain before submission. First, the current evidence is
two-region and descriptive. Broader generalization claims require additional
external regions and a predefined comparison protocol. Second, the
pairwise-only baseline policy remains unresolved unless the author explicitly
accepts the matched Paper9 `rank_seed2028` baseline as that comparator. Third,
full Bishan, GPKG-root and Dongxing/Neijiang prepared data routes are not yet
deposited or assigned to controlled access. These are submission blockers for
a final CEUS package, not minor wording issues.

## 5. Conclusion

Paper10 supports monitor-gated value filtering with executable masking as a
calibrated workflow for constrained farmland layout planning. The validated
Bishan 20x16/top5 value filter improved reward relative to the matched Paper9
baseline, and the mechanism ablation shows that executable masks are
rollout-critical, but Stage 3 confirmatory 50-state rows did not, and the
later candidate-score sweep on the 50x24/f075 line did not overturn that
boundary. The manuscript should therefore claim a bounded, reproducible
evidence-control workflow for GeoJEPA-MPC planning, not direct 50-state Bishan
scale-up success, solved irregular parcel deployment or robust Bishan-to-Dongxing
transfer superiority.

## Data and Code Availability

This statement is a CEUS-facing draft and must be backfilled after the author
team selects repository identifiers, licences and controlled-access routes.

The data supporting the packaged analyses will be mapped through a versioned
Paper10 repository archive and associated data records. The repository archive
is intended to contain the custom code, tests, scripts, small reviewer smoke
dataset, generated value-label files, monitor outputs, rollout summaries,
figure-ready CSV source data, manuscript table source notes, saved checkpoints
and metadata needed to inspect the reported Bishan 10x12/top4, Bishan
20x16/top5, Bishan Stage 3 confirmatory 50-state boundary and Dongxing summary
results. The repository DOI or anonymous reviewer link is pending and must be
added before submission.

The full Bishan Tool2 transition and pairwise datasets are external to Git
because they are large binary scientific data. Full Bishan reruns also require
the prepared GPKG-root geospatial inputs, block products and township inputs.
These data must be deposited in a durable repository if redistribution rights
allow, or assigned to a controlled institutional access route with public
metadata, eligible requester criteria, review procedure, reviewer access and
data-use terms.

The Dongxing/Neijiang prepared data are also external to Git. The tracked
repository contains derived Dongxing summary tables and figure source CSVs,
but full external-region reruns require prepared block products, parcel
assignments, transition trajectories, pairwise labels, environment wrapper
files and slope-enriched geospatial inputs. These files need a public data
record or a controlled-access metadata record before final submission.

All custom code used for the packaged analyses is in the Paper10 repository.
The software licence and generated-output rights terms remain pending author
or institutional decisions. The final archive metadata should cite the exact
submission commit and map each figure and table to its source data.

## Figure and Table List

| item | role | source-data route |
|---|---|---|
| Main Figure 1 | Monitor-gated value filtering workflow. | Code modules and workflow source map. |
| Main Figure 2 | Bishan 20x16/top5 reward and stability. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`; rollout summaries. |
| Main Figure 3 | Bishan Stage 3 50-state boundary. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`; `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`. |
| Main Figure 4 | Dongxing return-label scaling. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`. |
| Supplementary Figure S1 | Dongxing low-label transfer stress test. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`. |
| Main Table 1 | Bishan monitor-selected gates. | Monitor JSON files and integrated table package. |
| Main Table 2 | Bishan matched-baseline rollout comparison. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`; Stage 3 summary JSON. |
| Main Table 3 | Dongxing return-label scaling. | Dongxing family summary CSV and integrated table package. |
| Supplementary Table S1 | Stage 3 seed-level rollout rewards. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`. |
| Supplementary Table S2 | Dongxing low-label stress test. | Dongxing low-label summary CSV and detailed result note. |
| Supplementary Table S3 | Mechanism ablation and control comparison. | `e0_paper10_mechanism_ablation_packet_2026-06-20.md`; `e0_paper10_mechanism_ablation_packet_2026-06-20.json`. |

## Claim-Evidence and Unresolved Blockers

| claim or blocker | manuscript status | evidence or required action |
|---|---|---|
| Monitor-gated Bishan labels train a useful value filter at the validated anchor scale. | Supported descriptively. | Bishan 20x16/top5 mean reward 69.4705 versus matched Paper9 baseline 67.5437; sample standard deviation 1.0004 versus 7.2246; post-CEUS matched 5-seed audit records wins on 3/5 seeds and losses on seeds 0 and 4. |
| Executable mask is rollout-critical. | Supported. | full_gated_masked mean reward 69.4705 versus no_mask 40.3515; no_mask produced 100 zero-swap steps and 98 negative zero-swap steps. |
| Ungated top-4 control improves on the gated anchor. | Not supported. | ungated_top4 matched full_gated_masked at 69.4705 mean reward and 1.0004 sample std under the same rollout protocol. |
| Stage 3 confirmatory 50-state rows improve on the matched Paper9 baseline. | Not supported. | 50x16/top6 mean reward 64.2960 and 50x24/top12 mean reward 66.2544, both below the matched Paper9 baseline. Do not claim direct 50-state Bishan scale-up success. |
| Candidate-score tuning rescues the 50x24/f075 line. | Not supported. | The 2026-06-20 sweep over `blend` 0.05/0.10/0.15/0.25 and `value` kept the best candidate-filter result at 67.4913, still below the matched Paper9 baseline. |
| The diagnostic near-pass row can strengthen the confirmatory 50-state claim. | Not supported. | diagnostic_near_pass 50x24/top12 seed48 mean reward 67.4913, still below baseline by 0.0524, and must not be pooled with confirmatory rows. |
| Paper10 runs in a second real county-level environment. | Supported with access-route boundary. | Dongxing/Neijiang loaded 3711 blocks and completed return-label training and rollout summaries. |
| Dongxing return-label scaling improves planning families. | Supported descriptively. | Transfer increased from 37.8894 to 51.6183; scratch increased from 40.2111 to 55.7324. |
| Bishan-to-Dongxing transfer is robustly superior. | Not supported. | Scratch remains higher at 50x16 and at 5-label and 10-label low-budget settings. Do not claim robust Bishan-to-Dongxing transfer superiority. |
| Irregular cadastral parcel deployment is solved. | Not supported. | Current evidence uses block-level planning-unit abstraction and queen contiguity; area-tolerance matching and shared-perimeter-weighted contiguity remain future extensions. |
| Pairwise-only baseline policy. | Submission blocker. | Decide whether the matched Paper9 baseline is the accepted comparator or run/report a separately identified pairwise-only baseline. |
| Full data access route. | Submission blocker. | Choose public DOI or controlled-access records for full Bishan Tool2, GPKG-root geospatial data and Dongxing/Neijiang prepared data. |
| Code and generated-output rights. | Submission blocker. | Select software licence, generated-output rights terms and model/checkpoint rights terms. |
| Citation and reference style. | Submission blocker. | Use verified public sources; keep the self-contained Paper10 Methods route unless Paper9 becomes public. |
| Statistical reporting. | Submission blocker. | Current draft uses descriptive evidence only; formal hypothesis-test language requires a predefined statistical plan. |

## Chinese Author Notes

- 这份文件是 2026-06-18 Stage 3 之后的完整 CEUS manuscript draft，不是最终投稿稿。
- 论文主线已经从“50-state scale-up 成功”改为“monitor-gated value labels 作为证据控制流程”。
- 目前可以支持 Bishan 20x16/top5 相对 matched Paper9 baseline 的正向结果。
- 目前不能支持 direct 50-state Bishan scale-up success，也不能支持 robust Bishan-to-Dongxing transfer superiority。
- 下一步需要作者明确 pairwise-only baseline 政策、repository DOI/reviewer link、license、full-data access route、citation policy 和 statistical reporting policy。
