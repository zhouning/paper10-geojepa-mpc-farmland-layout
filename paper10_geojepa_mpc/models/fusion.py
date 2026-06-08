import torch
import torch.nn as nn


class GatedFeatureFusion(nn.Module):
    def __init__(self, engineered_dim: int, geofm_dim: int, hidden_dim: int):
        super().__init__()
        self.engineered_encoder = nn.Sequential(
            nn.Linear(engineered_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.geofm_encoder = nn.Sequential(
            nn.Linear(geofm_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.gate = nn.Sequential(
            nn.Linear(engineered_dim + geofm_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, engineered: torch.Tensor, geofm: torch.Tensor):
        if engineered.shape[:-1] != geofm.shape[:-1]:
            raise ValueError("engineered and geofm features must share batch/block axes")

        h_engineered = self.engineered_encoder(engineered)
        h_geofm = self.geofm_encoder(geofm)
        gate = self.gate(torch.cat([engineered, geofm], dim=-1))
        return gate * h_engineered + (1.0 - gate) * h_geofm, gate
