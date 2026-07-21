import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_policy_iteration_lineage import (
    ROUND1_LABEL_POLICY_CONFIG,
    verify_policy_iteration_root,
    write_round_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE_CHECKPOINT = (
    ROOT
    / "paper10_geojepa_mpc"
    / "experiments"
    / "checkpoints"
    / "e0_bishan_rank_seed2028"
    / "rank_seed2028.pt"
)
DEVELOPMENT_COVERAGES = (0.8, 0.9, 0.95)


def _coverage_token(coverage: float) -> str:
    return f"{float(coverage):.2f}".replace(".", "p")


def build_iteration_command_plan(
    args,
    *,
    model_seed: int,
    round1_checkpoint_roots: dict[int, str | Path],
) -> dict[str, object]:
    output_root = Path(args.output_dir)
    seed_root = output_root / f"seed_{int(model_seed)}"
    round2_root = seed_root / "round2"
    round2_train_labels = round2_root / "labels" / "train"
    round2_calibration_labels = round2_root / "labels" / "calibration"

    def family_root(round_index: int, ensemble_size: int) -> Path:
        return seed_root / f"round{round_index}" / f"k{int(ensemble_size)}"

    def calibrator_dir(
        round_index: int,
        ensemble_size: int,
        coverage: float,
    ) -> Path:
        return (
            family_root(round_index, ensemble_size)
            / "calibration"
            / f"coverage_{_coverage_token(coverage)}"
        )

    round1_k3 = Path(round1_checkpoint_roots[3])
    round1_calibrator = calibrator_dir(1, 3, 0.9) / "calibrator.json"

    def label_command(partition: str, output: Path) -> list[str]:
        command = [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.run_pcc_label_jobs",
            "--registry",
            str(args.registry),
            "--partition",
            partition,
            "--max-workers",
            str(args.max_label_workers),
            "--env-source",
            str(args.env_source),
            "--prepared-dir",
            str(args.prepared_dir),
            "--policy",
            "pcc",
            "--reference-checkpoint",
            str(args.reference_checkpoint),
            "--reference-horizon",
            str(args.reference_horizon),
            "--reference-top-k",
            str(args.reference_top_k),
            "--gamma",
            str(args.gamma),
            "--pcc-checkpoint-root",
            str(round1_k3),
            "--pcc-calibrator",
            str(round1_calibrator),
            "--pcc-model-seed",
            str(model_seed),
            "--pcc-planning-horizon",
            str(args.round1_iteration_horizon),
            "--pcc-candidate-budget",
            str(args.round1_iteration_candidate_budget),
            "--pcc-tolerance-scale",
            str(args.round1_iteration_tolerance_scale),
            "--device",
            str(args.device),
            "--output-root",
            str(output),
        ]
        if args.resume:
            command.append("--resume")
        return command

    def calibration_command(
        *,
        labels_manifest: str | Path,
        checkpoint_root: str | Path,
        coverage: float,
        output_dir: str | Path,
    ) -> list[str]:
        return [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.planning.paired_conformal",
            "--registry",
            str(args.registry),
            "--labels-manifest",
            str(labels_manifest),
            "--checkpoint-root",
            str(checkpoint_root),
            "--coverage",
            str(float(coverage)),
            "--device",
            str(args.device),
            "--output-dir",
            str(output_dir),
        ]

    round1_calibrations = {
        (ensemble_size, coverage): calibration_command(
            labels_manifest=args.round0_calibration_labels,
            checkpoint_root=round1_checkpoint_roots[ensemble_size],
            coverage=coverage,
            output_dir=calibrator_dir(1, ensemble_size, coverage),
        )
        for ensemble_size in (3, 5)
        for coverage in DEVELOPMENT_COVERAGES
    }
    round2_training = {
        ensemble_size: [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.run_pcc_train",
            "--registry",
            str(args.registry),
            "--labels-manifest",
            str(round2_train_labels / "manifest.json"),
            "--model-seed",
            str(model_seed),
            "--ensemble-size",
            str(ensemble_size),
            "--epochs",
            str(args.epochs),
            "--batch-size",
            str(args.batch_size),
            "--learning-rate",
            str(args.learning_rate),
            "--hidden-dim",
            str(args.hidden_dim),
            "--device",
            str(args.device),
            "--output-dir",
            str(family_root(2, ensemble_size) / "checkpoints"),
        ]
        for ensemble_size in (3, 5)
    }
    round2_calibrations = {
        (ensemble_size, coverage): calibration_command(
            labels_manifest=round2_calibration_labels / "manifest.json",
            checkpoint_root=family_root(2, ensemble_size) / "checkpoints",
            coverage=coverage,
            output_dir=calibrator_dir(2, ensemble_size, coverage),
        )
        for ensemble_size in (3, 5)
        for coverage in DEVELOPMENT_COVERAGES
    }
    return {
        "round1_calibrations": round1_calibrations,
        "round2_train_labels": label_command("train", round2_train_labels),
        "round2_calibration_labels": label_command(
            "calibration",
            round2_calibration_labels,
        ),
        "round2_training": round2_training,
        "round2_calibrations": round2_calibrations,
    }


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_label_manifest(
    path: str | Path,
    *,
    expected_partition: str,
    expected_seeds,
) -> dict[str, object]:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_digest = payload.get("manifest_digest")
    clean = {
        key: value for key, value in payload.items() if key != "manifest_digest"
    }
    observed_digest = hashlib.sha256(
        json.dumps(
            clean,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    if expected_digest != observed_digest:
        raise ValueError(f"label manifest digest mismatch: {path}")
    if payload.get("partition") != str(expected_partition):
        raise ValueError(f"label manifest partition mismatch: {path}")
    if tuple(map(int, payload.get("trajectory_seeds", []))) != tuple(
        map(int, expected_seeds)
    ):
        raise ValueError(f"label manifest seed block mismatch: {path}")
    return payload


def _checkpoint_digests(
    checkpoint_root: str | Path,
    *,
    model_seed: int,
    ensemble_size: int,
) -> list[str]:
    import torch

    root = Path(checkpoint_root)
    paths = sorted(root.glob("member_*.pt"))
    if len(paths) != int(ensemble_size):
        raise ValueError(
            f"checkpoint root {root} does not contain {ensemble_size} members"
        )
    member_indexes = set()
    digests = []
    for path in paths:
        payload = torch.load(path, map_location="cpu", weights_only=False)
        if int(payload.get("model_seed", -1)) != int(model_seed):
            raise ValueError(f"checkpoint model seed mismatch: {path}")
        member_indexes.add(int(payload.get("member_index", -1)))
        digests.append(_sha256_file(path))
    if member_indexes != set(range(int(ensemble_size))):
        raise ValueError(f"checkpoint member indexes are incomplete: {root}")
    if len(set(digests)) != len(digests):
        raise ValueError(f"checkpoint digests are duplicated: {root}")
    return digests


def _resolve_round1_checkpoint_root(
    root: str | Path,
    *,
    model_seed: int,
    ensemble_size: int,
) -> Path:
    root = Path(root)
    candidates = [root / f"seed{int(model_seed)}_k{int(ensemble_size)}"]
    candidates.extend(
        path.parent for path in sorted(root.rglob("training_summary.json"))
    )
    valid = []
    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen or not candidate.is_dir():
            continue
        seen.add(candidate)
        try:
            _checkpoint_digests(
                candidate,
                model_seed=model_seed,
                ensemble_size=ensemble_size,
            )
        except (OSError, ValueError, KeyError, TypeError):
            continue
        valid.append(candidate)
    if len(valid) != 1:
        raise ValueError(
            "round-1 checkpoint root must resolve to exactly one model-seed ensemble"
        )
    return valid[0]


def _load_valid_calibrator(
    path: str | Path,
    *,
    labels_manifest_digest: str,
    checkpoint_digests,
    calibration_seeds,
):
    from paper10_geojepa_mpc.planning.paired_conformal import (
        load_joint_calibrator,
    )

    calibrator = load_joint_calibrator(path)
    if calibrator.labels_manifest_digest != str(labels_manifest_digest):
        raise ValueError("calibrator label lineage mismatch")
    if tuple(calibrator.checkpoint_digests) != tuple(map(str, checkpoint_digests)):
        raise ValueError("calibrator checkpoint lineage mismatch")
    if tuple(calibrator.calibration_seeds) != tuple(map(int, calibration_seeds)):
        raise ValueError("calibrator seed block mismatch")
    if not np.isfinite(calibrator.q_joint) or not np.isfinite(
        calibrator.trajectory_scores
    ).all():
        raise ValueError("calibrator contains non-finite values")
    return calibrator


def _run_command(command: list[str], *, log_path: str | Path) -> None:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(f"policy iteration stage failed; see {log_path}")


def _calibrator_or_none(
    path: Path,
    *,
    labels_manifest_digest: str,
    checkpoint_digests,
    calibration_seeds,
):
    if not path.exists():
        return None
    try:
        return _load_valid_calibrator(
            path,
            labels_manifest_digest=labels_manifest_digest,
            checkpoint_digests=checkpoint_digests,
            calibration_seeds=calibration_seeds,
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _family_root(
    output_root: str | Path,
    *,
    model_seed: int,
    round_index: int,
    ensemble_size: int,
) -> Path:
    return (
        Path(output_root)
        / f"seed_{int(model_seed)}"
        / f"round{int(round_index)}"
        / f"k{int(ensemble_size)}"
    )


def _calibrator_path(
    output_root: str | Path,
    *,
    model_seed: int,
    round_index: int,
    ensemble_size: int,
    coverage: float,
) -> Path:
    return (
        _family_root(
            output_root,
            model_seed=model_seed,
            round_index=round_index,
            ensemble_size=ensemble_size,
        )
        / "calibration"
        / f"coverage_{_coverage_token(coverage)}"
        / "calibrator.json"
    )


def _import_checkpoint_family(
    source_root: str | Path,
    destination_root: str | Path,
    *,
    model_seed: int,
    ensemble_size: int,
) -> Path:
    source_root = Path(source_root).resolve()
    destination_root = Path(destination_root).resolve()
    source_digests = _checkpoint_digests(
        source_root,
        model_seed=model_seed,
        ensemble_size=ensemble_size,
    )
    destination_root.mkdir(parents=True, exist_ok=True)
    source_paths = sorted(source_root.glob("member_*.pt"))
    for source_path, expected_digest in zip(source_paths, source_digests, strict=True):
        destination_path = destination_root / source_path.name
        if destination_path.exists() and _sha256_file(destination_path) == expected_digest:
            continue
        temporary = destination_path.with_suffix(destination_path.suffix + ".tmp")
        shutil.copy2(source_path, temporary)
        if _sha256_file(temporary) != expected_digest:
            raise ValueError("imported checkpoint digest mismatch")
        temporary.replace(destination_path)
    observed = _checkpoint_digests(
        destination_root,
        model_seed=model_seed,
        ensemble_size=ensemble_size,
    )
    if observed != source_digests:
        raise ValueError("imported checkpoint family differs from its source")
    return destination_root


def execute_policy_iteration(args, *, registry: dict[str, object]) -> dict[str, object]:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        validate_registry,
    )

    validate_registry(registry)
    if int(args.rounds) != 2:
        raise ValueError("PCC requires exactly two policy-improvement rounds")
    expected_iteration = (
        int(args.round1_iteration_ensemble_size),
        float(args.round1_iteration_coverage),
        float(args.round1_iteration_tolerance_scale),
        int(args.round1_iteration_horizon),
    )
    locked_iteration = (
        int(ROUND1_LABEL_POLICY_CONFIG["ensemble_size"]),
        float(ROUND1_LABEL_POLICY_CONFIG["joint_coverage"]),
        float(ROUND1_LABEL_POLICY_CONFIG["tolerance_scale"]),
        int(ROUND1_LABEL_POLICY_CONFIG["planning_horizon"]),
    )
    if expected_iteration != locked_iteration:
        raise ValueError("round-1 iteration policy differs from predeclared config")
    if int(args.round1_iteration_candidate_budget) != 50:
        raise ValueError("round-1 iteration candidate budget is locked to 50")
    required = (
        args.round0_train_labels,
        args.round0_calibration_labels,
        args.round1_checkpoints,
        args.output_dir,
    )
    if any(value is None for value in required):
        raise ValueError("policy iteration execution arguments are incomplete")
    if _sha256_file(args.reference_checkpoint) != str(
        registry["offline_reference_policy"]["checkpoint_sha256"]
    ):
        raise ValueError("policy iteration reference checkpoint digest mismatch")

    train_seeds = registry["partitions"]["train"]
    calibration_seeds = registry["partitions"]["calibration"]
    round0_train = _load_label_manifest(
        args.round0_train_labels,
        expected_partition="train",
        expected_seeds=train_seeds,
    )
    round0_calibration = _load_label_manifest(
        args.round0_calibration_labels,
        expected_partition="calibration",
        expected_seeds=calibration_seeds,
    )
    if round0_train["continuation_policy"] != round0_calibration[
        "continuation_policy"
    ]:
        raise ValueError("round-0 train/calibration continuation policies differ")

    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    ensemble_sizes = tuple(int(value) for value in registry["grid"]["ensemble_size"])
    coverages = tuple(float(value) for value in registry["grid"]["joint_coverage"])
    if ensemble_sizes != (3, 5) or coverages != DEVELOPMENT_COVERAGES:
        raise ValueError("policy iteration factorial differs from the locked grid")

    for model_seed in map(int, registry["model_seeds"]):
        round1_checkpoints = {}
        round1_digests = {}
        for ensemble_size in ensemble_sizes:
            source_root = _resolve_round1_checkpoint_root(
                args.round1_checkpoints,
                model_seed=model_seed,
                ensemble_size=ensemble_size,
            )
            destination_root = _family_root(
                output_root,
                model_seed=model_seed,
                round_index=1,
                ensemble_size=ensemble_size,
            ) / "checkpoints"
            round1_checkpoints[ensemble_size] = _import_checkpoint_family(
                source_root,
                destination_root,
                model_seed=model_seed,
                ensemble_size=ensemble_size,
            )
            round1_digests[ensemble_size] = _checkpoint_digests(
                destination_root,
                model_seed=model_seed,
                ensemble_size=ensemble_size,
            )
        plan = build_iteration_command_plan(
            args,
            model_seed=model_seed,
            round1_checkpoint_roots=round1_checkpoints,
        )
        seed_root = output_root / f"seed_{model_seed}"
        round2_root = seed_root / "round2"
        round1_calibrators = {}
        for ensemble_size in ensemble_sizes:
            for coverage in coverages:
                path = _calibrator_path(
                    output_root,
                    model_seed=model_seed,
                    round_index=1,
                    ensemble_size=ensemble_size,
                    coverage=coverage,
                )
                calibrator = (
                    _calibrator_or_none(
                        path,
                        labels_manifest_digest=round0_calibration["manifest_digest"],
                        checkpoint_digests=round1_digests[ensemble_size],
                        calibration_seeds=calibration_seeds,
                    )
                    if args.resume
                    else None
                )
                if calibrator is None:
                    _run_command(
                        plan["round1_calibrations"][(ensemble_size, coverage)],
                        log_path=path.parent / "calibration.log",
                    )
                    calibrator = _load_valid_calibrator(
                        path,
                        labels_manifest_digest=round0_calibration["manifest_digest"],
                        checkpoint_digests=round1_digests[ensemble_size],
                        calibration_seeds=calibration_seeds,
                    )
                round1_calibrators[(ensemble_size, coverage)] = path

        round1_manifests = {}
        for ensemble_size in ensemble_sizes:
            primary_payload = json.loads(
                round1_calibrators[(ensemble_size, 0.9)].read_text(
                    encoding="utf-8"
                )
            )
            family_root = _family_root(
                output_root,
                model_seed=model_seed,
                round_index=1,
                ensemble_size=ensemble_size,
            )
            round1_manifests[ensemble_size] = write_round_manifest(
                family_root / "round_manifest.json",
                model_seed=model_seed,
                round_index=1,
                parent_digest=str(
                    registry["offline_reference_policy"]["checkpoint_sha256"]
                ),
                train_labels_digest=str(round0_train["manifest_digest"]),
                calibration_labels_digest=str(round0_calibration["manifest_digest"]),
                checkpoint_digests=round1_digests[ensemble_size],
                calibrator_digest=str(primary_payload["calibrator_digest"]),
                continuation_policy=dict(round0_train["continuation_policy"]),
            )

        _run_command(
            plan["round2_train_labels"],
            log_path=round2_root / "train_labels.log",
        )
        _run_command(
            plan["round2_calibration_labels"],
            log_path=round2_root / "calibration_labels.log",
        )
        round2_train = _load_label_manifest(
            round2_root / "labels" / "train" / "manifest.json",
            expected_partition="train",
            expected_seeds=train_seeds,
        )
        round2_calibration = _load_label_manifest(
            round2_root / "labels" / "calibration" / "manifest.json",
            expected_partition="calibration",
            expected_seeds=calibration_seeds,
        )
        if round2_train["continuation_policy"] != round2_calibration[
            "continuation_policy"
        ]:
            raise ValueError("round-2 train/calibration continuation policies differ")
        if (
            round2_train["continuation_policy"].get("name") != "pcc_round1"
            or int(round2_train["continuation_policy"].get("model_seed", -1))
            != model_seed
        ):
            raise ValueError("round-2 label continuation lineage mismatch")

        round2_digests = {}
        for ensemble_size in ensemble_sizes:
            checkpoints = _family_root(
                output_root,
                model_seed=model_seed,
                round_index=2,
                ensemble_size=ensemble_size,
            ) / "checkpoints"
            digests = None
            if args.resume:
                try:
                    digests = _checkpoint_digests(
                        checkpoints,
                        model_seed=model_seed,
                        ensemble_size=ensemble_size,
                    )
                except (OSError, ValueError, KeyError, TypeError):
                    digests = None
            if digests is None:
                _run_command(
                    plan["round2_training"][ensemble_size],
                    log_path=checkpoints.parent / "training.log",
                )
                digests = _checkpoint_digests(
                    checkpoints,
                    model_seed=model_seed,
                    ensemble_size=ensemble_size,
                )
            round2_digests[ensemble_size] = digests

        round2_calibrators = {}
        for ensemble_size in ensemble_sizes:
            for coverage in coverages:
                path = _calibrator_path(
                    output_root,
                    model_seed=model_seed,
                    round_index=2,
                    ensemble_size=ensemble_size,
                    coverage=coverage,
                )
                calibrator = (
                    _calibrator_or_none(
                        path,
                        labels_manifest_digest=round2_calibration["manifest_digest"],
                        checkpoint_digests=round2_digests[ensemble_size],
                        calibration_seeds=calibration_seeds,
                    )
                    if args.resume
                    else None
                )
                if calibrator is None:
                    _run_command(
                        plan["round2_calibrations"][(ensemble_size, coverage)],
                        log_path=path.parent / "calibration.log",
                    )
                    calibrator = _load_valid_calibrator(
                        path,
                        labels_manifest_digest=round2_calibration["manifest_digest"],
                        checkpoint_digests=round2_digests[ensemble_size],
                        calibration_seeds=calibration_seeds,
                    )
                round2_calibrators[(ensemble_size, coverage)] = path

        for ensemble_size in ensemble_sizes:
            primary_payload = json.loads(
                round2_calibrators[(ensemble_size, 0.9)].read_text(
                    encoding="utf-8"
                )
            )
            family_root = _family_root(
                output_root,
                model_seed=model_seed,
                round_index=2,
                ensemble_size=ensemble_size,
            )
            write_round_manifest(
                family_root / "round_manifest.json",
                model_seed=model_seed,
                round_index=2,
                parent_digest=str(round1_manifests[3]["round_digest"]),
                train_labels_digest=str(round2_train["manifest_digest"]),
                calibration_labels_digest=str(round2_calibration["manifest_digest"]),
                checkpoint_digests=round2_digests[ensemble_size],
                calibrator_digest=str(primary_payload["calibrator_digest"]),
                continuation_policy=dict(round2_train["continuation_policy"]),
            )

    report = verify_policy_iteration_root(output_root, registry=registry)
    verification_path = output_root / "verification.json"
    temporary = verification_path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(verification_path)
    return report
