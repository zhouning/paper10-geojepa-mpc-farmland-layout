import argparse
import json
from pathlib import Path
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.training.e0_training import train_e0_smoke_config


def resolve_checkpoint_metric(metric: str, candidate_top_k: int) -> str:
    if metric == "auto":
        return f"candidate_top{int(candidate_top_k)}_regret"
    return metric


def build_train_kwargs(args) -> dict:
    return {
        "transition_path": args.transition_path,
        "pairwise_path": args.pairwise_path,
        "n_blocks": int(args.n_blocks),
        "k_global": int(args.k_global),
        "epochs": int(args.epochs),
        "batch_size": int(args.batch_size),
        "lr": float(args.lr),
        "lambda_rank": float(args.lambda_rank),
        "lambda_sig": float(args.lambda_sig),
        "n_pairs": int(args.n_pairs),
        "margin": float(args.margin),
        "pairwise_subsample": int(args.pairwise_subsample),
        "max_transition_samples": args.transition_samples,
        "max_pairwise_states": args.pairwise_states,
        "compute_candidate_metrics": True,
        "candidate_top_k": int(args.candidate_top_k),
        "candidate_batch_states": int(args.candidate_batch_states),
        "candidate_max_states": args.candidate_max_states,
        "checkpoint_path": args.checkpoint_path,
        "checkpoint_metric": resolve_checkpoint_metric(
            args.checkpoint_metric,
            args.candidate_top_k,
        ),
        "checkpoint_mode": args.checkpoint_mode,
        "init_checkpoint_path": args.init_checkpoint,
        "trainable_scope": "value_head",
        "rank_score_mode": "value",
        "rank_value_weight": float(args.rank_value_weight),
        "seed": int(args.seed),
        "eval_seed": int(args.eval_seed),
        "device": args.device,
    }


def run_training(args) -> dict:
    started = perf_counter()
    kwargs = build_train_kwargs(args)
    metrics = train_e0_smoke_config(**kwargs)
    metrics["elapsed_sec"] = perf_counter() - started
    metrics["device"] = args.device
    metrics["value_head_train_entry"] = "run_e0_value_head_train"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(metrics, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return metrics


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transition-path", default=str(ROOT / "tool2" / "transitions.npz"))
    parser.add_argument("--pairwise-path", required=True)
    parser.add_argument(
        "--init-checkpoint",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "checkpoints"
            / "e0_bishan_rank_seed2028"
            / "rank_seed2028.pt"
        ),
    )
    parser.add_argument("--checkpoint-path", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--n-blocks", type=int, default=2600)
    parser.add_argument("--k-global", type=int, default=12)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--lambda-rank", type=float, default=1.0)
    parser.add_argument("--lambda-sig", type=float, default=0.0)
    parser.add_argument("--n-pairs", type=int, default=8)
    parser.add_argument("--margin", type=float, default=0.1)
    parser.add_argument("--pairwise-subsample", type=int, default=32)
    parser.add_argument("--transition-samples", type=int, default=6000)
    parser.add_argument("--pairwise-states", type=int, default=None)
    parser.add_argument("--candidate-top-k", type=int, default=3)
    parser.add_argument("--candidate-batch-states", type=int, default=4)
    parser.add_argument("--candidate-max-states", type=int, default=None)
    parser.add_argument("--checkpoint-metric", default="auto")
    parser.add_argument("--checkpoint-mode", choices=("min", "max"), default="min")
    parser.add_argument("--rank-value-weight", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=3035)
    parser.add_argument("--eval-seed", type=int, default=12345)
    parser.add_argument("--device", default="cpu")
    return parser.parse_args()


def main() -> None:
    metrics = run_training(parse_args())
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
