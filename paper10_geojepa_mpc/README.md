# Paper10 GeoJEPA-MPC

This directory is an isolated research scaffold for Paper10:

`JEPA-Regularized Geospatial World Models for Constrained Farmland Layout Planning`

It does not modify Paper9 production code. The first coded subset focuses on
Experiment 0 compatibility:

- read existing Paper9 Tool2 datasets without mutating them
- keep the Paper9 selected-block transition contract
- add a latent hook for SIGReg-style regularization
- add optional gated GeoFM fusion
- expose pairwise action-ranking helpers

## Reused Local Assets

- Smoke Paper9 Tool2 data:
  `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2`
- Full Bishan Tool2 data:
  `tool2`
- Existing Bishan GeoFM embeddings:
  `paper7/data/block_geofm_embeddings.npy`

## First Commands

Run unit tests:

```powershell
python -m pytest paper10_geojepa_mpc/tests -q
```

Run the Experiment 0 smoke data summary:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_smoke.py
```

Run the Experiment 0 smoke training loop:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_train_smoke.py
```

Run a full Bishan one-epoch feasibility probe:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_train_bishan_probe.py --config rank --epochs 1 --batch-size 16 --transition-samples 6000 --pairwise-states 1000 --pairwise-subsample 16 --n-pairs 4 --device cpu
```

Run the full Bishan E0 experiment runner:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_bishan_experiment.py --configs mse_only,rank,rank_sigreg --seeds 2026 --epochs 5 --batch-size 16 --transition-samples 6000 --pairwise-states 1000 --pairwise-subsample 16 --n-pairs 4 --eval-seed 12345 --device cpu --output paper10_geojepa_mpc/experiments/results/e0_bishan_5epoch_seed2026.json
```

Score a saved checkpoint against pairwise candidates:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_score_checkpoint.py --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --pairwise tool2/pairwise.npz --top-k 5 --batch-states 4 --max-states 1000 --device cpu --output paper10_geojepa_mpc/experiments/results/e0_bishan_rank_seed2028_checkpoint_scoring.json
```

Smoke-test Paper9's `mpc_select_action` with a Paper10 checkpoint adapter:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_mpc_select_smoke.py --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --pairwise tool2/pairwise.npz --state-index 0 --top-k 5 --horizon 3 --device cpu --output paper10_geojepa_mpc/experiments/results/e0_mpc_select_smoke_state0_h3.json
```

Run a real Paper9 `CountyLevelEnv` short rollout with a Paper10 checkpoint:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --prepared-dir . --rollout-steps 3 --horizon 3 --top-k 20 --seed 0 --device cpu --output paper10_geojepa_mpc/experiments/results/e0_env_rollout_smoke_3step_h3_k20.json
```

Run a full 100-step rollout with Paper10's executable-swap mask:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seed 0 --device cpu --mask-mode executable --output paper10_geojepa_mpc/experiments/results/e0_env_rollout_full1_h5_k50_seed0_executable_mask.json
```

Run the matched five-seed rollout comparison:

```powershell
python paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --output paper10_geojepa_mpc/experiments/results/e0_env_rollout_5seed_h5_k50_executable_mask.json
```

Summarize a rollout JSON:

```powershell
python -m paper10_geojepa_mpc.experiments.rollout_summary paper10_geojepa_mpc/experiments/results/e0_env_rollout_full1_h5_k50_seed0_executable_mask.json --output paper10_geojepa_mpc/experiments/results/e0_env_rollout_full1_h5_k50_seed0_executable_mask_summary.json
```

Diagnose model ranking on states visited by a rollout:

```powershell
python -m paper10_geojepa_mpc.experiments.rollout_candidate_diagnostics --checkpoint paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt --prepared-dir . --rollout-steps 10 --horizon 5 --top-k 50 --candidate-actions 50 --metric-top-k 10 --seed 0 --device cpu --output paper10_geojepa_mpc/experiments/results/e0_rollout_candidate_diag_10step_h5_k50_seed0.json
```

Note: `--rollout-steps` only controls how many steps this diagnostic script
runs. `--max-steps` changes `CountyLevelEnv.max_steps`, which also changes
the baimu-fang recomputation interval; use it only when that altered episode
semantics is intentional.

