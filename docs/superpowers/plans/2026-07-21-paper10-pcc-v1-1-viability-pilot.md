# Paper10 PCC v1.1 Viability Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox ("- [ ]") syntax for tracking.

**Goal:** Replace the non-viable PCC v1 development path with a protocol-isolated direct paired-delta GeoJEPA policy, selected-candidate conformal planning certificate, and fail-closed real-data viability pilot.

**Architecture:** Keep PCC v1 source data and failure evidence immutable. Build PCC v1.1 in new modules with a direct candidate-versus-reference model, model-specific selected-candidate labels, one-sided planning-only conformal calibration, and a pilot orchestrator that stops before the full factorial unless a non-trivial policy passes every predeclared gate.

**Tech Stack:** Python 3.13, PyTorch, NumPy, pytest, existing Paper9/Paper10 environment adapters, JSON/Markdown/SHA-256 artifacts, Git worktrees.

---

## Execution Rules

1. Use "D:\adk\.venv\Scripts\python.exe" for every Python command.
2. Work only in "D:\test\paper10-geojepa-mpc-farmland-layout\.worktrees\pcc-v1-completion" on branch "codex/pcc-v1-completion".
3. Implement every production behavior RED -> verify RED -> GREEN -> verify GREEN.
4. Keep "paper10_geojepa_mpc/experiments/protocols/pcc_v1.json" and all PCC v1 outputs immutable.
5. Create PCC v1.1 outputs only under "D:\test\paper10_pcc_v1_1_runs".
6. Reuse round-0 PCC v1 train/calibration labels only through explicit source-protocol and manifest-digest validation.
7. Do not run Bishan seeds 4000-4019 or Dongxing seeds 8000-8019 in this plan.
8. Do not implement the full factorial, freeze, confirmation, figures, or manuscript in this plan. A passing pilot is the handoff gate for the next plan.
9. Record a valid pilot failure without changing coverage, thresholds, seeds, or retrying a seed under another configuration.
10. Commit after each task with only the files listed for that task.

## File Map

### Protocol and failure boundary

- Create "paper10_geojepa_mpc/experiments/protocols/pcc_v1_1.json": new development registry.
- Modify "paper10_geojepa_mpc/experiments/pcc_protocol_registry.py": dispatch locked validation for PCC v1.1 while leaving PCC v1 unchanged.
- Create "paper10_geojepa_mpc/experiments/pcc_v1_abandonment_audit.py": verify and serialize the stopped PCC v1 evidence.
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_1_protocol.py".
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_abandonment_audit.py".

### Model and training

- Create "paper10_geojepa_mpc/models/pcc_paired_delta.py": action-relative online/EMA target encoders and paired heads.
- Create "paper10_geojepa_mpc/training/pcc_v1_1_training.py": source loading, transfer initialization, losses, bootstrap training, and checkpoint IO.
- Create "paper10_geojepa_mpc/experiments/run_pcc_v1_1_train.py": focused training CLI.
- Create "paper10_geojepa_mpc/tests/test_pcc_paired_delta.py".
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_1_training.py".

### Selection and calibration

- Create "paper10_geojepa_mpc/planning/pcc_v1_1_selector.py": direct paired ensemble statistics, base selection, and certificate execution.
- Create "paper10_geojepa_mpc/planning/selected_conformal.py": one-sided planning-only trajectory calibration.
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_1_selector.py".
- Create "paper10_geojepa_mpc/tests/test_selected_conformal.py".

### Selected labels and pilot control

- Create "paper10_geojepa_mpc/experiments/pcc_v1_1_selected_labels.py": paired selected-action evaluation and atomic artifacts.
- Create "paper10_geojepa_mpc/experiments/run_pcc_v1_1_selected_labels.py": selected-label CLI.
- Create "paper10_geojepa_mpc/experiments/pcc_v1_1_viability.py": immutable pilot gate and report.
- Create "paper10_geojepa_mpc/experiments/run_pcc_v1_1_pilot.py": dry-run, execution, resume, and closeout.
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_1_selected_labels.py".
- Create "paper10_geojepa_mpc/tests/test_pcc_v1_1_viability.py".
- Create "paper10_geojepa_mpc/tests/test_run_pcc_v1_1_pilot.py".

### Tracked scientific audits

- Generate "paper10_geojepa_mpc/experiments/results/pcc_v1/pcc_v1_abandonment_audit.json".
- Generate "paper10_geojepa_mpc/experiments/results/pcc_v1/pcc_v1_abandonment_audit.md".
- Generate after real pilot "paper10_geojepa_mpc/experiments/results/pcc_v1_1/pilot_audit.json".
- Generate after real pilot "paper10_geojepa_mpc/experiments/results/pcc_v1_1/pilot_audit.md".

## Task 1: Lock PCC v1.1 and Record the PCC v1 Abandonment Boundary

**Files:**

- Create: "paper10_geojepa_mpc/experiments/protocols/pcc_v1_1.json"
- Modify: "paper10_geojepa_mpc/experiments/pcc_protocol_registry.py"
- Create: "paper10_geojepa_mpc/experiments/pcc_v1_abandonment_audit.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_1_protocol.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_abandonment_audit.py"

- [ ] **Step 1: Write failing PCC v1.1 registry tests**

Add tests that load the new registry and protect protocol separation:

~~~python
from copy import deepcopy
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)


REGISTRY = (
    Path(__file__).parents[1]
    / "experiments"
    / "protocols"
    / "pcc_v1_1.json"
)


def test_pcc_v1_1_locks_source_protocol_and_selected_risk_contract():
    payload = load_registry(REGISTRY)
    validate_registry(payload)
    assert payload["protocol_id"] == "pcc_v1_1"
    assert payload["status"] == "development"
    assert payload["source_inputs"]["protocol_id"] == "pcc_v1"
    assert payload["selected_conformal"]["score"] == (
        "one_sided_selected_trajectory_planning_max"
    )
    assert payload["selected_conformal"]["objectives"] == [
        "slope_benefit",
        "contiguity_benefit",
        "connected_area_benefit",
    ]
    assert payload["compute_modes"] == {
        "matched": "floor(50 / ensemble_size)",
        "full": 50,
    }
    assert payload["viability"]["development_seeds"] == list(range(3000, 3010))
    assert payload["viability"]["states_per_trajectory"] == 20


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("source_inputs", "protocol_id"), "pcc_v1_1"),
        (("viability", "minimum_nonfallback_rate"), 0.0),
        (("viability", "minimum_action_difference_rate"), 0.0),
        (("selected_conformal", "score"), "absolute_all_candidate_max"),
    ],
)
def test_pcc_v1_1_rejects_scientific_contract_mutation(path, value):
    payload = deepcopy(load_registry(REGISTRY))
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError, match="pcc_v1_1"):
        validate_registry(payload)


