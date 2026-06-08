import numpy as np
import torch

from paper10_geojepa_mpc.models.geojepa_transition_model import GeoJEPATransitionModel
from paper10_geojepa_mpc.training.e0_training import (
    evaluate_candidate_action_metrics,
    evaluate_pairwise_rank_accuracy,
    load_e0_checkpoint,
    pairwise_ranking_loss_for_batch,
    train_e0_smoke_config,
    transition_mse_loss,
)


def _transition_tensors(n_samples=8, n_blocks=4):
    torch.manual_seed(7)
    block_features = torch.randn(n_samples, n_blocks, 17)
    global_features = torch.randn(n_samples, 12)
    actions = torch.arange(n_samples) % n_blocks
    rewards = torch.randn(n_samples, 1)
    next_block_features = block_features.clone()
    for row, action in enumerate(actions):
        next_block_features[row, action] = next_block_features[row, action] + 0.05
    next_global_features = global_features + 0.02
    return (
        block_features,
        global_features,
        actions,
        rewards,
        next_block_features,
        next_global_features,
    )


def test_transition_mse_loss_returns_finite_scalar_and_metrics():
    model = GeoJEPATransitionModel(n_blocks=4, k_global=12)
    batch = _transition_tensors()

    loss, metrics = transition_mse_loss(model, *batch)

    assert loss.ndim == 0
    assert torch.isfinite(loss)
    assert set(metrics) == {"block_mse", "global_mse", "reward_mse"}


def test_pairwise_ranking_loss_for_batch_returns_loss_and_accuracy():
    model = GeoJEPATransitionModel(n_blocks=4, k_global=12)
    block_features = torch.randn(5, 4, 17)
    global_features = torch.randn(5, 12)
    actions = torch.tensor(
        [
            [0, 1, 2],
            [1, 2, 3],
            [0, 2, 3],
            [0, 1, 3],
            [0, 1, 2],
        ]
    )
    rewards = torch.tensor(
        [
            [3.0, 2.0, 1.0],
            [1.0, 3.0, 2.0],
            [2.0, 1.0, 3.0],
            [0.0, 1.0, 2.0],
            [1.0, 1.0, 2.0],
        ]
    )

    loss, accuracy = pairwise_ranking_loss_for_batch(
        model, block_features, global_features, actions, rewards, n_pairs=4
    )

    assert loss.ndim == 0
    assert torch.isfinite(loss)
    assert 0.0 <= accuracy <= 1.0


def test_evaluate_pairwise_rank_accuracy_is_deterministic_with_seed():
    model = GeoJEPATransitionModel(n_blocks=4, k_global=12)
    block_features = torch.randn(5, 4, 17)
    global_features = torch.randn(5, 12)
    actions = torch.tensor(
        [
            [0, 1, 2, 3],
            [0, 1, 2, 3],
            [0, 1, 2, 3],
            [0, 1, 2, 3],
            [0, 1, 2, 3],
        ]
    )
    rewards = torch.randn(5, 4)

    acc_1 = evaluate_pairwise_rank_accuracy(
        model,
        block_features,
        global_features,
        actions,
        rewards,
        max_states=5,
        n_pairs=12,
        eval_seed=123,
    )
    acc_2 = evaluate_pairwise_rank_accuracy(
        model,
        block_features,
        global_features,
        actions,
        rewards,
        max_states=5,
        n_pairs=12,
        eval_seed=123,
    )

    assert acc_1 == acc_2


def test_evaluate_candidate_action_metrics_reports_topk_regret():
    class ActionIdRewardModel(torch.nn.Module):
        def forward(self, block_features, global_features, action, geofm_features=None):
            reward = action.float().unsqueeze(-1)
            return block_features, global_features, reward, {"latent": reward}

    model = ActionIdRewardModel()
    block_features = torch.zeros(2, 4, 17)
    global_features = torch.zeros(2, 12)
    actions = torch.tensor([[0, 1, 2], [0, 1, 2]])
    rewards = torch.tensor([[0.0, 1.0, 2.0], [2.0, 1.0, 0.0]])

    metrics = evaluate_candidate_action_metrics(
        model,
        block_features,
        global_features,
        actions,
        rewards,
        top_k=2,
        batch_states=1,
    )

    assert metrics["candidate_top1_hit_rate"] == 0.5
    assert metrics["candidate_top2_hit_rate"] == 0.5
    assert metrics["candidate_top1_regret"] == 1.0
    assert metrics["candidate_top2_regret"] == 0.5


