# Paper10 PCC v1.1 Selected-Candidate Risk-Control Design

Date: 2026-07-21

Status: approved design replacing the non-viable PCC v1 development path

Target journal: *Computers, Environment and Urban Systems* (CEUS)

## 1. Purpose

PCC v1.1 replaces the PCC v1 action rule and calibration contract before any
confirmation seed is used. The replacement is required because the real PCC v1
pilot produced a policy that copied the Paper9 reference trajectory through
fallback rather than policy improvement.

The scientific objective remains unchanged: improve reward relative to the
strongest deployable no-oracle comparator while preserving slope, contiguity,
and connected farmland area. The online policy remains deployable and may use
only observable state, frozen model outputs, frozen calibrators, executable
masks, and outcomes of actions that were actually executed.

PCC v1.1 changes the means by which risk is controlled. Reward is the online
optimization objective and is tested at the policy level on independent
rollouts. A selected-candidate conformal certificate controls the three planning
constraints. Reward is no longer required to have a positive per-action lower
confidence bound.

## 2. Evidence Requiring Replacement

The PCC v1 run was stopped before development freeze and before any confirmation
seed was used. The following evidence was observed under model seed 5101,
round 1, ensemble size 3, coverage 0.90:

- round-2 label artifacts for completed seeds were byte-identical to their
  round-0 Paper9 artifacts;
- the first reproduced PCC decision returned `fallback=true` with reason
  `no_admissible_candidate` and selected the Paper9 reference action;
- the calibrator had `q_joint=10.708946899730266`;
- among 160 inspected candidate decisions, 129 passed the executable
  probability threshold, but none passed the reward lower-bound gate and none
  passed the joint planning lower-bound gate;
- without any uncertainty subtraction, 11 of those candidates satisfied the
  four mean constraints, while the largest conformal multiplier that allowed
  any candidate to pass was only 0.02715;
- the PCC v1 Stage A audit mixed an absolute immediate-outcome prediction and
  marginal scale with a paired, multi-horizon calibrator; and
- the PCC v1 freeze rule did not require a non-zero non-fallback rate, a
  non-zero action-difference rate, or positive development reward.

The root causes are structural, not a threshold accident. PCC v1 formed a
paired scale by adding candidate and reference marginal aleatoric variances as
if their errors were independent, despite the paired predictions sharing the
same state, model, and continuation. Its trajectory score then took the maximum
absolute residual across candidates, horizons, and objectives even though the
online policy used a one-sided lower bound at one horizon. Calibration labels
used random candidates while the online policy selected ranker-proposed
candidates. These choices made the certificate both statistically mismatched and
too conservative to execute a non-reference action.

## 3. Protocol Identity and Artifact Boundary

PCC v1 remains an immutable failed development protocol. Its registry and local
run outputs are not deleted or silently repurposed. A tracked abandonment audit
will record:

- the PCC v1 registry and source commit;
- the stopped process command and stop time;
- the completed round-2 seed artifacts present at shutdown;
- the byte-identity and fallback evidence;
- the fact that no Bishan 4000-4019 or Dongxing 8000-8019 confirmation seed was
  run; and
- the rule that PCC v1 policy-iteration artifacts cannot satisfy a PCC v1.1
  inventory or resume check.

PCC v1.1 uses a new registry, protocol identifier, and run root. Existing
round-0 train and calibration label manifests may be reused only as immutable
source datasets. Their original protocol identity and digest remain unchanged,
and the PCC v1.1 registry declares their exact source protocol and manifest
digests. Derived PCC v1.1 checkpoints, selected-candidate labels, calibrators,
and audits carry the PCC v1.1 protocol digest.

## 4. Model Architecture

### 4.1 Action-relative paired representation

The new member model receives observable state features, one candidate action,
and the Paper9 reference action. It encodes each action without a county-specific
action embedding. For action `a`, the representation uses:

- the selected block embedding;
- the selected block-neighbour embedding;
- the selected block minus county-mean embedding;
- county mean and max-pooled embeddings; and
- the global-state embedding.

The paired head combines candidate and reference representations using the two
representations, their signed difference, and their absolute difference. It
directly predicts `delta_mean` and `delta_log_scale` for four oriented objectives
at horizons 1, 3, and 5. It does not obtain a delta scale by summing two marginal
outcome variances.

The direct target is

```text
Delta_h(s, a, r) = Y_h(s, a) - Y_h(s, r),
```

where `r` is the Paper9 reference action and paired candidate/reference rollouts
use the same continuation seed.

### 4.2 GeoJEPA auxiliary objective

Compatible Paper9 block and global encoder weights initialize the online
encoder. The neighbour encoder is initialized from the block encoder. An EMA
target encoder receives candidate and reference next states with gradients
stopped. The online predictor maps the current state-action representation to
the target next-state latent. This replaces the raw full-state transition loss,
which was dominated by unchanged blocks.

The training objective contains:

- direct paired-delta heteroscedastic negative log likelihood;
- candidate-versus-reference ranking loss;
- strict executable-target binary cross entropy;
- candidate and reference GeoJEPA latent-prediction loss; and
- a small anti-collapse regularizer on the online latent.

