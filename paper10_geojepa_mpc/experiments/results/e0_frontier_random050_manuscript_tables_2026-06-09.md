# E0 frontier_random050 manuscript tables

Date: 2026-06-09

These tables are manuscript-ready summaries of the current E0
`frontier_random050` evidence. They are derived from the packaged 10x12/top4
pilot, the packaged 20x16/top5 scale-up, the macOS GPKG reproduction audit, and
the Windows 50-state ablation diagnostics.

## Table E0-1. Monitor-selected training gates

**Caption.** Monitor-gated label selection for the two value-head training runs
used as Paper10 E0 evidence. Candidate regret is the return gap under the
candidate-score top-k set. Candidate overlap measures agreement with the
return-ranked top-k set. One-step regret quantifies whether the multi-step label
adds signal beyond immediate reward.

| run | states | candidates | horizon | selected top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| `10x12/h5 seed43` | 10 | 12 | 5 | 4 | `continue` | 0.4923 | 0.5000 | 1.2916 |
| `20x16/h5 seed44` | 20 | 16 | 5 | 5 | `continue` | 0.1877 | 0.6300 | 2.4626 |

**Use in text.** The gate shifted from top-4 to top-5 as label coverage and
candidate count increased. The 20x16/top5 gate preserved lower candidate regret
and higher overlap while retaining material one-step regret.

## Table E0-2. Five-seed rollout comparison

**Caption.** Rollout performance for the 10x12/top4 pilot and 20x16/top5
scale-up. Both use executable masks, `selector=value_filter`, horizon 5, global
top-k 50, blend candidate score mode, and candidate value weight 0.1 over
100-step rollouts for seeds 0-4.

| metric | 10x12/top4 | 20x16/top5 | change |
|---|---:|---:|---:|
| Mean total reward | 65.2566 | 69.4705 | +4.2139 |
| Relative mean change | n/a | n/a | +6.46% |
| Sample std | 5.0037 | 1.0004 | -4.0034 |
| Minimum total reward | 57.9750 | 67.7135 | +9.7385 |
| Maximum total reward | 69.4293 | 70.2252 | +0.7959 |
| Mean slope change % | -1.2923 | -1.2507 | +0.0415 |
| Mean continuity change | 0.0198 | 0.0192 | -0.0006 |
| Mean baimu-area change ha | -231.3513 | -207.2639 | +24.0873 |

**Use in text.** The 20x16/top5 value filter improved mean reward and reduced
seed sensitivity. The lower standard deviation and higher minimum reward are
the strongest stability evidence.

## Table E0-3. Seed-wise rollout rewards

**Caption.** Seed-wise 100-step rollout rewards for the two trained
`frontier_random050` value heads. The 20x16/top5 run reduced the weak-seed
behavior seen in the 10x12/top4 pilot.

| seed | 10x12/top4 reward | 20x16/top5 reward | change |
|---:|---:|---:|---:|
| 0 | 69.4293 | 67.7135 | -1.7158 |
| 1 | 69.1794 | 70.2252 | +1.0459 |
| 2 | 57.9750 | 69.7218 | +11.7468 |
| 3 | 67.4951 | 69.8245 | +2.3294 |
| 4 | 62.2042 | 69.8677 | +7.6635 |

**Use in text.** The seed0 reward was lower in 20x16/top5, but seeds 1-4 were
higher, and seed2 improved by `11.7468`. This supports the claim that the
scale-up improved the rollout distribution rather than only the best case.

## Table E0-4. Default-gate failures for 50-state labels

**Caption.** Default monitor outcomes for tested 50-state label sets. None of
these rows passed top-3, top-4, or top-5. The table reports the least-bad
default top-k per row, which was top-5 in each case.

