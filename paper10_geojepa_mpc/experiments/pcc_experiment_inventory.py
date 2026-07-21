import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np
import torch

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.experiments.pcc_policy_iteration_lineage import (
    verify_round_manifest,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    DEFAULT_REGISTRY,
    load_registry,
    validate_registry,
    verify_frozen_registry,
)
from paper10_geojepa_mpc.planning.paired_conformal import (
    JointPairedCalibrator,
    load_joint_calibrator,
)


@dataclass(frozen=True)
class _CheckpointArtifact:
    path: Path
    digest: str
    model_seed: int
    ensemble_size: int
    member_seed: int
    member_index: int
    bootstrap_trajectory_ids: tuple[int, ...]
    labels_manifest_digest: str
    registry_digest: str | None
    protocol_id: str


@dataclass(frozen=True)
class _CalibratorArtifact:
    path: Path
    digest: str
    calibrator: JointPairedCalibrator


@dataclass(frozen=True)
class EnsembleInventoryRecord:
    model_seed: int
    ensemble_size: int
    policy_round: int
    checkpoint_root: Path
    checkpoint_paths: tuple[Path, ...]
    checkpoint_digests: tuple[str, ...]
    calibrators: Mapping[float, Path]
    calibrator_digests: Mapping[float, str]
    round_manifest_path: Path
    round_digest: str
    train_labels_digest: str
    calibration_labels_digest: str