def test_train_e0_smoke_config_runs_one_epoch_on_tiny_npz(tmp_path):
    rng = np.random.default_rng(11)
    n_samples = 12
    n_states = 6
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    pairwise_path = tmp_path / "pairwise.npz"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = rng.normal(size=n_samples).astype("float32")
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.05
    next_global_features = (global_features + 0.02).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )

    states_bf = rng.normal(size=(n_states, n_blocks, 17)).astype("float32")
    states_gf = rng.normal(size=(n_states, 12)).astype("float32")
    pair_actions = np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1))
    pair_rewards = rng.normal(size=(n_states, n_blocks)).astype("float32")
    np.savez(
        pairwise_path,
        states_bf=states_bf,
        states_gf=states_gf,
        actions=pair_actions,
        rewards=pair_rewards,
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=pairwise_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=1,
        batch_size=4,
        lambda_rank=0.1,
        lambda_sig=0.01,
        n_pairs=2,
        max_transition_samples=8,
        max_pairwise_states=4,
        compute_candidate_metrics=True,
        candidate_top_k=2,
        candidate_batch_states=2,
        candidate_max_states=4,
        seed=13,
        device="cpu",
    )

    assert metrics["epochs"] == 1
    assert metrics["n_transition_samples"] == 8
    assert metrics["n_pairwise_states"] == 4
    assert metrics["candidate_states"] == 4
    assert metrics["candidate_top_k"] == 2
    assert 0.0 <= metrics["candidate_top1_hit_rate"] <= 1.0
    assert metrics["candidate_top1_regret"] >= 0.0
    assert np.isfinite(metrics["final_loss"])
    assert 0.0 <= metrics["ranking_acc"] <= 1.0


def test_train_e0_smoke_config_saves_and_loads_best_checkpoint(tmp_path):
    rng = np.random.default_rng(17)
    n_samples = 10
    n_states = 5
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    pairwise_path = tmp_path / "pairwise.npz"
    checkpoint_path = tmp_path / "best_model.pt"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = rng.normal(size=n_samples).astype("float32")
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.03
    next_global_features = (global_features + 0.01).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )

    np.savez(
        pairwise_path,
        states_bf=rng.normal(size=(n_states, n_blocks, 17)).astype("float32"),
        states_gf=rng.normal(size=(n_states, 12)).astype("float32"),
        actions=np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1)),
        rewards=rng.normal(size=(n_states, n_blocks)).astype("float32"),
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=pairwise_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=2,
        batch_size=5,
        lambda_rank=0.1,
        n_pairs=2,
        compute_candidate_metrics=True,
        candidate_top_k=2,
        candidate_batch_states=2,
        checkpoint_path=checkpoint_path,
        checkpoint_metric="candidate_top2_regret",
        checkpoint_mode="min",
        seed=19,
        device="cpu",
    )

    assert checkpoint_path.exists()
    assert metrics["checkpoint_path"] == str(checkpoint_path)
    assert 1 <= metrics["best_checkpoint_epoch"] <= 2

    model, checkpoint = load_e0_checkpoint(checkpoint_path, device="cpu")
    assert checkpoint["model_kwargs"]["n_blocks"] == n_blocks
    block_batch = torch.randn(2, n_blocks, 17)
    global_batch = torch.randn(2, 12)
    action_batch = torch.tensor([0, 3])

    next_block, next_global, reward, aux = model(block_batch, global_batch, action_batch)

    assert next_block.shape == block_batch.shape
    assert next_global.shape == global_batch.shape
    assert reward.shape == (2, 1)
    assert aux["latent"].shape[0] == 2


def test_train_e0_smoke_config_accepts_returns_pairwise_labels(tmp_path):
    rng = np.random.default_rng(23)
    n_samples = 8
    n_states = 4
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    value_path = tmp_path / "value_labels.npz"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = rng.normal(size=n_samples).astype("float32")
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.02
    next_global_features = (global_features + 0.01).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )

    pair_actions = np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1))
    returns = np.tile(
        np.asarray([0.0, 1.0, 3.0, 2.0], dtype=np.float32), (n_states, 1)
    )
    np.savez(
        value_path,
        states_bf=rng.normal(size=(n_states, n_blocks, 17)).astype("float32"),
        states_gf=rng.normal(size=(n_states, 12)).astype("float32"),
        actions=pair_actions,
        returns=returns,
        one_step_rewards=(returns - 0.5).astype("float32"),
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=value_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=1,
        batch_size=4,
        lambda_rank=0.1,
        n_pairs=2,
        max_transition_samples=8,
        max_pairwise_states=4,
        compute_candidate_metrics=True,
        candidate_top_k=2,
        candidate_batch_states=2,
        seed=29,
        device="cpu",
    )

    assert metrics["pairwise_label_key"] == "returns"
    assert metrics["n_pairwise_states"] == 4
    assert metrics["candidate_states"] == 4
    assert np.isfinite(metrics["final_loss"])


