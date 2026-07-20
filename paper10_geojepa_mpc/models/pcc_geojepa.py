from typing import NamedTuple

import torch
import torch.nn as nn

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


HORIZONS = (1, 3, 5)


class PCCModelOutput(NamedTuple):
    next_block: torch.Tensor
    next_global: torch.Tensor
    immediate_mean: torch.Tensor
    immediate_log_scale: torch.Tensor
    horizon_mean: torch.Tensor
    horizon_log_scale: torch.Tensor
    executable_logit: torch.Tensor
    latent: torch.Tensor


def summarize_block_neighbours(
    block_features: torch.Tensor,
    adjacency,
) -> torch.Tensor:
    if block_features.ndim != 2:
        raise ValueError("block_features must have shape [n_blocks, n_features]")
    if len(adjacency) != block_features.shape[0]:
        raise ValueError("adjacency length must equal n_blocks")

    rows = []
    for neighbours in adjacency:
        indexes = torch.as_tensor(
            neighbours,
            dtype=torch.long,
            device=block_features.device,
        ).reshape(-1)
        if indexes.numel() == 0:
            rows.append(torch.zeros_like(block_features[0]))
        else:
            if indexes.min() < 0 or indexes.max() >= block_features.shape[0]:
                raise ValueError("adjacency contains an out-of-range block index")
            rows.append(block_features.index_select(0, indexes).mean(dim=0))
    return torch.stack(rows, dim=0)


class PCCGeoJEPAMember(nn.Module):
    def __init__(
        self,
        block_feature_dim: int,
        k_global: int,
        hidden_dim: int = 32,
        representation: str = "action_relative",
        county_action_count: int | None = None,
    ):
        super().__init__()
        self.block_feature_dim = int(block_feature_dim)
        self.k_global = int(k_global)
        self.hidden_dim = int(hidden_dim)
        self.representation = str(representation)
        self.county_action_count = (
            None if county_action_count is None else int(county_action_count)
        )
        if min(self.block_feature_dim, self.k_global, self.hidden_dim) <= 0:
            raise ValueError("model dimensions must be positive")
        if self.representation not in {
            "action_relative",
            "county_specific_action_embedding",
        }:
            raise ValueError("unknown PCC representation")
        if self.representation == "county_specific_action_embedding":
            if self.county_action_count is None or self.county_action_count <= 0:
                raise ValueError(
                    "county-specific representation requires county_action_count"
                )
            self.action_embedding = nn.Embedding(
                self.county_action_count,
                self.hidden_dim,
            )
        elif self.county_action_count is not None:
            raise ValueError(
                "county_action_count is valid only for county-specific representation"
            )

        self.block_encoder = nn.Sequential(
            nn.Linear(self.block_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, self.hidden_dim),
            nn.ReLU(),
        )
        self.neighbour_encoder = nn.Sequential(
            nn.Linear(self.block_feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, self.hidden_dim),
            nn.ReLU(),
        )
        self.global_encoder = nn.Sequential(
            nn.Linear(self.k_global, 64),
            nn.ReLU(),
            nn.Linear(64, self.hidden_dim),
            nn.ReLU(),
        )

        context_dim = self.hidden_dim * 6
        self.trunk = nn.Sequential(
            nn.Linear(context_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        self.block_delta_head = nn.Linear(128, self.block_feature_dim)
        self.global_delta_head = nn.Linear(128, self.k_global)
        self.immediate_head = nn.Linear(128, 2 * len(OBJECTIVE_NAMES))
        self.horizon_head = nn.Linear(
            128,
            len(HORIZONS) * 2 * len(OBJECTIVE_NAMES),
        )
        self.executable_head = nn.Linear(128, 1)

    def _validate_inputs(
        self,
        block: torch.Tensor,
        neighbour: torch.Tensor,
        global_features: torch.Tensor,
        actions: torch.Tensor,
    ) -> torch.Tensor:
        if block.ndim != 3 or block.shape[-1] != self.block_feature_dim:
            raise ValueError("block must have shape [batch, n_blocks, block_feature_dim]")
        if neighbour.shape != block.shape:
            raise ValueError("neighbour features must match block feature shape")
        if global_features.shape != (block.shape[0], self.k_global):
            raise ValueError("global_features shape is incompatible with the model")
        actions = actions.long().reshape(-1)
        if actions.shape[0] != block.shape[0]:
            raise ValueError("one action index is required per batch row")
        if actions.numel() and (
            int(actions.min()) < 0 or int(actions.max()) >= block.shape[1]
        ):
            raise ValueError("action index is out of range")
        if (
            self.representation == "county_specific_action_embedding"
            and actions.numel()
            and int(actions.max()) >= self.county_action_count
        ):
            raise ValueError("action index exceeds the county action space")
        return actions

    def forward(
        self,
        block: torch.Tensor,
        neighbour: torch.Tensor,
        global_features: torch.Tensor,
        actions: torch.Tensor,
    ) -> PCCModelOutput:
        actions = self._validate_inputs(
            block,
            neighbour,
            global_features,
            actions,
        )
        batch_size = block.shape[0]
        rows = torch.arange(batch_size, device=block.device)

        encoded = self.block_encoder(block)
        neighbour_encoded = self.neighbour_encoder(neighbour)
        selected = encoded[rows, actions]
        if self.representation == "county_specific_action_embedding":
            selected = selected + self.action_embedding(actions)
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
        latent = self.trunk(context)

        next_block = block.clone()
        next_block[rows, actions] = (
            next_block[rows, actions] + self.block_delta_head(latent)
        )
        next_global = global_features + self.global_delta_head(latent)

        immediate = self.immediate_head(latent).reshape(
            batch_size,
            2,
            len(OBJECTIVE_NAMES),
        )
        horizon = self.horizon_head(latent).reshape(
            batch_size,
            len(HORIZONS),
            2,
            len(OBJECTIVE_NAMES),
        )
        return PCCModelOutput(
            next_block=next_block,
            next_global=next_global,
            immediate_mean=immediate[:, 0],
            immediate_log_scale=immediate[:, 1].clamp(-8.0, 5.0),
            horizon_mean=horizon[:, :, 0],
            horizon_log_scale=horizon[:, :, 1].clamp(-8.0, 5.0),
            executable_logit=self.executable_head(latent).squeeze(-1),
            latent=latent,
        )