| run | platform | states | candidates | frontier fraction | seed | top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| `50x24/h5 seed45` | macOS | 50 | 24 | 0.5 | 45 | 5 | `stop` | 1.0241 | 0.4160 | 3.0139 |
| `50x16/h5 seed46` | Windows | 50 | 16 | 0.5 | 46 | 5 | `stop` | 0.3840 | 0.5760 | 1.7764 |
| `50x20/h5 seed46` | Windows | 50 | 20 | 0.5 | 46 | 5 | `stop` | 0.5841 | 0.5320 | 2.6927 |
| `50x24/h5 seed46` | Windows | 50 | 24 | 0.75 | 46 | 5 | `stop` | 1.1009 | 0.2960 | 2.5471 |
| `50x24/h5 seed46` | Windows | 50 | 24 | 1.0 | 46 | 5 | `stop` | 1.3346 | 0.3240 | 2.8339 |

**Use in text.** The current 50-state evidence should be framed as a boundary
result. These rows should not be trained because none passed the monitor gate.

## Table E0-5. Post-hoc larger top-k diagnostics for failed Windows rows

**Caption.** Post-hoc larger top-k monitor checks for Windows seed46 50-state
labels. These checks were diagnostic only and did not change the training
decision.

| run | top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---|---:|---:|---:|
| `50x16 f0.5` | 6 | `stop` | 0.3010 | 0.6533 | 1.4748 |
| `50x16 f0.5` | 8 | `stop` | 0.1324 | 0.7350 | 0.1056 |
| `50x16 f0.5` | 10 | `stop` | 0.1324 | 0.7560 | 0.0811 |
| `50x16 f0.5` | 12 | `stop` | 0.1238 | 0.8067 | 0.0725 |
| `50x20 f0.5` | 6 | `stop` | 0.5164 | 0.5467 | 1.3441 |
| `50x20 f0.5` | 8 | `stop` | 0.4685 | 0.6175 | 0.1588 |
| `50x20 f0.5` | 10 | `stop` | 0.0780 | 0.7280 | 0.0739 |
| `50x20 f0.5` | 12 | `stop` | 0.0739 | 0.7550 | 0.0000 |
| `50x24 f0.75` | 6 | `stop` | 0.9522 | 0.3467 | 2.4113 |
| `50x24 f0.75` | 8 | `stop` | 0.9118 | 0.4250 | 2.0970 |
| `50x24 f0.75` | 10 | `stop` | 0.6931 | 0.4960 | 0.3802 |
| `50x24 f0.75` | 12 | `stop` | 0.2912 | 0.6167 | 0.3419 |
| `50x24 f1.0` | 6 | `stop` | 1.2449 | 0.3967 | 2.8339 |
| `50x24 f1.0` | 8 | `stop` | 1.2432 | 0.4675 | 2.7080 |
| `50x24 f1.0` | 10 | `stop` | 0.5200 | 0.5780 | 0.6433 |
| `50x24 f1.0` | 12 | `stop` | 0.2691 | 0.6400 | 0.6011 |

**Use in text.** Larger top-k values did not rescue the failed 50-state rows.
For `50x16` and `50x20`, larger top-k values reduced candidate regret but also
made one-step regret too small. For the `50x24` rows, candidate regret or
overlap remained limiting until the top-k became broad enough to weaken the
filtering task.

## Table E0-S1. macOS GPKG reproduction audit

**Caption.** Array-level comparison between the packaged 20x16/h5 seed44 label
set and a macOS rerun using the GPKG data root.

| array | reproduction result |
|---|---|
| `actions` | exact match |
| `returns` | exact match |
| `one_step_rewards` | exact match |
| `n_valid_actions` | exact match |
| `state_steps` | exact match |
| `states_bf` | allclose, max abs diff `7.424993508919897e-09` |
| `states_gf` | exact match |
| `candidate_scores` | allclose, max abs diff `1.1920928955078125e-07` |

**Use in text.** This table belongs in supplementary material unless the paper
needs a dedicated reproducibility subsection in the main Results.

## Placement recommendation

- Main text: Tables E0-1, E0-2, and a compact version of E0-4.
- Supplementary material: Tables E0-3, E0-5, and E0-S1.
- Figure candidates: convert Table E0-3 into a seed-wise reward dot plot and
  Table E0-5 into a top-k diagnostic line plot.

Figure-ready CSVs are now tracked as:

- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`

Draft PNG/SVG figures can be generated offline with:

```bash
python scripts/paper10/plot_frontier_random050_figures.py
```
