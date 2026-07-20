import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_confirmation_artifacts import (
    MODEL_INDEPENDENT_POLICIES,
    complete_policy_block,
    load_confirmation_artifacts,
    verify_model_dependent_checkpoints,
    verify_reference_policy_checkpoints,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    verify_frozen_registry,
)
from paper10_geojepa_mpc.experiments.pcc_experiment_inventory import build_inventory


@dataclass(frozen=True)
class ConfirmationJob:
    region: str
    policy: str
    model_seed: int
    seeds: tuple[int, ...]
    command: tuple[str, ...]
    output: Path
    metadata: Path
    checkpoint_digests: tuple[str, ...]
    calibrator_digest: str | None


@dataclass(frozen=True)
class ConfirmationPlan:
    registry_digest: str
    region: str
    jobs: tuple[ConfirmationJob, ...]


def _git_output(cwd: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError("frozen registry is not committed") from exc
    return completed.stdout


def assert_frozen_registry_committed(
    registry_path: str | Path,
    expected_digest: str,
) -> None:
    registry_path = Path(registry_path).resolve()
    repo_root = Path(
        _git_output(registry_path.parent, "rev-parse", "--show-toplevel").strip()
    ).resolve()
    try:
        relative = registry_path.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError("frozen registry is not committed inside the repository") from exc
    committed_text = _git_output(repo_root, "show", f"HEAD:{relative}")
    try:
        committed = json.loads(committed_text)
        working = load_registry(registry_path)
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("committed frozen registry cannot be loaded") from exc
    if committed != working:
        raise ValueError("frozen registry working file does not match committed blob")
    observed = verify_frozen_registry(committed)
    if observed != str(expected_digest):
        raise ValueError("committed frozen registry digest mismatch")


def _policy_models(registry, policy: str) -> tuple[int, ...]:
    model_seeds = tuple(int(value) for value in registry["model_seeds"])
    if policy in MODEL_INDEPENDENT_POLICIES:
        return model_seeds[:1]
    return model_seeds


def _confirmation_job(
    *,
    registry,
    registry_path: Path,
    registry_digest: str,
    run_root: Path,
    region: str,
    policy: str,
    model_seed: int,
    seeds: tuple[int, ...],
    inventory,
    prepared_dir: Path,
    device: str,
) -> ConfirmationJob:
    selected = registry["selected_config"]
    model_dependent = policy not in MODEL_INDEPENDENT_POLICIES
    checkpoint_root = None
    calibrator = None
    calibrator_digest = None
    if model_dependent:
        checkpoint_root = inventory.checkpoint_root(
            model_seed,
            int(selected["ensemble_size"]),
            int(selected["policy_round"]),
        )
        checkpoint_digests = inventory.checkpoint_digests(
            model_seed,
            int(selected["ensemble_size"]),
            int(selected["policy_round"]),
        )
    else:
        checkpoint_digests = (
            str(registry["offline_reference_policy"]["checkpoint_sha256"]),
        )
    if policy in {"pcc_matched", "pcc_full"}:
        calibrator = inventory.calibrator(
            model_seed,
            int(selected["ensemble_size"]),
            int(selected["policy_round"]),
            float(selected["joint_coverage"]),
        )
        calibrator_digest = inventory.calibrator_digest(
            model_seed,
            int(selected["ensemble_size"]),
            int(selected["policy_round"]),
            float(selected["joint_coverage"]),
        )
    output = (
        run_root
        / "confirmation"
        / region
        / policy
        / f"model-{model_seed}.json"
    )
    metadata = output.with_suffix(".meta.json")
    command = [
        sys.executable,
        "-m",
        "paper10_geojepa_mpc.experiments.run_pcc_rollouts",
        "--registry",
        str(registry_path),
        "--mode",
        "confirmation",
        "--policy",
        policy,
        "--env-source",
        "paper9" if region == "bishan" else "neijiang",
        "--prepared-dir",
        str(prepared_dir),
        "--model-seed",
        str(model_seed),
        "--seeds",
        ",".join(map(str, seeds)),
        "--rollout-steps",
        str(int(registry["confirmation"]["rollout_steps"])),
        "--device",
        str(device),
    ]
    if checkpoint_root is not None:
        command.extend(("--checkpoint-root", str(checkpoint_root)))
    if calibrator is not None:
        command.extend(("--calibrator", str(calibrator)))
    if policy == "pcc_full":
        command.extend(("--compute-mode", "full"))
    elif policy == "pcc_matched":
        command.extend(("--compute-mode", "matched"))
    command.extend(("--output", str(output)))
    return ConfirmationJob(
        region=region,
        policy=policy,
        model_seed=int(model_seed),
        seeds=seeds,
        command=tuple(command),
        output=output,
        metadata=metadata,
        checkpoint_digests=tuple(map(str, checkpoint_digests)),
        calibrator_digest=(
            str(calibrator_digest) if calibrator_digest is not None else None
        ),
    )


def build_confirmation_plan(
    registry: dict[str, object],
    *,
    registry_path: str | Path,
    run_root: str | Path,
    region: str,
    inventory,
    prepared_dir_bishan: str | Path = ".",
    prepared_dir_dongxing: str | Path = ".",
    device: str = "cpu",
) -> ConfirmationPlan:
    registry_digest = verify_frozen_registry(registry)
    region = str(region)
    if region not in {"bishan", "dongxing"}:
        raise ValueError("confirmation region must be bishan or dongxing")
    partition = "confirmation" if region == "bishan" else "dongxing_confirmation"
    seeds = tuple(int(value) for value in registry["partitions"][partition])
    prepared_dir = Path(
        prepared_dir_bishan if region == "bishan" else prepared_dir_dongxing
    ).resolve()
    registry_path = Path(registry_path).resolve()
    run_root = Path(run_root).resolve()
    jobs = tuple(
        _confirmation_job(
            registry=registry,
            registry_path=registry_path,
            registry_digest=registry_digest,
            run_root=run_root,
            region=region,
            policy=str(policy),
            model_seed=model_seed,
            seeds=seeds,
            inventory=inventory,
            prepared_dir=prepared_dir,
            device=device,
        )
        for policy in registry["deployable_baselines"]
        for model_seed in _policy_models(registry, str(policy))
    )
    return ConfirmationPlan(
        registry_digest=registry_digest,
        region=region,
        jobs=jobs,
    )


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: str | Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _job_metadata(job: ConfirmationJob, *, registry_digest: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "registry_digest": str(registry_digest),
        "region": job.region,
        "policy": job.policy,
        "model_seed": int(job.model_seed),
        "seeds": list(job.seeds),
        "checkpoint_digests": list(job.checkpoint_digests),
        "calibrator_digest": job.calibrator_digest,
        "output_sha256": None,
    }


def _plan_payload(plan: ConfirmationPlan) -> dict[str, object]:
    return {
        "schema_version": 1,
        "registry_digest": plan.registry_digest,
        "region": plan.region,
        "jobs": [
            {
                "region": job.region,
                "policy": job.policy,
                "model_seed": job.model_seed,
                "seeds": list(job.seeds),
                "command": list(job.command),
                "output": str(job.output),
                "metadata": str(job.metadata),
                "checkpoint_digests": list(job.checkpoint_digests),
                "calibrator_digest": job.calibrator_digest,
            }
            for job in plan.jobs
        ],
    }


def _validate_job_output(
    job: ConfirmationJob,
    *,
    registry_digest: str,
    verify_digest: bool = True,
    require_complete: bool = True,
) -> dict[str, object]:
    if not job.output.is_file() or not job.metadata.is_file():
        raise FileNotFoundError("confirmation output or metadata is missing")
    payload = json.loads(job.output.read_text(encoding="utf-8"))
    metadata = json.loads(job.metadata.read_text(encoding="utf-8"))
    expected_metadata = _job_metadata(job, registry_digest=registry_digest)
    for field, expected in expected_metadata.items():
        if field == "output_sha256":
            continue
        if metadata.get(field) != expected:
            raise ValueError(f"confirmation job metadata mismatch: {field}")
    if payload.get("registry_digest") != str(registry_digest):
        raise ValueError("confirmation output registry digest mismatch")
    if payload.get("checkpoint_digests") != list(job.checkpoint_digests):
        raise ValueError("confirmation output checkpoint digest mismatch")
    rows = payload.get("seed_results")
    if not isinstance(rows, list):
        raise ValueError("confirmation output seed results are invalid")
    observed_seeds = []
    for row in rows:
        if (
            row.get("policy") != job.policy
            or int(row.get("model_seed", -1)) != job.model_seed
            or row.get("registry_digest") != str(registry_digest)
            or row.get("checkpoint_digests") != list(job.checkpoint_digests)
        ):
            raise ValueError("confirmation seed result identity mismatch")
        observed_seeds.append(int(row["seed"]))
        objective = np.asarray(row.get("objective_outcome"), dtype=np.float64)
        if objective.shape != (4,) or not np.isfinite(objective).all():
            raise ValueError("confirmation objective outcome is invalid")
        steps = row.get("steps")
        if (
            not isinstance(steps, list)
            or int(row.get("environment_step_count", -1)) != len(steps)
            or any(
                not isinstance(step, dict)
                or step.get("unexecuted_real_reward_queries") != 0
                for step in steps
            )
        ):
            raise ValueError("confirmation information-set record is invalid")
    if len(observed_seeds) != len(set(observed_seeds)):
        raise ValueError("confirmation output rollout-seed block is incomplete")
    if require_complete:
        valid_seed_block = sorted(observed_seeds) == sorted(job.seeds)
    else:
        valid_seed_block = bool(observed_seeds) and set(observed_seeds).issubset(
            set(job.seeds)
        )
    if not valid_seed_block:
        raise ValueError("confirmation output rollout-seed block is incomplete")
    if verify_digest:
        expected_digest = metadata.get("output_sha256")
        if (
            not isinstance(expected_digest, str)
            or _sha256_file(job.output) != expected_digest
        ):
            raise ValueError("confirmation output digest mismatch")
    return payload


def _execute_confirmation_job(
    job: ConfirmationJob,
    *,
    registry_digest: str,
    resume: bool,
    runner,
) -> dict[str, object]:
    expected_metadata = _job_metadata(job, registry_digest=registry_digest)
    command = list(job.command)
    if job.output.exists() or job.metadata.exists():
        if not resume:
            raise ValueError("confirmation output exists without resume")
        if job.metadata.is_file():
            metadata = json.loads(job.metadata.read_text(encoding="utf-8"))
            if isinstance(metadata.get("output_sha256"), str):
                return _validate_job_output(
                    job,
                    registry_digest=registry_digest,
                )
            if metadata.get("output_sha256") is None and job.output.is_file():
                _validate_job_output(
                    job,
                    registry_digest=registry_digest,
                    verify_digest=False,
                    require_complete=False,
                )
                if "--resume" not in command:
                    command.append("--resume")
            else:
                raise ValueError("partial confirmation output is not digest-bound")
        else:
            raise ValueError("partial confirmation output is not digest-bound")
    else:
        _write_json_atomic(job.metadata, expected_metadata)
    completed = runner(command, check=False)
    if int(completed.returncode) != 0:
        raise RuntimeError(
            f"confirmation worker failed with exit code {completed.returncode}"
        )
    payload = _validate_job_output(
        job,
        registry_digest=registry_digest,
        verify_digest=False,
    )
    expected_metadata["output_sha256"] = _sha256_file(job.output)
    _write_json_atomic(job.metadata, expected_metadata)
    _validate_job_output(job, registry_digest=registry_digest)
    return payload


def execute_confirmation_plan(
    plan: ConfirmationPlan,
    *,
    plan_path: str | Path,
    resume: bool = False,
    runner=subprocess.run,
) -> list[dict[str, object]]:
    _write_json_atomic(plan_path, _plan_payload(plan))
    return [
        _execute_confirmation_job(
            job,
            registry_digest=plan.registry_digest,
            resume=resume,
            runner=runner,
        )
        for job in plan.jobs
    ]


def close_confirmation_plan(
    plan: ConfirmationPlan,
    *,
    manifest_path: str | Path,
) -> dict[str, object]:
    if not plan.jobs:
        raise ValueError("confirmation plan has no jobs")
    for job in plan.jobs:
        _validate_job_output(job, registry_digest=plan.registry_digest)
    policies = tuple(dict.fromkeys(job.policy for job in plan.jobs))
    model_seeds = tuple(
        sorted(
            {
                job.model_seed
                for job in plan.jobs
                if job.policy not in MODEL_INDEPENDENT_POLICIES
            }
        )
    )
    if not model_seeds:
        raise ValueError("confirmation plan has no model-dependent policy block")
    rollout_seeds = plan.jobs[0].seeds
    if any(job.seeds != rollout_seeds for job in plan.jobs):
        raise ValueError("confirmation jobs do not share one rollout-seed block")
    region_root = plan.jobs[0].output.parent.parent
    artifacts = load_confirmation_artifacts(
        region_root,
        expected_registry_digest=plan.registry_digest,
        allowed_policies=policies,
    )
    physical_model_blocks = {}
    for policy in policies:
        complete_policy_block(
            artifacts,
            policy=policy,
            model_seeds=model_seeds,
            rollout_seeds=rollout_seeds,
            allow_shared_model_block=policy in MODEL_INDEPENDENT_POLICIES,
        )
        jobs = [job for job in plan.jobs if job.policy == policy]
        physical_model_blocks[policy] = len(jobs)
        if policy in MODEL_INDEPENDENT_POLICIES:
            if len(jobs) != 1:
                raise ValueError(
                    f"model-independent policy has duplicate physical blocks: {policy}"
                )
            verify_reference_policy_checkpoints(
                artifacts,
                policy=policy,
                expected_digests=jobs[0].checkpoint_digests,
            )
        else:
            expected_digests = [
                digest
                for job in jobs
                for digest in job.checkpoint_digests
            ]
            verify_model_dependent_checkpoints(
                artifacts,
                policy=policy,
                model_seeds=model_seeds,
                expected_flat_digests=expected_digests,
            )
    manifest = {
        "schema_version": 1,
        "registry_digest": plan.registry_digest,
        "region": plan.region,
        "complete": True,
        "policies": list(policies),
        "model_seeds": list(model_seeds),
        "rollout_seeds": list(rollout_seeds),
        "physical_model_blocks": physical_model_blocks,
        "information_audit_passed": bool(
            artifacts["information_audit_passed"]
        ),
        "jobs": [
            {
                "policy": job.policy,
                "model_seed": job.model_seed,
                "output": str(job.output),
                "output_sha256": _sha256_file(job.output),
                "checkpoint_digests": list(job.checkpoint_digests),
                "calibrator_digest": job.calibrator_digest,
            }
            for job in plan.jobs
        ],
    }
    if manifest["information_audit_passed"] is not True:
        raise ValueError("confirmation information audit is incomplete")
    _write_json_atomic(manifest_path, manifest)
    return manifest


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument(
        "--region",
        choices=("bishan", "dongxing", "all"),
        default="all",
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--prepared-dir-bishan", required=True)
    parser.add_argument("--prepared-dir-dongxing", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--calibration-root")
    parser.add_argument("--dongxing-checkpoint-root")
    parser.add_argument("--dongxing-calibration-root")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry_path = Path(args.registry).resolve()
    registry = load_registry(registry_path)
    registry_digest = verify_frozen_registry(registry)
    assert_frozen_registry_committed(registry_path, registry_digest)
    regions = ("bishan", "dongxing") if args.region == "all" else (args.region,)
    summaries = []
    for region in regions:
        if region == "bishan":
            checkpoint_root = args.checkpoint_root
            calibrator_root = args.calibration_root or args.checkpoint_root
        else:
            if args.dongxing_checkpoint_root is None:
                raise ValueError("Dongxing confirmation requires adapted checkpoints")
            checkpoint_root = args.dongxing_checkpoint_root
            calibrator_root = (
                args.dongxing_calibration_root or args.dongxing_checkpoint_root
            )
        inventory = build_inventory(
            checkpoint_root,
            calibrator_root=calibrator_root,
            model_seeds=registry["model_seeds"],
            registry=registry,
        )
        plan = build_confirmation_plan(
            registry,
            registry_path=registry_path,
            run_root=args.run_root,
            region=region,
            inventory=inventory,
            prepared_dir_bishan=args.prepared_dir_bishan,
            prepared_dir_dongxing=args.prepared_dir_dongxing,
            device=args.device,
        )
        region_root = Path(args.run_root).resolve() / "confirmation" / region
        plan_path = region_root / "execution_plan.json"
        if args.dry_run:
            _write_json_atomic(plan_path, _plan_payload(plan))
            summaries.append(
                {
                    "region": region,
                    "plan": str(plan_path),
                    "jobs": len(plan.jobs),
                    "dry_run": True,
                }
            )
            continue
        execute_confirmation_plan(
            plan,
            plan_path=plan_path,
            resume=bool(args.resume),
        )
        manifest_path = region_root / "manifest.json"
        manifest = close_confirmation_plan(plan, manifest_path=manifest_path)
        summaries.append(
            {
                "region": region,
                "manifest": str(manifest_path),
                "jobs": len(plan.jobs),
                "complete": bool(manifest["complete"]),
            }
        )
    print(json.dumps({"registry_digest": registry_digest, "regions": summaries}))


if __name__ == "__main__":
    main()
