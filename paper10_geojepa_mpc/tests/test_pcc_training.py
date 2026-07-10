from pathlib import Path

import numpy as np
import torch

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    write_label_manifest,
    write_trajectory_artifact,
)
from paper10_geojepa_mpc.models.pcc_geojepa import PCCGeoJEPAMember
from paper10_geojepa_mpc.experiments.run_pcc_train import resolve_ensemble_size
from paper10_geojepa_mpc.training.pcc_training import (
    bootstrap_trajectory_ids,
    compute_robust_objective_scaling,
    heteroscedastic_objective_loss,
    load_pcc_checkpoint,
    pairwise_delta_ranking_loss,
    set_trainable_scope,
    train_pcc_ensemble,
)


def test_bootstrap_samples_complete_trajectories_reproducibly():
    first = bootstrap_trajectory_ids(np.array([1000, 1001, 1002]), seed=5101)
    second = bootstrap_trajectory_ids(np.array([1000, 1001, 1002]), seed=5101)

    assert first.tolist() == second.tolist()
    assert len(first) == 3
    assert set(first.tolist()) <= {1000, 1001, 1002}


def test_objective_loss_rewards_accurate_mean_and_finite_scale():
    target = torch.zeros(2, 3, 4)
    exact = heteroscedastic_objective_loss(
        target,
        torch.zeros_like(target),
        torch.zeros_like(target),
    )
    wrong = heteroscedastic_objective_loss(
        target,
        torch.ones_like(target),
        torch.zeros_like(target),
    )

    assert torch.isfinite(exact)
    assert exact < wrong


def test_pairwise_loss_prefers_correct_candidate_reference_order():
    target_delta = torch.tensor([[[2.0, -1.0]]])
    correct = pairwise_delta_ranking_loss(
        torch.tensor([[[2.0, 0.0]]]),
        torch.tensor([[[0.0, 1.0]]]),
        target_delta,
    )
    reversed_order = pairwise_delta_ranking_loss(
        torch.tensor([[[0.0, 1.0]]]),
        torch.tensor([[[2.0, 0.0]]]),
        target_delta,
    )

    assert correct < reversed_order


def test_robust_scaling_preserves_horizon_and_objective_axes():
    candidate = np.arange(4 * 3 * 4, dtype=np.float32).reshape(4, 3, 4)
    reference = np.zeros_like(candidate)

    scaling = compute_robust_objective_scaling(candidate, reference)

    assert np.asarray(scaling["center"]).shape == (3, 4)
    assert np.asarray(scaling["scale"]).shape == (3, 4)
    assert np.all(np.asarray(scaling["scale"]) > 0.0)


def test_objective_heads_scope_freezes_executable_and_representation_layers():
    model = PCCGeoJEPAMember(block_feature_dim=2, k_global=2, hidden_dim=8)

    trainable = set_trainable_scope(model, "objective_heads")

    assert trainable
    assert all(
        name.startswith("immediate_head.") or name.startswith("horizon_head.")
        for name in trainable
    )
    assert all(
        parameter.requires_grad is (name in trainable)
        for name, parameter in model.named_parameters()
    )


