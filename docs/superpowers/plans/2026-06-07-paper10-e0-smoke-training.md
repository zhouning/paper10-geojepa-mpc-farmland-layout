# Paper10 E0 Smoke Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal Experiment 0 training loop that proves the Paper10 latent transition model, pairwise ranking loss, and SIGReg hook can train end-to-end on the existing 30-block Paper9 smoke data.

**Architecture:** Keep training utilities isolated in `paper10_geojepa_mpc/training/e0_training.py`. The utilities load existing `.npz` arrays, compute transition MSE, sample pairwise action comparisons, optionally add SIGReg on `aux["latent"]`, and return compact metrics. A new experiment script runs three short smoke configs: MSE only, MSE plus ranking, and MSE plus ranking plus SIGReg.

**Tech Stack:** Python 3, NumPy, PyTorch, pytest.

---

## File Structure

- Create `paper10_geojepa_mpc/training/e0_training.py`: E0 data loading, losses, training loop, and ranking evaluation.
- Create `paper10_geojepa_mpc/tests/test_e0_training.py`: focused unit tests using synthetic tiny arrays.
- Create `paper10_geojepa_mpc/experiments/run_e0_train_smoke.py`: command-line smoke runner for the real 30-block Paper9 smoke dataset.

## Task 1: E0 Training Utilities

**Files:**
- Create: `paper10_geojepa_mpc/training/e0_training.py`
- Test: `paper10_geojepa_mpc/tests/test_e0_training.py`

- [ ] **Step 1: Write failing tests**

Test three behaviors:

1. `transition_mse_loss` returns a finite scalar and metric dictionary for a real `GeoJEPATransitionModel`.
2. `pairwise_ranking_loss_for_batch` returns a finite scalar loss and an accuracy in `[0, 1]`.
3. `train_e0_smoke_config` runs one epoch on a tiny synthetic `.npz` dataset and returns `final_loss`, `ranking_acc`, and `epochs`.

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc/tests/test_e0_training.py -q -p no:cacheprovider
```

Expected: FAIL because `paper10_geojepa_mpc.training.e0_training` does not exist.

- [ ] **Step 3: Implement minimal utilities**

Implement:

- `load_npz_arrays(path) -> dict[str, np.ndarray]`
- `transition_mse_loss(model, bf, gf, actions, rewards, nbf, ngf, geofm_features=None) -> tuple[Tensor, dict]`
- `pairwise_ranking_loss_for_batch(model, bf, gf, actions, rewards, n_pairs, margin, generator=None) -> tuple[Tensor, float]`
- `evaluate_pairwise_rank_accuracy(model, bf, gf, actions, rewards, max_states=64, n_pairs=16) -> float`
- `train_e0_smoke_config(...) -> dict`

- [ ] **Step 4: Run tests to verify they pass**

Run the same pytest command. Expected: PASS.

## Task 2: E0 Smoke Training Script

**Files:**
- Create: `paper10_geojepa_mpc/experiments/run_e0_train_smoke.py`

- [ ] **Step 1: Add script**

The script should:

- use `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/transitions.npz`
- use `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/pairwise.npz`
- train three configs for a short run:
  - `mse_only`: `lambda_rank=0.0`, `lambda_sig=0.0`
  - `rank`: `lambda_rank=1.0`, `lambda_sig=0.0`
  - `rank_sigreg`: `lambda_rank=1.0`, `lambda_sig=0.01`
- print JSON metrics.

- [ ] **Step 2: Run script**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe paper10_geojepa_mpc/experiments/run_e0_train_smoke.py
```

Expected: exits 0 and prints metrics for all three configs.

## Verification

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe paper10_geojepa_mpc/experiments/run_e0_train_smoke.py
```

Expected: all tests pass, smoke training prints JSON metrics, and no Paper9 production files are modified.