@dataclass(frozen=True)
class ExperimentInventory:
    records: tuple[EnsembleInventoryRecord, ...]

    def __post_init__(self):
        index = {}
        for record in self.records:
            key = (
                int(record.model_seed),
                int(record.ensemble_size),
                int(record.policy_round),
            )
            if key in index:
                raise ValueError(f"duplicate experiment inventory key: {key}")
            index[key] = record
        object.__setattr__(self, "_index", MappingProxyType(index))

    def _record(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
    ) -> EnsembleInventoryRecord:
        key = (int(model_seed), int(ensemble_size), int(policy_round))
        try:
            return self._index[key]
        except KeyError as exc:
            raise KeyError(f"experiment inventory key is missing: {key}") from exc

    def checkpoint_root(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
    ) -> Path:
        return self._record(model_seed, ensemble_size, policy_round).checkpoint_root

    def checkpoint_digests(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
    ) -> tuple[str, ...]:
        return self._record(
            model_seed,
            ensemble_size,
            policy_round,
        ).checkpoint_digests

    def calibrator(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
        coverage: float,
    ) -> Path:
        record = self._record(model_seed, ensemble_size, policy_round)
        try:
            return record.calibrators[float(coverage)]
        except KeyError as exc:
            raise KeyError(f"calibrator coverage is missing: {coverage}") from exc

    def coverages(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
    ) -> tuple[float, ...]:
        record = self._record(model_seed, ensemble_size, policy_round)
        return tuple(sorted(record.calibrators))

    def calibrator_digest(
        self,
        model_seed: int,
        ensemble_size: int,
        policy_round: int,
        coverage: float,
    ) -> str:
        record = self._record(model_seed, ensemble_size, policy_round)
        try:
            return record.calibrator_digests[float(coverage)]
        except KeyError as exc:
            raise KeyError(f"calibrator coverage is missing: {coverage}") from exc

    def report(self) -> dict[str, object]:
        records = []
        for record in self.records:
            records.append(
                {
                    "model_seed": record.model_seed,
                    "ensemble_size": record.ensemble_size,
                    "policy_round": record.policy_round,
                    "checkpoint_root": str(record.checkpoint_root),
                    "checkpoint_paths": [
                        str(path) for path in record.checkpoint_paths
                    ],
                    "checkpoint_digests": list(record.checkpoint_digests),
                    "member_indexes": list(range(record.ensemble_size)),
                    "calibrators": {
                        str(coverage): {
                            "path": str(path),
                            "digest": record.calibrator_digests[coverage],
                        }
                        for coverage, path in sorted(record.calibrators.items())
                    },
                    "round_manifest_path": str(record.round_manifest_path),
                    "round_digest": record.round_digest,
                    "train_labels_digest": record.train_labels_digest,
                    "calibration_labels_digest": (
                        record.calibration_labels_digest
                    ),
                }
            )
        return {
            "passed": True,
            "model_seeds": sorted({row.model_seed for row in self.records}),
            "n_records": len(records),
            "records": records,
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_artifacts(root: Path) -> dict[str, _CheckpointArtifact]:
    artifacts = {}
    for path in sorted(root.rglob("*.pt")):
        payload = torch.load(path, map_location="cpu", weights_only=False)
        if not isinstance(payload, dict) or not {
            "model_seed",
            "member_seed",
            "member_index",
        }.issubset(payload):
            continue
        resolved = path.resolve()
        digest = _sha256_file(resolved)
        if digest in artifacts:
            raise ValueError("checkpoint digest identifies multiple physical files")
        artifacts[digest] = _CheckpointArtifact(
            path=resolved,
            digest=digest,
            model_seed=int(payload["model_seed"]),
            ensemble_size=int(payload.get("ensemble_size", -1)),
            member_seed=int(payload["member_seed"]),
            member_index=int(payload["member_index"]),
            bootstrap_trajectory_ids=tuple(
                int(value)
                for value in payload.get("bootstrap_trajectory_ids", [])
            ),
            labels_manifest_digest=str(
                payload.get("labels_manifest_digest", "")
            ),
            registry_digest=(
                None
                if payload.get("registry_digest") is None
                else str(payload["registry_digest"])
            ),
            protocol_id=str(payload.get("protocol_id", "")),
        )
    return artifacts


def _json_payloads(root: Path):
    for path in sorted(root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            yield path.resolve(), payload


def _round_manifests(root: Path) -> list[tuple[Path, dict[str, object]]]:
    required = {
        "round_digest",
        "round_index",
        "model_seed",
        "checkpoint_digests",
        "calibrator_digest",
    }
    manifests = []
    for path, payload in _json_payloads(root):
        if required.issubset(payload):
            verify_round_manifest(payload)
            manifests.append((path, payload))
    return manifests


def _calibrator_artifacts(root: Path) -> dict[str, _CalibratorArtifact]:
    required = {
        "calibrator_digest",
        "coverage",
        "q_joint",
        "objective_names",
        "checkpoint_digests",
    }
    artifacts = {}
    for path, payload in _json_payloads(root):
        if not required.issubset(payload):
            continue
        calibrator = load_joint_calibrator(path)
        digest = str(payload["calibrator_digest"])
        if digest in artifacts:
            raise ValueError("calibrator digest identifies multiple physical files")
        artifacts[digest] = _CalibratorArtifact(
            path=path,
            digest=digest,
            calibrator=calibrator,
        )
    return artifacts


def _validate_checkpoint_group(
    manifest: dict[str, object],
    checkpoints_by_digest: Mapping[str, _CheckpointArtifact],
    *,
    protocol_id: str,
    frozen_registry_digest: str | None,
) -> tuple[_CheckpointArtifact, ...]:
    expected_digests = tuple(
        str(value) for value in manifest["checkpoint_digests"]
    )
    try:
        checkpoints = tuple(
            checkpoints_by_digest[digest] for digest in expected_digests
        )
    except KeyError as exc:
        raise ValueError("checkpoint digest does not match a physical file") from exc
    model_seed = int(manifest["model_seed"])
    member_indexes = tuple(checkpoint.member_index for checkpoint in checkpoints)
    ensemble_size = len(checkpoints)
    if set(member_indexes) != set(range(ensemble_size)) or len(
        set(member_indexes)
    ) != ensemble_size:
        raise ValueError("checkpoint member indexes are incomplete or duplicated")
    by_member = tuple(sorted(checkpoints, key=lambda row: row.member_index))
    if tuple(row.digest for row in by_member) != expected_digests:
        raise ValueError("checkpoint digest order does not match member indexes")
    if any(row.model_seed != model_seed for row in by_member):
        raise ValueError("checkpoint model seed lineage mismatch")
    if any(row.ensemble_size != ensemble_size for row in by_member):
        raise ValueError("checkpoint ensemble size lineage mismatch")
    if any(row.protocol_id != protocol_id for row in by_member):
        raise ValueError("checkpoint protocol lineage mismatch")
    train_digest = str(manifest.get("train_labels_digest", ""))
    if any(row.labels_manifest_digest != train_digest for row in by_member):
        raise ValueError("checkpoint label lineage mismatch")
    if len({row.member_seed for row in by_member}) != ensemble_size:
        raise ValueError("checkpoint member seeds are duplicated")
    if len(
        {row.bootstrap_trajectory_ids for row in by_member}
    ) != ensemble_size:
        raise ValueError("checkpoint bootstrap memberships are duplicated")
    if len({row.digest for row in by_member}) != ensemble_size:
        raise ValueError("checkpoint digests are duplicated")
    if frozen_registry_digest is not None and any(
        row.registry_digest not in {None, frozen_registry_digest}
        for row in by_member
    ):
        raise ValueError("checkpoint frozen registry lineage mismatch")
    return by_member


def _validate_calibrator(
    artifact: _CalibratorArtifact,
    manifest: dict[str, object],
    *,
    protocol_id: str,
    calibration_seeds: tuple[int, ...],
    allowed_coverages: set[float],
) -> float:
    calibrator = artifact.calibrator
    if calibrator.protocol_id != protocol_id:
        raise ValueError("calibrator protocol lineage mismatch")
    if tuple(calibrator.calibration_seeds) != calibration_seeds:
        raise ValueError("calibrator seed block mismatch")
    if tuple(map(int, calibrator.trajectory_ids)) != calibration_seeds:
        raise ValueError("calibrator trajectory IDs do not match the seed block")
    if len(calibrator.trajectory_scores) != len(calibration_seeds):
        raise ValueError("calibrator trajectory scores are incomplete")
    if calibrator.labels_manifest_digest != str(
        manifest.get("calibration_labels_digest", "")
    ):
        raise ValueError("calibrator label lineage mismatch")
    if tuple(calibrator.checkpoint_digests) != tuple(
        str(value) for value in manifest["checkpoint_digests"]
    ):
        raise ValueError("calibrator checkpoint lineage mismatch")
    coverage = float(calibrator.coverage)
    if coverage not in allowed_coverages:
        raise ValueError("calibrator coverage is outside the declared grid")
    if not np.isfinite(calibrator.q_joint) or not np.isfinite(
        calibrator.trajectory_scores
    ).all():
        raise ValueError("calibrator contains non-finite values")
    return coverage


def _record_calibrators(
    manifest: dict[str, object],
    calibrators_by_digest: Mapping[str, _CalibratorArtifact],
    *,
    protocol_id: str,
    calibration_seeds: tuple[int, ...],
    allowed_coverages: set[float],
) -> tuple[Mapping[float, Path], Mapping[float, str]]:
    primary_digest = str(manifest["calibrator_digest"])
    try:
        primary = calibrators_by_digest[primary_digest]
    except KeyError as exc:
        raise ValueError("round calibrator digest does not match an artifact") from exc
    _validate_calibrator(
        primary,
        manifest,
        protocol_id=protocol_id,
        calibration_seeds=calibration_seeds,
        allowed_coverages=allowed_coverages,
    )

    paths = {}
    digests = {}
    expected_checkpoints = tuple(
        str(value) for value in manifest["checkpoint_digests"]
    )
    expected_labels = str(manifest.get("calibration_labels_digest", ""))
    for artifact in calibrators_by_digest.values():
        calibrator = artifact.calibrator
        if (
            tuple(calibrator.checkpoint_digests) != expected_checkpoints
            or calibrator.labels_manifest_digest != expected_labels
        ):
            continue
        coverage = _validate_calibrator(
            artifact,
            manifest,
            protocol_id=protocol_id,
            calibration_seeds=calibration_seeds,
            allowed_coverages=allowed_coverages,
        )
        if coverage in paths:
            raise ValueError("calibrator coverage is duplicated for one record")
        paths[coverage] = artifact.path
        digests[coverage] = artifact.digest
    return MappingProxyType(paths), MappingProxyType(digests)


def _validate_inventory_keys(
    records: Sequence[EnsembleInventoryRecord],
    model_seeds: tuple[int, ...],
) -> None:
    keys_by_seed = {
        seed: {
            (record.ensemble_size, record.policy_round)
            for record in records
            if record.model_seed == seed
        }
        for seed in model_seeds
    }
    if any(not keys for keys in keys_by_seed.values()):
        raise ValueError("experiment inventory keys are missing a model seed")
    first = keys_by_seed[model_seeds[0]]
    if any(keys != first for keys in keys_by_seed.values()):
        raise ValueError("experiment inventory keys differ across model seeds")


def _validate_round_parents(
    records: Sequence[EnsembleInventoryRecord],
    manifests_by_digest: Mapping[str, dict[str, object]],
    *,
    reference_digest: str,
) -> None:
    for record in records:
        manifest = manifests_by_digest[record.round_digest]
        parent = str(manifest.get("parent_digest", ""))
        if record.policy_round == 1:
            if parent != reference_digest:
                raise ValueError("round-1 parent lineage mismatch")
            continue
        candidates = [
            row
            for row in records
            if row.model_seed == record.model_seed
            and row.policy_round == record.policy_round - 1
        ]
        if parent not in {row.round_digest for row in candidates}:
            raise ValueError("policy round parent lineage mismatch")


def _validate_complete_factorial(
    records: Sequence[EnsembleInventoryRecord],
    model_seeds: tuple[int, ...],
    *,
    registry: dict[str, object],
) -> None:
    expected_keys = {
        (int(ensemble_size), int(policy_round))
        for ensemble_size in registry["grid"]["ensemble_size"]
        for policy_round in registry["grid"]["policy_round"]
    }
    expected_coverages = {
        float(value) for value in registry["grid"]["joint_coverage"]
    }
    by_key = {
        (record.model_seed, record.ensemble_size, record.policy_round): record
        for record in records
    }
    for model_seed in model_seeds:
        observed_keys = {
            (record.ensemble_size, record.policy_round)
            for record in records
            if record.model_seed == model_seed
        }
        if observed_keys != expected_keys:
            raise ValueError("complete experiment factorial is missing a declared key")
        for ensemble_size, policy_round in expected_keys:
            record = by_key[(model_seed, ensemble_size, policy_round)]
            if set(record.calibrators) != expected_coverages:
                raise ValueError("complete calibration coverage factorial is missing")

        round1_k3 = by_key[(model_seed, 3, 1)]
        round1_records = [
            by_key[(model_seed, ensemble_size, 1)]
            for ensemble_size in registry["grid"]["ensemble_size"]
        ]
        if len({record.train_labels_digest for record in round1_records}) != 1:
            raise ValueError("round-1 factorial must share one training label manifest")
        if len({record.calibration_labels_digest for record in round1_records}) != 1:
            raise ValueError(
                "round-1 factorial must share one calibration label manifest"
            )
        for record in round1_records:
            payload = json.loads(
                record.round_manifest_path.read_text(encoding="utf-8")
            )
            if payload["continuation_policy"].get("name") != "paper9_mpc":
                raise ValueError("round-1 continuation policy lineage mismatch")

        round2_records = [
            by_key[(model_seed, ensemble_size, 2)]
            for ensemble_size in registry["grid"]["ensemble_size"]
        ]
        for record in round2_records:
            payload = json.loads(
                record.round_manifest_path.read_text(encoding="utf-8")
            )
            continuation = payload["continuation_policy"]
            if payload["parent_digest"] != round1_k3.round_digest:
                raise ValueError("round-2 factorial must share the round-1 K=3 parent")
            if continuation.get("name") != "pcc_round1":
                raise ValueError("round-2 continuation policy lineage mismatch")
            if int(continuation.get("model_seed", -1)) != int(model_seed):
                raise ValueError("round-2 continuation model seed mismatch")
            if tuple(continuation.get("checkpoint_digests", ())) != tuple(
                round1_k3.checkpoint_digests
            ):
                raise ValueError("round-2 continuation checkpoint lineage mismatch")
            if continuation.get("calibrator_digest") != round1_k3.calibrator_digests[
                0.9
            ]:
                raise ValueError("round-2 continuation calibrator lineage mismatch")
            if float(continuation.get("joint_coverage", -1.0)) != 0.9:
                raise ValueError("round-2 continuation coverage mismatch")
        if len({record.train_labels_digest for record in round2_records}) != 1:
            raise ValueError("round-2 factorial must share one training label manifest")
        if len({record.calibration_labels_digest for record in round2_records}) != 1:
            raise ValueError("round-2 factorial must share one calibration label manifest")


def build_inventory(
    root: str | Path,
    *,
    calibrator_root: str | Path | None = None,
    model_seeds: Sequence[int],
    registry: dict[str, object] | None = None,
    require_complete: bool = False,
) -> ExperimentInventory:
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"experiment inventory root does not exist: {root}")
    calibrator_root = (
        root if calibrator_root is None else Path(calibrator_root).resolve()
    )
    if not calibrator_root.is_dir():
        raise FileNotFoundError(
            f"calibrator inventory root does not exist: {calibrator_root}"
        )
    registry = load_registry() if registry is None else registry
    validate_registry(registry)
    expected_model_seeds = tuple(int(value) for value in model_seeds)
    if not expected_model_seeds or len(set(expected_model_seeds)) != len(
        expected_model_seeds
    ):
        raise ValueError("model seeds must be non-empty and distinct")
    if not set(expected_model_seeds) <= {
        int(value) for value in registry["model_seeds"]
    }:
        raise ValueError("model seeds are outside the declared registry")

    frozen_registry_digest = None
    if registry.get("status") == "frozen":
        frozen_registry_digest = verify_frozen_registry(registry)
    checkpoints = _checkpoint_artifacts(root)
    calibrators = _calibrator_artifacts(calibrator_root)
    manifests = _round_manifests(root)
    protocol_id = str(registry["protocol_id"])
    calibration_seeds = tuple(
        int(value) for value in registry["partitions"]["calibration"]
    )
    allowed_coverages = {
        float(value) for value in registry["grid"]["joint_coverage"]
    }

    records = []
    manifests_by_digest = {}
    for manifest_path, manifest in manifests:
        model_seed = int(manifest["model_seed"])
        if model_seed not in expected_model_seeds:
            continue
        round_index = int(manifest["round_index"])
        if round_index not in {
            int(value) for value in registry["grid"]["policy_round"]
        }:
            raise ValueError("policy round is outside the declared grid")
        checkpoint_group = _validate_checkpoint_group(
            manifest,
            checkpoints,
            protocol_id=protocol_id,
            frozen_registry_digest=frozen_registry_digest,
        )
        checkpoint_roots = {row.path.parent for row in checkpoint_group}
        if len(checkpoint_roots) != 1:
            raise ValueError("ensemble checkpoints do not share one physical root")
        calibrator_paths, calibrator_digests = _record_calibrators(
            manifest,
            calibrators,
            protocol_id=protocol_id,
            calibration_seeds=calibration_seeds,
            allowed_coverages=allowed_coverages,
        )
        round_digest = str(manifest["round_digest"])
        if round_digest in manifests_by_digest:
            raise ValueError("policy round digest identifies multiple manifests")
        manifests_by_digest[round_digest] = manifest
        records.append(
            EnsembleInventoryRecord(
                model_seed=model_seed,
                ensemble_size=len(checkpoint_group),
                policy_round=round_index,
                checkpoint_root=next(iter(checkpoint_roots)),
                checkpoint_paths=tuple(row.path for row in checkpoint_group),
                checkpoint_digests=tuple(row.digest for row in checkpoint_group),
                calibrators=calibrator_paths,
                calibrator_digests=calibrator_digests,
                round_manifest_path=manifest_path,
                round_digest=round_digest,
                train_labels_digest=str(manifest.get("train_labels_digest", "")),
                calibration_labels_digest=str(
                    manifest.get("calibration_labels_digest", "")
                ),
            )
        )
    records.sort(
        key=lambda row: (row.model_seed, row.ensemble_size, row.policy_round)
    )
    _validate_inventory_keys(records, expected_model_seeds)
    _validate_round_parents(
        records,
        manifests_by_digest,
        reference_digest=str(
            registry["offline_reference_policy"]["checkpoint_sha256"]
        ),
    )
    if require_complete:
        _validate_complete_factorial(
            records,
            expected_model_seeds,
            registry=registry,
        )
    return ExperimentInventory(tuple(records))


def _summary_checkpoint_path(summary_path: Path, raw_path: object) -> Path:
    path = Path(str(raw_path))
    if not path.is_absolute():
        path = summary_path.parent / path
    return path.resolve()


def audit_checkpoint_only_inventory(
    root: str | Path,
    *,
    registry: dict[str, object],
    model_seeds: Sequence[int],
) -> dict[str, object]:
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"checkpoint inventory root does not exist: {root}")
    validate_registry(registry)
    expected_models = tuple(int(value) for value in model_seeds)
    if (
        not expected_models
        or len(expected_models) != len(set(expected_models))
        or not set(expected_models).issubset(
            {int(value) for value in registry["model_seeds"]}
        )
    ):
        raise ValueError("checkpoint-only model seeds are invalid")
    expected_sizes = tuple(
        sorted(int(value) for value in registry["grid"]["ensemble_size"])
    )
    expected_keys = {
        (model_seed, ensemble_size)
        for model_seed in expected_models
        for ensemble_size in expected_sizes
    }

    summaries = {}
    for path, payload in _json_payloads(root):
        if payload.get("region") != "bishan" or "checkpoints" not in payload:
            continue
        key = (
            int(payload.get("model_seed", -1)),
            int(payload.get("ensemble_size", -1)),
        )
        if key in summaries:
            raise ValueError("checkpoint-only training summary is duplicated")
        summaries[key] = (path, payload)
    if set(summaries) != expected_keys:
        raise ValueError("checkpoint-only training factorial is incomplete")

    records = []
    all_digests = []
    all_member_seeds = []
    all_label_digests = []
    for model_seed, ensemble_size in sorted(expected_keys):
        summary_path, summary = summaries[(model_seed, ensemble_size)]
        if (
            summary.get("protocol_id") != registry["protocol_id"]
            or summary.get("registry_digest") is not None
            or summary.get("region") != "bishan"
            or summary.get("trainable_scope") != "all"
            or summary.get("representation") != "action_relative"
            or summary.get("county_action_count") is not None
            or summary.get("parent_checkpoint_digests") != []
        ):
            raise ValueError("checkpoint-only training summary lineage mismatch")
        checkpoint_rows = summary.get("checkpoints")
        if (
            not isinstance(checkpoint_rows, list)
            or len(checkpoint_rows) != ensemble_size
        ):
            raise ValueError("checkpoint-only member block is incomplete")

        block_digests = []
        block_member_seeds = []
        block_bootstraps = []
        block_label_digests = []
        for expected_member, row in enumerate(checkpoint_rows):
            checkpoint_path = _summary_checkpoint_path(summary_path, row["path"])
            if not checkpoint_path.is_relative_to(root):
                raise ValueError("checkpoint-only member is outside the inventory root")
            if not checkpoint_path.is_file():
                raise FileNotFoundError("checkpoint-only member file is missing")
            digest = _sha256_file(checkpoint_path)
            if digest != str(row.get("sha256", "")):
                raise ValueError("checkpoint-only physical digest mismatch")
            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=False,
            )
            if int(checkpoint.get("ensemble_size", -1)) != ensemble_size:
                raise ValueError("checkpoint-only member ensemble size mismatch")
            if (
                int(checkpoint.get("model_seed", -1)) != model_seed
                or int(checkpoint.get("member_index", -1)) != expected_member
                or checkpoint.get("protocol_id") != registry["protocol_id"]
                or checkpoint.get("region") != "bishan"
                or checkpoint.get("trainable_scope") != "all"
                or tuple(checkpoint.get("objective_names", ()))
                != OBJECTIVE_NAMES
            ):
                raise ValueError("checkpoint-only member lineage mismatch")
            member_seed = int(checkpoint.get("member_seed", -1))
            bootstrap = tuple(
                int(value)
                for value in checkpoint.get("bootstrap_trajectory_ids", [])
            )
            labels_digest = str(checkpoint.get("labels_manifest_digest", ""))
            if (
                member_seed < 0
                or len(bootstrap) != len(registry["partitions"]["train"])
                or not set(bootstrap).issubset(
                    {int(value) for value in registry["partitions"]["train"]}
                )
                or not labels_digest
            ):
                raise ValueError("checkpoint-only member data lineage mismatch")
            block_digests.append(digest)
            block_member_seeds.append(member_seed)
            block_bootstraps.append(bootstrap)
            block_label_digests.append(labels_digest)
        if (
            len(set(block_digests)) != ensemble_size
            or len(set(block_member_seeds)) != ensemble_size
            or len(set(block_bootstraps)) != ensemble_size
            or len(set(block_label_digests)) != 1
        ):
            raise ValueError("checkpoint-only ensemble members are duplicated")
        all_digests.extend(block_digests)
        all_member_seeds.extend(block_member_seeds)
        all_label_digests.extend(block_label_digests)
        records.append(
            {
                "model_seed": model_seed,
                "ensemble_size": ensemble_size,
                "summary_path": str(summary_path),
                "summary_sha256": _sha256_file(summary_path),
                "checkpoint_digests": block_digests,
                "member_seeds": block_member_seeds,
                "bootstrap_trajectory_ids": [list(row) for row in block_bootstraps],
                "labels_manifest_digest": block_label_digests[0],
            }
        )
    if len(set(all_digests)) != len(all_digests):
        raise ValueError("checkpoint-only checkpoint is reused across ensembles")
    if len(set(all_member_seeds)) != len(all_member_seeds):
        raise ValueError("checkpoint-only member seed is reused across ensembles")
    if len(set(all_label_digests)) != 1:
        raise ValueError("checkpoint-only training label lineage is inconsistent")
    return {
        "passed": True,
        "protocol_id": registry["protocol_id"],
        "root": str(root),
        "model_seeds": list(expected_models),
        "ensemble_sizes": list(expected_sizes),
        "n_summaries": len(records),
        "n_checkpoints": len(all_digests),
        "labels_manifest_digest": all_label_digests[0],
        "records": records,
    }


