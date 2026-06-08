import numpy as np
import pytest
import torch

from paper10_geojepa_mpc.models.geojepa_transition_model import GeoJEPATransitionModel
from paper10_geojepa_mpc.planning.paper9_adapter import TorchModelMPCAdapter
from paper10_geojepa_mpc.planning.value_filter_selector import (
    value_filter_mpc_select_action,
)


class RewardValueModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward_lookup = torch.tensor([0.0, 5.0, 100.0], device=action.device)
        value_lookup = torch.tensor([10.0, 9.0, 1.0], device=action.device)
        reward = reward_lookup[action.long()].unsqueeze(-1)
        value = value_lookup[action.long()].unsqueeze(-1)
        return block_features, global_features, reward, {"value": value}


class RewardAdapter:
    def __init__(self):
        self.model = RewardValueModel()
        self.device = torch.device("cpu")

    def batch_predict(self, block_features, global_features, actions):
        bf = np.asarray(block_features, dtype=np.float32)
        gf = np.asarray(global_features, dtype=np.float32)
        action_array = np.asarray(actions, dtype=np.int64)
        reward_lookup = np.asarray([0.0, 5.0, 100.0], dtype=np.float32)
        return bf.copy(), gf.copy(), reward_lookup[action_array], {}


class TieRewardValueModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward_lookup = torch.tensor([1.0, 0.0, 10.0], device=action.device)
        value_lookup = torch.tensor([10.0, 9.0, 0.0], device=action.device)
        reward = reward_lookup[action.long()].unsqueeze(-1)
        value = value_lookup[action.long()].unsqueeze(-1)
        return block_features, global_features, reward, {"value": value}


class TieRewardAdapter:
    def __init__(self):
        self.model = TieRewardValueModel()
        self.device = torch.device("cpu")

    def batch_predict(self, block_features, global_features, actions):
        bf = np.asarray(block_features, dtype=np.float32)
        gf = np.asarray(global_features, dtype=np.float32)
        action_array = np.asarray(actions, dtype=np.int64)
        reward_lookup = np.asarray([1.0, 0.0, 10.0], dtype=np.float32)
        return bf.copy(), gf.copy(), reward_lookup[action_array], {}


class FixedChoiceRng:
    def choice(self, valid_actions, size, replace=True):
        values = np.asarray([2, 0, 1], dtype=np.int64)
        return values[:size]


class FirstActionRng:
    def choice(self, valid_actions, size=None, replace=True):
        if size is None:
            return int(np.asarray(valid_actions, dtype=np.int64)[0])
        return np.full(size, int(np.asarray(valid_actions, dtype=np.int64)[0]), dtype=np.int64)


def test_value_filter_selects_best_reward_only_inside_value_topk():
    block_features = np.zeros((3, 17), dtype=np.float32)
    global_features = np.zeros(12, dtype=np.float32)
    action_mask = np.asarray([True, True, True])

    action, info = value_filter_mpc_select_action(
        RewardAdapter(),
        block_features,
        global_features,
        action_mask,
        horizon=1,
        top_k=2,
        gamma=0.99,
        scoring="reward",
        candidate_score_mode="value",
        rng=np.random.default_rng(0),
    )

    assert action == 1
    assert info["selector"] == "value_filter"
    assert info["candidate_score_mode"] == "value"
    assert info["n_candidates"] == 2
    assert info["best_cumrew"] == 5.0
    assert info["score_time_sec"] >= 0.0
    assert info["first_step_time_sec"] >= 0.0
    assert info["rollout_time_sec"] >= 0.0


def test_value_filter_can_stabilize_candidate_order_before_random_rollout():
    block_features = np.zeros((3, 17), dtype=np.float32)
    global_features = np.zeros(12, dtype=np.float32)
    action_mask = np.asarray([True, True, True])
    kwargs = dict(
        adapter=TieRewardAdapter(),
        block_features=block_features,
        global_features=global_features,
        action_mask=action_mask,
        horizon=2,
        top_k=2,
        gamma=1.0,
        scoring="reward",
        candidate_score_mode="value",
        rng=FixedChoiceRng(),
    )

    unstable_action, unstable_info = value_filter_mpc_select_action(
        **kwargs,
        stable_candidate_order=False,
    )
    stable_action, stable_info = value_filter_mpc_select_action(
        **kwargs,
        stable_candidate_order=True,
    )

    assert unstable_action == 1
    assert unstable_info["stable_candidate_order"] is False
    assert stable_action == 0
    assert stable_info["stable_candidate_order"] is True


def test_value_filter_can_use_common_random_continuation_for_all_candidates():
    block_features = np.zeros((3, 17), dtype=np.float32)
    global_features = np.zeros(12, dtype=np.float32)
    action_mask = np.asarray([True, True, True])
    kwargs = dict(
        adapter=TieRewardAdapter(),
        block_features=block_features,
        global_features=global_features,
        action_mask=action_mask,
        horizon=2,
        top_k=2,
        gamma=1.0,
        scoring="reward",
        candidate_score_mode="value",
    )

    independent_action, independent_info = value_filter_mpc_select_action(
        **kwargs,
        rng=FixedChoiceRng(),
        random_continuation_mode="independent",
    )
    common_action, common_info = value_filter_mpc_select_action(
        **kwargs,
        rng=FirstActionRng(),
        random_continuation_mode="common",
    )

    assert independent_action == 1
    assert independent_info["random_continuation_mode"] == "independent"
    assert common_action == 0
    assert common_info["random_continuation_mode"] == "common"


def test_geojepa_fast_path_matches_fallback_action_and_score():
    torch.manual_seed(0)
    model = GeoJEPATransitionModel(n_blocks=6, k_global=12, hidden_dim=8)
    adapter = TorchModelMPCAdapter(model, n_blocks=6, device="cpu", score_mode="reward")
    block_features = np.random.default_rng(0).normal(size=(6, 17)).astype(np.float32)
    global_features = np.random.default_rng(1).normal(size=12).astype(np.float32)
    action_mask = np.asarray([True, True, True, True, True, True])
    kwargs = dict(
        adapter=adapter,
        block_features=block_features,
        global_features=global_features,
        action_mask=action_mask,
        horizon=3,
        top_k=4,
        gamma=0.99,
        scoring="reward",
        candidate_score_mode="blend",
        candidate_value_weight=0.1,
    )

    fallback_action, fallback_info = value_filter_mpc_select_action(
        **kwargs,
        rng=np.random.default_rng(2),
        use_geojepa_fast_path=False,
    )
    fast_action, fast_info = value_filter_mpc_select_action(
        **kwargs,
        rng=np.random.default_rng(2),
        use_geojepa_fast_path=True,
    )

    assert fast_action == fallback_action
    assert fast_info["fast_path"] == "geojepa_state_rollout"
    assert fast_info["best_cumrew"] == pytest.approx(fallback_info["best_cumrew"])
