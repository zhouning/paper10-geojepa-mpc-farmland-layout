# Paper10 PCC-GeoJEPA-MPC Substantive Revision Design

Date: 2026-07-10

Status: user-approved design for algorithm, experiment, manuscript, and figure revision

Target journal: *Computers, Environment and Urban Systems* (CEUS)

## 1. Objective

Paper10 will be rebuilt around a deployable, no-oracle planning algorithm rather
than around evidence governance or an oracle action audit. The revised work must
make a substantive algorithmic contribution and must pass a confirmatory protocol
that was fixed before the confirmatory results were observed.

The central scientific argument is:

> In multi-objective farmland layout planning, PCC-GeoJEPA-MPC uses
> region-independent action representations, calibrated ensemble predictions,
> and conservative Pareto policy improvement to improve cumulative reward without
> materially degrading slope, contiguity, or connected farmland area, while using
> only information available to a deployable planner.

The design does not guarantee that the empirical success criteria will be met.
It guarantees that the implementation and experiment will make success or failure
scientifically interpretable. No claim will be rescued through post-confirmation
metric, seed, baseline, or threshold changes.

## 2. Locked Scientific Boundaries

### 2.1 Online information set

At decision time, the proposed algorithm may use only:

- the current observable state and executable-action mask;
- models, calibration objects, and reference policies frozen before the
  confirmatory experiment;
- predicted outcomes for candidate actions;
- outcomes observed after the planner executes its chosen action; and
- the history of previously executed actions and their observed outcomes.

The algorithm must not:

- query the real environment reward for an unexecuted candidate action;
- clone, rewind, or restore the real environment to evaluate counterfactual
  actions at decision time;
- use the original true-reward action-audit guard as a deployable component; or
- update model weights or selection thresholds from confirmatory outcomes.

Counterfactual environment rollouts are allowed only during offline training and
calibration on the designated training and calibration partitions. The oracle
action audit remains a labelled diagnostic upper bound in supplementary analyses.

### 2.2 Empirical success condition

All objectives are oriented so that larger values are better:

- cumulative reward: reported reward;
- slope benefit: `-slope_change_pct`;
- contiguity benefit: `cont_change`; and
- connected-area benefit: `baimu_area_change_ha`.

The main claim is supported only if all of the following hold:

1. On the independent Bishan confirmation partition, the one-sided 95% lower
   confidence bound for the paired cumulative-reward difference between
   PCC-GeoJEPA-MPC and the strongest frozen no-oracle baseline is greater than
   zero.
2. For each of the three planning benefits, the one-sided 95% lower confidence
   bound for the paired difference is at least zero. This is a zero-margin
   non-inferiority rule and therefore does not permit a claimed reward gain to be
   purchased by degradation of a planning metric.
3. The conclusion is obtained for at least two of three independent training
   seeds and for the hierarchical aggregate across training and rollout seeds.
4. A matched-compute PCC configuration reaches the same qualitative conclusion.
5. On Dongxing, the paired reward point estimate is positive and the one-sided
   95% lower confidence bound is non-negative; the one-sided 95% lower confidence
   bound is also non-negative for each of the three planning benefits under the
   frozen external-confirmation protocol.
6. Runtime logging confirms that no unexecuted action was evaluated with the real
   environment.

The oracle diagnostic, historical seeds 0-19, and any development experiment are
excluded from this success decision.

## 3. Terminology Ledger

| Canonical term | Definition | Terms not used as substitutes |
|---|---|---|
| PCC-GeoJEPA-MPC | Pareto-Calibrated Conservative GeoJEPA-MPC | true-reward guard, validation framework |
| reference policy | Frozen no-oracle policy `pi_b` used for conservative improvement and fallback | oracle baseline |
| action-relative representation | Candidate representation derived from candidate block features and state context, without an action-ID embedding | transferable action ID |
| objective vector | Reward, slope benefit, contiguity benefit, and connected-area benefit | scalar reward |
| joint conformal bound | Simultaneous calibrated interval over the candidate-versus-reference objective difference | uncertainty score |
| executed-feedback calibration | Online scale update using only outcomes of executed actions | online counterfactual calibration |
| oracle action-audit diagnostic | Privileged true-reward action audit used only as an upper-bound analysis | deployable planner |
| confirmation partition | Frozen, previously unseen rollout seeds used exactly once for the primary analysis | test set used for tuning |

