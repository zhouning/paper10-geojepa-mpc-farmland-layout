# Dongxing Paper10 Transfer Smoke

Date: 2026-06-10

This note records the first current-Paper10 smoke run on the prepared Neijiang
Dongxing cross-region arrays. It follows the local data audit in
`e0_dongxing_local_data_cross_region_audit_2026-06-10.md` and addresses the
known incompatibility between the Bishan 2,600-block checkpoint and the
Dongxing 3,711-block action space.

This is not a full Dongxing Paper10 experiment. It is a minimal engineering and
real-data compatibility check that verifies:

- Dongxing `pairwise_data_neijiang.npz` can drive the current
  `GeoJEPATransitionModel` value-head training path.
- A Bishan checkpoint can seed dimension-compatible weights.
- The mismatched `action_emb.weight` is skipped and reinitialized for 3,711
  actions.
- The saved 3,711-block checkpoint can be loaded by the existing scoring entry.

## Code Path Added

The training path now supports:

- `trainable_scope="value_head_action_emb"`
  - trains `value_head.*`
  - trains `action_emb.*`
  - freezes the other Paper10 model components
- `allow_init_action_emb_mismatch=True`
  - keeps the old exact-checkpoint behavior disabled by default
  - allows only `n_blocks` / `n_actions` to differ in transfer mode
  - copies same-shaped checkpoint tensors
  - skips only `action_emb.weight` when its shape differs

The command-line entry
`paper10_geojepa_mpc.experiments.run_e0_value_head_train` exposes the same
controls via:

- `--allow-init-action-emb-mismatch`
- `--trainable-scope value_head_action_emb`

## Inputs

Prepared Dongxing arrays:

- `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`
- `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`

Initial Bishan checkpoint:

- `paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt`

Output directory:

- `reviewer_outputs\dongxing_paper10_transfer_smoke\`

The output directory is ignored by git.

## Training Smoke Command

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz --pairwise-path D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --allow-init-action-emb-mismatch --trainable-scope value_head_action_emb --n-blocks 3711 --checkpoint-path reviewer_outputs\dongxing_paper10_transfer_smoke\value_head_action_seed3035.pt --output reviewer_outputs\dongxing_paper10_transfer_smoke\metrics.json --epochs 1 --batch-size 2 --n-pairs 2 --pairwise-subsample 4 --pairwise-states 5 --candidate-top-k 3 --candidate-batch-states 1 --candidate-max-states 5 --seed 3035 --eval-seed 12345 --device cpu
```

## Training Smoke Result

| metric | value |
|---|---:|
| elapsed sec | 2.916362799995113 |
| trainable scope | `value_head_action_emb` |
| transition loss enabled | `false` |
| pairwise label key | `rewards` |
| n transition samples | 6000 |
| n pairwise states | 5 |
| n trainable parameters | 127,073 |
| init copied state key count | 26 |
| init skipped state keys | `["action_emb.weight"]` |
| final loss | 0.17867423593997955 |
| final MSE | 0.0 |
| final rank loss | 0.17867423593997955 |
| ranking accuracy | 0.699999988079071 |
| candidate states | 5 |
| candidate actions | 50 |
| candidate top1 hit rate | 0.0 |
| candidate top1 regret | 1.4176451832056045 |
| candidate top3 hit rate | 0.0 |
| candidate top3 regret | 1.1590841084718704 |
| best checkpoint epoch | 1 |
| best checkpoint metric | `candidate_top3_regret` |
| best checkpoint value | 1.1590841084718704 |

Interpretation:

- The transfer path did not attempt to use the 2,600-row Bishan action
  embedding on 3,711 Dongxing action IDs.
- Transition MSE was intentionally disabled for this value/action-embedding
  smoke, so the large transition arrays were used only for row-count/header
  resolution.
- The pairwise file was real Dongxing data, not synthetic test data.

## Independent Checkpoint Scoring Smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_score_checkpoint --checkpoint reviewer_outputs\dongxing_paper10_transfer_smoke\value_head_action_seed3035.pt --pairwise D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --top-k 3 --batch-states 1 --max-states 5 --device cpu --output reviewer_outputs\dongxing_paper10_transfer_smoke\score_checkpoint_reward_head.json
```

Result:

| metric | value |
|---|---:|
| candidate states | 5 |
| candidate actions | 50 |
| candidate top1 hit rate | 0.0 |
| candidate top1 regret | 1.4176451832056045 |
| candidate top3 hit rate | 0.0 |
| candidate top3 regret | 1.15813367664814 |
| checkpoint epoch | 1 |
| checkpoint metric | `candidate_top3_regret` |
| checkpoint value | 1.1590841084718704 |

This scoring script uses the reward-head scoring path, while the training smoke
used value-head rank training. The purpose of this second command is therefore
checkpoint load/forward compatibility, not a separate value-head quality claim.

## Verification

Focused tests:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m pytest paper10_geojepa_mpc\tests\test_e0_training.py paper10_geojepa_mpc\tests\test_run_e0_value_head_train.py -q -p no:cacheprovider --basetemp .pytest_tmp\paper10-green-focused
```

Result: 18 passed.

Full package tests:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider --basetemp .pytest_tmp\paper10-green-full
```

Result: 119 passed.

## Limits and Next Steps

This smoke removes the immediate engineering blocker, but it does not yet prove
the Paper10 Dongxing claim. The next Paper10 work should be:

1. Train a real Dongxing value/action-embedding transfer run on more pairwise
   states and multiple seeds.
2. Add a from-scratch Dongxing baseline with the same value-label budget.
3. Run Dongxing MPC rollout evaluation with the saved 3,711-block checkpoints.
4. Compare transfer vs. scratch vs. old Paper9-style baseline on the same
   Dongxing metrics: reward, slope change, contiguity, and baimu-area change.
