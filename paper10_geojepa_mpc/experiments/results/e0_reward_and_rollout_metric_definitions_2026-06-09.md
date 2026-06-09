# E0 reward and rollout metric definitions

Date: 2026-06-09

This note records the reward, action feasibility, and rollout-metric
definitions used by the Paper10 E0 `frontier_random050` evidence package. It is
source-grounded Methods material, not a new experiment.

## One-sentence argument

The E0 rollout reward is the sum of per-step environment rewards from the
Paper9-compatible Bishan farmland environment, where each selected block
executes up to five slope-improving paired swaps and the reward combines
stepwise slope improvement, contiguity change, baimu-fang area change, new
baimu-fang patches, and penalties for baimu-area loss or zero-swap actions.

## Source-code basis

| definition | source |
|---|---|
| Environment weights and budget defaults | `county_env.py`, `CountyLevelEnv.__init__` |
| Base action mask | `county_env.py`, `CountyLevelEnv.action_masks` |
| Executable action mask | `paper10_geojepa_mpc/planning/env_masks.py`, `executable_swap_mask` |
| Per-block greedy swap execution | `county_env.py`, `_execute_greedy_in_block` |
| Baimu-fang counting | `county_env.py`, `_count_baimu_fang` |
| Per-step reward and info fields | `county_env.py`, `CountyLevelEnv.step` |
| Rollout step records and summaries | `paper10_geojepa_mpc/experiments/rollout_summary.py` |
| E0 rollout loop | `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py` |
| Value-label returns | `paper10_geojepa_mpc/experiments/value_label_generation.py` |

## Environment defaults

The E0 experiments use `make_env(prepared_dir=...)`, which instantiates
`CountyLevelEnv` with default environment hyperparameters unless explicitly
overridden. The relevant defaults are:

| item | value | meaning |
|---|---:|---|
| `total_budget` | 500 | Maximum parcel swaps available to an episode. |
| `swaps_per_step` | 5 | Maximum paired swaps executed after one block action. |
| `max_steps` | 100 | `total_budget // swaps_per_step`. |
| `slope_weight` | 4000.0 | Weight on normalized stepwise farmland-slope reduction. |
| `cont_weight` | 500.0 | Weight on normalized stepwise contiguity change. |
| `baimu_weight` | 1500.0 | Weight on normalized stepwise baimu-fang area change. |
| `baimu_bonus` | 5.0 | Bonus per newly counted baimu-fang patch. |
| `baimu_area_penalty` | 2000.0 | Extra penalty multiplier when baimu-fang area decreases. |
| `baimu_threshold_m2` | 66700.0 | Minimum connected farmland component area for one baimu-fang patch. |
| `delta_conn` | 0.5 | Connectivity adjustment for selecting farmland parcels to convert. |
| `gamma_conn` | 1.0 | Connectivity adjustment for selecting forest parcels to convert. |

## Action and executable mask

An action is a block identifier. The base environment marks a block as valid
when it still contains at least one unswapped farmland parcel and at least one
unswapped forest parcel:

```text
base_valid(block) = block_farm_avail(block) > 0
                    and block_forest_avail(block) > 0
```

The E0 paper-facing runs use `mask_mode=executable`, which intersects the base
mask with a planner-side executable mask. For each block, the executable mask
looks at currently unswapped farmland and forest parcels. It scores farmland
parcels by:

```text
farm_score(i) = slope(i) - delta_conn * farmland_neighbor_count(i)
```

and forest parcels by:

```text
forest_score(j) = slope(j) - gamma_conn * farmland_neighbor_count(j)
```

The executable mask selects the highest `farm_score` farmland parcel and the
lowest `forest_score` forest parcel. The block is executable only when the
selected farmland parcel has higher slope than the selected forest parcel:

```text
executable(block) = slope(best_farm) > slope(best_forest)
```

Thus, the action mask used by E0 label generation and rollout evaluation is:

```text
action_mask = base_valid and executable
```

This mask prevents the planner from selecting blocks that satisfy the coarse
farmland/forest availability check but would execute zero useful swaps under
the environment's greedy swap rule.

## Greedy block execution

After the planner selects a block, the environment attempts up to
`swaps_per_step=5` paired swaps inside that block. In each paired swap, the
environment:

1. Finds unswapped farmland and forest parcels in the selected block.
2. Selects `best_farm` as the farmland parcel with maximum `farm_score`.
3. Selects `best_forest` as the forest parcel with minimum `forest_score`.
4. Stops if `slope(best_farm) <= slope(best_forest)`.
5. Converts `best_farm` from farmland to forest and `best_forest` from forest
   to farmland.
6. Marks both parcels as swapped and updates slope, area, adjacency, and
   block-availability counters.

The return value `completed` is the number of paired swaps executed by the
selected block action. A zero-swap action receives an additional reward penalty
of `-1.0`.

## State metrics

The environment tracks three main layout metrics.

Average farmland slope is area-weighted:

```text
avg_slope = sum_i slope(i) * area(i) / sum_i area(i),
            over parcels i currently classified as farmland
```

Contiguity is the mean directed count of farmland neighbors per farmland
parcel:

```text
contiguity = total_farmland_adj / max(n_farmland, 1)
```

Baimu-fang patches are connected components of farmland parcels whose total
area is at least `66700.0` square meters. The environment counts these
components with union-find over the parcel adjacency graph and also records
their total area.

## Per-step reward

