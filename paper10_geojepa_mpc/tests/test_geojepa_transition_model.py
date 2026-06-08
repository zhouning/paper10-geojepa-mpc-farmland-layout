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
