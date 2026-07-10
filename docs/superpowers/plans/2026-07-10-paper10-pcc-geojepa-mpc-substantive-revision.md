# Paper10 PCC-GeoJEPA-MPC Substantive Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and independently confirm a deployable PCC-GeoJEPA-MPC planner that improves cumulative reward without degrading slope, contiguity, or connected farmland area, then rebuild the CEUS manuscript and figures from the frozen evidence.

**Architecture:** Add a new action-relative multi-objective ensemble beside the legacy GeoJEPA model, calibrate candidate-versus-reference differences by trajectory-level joint split conformal prediction, and select actions through a conservative Pareto gate with fail-closed fallback and executed-action-only residual scaling. A machine-readable protocol registry physically separates training, calibration, development, and confirmation; the legacy manuscript evidence remains intact until the new confirmation report passes every locked success gate.

**Tech Stack:** Python 3.13/3.14, PyTorch, NumPy, pytest, GeoPandas, matplotlib, existing Paper9/Paper10 environment adapters, Markdown/JSON/CSV/SVG/PDF/TIFF artifacts.

---

## Execution Rules

1. Run every code task as RED -> verify RED -> GREEN -> verify GREEN -> commit.
2. Do not edit legacy `GeoJEPATransitionModel` checkpoint semantics. PCC uses its own model class and checkpoint loader.
3. Do not use seeds 0-19 in any new confirmation artifact.
4. Do not run a confirmation command until the protocol registry status is `frozen` and its digest has been committed.
5. After freeze, only implementation defects that prevent the declared computation may be fixed. Any scientific configuration change requires protocol `pcc_v2` and a new confirmation seed namespace.
6. Never add `%SystemDrive%/` or `2503.05774v1.pdf` to Git.
7. Use `D:\adk\.venv\Scripts\python.exe` for repository tests and scientific runs unless a command explicitly verifies another interpreter.

## File Map

### New scientific modules

- `paper10_geojepa_mpc/models/pcc_geojepa.py`: action-relative ensemble member and typed multi-objective output.
- `paper10_geojepa_mpc/training/pcc_training.py`: bootstrap membership, normalized multi-loss training, and PCC checkpoints.
- `paper10_geojepa_mpc/planning/paired_conformal.py`: trajectory-level joint calibration.
- `paper10_geojepa_mpc/planning/executed_feedback.py`: bounded executed-outcome residual scaling.
- `paper10_geojepa_mpc/planning/pcc_selector.py`: candidate proposal, conservative Pareto gate, deterministic selection, and fallback.
- `paper10_geojepa_mpc/experiments/pcc_objectives.py`: objective orientation and local-horizon outcome extraction.
- `paper10_geojepa_mpc/experiments/pcc_protocol_registry.py`: partition validation, freeze digest, and confirmation guard.
- `paper10_geojepa_mpc/experiments/pcc_value_labels.py`: baseline-continuation multi-objective labels.
- `paper10_geojepa_mpc/experiments/run_pcc_train.py`: ensemble training CLI.
- `paper10_geojepa_mpc/experiments/run_pcc_policy_iteration.py`: exactly two
  offline conservative policy-improvement rounds.
- `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`: no-oracle rollout runner and resumable artifacts.
- `paper10_geojepa_mpc/experiments/run_pcc_development.py`: bounded development grid and lexicographic freeze selection.
- `paper10_geojepa_mpc/experiments/pcc_confirmatory_statistics.py`: hierarchical paired inference and success gates.
- `paper10_geojepa_mpc/experiments/pcc_information_set_audit.py`: audit of environment access and frozen digests.
- `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`: declared seed partitions, grid, baselines, and tests.
- `scripts/paper10/plot_pcc_manuscript_figures.py`: Python-only Figures 1-5 and source-data exports.

### New tests

- `paper10_geojepa_mpc/tests/test_pcc_protocol_registry.py`
- `paper10_geojepa_mpc/tests/test_pcc_geojepa.py`
- `paper10_geojepa_mpc/tests/test_pcc_objectives.py`
- `paper10_geojepa_mpc/tests/test_pcc_value_labels.py`
- `paper10_geojepa_mpc/tests/test_pcc_training.py`
- `paper10_geojepa_mpc/tests/test_pcc_policy_iteration.py`
- `paper10_geojepa_mpc/tests/test_paired_conformal.py`
- `paper10_geojepa_mpc/tests/test_executed_feedback.py`
- `paper10_geojepa_mpc/tests/test_pcc_selector.py`
- `paper10_geojepa_mpc/tests/test_run_pcc_rollouts.py`
- `paper10_geojepa_mpc/tests/test_pcc_development.py`
- `paper10_geojepa_mpc/tests/test_pcc_confirmatory_statistics.py`
- `paper10_geojepa_mpc/tests/test_pcc_information_set_audit.py`
- `paper10_geojepa_mpc/tests/test_pcc_figure_assets.py`

## Phase I: Scientific Contracts and Core Algorithm

### Task 1: Lock Objective Orientation and the Protocol State Machine

**Files:**
- Create: `paper10_geojepa_mpc/experiments/pcc_objectives.py`
- Create: `paper10_geojepa_mpc/experiments/pcc_protocol_registry.py`
- Create: `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`
- Test: `paper10_geojepa_mpc/tests/test_pcc_objectives.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_protocol_registry.py`

- [ ] **Step 1: Write failing objective-orientation tests**

```python
from paper10_geojepa_mpc.experiments.pcc_objectives import (
    OBJECTIVE_NAMES,
    oriented_outcome,
)


def test_oriented_outcome_makes_larger_values_better():
    start = {"avg_slope": 10.0, "contiguity": 0.20, "baimu_area_ha": 100.0}
    end = {"avg_slope": 9.0, "contiguity": 0.25, "baimu_area_ha": 103.0}
    out = oriented_outcome(7.5, start, end)
    assert OBJECTIVE_NAMES == (
        "reward", "slope_benefit", "contiguity_benefit", "connected_area_benefit"
    )
    assert out.tolist() == [7.5, 10.0, 0.05, 3.0]
```

- [ ] **Step 2: Run the objective test and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_objectives.py -q
```

Expected: collection fails because `pcc_objectives` does not exist.

- [ ] **Step 3: Implement the objective contract**

```python
from collections.abc import Mapping
import numpy as np

OBJECTIVE_NAMES = (
    "reward",
    "slope_benefit",
    "contiguity_benefit",
    "connected_area_benefit",
)


def oriented_outcome(
    reward: float,
    start: Mapping[str, float],
    end: Mapping[str, float],
) -> np.ndarray:
    slope_denominator = max(abs(float(start["avg_slope"])), 1e-8)
    return np.asarray(
        [
            float(reward),
            100.0 * (float(start["avg_slope"]) - float(end["avg_slope"]))
            / slope_denominator,
            float(end["contiguity"]) - float(start["contiguity"]),
            float(end["baimu_area_ha"]) - float(start["baimu_area_ha"]),
        ],
        dtype=np.float64,
    )
```

- [ ] **Step 4: Write failing registry tests**

```python
import json
from pathlib import Path
import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
    validate_registry,
)


def test_registry_rejects_partition_overlap(tmp_path: Path):
    payload = {
        "protocol_id": "pcc_v1",
        "status": "development",
        "partitions": {"train": [1000], "calibration": [1000], "development": [3000], "confirmation": [4000]},
        "model_seeds": [5101, 5102, 5103],
    }
    with pytest.raises(ValueError, match="overlap"):
        validate_registry(payload)


def test_registry_rejects_model_seed_used_as_data_seed():
    payload = load_registry()
    payload["model_seeds"][0] = payload["partitions"]["train"][0]
    with pytest.raises(ValueError, match="model seed overlaps"):
        validate_registry(payload)


def test_pcc_v1_rejects_any_change_to_locked_seed_namespaces():
    payload = load_registry()
    payload["partitions"]["confirmation"] = payload["partitions"]["confirmation"][:-1]
    with pytest.raises(ValueError, match="locked partition mismatch"):
        validate_registry(payload)


def test_registry_contains_locked_scientific_contract():
    payload = load_registry()
    assert payload["online_information_set"]["unexecuted_real_reward_queries"] == 0
    assert payload["compute_budget"]["single_model_candidate_equivalents"] == 50
    assert payload["success_gates"]["minimum_jointly_supporting_model_seeds"] == 2
    assert payload["success_gates"]["bishan"]["reward_lower_bound_strictly_positive"] is True
    assert payload["success_gates"]["dongxing"]["reward_lower_bound_minimum"] == 0.0
    assert "oracle_action_audit_diagnostic" not in payload["deployable_baselines"]


def test_frozen_registry_has_stable_digest_and_cannot_be_refrozen(tmp_path: Path):
    source = tmp_path / "registry.json"
    source.write_text(json.dumps(load_registry()), encoding="utf-8")
    frozen = freeze_registry(source, selected_config={"ensemble_size": 3})
    assert frozen["status"] == "frozen"
    assert len(frozen["frozen_digest"]) == 64
    with pytest.raises(ValueError, match="already frozen"):
        freeze_registry(source, selected_config={"ensemble_size": 5})
```

- [ ] **Step 5: Run registry tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
```

Expected: collection fails because `pcc_protocol_registry` does not exist.

- [ ] **Step 6: Implement registry validation and freezing**