At reset, the environment stores initial slope, contiguity, baimu-fang count,
baimu-fang area, and farmland area. At each step `t`, after executing the
selected block action, the environment computes:

```text
slope_delta_t = (prev_slope - cur_slope) / (abs(initial_slope) + 1e-8)

cont_delta_t = (cur_cont - prev_cont) / (abs(initial_cont) + 1e-8)

baimu_area_delta_t = (cur_baimu_area - prev_baimu_area)
                     / (initial_farm_area + 1e-8)

baimu_new_count_t = max(0, cur_baimu_count - prev_baimu_count)
```

The raw weighted reward is:

```text
reward_t = 4000.0 * slope_delta_t
           + 500.0 * cont_delta_t
           + 1500.0 * baimu_area_delta_t
           + 5.0 * baimu_new_count_t
```

If baimu-fang area decreases, the environment applies an extra asymmetric
penalty:

```text
if baimu_area_delta_t < 0:
    reward_t = reward_t + 2000.0 * baimu_area_delta_t
```

Because `baimu_area_delta_t` is negative in that case, this term reduces the
reward. If the selected block completes no paired swaps, the environment also
applies:

```text
if completed == 0:
    reward_t = reward_t - 1.0
```

After reward computation, the current slope, contiguity, baimu-fang count, and
baimu-fang area become the previous-step values for the next transition.

## Baimu-fang recomputation interval

Baimu-fang counting is comparatively expensive, so the environment recomputes
baimu-fang count and area every `max(1, max_steps // 20)` steps or at the final
environment step. Under the default `max_steps=100`, this is every 5 steps.
The per-step reward therefore uses the most recently recomputed baimu-fang
state between recomputation points.

## Rollout metrics

The E0 rollout script records one step record per environment action. Each step
record includes:

| field | definition |
|---|---|
| `reward` | Per-step environment reward after applying the selected block action. |
| `completed_swaps` | Number of paired swaps actually executed in the selected block. |
| `n_base_valid` | Number of blocks passing the base environment action mask. |
| `n_executable_valid` | Number of blocks passing the final executable action mask. |
| `n_candidates` | Number of candidate actions evaluated by the planner. |
| `best_cumrew` | Planner-side best cumulative predicted rollout score for the selected step. |
| `slope_change_pct` | Percent change in average farmland slope relative to the initial state. |
| `cont_change` | Absolute contiguity change relative to the initial state. |
| `baimu_area_change_ha` | Baimu-fang area change in hectares relative to the initial state. |

Episode total reward is the un-discounted sum of recorded per-step rewards:

```text
total_reward = sum_t reward_t
```

The five-seed E0 tables report the mean and sample standard deviation of
`total_reward` over seeds 0-4. The reported slope, contiguity, and baimu-area
metrics are final-step metrics extracted from the last step in each episode and
then averaged across seeds.

## Value-label return

Value-label generation uses the same environment reward and executable action
semantics. For each candidate action, the label generator applies the candidate
action, then follows the configured continuation policy for the remaining
horizon. It stores both:

```text
one_step_reward = reward after the candidate action
```

and the discounted multi-step return:

```text
return = sum_{h=0}^{H-1} gamma^h * reward_h
```

The packaged E0 `frontier_random050` labels use `H=5` and `gamma=0.99`.

## Manuscript wording

Suggested Methods wording:

> The environment reward was computed from stepwise changes in area-weighted
> farmland slope, contiguity, and connected baimu-fang area. At each selected
> block, the environment executed up to five connectivity-aware paired swaps,
> replacing the highest-scored unswapped farmland parcel with the lowest-scored
> unswapped forest parcel when the farmland parcel had higher slope. The
> per-step reward combined normalized slope reduction, normalized contiguity
> change, normalized baimu-fang area change, a bonus for newly counted
> baimu-fang patches, an asymmetric penalty for baimu-fang area loss, and a
> zero-swap penalty. Rollout total reward was the un-discounted sum of this
> per-step reward over 100 environment steps.

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| The E0 total reward is an un-discounted episode sum. | `run_e0_env_rollout_smoke.py` accumulates `total_reward += reward`; `rollout_summary.py` reports `total_reward`. | supported |
| E0 uses an executable mask stricter than the base action mask. | `run_e0_env_rollout_smoke.py` and `value_label_generation.py` intersect `env.action_masks()` with `executable_swap_mask` when `mask_mode=executable`. | supported |
| Reward contains slope, contiguity, baimu-area, baimu-count, and penalty terms. | `county_env.py`, `CountyLevelEnv.step`. | supported |
| Final slope, contiguity, and baimu-area metrics are final-step metrics. | `rollout_summary.py`, `summarize_rollout`. | supported |

## Assumptions or missing inputs

- This note describes the reward implementation in the packaged repository. If
  the final manuscript must align word-for-word with a prior Paper9 paper, the
  prior paper's published notation should be reconciled with this code-derived
  notation.
- The note does not introduce new reward ablations or statistical tests.

## Chinese author notes

- 这份说明把之前 Methods 草稿里“reward 公式待补”的缺口补上了，公式来自
  `county_env.py` 和 E0 rollout 代码。
- 注意 `slope_change_pct` 在结果表里是相对初始状态的最终变化百分比；每步
  reward 里的 `slope_delta_t` 是相对上一步的归一化改变量，二者不要混写。
- `total_reward` 是 100 步环境 reward 的未折扣总和；value label 的 `return`
  才是 `gamma=0.99` 的折扣多步回报。
