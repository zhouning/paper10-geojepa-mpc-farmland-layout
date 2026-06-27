# Paper10 real-environment rollout smoke

Date: 2026-06-27

Status: controlled summary of a short full-Bishan real-environment rollout. This is not a planning-quality result and does not change manuscript performance claims.

## Command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --rollout-steps 5 --horizon 5 --top-k 50 --seed 0 --device cpu --mask-mode executable --selector paper9 --output reviewer_outputs\paper10_real_env_matched_paper9_5step_h5_k50_seed0_2026-06-27.json
```

Raw local output: `reviewer_outputs\paper10_real_env_matched_paper9_5step_h5_k50_seed0_2026-06-27.json`

## Configuration

| field | value |
|---|---|
| checkpoint | `paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt` |
| prepared_dir | `D:\test` |
| env_source | `paper9` |
| seed | `0` |
| horizon | `5` |
| top_k | `50` |
| n_rollouts | `1` |
| rollout_steps | `5` |
| mask_mode | `executable` |
| selector | `paper9` |
| scoring | `reward` |
| candidate_score_mode | `value` |
| candidate_value_weight | `0.5` |
| random_continuation_mode | `independent` |
| stable_candidate_order | `False` |

## Outcome

| metric | value |
|---|---:|
| steps run | 5 |
| total reward | 2.4254 |
| elapsed seconds | 9.25 |
| min base-valid actions | 2381 |
| min executable-valid actions | 2312 |
| mean selection seconds | 1.6590 |
| positive reward steps | 4 |
| negative reward steps | 1 |
| final slope change pct | -0.103306 |
| final contiguity change | 0.000763 |
| final baimu area change ha | -24.969708 |

## Step Trace

| step | action | reward | executable valid | candidates | completed swaps | slope change pct | cont change | baimu area ha | select sec |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1434 | 0.6850 | 2316 | 50 | 3 | -0.016592 | 0.000153 | 0.000000 | 2.1449 |
| 2 | 2580 | 0.5801 | 2315 | 50 | 3 | -0.030031 | 0.000458 | 0.000000 | 1.8261 |
| 3 | 2414 | 1.2983 | 2314 | 50 | 2 | -0.063729 | 0.000102 | 0.000000 | 1.9936 |
| 4 | 2197 | 0.4960 | 2313 | 50 | 5 | -0.075420 | 0.000305 | 0.000000 | 1.2999 |
| 5 | 2379 | -0.6340 | 2312 | 50 | 5 | -0.103306 | 0.000763 | -24.969708 | 1.0303 |

## Interpretation Boundary

This smoke confirms the execution chain from a Paper10 checkpoint through the Paper9 adapter, MPC selector, executable mask, and full Bishan `CountyLevelEnv.step`. It is a five-step engineering check, not evidence for a new planning-quality or scale-up claim.

The trace includes a negative reward step, so this run is not short-horizon performance evidence for the selector.