## 4. Considered Approaches

### 4.1 Selected approach: calibrated ensemble Pareto improvement

The selected design combines an action-relative ensemble world model, multi-objective
return prediction, joint paired conformal calibration, conservative Pareto action
selection, fallback to a frozen reference policy, and executed-feedback residual
scaling. It directly addresses the three observed failure modes: privileged reward
access, model overconfidence, and conflict between scalar reward and planning
metrics.

### 4.2 Secondary approach: distributional risk-sensitive planning

A quantile/CVaR version without executed-feedback calibration will be implemented
as a strong baseline and ablation. It tests whether distributional predictions
alone explain the result.

### 4.3 Secondary approach: online expert selection

A controller that selects among frozen no-oracle experts from observable context
and executed feedback will be implemented as a baseline. It tests whether the
full PCC mechanism improves beyond a policy ensemble. It is not the paper's main
algorithm because its novelty and performance ceiling are more limited.

## 5. PCC-GeoJEPA-MPC Architecture

### 5.1 Action-relative representation

The existing model includes `action_emb(action_id)`, which binds learned parameters
to a county-specific block index. PCC replaces it with a representation computed
from observable quantities:

- encoded features of the candidate block;
- the candidate block's existing connectivity and local-planning features;
- candidate-minus-county pooled feature differences;
- mean and max pooled county context;
- encoded global state, remaining budget, and episode progress; and
- a neighbourhood summary computed from the environment's fixed adjacency
  structure.

The main Bishan and Dongxing models require the neighbourhood summary. Only unit
tests and smoke fixtures without an adjacency graph may supply a documented
all-zero neighbourhood mask; such fixtures cannot produce manuscript evidence.

The representation must be invariant to a simultaneous permutation of block rows,
action indices, and the executable mask. A checkpoint must accept Bishan and
Dongxing action spaces without copying or reinitializing a county-specific action
embedding.

### 5.2 Bootstrap ensemble and outputs

The primary development grid permits ensemble sizes `K in {3, 5}`. Each member is
trained from a trajectory-level bootstrap sample and an independent parameter
seed. A member predicts:

- selected-block and global-state deltas;
- immediate reward and immediate planning-benefit vector;
- discounted objective vectors for horizons 1, 3, and 5;
- aleatoric log scales for each objective; and
- executable-action probability.

Ensemble dispersion represents epistemic uncertainty. Predicted log scales
represent conditional noise. Both are retained separately in result artifacts.

### 5.3 Training targets

For a state `s`, candidate action `a`, and frozen continuation policy `pi_b`, the
offline label generator records

```
Q_h^{pi_b}(s, a) = [R_h, S_h, C_h, B_h], h in {1, 3, 5},
```

where `R` is discounted cumulative reward and `S`, `C`, and `B` are oriented
planning benefits. Candidate actions are evaluated only in the designated offline
environment partitions. Candidate and continuation randomness is stored in the
artifact metadata.

The loss contains:

- Huber transition-delta loss;
- heteroscedastic Gaussian negative log likelihood for each objective and horizon;
- pairwise ranking loss for candidate-versus-reference objective differences;
- binary cross entropy for executable-action probability; and
- the existing representation regularizer when transition training is active.

Loss weights are normalized from training-partition target scales. Confirmation
data cannot affect normalization.

### 5.4 Paired joint conformal calibration

Calibration operates on candidate-versus-reference differences because the policy
decision is whether to depart from `pi_b`, not whether an isolated value estimate
is accurate.

For trajectory `t`, decision row `i`, objective `j`, and candidate `a_ti`, define

```
d_tij       = Q_j(s_ti, a_ti) - Q_j(s_ti, pi_b(s_ti))
d_hat_tij   = ensemble prediction of d_tij
u_tij       = combined epistemic and aleatoric scale
e_t         = max_i max_j |d_tij - d_hat_tij| / max(u_tij, epsilon)
```

The calibration unit is a complete independent trajectory, not a state within a
trajectory. The finite-sample split-conformal quantile of `e_t` produces one joint
multiplier for all decisions and all four objectives. This avoids pseudoreplication
and avoids treating four separately calibrated intervals as a joint guarantee.
Candidate lower bounds are

