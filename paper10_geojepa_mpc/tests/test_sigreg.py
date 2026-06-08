import torch

from paper10_geojepa_mpc.models.sigreg import sigreg_loss


def test_sigreg_loss_is_scalar_and_nonnegative():
    z = torch.randn(32, 16)

    loss = sigreg_loss(z, n_projections=32, n_knots=16)

    assert loss.ndim == 0
    assert torch.isfinite(loss)
    assert loss.item() >= 0.0


def test_sigreg_loss_accepts_sequence_latents():
    z = torch.randn(4, 8, 12)

    loss = sigreg_loss(z, n_projections=16, n_knots=8)

    assert loss.ndim == 0
    assert torch.isfinite(loss)
