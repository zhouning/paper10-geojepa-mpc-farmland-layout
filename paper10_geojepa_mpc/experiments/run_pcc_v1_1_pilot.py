import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_digest(payload: dict[str, object], *, digest_field: str) -> str:
    clean = {key: value for key, value in payload.items() if key != digest_field}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _write_json_once(path: str | Path, payload: dict[str, object]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"existing JSON is invalid: {path}") from exc
        if existing != payload:
            raise ValueError(f"refusing to replace incompatible JSON: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_json_atomic(path: str | Path, payload: dict[str, object]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _file_digest_rows(paths) -> list[dict[str, str]]:
    rows = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_file():
            raise FileNotFoundError(f"pilot input or output is missing: {path}")
        rows.append(
            {
                "path": str(path.resolve()),
                "sha256": _sha256_file(path),
            }
        )
    return rows


def _validate_external_inputs(
    *,
    registry,
    registry_path: str | Path,
    registry_digest: str,
    train_manifest: str | Path,
    reference_checkpoint: str | Path,
) -> list[dict[str, object]]:
    manifest_path = Path(train_manifest)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("pilot train manifest is unreadable") from exc
    if (
        manifest.get("protocol_id") != registry["source_inputs"]["protocol_id"]
        or manifest.get("partition") != "train"
        or manifest.get("manifest_digest")
        != registry["source_inputs"]["train_manifest_digest"]
    ):
        raise ValueError("pilot train manifest lineage mismatch")
    reference_digest = _sha256_file(reference_checkpoint)
    if reference_digest != registry["model"]["transfer_checkpoint_sha256"]:
        raise ValueError("pilot reference checkpoint digest mismatch")
    inputs = [
        {
            "kind": "registry",
            "path": str(Path(registry_path).resolve()),
            "sha256": str(registry_digest),
        },
        {
            "kind": "train_manifest",
            "path": str(manifest_path.resolve()),
            "sha256": _sha256_file(manifest_path),
            "manifest_digest": manifest["manifest_digest"],
        },
        {
            "kind": "reference_checkpoint",
            "path": str(Path(reference_checkpoint).resolve()),
            "sha256": reference_digest,
        },
    ]
    for artifact in manifest.get("artifacts", []):
        path = manifest_path.parent / str(artifact["path"])
        digest = _sha256_file(path)
        if digest != str(artifact.get("sha256")):
            raise ValueError("pilot train artifact digest mismatch")
        inputs.append(
            {
                "kind": "train_artifact",
                "trajectory_seed": int(artifact["trajectory_seed"]),
                "path": str(path.resolve()),
                "sha256": digest,
            }
        )
    return inputs


def _option(command: Sequence[str], name: str) -> str:
    index = list(command).index(name)
    return str(command[index + 1])


def _selected_outputs(root: Path, seeds) -> list[str]:
    outputs = [
        str(root / "execution_plan.json"),
        str(root / "manifest.json"),
    ]
    for seed in seeds:
        outputs.extend(
            [
                str(root / f"seed_{seed}" / "manifest.json"),
                str(root / f"seed_{seed}" / f"trajectory_{seed}.npz"),
            ]
        )
    return outputs


def _job(
    root: Path,
    *,
    job_id: str,
    phase: str,
    command,
    registry_digest: str,
    input_paths,
    expected_outputs,
) -> dict[str, object]:
    return {
        "id": str(job_id),
        "phase": str(phase),
        "command": list(map(str, command)),
        "registry_digest": str(registry_digest),
        "input_paths": list(map(str, input_paths)),
        "expected_outputs": list(map(str, expected_outputs)),
        "metadata": str(root / "jobs" / job_id / "job_metadata.json"),
    }


def build_execution_plan(
    *,
    registry,
    registry_path: str | Path,
    registry_digest: str,
    train_manifest: str | Path,
    reference_checkpoint: str | Path,
    prepared_dir: str | Path,
    output_dir: str | Path,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    states_per_selected_trajectory: int,
    max_workers: int,
    device: str,
    audit_json: str | Path,
    audit_md: str | Path,
    external_inputs,
) -> dict[str, object]:
    root = Path(output_dir).resolve()
    registry_path = Path(registry_path).resolve()
    train_manifest = Path(train_manifest).resolve()
    reference_checkpoint = Path(reference_checkpoint).resolve()
    prepared_dir = Path(prepared_dir).resolve()
    model_seeds = [int(value) for value in registry["model_seeds"]]
    ensemble_size = int(registry["viability"]["ensemble_size"])
    policy_round = int(registry["viability"]["policy_round"])
    calibration_seeds = [int(value) for value in registry["partitions"]["calibration"]]
    development_seeds = [
        int(value) for value in registry["viability"]["development_seeds"]
    ]
    coverages = [
        float(value) for value in registry["selected_conformal"]["coverages"]
    ]
    planning_horizon = int(
        registry["development_baseline_anchor"]["planning_horizon"]
    )
    jobs = []
    checkpoint_roots = {}
    for model_seed in model_seeds:
        checkpoint_root = root / "checkpoints" / f"model_seed_{model_seed}"
        checkpoint_roots[model_seed] = checkpoint_root
        expected = [str(checkpoint_root / "training_summary.json")]
        expected.extend(
            str(checkpoint_root / f"member_{index}.pt")
            for index in range(ensemble_size)
        )
        command = [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.run_pcc_v1_1_train",
            "--registry",
            str(registry_path),
            "--labels-manifest",
            str(train_manifest),
            "--reference-checkpoint",
            str(reference_checkpoint),
            "--model-seed",
            str(model_seed),
            "--ensemble-size",
            str(ensemble_size),
            "--epochs",
            str(int(epochs)),
            "--batch-size",
            str(int(batch_size)),
            "--learning-rate",
            str(float(learning_rate)),
            "--device",
            str(device),
            "--output-dir",
            str(checkpoint_root),
        ]
        jobs.append(
            _job(
                root,
                job_id=f"train_model_seed_{model_seed}",
                phase="train",
                command=command,
                registry_digest=registry_digest,
                input_paths=[
                    str(registry_path),
                    str(train_manifest),
                    str(reference_checkpoint),
                    *[
                        row["path"]
                        for row in external_inputs
                        if row.get("kind") == "train_artifact"
                    ],
                ],
                expected_outputs=expected,
            )
        )

    selected_calibration_roots = {}
    for model_seed in model_seeds:
        checkpoint_root = checkpoint_roots[model_seed]
        selected_root = (
            root / "selected_calibration" / f"model_seed_{model_seed}"
        )
        selected_calibration_roots[model_seed] = selected_root
        checkpoint_paths = [
            checkpoint_root / f"member_{index}.pt"
            for index in range(ensemble_size)
        ]
        command = [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.run_pcc_v1_1_selected_labels",
            "--registry",
            str(registry_path),
            "--partition",
            "calibration",
            "--seeds",
            ",".join(map(str, calibration_seeds)),
            "--checkpoint-root",
            str(checkpoint_root),
            "--model-seed",
            str(model_seed),
            "--ensemble-size",
            str(ensemble_size),
            "--policy-round",
            str(policy_round),
            "--compute-mode",
            "matched",
            "--reference-checkpoint",
            str(reference_checkpoint),
            "--env-source",
            "paper9",
            "--prepared-dir",
            str(prepared_dir),
            "--states-per-trajectory",
            str(int(states_per_selected_trajectory)),
            "--max-workers",
            str(int(max_workers)),
            "--device",
            str(device),
            "--output-root",
            str(selected_root),
        ]
        jobs.append(
            _job(
                root,
                job_id=f"selected_calibration_model_seed_{model_seed}",
                phase="selected_calibration_labels",
                command=command,
                registry_digest=registry_digest,
                input_paths=[
                    str(registry_path),
                    str(reference_checkpoint),
                    *map(str, checkpoint_paths),
                ],
                expected_outputs=_selected_outputs(
                    selected_root, calibration_seeds
                ),
            )
        )

    calibrator_roots = {}
    for model_seed in model_seeds:
        checkpoint_root = checkpoint_roots[model_seed]
        selected_root = selected_calibration_roots[model_seed]
        checkpoint_paths = [
            checkpoint_root / f"member_{index}.pt"
            for index in range(ensemble_size)
        ]
        selected_inputs = [
            selected_root / "manifest.json",
            *[
                selected_root / f"seed_{seed}" / f"trajectory_{seed}.npz"
                for seed in calibration_seeds
            ],
        ]
        for coverage in coverages:
            calibrator_root = (
                root
                / "calibrators"
                / f"model_seed_{model_seed}"
                / f"coverage_{coverage:.2f}"
            )
            calibrator_roots[(model_seed, coverage)] = calibrator_root
            command = [
                sys.executable,
                "-m",
                "paper10_geojepa_mpc.planning.selected_conformal",
                "--registry",
                str(registry_path),
                "--selected-labels-manifest",
                str(selected_root / "manifest.json"),
                "--checkpoint-root",
                str(checkpoint_root),
                "--model-seed",
                str(model_seed),
                "--ensemble-size",
                str(ensemble_size),
                "--policy-round",
                str(policy_round),
                "--planning-horizon",
                str(planning_horizon),
                "--compute-mode",
                "matched",
                "--coverage",
                str(float(coverage)),
                "--output-dir",
                str(calibrator_root),
            ]
            jobs.append(
                _job(
                    root,
                    job_id=(
                        f"calibrator_model_seed_{model_seed}_"
                        f"coverage_{coverage:.2f}"
                    ),
                    phase="fit_selected_calibrators",
                    command=command,
                    registry_digest=registry_digest,
                    input_paths=[
                        str(registry_path),
                        *map(str, checkpoint_paths),
                        *map(str, selected_inputs),
                    ],
                    expected_outputs=[str(calibrator_root / "calibrator.json")],
                )
            )

    selected_development_root = root / "selected_development"
    for model_seed in model_seeds:
        checkpoint_root = checkpoint_roots[model_seed]
        selected_root = selected_development_root / f"model_seed_{model_seed}"
        checkpoint_paths = [
            checkpoint_root / f"member_{index}.pt"
            for index in range(ensemble_size)
        ]
        command = [
            sys.executable,
            "-m",
            "paper10_geojepa_mpc.experiments.run_pcc_v1_1_selected_labels",
            "--registry",
            str(registry_path),
            "--partition",
            "development",
            "--seeds",
            ",".join(map(str, development_seeds)),
            "--checkpoint-root",
            str(checkpoint_root),
            "--model-seed",
            str(model_seed),
            "--ensemble-size",
            str(ensemble_size),
            "--policy-round",
            str(policy_round),
            "--compute-mode",
            "matched",
            "--reference-checkpoint",
            str(reference_checkpoint),
            "--env-source",
            "paper9",
            "--prepared-dir",
            str(prepared_dir),
            "--states-per-trajectory",
            str(int(states_per_selected_trajectory)),
            "--max-workers",
            str(int(max_workers)),
            "--device",
            str(device),
            "--output-root",
            str(selected_root),
        ]
        jobs.append(
            _job(
                root,
                job_id=f"selected_development_model_seed_{model_seed}",
                phase="selected_development_labels",
                command=command,
                registry_digest=registry_digest,
                input_paths=[
                    str(registry_path),
                    str(reference_checkpoint),
                    *map(str, checkpoint_paths),
                ],
                expected_outputs=_selected_outputs(
                    selected_root, development_seeds
                ),
            )
        )

    closeout_root = root / "closeout"
    closeout_json = closeout_root / "viability.json"
    closeout_md = closeout_root / "viability.md"
    closeout_inputs = [str(registry_path)]
    for model_seed in model_seeds:
        development_root = (
            selected_development_root / f"model_seed_{model_seed}"
        )
        closeout_inputs.extend(
            [
                str(development_root / "manifest.json"),
                *[
                    str(
                        development_root
                        / f"seed_{seed}"
                        / f"trajectory_{seed}.npz"
                    )
                    for seed in development_seeds
                ],
            ]
        )
        closeout_inputs.extend(
            str(calibrator_roots[(model_seed, coverage)] / "calibrator.json")
            for coverage in coverages
        )
    closeout_command = [
        sys.executable,
        "-m",
        "paper10_geojepa_mpc.experiments.pcc_v1_1_viability",
        "--registry",
        str(registry_path),
        "--selected-development-root",
        str(selected_development_root),
        "--calibrator-root",
        str(root / "calibrators"),
        "--coverages",
        ",".join(f"{coverage:.2f}" for coverage in coverages),
        "--output-json",
        str(closeout_json),
        "--output-md",
        str(closeout_md),
    ]
    jobs.append(
        _job(
            root,
            job_id="viability_closeout",
            phase="viability_closeout",
            command=closeout_command,
            registry_digest=registry_digest,
            input_paths=closeout_inputs,
            expected_outputs=[str(closeout_json), str(closeout_md)],
        )
    )
    payload: dict[str, object] = {
        "schema_version": 1,
        "protocol_id": "pcc_v1_1",
        "phase": "viability_pilot",
        "registry": str(registry_path),
        "registry_digest": str(registry_digest),
        "model_seeds": model_seeds,
        "ensemble_size": ensemble_size,
        "policy_round": policy_round,
        "compute_mode": "matched",
        "coverages": coverages,
        "calibration_seeds": calibration_seeds,
        "development_seeds": development_seeds,
        "external_inputs": list(external_inputs),
        "audit_json": str(Path(audit_json).resolve()),
        "audit_md": str(Path(audit_md).resolve()),
        "jobs": jobs,
    }
    payload["plan_digest"] = _canonical_digest(
        payload, digest_field="plan_digest"
    )
    return payload


def _pending_job_metadata(
    job: dict[str, object],
    input_digests,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "job_id": str(job["id"]),
        "phase": str(job["phase"]),
        "command": list(job["command"]),
        "registry_digest": str(job["registry_digest"]),
        "input_digests": list(input_digests),
        "expected_outputs": [
            str(Path(path).resolve()) for path in job["expected_outputs"]
        ],
        "exit_code": None,
        "output_digests": [],
        "completed_at": None,
    }


def _validate_completed_metadata(metadata, expected) -> dict[str, object]:
    invariant_fields = (
        "schema_version",
        "job_id",
        "phase",
        "command",
        "registry_digest",
        "input_digests",
        "expected_outputs",
    )
    for field in invariant_fields:
        if metadata.get(field) != expected[field]:
            raise ValueError(f"pilot job metadata mismatch: {field}")
    if metadata.get("exit_code") != 0 or not isinstance(
        metadata.get("completed_at"), str
    ):
        raise ValueError("pilot job metadata is not complete")
    observed_outputs = _file_digest_rows(expected["expected_outputs"])
    if metadata.get("output_digests") != observed_outputs:
        raise ValueError("pilot job output digest mismatch")
    return metadata


def execute_pilot_job(
    job: dict[str, object],
    *,
    resume: bool,
    runner=subprocess.run,
) -> dict[str, object]:
    input_digests = _file_digest_rows(job["input_paths"])
    expected = _pending_job_metadata(job, input_digests)
    metadata_path = Path(job["metadata"])
    output_paths = [Path(path) for path in job["expected_outputs"]]
    command = list(job["command"])
    if metadata_path.exists():
        if not resume:
            raise ValueError("pilot job metadata exists without --resume")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        invariant_fields = (
            "schema_version",
            "job_id",
            "phase",
            "command",
            "registry_digest",
            "input_digests",
            "expected_outputs",
        )
        for field in invariant_fields:
            if metadata.get(field) != expected[field]:
                raise ValueError(f"pilot job metadata mismatch: {field}")
        if metadata.get("exit_code") == 0:
            return _validate_completed_metadata(metadata, expected)
        if job["phase"] in {
            "selected_calibration_labels",
            "selected_development_labels",
        }:
            if "--resume" not in command:
                command.append("--resume")
        elif any(path.exists() for path in output_paths):
            raise ValueError("incomplete pilot job has non-resumable outputs")
    else:
        if resume and any(path.exists() for path in output_paths):
            raise ValueError("pilot outputs exist without resumable metadata")
        if not resume and any(path.exists() for path in output_paths):
            raise ValueError("pilot outputs already exist")
        _write_json_once(metadata_path, expected)
    completed = runner(command, check=False)
    return_code = int(completed.returncode)
    if return_code != 0:
        raise RuntimeError(
            f"pilot worker {job['id']} failed with exit code {return_code}"
        )
    output_digests = _file_digest_rows(expected["expected_outputs"])
    finished = {
        **expected,
        "exit_code": 0,
        "output_digests": output_digests,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json_atomic(metadata_path, finished)
    return finished


def _execute_pilot_jobs(
    plan: dict[str, object],
    *,
    resume: bool,
    runner=subprocess.run,
) -> None:
    for job in plan["jobs"]:
        execute_pilot_job(job, resume=resume, runner=runner)


def _load_valid_plan(root: str | Path, *, registry_digest: str):
    path = Path(root) / "execution_plan.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("plan_digest") != _canonical_digest(
        payload, digest_field="plan_digest"
    ):
        raise ValueError("pilot execution plan digest mismatch")
    if (
        payload.get("protocol_id") != "pcc_v1_1"
        or payload.get("phase") != "viability_pilot"
        or payload.get("registry_digest") != registry_digest
    ):
        raise ValueError("pilot execution plan lineage mismatch")
    if (
        payload.get("ensemble_size") != 3
        or payload.get("policy_round") != 1
        or payload.get("compute_mode") != "matched"
    ):
        raise ValueError("pilot execution plan exceeded viability scope")
    command_text = "\n".join(
        " ".join(job["command"]) for job in payload.get("jobs", [])
    )
    if any(token in command_text for token in ("4000", "8000")):
        raise ValueError("pilot execution plan contains a confirmation seed")
    return path, payload


def verify_pilot_inventory(
    input_root: str | Path,
    *,
    registry_digest: str,
) -> dict[str, object]:
    _, plan = _load_valid_plan(input_root, registry_digest=registry_digest)
    jobs = list(plan["jobs"])
    expected_counts = {
        "train": 3,
        "selected_calibration_labels": 3,
        "fit_selected_calibrators": 9,
        "selected_development_labels": 3,
        "viability_closeout": 1,
    }
    observed_counts = {
        phase: sum(job["phase"] == phase for job in jobs)
        for phase in expected_counts
    }
    if observed_counts != expected_counts or len(jobs) != 19:
        raise ValueError("pilot job inventory is incomplete")
    output_digests = []
    for job in jobs:
        input_digests = _file_digest_rows(job["input_paths"])
        expected = _pending_job_metadata(job, input_digests)
        metadata = json.loads(Path(job["metadata"]).read_text(encoding="utf-8"))
        completed = _validate_completed_metadata(metadata, expected)
        output_digests.extend(
            {
                **row,
                "job_id": str(job["id"]),
                "phase": str(job["phase"]),
            }
            for row in completed["output_digests"]
        )
    closeout_job = next(
        job for job in jobs if job["phase"] == "viability_closeout"
    )
    closeout_path = Path(closeout_job["expected_outputs"][0])
    closeout = json.loads(closeout_path.read_text(encoding="utf-8"))
    if (
        closeout.get("protocol_id") != "pcc_v1_1"
        or closeout.get("registry_digest") != registry_digest
        or closeout.get("status") not in {"viable", "scientific_failure"}
    ):
        raise ValueError("pilot closeout lineage or status is invalid")
    passed = bool(closeout.get("passed"))
    selected_coverage = closeout.get("selected_coverage")
    if passed != (selected_coverage is not None):
        raise ValueError("pilot closeout selected coverage is inconsistent")
    coverage_reports = closeout.get("reports")
    expected_coverage_keys = {
        f"{float(coverage):.2f}" for coverage in plan["coverages"]
    }
    if (
        not isinstance(coverage_reports, dict)
        or set(coverage_reports) != expected_coverage_keys
        or any(
            not isinstance(report, dict) or "passed" not in report
            for report in coverage_reports.values()
        )
    ):
        raise ValueError("pilot closeout coverage report inventory is incomplete")
    return {
        "schema_version": 1,
        "protocol_id": "pcc_v1_1",
        "registry_digest": registry_digest,
        "plan_digest": plan["plan_digest"],
        "passed": passed,
        "status": "viable" if passed else "scientific_failure",
        "selected_coverage": selected_coverage,
        "checkpoint_families": observed_counts["train"],
        "physical_checkpoints": observed_counts["train"]
        * int(plan["ensemble_size"]),
        "selected_calibration_manifests": observed_counts[
            "selected_calibration_labels"
        ],
        "calibrators": observed_counts["fit_selected_calibrators"],
        "selected_development_manifests": observed_counts[
            "selected_development_labels"
        ],
        "failed_gates": list(closeout.get("failed_gates", [])),
        "coverage_reports": coverage_reports,
        "closeout_path": str(closeout_path.resolve()),
        "closeout_sha256": _sha256_file(closeout_path),
        "input_digests": output_digests,
    }


def _audit_markdown(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# PCC v1.1 Viability Pilot Audit",
            "",
            f"- Status: `{payload['status']}`",
            f"- Passed: `{str(bool(payload['passed'])).lower()}`",
            f"- Selected coverage: `{payload['selected_coverage']}`",
            f"- Checkpoint families: {payload['checkpoint_families']}",
            f"- Physical checkpoints: {payload['physical_checkpoints']}",
            f"- Selected calibration manifests: {payload['selected_calibration_manifests']}",
            f"- Calibrators: {payload['calibrators']}",
            f"- Selected development manifests: {payload['selected_development_manifests']}",
            f"- Failed gates: {payload.get('failed_gates', [])}",
            "",
            "## Coverage Reports",
            "",
            "| coverage | passed | failed gates |",
            "|---:|---|---|",
            *[
                f"| {coverage} | {report.get('passed')} | "
                f"{report.get('failed_gates', [])} |"
                for coverage, report in sorted(
                    payload.get("coverage_reports", {}).items()
                )
            ],
            "",
            "## Bound Artifacts",
            "",
            "| phase | job | path | sha256 |",
            "|---|---|---|---|",
            *[
                f"| {row.get('phase', '')} | {row.get('job_id', '')} | "
                f"{row.get('path', '')} | `{row['sha256']}` |"
                for row in payload.get("input_digests", [])
            ],
            "",
        ]
    )