```
L_j(s, a) = d_hat_j(s, a) - q_joint * u_j(s, a).
```

The development grid permits target joint coverages `{0.80, 0.90, 0.95}`. The
chosen coverage is frozen before confirmation and empirical calibration coverage
is reported without retroactive adjustment.

### 5.5 Conservative Pareto selection

At each step, the frozen reference policy proposes `a_b`. The candidate pool is
the union of top candidates proposed by the ensemble mean, reward head,
distributional-risk baseline, and reference policy. Duplicate actions are removed
before compute accounting.

A candidate is admissible only if:

- its executable probability exceeds the frozen development threshold;
- `L_reward > 0`;
- `L_slope >= -tau_slope`;
- `L_contiguity >= -tau_contiguity`; and
- `L_connected_area >= -tau_connected_area`.

Development tolerances are expressed in training-partition robust standard-deviation
units and are selected from `{0.00, 0.05, 0.10}` by a lexicographic rule: first
maximize the number of planning objectives satisfying zero-margin non-inferiority
on development rollouts, then reward, then lower compute. Confirmation success
still uses the zero-margin rule in Section 2.2 regardless of the internal gate
tolerance.

Among admissible actions, the planner maximizes reward lower bound, followed by
the minimum planning-benefit lower bound, followed by lower uncertainty. If no
candidate is admissible, it executes `a_b`. Deterministic tie-breaking uses action
index only after all scientific scores are equal.

### 5.6 Executed-feedback calibration

After an action is executed, the algorithm observes its real next state, reward,
and planning benefits. These observations update a bounded residual scale for the
current region and episode phase. They do not update model weights.

Because the reference action is not executed when PCC selects another action,
online calibration must not construct a fictitious candidate-versus-reference
residual. It updates marginal prediction-error scales only. The fixed paired
conformal multiplier remains unchanged. The online scale multiplier is clipped to
`[1.0, 3.0]`, so online feedback may make the gate more conservative but may not
shrink intervals below their offline calibration width.

Development window sizes are `{10, 20}` executed actions. The initial window uses
the offline scale. An episode with missing or non-finite outcomes fails closed to
the reference policy and records the reason.

### 5.7 Offline conservative policy iteration

The training partition permits exactly two policy-improvement rounds:

```
pi_0 -> Q^{pi_0} -> pi_1 -> Q^{pi_1} -> pi_2.
```

`pi_0` is the frozen reference policy selected from no-oracle development
baselines. The model and calibration objects from `pi_1` and `pi_2` are compared
on the development partition using the same lexicographic rule. No third round is
allowed after inspecting confirmation results.

## 6. Data Flow and Artifact Boundaries

### 6.1 Bishan partitions

Historical seeds 0-19 and all artifacts produced before this design are
exploratory-only. New seed namespaces are:

- offline label-training trajectories: 1000-1007;
- offline conformal-calibration trajectories: 2000-2019;
- development rollouts: 3000-3009;
- confirmation rollouts: 4000-4019; and
- independent model-training seeds: 5101, 5102, and 5103.

### 6.2 Dongxing partitions

- local adaptation trajectories: 6000-6003;
- external calibration trajectories: 7000-7019; and
- external confirmation rollouts: 8000-8019.

Dongxing confirmation is never used to choose candidate-value weight, calibration
coverage, gate tolerance, ensemble size, or horizon. The model may adapt only on
the declared adaptation partition and must use the same action-relative
architecture.

### 6.3 Registry and state machine

A machine-readable protocol registry records:

- partition seeds and their roles;
- input checksums;
- model and bootstrap seeds;
- candidate hyperparameter grid;
- lexicographic selection rule;
- selected frozen configuration;
- baseline definitions and compute budgets;
- success tests and confidence level;
- code commit; and
- status: `development`, `frozen`, or `confirmation_complete`.

The runner refuses to use a seed in more than one role. Moving to `frozen` writes
an immutable configuration digest. Confirmation outputs must match that digest
and are written to a separate directory. Resuming an interrupted run is allowed;
changing a frozen field is not.

## 7. Experimental Protocol

### 7.1 Stage A: implementation and falsification smoke tests