```python
import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path(__file__).with_name("protocols") / "pcc_v1.json"
LOCKED_PCC_V1_PARTITIONS = {
    "train": tuple(range(1000, 1008)),
    "calibration": tuple(range(2000, 2020)),
    "development": tuple(range(3000, 3010)),
    "confirmation": tuple(range(4000, 4020)),
    "dongxing_adaptation": tuple(range(6000, 6004)),
    "dongxing_calibration": tuple(range(7000, 7020)),
    "dongxing_confirmation": tuple(range(8000, 8020)),
}


def _canonical(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "frozen_digest"}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_registry(path: str | Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_registry(payload: dict[str, Any]) -> None:
    roles = payload["partitions"]
    observed: dict[int, str] = {}
    for role, seeds in roles.items():
        for seed in seeds:
            seed = int(seed)
            if seed in observed:
                raise ValueError(f"partition overlap: seed {seed} in {observed[seed]} and {role}")
            if 0 <= seed <= 19:
                raise ValueError(f"historical seed forbidden: {seed}")
            observed[seed] = role
    if len(set(payload["model_seeds"])) != len(payload["model_seeds"]):
        raise ValueError("model seed overlap")
    overlap = set(map(int, payload["model_seeds"])) & set(observed)
    if overlap:
        raise ValueError(f"model seed overlaps data partition: {sorted(overlap)}")
    if payload.get("protocol_id") == "pcc_v1":
        actual = {role: tuple(map(int, seeds)) for role, seeds in roles.items()}
        if actual != LOCKED_PCC_V1_PARTITIONS:
            raise ValueError("locked partition mismatch for pcc_v1")
        if tuple(map(int, payload["model_seeds"])) != (5101, 5102, 5103):
            raise ValueError("locked model seed mismatch for pcc_v1")


def freeze_registry(path: str | Path, selected_config: dict[str, Any]) -> dict[str, Any]:
    path = Path(path)
    payload = load_registry(path)
    validate_registry(payload)
    if payload["status"] != "development":
        raise ValueError("registry is already frozen")
    payload["status"] = "frozen"
    payload["selected_config"] = selected_config
    payload["frozen_digest"] = hashlib.sha256(_canonical(payload)).hexdigest()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
```

- [ ] **Step 7: Add the declared `pcc_v1` registry**

```json
{
  "protocol_id": "pcc_v1",
  "status": "development",
  "partitions": {
    "train": [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007],
    "calibration": [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
    "development": [3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009],
    "confirmation": [4000, 4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4010, 4011, 4012, 4013, 4014, 4015, 4016, 4017, 4018, 4019],
    "dongxing_adaptation": [6000, 6001, 6002, 6003],
    "dongxing_calibration": [7000, 7001, 7002, 7003, 7004, 7005, 7006, 7007, 7008, 7009, 7010, 7011, 7012, 7013, 7014, 7015, 7016, 7017, 7018, 7019],
    "dongxing_confirmation": [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018, 8019]
  },
  "model_seeds": [5101, 5102, 5103],
  "horizons": [1, 3, 5],
  "offline_sampling": {
    "train": {"states_per_trajectory": 20, "candidate_actions": 8},
    "calibration": {"states_per_trajectory": 10, "candidate_actions": 8},
    "dongxing_adaptation": {"states_per_trajectory": 20, "candidate_actions": 8},
    "dongxing_calibration": {"states_per_trajectory": 10, "candidate_actions": 8}
  },
  "grid": {
    "ensemble_size": [3, 5],
    "joint_coverage": [0.8, 0.9, 0.95],
    "tolerance_scale": [0.0, 0.05, 0.1],
    "planning_horizon": [3, 5],
    "residual_window": [10, 20],
    "policy_round": [1, 2]
  },
  "confirmation": {
    "rollout_steps": 100,
    "one_sided_confidence": 0.95,
    "primary_comparison_count": 1,
    "objective_noninferiority_margin": 0.0
  },
  "online_information_set": {
    "current_observable_state": true,
    "executable_action_mask": true,
    "frozen_models_calibrators_and_policies": true,
    "executed_action_outcomes_only": true,
    "unexecuted_real_reward_queries": 0,
    "environment_clone_rewind_or_restore": false,
    "confirmation_weight_updates": false
  },
  "deployable_baselines": [
    "executable_random",
    "paper9_mpc",
    "legacy_value_filter",
    "model_reward_greedy",
    "rank_only",
    "distributional_risk",
    "online_expert_selector",
    "pcc_matched",
    "pcc_full"
  ],
  "diagnostic_policies": ["oracle_action_audit_diagnostic"],
  "required_ablations": [
    "county_specific_action_embedding",
    "single_model",
    "no_aleatoric_scale",
    "uncalibrated_ensemble_scale",
    "reward_only",
    "no_executed_feedback",
    "no_reference_fallback",
    "one_policy_improvement_round"
  ],
  "compute_budget": {
    "single_model_candidate_equivalents": 50,
    "matched_ensemble_pool_rule": "floor(50 / ensemble_size)",
    "maximum_excess_candidate_equivalents": 1
  },
  "success_gates": {
    "minimum_jointly_supporting_model_seeds": 2,
    "matched_compute_must_reach_same_conclusion": true,
    "bishan": {
      "reward_lower_bound_strictly_positive": true,
      "planning_lower_bound_minimum": 0.0
    },
    "dongxing": {
      "reward_lower_bound_minimum": 0.0,
      "planning_lower_bound_minimum": 0.0
    },
    "information_audit_requires_zero_unexecuted_real_reward_queries": true
  }
}
```

- [ ] **Step 8: Run Task 1 tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_objectives.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
git add paper10_geojepa_mpc\experiments\pcc_objectives.py paper10_geojepa_mpc\experiments\pcc_protocol_registry.py paper10_geojepa_mpc\experiments\protocols\pcc_v1.json paper10_geojepa_mpc\tests\test_pcc_objectives.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py
git commit -m "feat: lock pcc objectives and protocol"
```

Expected: all Task 1 tests pass; commit contains only the five listed files.

### Task 2: Implement the Action-Relative Multi-Objective Model

**Files:**
- Create: `paper10_geojepa_mpc/models/pcc_geojepa.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_geojepa.py`

- [ ] **Step 1: Write failing permutation and shape tests**

```python
import torch

from paper10_geojepa_mpc.models.pcc_geojepa import (
    PCCGeoJEPAMember,
    summarize_block_neighbours,
)


def _inputs(n_blocks=4):
    torch.manual_seed(4)
    block = torch.randn(2, n_blocks, 17)
    neighbour = torch.randn(2, n_blocks, 17)
    global_features = torch.randn(2, 12)
    actions = torch.tensor([1, 3]) % n_blocks
    return block, neighbour, global_features, actions


def test_outputs_have_multi_horizon_multi_objective_shapes():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12, hidden_dim=16)
    block, neighbour, global_features, actions = _inputs()
    out = model(block, neighbour, global_features, actions)
    assert out.horizon_mean.shape == (2, 3, 4)
    assert out.horizon_log_scale.shape == (2, 3, 4)
    assert out.immediate_mean.shape == (2, 4)
    assert out.executable_logit.shape == (2,)


def test_action_scores_are_equivariant_to_block_permutation():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12, hidden_dim=16).eval()
    block, neighbour, global_features, actions = _inputs()
    permutation = torch.tensor([2, 0, 3, 1])
    inverse = torch.argsort(permutation)
    permuted_actions = inverse[actions]
    original = model(block, neighbour, global_features, actions).horizon_mean
    permuted = model(
        block[:, permutation], neighbour[:, permutation], global_features, permuted_actions
    ).horizon_mean
    torch.testing.assert_close(original, permuted)


def test_neighbour_summary_uses_graph_mean_and_zero_for_isolates():
    block = torch.tensor([[1.0], [3.0], [8.0]])
    adjacency = [torch.tensor([1]), torch.tensor([0, 2]), torch.tensor([], dtype=torch.long)]
    summary = summarize_block_neighbours(block, adjacency)
    torch.testing.assert_close(summary, torch.tensor([[3.0], [4.5], [0.0]]))
```

- [ ] **Step 2: Run model tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_geojepa.py -q
```

Expected: collection fails because `pcc_geojepa` does not exist.

- [ ] **Step 3: Implement typed outputs and the action-relative member**