def _fixture_dataset(seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_states, n_candidates, n_blocks = 2, 2, 3
    block = rng.normal(size=(n_states, n_blocks, 2)).astype(np.float32)
    neighbour = rng.normal(size=(n_states, n_blocks, 2)).astype(np.float32)
    global_features = rng.normal(size=(n_states, 2)).astype(np.float32)
    actions = np.asarray([[0, 1], [1, 2]], dtype=np.int64)
    reference_actions = np.zeros(n_states, dtype=np.int64)
    candidate_next_bf = np.repeat(block[:, None], n_candidates, axis=1)
    reference_next_bf = np.repeat(block[:, None], n_candidates, axis=1)
    for state in range(n_states):
        for candidate in range(n_candidates):
            candidate_next_bf[state, candidate, actions[state, candidate]] += 0.1
            reference_next_bf[state, candidate, reference_actions[state]] += 0.05
    candidate_next_gf = np.repeat(
        global_features[:, None], n_candidates, axis=1
    ) + 0.01
    reference_next_gf = np.repeat(
        global_features[:, None], n_candidates, axis=1
    ) + 0.005
    objective = rng.normal(size=(n_states, n_candidates, 3, 4)).astype(np.float32)
    reference = rng.normal(size=(n_states, n_candidates, 3, 4)).astype(np.float32)
    return {
        "states_bf": block,
        "states_neighbor_bf": neighbour,
        "states_gf": global_features,
        "actions": actions,
        "objective_returns": objective,
        "reference_actions": reference_actions,
        "reference_objective_returns": reference,
        "candidate_next_bf": candidate_next_bf.astype(np.float32),
        "candidate_next_gf": candidate_next_gf.astype(np.float32),
        "reference_next_bf": reference_next_bf.astype(np.float32),
        "reference_next_gf": reference_next_gf.astype(np.float32),
        "executable_targets": np.asarray([[1.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        "continuation_seeds": np.full((n_states, n_candidates), seed, dtype=np.uint64),
        "trajectory_ids": np.full(n_states, seed, dtype=np.int64),
        "state_steps": np.arange(n_states, dtype=np.int64),
        "horizons": np.asarray([1, 3, 5], dtype=np.int64),
    }


def _fixture_manifest(tmp_path: Path) -> Path:
    artifacts = []
    for seed in (1000, 1001):
        artifacts.append(
            write_trajectory_artifact(tmp_path, seed, _fixture_dataset(seed))
        )
    write_label_manifest(
        tmp_path,
        protocol_id="fixture",
        partition="train",
        artifacts=artifacts,
        continuation_policy={"name": "fixture"},
        horizons=(1, 3, 5),
    )
    return tmp_path / "manifest.json"


def test_tiny_ensemble_training_saves_reloadable_checkpoint(tmp_path):
    manifest = _fixture_manifest(tmp_path / "labels")
    output_dir = tmp_path / "checkpoints"

    paths = train_pcc_ensemble(
        labels_manifest=manifest,
        model_seed=5101,
        ensemble_size=1,
        epochs=1,
        batch_size=4,
        learning_rate=1e-3,
        device="cpu",
        output_dir=output_dir,
        hidden_dim=8,
    )

    assert len(paths) == 1
    model, checkpoint = load_pcc_checkpoint(paths[0], device="cpu")
    assert checkpoint["model_class"] == "PCCGeoJEPAMember"
    assert checkpoint["model_seed"] == 5101
    assert len(checkpoint["bootstrap_trajectory_ids"]) == 2
    block = torch.randn(1, 5, 2)
    neighbour = torch.randn(1, 5, 2)
    output = model(block, neighbour, torch.randn(1, 2), torch.tensor([4]))
    assert output.horizon_mean.shape == (1, 3, 4)


def test_frozen_ensemble_size_cannot_be_reselected_for_adaptation():
    registry = {
        "status": "frozen",
        "selected_config": {"ensemble_size": 5},
    }

    assert resolve_ensemble_size(registry, None, from_frozen=True) == 5


def test_ensemble_members_use_distinct_seeds_and_bootstrap_membership(tmp_path):
    manifest = _fixture_manifest(tmp_path / "labels")

    paths = train_pcc_ensemble(
        labels_manifest=manifest,
        model_seed=5101,
        ensemble_size=2,
        epochs=1,
        batch_size=4,
        learning_rate=0.0,
        device="cpu",
        output_dir=tmp_path / "checkpoints",
        hidden_dim=8,
    )
    checkpoints = [load_pcc_checkpoint(path, device="cpu")[1] for path in paths]

    assert checkpoints[0]["member_seed"] != checkpoints[1]["member_seed"]
    assert (
        checkpoints[0]["bootstrap_trajectory_ids"]
        != checkpoints[1]["bootstrap_trajectory_ids"]
    )