def test_pcc_v1_locked_contract_remains_unchanged():
    legacy = load_registry()
    validate_registry(legacy)
    assert legacy["protocol_id"] == "pcc_v1"
~~~

- [ ] **Step 2: Run the registry tests and verify RED**

Run:

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_protocol.py -q
~~~

Expected: FAIL because "pcc_v1_1.json" does not exist.

- [ ] **Step 3: Create the locked PCC v1.1 registry and validation branch**

The JSON must preserve the existing partition and model-seed blocks and add these exact fields:

~~~json
{
  "protocol_id": "pcc_v1_1",
  "status": "development",
  "source_inputs": {
    "protocol_id": "pcc_v1",
    "train_manifest_digest": "fd948356c45e68ccf4f95824902487ba62d6cc1eb912df812cc08842c9ce57db",
    "calibration_manifest_digest": "18f04a375bc59598047342bc59e27c05f29aaac96bc92d2583407e51f14d647b"
  },
  "model": {
    "class": "PCCPairedDeltaMember",
    "representation": "action_relative",
    "hidden_dim": 32,
    "ema_decay": 0.99,
    "transfer_checkpoint_sha256": "fd3cdeeb827dc59a30e559a36fc95166db77447dc6e7d1d4b5b4c081704c947f"
  },
  "selected_conformal": {
    "coverages": [0.8, 0.9, 0.95],
    "score": "one_sided_selected_trajectory_planning_max",
    "objectives": [
      "slope_benefit",
      "contiguity_benefit",
      "connected_area_benefit"
    ],
    "epsilon": 1e-06
  },
  "compute_modes": {
    "matched": "floor(50 / ensemble_size)",
    "full": 50
  },
  "viability": {
    "ensemble_size": 3,
    "policy_round": 1,
    "development_seeds": [
      3000,
      3001,
      3002,
      3003,
      3004,
      3005,
      3006,
      3007,
      3008,
      3009
    ],
    "states_per_trajectory": 20,
    "minimum_nonfallback_rate": 0.1,
    "minimum_action_difference_rate": 0.1,
    "minimum_reward_delta": 0.0,
    "minimum_planning_delta": 0.0,
    "minimum_supporting_model_seeds": 2,
    "coverage_selection": "highest_passing"
  }
}
~~~

Retain the existing partitions, horizons, offline reference policy, information set, and success gates. Add "LOCKED_PCC_V1_1_CONTRACT" and a "protocol_id == 'pcc_v1_1'" validation branch without modifying "LOCKED_PCC_V1_CONTRACT".

- [ ] **Step 4: Verify the registry tests GREEN**

Run the Task 1 registry command again.

Expected: all tests in "test_pcc_v1_1_protocol.py" pass.

- [ ] **Step 5: Write failing abandonment-audit tests**

Create fixtures with one completed seed whose new NPZ hash equals a round-0 hash and one incomplete directory. Assert:

~~~python
def test_abandonment_audit_records_only_atomic_complete_seeds(tmp_path):
    old_root, round0_root = make_old_run_fixture(tmp_path)
    report = audit_abandoned_pcc_v1(
        old_root,
        round0_root=round0_root,
        registry_digest="a" * 64,
        stop_verified_at="2026-07-21T12:40:00+09:00",
        confirmation_seeds_run=(),
    )
    assert report["status"] == "abandoned_before_freeze"
    assert report["completed_round2_train_seeds"] == [1000]
    assert report["byte_identical_to_round0_seeds"] == [1000]
    assert report["incomplete_seed_directories"] == ["seed_1001"]
    assert report["confirmation_seeds_run"] == []
    assert report["eligible_for_pcc_v1_1_resume"] is False


def test_abandonment_audit_rejects_any_confirmation_seed(tmp_path):
    old_root, round0_root = make_old_run_fixture(tmp_path)
    with pytest.raises(ValueError, match="confirmation"):
        audit_abandoned_pcc_v1(
            old_root,
            round0_root=round0_root,
            registry_digest="a" * 64,
            stop_verified_at="2026-07-21T12:40:00+09:00",
            confirmation_seeds_run=(4000,),
        )
~~~

- [ ] **Step 6: Verify RED, implement the audit, and verify GREEN**

Implement:

~~~python
def audit_abandoned_pcc_v1(
    run_root,
    *,
    round0_root,
    registry_digest,
    stop_verified_at,
    confirmation_seeds_run=(),
) -> dict[str, object]:
    run_root = Path(run_root).resolve()
    round0_root = Path(round0_root).resolve()
    confirmation = sorted(map(int, confirmation_seeds_run))
    if confirmation:
        raise ValueError("PCC v1 abandonment audit forbids confirmation seeds")
    complete, incomplete, identical, artifacts = [], [], [], []
    train_root = run_root / "seed_5101" / "round2" / "labels" / "train"
    for seed_dir in sorted(train_root.glob("seed_*")):
        manifest_path = seed_dir / "manifest.json"
        if not manifest_path.is_file():
            incomplete.append(seed_dir.name)
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifact = manifest["artifacts"][0]
        path = seed_dir / str(artifact["path"])
        if _sha256_file(path) != str(artifact["sha256"]):
            incomplete.append(seed_dir.name)
            continue
        seed = int(artifact["trajectory_seed"])
        complete.append(seed)
        round0 = round0_root / f"seed_{seed}" / f"trajectory_{seed}.npz"
        if round0.is_file() and _sha256_file(round0) == _sha256_file(path):
            identical.append(seed)
        artifacts.append(
            {"seed": seed, "path": str(path), "sha256": _sha256_file(path)}
        )
    return {
        "schema_version": 1,
        "protocol_id": "pcc_v1",
        "status": "abandoned_before_freeze",
        "registry_digest": str(registry_digest),
        "stop_verified_at": str(stop_verified_at),
        "completed_round2_train_seeds": sorted(complete),
        "byte_identical_to_round0_seeds": sorted(identical),
        "incomplete_seed_directories": sorted(incomplete),
        "artifacts": artifacts,
        "confirmation_seeds_run": confirmation,
        "eligible_for_pcc_v1_1_resume": False,
    }
~~~

The CLI writes canonical JSON plus Markdown and refuses to overwrite an audit whose canonical content differs.

Run:

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_protocol.py paper10_geojepa_mpc\tests\test_pcc_v1_abandonment_audit.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
~~~

- [ ] **Step 7: Commit the protocol boundary**

~~~powershell
git add paper10_geojepa_mpc\experiments\protocols\pcc_v1_1.json paper10_geojepa_mpc\experiments\pcc_protocol_registry.py paper10_geojepa_mpc\experiments\pcc_v1_abandonment_audit.py paper10_geojepa_mpc\tests\test_pcc_v1_1_protocol.py paper10_geojepa_mpc\tests\test_pcc_v1_abandonment_audit.py
git commit -m "feat: isolate pcc v1.1 development protocol"
~~~

