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
