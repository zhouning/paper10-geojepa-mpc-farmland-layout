import argparse
import json
from pathlib import Path
from typing import Sequence

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)
from paper10_geojepa_mpc.training.pcc_v1_1_training import (
    sha256_file,
    train_pcc_v1_1_ensemble,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--labels-manifest", required=True)
    parser.add_argument("--reference-checkpoint", required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--ensemble-size", type=int, required=True)
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--batch-size", type=int, required=True)
    parser.add_argument("--learning-rate", type=float, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def _validate_training_contract(registry, args) -> None:
    if (
        registry.get("protocol_id") != "pcc_v1_1"
        or registry.get("status") != "development"
    ):
        raise ValueError("training requires the PCC v1.1 development registry")
    if int(args.model_seed) not in {
        int(value) for value in registry["model_seeds"]
    }:
        raise ValueError("model seed is outside the PCC v1.1 registry")
    if int(args.ensemble_size) != int(
        registry["viability"]["ensemble_size"]
    ):
        raise ValueError("ensemble size must match the viability pilot")
    expected = {
        "epochs": int(registry["pilot_training"]["epochs"]),
        "batch_size": int(registry["pilot_training"]["batch_size"]),
        "learning_rate": float(
            registry["pilot_training"]["learning_rate"]
        ),
    }
    observed = {
        "epochs": int(args.epochs),
        "batch_size": int(args.batch_size),
        "learning_rate": float(args.learning_rate),
    }
    if observed != expected:
        raise ValueError(
            "pilot training hyperparameters must match the registry"
        )


def _write_summary_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    _validate_training_contract(registry, args)
    registry_digest = sha256_file(args.registry)
    paths = train_pcc_v1_1_ensemble(
        labels_manifest=args.labels_manifest,
        reference_checkpoint=args.reference_checkpoint,
        expected_source_manifest_digest=registry["source_inputs"][
            "train_manifest_digest"
        ],
        expected_transfer_checkpoint_sha256=registry["model"][
            "transfer_checkpoint_sha256"
        ],
        registry_digest=registry_digest,
        model_seed=args.model_seed,
        ensemble_size=args.ensemble_size,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        device=args.device,
        output_dir=args.output_dir,
        hidden_dim=int(registry["model"]["hidden_dim"]),
        ema_decay=float(registry["model"]["ema_decay"]),
    )
    summary = {
        "protocol_id": "pcc_v1_1",
        "registry_digest": registry_digest,
        "source_manifest_digest": registry["source_inputs"][
            "train_manifest_digest"
        ],
        "transfer_checkpoint_sha256": registry["model"][
            "transfer_checkpoint_sha256"
        ],
        "model_seed": int(args.model_seed),
        "ensemble_size": int(args.ensemble_size),
        "checkpoints": [
            {"path": str(path.resolve()), "sha256": sha256_file(path)}
            for path in paths
        ],
    }
    _write_summary_atomic(
        Path(args.output_dir) / "training_summary.json",
        summary,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
