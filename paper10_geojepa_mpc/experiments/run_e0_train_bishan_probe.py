import argparse
import json
from pathlib import Path
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.training.e0_training import train_e0_smoke_config


CONFIGS = {
    "mse_only": {"lambda_rank": 0.0, "lambda_sig": 0.0},
    "rank": {"lambda_rank": 1.0, "lambda_sig": 0.0},
    "rank_sigreg": {"lambda_rank": 1.0, "lambda_sig": 0.01},
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", choices=sorted(CONFIGS), default="rank")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--transition-samples", type=int, default=1024)
    parser.add_argument("--pairwise-states", type=int, default=128)
    parser.add_argument("--pairwise-subsample", type=int, default=16)
    parser.add_argument("--n-pairs", type=int, default=4)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--device", default="cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = CONFIGS[args.config]
    started = perf_counter()
    metrics = train_e0_smoke_config(
        transition_path=ROOT / "tool2" / "transitions.npz",
        pairwise_path=ROOT / "tool2" / "pairwise.npz",
        n_blocks=2600,
        k_global=12,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lambda_rank=cfg["lambda_rank"],
        lambda_sig=cfg["lambda_sig"],
        n_pairs=args.n_pairs,
        pairwise_subsample=args.pairwise_subsample,
        max_transition_samples=args.transition_samples,
        max_pairwise_states=args.pairwise_states,
        seed=args.seed,
        device=args.device,
    )
    metrics["config"] = args.config
    metrics["elapsed_sec"] = perf_counter() - started
    metrics["device"] = args.device
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
