import pytest
import torch

from paper10_geojepa_mpc.models.pcc_geojepa import (
    PCCGeoJEPAMember,
    summarize_block_neighbours,
)


def _inputs(n_blocks: int = 4):
    torch.manual_seed(4)
    block = torch.randn(2, n_blocks, 17)
    neighbour = torch.randn(2, n_blocks, 17)
    global_features = torch.randn(2, 12)
    actions = torch.tensor([1, 3]) % n_blocks
    return block, neighbour, global_features, actions


def test_outputs_have_multi_horizon_multi_objective_shapes_and_are_finite():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12, hidden_dim=16)
    block, neighbour, global_features, actions = _inputs()

    output = model(block, neighbour, global_features, actions)

    assert output.horizon_mean.shape == (2, 3, 4)
    assert output.horizon_log_scale.shape == (2, 3, 4)
    assert output.immediate_mean.shape == (2, 4)
    assert output.immediate_log_scale.shape == (2, 4)
    assert output.executable_logit.shape == (2,)
    assert output.next_block.shape == block.shape
    assert output.next_global.shape == global_features.shape
    assert all(torch.isfinite(value).all() for value in output)


def test_action_scores_are_equivariant_to_block_permutation():
    model = PCCGeoJEPAMember(
        block_feature_dim=17,
        k_global=12,
        hidden_dim=16,
    ).eval()
    block, neighbour, global_features, actions = _inputs()
    permutation = torch.tensor([2, 0, 3, 1])
    inverse = torch.argsort(permutation)
    permuted_actions = inverse[actions]

    original = model(block, neighbour, global_features, actions)
    permuted = model(
        block[:, permutation],
        neighbour[:, permutation],
        global_features,
        permuted_actions,
    )

    torch.testing.assert_close(original.horizon_mean, permuted.horizon_mean)
    torch.testing.assert_close(original.immediate_mean, permuted.immediate_mean)
    torch.testing.assert_close(
        original.next_block[:, permutation],
        permuted.next_block,
    )


def test_neighbour_summary_uses_graph_mean_and_zero_for_isolates():
    block = torch.tensor([[1.0], [3.0], [8.0]])
    adjacency = [
        torch.tensor([1]),
        torch.tensor([0, 2]),
        torch.tensor([], dtype=torch.long),
    ]

    summary = summarize_block_neighbours(block, adjacency)

    torch.testing.assert_close(summary, torch.tensor([[3.0], [4.5], [0.0]]))


def test_model_has_no_county_specific_action_embedding_and_changes_space_size():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12)
    assert all("action_emb" not in name for name, _ in model.named_parameters())

    for n_blocks in (4, 7):
        block, neighbour, global_features, actions = _inputs(n_blocks)
        output = model(block, neighbour, global_features, actions)
        assert output.horizon_mean.shape == (2, 3, 4)


def test_checkpoint_round_trip_is_independent_of_action_space_size():
    source = PCCGeoJEPAMember(block_feature_dim=17, k_global=12).eval()
    restored = PCCGeoJEPAMember(block_feature_dim=17, k_global=12).eval()
    restored.load_state_dict(source.state_dict())

    block, neighbour, global_features, actions = _inputs(n_blocks=7)
    expected = source(block, neighbour, global_features, actions)
    observed = restored(block, neighbour, global_features, actions)

    torch.testing.assert_close(expected.horizon_mean, observed.horizon_mean)
    torch.testing.assert_close(expected.executable_logit, observed.executable_logit)


def test_neighbour_features_change_objective_predictions():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12).eval()
    block, neighbour, global_features, actions = _inputs()

    original = model(block, neighbour, global_features, actions)
    changed = model(block, neighbour + 5.0, global_features, actions)

    assert not torch.allclose(original.horizon_mean, changed.horizon_mean)


def test_transition_head_changes_only_the_selected_block():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12).eval()
    block, neighbour, global_features, actions = _inputs()

    output = model(block, neighbour, global_features, actions)

    for row, action in enumerate(actions.tolist()):
        unchanged = torch.ones(block.shape[1], dtype=torch.bool)
        unchanged[action] = False
        torch.testing.assert_close(
            output.next_block[row, unchanged],
            block[row, unchanged],
        )


def test_forward_rejects_out_of_range_action():
    model = PCCGeoJEPAMember(block_feature_dim=17, k_global=12)
    block, neighbour, global_features, actions = _inputs()
    actions[0] = block.shape[1]

    with pytest.raises(ValueError, match="action index"):
        model(block, neighbour, global_features, actions)
