# Paper10 GeoJEPA-MPC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first tested Paper10 code scaffold for GeoJEPA-MPC without modifying Paper9 production code.

**Architecture:** The first implementation isolates Paper10 in `paper10_geojepa_mpc/`. It introduces a SIGReg regularizer, gated feature/GeoFM fusion, an action-conditioned latent transition model with the same forward contract as Paper9 (`next_block, next_global, reward`), and smoke-data utilities for the existing Tool2 datasets.

**Tech Stack:** Python 3, PyTorch, NumPy, pytest.

---

## File Structure

- Create `paper10_geojepa_mpc/__init__.py`: package marker.
- Create `paper10_geojepa_mpc/models/__init__.py`: model exports.
- Create `paper10_geojepa_mpc/models/sigreg.py`: Epps-Pulley / Cramer-Wold SIGReg implementation for latent tensors.
- Create `paper10_geojepa_mpc/models/fusion.py`: gated fusion between engineered block features and GeoFM embeddings.
- Create `paper10_geojepa_mpc/models/geojepa_transition_model.py`: Paper10 transition model with optional GeoFM channel and latent regularization hook.
- Create `paper10_geojepa_mpc/training/__init__.py`: training exports.
- Create `paper10_geojepa_mpc/training/ranking.py`: pairwise margin ranking loss and rank accuracy helpers.
- Create `paper10_geojepa_mpc/training/data_io.py`: load and summarize Paper9 Tool2 `.npz` files without mutating them.
- Create `paper10_geojepa_mpc/experiments/run_e0_smoke.py`: smoke entry point for Experiment 0.
- Create `paper10_geojepa_mpc/tests/test_sigreg.py`: SIGReg behavior tests.
- Create `paper10_geojepa_mpc/tests/test_fusion.py`: gated fusion tests.
- Create `paper10_geojepa_mpc/tests/test_geojepa_transition_model.py`: forward-contract tests.
- Create `paper10_geojepa_mpc/tests/test_ranking.py`: ranking loss tests.
- Create `paper10_geojepa_mpc/tests/test_data_io.py`: smoke dataset shape tests.
- Create `paper10_geojepa_mpc/README.md`: scope, assets, and first commands.

## Task 1: Scaffold Package and Data IO

**Files:**
- Create: `paper10_geojepa_mpc/__init__.py`
- Create: `paper10_geojepa_mpc/training/__init__.py`
- Create: `paper10_geojepa_mpc/training/data_io.py`
- Test: `paper10_geojepa_mpc/tests/test_data_io.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from paper10_geojepa_mpc.training.data_io import summarize_npz_headers


def test_summarize_npz_headers_reads_smoke_pairwise_shapes():
    path = Path("arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/pairwise.npz")

    summary = summarize_npz_headers(path)

    assert summary["states_bf"]["shape"] == (100, 30, 17)
    assert summary["states_gf"]["shape"] == (100, 12)
    assert summary["actions"]["shape"] == (100, 10)
    assert summary["rewards"]["shape"] == (100, 10)
    assert summary["rewards"]["dtype"] == "float32"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_data_io.py -q`

Expected: FAIL because `paper10_geojepa_mpc.training.data_io` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from pathlib import Path
from typing import Dict, Tuple
import zipfile

from numpy.lib import format as np_format


def _read_npy_header(file_obj) -> Tuple[tuple, str]:
    version = np_format.read_magic(file_obj)
    if version == (1, 0):
        shape, _, dtype = np_format.read_array_header_1_0(file_obj)
    elif version == (2, 0):
        shape, _, dtype = np_format.read_array_header_2_0(file_obj)
    else:
        shape, _, dtype = np_format.read_array_header_2_0(file_obj)
    return tuple(shape), str(dtype)


