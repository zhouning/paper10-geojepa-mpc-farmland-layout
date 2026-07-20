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


def validate_adaptation_request(
    registry: dict[str, object],
    *,
    labels_manifest: str | Path,
    model_seed: int,
    init_checkpoint_root: str | Path,
) -> list[str]:
    verify_frozen_registry(registry)
    manifest = json.loads(Path(labels_manifest).read_text(encoding="utf-8"))
    if manifest.get("protocol_id") != registry["protocol_id"]:
        raise ValueError("Dongxing adaptation protocol mismatch")
    if manifest.get("partition") != "dongxing_adaptation":
        raise ValueError("Dongxing adaptation label partition mismatch")
    observed_seeds = [int(value) for value in manifest.get("trajectory_seeds", [])]
    expected_seeds = [
        int(value) for value in registry["partitions"]["dongxing_adaptation"]
    ]
    if observed_seeds != expected_seeds:
        raise ValueError("Dongxing adaptation seed block mismatch")
    model_seeds = [int(value) for value in registry["model_seeds"]]
    try:
        model_index = model_seeds.index(int(model_seed))
    except ValueError as exc:
        raise ValueError("model seed is outside the frozen registry") from exc
    ensemble_size = int(registry["selected_config"]["ensemble_size"])
    frozen_digests = [
        str(value) for value in registry["selected_config"]["checkpoint_digests"]
    ]
    expected_count = len(model_seeds) * ensemble_size
    if (
        len(frozen_digests) != expected_count
        or len(frozen_digests) != len(set(frozen_digests))
    ):
        raise ValueError("frozen checkpoint lineage is incomplete")
    expected_parent = frozen_digests[
        model_index * ensemble_size : (model_index + 1) * ensemble_size
    ]
    root = Path(init_checkpoint_root)
    parent_paths = sorted(root.rglob("*.pt")) if root.is_dir() else [root]
    if len(parent_paths) != ensemble_size or any(
        not path.is_file() for path in parent_paths
    ):
        raise ValueError("adaptation parent checkpoint block is incomplete")
    observed_parent = [_sha256_file(path) for path in parent_paths]
    if observed_parent != expected_parent:
        raise ValueError("adaptation parent checkpoint digest mismatch")
    return observed_parent


def validate_adaptation_hyperparameters(
    registry: dict[str, object],
    *,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_dim: int,
    trainable_scope: str,
    representation: str,
    county_action_count: int | None,
) -> dict[str, object]:
    verify_frozen_registry(registry)
    expected = dict(registry["dongxing_adaptation_training"])
    observed = {
        "epochs": int(epochs),
        "batch_size": int(batch_size),
        "learning_rate": float(learning_rate),
        "hidden_dim": int(hidden_dim),
        "trainable_scope": str(trainable_scope),
        "representation": str(representation),
        "county_action_count": (
            None if county_action_count is None else int(county_action_count)
        ),
    }
    if observed != expected:
        raise ValueError(
            "Dongxing adaptation hyperparameters must match the frozen registry"
        )
    return expected


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--labels-manifest", required=True)
    parser.add_argument(
        "--region",
        choices=("bishan", "dongxing"),
        default="bishan",
    )
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
    parser.add_argument(
        "--representation",
        choices=("action_relative", "county_specific_action_embedding"),
        default="action_relative",
    )
    parser.add_argument("--county-action-count", type=int, default=None)
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
    parent_checkpoint_digests = []
    adaptation_hyperparameters = None
    if args.region == "dongxing":
        if args.trainable_scope != "objective_heads":
            raise ValueError("Dongxing adaptation must update objective heads only")
        if not args.ensemble_size_from_frozen_registry:
            raise ValueError("Dongxing ensemble size must come from the frozen registry")
        if args.representation != "action_relative":
            raise ValueError("Dongxing adaptation must preserve the frozen representation")
        if args.init_checkpoint_root is None:
            raise ValueError("Dongxing adaptation requires parent checkpoints")
        adaptation_hyperparameters = validate_adaptation_hyperparameters(
            registry,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            hidden_dim=args.hidden_dim,
            trainable_scope=args.trainable_scope,
            representation=args.representation,
            county_action_count=args.county_action_count,
        )
        parent_checkpoint_digests = validate_adaptation_request(
            registry,
            labels_manifest=args.labels_manifest,
            model_seed=args.model_seed,
            init_checkpoint_root=args.init_checkpoint_root,
        )
    elif args.trainable_scope == "objective_heads":
        raise ValueError("objective-head-only adaptation is reserved for Dongxing")
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
        representation=args.representation,
        county_action_count=args.county_action_count,
        region=args.region,
    )
    summary = {
        "protocol_id": registry["protocol_id"],
        "registry_digest": registry_digest,
        "model_seed": int(args.model_seed),
        "ensemble_size": ensemble_size,
        "region": args.region,
        "parent_checkpoint_digests": parent_checkpoint_digests,
        "trainable_scope": args.trainable_scope,
        "representation": args.representation,
        "county_action_count": args.county_action_count,
        "checkpoints": [
            {"path": str(path), "sha256": _sha256_file(path)} for path in paths
        ],
    }
    if adaptation_hyperparameters is not None:
        summary["adaptation_hyperparameters"] = adaptation_hyperparameters
    output_dir = Path(args.output_dir)
    summary_path = output_dir / "training_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
