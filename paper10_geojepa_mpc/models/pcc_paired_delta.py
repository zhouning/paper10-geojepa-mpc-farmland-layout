import copy
from typing import NamedTuple

import torch
import torch.nn as nn

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


HORIZONS = (1, 3, 5)


class PairedDeltaOutput(NamedTuple):
    delta_mean: torch.Tensor
    delta_log_scale: torch.Tensor
    candidate_absolute_mean: torch.Tensor
    candidate_absolute_log_scale: torch.Tensor
    executable_logit: torch.Tensor
    candidate_latent: torch.Tensor
    reference_latent: torch.Tensor


class ActionRelativeEncoder(nn.Module):
    def __init__(
        self,
        block_feature_dim: int,
        global_feature_dim: int,
        hidden_dim: int,
    ) -> None:
        super().__init__()
        self.block_encoder = nn.Sequential(
            nn.Linear(block_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.ReLU(),
        )
        self.neighbour_encoder = copy.deepcopy(self.block_encoder)
        self.global_encoder = nn.Sequential(
            nn.Linear(global_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.ReLU(),
        )
        self.projector = nn.Sequential(
            nn.Linear(hidden_dim * 6, 128),
            nn.ReLU(),
            nn.Linear(128, hidden_dim * 2),
        )

    def forward(
        self,
        block: torch.Tensor,
        neighbour: torch.Tensor,
        global_features: torch.Tensor,
        actions: torch.Tensor,
    ) -> torch.Tensor:
        actions = actions.long().reshape(-1)
        batch = block.shape[0]
        rows = torch.arange(batch, device=block.device)
        encoded = self.block_encoder(block)
        neighbour_encoded = self.neighbour_encoder(neighbour)
        selected = encoded[rows, actions]
        selected_neighbour = neighbour_encoded[rows, actions]
        county_mean = encoded.mean(dim=1)
        context = torch.cat(
            [
                selected,
                selected_neighbour,
                selected - county_mean,
                county_mean,
                encoded.max(dim=1).values,
                self.global_encoder(global_features),
            ],
            dim=-1,
        )
        return self.projector(context)


class PCCPairedDeltaMember(nn.Module):
    def __init__(
        self,
        block_feature_dim: int,
        global_feature_dim: int,
        hidden_dim: int = 32,
        ema_decay: float = 0.99,
    ) -> None:
        super().__init__()
        self.ema_decay = float(ema_decay)
        self.online_encoder = ActionRelativeEncoder(
            block_feature_dim,
            global_feature_dim,
            hidden_dim,
        )
        self.target_encoder = copy.deepcopy(self.online_encoder)
        self.target_encoder.requires_grad_(False)

        latent_dim = hidden_dim * 2
        self.jepa_predictor = nn.Sequential(
            nn.Linear(latent_dim, latent_dim),
            nn.ReLU(),
            nn.Linear(latent_dim, latent_dim),
        )
        self.paired_trunk = nn.Sequential(
            nn.Linear(latent_dim * 4, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
        )
        self.delta_head = nn.Linear(
            128,
            len(HORIZONS) * 2 * len(OBJECTIVE_NAMES),
        )
        self.absolute_head = nn.Linear(
            latent_dim,
            2 * len(OBJECTIVE_NAMES),
        )
        self.executable_head = nn.Linear(latent_dim, 1)

    @torch.no_grad()
    def encode_target(
        self,
        block: torch.Tensor,
        neighbour: torch.Tensor,
        global_features: torch.Tensor,
        actions: torch.Tensor,
    ) -> torch.Tensor:
        return self.target_encoder(
            block,
            neighbour,
            global_features,
            actions,
        )

    @torch.no_grad()
    def update_target_encoder(self) -> None:
        online_parameters = dict(self.online_encoder.named_parameters())
        for name, target in self.target_encoder.named_parameters():
            target.mul_(self.ema_decay).add_(
                online_parameters[name],
                alpha=1.0 - self.ema_decay,
            )
        online_buffers = dict(self.online_encoder.named_buffers())
        for name, target in self.target_encoder.named_buffers():
            target.copy_(online_buffers[name])

    def forward(
        self,
        block: torch.Tensor,
        neighbour: torch.Tensor,
        global_features: torch.Tensor,
        candidate_actions: torch.Tensor,
        reference_actions: torch.Tensor,
    ) -> PairedDeltaOutput:
        candidate_latent = self.online_encoder(
            block,
            neighbour,
            global_features,
            candidate_actions,
        )
        reference_latent = self.online_encoder(
            block,
            neighbour,
            global_features,
            reference_actions,
        )
        signed_difference = candidate_latent - reference_latent
        paired = self.paired_trunk(
            torch.cat(
                [
                    candidate_latent,
                    reference_latent,
                    signed_difference,
                    signed_difference.abs(),
                ],
                dim=-1,
            )
        )
        batch = block.shape[0]
        delta = self.delta_head(paired).reshape(
            batch,
            len(HORIZONS),
            2,
            len(OBJECTIVE_NAMES),
        )
        absolute = self.absolute_head(candidate_latent).reshape(
            batch,
            2,
            len(OBJECTIVE_NAMES),
        )
        return PairedDeltaOutput(
            delta_mean=delta[:, :, 0],
            delta_log_scale=delta[:, :, 1].clamp(-8.0, 5.0),
            candidate_absolute_mean=absolute[:, 0],
            candidate_absolute_log_scale=absolute[:, 1].clamp(-8.0, 5.0),
            executable_logit=self.executable_head(candidate_latent).squeeze(-1),
            candidate_latent=candidate_latent,
            reference_latent=reference_latent,
        )