```python
from typing import NamedTuple
import torch
import torch.nn as nn


class PCCModelOutput(NamedTuple):
    next_block: torch.Tensor
    next_global: torch.Tensor
    immediate_mean: torch.Tensor
    immediate_log_scale: torch.Tensor
    horizon_mean: torch.Tensor
    horizon_log_scale: torch.Tensor
    executable_logit: torch.Tensor
    latent: torch.Tensor


def summarize_block_neighbours(block_features: torch.Tensor, adjacency) -> torch.Tensor:
    rows = []
    for neighbours in adjacency:
        neighbours = torch.as_tensor(neighbours, dtype=torch.long, device=block_features.device)
        if neighbours.numel() == 0:
            rows.append(torch.zeros_like(block_features[0]))
        else:
            rows.append(block_features.index_select(0, neighbours).mean(dim=0))
    return torch.stack(rows)


class PCCGeoJEPAMember(nn.Module):
    def __init__(self, block_feature_dim: int, k_global: int, hidden_dim: int = 32):
        super().__init__()
        self.block_feature_dim = int(block_feature_dim)
        self.k_global = int(k_global)
        self.hidden_dim = int(hidden_dim)
        self.block_encoder = nn.Sequential(
            nn.Linear(block_feature_dim, 64), nn.ReLU(), nn.Linear(64, hidden_dim), nn.ReLU()
        )
        self.neighbour_encoder = nn.Sequential(
            nn.Linear(block_feature_dim, 64), nn.ReLU(), nn.Linear(64, hidden_dim), nn.ReLU()
        )
        self.global_encoder = nn.Sequential(
            nn.Linear(k_global, 64), nn.ReLU(), nn.Linear(64, hidden_dim), nn.ReLU()
        )
        context_dim = hidden_dim * 6
        self.trunk = nn.Sequential(nn.Linear(context_dim, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU())
        self.block_delta_head = nn.Linear(128, block_feature_dim)
        self.global_delta_head = nn.Linear(128, k_global)
        self.immediate_head = nn.Linear(128, 8)
        self.horizon_head = nn.Linear(128, 3 * 4 * 2)
        self.executable_head = nn.Linear(128, 1)

    def forward(self, block, neighbour, global_features, actions):
        encoded = self.block_encoder(block)
        neighbour_encoded = self.neighbour_encoder(neighbour)
        rows = torch.arange(block.shape[0], device=block.device)
        selected = encoded[rows, actions.long()]
        selected_neighbour = neighbour_encoded[rows, actions.long()]
        county_mean = encoded.mean(1)
        context = torch.cat(
            [
                selected,
                selected_neighbour,
                selected - county_mean,
                county_mean,
                encoded.max(1).values,
                self.global_encoder(global_features),
            ],
            dim=-1,
        )
        latent = self.trunk(context)
        next_block = block.clone()
        next_block[rows, actions.long()] = next_block[rows, actions.long()] + self.block_delta_head(latent)
        next_global = global_features + self.global_delta_head(latent)
        immediate = self.immediate_head(latent).view(-1, 2, 4)
        horizon = self.horizon_head(latent).view(-1, 3, 2, 4)
        return PCCModelOutput(
            next_block=next_block,
            next_global=next_global,
            immediate_mean=immediate[:, 0],
            immediate_log_scale=immediate[:, 1].clamp(-8.0, 5.0),
            horizon_mean=horizon[:, :, 0],
            horizon_log_scale=horizon[:, :, 1].clamp(-8.0, 5.0),
            executable_logit=self.executable_head(latent).squeeze(-1),
            latent=latent,
        )
```

- [ ] **Step 4: Add action-space compatibility and checkpoint round-trip tests**

```python
def test_model_has_no_county_specific_action_embedding():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12)
    names = dict(model.named_parameters())
    assert all("action_emb" not in name for name in names)
    for n_blocks in (4, 7):
        block, neighbour, global_features, actions = _inputs(n_blocks)
        assert model(block, neighbour, global_features, actions).horizon_mean.shape == (2, 3, 4)
```

- [ ] **Step 5: Run model tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_geojepa.py -q
git add paper10_geojepa_mpc\models\pcc_geojepa.py paper10_geojepa_mpc\tests\test_pcc_geojepa.py
git commit -m "feat: add action-relative pcc geojepa model"
```

Expected: all model tests pass and the legacy model tests remain unchanged.

### Task 3: Generate Baseline-Continuation Multi-Objective Labels

**Files:**
- Create: `paper10_geojepa_mpc/experiments/pcc_value_labels.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_value_labels.py`

- [ ] **Step 1: Write failing deterministic-label tests**

```python
import numpy as np

from paper10_geojepa_mpc.experiments.pcc_value_labels import evaluate_candidate_objectives


class TinyEnv:
    def __init__(self):
        self.value = 0
        self.step_count = 0
        self.max_steps = 8
    def metrics(self):
        return {"avg_slope": 10.0 - self.value, "contiguity": self.value / 10.0, "baimu_area_ha": 100.0 + self.value}
    def step(self, action):
        self.value += int(action)
        self.step_count += 1
        info = {"avg_slope": 10.0 - self.value, "contiguity": self.value / 10.0, "baimu_area_ha": 100.0 + self.value}
        return None, float(action), False, False, info


def test_candidate_labels_record_horizons_and_restore_environment():
    env = TinyEnv()
    result = evaluate_candidate_objectives(
        env=env,
        candidate_action=2,
        horizons=(1, 3, 5),
        gamma=1.0,
        reference_policy=lambda *_: 1,
        rng=np.random.default_rng(7),
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )
    assert result.shape == (3, 4)
    assert result[:, 0].tolist() == [2.0, 4.0, 6.0]
    assert env.value == 0 and env.step_count == 0


def test_neighbour_features_are_built_from_block_adjacency():
    env = type("Env", (), {"block_adj": [np.array([1]), np.array([0, 2]), np.array([], dtype=int)]})()
    block = np.array([[1.0], [3.0], [8.0]], dtype=np.float32)
    np.testing.assert_allclose(build_neighbour_feature_matrix(env, block), [[3.0], [4.5], [0.0]])
```

- [ ] **Step 2: Run label tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_value_labels.py -q
```

Expected: collection fails because `pcc_value_labels` does not exist.

- [ ] **Step 3: Implement local-horizon candidate and reference outcomes**

```python
import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import oriented_outcome
from paper10_geojepa_mpc.experiments.value_label_generation import restore_env, snapshot_env


def build_neighbour_feature_matrix(env, block_features):
    block_features = np.asarray(block_features, dtype=np.float32)
    rows = []
    for neighbours in env.block_adj:
        neighbours = np.asarray(neighbours, dtype=np.int64)
        rows.append(
            block_features[neighbours].mean(axis=0)
            if neighbours.size
            else np.zeros(block_features.shape[1], dtype=np.float32)
        )
    return np.stack(rows).astype(np.float32)


def evaluate_candidate_objectives(
    *, env, candidate_action, horizons, gamma, reference_policy, rng, metric_reader, state_attrs
):
    horizons = tuple(sorted(int(value) for value in horizons))
    snapshot = snapshot_env(env, state_attrs=state_attrs)
    start = metric_reader(env)
    rewards: list[float] = []
    outputs: list[np.ndarray] = []
    try:
        for step in range(1, max(horizons) + 1):
            action = int(candidate_action) if step == 1 else int(reference_policy(env, rng))
            _, reward, terminated, truncated, _ = env.step(action)
            rewards.append(float(reward))
            if step in horizons:
                discounted = sum((float(gamma) ** index) * value for index, value in enumerate(rewards))
                outputs.append(oriented_outcome(discounted, start, metric_reader(env)))
            if terminated or truncated:
                while len(outputs) < len(horizons):
                    outputs.append(oriented_outcome(discounted, start, metric_reader(env)))
                break
    finally:
        restore_env(env, snapshot)
    return np.stack(outputs).astype(np.float32)
```

- [ ] **Step 4: Add the dataset schema and CLI**

The CLI must write one compressed NPZ per trajectory seed with these exact arrays:

```python
dataset = {
    "states_bf": np.stack(states_bf).astype(np.float32),
    "states_neighbor_bf": np.stack(states_neighbor_bf).astype(np.float32),
    "states_gf": np.stack(states_gf).astype(np.float32),
    "actions": np.stack(actions).astype(np.int64),
    "objective_returns": np.stack(objective_returns).astype(np.float32),
    "reference_actions": np.asarray(reference_actions, dtype=np.int64),
    "reference_objective_returns": np.stack(reference_returns).astype(np.float32),
    "executable_targets": np.stack(executable_targets).astype(np.float32),
    "trajectory_ids": np.full(len(states_bf), trajectory_seed, dtype=np.int64),
    "state_steps": np.asarray(state_steps, dtype=np.int64),
    "horizons": np.asarray(horizons, dtype=np.int64),
}
```

Add assertions that every candidate/reference pair uses the same state snapshot and a continuation RNG derived from `(trajectory_seed, state_step, candidate_action)`.

- [ ] **Step 5: Run label tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_value_labels.py paper10_geojepa_mpc\tests\test_value_label_generation.py -q
git add paper10_geojepa_mpc\experiments\pcc_value_labels.py paper10_geojepa_mpc\tests\test_pcc_value_labels.py
git commit -m "feat: generate pcc multi-objective labels"
```

Expected: PCC and legacy label-generation tests pass.

### Task 4: Train Bootstrap Ensemble Members and PCC Checkpoints

**Files:**
- Create: `paper10_geojepa_mpc/training/pcc_training.py`
- Create: `paper10_geojepa_mpc/experiments/run_pcc_train.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_training.py`

- [ ] **Step 1: Write failing bootstrap and loss tests**

```python
import numpy as np
import torch

from paper10_geojepa_mpc.training.pcc_training import (
    bootstrap_trajectory_ids,
    heteroscedastic_objective_loss,
)


def test_bootstrap_samples_complete_trajectories_reproducibly():
    first = bootstrap_trajectory_ids(np.array([1000, 1001, 1002]), seed=5101)
    second = bootstrap_trajectory_ids(np.array([1000, 1001, 1002]), seed=5101)
    assert first.tolist() == second.tolist()
    assert len(first) == 3


def test_objective_loss_rewards_accurate_mean_and_finite_scale():
    target = torch.zeros(2, 3, 4)
    exact = heteroscedastic_objective_loss(target, torch.zeros_like(target), torch.zeros_like(target))
    wrong = heteroscedastic_objective_loss(target, torch.ones_like(target), torch.zeros_like(target))
    assert torch.isfinite(exact)
    assert exact < wrong
```

- [ ] **Step 2: Run training tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_training.py -q
```

Expected: collection fails because `pcc_training` does not exist.

- [ ] **Step 3: Implement trajectory bootstrap and normalized losses**