def _write_audit(
    output_json: str | Path,
    output_md: str | Path,
    payload: dict[str, object],
) -> None:
    _write_json_atomic(output_json, payload)
    path = Path(output_md)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(_audit_markdown(payload), encoding="utf-8")
    temporary.replace(path)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--train-manifest")
    parser.add_argument("--reference-checkpoint")
    parser.add_argument("--prepared-dir")
    parser.add_argument("--output-dir")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--learning-rate", type=float)
    parser.add_argument("--states-per-selected-trajectory", type=int)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--input-root")
    parser.add_argument("--audit-json")
    parser.add_argument("--audit-md")
    return parser.parse_args(argv)


def _require_execution_args(args) -> None:
    required = (
        "train_manifest",
        "reference_checkpoint",
        "prepared_dir",
        "output_dir",
        "epochs",
        "batch_size",
        "learning_rate",
        "states_per_selected_trajectory",
        "audit_json",
        "audit_md",
    )
    missing = [field for field in required if getattr(args, field) is None]
    if missing:
        raise ValueError(f"pilot execution arguments are missing: {missing}")
    if min(
        int(args.epochs),
        int(args.batch_size),
        int(args.states_per_selected_trajectory),
        int(args.max_workers),
    ) <= 0 or float(args.learning_rate) <= 0.0:
        raise ValueError("pilot execution numeric arguments must be positive")


