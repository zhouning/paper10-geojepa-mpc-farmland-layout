import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
    verify_frozen_registry,
)
from paper10_geojepa_mpc.training.pcc_training import train_pcc_ensemble


def resolve_ensemble_size(
    registry: dict[str, object],
    explicit_size: int | None,
    *,
    from_frozen: bool,
) -> int:
    if from_frozen:
        if explicit_size is not None:
            raise ValueError("explicit ensemble size cannot override frozen config")
        if registry.get("status") != "frozen":
            raise ValueError("ensemble size can be read from registry only after freeze")
        return int(registry["selected_config"]["ensemble_size"])
    if explicit_size is None:
        raise ValueError("--ensemble-size is required during development")
    declared = {int(value) for value in registry["grid"]["ensemble_size"]}
    if int(explicit_size) not in declared:
        raise ValueError("ensemble size is outside the declared development grid")
    return int(explicit_size)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--labels-manifest", required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--ensemble-size", type=int, default=None)
    parser.add_argument(
        "--ensemble-size-from-frozen-registry",
        action="store_true",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--trainable-scope",
        choices=("all", "objective_heads"),
        default="all",
    )
    parser.add_argument("--init-checkpoint-root", default=None)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    registry_digest = None
    if registry.get("status") == "frozen":
        registry_digest = verify_frozen_registry(registry)
    if int(args.model_seed) not in {
        int(value) for value in registry["model_seeds"]
    }:
        raise ValueError("model seed is outside the declared registry")
    ensemble_size = resolve_ensemble_size(
        registry,
        args.ensemble_size,
        from_frozen=args.ensemble_size_from_frozen_registry,
    )
    paths = train_pcc_ensemble(
        labels_manifest=args.labels_manifest,
        model_seed=args.model_seed,
        ensemble_size=ensemble_size,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        device=args.device,
        output_dir=args.output_dir,
        hidden_dim=args.hidden_dim,
        trainable_scope=args.trainable_scope,
        init_checkpoint_root=args.init_checkpoint_root,
        registry_digest=registry_digest,
    )
    summary = {
        "protocol_id": registry["protocol_id"],
        "registry_digest": registry_digest,
        "model_seed": int(args.model_seed),
        "ensemble_size": ensemble_size,
        "trainable_scope": args.trainable_scope,
        "checkpoints": [
            {"path": str(path), "sha256": _sha256_file(path)} for path in paths
        ],
    }
    output_dir = Path(args.output_dir)
    summary_path = output_dir / "training_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
