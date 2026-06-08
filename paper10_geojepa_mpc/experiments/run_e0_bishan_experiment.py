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


def _parse_csv(value: str):
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_int_csv(value: str):
    return [int(item) for item in _parse_csv(value)]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", default="mse_only,rank,rank_sigreg")
    parser.add_argument("--seeds", default="2026")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--transition-samples", type=int, default=6000)
    parser.add_argument("--pairwise-states", type=int, default=1000)
    parser.add_argument("--pairwise-subsample", type=int, default=16)
    parser.add_argument("--n-pairs", type=int, default=4)
    parser.add_argument("--eval-seed", type=int, default=12345)
    parser.add_argument("--candidate-metrics", action="store_true")
    parser.add_argument("--candidate-top-k", type=int, default=5)
    parser.add_argument("--candidate-batch-states", type=int, default=4)
    parser.add_argument("--candidate-max-states", type=int, default=None)
    parser.add_argument("--checkpoint-dir", default=None)
    parser.add_argument("--checkpoint-metric", default="candidate_top5_regret")
    parser.add_argument("--checkpoint-mode", choices=["min", "max"], default="min")
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--output",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "results"
            / "e0_bishan_experiment_latest.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configs = _parse_csv(args.configs)
    seeds = _parse_int_csv(args.seeds)

    unknown = sorted(set(configs) - set(CONFIGS))
    if unknown:
        raise ValueError(f"Unknown configs: {unknown}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = Path(args.checkpoint_dir) if args.checkpoint_dir else None
    if checkpoint_dir is not None:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

    runs = []
    experiment_start = perf_counter()
    for seed in seeds:
        for config_name in configs:
            cfg = CONFIGS[config_name]
            run_start = perf_counter()
            checkpoint_path = None
            if checkpoint_dir is not None:
                checkpoint_path = checkpoint_dir / f"{config_name}_seed{seed}.pt"
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
                compute_candidate_metrics=args.candidate_metrics,
                candidate_top_k=args.candidate_top_k,
                candidate_batch_states=args.candidate_batch_states,
                candidate_max_states=args.candidate_max_states,
                checkpoint_path=checkpoint_path,
                checkpoint_metric=args.checkpoint_metric,
                checkpoint_mode=args.checkpoint_mode,
                seed=seed,
                eval_seed=args.eval_seed,
                device=args.device,
            )
            metrics["config"] = config_name
            metrics["seed"] = seed
            metrics["elapsed_sec"] = perf_counter() - run_start
            runs.append(metrics)

            payload = {
                "dataset": "bishan_full_tool2",
                "device": args.device,
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "transition_samples": args.transition_samples,
                "pairwise_states": args.pairwise_states,
                "pairwise_subsample": args.pairwise_subsample,
                "n_pairs": args.n_pairs,
                "eval_seed": args.eval_seed,
                "candidate_metrics": args.candidate_metrics,
                "candidate_top_k": args.candidate_top_k,
                "candidate_max_states": args.candidate_max_states,
                "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir else None,
                "checkpoint_metric": args.checkpoint_metric,
                "checkpoint_mode": args.checkpoint_mode,
                "elapsed_sec": perf_counter() - experiment_start,
                "runs": runs,
            }
            output_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
            print(json.dumps(metrics, indent=2, sort_keys=True))

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