def test_train_e0_smoke_config_can_initialize_from_checkpoint(tmp_path):
    rng = np.random.default_rng(31)
    n_samples = 8
    n_states = 4
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    pairwise_path = tmp_path / "pairwise.npz"
    init_checkpoint_path = tmp_path / "init.pt"
    output_checkpoint_path = tmp_path / "fine_tuned.pt"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = rng.normal(size=n_samples).astype("float32")
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.01
    next_global_features = (global_features + 0.01).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )
    np.savez(
        pairwise_path,
        states_bf=rng.normal(size=(n_states, n_blocks, 17)).astype("float32"),
        states_gf=rng.normal(size=(n_states, 12)).astype("float32"),
        actions=np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1)),
        rewards=rng.normal(size=(n_states, n_blocks)).astype("float32"),
    )

    init_model = GeoJEPATransitionModel(n_blocks=n_blocks, k_global=12)
    init_state = {}
    for idx, (name, value) in enumerate(init_model.state_dict().items()):
        init_state[name] = torch.full_like(value, fill_value=(idx + 1) * 0.001)
    init_model.load_state_dict(init_state)
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": {
                "n_blocks": n_blocks,
                "k_global": 12,
                "block_feature_dim": 17,
            },
            "state_dict": init_model.state_dict(),
            "epoch": 3,
            "checkpoint_metric": "ranking_acc",
            "checkpoint_value": 0.5,
            "metrics": {"ranking_acc": 0.5},
        },
        init_checkpoint_path,
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=pairwise_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=1,
        batch_size=4,
        lr=0.0,
        lambda_rank=0.1,
        n_pairs=2,
        checkpoint_path=output_checkpoint_path,
        checkpoint_metric="ranking_acc",
        checkpoint_mode="max",
        init_checkpoint_path=init_checkpoint_path,
        seed=37,
        device="cpu",
    )

    loaded, checkpoint = load_e0_checkpoint(output_checkpoint_path, device="cpu")

    assert metrics["init_checkpoint_path"] == str(init_checkpoint_path)
    assert checkpoint["init_checkpoint_path"] == str(init_checkpoint_path)
    for name, expected in init_state.items():
        torch.testing.assert_close(loaded.state_dict()[name], expected)


def test_train_e0_smoke_config_can_freeze_all_but_reward_head(tmp_path):
    rng = np.random.default_rng(41)
    n_samples = 10
    n_states = 5
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    pairwise_path = tmp_path / "pairwise.npz"
    init_checkpoint_path = tmp_path / "init.pt"
    output_checkpoint_path = tmp_path / "reward_head_only.pt"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = np.linspace(5.0, 10.0, n_samples, dtype=np.float32)
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.01
    next_global_features = (global_features + 0.01).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )
    np.savez(
        pairwise_path,
        states_bf=rng.normal(size=(n_states, n_blocks, 17)).astype("float32"),
        states_gf=rng.normal(size=(n_states, 12)).astype("float32"),
        actions=np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1)),
        rewards=np.tile(
            np.asarray([0.0, 1.0, 3.0, 2.0], dtype=np.float32),
            (n_states, 1),
        ),
    )

    torch.manual_seed(41)
    init_model = GeoJEPATransitionModel(n_blocks=n_blocks, k_global=12)
    init_state = {name: value.detach().clone() for name, value in init_model.state_dict().items()}
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": {
                "n_blocks": n_blocks,
                "k_global": 12,
                "block_feature_dim": 17,
            },
            "state_dict": init_state,
            "epoch": 1,
            "checkpoint_metric": "ranking_acc",
            "checkpoint_value": 0.5,
            "metrics": {"ranking_acc": 0.5},
        },
        init_checkpoint_path,
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=pairwise_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=1,
        batch_size=5,
        lr=1e-2,
        lambda_rank=1.0,
        n_pairs=4,
        checkpoint_path=output_checkpoint_path,
        checkpoint_metric="ranking_acc",
        checkpoint_mode="max",
        init_checkpoint_path=init_checkpoint_path,
        trainable_scope="reward_head",
        seed=43,
        device="cpu",
    )

    loaded, checkpoint = load_e0_checkpoint(output_checkpoint_path, device="cpu")
    state = loaded.state_dict()
    reward_changed = []
    for name, initial_value in init_state.items():
        changed = not torch.equal(state[name], initial_value)
        if name.startswith("reward_head."):
            reward_changed.append(changed)
        else:
            torch.testing.assert_close(state[name], initial_value)

    assert metrics["trainable_scope"] == "reward_head"
    assert checkpoint["trainable_scope"] == "reward_head"
    assert any(reward_changed)


