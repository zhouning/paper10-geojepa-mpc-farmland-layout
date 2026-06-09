# E0 frontier_random050 results synthesis for Paper10

Date: 2026-06-09

This synthesis turns the packaged `frontier_random050` E0 experiments into
paper-facing results and discussion material. It is not a new experiment. It
organizes the validated 10x12 and 20x16 value-head runs, the macOS GPKG
reproduction audit, and the failed 50-state macOS/Windows diagnostics.

## One-sentence argument

In constrained farmland layout planning, the Paper10 E0 experiments show that a
GeoJEPA-MPC value filter can improve and stabilize long-horizon rollouts when it
is trained on monitor-gated frontier-random labels, supported by 10x12 and
20x16 value-head rollouts, with the present boundary that the tested 50-state
candidate-label settings fail the current monitor gate.

## Terminology ledger

| Canonical term | Meaning in this package | Notes |
|---|---|---|
| `frontier_random050` | Candidate label mode with `candidate_mode=frontier_random` and `frontier_fraction=0.5` | Use this exact run-family name for 10x12, 20x16, and most 50-state diagnostics. |
| value label | Multi-step return label generated for candidate actions | Distinguish from one-step reward. |
| value head | Trainable scalar head initialized from `rank_seed2028.pt` and trained from value labels | Training uses `transition_loss_enabled=false` in these value-head-only runs. |
| monitor gate | Top-k diagnostic rule that decides whether a label set is usable for value-head training | Default top-k checks are 3, 4, and 5. |
| candidate regret | Mean return gap between the best action and the best candidate-score-selected top-k action | Lower is better. |
| candidate overlap | Fractional overlap between candidate-score top-k and return top-k | Higher is better. |
| one-step regret | Return gap under one-step-reward top-k selection | Must remain material, otherwise the label adds little beyond one-step reward. |
| GPKG root | Prepared-data root that resolves `DLTB_with_slope.gpkg` | Required for reproducing the packaged 20x16 labels. |

## Evidence ladder

### 1. Workflow validation

The value-head-only training path was fixed so that `lambda_sig=0` no longer
triggers transition MSE training. Both the 10x12 and 20x16 value-head runs
trained only 8,321 value-head parameters and completed locally in minutes rather
than timing out.

### 2. Pilot result: 10x12 top-4

The 10-state, 12-candidate pilot selected top-4 as the usable monitor gate. Its
five-seed 100-step rollout reached mean total reward `65.2566` with sample
standard deviation `5.0037`. This improved over the prior
`frontier_independent` value-head branch, whose matched mean was `62.0344`.

### 3. Main packaged result: 20x16 top-5

The 20-state, 16-candidate scale-up selected top-5 as the usable monitor gate.
Top-5 achieved candidate regret `0.1877`, candidate overlap `0.6300`, and
one-step regret `2.4626`, so the label set retained both candidate coverage and
multi-step signal. The five-seed 100-step rollout reached mean total reward
`69.4705` with sample standard deviation `1.0004`.

Relative to 10x12/top4, 20x16/top5 increased mean total reward by `4.2139`
(`6.46%`) and reduced sample standard deviation by `4.0034`. The result is
therefore stronger as a paper-facing E0 experiment because it improves average
reward and reduces seed sensitivity.

### 4. Reproducibility audit

The packaged 20x16/h5 seed44 label set was reproduced on macOS when the
prepared-data root used `DLTB_with_slope.gpkg`. The arrays `actions`,
`returns`, `one_step_rewards`, `n_valid_actions`, `state_steps`, and
`states_gf` matched exactly, while `states_bf` and `candidate_scores` matched
within small floating-point tolerance. A root that resolved to the shapefile
version produced materially different labels, so the GPKG root is the
reproducible data-root convention.

### 5. Boundary result: failed 50-state label sets

The 50-state scale-up attempts did not pass the current monitor gate. On macOS,
`50x24/h5 seed45` failed top-3, top-4, and top-5, and post-hoc top-6/8/10/12
also returned `stop`. On Windows, the label-only ablation grid
(`50x16 f0.5`, `50x20 f0.5`, `50x24 f0.75`, and `50x24 f1.0`, all seed46)
also failed every default and post-hoc monitor check.

The best default Windows row was `50x16/h5 seed46 f0.5` at top-5, but its
candidate regret remained above threshold (`0.3840 > 0.2500`). Larger top-k
values did not rescue the decision: some rows became mostly explainable by
one-step reward, while others retained excessive candidate regret or weak
overlap.

## Paper-facing results draft

The E0 value-head experiments first tested whether frontier-random multi-step
labels could provide a usable candidate filter for GeoJEPA-MPC. In the 10x12
pilot, the monitor selected a top-4 gate because top-3 was too strict and
top-5 was largely covered by the one-step reward baseline. A value head trained
under this gate reached a five-seed mean total reward of `65.2566`, improving
over the prior `frontier_independent` value-head branch under the matched
100-step rollout configuration.