```python
import numpy as np
import torch


def bootstrap_trajectory_ids(unique_ids: np.ndarray, seed: int) -> np.ndarray:
    ids = np.asarray(unique_ids, dtype=np.int64)
    return np.random.default_rng(seed).choice(ids, size=len(ids), replace=True)


def heteroscedastic_objective_loss(target, mean, log_scale):
    log_scale = log_scale.clamp(-8.0, 5.0)
    inverse_variance = torch.exp(-2.0 * log_scale)
    return (0.5 * (target - mean).square() * inverse_variance + log_scale).mean()


def pairwise_delta_ranking_loss(candidate_mean, reference_mean, target_delta, margin=0.05):
    signed = torch.sign(target_delta)
    active = signed.ne(0)
    if not active.any():
        return (candidate_mean - reference_mean).sum() * 0.0
    predicted = candidate_mean - reference_mean
    return torch.relu(float(margin) - signed[active] * predicted[active]).mean()
```

The complete trainer uses the declared weighted sum:

```python
total_loss = (
    transition_huber
    + objective_nll
    + 0.25 * immediate_objective_nll
    + 0.20 * pairwise_rank_loss
    + 0.10 * executable_bce
    + 0.01 * representation_regularizer
)
```

Target scales are median absolute deviations computed from training trajectories
only and stored under `checkpoint["objective_scaling"]`.

- [ ] **Step 4: Implement checkpoint schema and ensemble CLI**

Each member checkpoint must contain:

```python
payload = {
    "model_class": "PCCGeoJEPAMember",
    "model_kwargs": model_kwargs,
    "state_dict": {key: value.detach().cpu() for key, value in model.state_dict().items()},
    "model_seed": int(model_seed),
    "bootstrap_trajectory_ids": [int(value) for value in bootstrap_ids],
    "objective_names": list(OBJECTIVE_NAMES),
    "horizons": [1, 3, 5],
    "objective_scaling": scaling,
    "protocol_id": registry["protocol_id"],
    "registry_digest": registry.get("frozen_digest"),
}
```

`run_pcc_train.py` accepts `--labels-manifest`, `--model-seed`, `--ensemble-size`,
`--epochs`, `--device`, `--init-checkpoint-root`,
`--trainable-scope {all,objective_heads}`, and `--output-dir`. It refuses
confirmation-labelled inputs. `objective_heads` freezes the block, neighbour,
global, trunk, and executable heads and trains only the immediate and multi-horizon
objective heads. This is the only trainable scope permitted for Dongxing
adaptation.

- [ ] **Step 5: Add a tiny end-to-end checkpoint test, run, and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_training.py paper10_geojepa_mpc\tests\test_pcc_geojepa.py -q
git add paper10_geojepa_mpc\training\pcc_training.py paper10_geojepa_mpc\experiments\run_pcc_train.py paper10_geojepa_mpc\tests\test_pcc_training.py
git commit -m "feat: train pcc bootstrap ensemble"
```

Expected: tiny fixture trains one epoch, reloads the checkpoint, and reproduces its outputs.

### Task 5: Implement Exactly Two Offline Conservative Policy-Improvement Rounds

**Files:**
- Create: `paper10_geojepa_mpc/experiments/run_pcc_policy_iteration.py`
- Modify: `paper10_geojepa_mpc/training/pcc_training.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_policy_iteration.py`

- [ ] **Step 1: Write failing round-boundary and lineage tests**

```python
import pytest

from paper10_geojepa_mpc.experiments.run_pcc_policy_iteration import (
    PolicyRound,
    build_policy_rounds,
)


def test_policy_iteration_has_exactly_two_improvement_rounds():
    rounds = build_policy_rounds(reference_policy="paper9_mpc")
    assert [row.round_index for row in rounds] == [0, 1, 2]
    assert rounds[0].label_policy == "paper9_mpc"
    assert rounds[1].label_policy == "pcc_round1"
    assert rounds[2].label_policy == "pcc_round2"


def test_third_improvement_round_is_forbidden():
    with pytest.raises(ValueError, match="exactly two"):
        PolicyRound(round_index=3, label_policy="pcc_round3", parent_digest="abc")
```

- [ ] **Step 2: Run the policy-iteration tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_policy_iteration.py -q
```

Expected: collection fails because `run_pcc_policy_iteration` does not exist.

- [ ] **Step 3: Implement immutable round lineage**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyRound:
    round_index: int
    label_policy: str
    parent_digest: str | None

    def __post_init__(self):
        if self.round_index not in {0, 1, 2}:
            raise ValueError("PCC uses exactly two policy-improvement rounds")


def build_policy_rounds(reference_policy: str) -> tuple[PolicyRound, ...]:
    return (
        PolicyRound(0, reference_policy, None),
        PolicyRound(1, "pcc_round1", "resolved_after_round0"),
        PolicyRound(2, "pcc_round2", "resolved_after_round1"),
    )
```

The runner receives the round-0 training/calibration label manifests and already
trained round-1 checkpoint root from Task 4. It first fits round-1 calibrators from
the round-0 calibration labels. The policy used to generate round-2 labels is
predeclared and fixed as ensemble size 3, joint coverage 0.90, tolerance scale
0.05, horizon 3, no executed-feedback update during offline labeling, and
reference fallback to Paper9 MPC. The runner then uses that frozen `pcc_round1`
policy to generate new training labels on seeds 1000-1007 and new calibration
labels on seeds 2000-2019, trains `pcc_round2`, and fits round-2 calibrators only
from the new round-2 calibration labels. Each manifest contains continuation
policy configuration, parent policy, parent digest, label manifest digest,
checkpoint digests, calibration-label digest, and round index. It raises before
work begins when `--rounds` is not exactly `2`.

- [ ] **Step 4: Add a tiny two-round orchestration test**

Use fixture callbacks for label generation, training, and calibration. Assert this
exact call order and no extra call:

```python
assert calls == [
    ("validate", 1, "round0_labels"),
    ("calibrate", 1, "round0_calibration_labels"),
    ("train_labels", 2, "pcc_round1"),
    ("calibration_labels", 2, "pcc_round1"),
    ("train", 2),
    ("calibrate", 2),
]
```

- [ ] **Step 5: Run policy-iteration and training tests; commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_policy_iteration.py paper10_geojepa_mpc\tests\test_pcc_training.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_policy_iteration.py paper10_geojepa_mpc\training\pcc_training.py paper10_geojepa_mpc\tests\test_pcc_policy_iteration.py
git commit -m "feat: add bounded pcc policy iteration"
```

Expected: exactly two improvement rounds execute and every artifact has an immutable parent lineage.

### Task 6: Implement Trajectory-Level Paired Joint Conformal Calibration

**Files:**
- Create: `paper10_geojepa_mpc/planning/paired_conformal.py`
- Test: `paper10_geojepa_mpc/tests/test_paired_conformal.py`

- [ ] **Step 1: Write failing hand-computed calibration tests**

```python
import numpy as np

from paper10_geojepa_mpc.planning.paired_conformal import fit_joint_calibrator


def test_joint_score_uses_maximum_across_rows_and_objectives_per_trajectory():
    target = np.zeros((4, 2, 4))
    predicted = np.zeros_like(target)
    scale = np.ones_like(target)
    target[1, 1, 3] = 2.0
    trajectory = np.array([10, 10, 11, 11])
    calibrator = fit_joint_calibrator(target, predicted, scale, trajectory, coverage=0.5)
    assert calibrator.trajectory_scores.tolist() == [2.0, 0.0]
    assert calibrator.q_joint == 2.0


def test_lower_bounds_share_one_joint_multiplier():
    target = np.zeros((3, 1, 4))
    calibrator = fit_joint_calibrator(target, target, np.ones_like(target), np.arange(3), coverage=0.8)
    lower = calibrator.lower_bounds(np.ones(4), np.full(4, 0.5))
    np.testing.assert_allclose(lower, np.ones(4) - calibrator.q_joint * 0.5)
```

- [ ] **Step 2: Run conformal tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_paired_conformal.py -q
```

Expected: collection fails because `paired_conformal` does not exist.

- [ ] **Step 3: Implement the finite-sample joint calibrator**

```python
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class JointPairedCalibrator:
    coverage: float
    q_joint: float
    trajectory_scores: np.ndarray
    objective_names: tuple[str, ...]

    def lower_bounds(self, mean_delta, scale, online_multiplier=1.0):
        return np.asarray(mean_delta) - self.q_joint * np.asarray(scale) * np.asarray(online_multiplier)


def fit_joint_calibrator(target_delta, predicted_delta, scale, trajectory_ids, coverage, objective_names=("reward", "slope_benefit", "contiguity_benefit", "connected_area_benefit")):
    if not 0.0 < float(coverage) < 1.0:
        raise ValueError("coverage must be in (0, 1)")
    normalized = np.abs(np.asarray(target_delta) - np.asarray(predicted_delta)) / np.maximum(np.asarray(scale), 1e-8)
    ids = np.asarray(trajectory_ids)
    scores = np.asarray([normalized[ids == value].max() for value in np.unique(ids)], dtype=np.float64)
    rank = min(len(scores), math.ceil((len(scores) + 1) * float(coverage)))
    q_joint = float(np.partition(scores, rank - 1)[rank - 1])
    return JointPairedCalibrator(float(coverage), q_joint, scores, tuple(objective_names))