def _validate_pilot_hyperparameters(registry, args) -> None:
    expected = registry["pilot_training"]
    observed = {
        "epochs": int(args.epochs),
        "batch_size": int(args.batch_size),
        "learning_rate": float(args.learning_rate),
    }
    if observed != {
        "epochs": int(expected["epochs"]),
        "batch_size": int(expected["batch_size"]),
        "learning_rate": float(expected["learning_rate"]),
    }:
        raise ValueError("pilot training hyperparameters mismatch the registry")


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    if registry.get("protocol_id") != "pcc_v1_1":
        raise ValueError("pilot orchestrator requires PCC v1.1")
    registry_digest = _sha256_file(args.registry)
    if args.verify_only:
        if not args.input_root:
            raise ValueError("--verify-only requires --input-root")
        result = verify_pilot_inventory(
            args.input_root,
            registry_digest=registry_digest,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return result
    if args.input_root:
        raise ValueError("--input-root is only valid with --verify-only")
    _require_execution_args(args)
    _validate_pilot_hyperparameters(registry, args)
    external_inputs = _validate_external_inputs(
        registry=registry,
        registry_path=args.registry,
        registry_digest=registry_digest,
        train_manifest=args.train_manifest,
        reference_checkpoint=args.reference_checkpoint,
    )
    plan = build_execution_plan(
        registry=registry,
        registry_path=args.registry,
        registry_digest=registry_digest,
        train_manifest=args.train_manifest,
        reference_checkpoint=args.reference_checkpoint,
        prepared_dir=args.prepared_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        states_per_selected_trajectory=args.states_per_selected_trajectory,
        max_workers=args.max_workers,
        device=args.device,
        audit_json=args.audit_json,
        audit_md=args.audit_md,
        external_inputs=external_inputs,
    )
    plan_path = Path(args.output_dir).resolve() / "execution_plan.json"
    _write_json_once(plan_path, plan)
    if args.dry_run:
        result = {
            "status": "dry_run",
            "plan": str(plan_path),
            "plan_digest": plan["plan_digest"],
            "jobs": len(plan["jobs"]),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return result
    _execute_pilot_jobs(plan, resume=args.resume)
    result = verify_pilot_inventory(
        args.output_dir,
        registry_digest=registry_digest,
    )
    _write_audit(args.audit_json, args.audit_md, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