Scaling the label set to 20 states and 16 candidate actions strengthened the
rollout result. The monitor selected top-5, where candidate regret was `0.1877`
and candidate overlap was `0.6300` while one-step regret remained high at
`2.4626`. The resulting value filter achieved a five-seed mean total reward of
`69.4705`, a `6.46%` increase over the 10x12/top4 pilot, and reduced sample
standard deviation from `5.0037` to `1.0004`.

The 20x16 result was also the largest tested configuration that passed the
monitor gate and was reproduced under the corrected geospatial data root. A
macOS audit showed that the packaged 20x16 labels reproduce on the GPKG root,
but not under a root that resolves to a shapefile when both formats are
present. This audit turns the 20x16/top5 route into the current reproducible E0
scale-up evidence.

The larger 50-state candidate-label attempts exposed the boundary of the
current candidate proposal strategy. The macOS 50x24 seed45 run and the Windows
seed46 ablation grid all failed the default top-3/top-4/top-5 monitor checks.
Post-hoc larger top-k checks did not justify training because they either
retained high candidate regret or became mostly solvable by one-step reward.
These failures indicate that the next 50-state attempt should modify candidate
proposal or monitor design rather than training value heads from failed label
sets.

## Paper-facing discussion draft

These experiments suggest that value-head filtering is useful when the label
set passes an explicit candidate-quality gate. The 20x16/top5 result improved
the five-seed reward distribution and substantially reduced seed sensitivity,
which is more important for a planning method than maximizing a single seed.
The result supports the paper's claim that learned value filtering can improve
GeoJEPA-MPC candidate selection when the labels preserve multi-step signal.

The same experiments also show that scale-up is not automatic. Increasing the
candidate count or frontier bias did not improve the 50-state labels under the
tested seeds. This may reflect a mismatch between the current frontier-random
proposal distribution and the return-ranked top-k set at larger state coverage.
It may also reflect a stricter monitor regime that rejects labels when larger
top-k values become too close to one-step reward selection. The honest boundary
is that 20x16/top5 is the current validated scale-up, while 50-state value-head
training requires a redesigned candidate proposal or a pre-registered change to
the gate.

## Recommended manuscript tables

### Table E0-1. Value-head rollout comparison

| metric | 10x12/top4 | 20x16/top5 | interpretation |
|---|---:|---:|---|
| Mean total reward | 65.2566 | 69.4705 | 20x16 improves mean reward. |
| Sample std | 5.0037 | 1.0004 | 20x16 is less seed-sensitive. |
| Minimum reward | 57.9750 | 67.7135 | 20x16 removes the weak seed observed in 10x12. |
| Slope change mean % | -1.2923 | -1.2507 | Similar constraint-side behavior. |
| Continuity change mean | 0.0198 | 0.0192 | Similar continuity behavior. |

### Table E0-2. Monitor-gate transition from pilot to scale-up

| run | selected top-k | candidate regret | candidate overlap | one-step regret |
|---|---:|---:|---:|---:|
| 10x12/h5 seed43 | 4 | 0.4923 | 0.5000 | 1.2916 |
| 20x16/h5 seed44 | 5 | 0.1877 | 0.6300 | 2.4626 |

### Table E0-3. Failed 50-state default-gate rows

| run | best default top-k checked | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---|---:|---:|---:|
| macOS 50x24/h5 seed45 f0.5 | 5 | `stop` | 1.0241 | 0.4160 | 3.0139 |
| Windows 50x16/h5 seed46 f0.5 | 5 | `stop` | 0.3840 | 0.5760 | 1.7764 |
| Windows 50x20/h5 seed46 f0.5 | 5 | `stop` | 0.5841 | 0.5320 | 2.6927 |
| Windows 50x24/h5 seed46 f0.75 | 5 | `stop` | 1.1009 | 0.2960 | 2.5471 |
| Windows 50x24/h5 seed46 f1.0 | 5 | `stop` | 1.3346 | 0.3240 | 2.8339 |

## Claim-evidence map

| Claim | Evidence | Status |
|---|---|---|
| Frontier-random labels can train a useful value filter. | 10x12/top4 and 20x16/top5 value-head rollouts both exceed the prior matched `frontier_independent` mean or the 10x12 pilot baseline. | Supported at pilot scale. |
| 20x16/top5 is stronger than 10x12/top4. | Mean reward increased by `4.2139` and sample std decreased by `4.0034` across seeds0-4. | Supported. |
| The 20x16/top5 result is reproducible under the correct data root. | macOS GPKG reproduction matched packaged arrays exactly or within floating-point tolerance. | Supported. |
| Current 50-state labels should not be trained. | macOS seed45 and Windows seed46 grids failed default and post-hoc monitor checks. | Supported. |
| The method scales beyond 20 states. | Current 50-state tests failed. | Not supported by current evidence. |

## Recommended decision for Paper10

Use `frontier_random050 20x16/h5 seed44 top5` as the current Paper10 E0
scale-up result. Treat 10x12/top4 as the pilot baseline and the 50-state
diagnostics as an explicit boundary result. Do not present 50-state training
claims unless a future label set passes the monitor before training.