The auxiliary absolute immediate-outcome head is retained only for executed
feedback monitoring. It is not used to fit or audit the paired conformal
certificate.

### 4.3 Training and adaptation

Ensemble members use trajectory bootstrap samples and deterministic member seeds.
Round-1 training uses the immutable round-0 labels. The encoder initialization,
trainable parameter names, parent checkpoint digest, source label digest, and
training metrics are stored in every checkpoint.

After a viable round-1 policy generates new labels, round-2 training uses an
explicit union manifest containing both round-0 and round-2 labels. Round-2
members retain parent-checkpoint lineage and do not replace round-0 coverage with
only on-policy data.

Dongxing adaptation preserves the action-relative encoder, GeoJEPA predictor,
candidate generator, Pareto logic, conformal score definition, and compute rule.
Only objective delta heads and the auxiliary absolute-outcome head may be
updated before Dongxing calibration.

## 5. Candidate Generation and Base Selection

The candidate generator is deterministic given observable state, executable
mask, frozen Paper9 rankers, and the declared compute mode. It constructs a
stable deduplicated prefix containing the Paper9 reference action, reward-ranker
proposals, value-ranker proposals, and remaining executable actions in stable
index order.

For ensemble size `K`:

- `matched` mode evaluates `floor(50 / K)` candidates so that ensemble member
  evaluations do not exceed 50 candidate equivalents; and
- `full` mode evaluates 50 candidates.

Matched and full modes are separate selection rules. They require separate
selected-candidate label manifests and calibrators.

The base selector is fixed before conformal calibration:

1. reject candidates below the strict executable-probability threshold;
2. retain candidates whose predicted mean planning deltas are no worse than the
   declared slope, contiguity, and connected-area tolerances;
3. select the candidate with the largest predicted reward delta;
4. break ties by the worst planning mean, predicted delta scale, and action
   index; and
5. select the Paper9 reference when no mean-admissible candidate exists.

The conformal multiplier cannot alter this candidate. It only certifies or
rejects the already selected candidate.

## 6. Selected-Candidate Conformal Certificate

### 6.1 Calibration labels

For each `(model_seed, K, policy_round, compute_mode)` family, a selected-label
runner reconstructs the declared offline trajectory states, applies the frozen
base selector, and evaluates only the selected candidate and Paper9 reference
under paired continuation seeds. It records the selected action even when it
equals the reference, the base-selection reason, true paired objectives,
predicted deltas and scales, and information-set counters.

Coverages 0.80, 0.90, and 0.95 reuse this selected-label manifest. Coverage does
not retrain the model or regenerate selected actions.

### 6.2 Nonconformity score

For planning horizon `h`, state `t`, and planning constraint `j`, define the
one-sided normalized residual

```text
R_tj = (mu_tj - Delta_tj) / max(s_tj, epsilon).
```

The trajectory score is

```text
R_trajectory = max(0, max_t max_j R_tj),
```

where `j` ranges only over slope benefit, contiguity benefit, and connected-area
benefit. Reward and unused horizons do not enter the certificate score.

For `n` calibration trajectories and target coverage `c`, the conformal
multiplier is the order statistic at rank

```text
min(n, ceil((n + 1) * c)).
```

The online lower bounds are

```text
LCB_j = mu_j - q_c * s_j * m_j,
```

where each executed-feedback multiplier `m_j` is at least one. Widening the
bound after adverse executed outcomes therefore cannot invalidate the frozen
certificate by making it less conservative.

The selected candidate executes only when all three lower bounds exceed the
negative declared tolerances. Otherwise the policy fails closed to Paper9.

### 6.3 Calibrator lineage

Every calibrator binds:

- PCC v1.1 protocol and registry digests;
- model seed, ensemble size, policy round, planning horizon, and compute mode;
- ordered checkpoint digests;
- source and selected-label manifest digests;
- candidate-generator and base-selector digests;
- calibration trajectory seeds;
- objective order, coverage, score definition, and finite-sample rank; and
- trajectory scores and calibrator digest.

No calibrator may be reused across matched/full modes, model seeds, ensemble
sizes, rounds, or horizons.

## 7. Viability Pilot

The viability pilot is a mandatory barrier before the full factorial. It trains
all three declared model seeds with ensemble size 3 for policy round 1, generates
matched-compute selected-candidate calibration labels, and fits the three
declared coverage values.

The pilot evaluates the predeclared development block. A coverage is viable only
if all of the following hold:

- trajectory-level simultaneous planning coverage reaches the target coverage;
- non-fallback rate is at least 0.10;
- action-difference rate relative to Paper9 is at least 0.10;
- mean true reward delta over non-fallback actions is strictly positive;
- mean true delta for each planning objective is non-negative;
- uncertainty and absolute error have positive rank association;
- every selected action is executable; and
- unexecuted real-reward query count is exactly zero.

The pilot chooses the highest declared coverage that passes every gate. This
rule is fixed before pilot outcomes are observed. If no coverage passes, PCC
v1.1 stops as a valid development-stage scientific failure. It does not lower a
threshold, add a coverage, reuse a seed, or launch the factorial.

