# E0 Real-Env Rollout Smoke

Date: 2026-06-07

Purpose: verify that a Paper10 PyTorch checkpoint can drive the real Paper9
`CountyLevelEnv` through the Paper9 `mpc_select_action` interface.

## Configuration

- checkpoint: `paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt`
- prepared dir: `D:/test`
- model: Paper10 `rank` checkpoint selected by candidate top-5 regret
- env: Paper9 Bishan `CountyLevelEnv`
- max steps: 3
- horizon: 3
- top_k: 20
- seed: 0
- device: CPU

## Result

The rollout completed 3 env steps without adapter or environment errors.

| step | action | n_valid | n_candidates | select sec | reward | slope change pct | cont change | baimu area ha |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 925 | 2381 | 20 | 2.006 | 5.078250 | -0.025436 | -0.000051 | -12.835856 |
| 2 | 959 | 2381 | 20 | 1.583 | 0.649538 | -0.035418 | 0.000203 | -5.933360 |
| 3 | 1006 | 2381 | 20 | 1.141 | 0.773619 | -0.060071 | 0.000559 | -9.543517 |

Total reward: 6.501407

Elapsed time including env build: 30.55 s

## Interpretation

This is a smoke test, not a planning-quality result. It confirms the execution
chain:

`Paper10 checkpoint -> TorchCheckpointMPCAdapter -> Paper9 mpc_select_action -> CountyLevelEnv.step`

The next validation should run a slightly longer short rollout, such as 10
steps with the same H=3/K=20 settings, then compare directionally with the
Paper9 ONNX baseline logs before attempting a full 100-step episode.