```

- [ ] **Step 4: Add serialization, coverage audit, tests, and commit**

Serialization stores `coverage`, `q_joint`, `trajectory_scores`, objective order,
protocol ID, calibration seed list, and SHA-256 digest. The coverage audit computes
the fraction of held-out trajectories for which every row and objective is covered.

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_paired_conformal.py -q
git add paper10_geojepa_mpc\planning\paired_conformal.py paper10_geojepa_mpc\tests\test_paired_conformal.py
git commit -m "feat: add paired joint conformal calibration"
```

Expected: all conformal tests pass, including malformed-shape and coverage-boundary cases.

### Task 7: Implement Executed-Outcome-Only Residual Scaling

**Files:**
- Create: `paper10_geojepa_mpc/planning/executed_feedback.py`
- Test: `paper10_geojepa_mpc/tests/test_executed_feedback.py`

- [ ] **Step 1: Write failing bounded-update tests**

```python
import numpy as np

from paper10_geojepa_mpc.planning.executed_feedback import ExecutedFeedbackScaler


def test_scaler_never_shrinks_offline_intervals():
    scaler = ExecutedFeedbackScaler(window=3, q_joint=2.0)
    scaler.update(np.zeros(4), np.ones(4), np.full(4, 0.5))
    assert np.all(scaler.multiplier() >= 1.0)


def test_scaler_widens_and_clips_after_large_executed_error():
    scaler = ExecutedFeedbackScaler(window=2, q_joint=1.0)
    scaler.update(np.full(4, 100.0), np.zeros(4), np.ones(4))
    assert scaler.multiplier().tolist() == [3.0, 3.0, 3.0, 3.0]
```

- [ ] **Step 2: Run feedback tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_executed_feedback.py -q
```

Expected: collection fails because `executed_feedback` does not exist.

- [ ] **Step 3: Implement the bounded scaler**

```python
from collections import deque
import numpy as np


class ExecutedFeedbackScaler:
    def __init__(self, window: int, q_joint: float):
        if int(window) <= 0 or float(q_joint) < 0.0:
            raise ValueError("window must be positive and q_joint non-negative")
        self.window = int(window)
        self.q_joint = max(float(q_joint), 1e-8)
        self._ratios = deque(maxlen=self.window)

    def update(self, observed, predicted, base_scale) -> None:
        ratio = np.abs(np.asarray(observed) - np.asarray(predicted)) / np.maximum(np.asarray(base_scale), 1e-8)
        if not np.isfinite(ratio).all():
            raise ValueError("executed residuals must be finite")
        self._ratios.append(ratio.astype(np.float64))

    def multiplier(self) -> np.ndarray:
        if not self._ratios:
            return np.ones(4, dtype=np.float64)
        empirical = np.quantile(np.stack(self._ratios), 0.9, axis=0)
        return np.clip(empirical / self.q_joint, 1.0, 3.0)
```

- [ ] **Step 4: Run tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_executed_feedback.py -q
git add paper10_geojepa_mpc\planning\executed_feedback.py paper10_geojepa_mpc\tests\test_executed_feedback.py
git commit -m "feat: calibrate pcc from executed outcomes"
```

Expected: multiplier begins at one, never narrows, clips at three, and rejects non-finite updates.

### Task 8: Implement Conservative Pareto Selection and Fail-Closed Fallback

**Files:**
- Create: `paper10_geojepa_mpc/planning/pcc_selector.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_selector.py`

- [ ] **Step 1: Write failing Pareto and fallback tests**

```python
import numpy as np

from paper10_geojepa_mpc.planning.pcc_selector import choose_from_bounds


def test_reward_positive_planning_harmful_action_is_rejected():
    actions = np.array([4, 7])
    lower = np.array([[2.0, -0.1, 0.2, 1.0], [1.0, 0.1, 0.1, 0.1]])
    chosen, info = choose_from_bounds(actions, lower, np.ones(2), np.array([0.2, 0.1]), reference_action=9, tolerances=np.zeros(3))
    assert chosen == 7
    assert info["admissible_actions"] == [7]


def test_no_admissible_action_falls_back_exactly_to_reference():
    chosen, info = choose_from_bounds(
        np.array([4]), np.array([[-1.0, 1.0, 1.0, 1.0]]), np.ones(1), np.array([0.2]), reference_action=9, tolerances=np.zeros(3)
    )
    assert chosen == 9
    assert info["fallback"] is True
```

- [ ] **Step 2: Run selector tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_selector.py -q
```

Expected: collection fails because `pcc_selector` does not exist.

- [ ] **Step 3: Implement deterministic Pareto choice**

```python
import numpy as np


def choose_from_bounds(actions, lower_bounds, executable_probability, uncertainty, reference_action, tolerances, executable_threshold=0.95):
    actions = np.asarray(actions, dtype=np.int64)
    lower = np.asarray(lower_bounds, dtype=np.float64)
    tolerances = np.asarray(tolerances, dtype=np.float64)
    admissible = (np.asarray(executable_probability) >= float(executable_threshold)) & (lower[:, 0] > 0.0)
    admissible &= np.all(lower[:, 1:] >= -tolerances[None, :], axis=1)
    indexes = np.flatnonzero(admissible)
    if indexes.size == 0:
        return int(reference_action), {"fallback": True, "admissible_actions": []}
    order = sorted(
        indexes.tolist(),
        key=lambda idx: (
            -lower[idx, 0],
            -float(lower[idx, 1:].min()),
            float(np.asarray(uncertainty)[idx]),
            int(actions[idx]),
        ),
    )
    selected = order[0]
    return int(actions[selected]), {
        "fallback": False,
        "admissible_actions": [int(actions[idx]) for idx in indexes],
        "selected_lower_bounds": lower[selected].tolist(),
    }
```

- [ ] **Step 4: Add ensemble prediction and candidate-proposal integration**

`pcc_select_action(...)` accepts a frozen reference-policy callable, ensemble,
calibrator, feedback scaler, observable arrays, executable mask, neighbour features,
candidate budget, and compute counter. Candidate proposals are the deduplicated
union of the reference action, scout reward top actions, scout conservative top
actions, and distributional baseline top actions. The ensemble is evaluated only
on that pool. `member_evaluations <= candidate_budget` is asserted for the
matched-compute configuration.

For member `k`, candidate `a`, and reference `b`, compute paired member deltas
`delta_k = mean_k(a) - mean_k(b)`. The calibrator receives:

```python
paired_mean = member_deltas.mean(axis=0)
epistemic_variance = member_deltas.var(axis=0, ddof=1)
aleatoric_variance = np.mean(
    np.exp(2.0 * candidate_log_scales)
    + np.exp(2.0 * reference_log_scales),
    axis=0,
)
paired_scale = np.sqrt(
    np.maximum(epistemic_variance + aleatoric_variance, 1e-12)
)
uncertainty_rank = paired_scale.max(axis=-1)
```

Executable probability is the mean sigmoid probability across members. The
conservative lower bound uses `paired_mean`, `paired_scale`, the joint conformal
multiplier, and the executed-feedback multiplier.

- [ ] **Step 5: Add non-finite fail-closed and deterministic-tie tests**

The tests must assert that non-finite means, scales, probabilities, or bounds return
the reference action with `fallback_reason` and never choose an action by array order.

- [ ] **Step 6: Run selector tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_selector.py -q
git add paper10_geojepa_mpc\planning\pcc_selector.py paper10_geojepa_mpc\tests\test_pcc_selector.py
git commit -m "feat: add conservative pareto pcc selector"
```

Expected: harmful actions are rejected, jointly positive actions are accepted, and every invalid state fails closed.

## Phase II: Safe Runners, Baselines, and Statistics

### Task 9: Build the No-Oracle Rollout Runner and Information-Set Audit

**Files:**
- Create: `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`
- Create: `paper10_geojepa_mpc/experiments/pcc_information_set_audit.py`
- Test: `paper10_geojepa_mpc/tests/test_run_pcc_rollouts.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_information_set_audit.py`
- Modify: `paper10_geojepa_mpc/experiments/rollout_summary.py`

- [ ] **Step 1: Write a spy-environment test that forbids counterfactual access**

```python
class SpyEnv:
    def __init__(self):
        self.step_calls = []
    def step(self, action):
        self.step_calls.append(int(action))
        return None, 1.0, False, False, {
            "avg_slope": 9.0, "contiguity": 0.2, "baimu_area_ha": 100.0,
            "slope_change_pct": -1.0, "cont_change": 0.0, "baimu_area_change_ha": 0.0,
        }


def test_selection_never_steps_or_snapshots_real_environment(monkeypatch):
    env = SpyEnv()
    action = select_without_execution(env=env, selector=lambda **_: (3, {}))
    assert action == 3
    assert env.step_calls == []
```

- [ ] **Step 2: Run runner tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_information_set_audit.py -q
```

Expected: collection fails because the PCC runner and audit do not exist.

- [ ] **Step 3: Implement strict separation between selection and execution**

```python
def select_without_execution(*, env, selector, **selector_kwargs):
    forbidden_before = int(getattr(env, "step_count", 0))
    action, info = selector(**selector_kwargs)
    forbidden_after = int(getattr(env, "step_count", 0))
    if forbidden_before != forbidden_after:
        raise RuntimeError("selector mutated the real environment")
    return int(action), info
