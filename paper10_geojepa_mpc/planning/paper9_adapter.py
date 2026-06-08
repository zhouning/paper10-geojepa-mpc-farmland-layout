from pathlib import Path

import numpy as np
import torch

from paper10_geojepa_mpc.planning.scoring import scalar_score_from_model_output


class TorchModelMPCAdapter:
    def __init__(
        self,
        model,
        n_blocks: int,
        device: str = "cpu",
        path: str | None = None,
        score_mode: str = "reward",
        value_weight: float = 0.5,
    ):
        self.model = model.to(device)
        self.model.eval()
        self.n_blocks = n_blocks
        self.device = torch.device(device)
        self.n_members = 1
        self.paths = [str(path)] if path is not None else ["torch_model"]
        self.score_mode = score_mode
        self.value_weight = float(value_weight)

    def assert_compatible(self, n_blocks: int) -> None:
        if int(n_blocks) != int(self.n_blocks):
            raise ValueError(f"n_blocks mismatch: adapter={self.n_blocks}, env={n_blocks}")

    def batch_predict(self, block_features, global_features, actions):
        bf = torch.tensor(block_features, device=self.device, dtype=torch.float32)
        gf = torch.tensor(global_features, device=self.device, dtype=torch.float32)
        act = torch.tensor(actions, device=self.device, dtype=torch.long)
        with torch.no_grad():
            next_block, next_global, reward, aux = self.model(bf, gf, act)
            score = scalar_score_from_model_output(
                reward,
                aux,
                score_mode=self.score_mode,
                value_weight=self.value_weight,
            )
        out_aux = {}
        if self.score_mode != "reward":
            out_aux["score_mode"] = self.score_mode
            if self.score_mode == "blend":
                out_aux["value_weight"] = self.value_weight
        return (
            next_block.detach().cpu().numpy().astype(np.float32),
            next_global.detach().cpu().numpy().astype(np.float32),
            score.squeeze(-1).detach().cpu().numpy().astype(np.float32),
            out_aux,
        )


class TorchCheckpointMPCAdapter(TorchModelMPCAdapter):
    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: str | Path,
        device: str = "cpu",
        score_mode: str = "reward",
        value_weight: float = 0.5,
    ):
        from paper10_geojepa_mpc.training.e0_training import load_e0_checkpoint

        model, checkpoint = load_e0_checkpoint(checkpoint_path, device=device)
        return cls(
            model,
            n_blocks=checkpoint["model_kwargs"]["n_blocks"],
            device=device,
            path=str(checkpoint_path),
            score_mode=score_mode,
            value_weight=value_weight,
        )