def summarize_npz_headers(path: str | Path) -> Dict[str, Dict[str, object]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    out = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            key = name[:-4] if name.endswith(".npy") else name
            with archive.open(name) as file_obj:
                shape, dtype = _read_npy_header(file_obj)
            out[key] = {"shape": shape, "dtype": dtype}
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_data_io.py -q`

Expected: PASS.

## Task 2: Implement SIGReg

**Files:**
- Create: `paper10_geojepa_mpc/models/sigreg.py`
- Test: `paper10_geojepa_mpc/tests/test_sigreg.py`

- [ ] **Step 1: Write failing tests**

```python
import torch

from paper10_geojepa_mpc.models.sigreg import sigreg_loss


def test_sigreg_loss_is_scalar_and_nonnegative():
    z = torch.randn(32, 16)

    loss = sigreg_loss(z, n_projections=32, n_knots=16)

    assert loss.ndim == 0
    assert torch.isfinite(loss)
    assert loss.item() >= 0.0


def test_sigreg_loss_accepts_sequence_latents():
    z = torch.randn(4, 8, 12)

    loss = sigreg_loss(z, n_projections=16, n_knots=8)

    assert loss.ndim == 0
    assert torch.isfinite(loss)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_sigreg.py -q`

Expected: FAIL because `sigreg_loss` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
import torch


def sigreg_loss(
    embeddings: torch.Tensor,
    n_projections: int = 128,
    n_knots: int = 32,
    knot_min: float = 0.2,
    knot_max: float = 4.0,
) -> torch.Tensor:
    z = embeddings.reshape(-1, embeddings.shape[-1])
    z = (z - z.mean(dim=0, keepdim=True)) / z.std(dim=0, keepdim=True).clamp_min(1e-6)
    dim = z.shape[-1]
    directions = torch.randn(dim, n_projections, device=z.device, dtype=z.dtype)
    directions = directions / directions.norm(dim=0, keepdim=True).clamp_min(1e-6)
    projected = z @ directions
    knots = torch.linspace(knot_min, knot_max, n_knots, device=z.device, dtype=z.dtype)
    values = projected.unsqueeze(-1) * knots
    empirical_real = torch.cos(values).mean(dim=0)
    empirical_imag = torch.sin(values).mean(dim=0)
    target = torch.exp(-0.5 * knots.square()).unsqueeze(0)
    return ((empirical_real - target).square() + empirical_imag.square()).mean()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_sigreg.py -q`

Expected: PASS.

## Task 3: Implement Gated Fusion

**Files:**
- Create: `paper10_geojepa_mpc/models/fusion.py`
- Test: `paper10_geojepa_mpc/tests/test_fusion.py`

- [ ] **Step 1: Write failing test**

```python
import torch

from paper10_geojepa_mpc.models.fusion import GatedFeatureFusion


def test_gated_feature_fusion_returns_encoded_blocks_and_gate_values():
    fusion = GatedFeatureFusion(engineered_dim=17, geofm_dim=64, hidden_dim=32)
    engineered = torch.randn(5, 30, 17)
    geofm = torch.randn(5, 30, 64)

    encoded, gates = fusion(engineered, geofm)

    assert encoded.shape == (5, 30, 32)
    assert gates.shape == (5, 30, 1)
    assert torch.all(gates >= 0.0)
    assert torch.all(gates <= 1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_fusion.py -q`

Expected: FAIL because `GatedFeatureFusion` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
import torch
import torch.nn as nn


class GatedFeatureFusion(nn.Module):
    def __init__(self, engineered_dim: int, geofm_dim: int, hidden_dim: int):
        super().__init__()
        self.engineered_encoder = nn.Sequential(
            nn.Linear(engineered_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
        )
        self.geofm_encoder = nn.Sequential(
            nn.Linear(geofm_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
        )
        self.gate = nn.Sequential(
            nn.Linear(engineered_dim + geofm_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, 1), nn.Sigmoid(),
        )

    def forward(self, engineered: torch.Tensor, geofm: torch.Tensor):
        if engineered.shape[:-1] != geofm.shape[:-1]:
            raise ValueError("engineered and geofm features must share batch/block axes")
        h_engineered = self.engineered_encoder(engineered)
        h_geofm = self.geofm_encoder(geofm)
        gate = self.gate(torch.cat([engineered, geofm], dim=-1))
        return gate * h_engineered + (1.0 - gate) * h_geofm, gate
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_fusion.py -q`

Expected: PASS.

## Task 4: Implement GeoJEPA Transition Model

**Files:**
- Create: `paper10_geojepa_mpc/models/geojepa_transition_model.py`
- Test: `paper10_geojepa_mpc/tests/test_geojepa_transition_model.py`

- [ ] **Step 1: Write failing tests**

```python
import torch

from paper10_geojepa_mpc.models.geojepa_transition_model import GeoJEPATransitionModel


def test_geojepa_transition_model_matches_paper9_forward_contract_without_geofm():
    model = GeoJEPATransitionModel(n_blocks=30, k_global=12)
    block_features = torch.randn(4, 30, 17)
    global_features = torch.randn(4, 12)
    actions = torch.tensor([0, 5, 10, 29])

    next_block, next_global, reward, aux = model(block_features, global_features, actions)

    assert next_block.shape == block_features.shape
    assert next_global.shape == global_features.shape
    assert reward.shape == (4, 1)
    assert aux["latent"].shape[0] == 4
    unchanged = torch.ones(30, dtype=torch.bool)
    unchanged[actions[0]] = False
    assert torch.allclose(next_block[0, unchanged], block_features[0, unchanged])


def test_geojepa_transition_model_accepts_geofm_features():
    model = GeoJEPATransitionModel(n_blocks=30, k_global=12, geofm_dim=64)
    block_features = torch.randn(2, 30, 17)
    geofm_features = torch.randn(2, 30, 64)
    global_features = torch.randn(2, 12)
    actions = torch.tensor([3, 7])

    next_block, next_global, reward, aux = model(
        block_features, global_features, actions, geofm_features=geofm_features
    )

    assert next_block.shape == (2, 30, 17)
    assert next_global.shape == (2, 12)
    assert reward.shape == (2, 1)
    assert aux["fusion_gate"].shape == (2, 30, 1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_geojepa_transition_model.py -q`

Expected: FAIL because `GeoJEPATransitionModel` does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement `GeoJEPATransitionModel` with selected-block residual update, global residual update, reward head, and optional GeoFM fusion.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_geojepa_transition_model.py -q`

Expected: PASS.

## Task 5: Implement Ranking Helpers

**Files:**
- Create: `paper10_geojepa_mpc/training/ranking.py`
- Test: `paper10_geojepa_mpc/tests/test_ranking.py`

- [ ] **Step 1: Write failing tests**

```python
import torch

from paper10_geojepa_mpc.training.ranking import pairwise_margin_ranking_loss, pairwise_rank_accuracy


def test_pairwise_ranking_loss_is_zero_when_margin_is_satisfied():
    pred_i = torch.tensor([2.0, 0.0])
    pred_j = torch.tensor([0.0, 2.0])
    true_i = torch.tensor([3.0, 1.0])
    true_j = torch.tensor([1.0, 3.0])

    loss = pairwise_margin_ranking_loss(pred_i, pred_j, true_i, true_j, margin=0.1)

    assert loss.item() == 0.0


def test_pairwise_rank_accuracy_counts_correct_signs():
    pred_i = torch.tensor([2.0, 0.0, 1.0])
    pred_j = torch.tensor([0.0, 2.0, 1.0])
    true_i = torch.tensor([3.0, 1.0, 5.0])
    true_j = torch.tensor([1.0, 3.0, 5.0])

    acc = pairwise_rank_accuracy(pred_i, pred_j, true_i, true_j)

    assert acc == 1.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_ranking.py -q`

Expected: FAIL because `ranking.py` does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement margin loss and sign accuracy with zero-difference true pairs ignored.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest paper10_geojepa_mpc/tests/test_ranking.py -q`

Expected: PASS.

## Task 6: Add README and Smoke Entry Point

**Files:**
- Create: `paper10_geojepa_mpc/README.md`
- Create: `paper10_geojepa_mpc/experiments/run_e0_smoke.py`

- [ ] **Step 1: Write README**

Document scope, existing assets, and the first smoke commands.

- [ ] **Step 2: Add smoke script**

Add a script that prints header summaries for the smoke `transitions.npz` and `pairwise.npz`.

- [ ] **Step 3: Run smoke script**

Run: `python paper10_geojepa_mpc/experiments/run_e0_smoke.py`

Expected: prints the 30-block transition and pairwise shapes.

## Self-Review

- Spec coverage: implements the first coded subset of the Paper10 spec: isolated directory, SIGReg, gated fusion, transition model contract, ranking helpers, and smoke asset loading.
- Out of scope for this plan: full training loop, ONNX export, Tool4 backport, raster encoder, long experiments.
- No production Paper9 files are modified.
