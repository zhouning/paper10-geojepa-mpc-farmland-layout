# Paper10 PCC v1 Completion and Independent Confirmation Design

Date: 2026-07-20

Status: approved design addendum for completing the existing PCC-GeoJEPA-MPC
substantive revision

Target journal: *Computers, Environment and Urban Systems* (CEUS)

## 1. Purpose

This addendum closes the gap between the approved PCC-GeoJEPA-MPC scientific
design and the commands that must train, select, freeze, confirm, analyse, and
report it. It does not change the scientific hypothesis, objective orientation,
seed namespaces, success gates, or the rule that confirmation data are used
exactly once after the protocol has been frozen and committed.

The work proceeds in this order:

1. repair protocol and artifact consistency;
2. complete executable development and confirmation orchestration;
3. train and calibrate the declared ensembles;
4. select on development seeds and commit a frozen registry;
5. run independent Bishan and Dongxing confirmation;
6. compute locked statistics and mechanism audits;
7. generate figures and tables from frozen evidence; and
8. rewrite the manuscript last.

## 2. Current Verified State

The isolated worktree starts from commit
`4c61d02d8e58e53d86d30675e6755880f772e77c` on branch
`codex/pcc-v1-completion`. The full baseline suite passes with 499 tests.

The following scientific inputs already exist outside the isolated worktree and
will be treated as immutable inputs:

- Bishan training trajectories for seeds 1000-1007;
- Bishan calibration trajectories for seeds 2000-2019;
- their seed-level artifacts, SHA-256 values, and merged manifests; and
- the locked Paper9 MPC reference checkpoint identified by
  `fd3cdeeb827dc59a30e559a36fc95166db77447dc6e7d1d4b5b4c081704c947f`.

No ensemble checkpoint, development freeze, or confirmation artifact is accepted
as complete at the start of this addendum. Confirmation seeds 4000-4019 and
8000-8019 remain prohibited until a frozen registry digest has been committed.

## 3. Approaches Considered

### 3.1 Selected: repair the PCC v1 control plane and complete the locked study

This route preserves the approved multi-objective, no-oracle scientific design.
It adds strict protocol-to-manifest validation, real development and confirmation
orchestrators, resumable per-policy artifacts, required ablations, and final
claim gates. It is selected because it directly addresses the reviewer findings
without using confirmation results to redesign the algorithm.

### 3.2 Rejected: rescue the legacy oracle-guard manuscript

The legacy true-reward guard has a clear information advantage and is not a
deployable planner. Rewriting its description cannot resolve that technical
defect. It remains only a diagnostic upper bound in supplementary evidence.

### 3.3 Rejected: reduce PCC v1 to a Bishan-only or baseline-light study

Dropping Dongxing, matched-compute evaluation, or the declared baseline and
ablation suite would lower computation but would also abandon the approved CEUS
claim and success gates. Any such reduced study would require a separately
designed protocol rather than a silent change to PCC v1.

## 4. Locked Scientific Contract

PCC v1 retains all boundaries from the 2026-07-10 design:

- online selection uses observable state, executable masks, frozen models,
  frozen calibrators, frozen policies, and outcomes of executed actions only;
- no unexecuted action may be evaluated with the real environment at decision
  time;
- the oracle action audit is labelled `deployable=false` and excluded from
  primary comparator selection;
- reward superiority must coexist with zero-margin non-inferiority for slope,
  contiguity, and connected farmland area;
- the qualitative conclusion must hold for at least two of three model seeds and
  for the hierarchical aggregate;
- matched-compute PCC must reach the same conclusion as the primary PCC result;
- Dongxing uses the frozen core configuration and no external-confirmation
  tuning; and
- a valid scientific failure is reported as failure, not followed by confirmatory
  retuning.

## 5. Protocol and Artifact Integrity Repair

### 5.1 Canonical continuation policy

