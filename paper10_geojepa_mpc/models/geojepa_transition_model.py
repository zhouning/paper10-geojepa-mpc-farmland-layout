from typing import Optional

import torch
import torch.nn as nn

from paper10_geojepa_mpc.models.fusion import GatedFeatureFusion


class GeoJEPATransitionModel(nn.Module):
    def __init__(
        self,
        n_blocks: int,
        n_actions: Optional[int] = None,
        k_global: int = 12,
        block_feature_dim: int = 17,
        hidden_dim: int = 32,
        geofm_dim: Optional[int] = None,
    ):
        super().__init__()
        self.n_blocks = n_blocks
        self.n_actions = n_actions or n_blocks
        self.k_global = k_global
        self.block_feature_dim = block_feature_dim
        self.hidden_dim = hidden_dim
        self.geofm_dim = geofm_dim

        if geofm_dim is None:
            self.block_encoder = nn.Sequential(
                nn.Linear(block_feature_dim, 64),
                nn.ReLU(),
                nn.Linear(64, hidden_dim),
                nn.ReLU(),
            )
            self.fusion = None
        else:
            self.block_encoder = None
            self.fusion = GatedFeatureFusion(block_feature_dim, geofm_dim, hidden_dim)

        self.action_emb = nn.Embedding(self.n_actions, hidden_dim)
        self.global_encoder = nn.Sequential(
            nn.Linear(k_global, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.ReLU(),
        )

        ctx_dim = hidden_dim * 4
        self.block_delta_head = nn.Sequential(
            nn.Linear(ctx_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, block_feature_dim),
        )
        self.global_delta_head = nn.Sequential(
            nn.Linear(ctx_dim, 256),
            nn.ReLU(),
            nn.Linear(256, k_global),
        )
        self.reward_head = nn.Sequential(
            nn.Linear(ctx_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )
        self.value_head = nn.Sequential(
            nn.Linear(ctx_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(
        self,
        block_features: torch.Tensor,
        global_features: torch.Tensor,
        action: torch.Tensor,
        geofm_features: Optional[torch.Tensor] = None,
    ):
        batch_size = block_features.shape[0]
        action = action.long().view(batch_size)

        aux = {}
        if self.fusion is None:
            all_enc = self.block_encoder(block_features)
        else:
            if geofm_features is None:
                raise ValueError("geofm_features is required when geofm_dim is set")
            all_enc, fusion_gate = self.fusion(block_features, geofm_features)
            aux["fusion_gate"] = fusion_gate

        mean_pool = all_enc.mean(dim=1)
        selected_idx = action.unsqueeze(-1).unsqueeze(-1).expand(
            batch_size, 1, self.hidden_dim
        )
        selected_enc = all_enc.gather(1, selected_idx).squeeze(1)
        action_enc = self.action_emb(action)
        global_enc = self.global_encoder(global_features)

        ctx = torch.cat([selected_enc, action_enc, global_enc, mean_pool], dim=-1)
        aux["latent"] = ctx

        block_delta = self.block_delta_head(ctx)
        global_delta = self.global_delta_head(ctx)
        reward = self.reward_head(ctx)
        aux["value"] = self.value_head(ctx)

        next_block = block_features.clone()
        action_idx = action.unsqueeze(-1).unsqueeze(-1).expand(
            batch_size, 1, self.block_feature_dim
        )
        selected_block = next_block.gather(1, action_idx)
        next_block.scatter_(1, action_idx, selected_block + block_delta.unsqueeze(1))

        next_global = global_features + global_delta
        return next_block, next_global, reward, aux
