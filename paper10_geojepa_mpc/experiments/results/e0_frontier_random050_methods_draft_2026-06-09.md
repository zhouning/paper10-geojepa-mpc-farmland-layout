# E0 frontier_random050 Methods draft

Date: 2026-06-09

This document drafts the paper-facing Methods section for the current Paper10
E0 `frontier_random050` evidence package. It is not a new experiment. It
translates the packaged pipeline, monitor gate, value-head training, rollout
evaluation, and reproducibility boundary into manuscript prose.

## One-sentence argument

In constrained farmland layout planning, we evaluate a monitor-gated
GeoJEPA-MPC value-filtering workflow that trains only on frontier-random
multi-step labels passing candidate-quality checks, supported by the packaged
10x12/top4 and 20x16/top5 experiments, with the boundary that all tested
50-state label sets failed the current gate.

## Terminology ledger

| canonical term | first-use definition | use decision |
|---|---|---|
| GeoJEPA-MPC | JEPA-regularized geospatial world-model planning with model-predictive candidate selection | Use as the method family name. |
| `frontier_random050` | Candidate proposal with `candidate_mode=frontier_random` and `frontier_fraction=0.5` | Use exactly for this E0 run family. |
| executable mask | Action mask that restricts swaps to actions executable in the farmland environment | Use for label generation and rollout evaluation. |
| value label | Discounted multi-step return recorded for a candidate action | Distinguish from one-step reward. |
| value head | Scalar ranking head trained from value labels while transition loss is disabled | Avoid implying full transition-model retraining. |
| monitor gate | Top-k diagnostic rule that decides whether a label set may be used for value-head training | Training is conditional on `decision=continue`. |
| candidate regret | Mean return gap under candidate-score-selected top-k actions | Lower is better. |
| candidate overlap | Fractional overlap between candidate-score top-k and return-ranked top-k actions | Higher is better. |
| one-step regret | Return gap under one-step-reward top-k action selection | Must remain above the minimum to show multi-step signal. |
| GPKG root | Prepared-data root resolving `DLTB_with_slope.gpkg` | Use as the reproducible data-root convention. |

## Section outline

1. Task formulation and data root.
2. GeoJEPA-MPC base planner.
3. Frontier-random value-label generation.
4. Monitor-gated label selection.
5. Value-head-only training.
6. Rollout evaluation and statistics.
7. Reproducibility and negative-label boundary.

## Draft

### Task formulation and data root

We formulate Bishan farmland layout optimization as a constrained sequential
swap-planning task. At each planning step, the environment exposes a land-use
state, block-level features, geospatial features, and a finite set of valid
swap actions. The planner selects one executable action, applies it to the
environment, and receives a reward that combines farmland layout objectives
recorded by the Paper9-compatible county environment. All E0 label-generation
and rollout experiments reported here use the executable swap mask, so
candidate actions are drawn only from swaps that the environment can apply at
the current state.

The full Bishan prepared dataset is external to the Git repository and is
resolved through the repository-level data layout described in the
reproducibility guide. For the paper-facing E0 evidence, the reproducible
geospatial root is the root that resolves `DLTB_with_slope.gpkg`. A macOS audit
showed that this GPKG root reproduced the packaged 20x16/h5 seed44 labels at
the array level, whereas a root that resolved the shapefile version first
produced materially different labels. We therefore treat the GPKG root as part
of the experimental condition rather than an incidental file-format choice.

### GeoJEPA-MPC base planner

The value-filtering workflow starts from the packaged GeoJEPA-MPC rank
checkpoint `rank_seed2028.pt`. The checkpoint is wrapped by the Paper9 adapter
so that it can score executable actions in the farmland environment and support
model-predictive candidate selection. In the base planning interface, candidate
actions are scored from the current state and evaluated over a finite planning
horizon. The E0 experiments do not claim a new transition model; they test
whether a separately trained value head can improve candidate filtering on top
of this existing rank checkpoint.

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
configuration disables transition mean-squared-error training and restricts
the trainable scope to the value head, which contains 8,321 trainable
parameters in the packaged runs. The checkpoint metric is selected from the
candidate top-k diagnostic, so the 20x16/top5 run selects the best checkpoint
by `candidate_top5_regret`.

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
mean baimu-area change. The 20x16/top5 value filter reached mean total reward
`69.4705`, sample standard deviation `1.0004`, and minimum reward `67.7135`.
The 10x12/top4 pilot reached mean total reward `65.2566`, sample standard
deviation `5.0037`, and minimum reward `57.9750`. The reported improvement is
therefore a distribution-level gain across seeds 0-4 rather than a single best
seed.

The exact reward and reporting definitions are recorded in
`e0_reward_and_rollout_metric_definitions_2026-06-09.md`. In brief, the
per-step environment reward combines normalized stepwise farmland-slope
reduction, normalized stepwise contiguity change, normalized baimu-fang area
change, a bonus for newly counted baimu-fang patches, an asymmetric penalty for
baimu-fang area loss, and a zero-swap penalty. Rollout total reward is the
un-discounted sum of this per-step reward over the 100-step episode.

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

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| The E0 workflow trains only after label-quality monitoring. | `value_label_monitor.py` returns `decision=continue` only when candidate regret, candidate overlap, one-step regret, and state-count gates pass. | supported |
| The main paper-facing E0 value head is 20x16/top5. | Packaged 20x16 monitor top-5 has candidate regret `0.1877`, overlap `0.6300`, and one-step regret `2.4626`; rollout mean is `69.4705`. | supported |
| Value-head training does not retrain the transition model in these runs. | Training metrics record `transition_loss_enabled=false`, `lambda_sig=0.0`, and 8,321 trainable parameters. | supported |
| The comparison with 10x12/top4 uses matched rollout settings. | Both summaries record `selector=value_filter`, executable masks, horizon `5`, top-k `50`, blend mode, candidate value weight `0.1`, and seeds 0-4. | supported |
| The tested 50-state rows should not be trained. | macOS seed45 and Windows seed46 50-state labels failed default and post-hoc monitor gates. | supported |
| The method has demonstrated successful 50-state value-head scale-up. | No tested 50-state label set passed the monitor gate. | not supported |

## Assumptions or missing inputs

- The target journal and required Methods length are not fixed.
- Literature citations for GeoJEPA, MPC planning, farmland layout planning, and
  prior Paper9 environment details still need to be inserted by source.
- The final manuscript should decide whether implementation details belong in
  the main Methods section or in supplementary Methods.
- The reward formula has been extracted from the packaged environment into
  `e0_reward_and_rollout_metric_definitions_2026-06-09.md`; before submission,
  align notation with the target journal and any prior Paper9 wording.

## Why this structure

- The section first fixes the task and data root so readers know the scope of
  the reproducible condition.
- The pipeline separates base planner, label generation, gate, training, and
  rollout evaluation to avoid mixing method design with performance claims.
- The monitor gate appears before value-head training because training is
  conditional on `decision=continue`.
- The 50-state evidence is placed in the boundary subsection to prevent the
  manuscript from implying that failed label sets were trained.

## Chinese author notes

- 这版 Methods 的重点是把 20x16/top5 写成当前可复现主线，而不是继续强调
  50-state 扩展。
- 50-state 部分只写成 label gate 未通过的边界诊断，避免被审稿人理解为
  训练失败或隐瞒负结果。
- reward 公式已经单独整理到
  `e0_reward_and_rollout_metric_definitions_2026-06-09.md`；投稿前还需要统一
  目标期刊格式和 GeoJEPA/MPC/农地规划相关引用。
