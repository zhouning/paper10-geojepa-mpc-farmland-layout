import torch

from paper10_geojepa_mpc.models.geojepa_transition_model import GeoJEPATransitionModel
from paper10_geojepa_mpc.planning.scoring import (
    score_candidate_actions,
    select_topk_actions,
)


class ActionIdRewardModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward = action.float().unsqueeze(-1)
        return block_features, global_features, reward, {"latent": reward}


class ActionIdRewardValueModel(torch.nn.Module):
    def forward(self, block_features, global_features, action, geofm_features=None):
        reward = action.float().unsqueeze(-1)
        value = (10.0 - action.float()).unsqueeze(-1)
        return block_features, global_features, reward, {"value": value}


class CountingEncoder(torch.nn.Module):
    def __init__(self, wrapped):
        super().__init__()
        self.wrapped = wrapped
        self.calls = 0
        self.batch_sizes = []

    def forward(self, features):
        self.calls += 1
        self.batch_sizes.append(int(features.shape[0]))
        return self.wrapped(features)


def test_score_candidate_actions_scores_single_state_actions():
    model = ActionIdRewardModel()
    block_features = torch.zeros(4, 17)
    global_features = torch.zeros(12)
    actions = torch.tensor([3, 1, 5])

    scores = score_candidate_actions(model, block_features, global_features, actions)

    assert scores.shape == (3,)
    assert torch.equal(scores, torch.tensor([3.0, 1.0, 5.0]))


def test_score_candidate_actions_scores_batched_state_actions():
    model = ActionIdRewardModel()
    block_features = torch.zeros(2, 4, 17)
    global_features = torch.zeros(2, 12)
    actions = torch.tensor([[0, 2], [1, 3]])

    scores = score_candidate_actions(model, block_features, global_features, actions)

    assert scores.shape == (2, 2)
    assert torch.equal(scores, torch.tensor([[0.0, 2.0], [1.0, 3.0]]))


def test_score_candidate_actions_can_use_value_head_scores():
    model = ActionIdRewardValueModel()
    block_features = torch.zeros(4, 17)
    global_features = torch.zeros(12)
    actions = torch.tensor([3, 1, 5])

    scores = score_candidate_actions(
        model,
        block_features,
        global_features,
        actions,
        score_mode="value",
    )

    assert torch.equal(scores, torch.tensor([7.0, 9.0, 5.0]))


def test_score_candidate_actions_can_blend_reward_and_value_scores():
    model = ActionIdRewardValueModel()
    block_features = torch.zeros(4, 17)
    global_features = torch.zeros(12)
    actions = torch.tensor([3, 1])

    scores = score_candidate_actions(
        model,
        block_features,
        global_features,
        actions,
        score_mode="blend",
        value_weight=0.25,
    )

    assert torch.equal(scores, torch.tensor([4.0, 3.0]))


def test_score_candidate_actions_fast_path_matches_geojepa_forward_for_single_state():
    torch.manual_seed(0)
    model = GeoJEPATransitionModel(n_blocks=8, k_global=12, hidden_dim=16)
    block_features = torch.randn(8, 17)
    global_features = torch.randn(12)
    actions = torch.tensor([0, 3, 5, 7])

    scores = score_candidate_actions(
        model,
        block_features,
        global_features,
        actions,
        score_mode="blend",
        value_weight=0.2,
        max_pairs_per_forward=2,
    )

    repeated_block = block_features.unsqueeze(0).repeat(actions.numel(), 1, 1)
    repeated_global = global_features.unsqueeze(0).repeat(actions.numel(), 1)
    _, _, reward, aux = model(repeated_block, repeated_global, actions)
    expected = 0.8 * reward.squeeze(-1) + 0.2 * aux["value"].squeeze(-1)
    assert torch.allclose(scores, expected)


def test_score_candidate_actions_geojepa_fast_path_encodes_single_state_once():
    torch.manual_seed(0)
    model = GeoJEPATransitionModel(n_blocks=8, k_global=12, hidden_dim=16)
    model.block_encoder = CountingEncoder(model.block_encoder)
    block_features = torch.randn(8, 17)
    global_features = torch.randn(12)
    actions = torch.arange(8)

    score_candidate_actions(
        model,
        block_features,
        global_features,
        actions,
        max_pairs_per_forward=2,
    )

    assert model.block_encoder.calls == 1
    assert model.block_encoder.batch_sizes == [1]


def test_score_candidate_actions_geojepa_fast_path_preserves_batch_size_one_shape():
    torch.manual_seed(0)
    model = GeoJEPATransitionModel(n_blocks=8, k_global=12, hidden_dim=16)
    block_features = torch.randn(1, 8, 17)
    global_features = torch.randn(1, 12)
    actions = torch.tensor([[0, 3, 5]])

    scores = score_candidate_actions(model, block_features, global_features, actions)

    assert scores.shape == (1, 3)


def test_select_topk_actions_returns_sorted_action_ids_and_scores():
    actions = torch.tensor([10, 20, 30, 40])
    scores = torch.tensor([0.2, 0.9, 0.1, 0.5])

    top_actions, top_scores = select_topk_actions(actions, scores, k=2)

    assert torch.equal(top_actions, torch.tensor([20, 40]))
    assert torch.equal(top_scores, torch.tensor([0.9, 0.5]))