def test_load_e0_checkpoint_initializes_missing_value_head_from_reward_head(tmp_path):
    n_blocks = 4
    checkpoint_path = tmp_path / "legacy.pt"
    torch.manual_seed(47)
    init_model = GeoJEPATransitionModel(n_blocks=n_blocks, k_global=12)
    legacy_state = {
        name: value.detach().clone()
        for name, value in init_model.state_dict().items()
        if not name.startswith("value_head.")
    }
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": {
                "n_blocks": n_blocks,
                "k_global": 12,
                "block_feature_dim": 17,
            },
            "state_dict": legacy_state,
            "epoch": 1,
            "checkpoint_metric": "ranking_acc",
            "checkpoint_value": 0.5,
            "metrics": {"ranking_acc": 0.5},
        },
        checkpoint_path,
    )

    loaded, checkpoint = load_e0_checkpoint(checkpoint_path, device="cpu")
    state = loaded.state_dict()

    assert "value_head.0.weight" in state
    assert checkpoint["missing_state_keys"] == [
        "value_head.0.weight",
        "value_head.0.bias",
        "value_head.2.weight",
        "value_head.2.bias",
    ]
    torch.testing.assert_close(state["value_head.0.weight"], state["reward_head.0.weight"])
    torch.testing.assert_close(state["value_head.0.bias"], state["reward_head.0.bias"])
    torch.testing.assert_close(state["value_head.2.weight"], state["reward_head.2.weight"])
    torch.testing.assert_close(state["value_head.2.bias"], state["reward_head.2.bias"])


def test_train_e0_smoke_config_can_freeze_all_but_value_head(tmp_path):
    rng = np.random.default_rng(53)
    n_samples = 10
    n_states = 5
    n_blocks = 4
    transition_path = tmp_path / "transitions.npz"
    pairwise_path = tmp_path / "value_labels.npz"
    init_checkpoint_path = tmp_path / "init.pt"
    output_checkpoint_path = tmp_path / "value_head_only.pt"

    block_features = rng.normal(size=(n_samples, n_blocks, 17)).astype("float32")
    global_features = rng.normal(size=(n_samples, 12)).astype("float32")
    actions = (np.arange(n_samples) % n_blocks).astype("int64")
    rewards = np.linspace(5.0, 10.0, n_samples, dtype=np.float32)
    next_block_features = block_features.copy()
    next_block_features[np.arange(n_samples), actions, :] += 0.01
    next_global_features = (global_features + 0.01).astype("float32")
    np.savez(
        transition_path,
        block_features=block_features,
        global_features=global_features,
        actions=actions,
        rewards=rewards,
        next_block_features=next_block_features,
        next_global_features=next_global_features,
    )
    np.savez(
        pairwise_path,
        states_bf=rng.normal(size=(n_states, n_blocks, 17)).astype("float32"),
        states_gf=rng.normal(size=(n_states, 12)).astype("float32"),
        actions=np.tile(np.arange(n_blocks, dtype="int64"), (n_states, 1)),
        returns=np.tile(
            np.asarray([0.0, 4.0, 1.0, 2.0], dtype=np.float32),
            (n_states, 1),
        ),
    )

    torch.manual_seed(59)
    init_model = GeoJEPATransitionModel(n_blocks=n_blocks, k_global=12)
    init_state = {
        name: value.detach().clone()
        for name, value in init_model.state_dict().items()
    }
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": {
                "n_blocks": n_blocks,
                "k_global": 12,
                "block_feature_dim": 17,
            },
            "state_dict": init_state,
            "epoch": 1,
            "checkpoint_metric": "ranking_acc",
            "checkpoint_value": 0.5,
            "metrics": {"ranking_acc": 0.5},
        },
        init_checkpoint_path,
    )

    metrics = train_e0_smoke_config(
        transition_path=transition_path,
        pairwise_path=pairwise_path,
        n_blocks=n_blocks,
        k_global=12,
        epochs=1,
        batch_size=5,
        lr=1e-2,
        lambda_rank=1.0,
        n_pairs=4,
        checkpoint_path=output_checkpoint_path,
        checkpoint_metric="ranking_acc",
        checkpoint_mode="max",
        init_checkpoint_path=init_checkpoint_path,
        trainable_scope="value_head",
        rank_score_mode="value",
        seed=61,
        device="cpu",
    )

    loaded, checkpoint = load_e0_checkpoint(output_checkpoint_path, device="cpu")
    state = loaded.state_dict()
    value_changed = []
    for name, initial_value in init_state.items():
        changed = not torch.equal(state[name], initial_value)
        if name.startswith("value_head."):
            value_changed.append(changed)
        else:
            torch.testing.assert_close(state[name], initial_value)

    assert metrics["trainable_scope"] == "value_head"
    assert metrics["rank_score_mode"] == "value"
    assert checkpoint["trainable_scope"] == "value_head"
    assert checkpoint["rank_score_mode"] == "value"
    assert any(value_changed)
