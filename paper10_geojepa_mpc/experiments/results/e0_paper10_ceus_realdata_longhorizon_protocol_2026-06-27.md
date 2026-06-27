# Paper10 CEUS real-data long-horizon matched rollout protocol

Status: locked pilot protocol before full matched real-data evaluation.

This protocol is created before running the 100-step seed0 pilot. It is intended
to prevent post-hoc threshold, seed, horizon, or candidate-weight tuning.

## Purpose

The CEUS review raised a real-data evaluation risk: short full-Bishan smokes
confirm execution-chain reachability, but they are not planning-quality
evidence. The next experiment tests whether the matched Paper9 and Paper10
value-filter policies diverge under a longer, fixed real-data rollout.

## Locked pilot settings

| field | value |
|---|---|
| data root | `D:\test` |
| environment | full Bishan `CountyLevelEnv` through the Paper9 adapter |
| pilot seed | `0` |
| rollout length | `100` steps |
| horizon | `5` |
| top_k | `50` |
| mask | `executable` |
| scoring | `reward` |
| baseline policy | matched Paper9 selector using `e0_bishan_rank_seed2028/rank_seed2028.pt` |
| Paper10 policy | value-filter selector using `e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt` |
| Paper10 candidate score | `blend` |
| Paper10 candidate value weight | `0.1` |
| random continuation mode | `independent` |
| stable candidate order | `false` |

## Pilot commands

Matched Paper9:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --rollout-steps 100 --horizon 5 --top-k 50 --seed 0 --device cpu --mask-mode executable --selector paper9 --progress-interval 20 --output reviewer_outputs\paper10_real_env_matched_paper9_100step_h5_k50_seed0_2026-06-27.json
```

Paper10 value-filter:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt --prepared-dir D:\test --rollout-steps 100 --horizon 5 --top-k 50 --seed 0 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --progress-interval 20 --output reviewer_outputs\paper10_real_env_matched_value_filter_100step_h5_k50_seed0_2026-06-27.json
```

## Decision rules

- This seed0 pilot estimates runtime and checks whether the five-step identical
  traces diverge under a 100-step rollout.
- The pilot alone must not be written as final planning-quality evidence.
- If both commands finish and produce interpretable output, the next
  confirmatory step is the same protocol on seeds `0-4`.
- If the two policies are equal or Paper10 is worse on seed0, keep Paper10
  claim-bounded and do not tune thresholds, top_k, or candidate weights to
  rescue the result.
- If Paper10 is better on seed0, treat it only as a pilot signal until the
  seeds `0-4` matched run is complete.

## Reporting boundary

The follow-up audit should report total reward, secondary metrics, negative
reward steps, action-trace divergence, and whether the run is complete. It
should use descriptive statistics only and should not introduce p-values or
new cross-region transfer claims.
