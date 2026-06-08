# E0 Real-Env Rollout Mask Diagnostics

Date: 2026-06-07

Checkpoint:
`paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt`

Environment:
Paper9 `CountyLevelEnv`, Bishan prepared data under `D:\test`, seed 0.

## Finding

Paper9's base `action_masks()` marks a block valid when it has at least one
available farmland parcel and one available forest parcel. The environment
step, however, calls `_execute_greedy_in_block()`, which may still complete
zero swaps if the current best farmland-to-forest pair no longer satisfies the
greedy slope-improvement condition.

In the H=3/K=20 base Paper10 rollout, block `2540` became the dominant failure
case. In the 35-step diagnostic replay it was selected 13 times; after the
first useful selection, 12 selections completed zero swaps and 10 of those
had negative reward. In the 100-step legacy base rollout it was selected 41
times.

## Paper10 Mask Prototype

`planning.env_masks.executable_swap_mask` is a Paper10-only planner-side mask.
It mirrors the first-pair feasibility condition used inside
`CountyLevelEnv._execute_greedy_in_block()` and is applied as:

`action_mask = env.action_masks() & executable_swap_mask(env)`

This does not modify Paper9 production code.

## Results

| Run | H/K | Mask | Steps | Total reward | Slope change | Cont change | Baimu area change | Zero-swap steps | Negative zero-swap steps |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 35-step diagnostic | 3/20 | base | 35 | 20.4401 | -0.5559% | 0.0034 | -141.43 ha | 12 | 10 |
| 35-step diagnostic | 3/20 | executable | 35 | 31.0775 | -0.7179% | 0.0031 | -179.88 ha | 0 | 0 |
| full episode | 3/20 | base | 100 | 8.2181 | -0.9371% | 0.0101 | -174.27 ha | legacy log | legacy log |
| full episode | 3/20 | executable | 100 | 63.4219 | -1.2604% | 0.0212 | -186.65 ha | 0 | 0 |
| full episode, seed 0 | 5/50 | executable | 100 | 70.9543 | -1.2933% | 0.0185 | -234.37 ha | 0 | 0 |
| full episode, seeds 0-4 mean | 5/50 | executable | 100 | 67.5437 | -1.2645% | 0.0195 | -211.85 ha | 0 | 0 |

Paper9 ONNX ensemble baseline at H=5/K=50 over five seeds:

| Baseline | Seeds | Mean slope | Seed-0 slope | Mean cont | Mean baimu area change | Mean reward |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Paper9 ONNX ensemble | 5 | -1.5439% | -1.5914% | 0.0214 | -345.10 ha | 62.1798 |

## Interpretation

The executable mask fixes a real planning-interface issue: it prevents the MPC
from spending steps on blocks that remain base-mask valid but cannot execute a
beneficial greedy pair swap. This turns Paper10 from a stuck rollout into a
usable rollout.

The mask is not evidence that the latent world model has caught up with
Paper9. Under matched H=5/K=50, Paper10's five-seed mean slope improvement is
`-1.2645%`, still behind Paper9's five-seed mean `-1.5439%`. Paper10 has
better mean reward here because it loses less baimu-fang area, but Paper9 is
stronger on the primary slope-reduction target. The next scientific target is
better action-ranking/world-model training and candidate-supervision coverage.

## Rollout Candidate Diagnostic

An additional 10-step diagnostic was run on the H=5/K=50 executable-mask
rollout. At each visited state, 50 executable actions were sampled, their true
one-step rewards were measured with env snapshot/restore, and the current
checkpoint's reward head was used to rank them.

Result:

| States | Candidate actions/state | Model top-1 hit | Model top-1 regret | Model top-10 hit | Model top-10 regret | Negative reward fraction |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 50 | 0.5000 | 0.3323 | 1.0000 | 0.0000 | 0.1280 |

This early-rollout sample says the current reward head usually keeps the best
one-step action inside its top-10 candidate set, but its top-1 ranking is still
noisy. Since H=5/K=50 already considers a wide candidate set, the remaining
gap to Paper9 is unlikely to be solved by only increasing `top_k`. A better
next experiment is to train a value-aware ranking target, for example ranking
actions by short-horizon rollout return rather than one-step reward alone.
