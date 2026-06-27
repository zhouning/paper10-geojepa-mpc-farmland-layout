# Paper10 real-data long-horizon matched 5-seed audit

Date: 2026-06-27

Status: source-derived descriptive matched 5-seed result; no rollout was rerun.

The locked 5-seed comparison reports a higher value-filter mean reward, but inferential superiority is not supported. Do not use this audit as a robust transfer, broad scale-up, or statistical-significance claim.

post-hoc tuning of thresholds, top_k, horizon, or candidate-value weight remains disallowed after seeing the seed0 pilot and 5-seed outcomes.

## Aggregate outcomes

| metric | matched Paper9 | value-filter | delta candidate-baseline |
|---|---:|---:|---:|
| total reward mean | 67.5437 | 69.4705 | 1.9269 |
| total reward sample std | 7.2246 | 1.0004 | -6.2242 |
| total reward min | 60.7625 | 67.7135 | 6.9510 |
| total reward max | 78.0925 | 70.2252 | -7.8673 |
| negative reward steps | 51 | 41 | -10 |
| candidate win count | 0 | 3 | 3 |

## Seed-level reward deltas

| seed | matched Paper9 | value-filter | delta | first divergence step |
|---:|---:|---:|---:|---:|
| 0 | 70.9543 | 67.7135 | -3.2408 | 9 |
| 1 | 66.6115 | 70.2252 | 3.6137 | 1 |
| 2 | 61.2976 | 69.7218 | 8.4242 | 1 |
| 3 | 60.7625 | 69.8245 | 9.0620 | 2 |
| 4 | 78.0925 | 69.8677 | -8.2248 | 2 |

## Seed0 pilot linkage

- Linkage available: `True`
- Matches pilot audit: `True`

## Evidence boundary

- The audit supports a bounded descriptive matched 5-seed Bishan statement.
- The seed0 pilot remains a loss for value-filter, so the result must be framed seed-wise rather than as uniform improvement.
- Inferential superiority is not supported because no predefined statistical test is introduced here.
- No cross-region transfer superiority or 50-state scale-up claim is supported.

## Source files

- baseline: `paper10_geojepa_mpc\experiments\results\e0_env_rollout_5seed_h5_k50_executable_mask.json`
- candidate: `paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json`
- candidate: `paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json`
