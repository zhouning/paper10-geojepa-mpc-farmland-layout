import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
from typing import Sequence

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)
from paper10_geojepa_mpc.experiments.pcc_value_labels import write_label_manifest


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_valid_seed_manifest(path: Path, expected_seed: int):
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected = payload.get("manifest_digest")
        clean = {
            key: value for key, value in payload.items() if key != "manifest_digest"
        }
        canonical = json.dumps(
            clean,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        if expected != hashlib.sha256(canonical).hexdigest():
            return None
        if payload.get("trajectory_seeds") != [int(expected_seed)]:
            return None
        artifacts = payload.get("artifacts", [])
        if len(artifacts) != 1:
            return None
        artifact_path = path.parent / artifacts[0]["path"]
        if not artifact_path.exists() or _sha256_file(artifact_path) != artifacts[0][
            "sha256"
        ]:
            return None
        return payload
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def valid_completed_seeds(output_root: str | Path, seeds) -> set[int]:
    output_root = Path(output_root)
    completed = set()
    for raw_seed in seeds:
        seed = int(raw_seed)
        manifest = output_root / f"seed_{seed}" / "manifest.json"
        if _load_valid_seed_manifest(manifest, seed) is not None:
            completed.add(seed)
    return completed


def merge_seed_manifests(
    output_root: str | Path,
    *,
    expected_protocol_id: str,
    expected_partition: str,
    expected_seeds,
):
    output_root = Path(output_root)
    manifests = []
    for raw_seed in expected_seeds:
        seed = int(raw_seed)
        path = output_root / f"seed_{seed}" / "manifest.json"
        payload = _load_valid_seed_manifest(path, seed)
        if payload is None:
            raise ValueError(f"seed artifact is missing or invalid: {seed}")
        if payload["protocol_id"] != expected_protocol_id:
            raise ValueError("seed manifest protocol mismatch")
        if payload["partition"] != expected_partition:
            raise ValueError("seed manifest partition mismatch")
        manifests.append(payload)

    horizons = manifests[0]["horizons"]
    continuation_policy = manifests[0]["continuation_policy"]
    artifacts = []
    for seed, payload in zip(expected_seeds, manifests):
        if payload["horizons"] != horizons:
            raise ValueError("seed manifest horizon mismatch")
        if payload["continuation_policy"] != continuation_policy:
            raise ValueError("seed continuation policy mismatch")
        artifact = dict(payload["artifacts"][0])
        artifact["path"] = (
            Path(f"seed_{int(seed)}") / str(artifact["path"])
        ).as_posix()
        artifacts.append(artifact)
    return write_label_manifest(
        output_root,
        protocol_id=expected_protocol_id,
        partition=expected_partition,
        artifacts=artifacts,
        continuation_policy=continuation_policy,
        horizons=horizons,
    )


def _parse_seed_spec(spec: str) -> list[int]:
    seeds = []
    for token in str(spec).split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start, end = int(start_text), int(end_text)
            if end < start:
                raise ValueError("seed range end must not precede start")
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(token))
    return seeds


def _run_seed_job(command: list[str], log_path: Path) -> int:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"label job failed; see {log_path}")
    return result.returncode


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--partition", required=True)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--env-source", choices=("paper9", "neijiang"), default="paper9")
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--reference-checkpoint", default=None)
    parser.add_argument("--states-per-trajectory", type=int, default=None)
    parser.add_argument("--candidate-actions", type=int, default=None)
    parser.add_argument("--horizons", default="1,3,5")
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--reference-horizon", type=int, default=5)
    parser.add_argument("--reference-top-k", type=int, default=50)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-root", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    declared = [int(value) for value in registry["partitions"][args.partition]]
    seeds = _parse_seed_spec(args.seeds) if args.seeds else declared
    if not seeds or len(seeds) != len(set(seeds)) or not set(seeds) <= set(declared):
        raise ValueError("job seeds must be a unique subset of the declared partition")
    sampling = registry["offline_sampling"].get(args.partition)
    if sampling is None:
        raise ValueError("partition has no declared offline sampling configuration")
    states = int(
        args.states_per_trajectory
        if args.states_per_trajectory is not None
        else sampling["states_per_trajectory"]
    )
    candidates = int(
        args.candidate_actions
        if args.candidate_actions is not None
        else sampling["candidate_actions"]
    )
    output_root = Path(args.output_root)
    completed = valid_completed_seeds(output_root, seeds) if args.resume else set()
    pending = [seed for seed in seeds if seed not in completed]

    commands = {}
    for seed in pending:
        seed_dir = output_root / f"seed_{seed}"
        command = [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.pcc_value_labels",
            "--registry",
            str(args.registry),
            "--partition",
            str(args.partition),
            "--seeds",
            str(seed),
            "--env-source",
            str(args.env_source),
            "--prepared-dir",
            str(args.prepared_dir),
            "--states-per-trajectory",
            str(states),
            "--candidate-actions",
            str(candidates),
            "--horizons",
            str(args.horizons),
            "--gamma",
            str(args.gamma),
            "--planning-horizon",
            str(args.reference_horizon),
            "--top-k",
            str(args.reference_top_k),
            "--device",
            str(args.device),
            "--output-dir",
            str(seed_dir),
        ]
        if args.reference_checkpoint:
            command.extend(["--reference-checkpoint", str(args.reference_checkpoint)])
        commands[seed] = command

    with ThreadPoolExecutor(max_workers=int(args.max_workers)) as executor:
        futures = {
            executor.submit(
                _run_seed_job,
                command,
                output_root / f"seed_{seed}" / "job.log",
            ): seed
            for seed, command in commands.items()
        }
        for future in as_completed(futures):
            future.result()

    manifest = merge_seed_manifests(
        output_root,
        expected_protocol_id=str(registry["protocol_id"]),
        expected_partition=str(args.partition),
        expected_seeds=seeds,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