```

The runner calls `env.step(action)` exactly once after selection, then passes only
the executed action's predicted mean/scale and observed outcome to
`ExecutedFeedbackScaler.update`.

- [ ] **Step 4: Add resumable artifact and compute accounting schema**

Each step record extends the legacy rollout record with:

```python
record.update({
    "reference_action": int(info["reference_action"]),
    "fallback": bool(info["fallback"]),
    "fallback_reason": info.get("fallback_reason"),
    "selected_lower_bounds": info.get("selected_lower_bounds"),
    "joint_q": float(info["joint_q"]),
    "online_multiplier": list(info["online_multiplier"]),
    "member_evaluations": int(info["member_evaluations"]),
    "model_forward_count": int(info["model_forward_count"]),
    "unexecuted_real_reward_queries": 0,
})
```

Partial output is written atomically through a temporary sibling file and renamed
after each completed seed. Resume skips a seed only when its registry digest and
checkpoint digests match.

- [ ] **Step 5: Implement and test the information-set audit**

The audit fails if any step has nonzero `unexecuted_real_reward_queries`, if the
environment step count differs from the number of recorded actions, or if a
confirmation artifact lacks the frozen registry digest.

- [ ] **Step 6: Run runner, legacy summary, and audit tests; commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_information_set_audit.py paper10_geojepa_mpc\tests\test_rollout_summary.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_rollouts.py paper10_geojepa_mpc\experiments\pcc_information_set_audit.py paper10_geojepa_mpc\experiments\rollout_summary.py paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_information_set_audit.py
git commit -m "feat: run and audit no-oracle pcc rollouts"
```

Expected: the spy test observes no selection-time environment mutation and legacy rollout tests stay green.

### Task 10: Add Matched No-Oracle Baselines and Compute Budgets

**Files:**
- Modify: `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`
- Create: `paper10_geojepa_mpc/planning/pcc_baselines.py`
- Test: `paper10_geojepa_mpc/tests/test_run_pcc_rollouts.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_selector.py`

- [ ] **Step 1: Add failing parameterized baseline tests**

```python
import pytest

@pytest.mark.parametrize("name", [
    "executable_random", "paper9_mpc", "legacy_value_filter", "model_reward_greedy",
    "rank_only", "distributional_risk", "online_expert_selector", "pcc_matched", "pcc_full",
])
def test_every_no_oracle_baseline_builds_without_real_reward_access(name, baseline_context):
    policy = build_baseline(name, baseline_context)
    action, info = policy.select(baseline_context.observable_state)
    assert isinstance(action, int)
    assert info["unexecuted_real_reward_queries"] == 0
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py -q
```

Expected: fails because `build_baseline` does not exist.

- [ ] **Step 3: Implement a common policy interface and frozen expert selector**

```python
from typing import Protocol

class ObservablePolicy(Protocol):
    def select(self, state: dict) -> tuple[int, dict]: ...
    def observe(self, transition: dict) -> None: ...
```

The expert selector uses exponential weights updated only from the reward of the
executed expert. It cannot score counterfactual expert rewards. Its learning rate
is fixed in development and stored in the frozen registry.

- [ ] **Step 4: Enforce matched compute**

For PCC with ensemble size `K`, set:

```python
matched_pool_size = max(1, 50 // K)
assert K * matched_pool_size <= 50
```

All policies log candidate count, member evaluations, model forward count,
wall-clock selection time, and peak resident memory. The oracle diagnostic uses a
separate CLI flag and cannot be selected as a primary comparator.

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_selector.py -q
git add paper10_geojepa_mpc\planning\pcc_baselines.py paper10_geojepa_mpc\experiments\run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_selector.py
git commit -m "feat: add matched pcc baseline suite"
```

Expected: every baseline passes the no-oracle audit and matched compute rejects excessive ensemble evaluation.

### Task 11: Implement Hierarchical Confirmation Statistics and Locked Gates

**Files:**
- Create: `paper10_geojepa_mpc/experiments/pcc_confirmatory_statistics.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_confirmatory_statistics.py`

- [ ] **Step 1: Write failing paired-bootstrap and all-gates tests**

```python
import numpy as np

from paper10_geojepa_mpc.experiments.pcc_confirmatory_statistics import evaluate_success


def test_reward_gain_cannot_pass_when_one_planning_gate_fails():
    differences = np.ones((3, 20, 4), dtype=float)
    differences[:, :, 3] = -1.0
    report = evaluate_success(differences, bootstrap_seed=20260710, draws=2000)
    assert report["reward_superiority"] is True
    assert report["planning_noninferiority"]["connected_area_benefit"] is False
    assert report["primary_success"] is False


def test_pairing_is_preserved_within_training_seed():
    differences = np.zeros((3, 20, 4), dtype=float)
    differences[:, :, 0] = np.arange(20)
    report = evaluate_success(differences, bootstrap_seed=4, draws=100)
    assert report["n_training_seeds"] == 3
    assert report["n_rollout_seeds"] == 20
```

- [ ] **Step 2: Run statistics tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py -q
```

Expected: collection fails because the statistics module does not exist.

- [ ] **Step 3: Implement hierarchical paired bootstrap**

```python
import numpy as np


def hierarchical_bootstrap(differences, draws, seed):
    values = np.asarray(differences, dtype=np.float64)
    rng = np.random.default_rng(seed)
    sampled = np.empty((int(draws), values.shape[-1]), dtype=np.float64)
    for draw in range(int(draws)):
        train_indexes = rng.integers(0, values.shape[0], size=values.shape[0])
        blocks = []
        for train_index in train_indexes:
            rollout_indexes = rng.integers(0, values.shape[1], size=values.shape[1])
            blocks.append(values[train_index, rollout_indexes])
        sampled[draw] = np.concatenate(blocks, axis=0).mean(axis=0)
    return sampled


def evaluate_success(differences, bootstrap_seed=20260710, draws=20000):
    values = np.asarray(differences, dtype=np.float64)
    bootstrap = hierarchical_bootstrap(values, draws, bootstrap_seed)
    lower = np.quantile(bootstrap, 0.05, axis=0)
    names = ("reward", "slope_benefit", "contiguity_benefit", "connected_area_benefit")
    rng = np.random.default_rng(bootstrap_seed + 1)
    per_training_lower = []
    for training_index in range(values.shape[0]):
        sampled = np.empty((int(draws), values.shape[-1]), dtype=np.float64)
        for draw in range(int(draws)):
            rollout_indexes = rng.integers(0, values.shape[1], size=values.shape[1])
            sampled[draw] = values[training_index, rollout_indexes].mean(axis=0)
        per_training_lower.append(np.quantile(sampled, 0.05, axis=0))
    per_training_lower = np.stack(per_training_lower)
    support_by_training = (per_training_lower[:, 0] > 0.0) & np.all(per_training_lower[:, 1:] >= 0.0, axis=1)
    planning = {name: bool(lower[index] >= 0.0) for index, name in enumerate(names[1:], 1)}
    return {
        "n_training_seeds": int(values.shape[0]),
        "n_rollout_seeds": int(values.shape[1]),
        "lower_95_one_sided": dict(zip(names, lower.tolist())),
        "reward_superiority": bool(lower[0] > 0.0),
        "planning_noninferiority": planning,
        "per_training_seed_lower_95_one_sided": per_training_lower.tolist(),
        "training_seed_joint_support": int(support_by_training.sum()),
        "primary_success": bool(lower[0] > 0.0 and all(planning.values()) and support_by_training.sum() >= 2),
    }
```

- [ ] **Step 4: Add artifact loading, Holm-adjusted secondary comparisons, and Dongxing gates**

The CLI requires complete `3 x 20` Bishan blocks and complete declared Dongxing
blocks, verifies policy/checkpoint/registry digests, identifies the already frozen
primary comparator, and writes JSON, Markdown, and seed-level CSV. Incomplete or
duplicate blocks raise an error instead of being silently dropped.

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py -q
git add paper10_geojepa_mpc\experiments\pcc_confirmatory_statistics.py paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py
git commit -m "feat: add locked pcc confirmation statistics"
```

Expected: a reward-only win fails the overall gate, pairing is preserved, and incomplete blocks fail closed.

## Phase III: Development, Freeze, and Independent Confirmation

### Task 12: Build the Bounded Development Orchestrator

**Files:**
- Create: `paper10_geojepa_mpc/experiments/run_pcc_development.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_development.py`

- [ ] **Step 1: Write failing grid and lexicographic-selection tests**

```python
from paper10_geojepa_mpc.experiments.run_pcc_development import enumerate_grid, select_configuration


def test_grid_contains_only_registry_declared_values(registry):
    rows = enumerate_grid(registry["grid"])
    assert len(rows) == 144
    assert {row["ensemble_size"] for row in rows} == {3, 5}


def test_selection_prioritizes_planning_gates_then_reward_then_compute():
    rows = [
        {"id": "reward_only", "planning_gate_count": 2, "reward": 5.0, "compute": 10},
        {"id": "safe_slow", "planning_gate_count": 3, "reward": 1.0, "compute": 20},
        {"id": "safe_fast", "planning_gate_count": 3, "reward": 1.0, "compute": 10},
    ]
    assert select_configuration(rows)["id"] == "safe_fast"
```

- [ ] **Step 2: Run development tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_development.py -q
```

Expected: collection fails because `run_pcc_development` does not exist.

- [ ] **Step 3: Implement deterministic grid enumeration and selection**

```python
from itertools import product


def enumerate_grid(grid):
    keys = tuple(grid)
    return [dict(zip(keys, values)) for values in product(*(grid[key] for key in keys))]


def select_configuration(rows):
    if not rows:
        raise ValueError("development rows are empty")
    return sorted(rows, key=lambda row: (-row["planning_gate_count"], -row["reward"], row["compute"], row["id"]))[0]
```

The orchestrator implements successive halving on development seeds only:

