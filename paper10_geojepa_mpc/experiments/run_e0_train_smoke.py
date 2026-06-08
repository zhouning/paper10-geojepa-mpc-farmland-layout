import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.training.e0_training import train_e0_smoke_config


SMOKE_TOOL2 = (
    ROOT / "arcgis_toolbox_paper9" / "_scratch" / "tool1_smoke" / "prepared" / "tool2"
)


def main() -> None:
    transition_path = SMOKE_TOOL2 / "transitions.npz"
    pairwise_path = SMOKE_TOOL2 / "pairwise.npz"
    configs = [
        {"name": "mse_only", "lambda_rank": 0.0, "lambda_sig": 0.0},
        {"name": "rank", "lambda_rank": 1.0, "lambda_sig": 0.0},
        {"name": "rank_sigreg", "lambda_rank": 1.0, "lambda_sig": 0.01},
    ]

    results = []
    for config in configs:
        metrics = train_e0_smoke_config(
            transition_path=transition_path,
            pairwise_path=pairwise_path,
            n_blocks=30,
            k_global=12,
            epochs=3,
            batch_size=64,
            lambda_rank=config["lambda_rank"],
            lambda_sig=config["lambda_sig"],
            n_pairs=4,
            pairwise_subsample=32,
            seed=2026,
            device="cpu",
        )
        metrics["name"] = config["name"]
        results.append(metrics)

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
