import numpy as np
import torch

from paper10_geojepa_mpc.planning.paper9_adapter import TorchModelMPCAdapter


class ActionIdRewardModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward = action.float().unsqueeze(-1)
        return block_features + 1.0, global_features + 2.0, reward, {"latent": reward}


class ActionIdRewardValueModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward = action.float().unsqueeze(-1)
        value = (10.0 - action.float()).unsqueeze(-1)
        return block_features + 1.0, global_features + 2.0, reward, {"value": value}


def test_torch_model_mpc_adapter_matches_paper9_batch_predict_contract():
    adapter = TorchModelMPCAdapter(ActionIdRewardModel(), n_blocks=4, device="cpu")
    block_features = np.zeros((3, 4, 17), dtype=np.float32)
    global_features = np.zeros((3, 12), dtype=np.float32)
    actions = np.array([2, 0, 3], dtype=np.int64)

    next_block, next_global, rewards, aux = adapter.batch_predict(
        block_features, global_features, actions
    )

    assert next_block.shape == (3, 4, 17)
    assert next_global.shape == (3, 12)
    assert rewards.shape == (3,)
    assert np.array_equal(rewards, np.array([2.0, 0.0, 3.0], dtype=np.float32))
    assert aux == {}


def test_torch_model_mpc_adapter_can_emit_value_scores_as_rewards():
    adapter = TorchModelMPCAdapter(
        ActionIdRewardValueModel(),
        n_blocks=4,
        device="cpu",
        score_mode="value",
    )
    block_features = np.zeros((2, 4, 17), dtype=np.float32)
    global_features = np.zeros((2, 12), dtype=np.float32)
    actions = np.array([2, 7], dtype=np.int64)

    _, _, rewards, aux = adapter.batch_predict(block_features, global_features, actions)

    assert np.array_equal(rewards, np.array([8.0, 3.0], dtype=np.float32))
    assert aux == {"score_mode": "value"}


def test_torch_model_mpc_adapter_can_emit_blended_scores_as_rewards():
    adapter = TorchModelMPCAdapter(
        ActionIdRewardValueModel(),
        n_blocks=4,
        device="cpu",
        score_mode="blend",
        value_weight=0.25,
    )
    block_features = np.zeros((2, 4, 17), dtype=np.float32)
    global_features = np.zeros((2, 12), dtype=np.float32)
    actions = np.array([2, 7], dtype=np.int64)

    _, _, rewards, aux = adapter.batch_predict(block_features, global_features, actions)

    assert np.array_equal(rewards, np.array([3.5, 6.0], dtype=np.float32))
    assert aux == {"score_mode": "blend", "value_weight": 0.25}


def test_torch_model_mpc_adapter_asserts_compatible_block_count():
    adapter = TorchModelMPCAdapter(ActionIdRewardModel(), n_blocks=4, device="cpu")

    adapter.assert_compatible(4)

    try:
        adapter.assert_compatible(5)
    except ValueError as exc:
        assert "n_blocks mismatch" in str(exc)
    else:
        raise AssertionError("expected block-count mismatch")