- all 144 configurations: seeds 3000-3001, 20 steps;
- top 36: seeds 3000-3004, 50 steps;
- top 8: seeds 3000-3009, 100 steps;
- final winner: all three model seeds on seeds 3000-3009.

Ranking at every rung uses the same lexicographic rule. Intermediate output never
touches the confirmation namespace.

- [ ] **Step 4: Add freeze command and primary-comparator declaration**

`--freeze` writes the selected PCC config, selected strongest no-oracle comparator,
all checkpoint/calibrator digests, expert-selector learning rate, and compute budget
into the registry through `freeze_registry`. It refuses to freeze unless the Stage A
uncertainty-error correlation is positive and calibration coverage lies inside the
exact binomial 95% interval for the declared nominal coverage.

- [ ] **Step 5: Run tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_development.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_development.py paper10_geojepa_mpc\tests\test_pcc_development.py
git commit -m "feat: orchestrate and freeze pcc development"
```

Expected: grid size and lexicographic ordering are deterministic and freeze cannot inspect confirmation files.

### Task 13: Run Stage A, Generate Offline Data, Train, Calibrate, and Freeze

**Files:**
- Generate under ignored local root: `paper10_runs/pcc_v1/`
- Track summaries under: `paper10_geojepa_mpc/experiments/results/pcc_v1/`
- Modify only if Stage A reveals implementation defects: PCC modules and their tests

- [ ] **Step 1: Run the focused unit suite before scientific work**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -k "pcc or paired_conformal or executed_feedback"
```

Expected: all focused tests pass.

- [ ] **Step 2: Run a three-step real-data information-set smoke**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_rollouts --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --mode smoke --env-source paper9 --seeds 3000 --rollout-steps 3 --output paper10_runs\pcc_v1\smoke\bishan_seed3000.json
```

Expected: three recorded actions, three environment steps, zero unexecuted real-reward queries, finite bounds, and a recorded fallback decision for every step.

- [ ] **Step 3: Generate Bishan training labels**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_value_labels --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --partition train --seeds 1000-1007 --env-source paper9 --prepared-dir D:\test --states-per-trajectory 20 --candidate-actions 8 --horizons 1,3,5 --gamma 0.99 --output-dir paper10_runs\pcc_v1\labels\bishan_train
```

Expected: eight seed-specific NPZ files and a manifest whose trajectory IDs are exactly 1000-1007.

- [ ] **Step 4: Generate Bishan calibration labels**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_value_labels --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --partition calibration --seeds 2000-2019 --env-source paper9 --prepared-dir D:\test --states-per-trajectory 10 --candidate-actions 8 --horizons 1,3,5 --gamma 0.99 --output-dir paper10_runs\pcc_v1\labels\bishan_calibration
```

Expected: 20 seed-specific NPZ files with IDs 2000-2019 and no overlap with training.

- [ ] **Step 5: Train the declared model seeds and ensemble sizes**

```powershell
$modelSeeds = 5101,5102,5103
$ensembleSizes = 3,5
foreach ($modelSeed in $modelSeeds) {
  foreach ($ensembleSize in $ensembleSizes) {
    D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_train --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --labels-manifest paper10_runs\pcc_v1\labels\bishan_train\manifest.json --model-seed $modelSeed --ensemble-size $ensembleSize --epochs 20 --device cpu --output-dir "paper10_runs\pcc_v1\checkpoints\seed${modelSeed}_k${ensembleSize}"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
}
```

Expected: 24 member checkpoints total, each with distinct bootstrap membership and the correct model seed.

- [ ] **Step 6: Run exactly two offline policy-improvement rounds**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_policy_iteration --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --round0-train-labels paper10_runs\pcc_v1\labels\bishan_train\manifest.json --round0-calibration-labels paper10_runs\pcc_v1\labels\bishan_calibration\manifest.json --round1-checkpoints paper10_runs\pcc_v1\checkpoints --round1-iteration-ensemble-size 3 --round1-iteration-coverage 0.90 --round1-iteration-tolerance-scale 0.05 --round1-iteration-horizon 3 --rounds 2 --output-dir paper10_runs\pcc_v1\policy_iteration
```

Expected: manifests exist for rounds 1 and 2, each names its parent policy and
digest, and no round 3 artifact exists. All later development commands use the
round-1/round-2 manifests as declared `policy_round` choices.

- [ ] **Step 7: Verify round-specific calibration coverage artifacts**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_policy_iteration --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --verify-only --input-root paper10_runs\pcc_v1\policy_iteration
```

Expected: every round/ensemble-size/coverage calibration JSON records exactly 20
independent trajectory scores, a finite joint multiplier, and a calibration-label
digest matching the same round's continuation policy.

- [ ] **Step 8: Run bounded development and freeze**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_development --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --checkpoint-root paper10_runs\pcc_v1\policy_iteration --calibration-root paper10_runs\pcc_v1\policy_iteration --output-dir paper10_runs\pcc_v1\development --freeze
```

Expected: registry changes from `development` to `frozen`, records one PCC configuration and one strongest no-oracle primary comparator, and writes a stable SHA-256 digest.

- [ ] **Step 9: Audit, summarize, and commit the freeze**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_information_set_audit --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --input-root paper10_runs\pcc_v1\development --output-json paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.json --output-md paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.md
git add paper10_geojepa_mpc\experiments\protocols\pcc_v1.json paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.json paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.md
git commit -m "exp: freeze pcc v1 development protocol"
```

Expected: audit passes and the commit predates every confirmation artifact.

### Task 14: Run Independent Bishan and Dongxing Confirmation

**Files:**
- Generate under ignored local root: `paper10_runs/pcc_v1/confirmation/`
- Track frozen summaries under: `paper10_geojepa_mpc/experiments/results/pcc_v1/`

- [ ] **Step 1: Verify the frozen registry from a clean process**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_protocol_registry --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --verify-frozen
```

Expected: prints the frozen digest and exits zero.

- [ ] **Step 2: Run all frozen Bishan no-oracle policies on seeds 4000-4019**

```powershell
$policies = 'executable_random','paper9_mpc','legacy_value_filter','model_reward_greedy','rank_only','distributional_risk','online_expert_selector','pcc_matched','pcc_full'
foreach ($policy in $policies) {
  D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_rollouts --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --mode confirmation --env-source paper9 --policy $policy --model-seeds 5101,5102,5103 --seeds 4000-4019 --rollout-steps 100 --resume --output "paper10_runs\pcc_v1\confirmation\bishan_${policy}.json"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
```

Expected: every stochastic learned policy has a complete `3 x 20` block; deterministic policies contain one shared policy block mapped consistently across model seeds.

- [ ] **Step 3: Run the oracle diagnostic separately**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_rollouts --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --mode diagnostic --env-source paper9 --policy oracle_action_audit --seeds 4000-4019 --rollout-steps 100 --resume --output paper10_runs\pcc_v1\confirmation\bishan_oracle_diagnostic.json
```

Expected: output is labelled `deployable=false` and is excluded by the statistics CLI from primary comparison selection.

- [ ] **Step 4: Generate Dongxing adaptation and calibration labels**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_value_labels --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --partition dongxing_adaptation --seeds 6000-6003 --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --states-per-trajectory 20 --candidate-actions 8 --horizons 1,3,5 --output-dir paper10_runs\pcc_v1\labels\dongxing_adaptation
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_value_labels --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --partition dongxing_calibration --seeds 7000-7019 --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --states-per-trajectory 10 --candidate-actions 8 --horizons 1,3,5 --output-dir paper10_runs\pcc_v1\labels\dongxing_calibration
```

Expected: action-relative checkpoints require no action-embedding replacement; only the declared adapter/calibration stage uses these labels.

- [ ] **Step 5: Adapt only the frozen PCC heads and fit Dongxing calibration**

```powershell
$modelSeeds = 5101,5102,5103
foreach ($modelSeed in $modelSeeds) {
  D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_train --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --labels-manifest paper10_runs\pcc_v1\labels\dongxing_adaptation\manifest.json --model-seed $modelSeed --ensemble-size-from-frozen-registry --init-checkpoint-root paper10_runs\pcc_v1\policy_iteration --trainable-scope objective_heads --epochs 10 --device cpu --output-dir "paper10_runs\pcc_v1\dongxing_adaptation\seed${modelSeed}"
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.planning.paired_conformal --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --labels-manifest paper10_runs\pcc_v1\labels\dongxing_calibration\manifest.json --checkpoint-root paper10_runs\pcc_v1\dongxing_adaptation --coverage-from-frozen-registry --output-dir paper10_runs\pcc_v1\dongxing_calibration
```

Expected: the action-relative trunk and all selection hyperparameters remain
frozen; only objective heads are adapted, and the coverage value is copied from
the frozen Bishan configuration rather than selected on Dongxing.

- [ ] **Step 6: Run Dongxing confirmation on seeds 8000-8019**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_rollouts --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --mode confirmation --env-source neijiang --prepared-dir D:\test\neijiang_cross_region --policy-set frozen_external --model-seeds 5101,5102,5103 --seeds 8000-8019 --rollout-steps 100 --resume --output paper10_runs\pcc_v1\confirmation\dongxing_frozen_external.json
```

Expected: complete external-confirmation blocks with the same frozen core architecture and no region-specific hyperparameter search.

- [ ] **Step 7: Run information-set audit and locked statistics**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_information_set_audit --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --input-root paper10_runs\pcc_v1\confirmation --output-json paper10_geojepa_mpc\experiments\results\pcc_v1\confirmation_information_audit.json --output-md paper10_geojepa_mpc\experiments\results\pcc_v1\confirmation_information_audit.md
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_confirmatory_statistics --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --bishan-root paper10_runs\pcc_v1\confirmation --dongxing-json paper10_runs\pcc_v1\confirmation\dongxing_frozen_external.json --draws 20000 --bootstrap-seed 20260710 --output-prefix paper10_geojepa_mpc\experiments\results\pcc_v1\confirmatory
```

Expected: information audit passes; statistics emits JSON, Markdown, and CSV and records each success gate as true or false without changing the registry.

- [ ] **Step 8: Commit immutable confirmation summaries**

```powershell
git add paper10_geojepa_mpc\experiments\results\pcc_v1
git commit -m "exp: record pcc v1 independent confirmation"
```

Expected: only derived summaries/source data are tracked; restricted inputs and bulky local rollout logs remain outside Git.

## Phase IV: Figures, Manuscript, and Submission Evidence

### Task 15: Generate Python Figures 1-5 and Tables 1-3

**Files:**
- Create: `scripts/paper10/plot_pcc_manuscript_figures.py`
- Create: `paper10_geojepa_mpc/tests/test_pcc_figure_assets.py`
- Generate: `paper10_geojepa_mpc/experiments/results/ceus_submission_assets/pcc_v1/`
- Generate: `paper10_geojepa_mpc/experiments/results/pcc_v1/source_data/`

- [ ] **Step 1: Read figure QA references before plotting**

Read completely:

```text
C:\Users\zn198\.codex\skills\nature-figure\references\figure-contract.md
C:\Users\zn198\.codex\skills\nature-figure\references\api.md
C:\Users\zn198\.codex\skills\nature-figure\references\qa-contract.md
C:\Users\zn198\.codex\skills\nature-figure\references\figure-legend-conventions.md
```

- [ ] **Step 2: Write failing figure-contract tests**

```python
from pathlib import Path

ASSET_ROOT = Path("paper10_geojepa_mpc/experiments/results/ceus_submission_assets/pcc_v1")


def test_every_main_figure_has_editable_and_raster_exports():
    for number in range(1, 6):
        stem = ASSET_ROOT / f"figure_{number}_pcc"
        assert stem.with_suffix(".svg").exists()
        assert stem.with_suffix(".pdf").exists()
        assert stem.with_suffix(".tiff").exists()


def test_svg_has_editable_text_and_no_clipping_markers():
    text = (ASSET_ROOT / "figure_2_pcc.svg").read_text(encoding="utf-8")
    assert "<text" in text
    assert "clip-warning" not in text
```

- [ ] **Step 3: Run figure tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_figure_assets.py -q
```

Expected: fails because the plotting script and assets do not exist.

- [ ] **Step 4: Implement one source-data-driven plotting entry point**

Use these exact export settings:

```python
import matplotlib as mpl

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "legend.frameon": False,
})