Synthetic and three-step real-environment tests verify:

- action-permutation invariance;
- compatibility with different action-space sizes;
- no counterfactual environment access during selection;
- finite uncertainty and objective outputs;
- Pareto rejection and fallback; and
- resumable artifact writing.

A five-seed development pilot proceeds only if uncertainty is positively associated
with absolute prediction error and the conformal layer meets its nominal coverage
within the finite-sample interval expected from the calibration size.

### 7.2 Stage B: bounded development grid

The grid is limited to:

- ensemble size: 3 or 5;
- joint coverage: 0.80, 0.90, or 0.95;
- planning tolerance scale: 0.00, 0.05, or 0.10;
- planning horizon: 3 or 5;
- online residual window: 10 or 20; and
- policy-improvement round: 1 or 2.

Successive halving is allowed only within the development seeds and must use the
predeclared lexicographic score. The winning configuration is frozen before any
confirmation rollout is started.

### 7.3 Stage C: independent confirmation

Each stochastic learned policy is evaluated using the three independent model
training seeds and the same 20 confirmation rollout seeds. Common random numbers
are used within each training-seed and rollout-seed block. All policies use the
same executable mask, maximum of 100 steps, and stored initial-state convention.

The primary comparison uses a matched-compute PCC configuration. If the ensemble
size is `K`, its per-member MPC candidate count is `floor(50 / K)` and its total
predicted transition budget cannot exceed the single-model baseline's 50-candidate
budget by more than one candidate-equivalent. A full-budget PCC configuration may
be reported as a secondary performance-cost result.

### 7.4 Baselines

The required baseline set is:

1. executable random;
2. Paper9 matched MPC;
3. legacy value-filter MPC;
4. model-reward greedy;
5. rank-only/no-value MPC;
6. distributional risk-sensitive GeoJEPA-MPC;
7. online no-oracle expert selector;
8. PCC-GeoJEPA-MPC matched-compute;
9. PCC-GeoJEPA-MPC full-budget; and
10. oracle action-audit diagnostic, excluded from deployable-policy ranking.

The strongest no-oracle development baseline under the same lexicographic rule is
declared as the primary comparator before confirmation.

### 7.5 Ablations

The following ablations are individually required:

- restore county-specific action-ID embedding;
- use a single model instead of an ensemble;
- remove aleatoric output scales;
- replace paired joint conformal calibration with uncalibrated ensemble standard
  deviation;
- optimize reward without Pareto constraints;
- disable executed-feedback scale updates;
- disable reference-policy fallback; and
- stop after the first offline policy-improvement round.

Each ablation is linked to one mechanism claim. Ablations are development analyses
unless designated before freeze as confirmatory secondary tests.

### 7.6 Statistics

The primary estimator is the paired PCC-minus-comparator difference for each
training seed and rollout seed. A hierarchical paired bootstrap resamples training
seeds and, within each sampled training seed, rollout seeds. The primary report
contains:

- mean and median paired effect;
- one-sided 95% lower confidence bound;
- two-sided 95% interval for descriptive interpretation;
- wins, losses, and ties;
- per-training-seed effects; and
- all seed-level points.

The primary comparison is singular and is not selected after confirmation.
Secondary pairwise comparisons use Holm adjustment. Calibration coverage,
fallback rate, interval width, model error, candidate count, model forward count,
wall-clock time, and peak memory are reported as mechanism and cost outcomes.

## 8. Failure Handling and Scientific Safeguards

The implementation fails closed to the reference policy when:

- all candidate bounds are non-finite;
- the calibration object is absent or has a mismatched digest;
- the current observation is incompatible with the model schema;
- objective orientation metadata are missing;
- executed-feedback residuals are non-finite; or
- the executable mask is empty or inconsistent.

The runner must distinguish implementation failures from scientific failures.
Crashes, missing data, and digest mismatches are implementation failures and may
be fixed without changing the frozen scientific configuration. A valid run that
fails a reward or non-inferiority test is a scientific failure and must not trigger
new confirmatory tuning.

Any protocol correction after freeze requires a new registry version, new
confirmation seed namespace, and explicit disclosure. The old result remains in
the evidence archive.

## 9. Proposed Code Boundaries

