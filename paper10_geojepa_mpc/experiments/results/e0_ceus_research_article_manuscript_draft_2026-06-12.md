# Paper10 CEUS Research Article Manuscript Draft

Date: 2026-06-12

Status: CEUS Research Article candidate draft. This file is a manuscript-facing
conversion draft, not a final submission package. It preserves the unresolved
repository DOI, licence, full-data access, citation-policy, statistical-policy,
and final figure-export blockers tracked in
`e0_submission_blocker_decision_packet_2026-06-11.md`.

Stage 3 update: use
`e0_ceus_stage3_manuscript_reframe_2026-06-18.md` as the current
manuscript-facing claim boundary before editing this draft. The 2026-06-18
Stage 3 confirmatory rollouts showed that the tested confirmatory 50-state
rows did not beat the matched Paper9 baseline, so this older 2026-06-12 draft
must not be converted into a final manuscript without the Stage 3 replacement
title, abstract, Results, Discussion and Conclusion.

Source controls used for this conversion:

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_ceus_reviewer_improvement_packet_2026-06-12.md`

Paper9 has not been formally submitted. This draft therefore uses the
self-contained Paper10 Methods route and does not cite the local Paper9
placeholder in public manuscript text.

## One-Sentence Argument

In constrained farmland layout planning, we show that monitor-gated
GeoJEPA-MPC value filtering improves the Bishan 20x16/top5 real-environment
rollout and can be calibrated in a Dongxing/Neijiang external-region stress
test, supported by source-mapped descriptive evidence, with the boundary that
direct 50-state Bishan scaling, arbitrary irregular cadastral parcel exchange,
and robust Bishan-to-Dongxing transfer superiority are not supported by the
current experiments.

## Terminology Ledger

| canonical term | first-use definition | conversion rule |
|---|---|---|
| GeoJEPA-MPC | A geospatial JEPA and model-predictive planning workflow for constrained farmland layout planning. | Use as the method name throughout the draft. |
| monitor gate | A pre-training candidate-label quality check applied before value-head training and claim escalation. | Present as a guardrail, not as an after-the-fact explanation. |
| value label | A finite-horizon return label generated for candidate actions. | State label scale, horizon, candidate count, and selected top-k when reporting evidence. |
| value filter | The trained scalar value head used to filter candidate swaps before rollout scoring. | Link performance claims to the Bishan 20x16/top5 and Dongxing return-label evidence. |
| executable mask | A hard action mask that removes infeasible block swaps before candidate selection. | Use for inference and rollout enforcement. |
| block-level planning-unit abstraction | The implemented planning abstraction in which actions select blocks rather than arbitrary individual parcels. | State as a current boundary for CEUS readers. |
| queen contiguity | The implemented adjacency abstraction for current environment topology. | State shared-perimeter-weighted contiguity as a future irregular-parcel extension. |
| soft training and hard inference | Reward and count penalties guide training labels, while executable masks and paired inference enforce rollout feasibility. | Do not describe the implementation as a Constrained MDP, CPO, or RCPO solver. |
| Dongxing/Neijiang | The external-region package with 3711 blocks and 76,376 parcel assignments. | Use as calibration and stress-test evidence, not as robust transfer proof. |

## Title

Monitor-gated value filtering for GeoJEPA-MPC farmland layout planning

## Highlights

- Monitor gates audit value labels before GeoJEPA-MPC training.
- Bishan 20x16/top5 improved five-seed reward by 6.46%.
- Tested 50-state Bishan labels failed monitor gates.
- Dongxing return-label scaling supported planner calibration.
- Mixed transfer results bound cross-region claims.

## Abstract

Constrained farmland layout planning requires sequential spatial decisions
that improve slope, contiguity and area objectives while preserving executable
swap constraints. Learned world-model planners can evaluate candidate actions,
but one-step rewards do not necessarily provide stable long-horizon rankings,
and larger return-label sets can degrade candidate quality. We present a
monitor-gated GeoJEPA-MPC workflow that generates finite-horizon value labels,
audits label quality before training, trains a value filter only for accepted
label sets and applies hard executable masks during rollout. In the Bishan
real-environment setting, a 20-state, 16-candidate, horizon-5 label set
selected a top-5 gate and improved five-seed 100-step mean reward from 65.2566
to 69.4705 relative to the 10x12/top4 pilot, while sample standard deviation
decreased from 5.0037 to 1.0004. Tested 50-state Bishan label sets failed the
monitor gates, defining a current scale-up boundary. In the Dongxing/Neijiang
setting, return-label scaling increased mean reward for both Bishan-initialized
transfer and Dongxing scratch families, with the strongest family result from
scratch 50x16 labels (55.7324). Dongxing planning also required
candidate-value-weight=1.0, showing that value filtering is a calibratable
planning component rather than a universal checkpoint. These descriptive
two-region results support monitor-gated value filtering as a reproducible
planning-support workflow, while bounding claims about arbitrary cadastral
parcel deployment, direct 50-state scaling and robust cross-region transfer
superiority.

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
constraints. Model-predictive control provides a natural template for such
rolling finite-horizon decision making [@mayne2014mpc_future_promise;
@rawlings2017model_predictive_control], while learned world models show how
latent dynamics can support candidate rollout and search [@ha2018recurrent_world_models;
@hafner2019planet].

Value functions can improve candidate selection, but using value labels in
geospatial planning creates an additional quality-control problem. A larger
label set is useful only if the generated returns preserve meaningful
candidate rankings and if the resulting value filter remains compatible with
hard feasibility masks during rollout. JEPA-style predictive representations
motivate learning in an embedding space rather than by reconstructing raw
inputs [@assran2023ijepa], but the manuscript-facing claim in this paper is
not that representation learning alone solves farmland planning. The claim is
that value labels need explicit monitoring before they are used to train a
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
positive result: a monitor-selected 20x16/top5 value-label setting improved
100-step five-seed rollout reward and reduced seed-level variation relative to
a 10x12/top4 pilot. Tested 50-state Bishan labels failed monitor gates and are
reported as a scale boundary, not as affirmative scale-up evidence.
Dongxing/Neijiang then tests whether the workflow can be adapted in a second
real environment. Return-label scaling improved both transfer and scratch
families, but scratch remained stronger in several settings, so the paper
does not claim robust Bishan-to-Dongxing transfer superiority.

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
rather than silently converting them into model checkpoints. The tested
50-state Bishan rows failed default and post-hoc monitor checks and were not
used as affirmative scale-up training evidence.

### 2.5 Bishan Protocol

Bishan is the primary validation environment for the current draft. The
paper-facing route uses the GPKG-root prepared-data convention that resolves
`dem_slope_analysis/output/DLTB_with_slope.gpkg`, because the local
reproduction audit matched the packaged 20x16/horizon-5 seed44 label arrays
under that root. Full reruns require the external full Bishan Tool2 transition
and pairwise data plus prepared geospatial inputs; the Git repository includes
smoke data, generated value labels, monitor outputs, checkpoints, rollout
summaries and figure-ready source data.

The Bishan evidence compares a 10-state, 12-candidate, horizon-5 pilot with a
20-state, 16-candidate, horizon-5 scale-up. The monitor selected top-4 for the
10x12 pilot and top-5 for the 20x16 row. Rollouts used executable masks,
100-step episodes, five seeds and the same value-filter planner settings
except for the trained value head and selected top-k.

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

### 3.2 Bishan 20x16/top5 Improved Reward and Seed Stability

The monitor-selected 20x16/top5 value filter improved the Bishan 100-step
rollout relative to the 10x12/top4 pilot. Mean total reward increased from
65.2566 to 69.4705, a +4.2139 absolute change and +6.46% relative change.
Sample standard deviation decreased from 5.0037 to 1.0004, and the minimum
seed reward increased from 57.9750 to 67.7135. The mean slope, contiguity and
baimu-area metrics did not all move in the same direction, so the safest
interpretation is improved reward and weak-seed behavior under the implemented
reward definition rather than universal improvement across every planning
indicator.

### 3.3 Tested Bishan 50-State Labels Defined a Scale Boundary

The tested Bishan 50-state label sets failed monitor gates and should be read
as boundary evidence. The macOS 50x24/horizon-5 seed45 row and Windows seed46
50-state rows did not pass top-3, top-4 or top-5 default monitor checks. The
least-bad default top-k was top-5 for each row, but the monitor decision
remained `stop`. These results indicate that larger Bishan label sets are not
automatically trainable under the current candidate proposal and monitoring
design.

### 3.4 Dongxing Required Planner Calibration

The Dongxing/Neijiang package established that the workflow could execute in a
second real county-level environment. The action space contained 3711 blocks
from 76,376 parcel assignments, requiring action-space adaptation when loading
Bishan-initialized checkpoints. The planner did not reuse the Bishan
candidate-value-weight setting unchanged. Dongxing return-label rollouts used
candidate-value-weight=1.0, compared with the Bishan default 0.1, supporting
the interpretation that value filtering is a calibratable component in a
planning-support workflow.

### 3.5 Dongxing Return Labels Improved Transfer and Scratch Families

In Dongxing, real-environment return-label scaling improved both
Bishan-initialized transfer and Dongxing scratch families relative to
pairwise-only labels. Pairwise-only transfer reached 37.8894 mean reward, and
pairwise-only scratch reached 40.2111. With 50x16 return labels, transfer
increased to 51.6183 and scratch increased to 55.7324. The strongest family
mean in this comparison was scratch 50x16, not transfer 50x16, so the result
supports local calibration and return-label scaling rather than robust
transfer superiority.

### 3.6 Low-Label Dongxing Transfer Was Mixed

The Dongxing low-label stress test further bounds the transfer claim. At 5
labels, scratch had higher mean reward than transfer (50.3654 versus
41.6380). At 10 labels, scratch again had higher mean reward (47.7970 versus
44.3382). At 20 labels, transfer had higher mean reward than scratch (44.7080
versus 40.4596). Transfer showed stronger slope reduction, while scratch
showed stronger contiguity and baimu-area outcomes. These mixed outcomes
should remain visible in the manuscript package.

## 4. Discussion

The central contribution is a monitor-gated value-filtering workflow for
GeoJEPA-MPC farmland layout planning, not a universal cross-region transfer
claim. The Bishan 20x16/top5 result shows that a monitored finite-horizon
return-label set can train a value filter that improves rollout reward and
reduces seed-level variation under executable masks. The failed Bishan
50-state rows show why the monitor gate is necessary: increasing label scale
does not by itself preserve useful candidate rankings.

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
external regions and a predefined comparison protocol. Second, no external
optimizer baseline suite has been added under equal budgets, feasibility
constraints and seed design. Third, full Bishan, GPKG-root and
Dongxing/Neijiang prepared data routes are not yet deposited or assigned to
controlled access. These are submission blockers for a final CEUS package, not
minor wording issues.

## 5. Conclusion

Monitor-gated value labels improved GeoJEPA-MPC rollouts at the validated
Bishan 20x16/top5 scale and enabled a Dongxing/Neijiang calibration study in a
second real environment. The same experiments define the current boundary:
tested Bishan 50-state labels failed monitor gates, Dongxing required local
planner calibration, and Bishan-initialized transfer did not robustly
outperform scratch adaptation. Paper10 should therefore claim a reproducible,
monitor-gated calibration workflow for constrained geospatial planning, not
broad transfer superiority or solved irregular cadastral parcel deployment.

## Data and Code Availability

This statement is a CEUS-facing draft and must be backfilled after the author
team selects repository identifiers, licences and controlled-access routes.

The data supporting the packaged analyses will be mapped through a versioned
Paper10 repository archive and associated data records. The repository archive
is intended to contain the custom code, tests, scripts, small reviewer smoke
dataset, generated value-label files, monitor outputs, rollout summaries,
figure-ready CSV source data, manuscript table source notes, saved checkpoints
and metadata needed to inspect the reported Bishan 10x12/top4, Bishan
20x16/top5, Bishan 50-state diagnostic and Dongxing summary results. The
repository DOI or anonymous reviewer link is pending and must be added before
submission.

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
| Main Figure 2 | Bishan 20x16/top5 reward and stability. | `e0_frontier_random050_seedwise_rewards_2026-06-09.csv`; rollout summaries. |
| Main Figure 3 | Bishan 50-state monitor boundary. | `e0_frontier_random050_topk_diagnostics_2026-06-09.csv`; 50-state audit notes. |
| Main Figure 4 | Dongxing return-label scaling. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`. |
| Supplementary Figure S1 | Dongxing low-label transfer stress test. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`. |
| Main Table 1 | Bishan monitor-selected gates. | Monitor JSON files and integrated table package. |
| Main Table 2 | Bishan rollout improvement and stability. | Bishan rollout summary JSON files and integrated table package. |
| Main Table 3 | Dongxing return-label scaling. | Dongxing family summary CSV and integrated table package. |
| Supplementary Table S1 | Bishan 50-state monitor-gate boundary. | Windows and macOS 50-state diagnostic notes. |
| Supplementary Table S2 | Dongxing low-label transfer stress test. | Dongxing low-label summary CSV and detailed result note. |

## Claim-Evidence and Unresolved Blockers

| claim or blocker | manuscript status | evidence or required action |
|---|---|---|
| Monitor-gated Bishan labels train a useful value filter. | Supported. | 20x16/top5 mean reward 69.4705, sample standard deviation 1.0004 and monitor gate continuation. |
| Larger Bishan labels are automatically better. | Not supported. | Tested 50-state rows failed monitor gates. Do not claim direct 50-state Bishan scale-up success. |
| Paper10 runs in a second real county-level environment. | Supported with access-route boundary. | Dongxing/Neijiang loaded 3711 blocks and completed return-label training and rollout summaries. |
| Dongxing return-label scaling improves planning families. | Supported descriptively. | Transfer increased from 37.8894 to 51.6183; scratch increased from 40.2111 to 55.7324. |
| Bishan-to-Dongxing transfer is robustly superior. | Not supported. | Scratch remains higher at 50x16 and at 5-label and 10-label low-budget settings. Do not claim robust Bishan-to-Dongxing transfer superiority. |
| Irregular cadastral parcel deployment is solved. | Not supported. | Current evidence uses block-level planning-unit abstraction and queen contiguity; area-tolerance matching and shared-perimeter-weighted contiguity remain future extensions. |
| Full data access route. | Submission blocker. | Choose public DOI or controlled-access records for full Bishan Tool2, GPKG-root geospatial data and Dongxing/Neijiang prepared data. |
| Code and generated-output rights. | Submission blocker. | Select software licence, generated-output rights terms and model/checkpoint rights terms. |
| Citation and reference style. | Submission blocker. | Use verified public sources; keep the self-contained Paper10 Methods route unless Paper9 becomes public. |
| Statistical reporting. | Submission blocker. | Current draft uses descriptive evidence only; formal hypothesis-test language requires a predefined statistical plan. |

## Chinese Author Notes

- 这份文件已经按 CEUS Research Article candidate route 写成英文稿件草稿，但还不是最终投稿稿。
- public manuscript 继续走 self-contained Paper10 Methods route，不依赖尚未正式投稿的 Paper9。
- 当前不建议补外部优化器 baseline，除非先制定公平预算、约束、seed 和指标协议。
- 下一步最关键的作者决策仍是 repository DOI/reviewer link、代码许可证、full Bishan/GPKG/Dongxing 数据访问路线，以及是否继续保持 descriptive-only statistical reporting。