def save_figure(fig, stem):
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=200, bbox_inches="tight")
```

The script reads only frozen confirmation JSON/CSV and creates Figure 1 mechanism,
Figure 2 Bishan effects, Figure 3 calibration/ablation, Figure 4 Dongxing effects,
Figure 5 spatial outcomes, Tables 1-3 CSV/Markdown, and per-figure source-data CSV.

- [ ] **Step 5: Generate assets and perform visual QA**

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\plot_pcc_manuscript_figures.py --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --results-root paper10_geojepa_mpc\experiments\results\pcc_v1 --output-root paper10_geojepa_mpc\experiments\results\ceus_submission_assets\pcc_v1
```

Inspect every PNG with the image viewer at original detail. Correct overlaps,
clipping, unreadable labels, inconsistent axes, and map extent differences in the
Python script, regenerate, and repeat until all five pass.

- [ ] **Step 6: Run figure tests and commit**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_figure_assets.py -q
git add scripts\paper10\plot_pcc_manuscript_figures.py paper10_geojepa_mpc\tests\test_pcc_figure_assets.py paper10_geojepa_mpc\experiments\results\ceus_submission_assets\pcc_v1 paper10_geojepa_mpc\experiments\results\pcc_v1\source_data
git commit -m "fig: add pcc manuscript evidence figures"
```

Expected: all exports exist, SVG text is editable, and visual inspection records no overlap or clipping.

### Task 16: Rebuild the CEUS Manuscript from Frozen Evidence

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_ceus_main_manuscript_2026-07-10.md`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_claim_evidence_map_2026-07-10.md`
- Modify: `references/paper10_verified_references_2026-06-09.bib`
- Modify: `references/paper10_citation_map_2026-06-09.md`
- Modify: `DATA_AVAILABILITY.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `README.md`
- Modify: `MANIFEST.md`
- Modify: `scripts/paper10/preflight_submission_checks.py`
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`

- [ ] **Step 1: Run a final verified literature search before novelty wording**

Search CrossRef/OpenAlex/arXiv for the exact intersection of:

```text
paired conformal policy improvement; multi-objective model predictive control;
ensemble world models; conservative Pareto reinforcement learning;
executed-feedback calibration; spatial land-use planning.
```

Verify every added citation by DOI or arXiv identifier, add only sources actually
read, and do not claim that ensemble, conformal prediction, Pareto optimization,
or conservative planning is individually new.

- [ ] **Step 2: Write failing manuscript/preflight tests**

Add checks that the new main manuscript:

```python
assert "PCC-GeoJEPA-MPC" in manuscript
assert "oracle action-audit diagnostic upper bound" in manuscript
assert "unexecuted real-reward queries" in manuscript
assert "@" not in references_section
assert "pending author decision" not in public_main_text.lower()
assert confirmatory_report["primary_success"] == manuscript_claims["primary_success"]
```

The test must fail if any success claim appears when the corresponding frozen gate
is false, or if Figure 1-5/Table 1-3 source paths do not resolve.

- [ ] **Step 3: Run preflight tests and verify RED**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q
```

Expected: fails because the PCC manuscript and PCC preflight checks are absent.

- [ ] **Step 4: Draft the manuscript in evidence order**

Use the locked structure:

1. Introduction: multi-objective planning problem, model uncertainty and scalar
   reward mismatch, exact prior-work boundary, and PCC contribution.
2. Methods: formal task/objective orientation, online information set,
   action-relative ensemble, joint calibration, Pareto gate, executed feedback,
   protocol registry, and statistics.
3. Results: calibration validity, Bishan confirmation, planning non-inferiority,
   matched compute, ablations, Dongxing confirmation, runtime, and failures.
4. Discussion: mechanism interpretation, rival explanations, scalar-reward
   alignment, external adaptation, confidentiality, block abstraction, and
   deployment boundary.
5. Conclusion: contribution, decisive frozen evidence, implication, and exact
   boundary.

If `primary_success` is false, do not write a breakthrough claim. Record which
locked condition failed and stop submission conversion pending a new, separately
designed `pcc_v2`; do not reuse the `pcc_v1` confirmation seeds.

- [ ] **Step 5: Replace internal artifact prose with reader-facing content**

Remove experiment-package names, source-control narration, unresolved field notes,
raw config strings, citation keys, and caption instructions from the main text.
Keep commands, digests, and artifact maps in `REPRODUCIBILITY.md` and the claim map.

- [ ] **Step 6: Update data/code availability and exact archive identity**

State the confidential DLTB boundary, public derived artifacts, exact reviewer
snapshot commit/digest, code licence, generated-data licence, and which experiments
can and cannot be independently rerun. The anonymous reviewer archive must map to
the exact submission commit before preflight can pass.

- [ ] **Step 7: Run manuscript, citation, and preflight checks**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected: PCC manuscript checks pass and `Paper10 preflight: PASS`.

- [ ] **Step 8: Commit the rebuilt submission evidence**

```powershell
git add paper10_geojepa_mpc\experiments\results\e0_paper10_pcc_ceus_main_manuscript_2026-07-10.md paper10_geojepa_mpc\experiments\results\e0_paper10_pcc_claim_evidence_map_2026-07-10.md references DATA_AVAILABILITY.md REPRODUCIBILITY.md README.md MANIFEST.md scripts\paper10\preflight_submission_checks.py paper10_geojepa_mpc\tests\test_submission_preflight.py
git commit -m "docs: rebuild paper10 around confirmed pcc evidence"
```

Expected: commit includes no unresolved citation keys, no unverified novelty claim, and no untracked local inputs.

### Task 17: Final Verification and Branch Handoff

**Files:**
- No new files unless verification exposes a defect; defects require a failing regression test before repair.

- [ ] **Step 1: Run the complete test suite**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q
```

Expected: all tests pass with zero failures.

- [ ] **Step 2: Run submission preflight again from the final tree**

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected: `Paper10 preflight: PASS`.

- [ ] **Step 3: Verify tracked-tree and artifact integrity**

```powershell
git status --short --branch
git diff --check
git log -5 --oneline
```

Expected: no tracked modifications; only the preserved `%SystemDrive%/` and
`2503.05774v1.pdf` may remain untracked.

- [ ] **Step 4: Verify all reported values regenerate**

Regenerate statistics, tables, and figures from frozen inputs and compare hashes
or numeric source data to tracked outputs. Any mismatch blocks completion.

- [ ] **Step 5: Use `superpowers:requesting-code-review` and then `superpowers:finishing-a-development-branch`**

Request a final review focused on information leakage, statistical independence,
objective orientation, matched compute, manuscript claim/evidence consistency, and
missing tests. Resolve verified findings with TDD before presenting integration
options.