For each model seed, the passing round-1 K=3 matched policy generates the
round-2 train and calibration state distributions. Round-2 K=3 and K=5 members
for that model seed use the same immutable round-2 label manifests.

## 8. Full Development and Freeze

After the pilot passes, the complete inventory contains:

- 12 checkpoint families: 3 model seeds x 2 ensemble sizes x 2 policy rounds;
- 48 physical checkpoints: 24 in each policy round;
- 24 selected-candidate label families: checkpoint family x matched/full mode;
  and
- 72 calibrators: selected-label family x 3 coverages.

Bounded development evaluates the declared coverage, ensemble size, planning
horizon, tolerance, residual-window, policy-round, and compute-mode choices with
successive halving. It also evaluates every required no-oracle baseline and
single-mechanism ablation.

A configuration cannot freeze unless:

- the viability pilot and selected-candidate coverage audit pass;
- non-fallback and action-difference rates each remain at least 0.10 on the
  complete development block;
- mean reward delta relative to the selected primary comparator is positive;
- all three one-sided planning bootstrap lower bounds are non-negative;
- at least two of three model seeds have positive reward delta and non-negative
  planning means;
- the matched-compute policy reaches the same qualitative gate conclusion;
- all required ablations are complete;
- every checkpoint, label, calibrator, plan, and result digest validates; and
- no confirmation path or seed has been accessed.

The winner is selected lexicographically among gate-passing configurations by
reward, lower planning margin, non-fallback rate, compute, and stable identifier.
An all-fallback or Paper9-identical configuration is ineligible rather than a
low-ranked winner.

## 9. Independent Confirmation

Confirmation remains prohibited until the PCC v1.1 registry and freeze audit
are committed. A fresh process verifies that the working registry and committed
Git blob have the same frozen digest.

Bishan uses seeds 4000-4019 exactly once. Dongxing uses its declared adaptation
and calibration seeds before seeds 8000-8019 are used exactly once. Primary
statistics preserve paired rollout seeds and model-seed hierarchy. Deterministic
policies are not replicated as independent model draws.

The locked confirmation claim requires:

- reward superiority over the frozen primary comparator;
- zero-margin non-inferiority for all three planning outcomes;
- support from at least two model seeds and the hierarchical aggregate;
- the same qualitative conclusion for matched compute; and
- a zero unexecuted-real-reward information-set audit.

A valid failed gate is reported as a negative result. Confirmation outcomes may
not change PCC v1.1, its thresholds, or its seed sets.

## 10. Execution, Resume, and Failure Handling

Every runner writes its execution plan before starting subprocesses. Seed-level
artifacts are written through temporary files and atomic replacement. Resume
accepts a seed only after validating its manifest, physical file digest,
registry digest, model lineage, candidate rule, and compute mode.

Implementation defects include malformed schemas, incompatible transferred
weights, non-finite model outputs, digest mismatches, unsupported environment
shapes, incomplete blocks, and invalid resume state. Each defect requires a
failing regression test before repair.

Scientific failures include no viable pilot coverage, inadequate non-fallback
rate, calibration undercoverage, non-positive development reward, planning
degradation, matched-compute failure, or confirmation gate failure. Scientific
failures are recorded without automatic retuning.

Selectors fail closed for missing calibration, empty executable masks,
incompatible state shapes, non-finite outputs, and invalid feedback. Every
fallback records a stable reason code.

## 11. Test Strategy

Production behavior is implemented test first. Focused unit tests cover:

- direct paired-delta means and scales;
- correlated candidate/reference errors not being treated as independent
  marginal variances;
- EMA target updates and stopped target gradients;
- one-sided, horizon-specific trajectory scores and finite-sample ranks;
- harmless lower-tail errors not widening a lower-bound calibrator;
- candidate identity being independent of conformal coverage;
- matched/full candidate and calibrator separation;
- source-protocol migration and digest binding;
- minimum non-fallback and action-difference freeze gates; and
- refusal to freeze a reward-nonpositive winner.

Integration tests cover:

- pilot success and scientific-failure closeout;
- atomic selected-label generation and resume;
- round-2 K=3/K=5 shared-label lineage;
- the 12-family, 48-checkpoint, 24-selected-label, 72-calibrator inventory;
- development and ablation completeness;
- committed-freeze verification; and
- confirmation barriers and complete paired blocks.

The full repository suite, Paper10 submission preflight, source-data
regeneration, figure/table regeneration, and Git integrity checks remain final
completion gates. Manuscript prose is revised only after frozen experimental
evidence exists.

## 12. Completion Criteria

PCC v1.1 algorithm development is complete only when:

- the PCC v1 abandonment audit is tracked;
- the new protocol rejects every old policy-iteration artifact;
- the viability pilot passes without threshold changes;
- all model, selected-label, calibrator, development, and ablation inventories
  are complete and digest-bound;
- a non-trivial development winner is committed and independently verified;
- Bishan and Dongxing confirmation are complete or explicitly recorded as
  scientific failures;
- information-set and matched-compute audits pass;
- statistics, figures, tables, and manuscript claims regenerate from the frozen
  result object; and
- the complete tests and submission preflight pass on a clean tracked tree.
