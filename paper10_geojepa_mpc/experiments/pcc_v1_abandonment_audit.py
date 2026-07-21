import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sha256(value: str, *, field: str) -> str:
    value = str(value)
    if len(value) != 64:
        raise ValueError(f"{field} must be SHA-256")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError(f"{field} must be SHA-256") from error
    return value


def _validate_timestamp(value: str) -> str:
    value = str(value)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("stop_verified_at must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise ValueError("stop_verified_at must include a timezone")
    return value


def audit_abandoned_pcc_v1(
    run_root: str | Path,
    *,
    round0_root: str | Path,
    registry_digest: str,
    stop_verified_at: str,
    confirmation_seeds_run: Sequence[int] = (),
) -> dict[str, object]:
    run_root = Path(run_root).resolve()
    round0_root = Path(round0_root).resolve()
    registry_digest = _validate_sha256(
        registry_digest,
        field="registry_digest",
    )
    stop_verified_at = _validate_timestamp(stop_verified_at)
    confirmation = sorted(map(int, confirmation_seeds_run))
    if confirmation:
        raise ValueError("PCC v1 abandonment audit forbids confirmation seeds")

    complete: list[int] = []
    incomplete: list[str] = []
    identical: list[int] = []
    artifacts: list[dict[str, object]] = []
    train_root = (
        run_root / "seed_5101" / "round2" / "labels" / "train"
    )
    for seed_dir in sorted(train_root.glob("seed_*")):
        manifest_path = seed_dir / "manifest.json"
        if not manifest_path.is_file():
            incomplete.append(seed_dir.name)
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact_rows = list(manifest["artifacts"])
            if len(artifact_rows) != 1:
                raise ValueError("seed manifest must contain one artifact")
            artifact = dict(artifact_rows[0])
            seed = int(artifact["trajectory_seed"])
            if seed_dir.name != f"seed_{seed}":
                raise ValueError("seed directory and manifest disagree")
            path = seed_dir / str(artifact["path"])
            observed_digest = _sha256_file(path)
            if observed_digest != str(artifact["sha256"]):
                raise ValueError("seed artifact digest mismatch")
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
            incomplete.append(seed_dir.name)
            continue

        complete.append(seed)
        round0_path = (
            round0_root / f"seed_{seed}" / f"trajectory_{seed}.npz"
        )
        if (
            round0_path.is_file()
            and _sha256_file(round0_path) == observed_digest
        ):
            identical.append(seed)
        artifacts.append(
            {
                "seed": seed,
                "path": str(path),
                "sha256": observed_digest,
            }
        )

    return {
        "schema_version": 1,
        "protocol_id": "pcc_v1",
        "status": "abandoned_before_freeze",
        "registry_digest": registry_digest,
        "stop_verified_at": stop_verified_at,
        "completed_round2_train_seeds": sorted(complete),
        "byte_identical_to_round0_seeds": sorted(identical),
        "incomplete_seed_directories": sorted(incomplete),
        "artifacts": sorted(artifacts, key=lambda row: int(row["seed"])),
        "confirmation_seeds_run": confirmation,
        "eligible_for_pcc_v1_1_resume": False,
    }


def _write_json_atomic(path: str | Path, payload: dict[str, object]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(
                f"refusing to overwrite different audit: {path}"
            ) from error
        if existing != payload:
            raise ValueError(f"refusing to overwrite different audit: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_markdown_atomic(path: str | Path, payload: dict[str, object]) -> None:
    path = Path(path)
    completed = ", ".join(
        map(str, payload["completed_round2_train_seeds"])
    )
    identical = ", ".join(
        map(str, payload["byte_identical_to_round0_seeds"])
    )
    content = "\n".join(
        [
            "# PCC v1 Abandonment Audit",
            "",
            f"- Status: {payload['status']}",
            f"- Stop verified at: {payload['stop_verified_at']}",
            f"- Completed round-2 train seeds: {completed}",
            f"- Byte-identical round-0 seeds: {identical}",
            "- Confirmation seeds run: none",
            "- Eligible for PCC v1.1 resume: false",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        if path.read_text(encoding="utf-8") != content:
            raise ValueError(f"refusing to overwrite different audit: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _parse_seeds(specification: str) -> tuple[int, ...]:
    return tuple(
        int(token.strip())
        for token in specification.split(",")
        if token.strip()
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--round0-root", required=True)
    parser.add_argument("--stop-verified-at", required=True)
    parser.add_argument("--confirmation-seeds-run", default="")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    report = audit_abandoned_pcc_v1(
        args.run_root,
        round0_root=args.round0_root,
        registry_digest=_sha256_file(args.registry),
        stop_verified_at=args.stop_verified_at,
        confirmation_seeds_run=_parse_seeds(args.confirmation_seeds_run),
    )
    _write_json_atomic(args.output_json, report)
    _write_markdown_atomic(args.output_md, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