## Task 2: Implement the Direct Paired-Delta GeoJEPA Member

**Files:**

- Create: "paper10_geojepa_mpc/models/pcc_paired_delta.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_paired_delta.py"

- [ ] **Step 1: Write failing shape, identity, and EMA tests**

Add:

~~~python
def make_inputs(batch=3, blocks=7):
    torch.manual_seed(4)
    return {
        "block": torch.randn(batch, blocks, 17),
        "neighbour": torch.randn(batch, blocks, 17),
        "global_features": torch.randn(batch, 12),
        "candidate_actions": torch.tensor([1, 2, 3])[:batch],
        "reference_actions": torch.tensor([0, 0, 0])[:batch],
    }


def test_paired_delta_member_outputs_direct_horizon_delta_and_scale():
    model = PCCPairedDeltaMember(17, 12, hidden_dim=16)
    output = model(**make_inputs())
    assert output.delta_mean.shape == (3, 3, 4)
    assert output.delta_log_scale.shape == (3, 3, 4)
    assert output.candidate_absolute_mean.shape == (3, 4)
    assert output.executable_logit.shape == (3,)
    assert output.candidate_latent.shape == output.reference_latent.shape
    assert torch.isfinite(output.delta_mean).all()


def test_model_uses_no_county_specific_action_embedding():
    model = PCCPairedDeltaMember(17, 12)
    assert not any("embedding" in name for name, _ in model.named_parameters())
    large_county = make_inputs(blocks=11)
    model(**large_county)


def test_target_encoder_is_frozen_and_moves_only_by_ema():
    model = PCCPairedDeltaMember(17, 12, ema_decay=0.5)
    assert not any(p.requires_grad for p in model.target_encoder.parameters())
    before = clone_parameters(model.target_encoder)
    with torch.no_grad():
        next(model.online_encoder.parameters()).add_(2.0)
    model.update_target_encoder()
    after = clone_parameters(model.target_encoder)
    assert any(not torch.equal(before[k], after[k]) for k in before)
    for name, target in after.items():
        expected = 0.5 * before[name] + 0.5 * dict(
            model.online_encoder.named_parameters()
        )[name]
        assert torch.allclose(target, expected)


def test_target_latent_has_stopped_gradient():
    model = PCCPairedDeltaMember(17, 12)
    inputs = make_inputs()
    target = model.encode_target(
        inputs["block"],
        inputs["neighbour"],
        inputs["global_features"],
        inputs["candidate_actions"],
    )
    assert target.requires_grad is False
~~~

- [ ] **Step 2: Run and verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_paired_delta.py -q
~~~

Expected: collection fails because "pcc_paired_delta" does not exist.

- [ ] **Step 3: Implement the model**

Use these public types and methods:

~~~python
HORIZONS = (1, 3, 5)


class PairedDeltaOutput(NamedTuple):
    delta_mean: torch.Tensor
    delta_log_scale: torch.Tensor
    candidate_absolute_mean: torch.Tensor
    candidate_absolute_log_scale: torch.Tensor
    executable_logit: torch.Tensor
    candidate_latent: torch.Tensor
    reference_latent: torch.Tensor


