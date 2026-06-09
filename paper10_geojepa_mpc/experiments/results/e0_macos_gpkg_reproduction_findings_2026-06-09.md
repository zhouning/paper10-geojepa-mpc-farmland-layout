# E0 macOS GPKG reproduction findings

Date: 2026-06-09

This note records the macOS local reproduction audit for the Paper10
`frontier_random050` value-label experiments. The audit was needed because a
local 20x16/h5 seed44 rerun initially failed to reproduce the packaged label
gate, even though the repository already contains a passing 20x16/top5 report.

## Canonical macOS data root

The reproducible macOS data root is:

`/Users/zhouning/paper10_runs/data/bishan_prepared_13township_2600_gpkg`

This root uses:

- `DLTB_with_slope.gpkg` from `/Users/zhouning/Downloads/bishan/DLTB_with_slope.gpkg`
- `tool2/` and `results_real/` symlinked from the full Bishan prepared data
- a 13-township `townships.json`, matching the 2600-block checkpoint

The earlier local root
`/Users/zhouning/paper10_runs/data/bishan_prepared_13township_2600`
resolved to `DLTB_with_slope.shp`, because `make_env()` prefers `.shp` when
both `.shp` and `.gpkg` exist. That shapefile root produced materially
different labels and failed to reproduce the packaged seed44 gate.

## Packaged 20x16/h5 seed44 reproduction

Packaged label:

`paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`

Local reproduced label:

`/Users/zhouning/paper10_runs/frontier_random050_20x16_h5_seed44_gpkg_repro/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`

Array-level comparison:

| array | result |
|---|---|
| `actions` | exact match |
| `returns` | exact match |
| `one_step_rewards` | exact match |
| `n_valid_actions` | exact match |
| `state_steps` | exact match |
| `states_bf` | allclose, max abs diff `7.424993508919897e-09` |
| `states_gf` | exact match |
| `candidate_scores` | allclose, max abs diff `1.1920928955078125e-07` |

Monitor results:

| top-k | decision | candidate regret | candidate overlap | one-step regret |
|---:|---|---:|---:|---:|
| 3 | `stop` | 0.6507 | 0.3667 | 2.6006 |
| 4 | `stop` | 0.4680 | 0.4875 | 2.4626 |
| 5 | `continue` | 0.1877 | 0.6300 | 2.4626 |

Conclusion: the repository-packaged macOS-continuable route is reproducible on
the GPKG root:

`frontier_random050 20x16/h5 seed44, selected top-k=5`.

## 50x24/h5 seed45 macOS rerun

The macOS runner was rerun with:

- `DATA_ROOT=/Users/zhouning/paper10_runs/data/bishan_prepared_13township_2600_gpkg`
- `RUN_NAME=frontier_random050_50x24_h5_seed45_gpkg`
- `PYTHON_BIN=/Users/zhouning/miniconda3/envs/farmland-mpc/bin/python`
- `DEVICE=cpu`

Run directory:

`/Users/zhouning/paper10_runs/frontier_random050_50x24_h5_seed45_gpkg`

Generated label:

`/Users/zhouning/paper10_runs/frontier_random050_50x24_h5_seed45_gpkg/e0_value_labels_frontier_random050_rank_seed2028_50x24_h5_seed45.npz`

Label generation summary:

| metric | value |
|---|---:|
| states | 50 |
| candidates | 24 |
| horizon | 5 |
| seed | 45 |
| elapsed sec | 158.3617 |
| return mean | 1.4992 |
| return std | 3.4453 |
| one-step reward mean | 0.7767 |
| one-step reward std | 1.7099 |

Default monitor results:

| top-k | decision | candidate regret | candidate overlap | one-step regret |
|---:|---|---:|---:|---:|
| 3 | `stop` | 1.4471 | 0.2867 | 3.2828 |
| 4 | `stop` | 1.0797 | 0.3300 | 3.2754 |
| 5 | `stop` | 1.0241 | 0.4160 | 3.0139 |

Additional post-hoc monitor checks:

| top-k | decision | candidate regret | candidate overlap | one-step regret |
|---:|---|---:|---:|---:|
| 6 | `stop` | 0.8443 | 0.4767 | 1.2257 |
| 8 | `stop` | 0.8443 | 0.5500 | 0.4713 |
| 10 | `stop` | 0.3835 | 0.6680 | 0.0720 |
| 12 | `stop` | 0.0544 | 0.7533 | 0.0544 |

Conclusion: do not continue the 50x24/h5 seed45 label set into value-head
training under the current gate. It fails the default top-3/top-4/top-5
monitor, and larger top-k values either retain too much candidate regret or
become mostly solvable by one-step reward.

## Verification

The macOS runner first executed the repository tests with:

```bash
/Users/zhouning/miniconda3/envs/farmland-mpc/bin/python -m pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider
```

Result: `99 passed`.