The implementation will follow existing package patterns while separating model,
calibration, planning, protocol, and reporting responsibilities.

### New focused modules

- `paper10_geojepa_mpc/models/pcc_geojepa.py`: action-relative ensemble member and
  multi-objective outputs.
- `paper10_geojepa_mpc/training/pcc_training.py`: bootstrap training, objective
  scaling, checkpoint metadata, and policy-iteration training.
- `paper10_geojepa_mpc/planning/paired_conformal.py`: joint residuals, finite-sample
  quantile, and calibrated intervals.
- `paper10_geojepa_mpc/planning/executed_feedback.py`: bounded online marginal
  residual scaling.
- `paper10_geojepa_mpc/planning/pcc_selector.py`: candidate construction, Pareto
  gate, deterministic choice, and fallback.
- `paper10_geojepa_mpc/experiments/pcc_protocol_registry.py`: partition validation,
  freeze digest, and experiment state machine.
- `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`: resumable development and
  confirmation rollouts with information-set audit logging.
- `paper10_geojepa_mpc/experiments/pcc_confirmatory_statistics.py`: hierarchical
  paired inference and success-gate report.
- `scripts/paper10/plot_pcc_manuscript_figures.py`: Python-only manuscript figure
  generation.

### Modified integration modules

- `paper10_geojepa_mpc/experiments/value_label_generation.py`: multi-objective,
  baseline-continuation labels and partition metadata.
- `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py`: selector interface
  compatibility and compute accounting where shared behavior remains appropriate.
- submission audits, result-table builders, source-data maps, `MANIFEST.md`,
  `README.md`, `REPRODUCIBILITY.md`, and the CEUS manuscript after evidence is
  frozen.

## 10. Testing Strategy

Production behavior will be implemented test-first. Required automated tests
include:

### Model tests

- candidate scores permute equivariantly when block rows and masks are permuted;
- checkpoints load across different action-space sizes;
- objective heads have the declared shapes and finite values;
- ensemble members use different bootstrap membership and seeds; and
- state and objective scale metadata round-trip through checkpoints.

### Calibration tests

- a hand-computed paired residual example produces the expected joint quantile;
- all four objective intervals use the same joint coverage multiplier;
- an under-covered synthetic dataset widens rather than narrows bounds;
- executed-feedback calibration uses only the executed action outcome; and
- the online multiplier never drops below 1.0 or exceeds 3.0.

### Planner tests

- a reward-positive but planning-harmful action is rejected;
- a jointly positive action is accepted;
- no admissible candidate invokes the reference policy exactly once;
- a spy environment detects and forbids clone, rewind, and unexecuted `step`
  calls during action selection;
- ties are deterministic; and
- matched-compute accounting rejects an excessive transition budget.

### Protocol tests

- all partition seed sets are disjoint;
- historical seeds cannot enter confirmation;
- a frozen registry cannot be mutated;
- output digests match the frozen registry;
- interruption and resume do not duplicate seeds; and
- confirmation statistics reject incomplete training-seed/rollout-seed blocks.

### Statistical and figure tests

- hierarchical bootstrap preserves pairing on synthetic fixtures;
- reward superiority cannot pass when a planning non-inferiority gate fails;
- table and figure source values reproduce the frozen JSON values;
- SVG/PDF text remains editable and TIFF/PNG raster exports meet resolution
  requirements; and
- rendered previews pass nonblank, clipping, overlap, and minimum-font checks.

## 11. Manuscript Reconstruction

The paper is rewritten only after confirmatory evidence is frozen.

### 11.1 One-sentence paper argument

The final argument uses the sentence in Section 1 only if the success condition in
Section 2.2 passes. Otherwise, the manuscript reports the exact failed condition
and does not claim a performance breakthrough.

### 11.2 Section architecture

1. **Introduction**: multi-objective spatial-planning need, model-error and
   scalar-reward failure modes, prior method boundary, and PCC contribution.
2. **Materials and methods**: task formulation, information set, action-relative
   ensemble, multi-objective targets, paired calibration, Pareto gate, feedback
   scaling, protocol registry, and statistics.
3. **Results**: calibration validity, Bishan confirmation, planning-metric
   non-inferiority, matched-compute comparison, mechanism ablations, Dongxing
   confirmation, and cost/failure analysis.