The current registry contains `offline_reference_policy.continuation = random`,
while the completed train and calibration manifests identify the continuation
policy as locked `paper9_mpc` with the reference checkpoint digest, horizon 5,
top-k 50, and gamma 0.99. The generated manifests are the authoritative record of
what produced the trajectories.

Before any model training, PCC v1 will be corrected while it is still in
`development` so that the registry and manifests both declare `paper9_mpc`.
Validation will compare name, checkpoint digest, horizon, top-k, gamma, partition,
seed set, and artifact digest. A mismatch fails before training.

### 5.2 Immutable input audit

The label manifests are referenced by absolute path from the original checkout;
they are not copied or regenerated merely to populate the worktree. A tracked
input-audit summary records their canonical paths, merged-manifest digests,
artifact counts, trajectory seed sets, and continuation-policy fields. The
scientific run root for new bulky outputs is isolated from the source checkout
and remains ignored by Git.

### 5.3 Freeze barrier

The registry may move from `development` to `frozen` only when:

- all referenced train, calibration, checkpoint, calibrator, and development
  artifacts pass digest validation;
- Stage A uncertainty-error association and calibration coverage gates pass;
- the development grid is complete under its declared successive-halving rules;
- one PCC configuration and one strongest no-oracle comparator are selected by
  the declared lexicographic rule;
- matched and full compute budgets are recorded; and
- all required configuration and artifact digests are present.

Freezing writes one canonical digest, a tracked audit, and a commit. Confirmation
runners verify that committed digest from a fresh process before creating output.

## 6. Execution Architecture

### 6.1 Single-policy rollout worker

`run_pcc_rollouts.py` remains a single-policy, single-model-seed worker. It owns
environment creation, observable-state construction, policy execution, per-step
information-set logging, atomic seed output, and resume validation. It does not
gain a plural model-seed or policy-set interface.

Development smoke tests use `mode=development` with three steps. The obsolete
planned `mode=smoke` command is removed from the execution plan rather than added
as an unnecessary protocol state.

### 6.2 Development orchestrator

`run_pcc_development.py` gains a real CLI and orchestration layer. It:

- loads round-specific checkpoint and calibrator inventories;
- validates that only seeds 3000-3009 are requested;
- executes the declared successive-halving rungs;
- schedules the single-policy rollout worker for each model seed and
  configuration;
- records calibration coverage, uncertainty-error association, planning-gate
  count, reward, compute, runtime, and failures;
- selects strictly by planning gates, reward, compute, then stable ID; and
- optionally freezes only after all gates and artifacts pass.

### 6.3 Confirmation orchestrator

A focused confirmation orchestrator schedules the frozen policy matrix without
changing worker semantics. It creates one artifact per region, policy, and model
seed, then validates the complete block before statistics. Deterministic policies
may be run once per rollout seed but must be mapped consistently across model-seed
blocks without inflating effective sample size.

The orchestrator refuses to start when the registry is not frozen, the frozen
digest is not committed, an output already references another digest, or a seed is
outside its declared confirmation partition.

### 6.4 Oracle diagnostic

The oracle action-audit diagnostic uses a separate explicitly privileged path.
Its records contain `deployable=false`, the count of true-reward queries, and the
diagnostic role. No primary-statistics loader accepts it as a comparator. The
no-oracle information-set audit is run independently and must report exactly zero
unexecuted real-reward queries.

## 7. Baselines and Ablations

The no-oracle primary baseline inventory remains:

- executable random;
- Paper9 matched MPC;
- legacy value-filter MPC;
- model-reward greedy;
- rank-only/no-value MPC;
- distributional risk-sensitive GeoJEPA-MPC;
- online no-oracle expert selection;
- PCC matched-compute; and
- PCC full-budget.

Every policy logs candidate count, ensemble member evaluations, model-forward
count, selection time, peak memory, fallback rate, and information-set counters.
Primary comparator selection occurs on development outputs only.

The required development ablations remain:

- county-specific action embedding;
- single model;
- no aleatoric scale;
- uncalibrated ensemble scale;
- reward-only selection;
- no executed-feedback scaling;
- no reference fallback; and
- one policy-improvement round.