## Current Rollout Finding

Paper9's base `action_masks()` only checks whether a block still contains
available farmland and forest. It can leave a block valid even when
`_execute_greedy_in_block()` cannot complete a beneficial pair swap. In the
Paper10 H=3/K=20 100-step base rollout, action `2540` was selected 41 times
and the final slope change was only `-0.9371%`.

Paper10 therefore includes an optional `planning.env_masks.executable_swap_mask`
prototype that mirrors the first-pair feasibility condition in
`CountyLevelEnv._execute_greedy_in_block()`. It does not modify Paper9 code.
With the same checkpoint and seed:

| Setting | Mask | Steps | Total reward | Slope change | Cont change | Baimu area change | Zero-swap steps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| H=3/K=20 | base | 100 | 8.2181 | -0.9371% | 0.0101 | -174.27 ha | legacy log |
| H=3/K=20 | executable | 100 | 63.4219 | -1.2604% | 0.0212 | -186.65 ha | 0 |
| H=5/K=50 seed 0 | executable | 100 | 70.9543 | -1.2933% | 0.0185 | -234.37 ha | 0 |
| H=5/K=50 seeds 0-4 mean | executable | 100 | 67.5437 | -1.2645% | 0.0195 | -211.85 ha | 0 |

The matched Paper9 ONNX ensemble baseline at H=5/K=50 over five seeds has
mean slope change `-1.5439%` (seed 0: `-1.5914%`). Current Paper10 is now
usable for real-env rollouts but remains below Paper9 on the primary slope
metric; the next target is training quality and candidate-supervision
coverage, not more planner plumbing.

A 10-step rollout-state candidate diagnostic found top-10 hit rate `1.0000`
and top-1 hit rate `0.5000` over 50 executable sampled actions per state. This
suggests the current one-step reward head usually keeps good actions in the
candidate pool but is noisy at the very top. The next modeling target should
be short-horizon/value-aware ranking supervision, not simply larger `top_k`.

## Current Scope

Included now:

- `models.sigreg.sigreg_loss`
- `models.fusion.GatedFeatureFusion`
- `models.geojepa_transition_model.GeoJEPATransitionModel`
- `training.ranking` pairwise helpers
- `training.data_io.summarize_npz_headers`
- `training.e0_training` smoke-scale training utilities
- `planning.env_masks.executable_swap_mask` Paper10-only rollout feasibility mask
- `experiments.rollout_summary` rollout diagnostics
- `experiments.rollout_candidate_diagnostics` rollout-state ranking diagnostics
- `experiments.results.e0_bishan_probe_2026-06-07.json` full-scale one-epoch CPU probe
- `experiments.results.e0_bishan_5epoch_seed2026.json` full-scale five-epoch CPU run
- `experiments.results.e0_bishan_5epoch_3seed_summary.md` three-seed five-epoch summary
- `experiments.results.e0_bishan_5epoch_seed2026_candidate_summary.md` candidate top-K metrics summary
- `experiments.results.e0_bishan_5epoch_3seed_candidate_summary.md` three-seed candidate top-K summary
- `experiments.checkpoints.e0_bishan_rank_seed2028.rank_seed2028.pt` primary rank checkpoint selected by top-5 regret
- `experiments.results.e0_bishan_rank_seed2028_checkpoint_scoring.json` checkpoint scoring verification
- `experiments.results.e0_mpc_select_smoke_state0_h3.json` Paper9 MPC select-action adapter smoke
- `experiments.results.e0_env_rollout_smoke_3step_h3_k20.json` real-env 3-step rollout smoke
- `experiments.results.e0_env_rollout_full1_h5_k50_seed0_executable_mask_summary.json` matched H=5/K=50 Paper10 rollout summary
- `experiments.results.e0_env_rollout_5seed_h5_k50_executable_mask.json` matched five-seed Paper10 rollout
- `experiments.results.e0_rollout_candidate_diag_10step_h5_k50_seed0.json` rollout-state candidate ranking diagnostic

Not included yet:

- ONNX export
- production Paper9 Tool 4 integration for the executable mask
- long-epoch Bishan and GeoFM ablation experiments
- raster or parcel-aware encoder