class ActionRelativeEncoder(nn.Module):
    def __init__(self, block_feature_dim, global_feature_dim, hidden_dim):
        super().__init__()
        self.block_encoder = nn.Sequential(
            nn.Linear(block_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.ReLU(),
        )
        self.neighbour_encoder = copy.deepcopy(self.block_encoder)
        self.global_encoder = nn.Sequential(
            nn.Linear(global_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.ReLU(),
        )
        self.projector = nn.Sequential(
            nn.Linear(hidden_dim * 6, 128),
            nn.ReLU(),
            nn.Linear(128, hidden_dim * 2),
        )

    def forward(self, block, neighbour, global_features, actions):
        batch = block.shape[0]
        rows = torch.arange(batch, device=block.device)
        encoded = self.block_encoder(block)
        neighbour_encoded = self.neighbour_encoder(neighbour)
        selected = encoded[rows, actions.long()]
        selected_neighbour = neighbour_encoded[rows, actions.long()]
        county_mean = encoded.mean(dim=1)
        context = torch.cat(
            [
                selected,
                selected_neighbour,
                selected - county_mean,
                county_mean,
                encoded.max(dim=1).values,
                self.global_encoder(global_features),
            ],
            dim=-1,
        )
        return self.projector(context)
~~~

"PCCPairedDeltaMember" owns "online_encoder", a deep-copied frozen "target_encoder", "jepa_predictor", "paired_trunk", "delta_head", "absolute_head", and "executable_head". Reshape the delta head to "[batch, 3, 2, 4]"; clamp log scales to "[-8, 5]". "update_target_encoder" applies the exact EMA equation from the test and copies buffers.

- [ ] **Step 4: Add a direct-pair permutation test**

Permute block rows and remap both candidate and reference actions. Require unchanged delta outputs. This protects county-size transfer without action embeddings.

- [ ] **Step 5: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_paired_delta.py paper10_geojepa_mpc\tests\test_pcc_geojepa.py -q
git add paper10_geojepa_mpc\models\pcc_paired_delta.py paper10_geojepa_mpc\tests\test_pcc_paired_delta.py
git commit -m "feat: add direct paired-delta geojepa member"
~~~

## Task 3: Implement Transfer-Initialized PCC v1.1 Training

**Files:**

- Create: "paper10_geojepa_mpc/training/pcc_v1_1_training.py"
- Create: "paper10_geojepa_mpc/experiments/run_pcc_v1_1_train.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_1_training.py"

- [ ] **Step 1: Write failing direct-target and transfer tests**

Add:

~~~python
def test_batch_targets_are_direct_candidate_minus_reference():
    arrays = tiny_source_arrays()
    batch = next(iter_paired_batches(arrays, batch_size=4, rng=np.random.default_rng(3)))
    expected = (
        arrays["objective_returns"][0, 0]
        - arrays["reference_objective_returns"][0, 0]
    )
    assert np.allclose(batch["target_delta"][0], expected)


def test_transfer_initialization_copies_only_compatible_encoders(tmp_path):
    source = write_tiny_e0_checkpoint(tmp_path / "e0.pt")
    model = PCCPairedDeltaMember(17, 12, hidden_dim=32)
    digest = initialize_from_paper9(model, source)
    _, checkpoint = load_e0_checkpoint(source)
    assert digest == sha256_file(source)
    assert torch.equal(
        model.online_encoder.block_encoder[0].weight,
        checkpoint["state_dict"]["block_encoder.0.weight"],
    )
    assert torch.equal(
        model.online_encoder.neighbour_encoder[0].weight,
        checkpoint["state_dict"]["block_encoder.0.weight"],
    )
    assert not any(
        "action_emb" in name for name, _ in model.named_parameters()
    )


def test_direct_delta_loss_does_not_sum_marginal_candidate_reference_variance():
    output = paired_output(
        delta_mean=torch.zeros(2, 3, 4),
        delta_log_scale=torch.zeros(2, 3, 4),
    )
    target = torch.ones(2, 3, 4)
    loss = direct_delta_nll(target, output.delta_mean, output.delta_log_scale)
    expected = heteroscedastic_objective_loss(
        target, output.delta_mean, output.delta_log_scale
    )
    assert torch.equal(loss, expected)
~~~

- [ ] **Step 2: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_training.py -q
~~~

- [ ] **Step 3: Implement streaming paired batches and losses**

"iter_paired_batches" streams one trajectory artifact at a time and yields:

~~~python
{
    "block": states_bf[state_indexes],
    "neighbour": states_neighbor_bf[state_indexes],
    "global_features": states_gf[state_indexes],
    "candidate_actions": actions[state_indexes, candidate_indexes],
    "reference_actions": reference_actions[state_indexes],
    "target_delta": (
        objective_returns[state_indexes, candidate_indexes]
        - reference_objective_returns[state_indexes, candidate_indexes]
    ),
    "candidate_absolute_target": objective_returns[
        state_indexes, candidate_indexes, 0
    ],
    "candidate_next_block": candidate_next_bf[
        state_indexes, candidate_indexes
    ],
    "candidate_next_global": candidate_next_gf[
        state_indexes, candidate_indexes
    ],
    "reference_next_block": reference_next_bf[
        state_indexes, candidate_indexes
    ],
    "reference_next_global": reference_next_gf[
        state_indexes, candidate_indexes
    ],
    "executable": executable_targets[state_indexes, candidate_indexes],
}
~~~

The training step computes:

~~~python
delta_nll = direct_delta_nll(
    target_delta_normalized,
    output.delta_mean,
    output.delta_log_scale,
)
absolute_nll = heteroscedastic_objective_loss(
    candidate_absolute_normalized,
    output.candidate_absolute_mean,
    output.candidate_absolute_log_scale,
)
candidate_target = model.encode_target(
    candidate_next_block,
    neighbour,
    candidate_next_global,
    candidate_actions,
)
reference_target = model.encode_target(
    reference_next_block,
    neighbour,
    reference_next_global,
    reference_actions,
)
jepa_loss = 0.5 * (
    F.smooth_l1_loss(model.jepa_predictor(output.candidate_latent), candidate_target)
    + F.smooth_l1_loss(model.jepa_predictor(output.reference_latent), reference_target)
)
rank_loss = zero_boundary_delta_ranking_loss(
    target_delta[..., :1],
    predicted_normalized=output.delta_mean[..., :1],
    center=delta_center[..., :1],
    scale=delta_scale[..., :1],
)
executable_bce = F.binary_cross_entropy_with_logits(
    output.executable_logit,
    executable,
)
loss = (
    delta_nll
    + 0.25 * absolute_nll
    + 0.25 * jepa_loss
    + 0.20 * rank_loss
    + 0.10 * executable_bce
    + 0.01 * sigreg_loss(
        torch.cat([output.candidate_latent, output.reference_latent], dim=0),
        n_projections=16,
        n_knots=8,
    )
)
~~~

After "optimizer.step()", call "model.update_target_encoder()".

The rank term uses the sign of the uncentered candidate-minus-reference target.
Its normalized prediction is shifted by `center / scale`, so the decision
boundary remains a raw delta of zero rather than the training-set median. Exact
zero targets do not impose a ranking direction.

- [ ] **Step 4: Implement checkpoint transfer, lineage, and IO**

Checkpoint payloads must include:

~~~python
{
    "model_class": "PCCPairedDeltaMember",
    "protocol_id": "pcc_v1_1",
    "source_protocol_id": "pcc_v1",
    "source_manifest_digest": source_manifest_digest,
    "transfer_checkpoint_sha256": transfer_digest,
    "model_seed": model_seed,
    "ensemble_size": ensemble_size,
    "member_index": member_index,
    "member_seed": member_seed,
    "bootstrap_trajectory_ids": bootstrap_ids.tolist(),
    "model_kwargs": model.model_kwargs(),
    "delta_scaling": delta_scaling,
    "absolute_scaling": absolute_scaling,
    "trainable_parameter_names": sorted(trainable_names),
    "metrics": metrics,
    "state_dict": cpu_state_dict(model),
}
~~~

"load_pcc_v1_1_checkpoint" rejects PCC v1 checkpoints and verifies objective/horizon order.

"delta_scaling" has center/scale arrays of shape "[3, 4]" computed from direct
candidate-minus-reference targets. "absolute_scaling" has center/scale arrays of
shape "[4]" computed from candidate horizon-1 outcomes. Training normalizes the
two heads with their own scaling, and checkpoint loading rejects missing,
non-finite, or non-positive scales.

- [ ] **Step 5: Add the focused training CLI and round-trip test**

The CLI accepts:

~~~text
--registry
--labels-manifest
--reference-checkpoint
--model-seed
--ensemble-size
--epochs
--batch-size
--learning-rate
--device
--output-dir
~~~

It verifies source protocol/digest before creating the output directory.

- [ ] **Step 6: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_training.py paper10_geojepa_mpc\tests\test_pcc_paired_delta.py paper10_geojepa_mpc\tests\test_pcc_training.py -q
git add paper10_geojepa_mpc\training\pcc_v1_1_training.py paper10_geojepa_mpc\experiments\run_pcc_v1_1_train.py paper10_geojepa_mpc\tests\test_pcc_v1_1_training.py
git commit -m "feat: train transfer-initialized paired-delta ensembles"
~~~

## Task 4: Implement Fixed Base Selection and Certificate Execution

**Files:**

- Create: "paper10_geojepa_mpc/planning/pcc_v1_1_selector.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_1_selector.py"

- [ ] **Step 1: Write failing direct-scale and base-selection tests**

Add:

~~~python
def test_direct_paired_statistics_use_direct_aleatoric_scale():
    means = np.array(
        [
            [[[1.0, 0.0, 0.0, 0.0]]],
            [[[3.0, 0.0, 0.0, 0.0]]],
        ]
    )
    log_scales = np.log(np.full_like(means, 2.0))
    stats = direct_paired_statistics(means, log_scales)
    assert np.allclose(stats.mean_delta[..., 0], 2.0)
    assert np.allclose(
        stats.paired_scale[..., 0],
        np.sqrt(np.var([1.0, 3.0], ddof=1) + 4.0),
    )


def test_base_selector_optimizes_reward_mean_without_reward_lcb():
    actions = np.array([10, 20, 30])
    means = np.array(
        [
            [0.2, 0.0, 0.0, 0.0],
            [0.7, 0.1, 0.1, 0.1],
            [1.0, -0.2, 0.1, 0.1],
        ]
    )
    selected, info = choose_base_candidate(
        actions,
        means,
        scales=np.ones_like(means),
        executable_probability=np.ones(3),
        tolerances=np.zeros(3),
        executable_threshold=0.95,
    )
    assert selected == 20
    assert info["base_selection_reason"] == "reward_mean_among_mean_safe"


def test_coverage_changes_certificate_but_never_base_candidate():
    prediction = fixed_prediction(base_action=20)
    loose = calibrator(q=0.5, coverage=0.8)
    strict = calibrator(q=4.0, coverage=0.95)
    loose_action, loose_info = select_with_certificate(prediction, loose)
    strict_action, strict_info = select_with_certificate(prediction, strict)
    assert loose_info["base_selected_action"] == 20
    assert strict_info["base_selected_action"] == 20
    assert loose_action == 20
    assert strict_action == prediction.reference_action
~~~

- [ ] **Step 2: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_selector.py -q
~~~

- [ ] **Step 3: Implement direct ensemble prediction**

"predict_direct_paired_ensemble" loads each member once, batches the alternative actions, and returns physical-unit means/scales:

~~~python
member_means = np.stack(member_means, axis=0)
member_log_scales = np.stack(member_log_scales, axis=0)
mean_delta = member_means.mean(axis=0)
epistemic = (
    member_means.var(axis=0, ddof=1)
    if member_means.shape[0] > 1
    else np.zeros_like(mean_delta)
)
aleatoric = np.mean(np.exp(2.0 * member_log_scales), axis=0)
paired_scale = np.sqrt(np.maximum(epistemic + aleatoric, 1e-12))
~~~

Before these statistics, convert every member's normalized delta mean and scale
with that checkpoint's "delta_scaling". Convert the auxiliary absolute head only
with "absolute_scaling". Require all ensemble members to carry identical scaling
arrays.

Do not import or call "paired_ensemble_statistics" from PCC v1.

- [ ] **Step 4: Implement compute-mode candidate budgets and base selection**

~~~python
def candidate_budget(*, compute_mode: str, ensemble_size: int) -> int:
    if compute_mode == "matched":
        return 50 // int(ensemble_size)
    if compute_mode == "full":
        return 50
    raise ValueError("compute mode must be matched or full")
~~~

"build_v1_1_candidate_pool" uses the stable prefix declared in the design. Exclude the Paper9 reference from alternatives after recording it separately. "choose_base_candidate" filters executable probability and mean planning tolerances, then sorts by:

~~~python
(
    -mean_delta[index, 0],
    -mean_delta[index, 1:].min(),
    scales[index, 1:].max(),
    int(actions[index]),
)
~~~

- [ ] **Step 5: Implement certificate execution and stable fallback reasons**

Certificate lower bounds use planning objectives only:

~~~python
planning_lower = (
    selected_mean[1:]
    - calibrator.q_planning
    * selected_scale[1:]
    * feedback_multiplier[1:]
)
certified = np.all(planning_lower >= -tolerances)
~~~

Return one of:

- "no_executable_alternative"
- "no_mean_safe_candidate"
- "planning_certificate_rejected"
- "selected_candidate"
- "invalid_pcc_v1_1_state:<message>"

Always log "base_selected_action", "reference_action", "compute_mode", "candidate_count", "member_evaluations", "model_forward_count", "unexecuted_real_reward_queries=0", and the three planning lower bounds.

- [ ] **Step 6: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_selector.py paper10_geojepa_mpc\tests\test_pcc_selector.py -q
git add paper10_geojepa_mpc\planning\pcc_v1_1_selector.py paper10_geojepa_mpc\tests\test_pcc_v1_1_selector.py
git commit -m "feat: select pcc v1.1 candidates before certification"
~~~

## Task 5: Implement One-Sided Selected-Candidate Conformal Calibration

**Files:**

- Create: "paper10_geojepa_mpc/planning/selected_conformal.py"
- Create: "paper10_geojepa_mpc/tests/test_selected_conformal.py"

- [ ] **Step 1: Write failing score and finite-sample tests**

Add:

~~~python
def test_one_sided_score_ignores_harmless_underprediction():
    true = np.array([[[0.0, 10.0, 10.0, 10.0]]])
    predicted = np.array([[[0.0, 0.0, 0.0, 0.0]]])
    scale = np.ones_like(true)
    scores = selected_trajectory_scores(
        true,
        predicted,
        scale,
        trajectory_ids=np.array([2000]),
        planning_horizon_index=0,
    )
    assert scores.tolist() == [0.0]


def test_score_uses_only_selected_horizon_and_planning_objectives():
    true = np.zeros((2, 3, 4))
    predicted = np.zeros_like(true)
    predicted[0, 0, 0] = 1000.0
    predicted[0, 2, 1:] = 1000.0
    predicted[1, 1, 2] = 3.0
    scores = selected_trajectory_scores(
        true,
        predicted,
        np.ones_like(true),
        trajectory_ids=np.array([2000, 2000]),
        planning_horizon_index=1,
    )
    assert scores.tolist() == [3.0]


@pytest.mark.parametrize(
    ("coverage", "expected_rank"),
    [(0.8, 17), (0.9, 19), (0.95, 20)],
)
def test_twenty_trajectory_finite_sample_rank(coverage, expected_rank):
    calibrator = fit_selected_planning_calibrator(
        trajectory_scores=np.arange(1, 21, dtype=float),
        trajectory_ids=np.arange(2000, 2020),
        coverage=coverage,
        lineage=valid_lineage(),
    )
    assert calibrator.finite_sample_rank == expected_rank
    assert calibrator.q_planning == float(expected_rank)
~~~

- [ ] **Step 2: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_selected_conformal.py -q
~~~

- [ ] **Step 3: Implement score, fit, audit, and serialization**

Use:

~~~python
@dataclass(frozen=True)
class SelectedPlanningCalibrator:
    coverage: float
    q_planning: float
    finite_sample_rank: int
    planning_horizon: int
    trajectory_ids: np.ndarray
    trajectory_scores: np.ndarray
    model_seed: int
    ensemble_size: int
    policy_round: int
    compute_mode: str
    checkpoint_digests: tuple[str, ...]
    selected_labels_manifest_digest: str
    candidate_generator_digest: str
    base_selector_digest: str
    protocol_id: str = "pcc_v1_1"
~~~

"selected_trajectory_scores" validates shapes "[states, 3, 4]", uses objective indexes 1:4 at one horizon, divides by "max(scale, epsilon)", groups by trajectory ID, and clips each trajectory maximum at zero. "fit_selected_planning_calibrator" uses "ceil((n + 1) * coverage)" and stable order statistics. Save/load canonical JSON with "calibrator_digest".

The same module exposes a CLI:

~~~text
--registry
--selected-labels-manifest
--checkpoint-root
--model-seed
--ensemble-size
--policy-round
--planning-horizon
--compute-mode matched|full
--coverage
--output-dir
~~~

It loads the physical predictions and true deltas from the selected-label
artifacts, verifies every lineage field, fits one coverage-specific calibrator,
and writes "calibrator.json" atomically.

- [ ] **Step 4: Add lineage mutation and coverage-audit tests**

Mutating compute mode, selected-label digest, checkpoint order, horizon, or q must invalidate the digest or fail expected-lineage validation. "audit_selected_coverage" counts complete trajectories, not state rows.

- [ ] **Step 5: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_selected_conformal.py paper10_geojepa_mpc\tests\test_paired_conformal.py -q
git add paper10_geojepa_mpc\planning\selected_conformal.py paper10_geojepa_mpc\tests\test_selected_conformal.py
git commit -m "feat: calibrate selected planning certificates"
~~~

## Task 6: Generate Atomic Selected-Candidate Calibration and Audit Labels

**Files:**

- Create: "paper10_geojepa_mpc/experiments/pcc_v1_1_selected_labels.py"
- Create: "paper10_geojepa_mpc/experiments/run_pcc_v1_1_selected_labels.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_1_selected_labels.py"

- [ ] **Step 1: Write failing no-oracle paired-evaluation tests**

Use a tiny restorable environment and deterministic base policy:

~~~python
def test_selected_label_trajectory_evaluates_only_selected_and_reference():
    env = TinyPairedEnv()
    policy = FixedBasePolicy(selected=2, reference=1)
    result = generate_selected_label_trajectory(
        env=env,
        trajectory_seed=2000,
        n_states=2,
        horizons=(1, 3, 5),
        gamma=0.99,
        base_policy=policy,
        continuation_policy=FixedContinuationPolicy(),
        metric_reader=read_metrics,
    )
    assert env.real_step_calls == 2
    assert result["selected_actions"].tolist() == [2, 2]
    assert result["reference_actions"].tolist() == [1, 1]
    assert result["unexecuted_real_reward_queries"].tolist() == [0, 0]
    assert result["true_delta"].shape == (2, 3, 4)
    assert result["predicted_delta"].shape == (2, 3, 4)
    assert result["predicted_scale"].shape == (2, 3, 4)


def test_selected_label_generation_advances_on_reference_path():
    env = TinyPairedEnv()
    generate_selected_label_trajectory(
        env=env,
        trajectory_seed=2000,
        n_states=2,
        horizons=(1, 3, 5),
        gamma=0.99,
        base_policy=FixedBasePolicy(selected=2, reference=1),
        continuation_policy=FixedContinuationPolicy(),
        metric_reader=read_metrics,
    )
    assert env.executed_actions == [1, 1]
~~~

- [ ] **Step 2: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_selected_labels.py -q
~~~

- [ ] **Step 3: Implement selected trajectory generation**

At each state:

1. obtain observable state and base selection without conformal;
2. require "unexecuted_real_reward_queries == 0";
3. call the existing "evaluate_paired_objectives" exactly once for the selected/reference pair with a stable continuation seed;
4. store physical predicted delta/scale and true paired delta;
5. restore the environment after counterfactual evaluation; and
6. execute only the Paper9 reference action to advance the calibration path.

Store arrays:

~~~python
{
    "selected_actions": np.asarray(selected_actions, dtype=np.int64),
    "reference_actions": np.asarray(reference_actions, dtype=np.int64),
    "predicted_delta": np.stack(predicted_delta).astype(np.float32),
    "predicted_scale": np.stack(predicted_scale).astype(np.float32),
    "true_delta": np.stack(true_delta).astype(np.float32),
    "executable_probability": np.asarray(probability, dtype=np.float32),
    "base_selection_reason": np.asarray(reasons, dtype="U64"),
    "state_steps": np.asarray(state_steps, dtype=np.int64),
    "trajectory_ids": np.full(len(state_steps), trajectory_seed, dtype=np.int64),
    "unexecuted_real_reward_queries": np.zeros(len(state_steps), dtype=np.int64),
}
~~~

- [ ] **Step 4: Implement atomic artifact and manifest lineage**

The manifest binds protocol, registry digest, partition, seeds, model seed, K, round, compute mode, checkpoint digests, candidate-generator digest, base-selector digest, reference checkpoint digest, and artifact hashes. "load_resumable_selected_manifest" rejects any mismatch before accepting a completed seed.

- [ ] **Step 5: Add the CLI and subprocess-free fixture test**

CLI:

~~~text
--registry
--partition calibration|development
--seeds
--checkpoint-root
--model-seed
--ensemble-size
--policy-round
--compute-mode matched|full
--reference-checkpoint
--env-source paper9
--prepared-dir
--states-per-trajectory
--max-workers
--device
--resume
--output-root
~~~

The parser rejects confirmation partitions before loading an environment.

- [ ] **Step 6: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_selected_labels.py paper10_geojepa_mpc\tests\test_pcc_value_labels.py paper10_geojepa_mpc\tests\test_pcc_label_jobs.py -q
git add paper10_geojepa_mpc\experiments\pcc_v1_1_selected_labels.py paper10_geojepa_mpc\experiments\run_pcc_v1_1_selected_labels.py paper10_geojepa_mpc\tests\test_pcc_v1_1_selected_labels.py
git commit -m "feat: generate selected-candidate certificate labels"
~~~

## Task 7: Implement the Fail-Closed Viability Gate

**Files:**

- Create: "paper10_geojepa_mpc/experiments/pcc_v1_1_viability.py"
- Create: "paper10_geojepa_mpc/tests/test_pcc_v1_1_viability.py"

- [ ] **Step 1: Write failing all-fallback and coverage tests**

Add:

~~~python
def test_all_fallback_pilot_is_ineligible_even_with_perfect_planning():
    rows = synthetic_rows(
        certificate_passed=False,
        action_differs=False,
        reward_delta=0.0,
        planning_delta=(0.0, 0.0, 0.0),
        covered=True,
    )
    report = evaluate_viability(rows, contract=contract())
    assert report["passed"] is False
    assert "minimum_nonfallback_rate" in report["failed_gates"]
    assert "minimum_action_difference_rate" in report["failed_gates"]
    assert "positive_reward_delta" in report["failed_gates"]


def test_highest_coverage_passing_every_gate_is_selected():
    reports = {
        0.80: passing_coverage_report(0.80),
        0.90: passing_coverage_report(0.90),
        0.95: failing_coverage_report(0.95, "coverage"),
    }
    selected = select_viable_coverage(reports, declared=(0.80, 0.90, 0.95))
    assert selected == 0.90


def test_pilot_requires_two_supporting_model_seeds():
    rows = synthetic_model_seed_rows(
        support={5101: True, 5102: False, 5103: False}
    )
    report = evaluate_viability(rows, contract=contract())
    assert report["passed"] is False
    assert report["supporting_model_seeds"] == [5101]
~~~

- [ ] **Step 2: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_viability.py -q
~~~

- [ ] **Step 3: Implement development selected-label loading**

For each model seed and coverage:

- verify the selected-label and calibrator lineages;
- compute trajectory-level conformal coverage;
- derive certificate pass per state from the frozen q;
- set executed delta to selected true delta on certificate pass and zero on fallback;
- count base-selection, certificate, and invalid-state reasons; and
- reject any non-zero unexecuted real-reward query.

Compute coverage, non-fallback rate, action-difference rate, reward delta,
planning deltas, and rank association separately for each model seed. The ten
rollout seeds are the coverage units inside each model-seed block. Do not pool the
three predictions for one rollout seed as independent trajectories.

- [ ] **Step 4: Implement exact gate report**

"evaluate_viability" returns:

~~~python
{
    "passed": not failed_gates,
    "coverage": coverage,
    "trajectory_coverage": covered_trajectories / n_trajectories,
    "covered_trajectories": covered_trajectories,
    "n_trajectories": n_trajectories,
    "nonfallback_rate": certificate_passed.mean(),
    "action_difference_rate": action_differs.mean(),
    "mean_nonfallback_reward_delta": nonfallback_reward.mean(),
    "mean_executed_planning_delta": executed_planning.mean(axis=0).tolist(),
    "spearman_uncertainty_error": spearman,
    "supporting_model_seeds": supporting_model_seeds,
    "per_model_seed": per_model_seed_reports,
    "fallback_reasons": fallback_reason_counts,
    "unexecuted_real_reward_queries": query_count,
    "failed_gates": failed_gates,
}
~~~

Gate comparisons are:

~~~python
all(
    [
        seed_report["trajectory_coverage"] >= coverage,
        seed_report["nonfallback_rate"] >= 0.10,
        seed_report["action_difference_rate"] >= 0.10,
        seed_report["mean_nonfallback_reward_delta"] > 0.0,
        np.all(np.asarray(seed_report["mean_executed_planning_delta"]) >= 0.0),
        seed_report["spearman_uncertainty_error"] > 0.0,
        seed_report["unexecuted_real_reward_queries"] == 0,
    ]
)
len(supporting_model_seeds) >= 2
query_count == 0
~~~

Aggregate metrics first average within rollout seed and then summarize across
the ten paired rollout seeds. They are descriptive and cannot turn a failing
model-seed block into a supporting block.

- [ ] **Step 5: Implement deterministic JSON/Markdown output**

The Markdown lists every gate, observed value, threshold, pass/fail, model-seed rows, fallback reasons, source seeds, and all input digests. A failed pilot is a valid serialized report, not an exception. Schema or lineage defects still raise exceptions.

Expose a closeout CLI in the same module:

~~~text
--registry
--selected-development-root
--calibrator-root
--coverages 0.80,0.90,0.95
--output-json
--output-md
~~~

It loads all three model-seed blocks for every coverage, emits per-coverage gate
reports, applies "highest_passing", and exits zero for both a valid pass and a
valid scientific failure. It exits non-zero only for an implementation or
lineage defect.

- [ ] **Step 6: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_viability.py paper10_geojepa_mpc\tests\test_pcc_development.py -q
git add paper10_geojepa_mpc\experiments\pcc_v1_1_viability.py paper10_geojepa_mpc\tests\test_pcc_v1_1_viability.py
git commit -m "feat: gate pcc v1.1 on non-trivial viability"
~~~

## Task 8: Build the Resumable Viability Pilot Orchestrator

**Files:**

- Create: "paper10_geojepa_mpc/experiments/run_pcc_v1_1_pilot.py"
- Create: "paper10_geojepa_mpc/tests/test_run_pcc_v1_1_pilot.py"

- [ ] **Step 1: Write a failing dry-run plan test**

Add:

~~~python
def test_pilot_dry_run_contains_no_confirmation_seed_or_full_factorial(tmp_path):
    main(
        [
            "--registry",
            str(V11_REGISTRY),
            "--train-manifest",
            str(source_train_manifest(tmp_path)),
            "--reference-checkpoint",
            str(reference_checkpoint(tmp_path)),
            "--prepared-dir",
            str(tmp_path),
            "--output-dir",
            str(tmp_path / "pilot"),
            "--dry-run",
        ]
    )
    plan = json.loads((tmp_path / "pilot" / "execution_plan.json").read_text())
    assert plan["phase"] == "viability_pilot"
    assert plan["model_seeds"] == [5101, 5102, 5103]
    assert plan["ensemble_size"] == 3
    assert plan["policy_round"] == 1
    assert {job["phase"] for job in plan["jobs"]} == {
        "train",
        "selected_calibration_labels",
        "fit_selected_calibrators",
        "selected_development_labels",
        "viability_closeout",
    }
    command_text = "\n".join(
        " ".join(job["command"]) for job in plan["jobs"]
    )
    assert "4000" not in command_text
    assert "8000" not in command_text
    assert "--ensemble-size 5" not in command_text
    assert "--policy-round 2" not in command_text
~~~

- [ ] **Step 2: Write failing resume and stop-gate tests**

Require exact job metadata and output digests before resume. Mock subprocesses so a failed viability report proves that no round-2 or factorial job can be created:

~~~python
def test_failed_pilot_closes_without_factorial_jobs(tmp_path, monkeypatch):
    install_fake_pilot_workers(monkeypatch, outcome="scientific_failure")
    result = run_pilot(valid_args(tmp_path))
    assert result["status"] == "scientific_failure"
    assert result["selected_coverage"] is None
    assert not (tmp_path / "pilot" / "round2").exists()
    assert not (tmp_path / "pilot" / "factorial").exists()
~~~

- [ ] **Step 3: Verify RED**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_v1_1_pilot.py -q
~~~

- [ ] **Step 4: Implement execution-plan construction**

The CLI accepts:

~~~text
--registry
--train-manifest
--reference-checkpoint
--prepared-dir
--output-dir
--epochs
--batch-size
--learning-rate
--states-per-selected-trajectory
--max-workers
--device
--resume
--dry-run
--verify-only
--input-root
--audit-json
--audit-md
~~~

The plan contains 3 training jobs, 3 calibration selected-label jobs in matched mode, 9 calibrator jobs, 3 development selected-label jobs, and one closeout job. Coverage does not duplicate selected-label generation.

- [ ] **Step 5: Implement subprocess execution and atomic resume**

Write "job_metadata.json" before each worker. A completed job requires:

- matching command and registry digest;
- matching input file digests;
- a zero exit code;
- complete expected output files;
- output SHA-256 values; and
- a "completed_at" timestamp.

Resume rejects metadata mismatch rather than deleting or overwriting an output.

- [ ] **Step 6: Implement closeout and pilot inventory**

Closeout verifies:

- 3 model-seed families;
- exactly 9 member checkpoints;
- 3 matched selected-calibration manifests;
- 9 selected calibrators;
- 3 matched selected-development manifests;
- one report for each coverage; and
- the highest passing coverage or an explicit scientific failure.

Write the canonical tracked audit paths supplied by "--audit-json" and "--audit-md". The audit may contain paths to bulky local artifacts but must bind every path to a digest.

"--verify-only" requires "--input-root", forbids subprocess execution, reloads the
saved plan and every bound artifact from a fresh process, and emits the same
inventory counts plus "passed" and "status". It must not import or create an
environment.

- [ ] **Step 7: Verify GREEN and commit**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_v1_1_pilot.py paper10_geojepa_mpc\tests\test_pcc_v1_1_viability.py paper10_geojepa_mpc\tests\test_pcc_v1_1_selected_labels.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_v1_1_pilot.py paper10_geojepa_mpc\tests\test_run_pcc_v1_1_pilot.py
git commit -m "feat: orchestrate the pcc v1.1 viability pilot"
~~~

## Task 9: Verify the Implementation and Execute the Real Pilot

**Files:**

- Generate and track: "paper10_geojepa_mpc/experiments/results/pcc_v1/pcc_v1_abandonment_audit.json"
- Generate and track: "paper10_geojepa_mpc/experiments/results/pcc_v1/pcc_v1_abandonment_audit.md"
- Generate and track: "paper10_geojepa_mpc/experiments/results/pcc_v1_1/pilot_audit.json"
- Generate and track: "paper10_geojepa_mpc/experiments/results/pcc_v1_1/pilot_audit.md"
- Generate locally only: "D:\test\paper10_pcc_v1_1_runs\pilot"

- [ ] **Step 1: Run all PCC v1.1 focused tests**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_v1_1_protocol.py paper10_geojepa_mpc\tests\test_pcc_v1_abandonment_audit.py paper10_geojepa_mpc\tests\test_pcc_paired_delta.py paper10_geojepa_mpc\tests\test_pcc_v1_1_training.py paper10_geojepa_mpc\tests\test_pcc_v1_1_selector.py paper10_geojepa_mpc\tests\test_selected_conformal.py paper10_geojepa_mpc\tests\test_pcc_v1_1_selected_labels.py paper10_geojepa_mpc\tests\test_pcc_v1_1_viability.py paper10_geojepa_mpc\tests\test_run_pcc_v1_1_pilot.py -q
~~~

Expected: all PCC v1.1 tests pass.

- [ ] **Step 2: Run the complete repository suite**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q
~~~

Expected: no regression.

- [ ] **Step 3: Generate and inspect the PCC v1 abandonment audit**

Run:

~~~powershell
$pccStopVerifiedAt = Get-Date -Format o
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_v1_abandonment_audit --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --run-root D:\test\paper10_pcc_v1_completion_runs\policy_iteration --round0-root D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_train --stop-verified-at $pccStopVerifiedAt --output-json paper10_geojepa_mpc\experiments\results\pcc_v1\pcc_v1_abandonment_audit.json --output-md paper10_geojepa_mpc\experiments\results\pcc_v1\pcc_v1_abandonment_audit.md
~~~

Immediately before the command, capture the current ISO-8601 time with "Get-Date -Format o" and pass that literal value as "stop_verified_at". This records when the stopped state was verified, not an inferred process exit time. Require completed seeds "[1000, 1001, 1002, 1003, 1005]", no confirmation seeds, and "eligible_for_pcc_v1_1_resume=false".

- [ ] **Step 4: Dry-run and inspect the real pilot plan**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_v1_1_pilot --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1_1.json --train-manifest D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_train\manifest.json --reference-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir D:\test --output-dir D:\test\paper10_pcc_v1_1_runs\pilot --epochs 20 --batch-size 128 --learning-rate 0.001 --states-per-selected-trajectory 20 --max-workers 4 --device cpu --audit-json paper10_geojepa_mpc\experiments\results\pcc_v1_1\pilot_audit.json --audit-md paper10_geojepa_mpc\experiments\results\pcc_v1_1\pilot_audit.md --dry-run
~~~

Inspect "execution_plan.json". Require no K=5, no round 2, and no confirmation seed.

- [ ] **Step 5: Execute the real pilot with resume**

Run the same command without "--dry-run" and add "--resume".

Monitor exact completed job counts and process health. Do not start a duplicate process. A scientific-failure closeout is a completed pilot outcome.

- [ ] **Step 6: Verify the pilot result from a fresh process**

Run the "--verify-only --input-root" mode implemented in Task 8:

~~~powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_v1_1_pilot --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1_1.json --verify-only --input-root D:\test\paper10_pcc_v1_1_runs\pilot
~~~

Expected output has:

~~~json
{
  "passed": true,
  "checkpoint_families": 3,
  "physical_checkpoints": 9,
  "selected_calibration_manifests": 3,
  "calibrators": 9,
  "selected_development_manifests": 3
}
~~~

If "passed" is false, require the same complete inventory and an explicit "scientific_failure" with failed gates. Do not proceed to the full factorial.

- [ ] **Step 7: Commit the immutable audits**

~~~powershell
git add paper10_geojepa_mpc\experiments\results\pcc_v1\pcc_v1_abandonment_audit.json paper10_geojepa_mpc\experiments\results\pcc_v1\pcc_v1_abandonment_audit.md paper10_geojepa_mpc\experiments\results\pcc_v1_1\pilot_audit.json paper10_geojepa_mpc\experiments\results\pcc_v1_1\pilot_audit.md
git commit -m "exp: record pcc v1.1 viability pilot"
~~~

- [ ] **Step 8: Stop at the scientific gate**

If the pilot passes, write a new implementation plan for the complete 12-family, 48-checkpoint, 24-selected-label, 72-calibrator factorial. If it fails, record the negative development result and return to a separately approved design cycle. In both cases, do not run confirmation seeds under this plan.

## Final Verification for This Plan

- [ ] **Step 1: Verify tests and formatting**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q
git diff --check
~~~

- [ ] **Step 2: Verify protocol and seed boundaries**

~~~powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_protocol_registry --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1_1.json --verify-development
rg -n "4000|8000" D:\test\paper10_pcc_v1_1_runs\pilot\execution_plan.json
~~~

Expected: registry verification passes; confirmation seed search has no matches.

- [ ] **Step 3: Verify Git integrity**

~~~powershell
git status --short --branch
git log -12 --oneline
~~~

Expected: only the scoped PCC v1.1 commits and tracked audits are present; no bulky run artifact is tracked.

- [ ] **Step 4: Request code and scientific review**

Use "superpowers:requesting-code-review" with focus on direct-delta scale semantics, one-sided selected-candidate validity, candidate identity independence from coverage, source-protocol separation, no-oracle information set, pilot gate completeness, and confirmation isolation.
