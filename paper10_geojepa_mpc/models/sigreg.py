import torch


def sigreg_loss(
    embeddings: torch.Tensor,
    n_projections: int = 128,
    n_knots: int = 32,
    knot_min: float = 0.2,
    knot_max: float = 4.0,
) -> torch.Tensor:
    z = embeddings.reshape(-1, embeddings.shape[-1])
    z = (z - z.mean(dim=0, keepdim=True)) / z.std(
        dim=0, keepdim=True, unbiased=False
    ).clamp_min(1e-6)

    dim = z.shape[-1]
    directions = torch.randn(dim, n_projections, device=z.device, dtype=z.dtype)
    directions = directions / directions.norm(dim=0, keepdim=True).clamp_min(1e-6)

    projected = z @ directions
    knots = torch.linspace(knot_min, knot_max, n_knots, device=z.device, dtype=z.dtype)
    values = projected.unsqueeze(-1) * knots

    empirical_real = torch.cos(values).mean(dim=0)
    empirical_imag = torch.sin(values).mean(dim=0)
    target = torch.exp(-0.5 * knots.square()).unsqueeze(0)

    return ((empirical_real - target).square() + empirical_imag.square()).mean()
