import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)


def _canonical_manifest(payload: dict[str, object]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "manifest_digest"}
    return json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _seed_range(seeds) -> str:
    values = tuple(map(int, seeds))
    if not values:
        return "none"
    if values == tuple(range(values[0], values[-1] + 1)):
        return f"{values[0]}-{values[-1]}"
    return ",".join(map(str, values))


def audit_manifest(
    path: str | Path,
    *,
    registry: dict[str, object],
    partition: str,
) -> dict[str, object]:
    manifest_path = Path(path).resolve()
    manifest_root = manifest_path.parent.resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_digest = payload.get("manifest_digest")
    observed_digest = _sha256_bytes(_canonical_manifest(payload))
    if expected_digest != observed_digest:
        raise ValueError(f"label manifest digest mismatch: {manifest_path}")
    if payload.get("protocol_id") != registry.get("protocol_id"):
        raise ValueError(f"label manifest protocol mismatch: {manifest_path}")
    if payload.get("partition") != partition:
        raise ValueError(f"label manifest partition mismatch: {manifest_path}")
    if payload.get("horizons") != registry.get("horizons"):
        raise ValueError(f"label manifest horizon mismatch: {manifest_path}")

    expected_seeds = tuple(map(int, registry["partitions"][partition]))
    observed_seeds = tuple(map(int, payload.get("trajectory_seeds", [])))
    if observed_seeds != expected_seeds:
        raise ValueError(f"label manifest seed block mismatch: {manifest_path}")

    reference = registry["offline_reference_policy"]
    continuation = payload.get("continuation_policy", {})
    expected_continuation = {
        "name": reference["name"],
        "checkpoint_sha256": reference["checkpoint_sha256"],
        "planning_horizon": reference["planning_horizon"],
        "top_k": reference["top_k"],
        "gamma": reference["gamma"],
    }
    for key, value in expected_continuation.items():
        if continuation.get(key) != value:
            raise ValueError(
                f"continuation policy mismatch for {key}: {manifest_path}"
            )

    sampling = registry["offline_sampling"][partition]
    artifacts = payload.get("artifacts", [])
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_seeds):
        raise ValueError(f"label artifact count mismatch: {manifest_path}")
    artifact_seeds = []
    artifact_digests = []
    for artifact in artifacts:
        seed = int(artifact.get("trajectory_seed", -1))
        artifact_seeds.append(seed)
        if int(artifact.get("n_states", -1)) != int(
            sampling["states_per_trajectory"]
        ):
            raise ValueError(f"label artifact state count mismatch: {manifest_path}")
        if int(artifact.get("n_candidates", -1)) != int(
            sampling["candidate_actions"]
        ):
            raise ValueError(
                f"label artifact candidate count mismatch: {manifest_path}"
            )
        artifact_path = (manifest_root / str(artifact.get("path", ""))).resolve()
        if not _inside_root(artifact_path, manifest_root):
            raise ValueError(f"label artifact is outside manifest root: {artifact_path}")
        if not artifact_path.is_file():
            raise ValueError(f"label artifact is missing: {artifact_path}")
        digest = _sha256_file(artifact_path)
        if digest != artifact.get("sha256"):
            raise ValueError(f"label artifact digest mismatch: {artifact_path}")
        artifact_digests.append(digest)
    if tuple(artifact_seeds) != expected_seeds:
        raise ValueError(f"label artifact seed order mismatch: {manifest_path}")
    if len(set(artifact_digests)) != len(artifact_digests):
        raise ValueError(f"label artifact digests are duplicated: {manifest_path}")

    return {
        "manifest_path": manifest_path.as_posix(),
        "manifest_digest": str(expected_digest),
        "manifest_file_sha256": _sha256_file(manifest_path),
        "partition": partition,
        "trajectory_seeds": list(expected_seeds),
        "seed_range": _seed_range(expected_seeds),
        "artifact_count": len(artifacts),
        "artifact_digests": artifact_digests,
        "states_per_trajectory": int(sampling["states_per_trajectory"]),
        "candidate_actions": int(sampling["candidate_actions"]),
        "continuation_policy": dict(continuation),
    }


def audit_pcc_inputs(
    registry: dict[str, object],
    train_manifest: str | Path,
    calibration_manifest: str | Path,
) -> dict[str, object]:
    validate_registry(registry)
    if registry.get("status") != "development":
        raise ValueError("PCC input audit must precede protocol freeze")
    train = audit_manifest(train_manifest, registry=registry, partition="train")
    calibration = audit_manifest(
        calibration_manifest,
        registry=registry,
        partition="calibration",
    )
    if train["continuation_policy"] != calibration["continuation_policy"]:
        raise ValueError("train and calibration continuation policies differ")
    return {
        "schema_version": 1,
        "protocol_id": registry["protocol_id"],
        "protocol_status": registry["status"],
        "passed": True,
        "continuation_policy": registry["offline_reference_policy"]["name"],
        "train": train,
        "calibration": calibration,
    }


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write_audit_outputs(
    report: dict[str, object],
    *,
    output_json: str | Path,
    output_md: str | Path,
) -> None:
    _write_atomic(
        Path(output_json),
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
    )
    train = report["train"]
    calibration = report["calibration"]
    markdown = [
        "# PCC v1 immutable input audit",
        "",
        f"- Status: `{'PASS' if report['passed'] else 'FAIL'}`",
        f"- Protocol: `{report['protocol_id']}` (`{report['protocol_status']}`)",
        "- Continuation policy: `Paper9 MPC` (`paper9_mpc`)",
        "",
        "| Partition | Seeds | Artifacts | States per trajectory | Candidates | Manifest digest |",
        "| --- | --- | ---: | ---: | ---: | --- |",
        (
            f"| Train | {train['seed_range']} | {train['artifact_count']} | "
            f"{train['states_per_trajectory']} | {train['candidate_actions']} | "
            f"`{train['manifest_digest']}` |"
        ),
        (
            f"| Calibration | {calibration['seed_range']} | "
            f"{calibration['artifact_count']} | "
            f"{calibration['states_per_trajectory']} | "
            f"{calibration['candidate_actions']} | "
            f"`{calibration['manifest_digest']}` |"
        ),
        "",
        f"- Train manifest: `{train['manifest_path']}`",
        f"- Calibration manifest: `{calibration['manifest_path']}`",
        "",
    ]
    _write_atomic(Path(output_md), "\n".join(markdown))


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--train-manifest", required=True)
    parser.add_argument("--calibration-manifest", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    report = audit_pcc_inputs(
        registry,
        args.train_manifest,
        args.calibration_manifest,
    )
    write_audit_outputs(
        report,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