Each ablation is represented by a named frozen configuration overlay with an
explicit mechanism claim. Ablations cannot silently alter unrelated settings.

## 8. Dongxing External Confirmation

Dongxing adaptation uses seeds 6000-6003 and trains objective heads only.
Calibration uses seeds 7000-7019 and the coverage value already selected in
Bishan development. The action-relative trunk, candidate construction, Pareto
logic, residual-window choice, thresholds, horizon, and compute rule remain
frozen.

Dongxing confirmation uses seeds 8000-8019 exactly once. Failure to load the
frozen architecture across its action space is an implementation defect; failure
of reward or planning gates is a scientific result.

## 9. Statistics and Claim Gate

Confirmation artifacts must form complete paired blocks. The hierarchical paired
bootstrap resamples model seeds and rollout seeds while preserving pairing. The
report includes mean and median effects, one-sided lower bounds, two-sided
intervals, wins/losses/ties, model-seed effects, calibration coverage, fallback,
runtime, memory, and seed-level rows.

The manuscript claim is generated from the locked result object:

- if every primary gate passes, the paper may state the exact supported PCC
  improvement and non-inferiority boundary;
- if any gate fails, the paper identifies the failed gate and does not claim a
  performance breakthrough; and
- no PCC v1 confirmation seed is reused in a redesigned PCC v2 study.

## 10. Failure Handling

Implementation defects include crashes, missing files, malformed schemas,
incorrect digests, unsupported CLI paths, and violated resume semantics. Each
defect requires a failing regression test before repair.

Scientific failures include valid calibration failure, a development gate that
cannot select a configuration, reward non-superiority, planning degradation,
matched-compute failure, Dongxing failure, or fewer than two supporting model
seeds. Scientific failures are recorded without post-confirmation tuning.

All selectors fail closed to the reference policy for missing calibration,
non-finite outputs, incompatible observations, empty masks, or invalid executed
feedback. Confirmation orchestration fails closed rather than dropping incomplete
blocks.

## 11. Testing Strategy

New behavior is implemented with RED-GREEN-REFACTOR cycles. Tests cover:

- registry-to-label-manifest continuation and digest agreement;
- development CLI argument validation and no-confirmation-seed access;
- deterministic successive-halving scheduling and resume;
- freeze rejection for incomplete artifacts or failed Stage A gates;
- confirmation refusal before a committed frozen digest;
- complete policy-by-model-by-rollout blocks;
- deterministic-policy mapping without pseudoreplication;
- oracle diagnostic exclusion from primary statistics;
- every ablation overlay changing only its declared mechanism;
- Dongxing objective-head-only adaptation; and
- final source-data, figure, table, manuscript, and preflight consistency.

Focused tests run after every change. The complete repository suite and Paper10
preflight run before any completion claim.

## 12. Manuscript and Figure Boundary

No legacy manuscript text is polished during algorithm development. Figures and
tables are generated only from frozen confirmation summaries. The new manuscript
removes internal artifact narration, presents the oracle only as a supplementary
diagnostic upper bound, contains a self-contained reward and dataset description,
and maps every result sentence to frozen source data.

If the frozen primary success gate is false, manuscript reconstruction reports
the negative result and stops submission conversion until a separately approved
next study exists.

## 13. Completion Criteria

This completion cycle ends only when:

- registry and completed label manifests agree exactly;
- all declared ensemble checkpoints and two policy-improvement rounds are valid;
- development selection and the committed freeze audit are complete;
- all no-oracle baselines, required ablations, Bishan confirmation, and Dongxing
  confirmation are complete or explicitly recorded as scientific failures;
- information-set and matched-compute audits pass;
- locked statistics and seed-level source data regenerate;
- Figures 1-5 and Tables 1-3 pass automated and visual QA;
- the CEUS manuscript matches the frozen claim gates;
- the anonymous archive maps to the exact submission commit; and
- the full test suite and submission preflight pass on a clean tracked tree.