4. **Discussion**: mechanism interpretation, scalar-reward misalignment, external
   adaptation, data and spatial-abstraction limits, and deployment boundary.
5. **Conclusion**: contribution, decisive evidence, application meaning, and the
   exact supported boundary.

The title and abstract no longer centre the legacy monitor gate or oracle guard.
Internal artifact names, source-control notes, and manuscript assembly language
are removed from reader-facing prose.

### 11.3 Literature-positioning gate

Ensemble uncertainty, conservative model-based reinforcement learning,
distributional planning, conformal prediction, and multi-objective control are not
individually claimed as new. The novelty claim is limited to the method combination
and its spatial-planning formulation only after a final verified literature search
shows that the same paired joint calibration, Pareto fallback, and executed-feedback
scheme has not already been reported.

## 12. Python Figure Contract

All manuscript figures are generated with Python/matplotlib. SVG and PDF retain
editable text; TIFF is exported at 600 dpi. Main figures target a maximum width of
180 mm with a white background, restrained colour palette, direct labels where
possible, raw seed points, sample sizes, and interval definitions.

### Figure 1: PCC-GeoJEPA-MPC mechanism

- **Core conclusion**: the deployable planner replaces oracle reward queries with
  calibrated multi-objective predictions and conservative fallback.
- **Archetype**: schematic-led composite.
- **Panels**: information boundary; action-relative ensemble; objective
  distributions; paired calibration; Pareto gate; executed-feedback update.
- **Review risk addressed**: any visual implication that unexecuted actions reach
  the real environment.

### Figure 2: Bishan confirmatory result

- **Core conclusion**: PCC improves reward over the strongest no-oracle baseline
  while satisfying all three zero-margin planning non-inferiority gates.
- **Archetype**: asymmetric quantitative grid with a reward-effect hero panel.
- **Panels**: paired reward effects; three planning-benefit effects; training-seed
  stability; matched-compute result; runtime.
- **Integrity rule**: all 60 training-seed/rollout-seed points are visible or
  available in an adjacent source-data panel.

### Figure 3: calibration and mechanism

- **Core conclusion**: calibrated uncertainty identifies model error and the
  Pareto/fallback mechanisms prevent harmful switches.
- **Archetype**: quantitative grid.
- **Panels**: nominal versus empirical joint coverage; uncertainty-error relation;
  fallback rate and avoided harmful actions; ablation effects.

### Figure 4: Dongxing external confirmation

- **Core conclusion**: the action-relative method retains its direction under a
  different action space without county-specific action embeddings.
- **Archetype**: quantitative grid.
- **Panels**: reward effect; three planning benefits; calibration coverage;
  adaptation and inference cost.

### Figure 5: spatial planning outcomes

- **Core conclusion**: aggregate effects correspond to interpretable spatial
  changes rather than only scalar reward differences.
- **Archetype**: image plate plus quantitative summaries.
- **Panels**: initial layout; reference-policy final layout; PCC final layout;
  changed blocks and local metric summaries.
- **Integrity rule**: identical extent, projection, classification, and colour
  mapping across compared maps.

### Tables

- **Table 1**: partitions, information sets, model seeds, rollout seeds, compute
  budgets, and confirmation rules.
- **Table 2**: main no-oracle baselines, reward, three planning effects,
  non-inferiority gates, runtime, and deployability.
- **Table 3**: mechanism ablations, calibration, fallback, and failure modes.

The existing oracle guard is moved to supplementary material and explicitly
labelled `oracle action-audit diagnostic upper bound`.

## 13. Completion Criteria

The substantive revision is complete only when:

- the protocol registry is frozen before confirmation;
- all model, calibration, planner, protocol, statistics, and figure tests pass;
- all required no-oracle baselines and ablations have complete artifacts;
- the Bishan and Dongxing confirmation blocks are complete or explicitly recorded
  as scientifically failed;
- the information-set audit confirms no unexecuted real-reward query;
- the manuscript claim matches the frozen success-gate report;
- Figures 1-5 and Tables 1-3 are generated from frozen source data;
- references and related-work distinctions are verified;
- the anonymous reviewer archive maps to the exact submission commit; and
- the full test suite and Paper10 preflight pass on the final tracked tree.
