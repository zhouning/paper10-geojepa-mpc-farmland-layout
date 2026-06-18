# Paper10 real-environment rollout smoke

Date: 2026-06-18

Status: controlled summary of a short full-Bishan real-environment rollout. This is not a planning-quality result and does not change manuscript performance claims.

## Command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --rollout-steps 5 --horizon 3 --top-k 20 --seed 0 --device cpu --mask-mode executable --output reviewer_outputs\paper10_real_env_smoke_5step_h3_k20_seed0.json
```

Raw local output: `reviewer_outputs\paper10_real_env_smoke_5step_h3_k20_seed0.json`

## Configuration

| field | value |
|---|---|
| checkpoint | `paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt` |
| prepared_dir | `D:\test` |
| env_source | `paper9` |
| seed | `0` |
| horizon | `3` |
| top_k | `20` |
| rollout_steps | `5` |
| mask_mode | `executable` |
| selector | `paper9` |
| scoring | `reward` |

## Outcome

| metric | value |
|---|---:|
| steps run | 5 |
| total reward | 7.6466 |
| elapsed seconds | 7.36 |
| min base-valid actions | 2381 |
| min executable-valid actions | 2313 |
| mean selection seconds | 1.3100 |
| positive reward steps | 5 |
| negative reward steps | 0 |
| final slope change pct | -0.074700 |
| final contiguity change | 0.001627 |
| final baimu area change ha | -7.826418 |

## Step Trace

| step | action | reward | executable valid | candidates | completed swaps | slope change pct | cont change | baimu area ha | select sec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 11 | 0.5524 | 2316 | 20 | 5 | -0.014697 | -0.000254 | 0.000000 | 2.2086 |
| 2 | 1289 | 0.5956 | 2315 | 20 | 5 | -0.028878 | -0.000051 | 0.000000 | 1.5387 |
| 3 | 2540 | 0.4641 | 2315 | 20 | 3 | -0.039238 | 0.000305 | 0.000000 | 1.2682 |
| 4 | 2200 | 1.1723 | 2314 | 20 | 5 | -0.065887 | 0.001068 | 0.000000 | 0.8197 |
| 5 | 2346 | 4.8622 | 2313 | 20 | 5 | -0.074700 | 0.001627 | -7.826418 | 0.7147 |

## Interpretation Boundary

This smoke confirms the execution chain from a Paper10 checkpoint through the Paper9 adapter, MPC selector, executable mask, and full Bishan `CountyLevelEnv.step`. It is a five-step engineering check, not evidence for a new planning-quality or scale-up claim.