def build_adapted_inventory(
    root: str | Path,
    *,
    calibrator_root: str | Path,
    registry: dict[str, object],
) -> ExperimentInventory:
    root = Path(root).resolve()
    calibrator_root = Path(calibrator_root).resolve()
    if not root.is_dir() or not calibrator_root.is_dir():
        raise FileNotFoundError("adapted checkpoint or calibrator root is missing")
    validate_registry(registry)
    frozen_digest = verify_frozen_registry(registry)
    selected = registry["selected_config"]
    model_seeds = tuple(int(value) for value in registry["model_seeds"])
    ensemble_size = int(selected["ensemble_size"])
    policy_round = int(selected["policy_round"])
    coverage = float(selected["joint_coverage"])
    parent_digests = tuple(str(value) for value in selected["checkpoint_digests"])
    if (
        len(parent_digests) != len(model_seeds) * ensemble_size
        or len(parent_digests) != len(set(parent_digests))
    ):
        raise ValueError("frozen parent checkpoint lineage is incomplete")

    summaries = []
    for path, payload in _json_payloads(root):
        if payload.get("region") == "dongxing" and "checkpoints" in payload:
            summaries.append((path, payload))
    by_model = {}
    for path, summary in summaries:
        model_seed = int(summary.get("model_seed", -1))
        if model_seed in by_model:
            raise ValueError("Dongxing training summary is duplicated")
        by_model[model_seed] = (path, summary)
    if set(by_model) != set(model_seeds):
        raise ValueError("Dongxing training summaries are incomplete")

    calibrator_artifacts = _calibrator_artifacts(calibrator_root)
    calibration_seeds = tuple(
        int(value) for value in registry["partitions"]["dongxing_calibration"]
    )
    adaptation_seeds = frozenset(
        int(value) for value in registry["partitions"]["dongxing_adaptation"]
    )
    records = []
    all_adapted_digests = []
    for model_index, model_seed in enumerate(model_seeds):
        summary_path, summary = by_model[model_seed]
        expected_parents = parent_digests[
            model_index * ensemble_size : (model_index + 1) * ensemble_size
        ]
        if (
            summary.get("adaptation_hyperparameters")
            != registry["dongxing_adaptation_training"]
        ):
            raise ValueError("Dongxing adaptation hyperparameters mismatch")
        if (
            summary.get("protocol_id") != registry["protocol_id"]
            or summary.get("registry_digest") != frozen_digest
            or summary.get("region") != "dongxing"
            or summary.get("trainable_scope") != "objective_heads"
            or int(summary.get("ensemble_size", -1)) != ensemble_size
            or tuple(map(str, summary.get("parent_checkpoint_digests", [])))
            != expected_parents
        ):
            raise ValueError("Dongxing training summary lineage mismatch")
        checkpoint_rows = summary.get("checkpoints")
        if not isinstance(checkpoint_rows, list) or len(checkpoint_rows) != ensemble_size:
            raise ValueError("Dongxing checkpoint block is incomplete")
        checkpoints = []
        adaptation_label_digests = set()
        bootstrap_blocks = set()
        for member_index, row in enumerate(checkpoint_rows):
            checkpoint_path = _summary_checkpoint_path(summary_path, row["path"])
            if not checkpoint_path.is_file():
                raise FileNotFoundError("Dongxing adapted checkpoint is missing")
            digest = _sha256_file(checkpoint_path)
            if digest != str(row.get("sha256")):
                raise ValueError("Dongxing adapted checkpoint digest mismatch")
            checkpoint = torch.load(
                checkpoint_path,
                map_location="cpu",
                weights_only=False,
            )
            trainable_names = tuple(
                str(value) for value in checkpoint.get("trainable_parameter_names", [])
            )
            if tuple(checkpoint.get("objective_names", ())) != OBJECTIVE_NAMES:
                raise ValueError("Dongxing objective order mismatch")
            if (
                int(checkpoint.get("model_seed", -1)) != model_seed
                or int(checkpoint.get("ensemble_size", -1)) != ensemble_size
                or int(checkpoint.get("member_index", -1)) != member_index
                or checkpoint.get("registry_digest") != frozen_digest
                or checkpoint.get("protocol_id") != registry["protocol_id"]
                or checkpoint.get("region") != "dongxing"
                or checkpoint.get("trainable_scope") != "objective_heads"
                or checkpoint.get("parent_checkpoint_sha256")
                != expected_parents[member_index]
                or not trainable_names
                or not all(
                    name.startswith(("immediate_head.", "horizon_head."))
                    for name in trainable_names
                )
            ):
                raise ValueError("Dongxing adapted checkpoint lineage mismatch")
            adaptation_digest = str(
                checkpoint.get("adaptation_labels_manifest_digest", "")
            )
            if (
                not adaptation_digest
                or adaptation_digest
                != str(checkpoint.get("labels_manifest_digest", ""))
            ):
                raise ValueError("Dongxing adaptation label lineage mismatch")
            adaptation_label_digests.add(adaptation_digest)
            bootstrap = tuple(
                int(value)
                for value in checkpoint.get("bootstrap_trajectory_ids", [])
            )
            if (
                len(bootstrap) != len(adaptation_seeds)
                or not set(bootstrap).issubset(adaptation_seeds)
            ):
                raise ValueError("Dongxing bootstrap adaptation partition mismatch")
            bootstrap_blocks.add(bootstrap)
            checkpoints.append((checkpoint_path, digest))
        if len(adaptation_label_digests) != 1:
            raise ValueError("Dongxing adaptation label lineage is inconsistent")
        if len(bootstrap_blocks) != ensemble_size:
            raise ValueError("Dongxing bootstrap memberships are duplicated")
        checkpoint_digests = tuple(digest for _, digest in checkpoints)
        if len(checkpoint_digests) != len(set(checkpoint_digests)):
            raise ValueError("Dongxing adapted checkpoint digests are duplicated")
        all_adapted_digests.extend(checkpoint_digests)

        matching_calibrators = []
        for artifact in calibrator_artifacts.values():
            calibrator = artifact.calibrator
            if tuple(calibrator.checkpoint_digests) == checkpoint_digests:
                matching_calibrators.append(artifact)
        if len(matching_calibrators) != 1:
            raise ValueError("Dongxing frozen-coverage calibrator is missing or duplicated")
        artifact = matching_calibrators[0]
        calibration_manifest = {
            "checkpoint_digests": list(checkpoint_digests),
            "calibration_labels_digest": artifact.calibrator.labels_manifest_digest,
        }
        observed_coverage = _validate_calibrator(
            artifact,
            calibration_manifest,
            protocol_id=str(registry["protocol_id"]),
            calibration_seeds=calibration_seeds,
            allowed_coverages={coverage},
        )
        records.append(
            EnsembleInventoryRecord(
                model_seed=model_seed,
                ensemble_size=ensemble_size,
                policy_round=policy_round,
                checkpoint_root=checkpoints[0][0].parent,
                checkpoint_paths=tuple(path for path, _ in checkpoints),
                checkpoint_digests=checkpoint_digests,
                calibrators=MappingProxyType(
                    {observed_coverage: artifact.path}
                ),
                calibrator_digests=MappingProxyType(
                    {observed_coverage: artifact.digest}
                ),
                round_manifest_path=summary_path,
                round_digest=_sha256_file(summary_path),
                train_labels_digest=next(iter(adaptation_label_digests)),
                calibration_labels_digest=(
                    artifact.calibrator.labels_manifest_digest
                ),
            )
        )
    if len({record.train_labels_digest for record in records}) != 1:
        raise ValueError("Dongxing models require one shared adaptation label manifest")
    if len({record.calibration_labels_digest for record in records}) != 1:
        raise ValueError("Dongxing models require one shared calibration label manifest")
    if len(all_adapted_digests) != len(set(all_adapted_digests)):
        raise ValueError("Dongxing adapted checkpoints are reused across model seeds")
    return ExperimentInventory(tuple(records))


def _parse_model_seeds(specification: str) -> tuple[int, ...]:
    values = tuple(
        int(token.strip())
        for token in str(specification).split(",")
        if token.strip()
    )
    if not values:
        raise ValueError("--model-seeds must contain at least one seed")
    return values


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--model-seeds", required=True)
    parser.add_argument("--checkpoint-only", action="store_true")
    parser.add_argument("--output-json", default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    model_seeds = _parse_model_seeds(args.model_seeds)
    if args.checkpoint_only:
        report = audit_checkpoint_only_inventory(
            args.root,
            registry=registry,
            model_seeds=model_seeds,
        )
    else:
        report = build_inventory(
            args.root,
            model_seeds=model_seeds,
            registry=registry,
            require_complete=True,
        ).report()
    rendered = json.dumps(
        report,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
    )
    if args.output_json is not None:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        temporary.replace(path)
    print(rendered)


if __name__ == "__main__":
    main()
