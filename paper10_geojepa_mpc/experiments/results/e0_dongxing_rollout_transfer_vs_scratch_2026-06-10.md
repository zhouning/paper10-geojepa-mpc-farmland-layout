# Dongxing Real-Environment Rollout: Transfer vs Scratch

Date: 2026-06-10

This note records the first real Dongxing/Neijiang environment rollout
comparison for Paper10. It follows the pairwise-only all-parameter diagnostic
and evaluates saved 1000-state checkpoints in the actual 3711-block environment
instead of using only pairwise ranking metrics.

## Code Path

`run_e0_env_rollout_smoke.py` now accepts:

- `--env-source paper9`, the default Bishan/Paper9 prepared-data layout.
- `--env-source neijiang`, which loads
  `county_env_neijiang.py` from `--prepared-dir` and calls
  `make_neijiang_env()`.

This is needed because the Dongxing prepared directory is not organized like
the Bishan Paper9 root. The wrapper still prints a historical "Bishan" label
while loading, but the loaded environment has 3711 Dongxing/Neijiang blocks
from `D:\test\neijiang_cross_region`.

The new adapter path is covered by tests for CLI parsing and dynamic loading of
the Neijiang environment factory.

## Inputs

Prepared Dongxing/Neijiang data:

- `D:\test\neijiang_cross_region\county_env_neijiang.py`
- `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`
- `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`

Checkpoints from the previous all-parameter pairwise-only run:

- transfer:
  `reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt`
- scratch:
  `reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed3035_1000s_3e.pt`

The checkpoints and rollout JSONs are in `reviewer_outputs\`, which is ignored
by git.

## Environment Smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --env-source neijiang --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --prepared-dir D:\test\neijiang_cross_region --rollout-steps 1 --horizon 1 --top-k 5 --seed 0 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode value --progress-interval 1 --output reviewer_outputs\dongxing_rollout_probe\transfer_all_seed3035_1000s_1step.json
```

Result:

| field | value |
|---|---:|
| n blocks | 3711 |
| selected action | 527 |
| completed swaps | 5 |
| executable candidates evaluated | 5 |
| executable valid actions | 3520 |
| reward | 0.08198325343306823 |
| slope change pct | -0.0020495813358267054 |
| contiguity change | 0.0 |
| baimu area change ha | 0.0 |

This confirms that the Paper10 rollout code can execute against the real
Dongxing environment.

## Five-Seed Rollout Setup

Both runs used:

| setting | value |
|---|---:|
| environment source | `neijiang` |
| rollout seeds | `0-4` |
| rollout steps | 100 |
| horizon | 5 |
| top-k | 50 |
| mask mode | `executable` |
| selector | `value_filter` |
| candidate score mode | `blend` |
| candidate value weight | 0.1 |
| device | `cpu` |

Transfer command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --env-source neijiang --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\transfer_all_seed3035_1000s_3e.pt --prepared-dir D:\test\neijiang_cross_region --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --progress-interval 20 --output reviewer_outputs\dongxing_rollout_compare\transfer_all_seed3035_1000s_h5_k50_seeds0-4_100step.json
```

Scratch command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --env-source neijiang --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\scratch_all_seed3035_1000s_3e.pt --prepared-dir D:\test\neijiang_cross_region --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --progress-interval 20 --output reviewer_outputs\dongxing_rollout_compare\scratch_all_seed3035_1000s_h5_k50_seeds0-4_100step.json
```

## Results

Higher total reward and contiguity change are better. More negative slope
change means lower average farmland slope. Baimu area change is measured
relative to the initial state; negative values mean loss of connected
baimu-fang area, which the environment penalizes.

| mode | mean total reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|
| transfer_all | 33.887593362870945 | 4.20111235969505 | 29.0438474218871 | 40.4284925509126 | -0.28770717053397393 | 0.010128132242970355 | -160.54935413917303 |
| scratch_all | 60.85876916823652 | 10.4159501927597 | 44.1107268772245 | 70.7277540677464 | -0.15595155384905524 | 0.007827874229238762 | -96.70650328375578 |

Scratch minus transfer:

| metric | delta |
|---|---:|
| mean total reward | 26.971175805365575 |
| mean total reward percent vs transfer | 79.59011876870735 |
| mean slope change pct | 0.13175561668491869 |
| mean contiguity change | -0.002300258013731593 |
| mean baimu area change ha | 63.84285085541725 |

Per-seed totals:

| seed | transfer reward | transfer slope pct | transfer cont | transfer baimu ha | scratch reward | scratch slope pct | scratch cont | scratch baimu ha |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 34.77448353446728 | -0.29519929339649975 | 0.010714129531639749 | -163.88523700593709 | 58.35679760194085 | -0.13512104253640658 | 0.008964883893820996 | -20.662664889359473 |
| 1 | 40.4284925509126 | -0.28979246695250516 | 0.010757860672585107 | -148.61618866608143 | 63.84449975000173 | -0.1686779107971499 | 0.0069969825512750106 | -161.4764760957241 |
| 2 | 29.043847421887076 | -0.2822038676934818 | 0.009271001880438945 | -142.0872743364811 | 44.110726877224515 | -0.16199335143688504 | 0.008265185638693495 | -136.33396736109256 |
| 3 | 32.258726781986255 | -0.2968953159896378 | 0.008265185638693495 | -224.3530081082344 | 70.72775406774643 | -0.16202750664140295 | 0.007434293960729477 | -108.03379596743584 |
| 4 | 32.93241652510153 | -0.27444490863774507 | 0.011632483491494483 | -123.80506257913113 | 67.25406754426906 | -0.1519379578334317 | 0.0074780251016748345 | -57.025612105166914 |

## Interpretation

The real-environment rollout does not support a strong Dongxing transfer
advantage.

The transfer checkpoint produces larger slope reduction and slightly larger
contiguity improvement, but it loses more connected baimu-fang area. Because
the environment explicitly penalizes baimu-fang area loss, the transfer rollout
has much lower mean total reward than the scratch checkpoint:
`33.8876` vs. `60.8588`.

This result is consistent with the 1000-state pairwise diagnostic: transfer was
not robustly better than scratch there either. The current Dongxing evidence
supports a narrower claim:

- Paper10 can load and run on the real Dongxing/Neijiang environment.
- The 3711-block action-space adapter path works for real rollouts.
- Bishan-initialized transfer is feasible, but it is not yet a reliable
  performance improvement over Dongxing scratch training.

For Paper10, this should be framed as a cross-region stress test or negative
transfer finding unless later experiments improve the transfer checkpoint or
change the adaptation protocol.

## Next Step

The next useful experiment is not another short smoke. Use the same real
Dongxing rollout protocol to test whether transfer improves after one of these
changes:

1. fine-tune with a baimu-aware value target rather than pairwise-only ranking;
2. train multiple transfer and scratch checkpoints and compare checkpoint
   families, not only seed3035;
3. tune the planner's candidate blend weight separately for Dongxing instead
   of reusing the Bishan value-filter setting.
