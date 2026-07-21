import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from itertools import product
from pathlib import Path
import subprocess
import sys
from typing import Mapping, Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_experiment_inventory import build_inventory
from paper10_geojepa_mpc.experiments.pcc_ablations import ABLATION_CONTRACTS
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
    validate_registry,
)


GRID_KEYS = (
    "ensemble_size",
    "joint_coverage",
    "tolerance_scale",
    "planning_horizon",
    "residual_window",
    "policy_round",
)
MODEL_DEPENDENT_BASELINES = {
    "distributional_risk",
    "online_expert_selector",
}


@dataclass(frozen=True)
class DevelopmentRung:
    seeds: tuple[int, ...]
    steps: int
    keep: int


def build_development_schedule(
    registry: dict[str, object],
) -> tuple[DevelopmentRung, ...]:
    development_seeds = tuple(
        int(value) for value in registry["partitions"]["development"]
    )
    if development_seeds != tuple(range(3000, 3010)):
        raise ValueError("development seed block does not match PCC v1")
    confirmation_seeds = {
        int(value) for value in registry["partitions"]["confirmation"]
    }
    if set(development_seeds) & confirmation_seeds:
        raise ValueError("development schedule overlaps confirmation seeds")
    return (
        DevelopmentRung(seeds=development_seeds[:2], steps=20, keep=144),
        DevelopmentRung(seeds=development_seeds[:5], steps=50, keep=36),
        DevelopmentRung(seeds=development_seeds, steps=100, keep=8),
    )


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _paired_objective_effects(
    policy_rows,
    *,
    policy: str,
    comparator: str,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    by_role: dict[str, dict[tuple[int, int], dict[str, object]]] = {
        policy: {},
        comparator: {},
    }
    for source in policy_rows:
        row = dict(source)
        role = str(row.get("policy", ""))
        if role not in by_role:
            continue
        key = (int(row["model_seed"]), int(row["seed"]))
        if key in by_role[role]:
            raise ValueError(f"duplicate paired development row: {role} {key}")
        outcome = np.asarray(row.get("objective_outcome"), dtype=np.float64)
        if outcome.shape != (4,) or not np.isfinite(outcome).all():
            raise ValueError("development objective outcomes must be finite length-4")
        row["objective_outcome"] = outcome
        by_role[role][key] = row
    policy_keys = set(by_role[policy])
    comparator_keys = set(by_role[comparator])
    if not policy_keys or policy_keys != comparator_keys:
        raise ValueError("development policy rows must form complete paired blocks")
    ordered_keys = sorted(policy_keys)
    effects = np.stack(
        [
            by_role[policy][key]["objective_outcome"]
            - by_role[comparator][key]["objective_outcome"]
            for key in ordered_keys
        ],
        axis=0,
    )
    return effects, [by_role[policy][key] for key in ordered_keys]


def _one_sided_seed_bootstrap_lower(
    effects: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> np.ndarray:
    if int(draws) <= 0:
        raise ValueError("bootstrap draws must be positive")
    rng = np.random.default_rng(int(seed))
    indexes = rng.integers(
        0,
        effects.shape[0],
        size=(int(draws), effects.shape[0]),
    )
    sampled = effects[indexes].mean(axis=1)
    return np.quantile(sampled, 0.05, axis=0)


def _mean_effects_by_rollout_seed(
    effects: np.ndarray,
    pairs: Sequence[tuple[int, int]],
) -> np.ndarray:
    effects = np.asarray(effects, dtype=np.float64)
    if effects.ndim != 2 or effects.shape[0] != len(pairs):
        raise ValueError("paired effects and identities are inconsistent")
    by_seed: dict[int, dict[int, np.ndarray]] = {}
    for effect, (model_seed, rollout_seed) in zip(effects, pairs):
        models = by_seed.setdefault(int(rollout_seed), {})
        if int(model_seed) in models:
            raise ValueError("duplicate model-seed effect within rollout seed")
        models[int(model_seed)] = effect
    model_blocks = [set(models) for models in by_seed.values()]
    if not model_blocks or any(block != model_blocks[0] for block in model_blocks):
        raise ValueError("rollout seeds have inconsistent model-seed blocks")
    return np.stack(
        [
            np.stack(list(by_seed[seed].values()), axis=0).mean(axis=0)
            for seed in sorted(by_seed)
        ],
        axis=0,
    )


def development_row(config, policy_rows, *, draws: int = 20000):
    config = dict(config)
    for field in ("id", "policy", "primary_candidate"):
        if field not in config:
            raise ValueError(f"development configuration is missing {field}")
    effects, pcc_rows = _paired_objective_effects(
        policy_rows,
        policy=str(config["policy"]),
        comparator=str(config["primary_candidate"]),
    )
    seed_effects = _mean_effects_by_rollout_seed(
        effects,
        [
            (int(row["model_seed"]), int(row["seed"]))
            for row in pcc_rows
        ],
    )
    lower = _one_sided_seed_bootstrap_lower(
        seed_effects,
        draws=draws,
        seed=int(config.get("development_bootstrap_seed", 20260710)),
    )
    compute = 0
    for row in pcc_rows:
        for step in row.get("steps", []):
            raw_value = step.get("member_evaluations", 0)
            value = float(raw_value)
            if not np.isfinite(value) or value < 0.0 or not value.is_integer():
                raise ValueError("member evaluations must be non-negative integers")
            compute += int(value)
    return {
        **config,
        "planning_gate_count": int(np.sum(lower[1:] >= 0.0)),
        "reward": float(effects[:, 0].mean()),
        "compute": int(compute),
        "lower_95_one_sided": lower.tolist(),
        "paired_observations": int(effects.shape[0]),
        "bootstrap_rollout_seeds": int(seed_effects.shape[0]),
    }


def stage_a_report_from_payloads(
    payloads: Mapping[str, Mapping[str, object]],
    *,
    model_seeds,
    seeds,
    nominal_coverage: float,
) -> dict[str, object]:
    model_seeds = tuple(int(value) for value in model_seeds)
    seeds = tuple(int(value) for value in seeds)
    if set(payloads) != {str(value) for value in model_seeds}:
        raise ValueError("Stage A payloads have an incomplete model-seed block")
    uncertainty_rows = []
    absolute_error_rows = []
    covered_by_seed = {seed: True for seed in seeds}
    query_count = 0
    for model_seed in model_seeds:
        payload = payloads[str(model_seed)]
        rows = [dict(row) for row in payload.get("seed_results", [])]
        if {int(row["seed"]) for row in rows} != set(seeds) or len(rows) != len(
            seeds
        ):
            raise ValueError("Stage A payload has an incomplete trajectory block")
        for row in rows:
            if int(row.get("model_seed", -1)) != model_seed:
                raise ValueError("Stage A payload model-seed identity mismatch")
            seed = int(row["seed"])
            steps = list(row.get("steps", []))
            if not steps:
                raise ValueError("Stage A trajectory has no executed steps")
            for step in steps:
                query_count += int(
                    step.get("unexecuted_real_reward_queries", -1)
                )
                observed = np.asarray(
                    step.get("observed_outcome"), dtype=np.float64
                )
                predicted = np.asarray(
                    step.get("selected_predicted_mean"), dtype=np.float64
                )
                scale = np.asarray(
                    step.get("selected_base_scale"), dtype=np.float64
                )
                if (
                    observed.shape != (4,)
                    or predicted.shape != (4,)
                    or scale.shape != (4,)
                    or not np.isfinite(observed).all()
                    or not np.isfinite(predicted).all()
                    or not np.isfinite(scale).all()
                    or np.any(scale <= 0.0)
                ):
                    raise ValueError(
                        "Stage A executed prediction record is invalid"
                    )
                q_joint = float(step.get("joint_q", np.nan))
                if not np.isfinite(q_joint) or q_joint < 0.0:
                    raise ValueError("Stage A joint conformal multiplier is invalid")
                error = np.abs(observed - predicted)
                uncertainty_rows.extend(scale.tolist())
                absolute_error_rows.extend(error.tolist())
                covered_by_seed[seed] = bool(
                    covered_by_seed[seed]
                    and np.all(error <= q_joint * scale)
                )
    if query_count != 0:
        raise ValueError("Stage A queried unexecuted real reward")
    report = stage_a_gate(
        uncertainty=uncertainty_rows,
        absolute_error=absolute_error_rows,
        covered_trajectories=sum(covered_by_seed.values()),
        n_trajectories=len(seeds),
        nominal_coverage=float(nominal_coverage),
    )
    report.update(
        {
            "model_seeds": list(model_seeds),
            "source_seeds": list(seeds),
            "unexecuted_real_reward_queries": query_count,
            "coverage_unit": "rollout_seed",
        }
    )
    return report


def select_primary_comparator(rows, *, candidates) -> dict[str, object]:
    candidates = tuple(str(value) for value in candidates)
    forbidden = {
        "pcc_matched",
        "pcc_full",
        "oracle_action_audit_diagnostic",
    }
    if (
        not candidates
        or len(candidates) != len(set(candidates))
        or set(candidates) & forbidden
    ):
        raise ValueError("primary comparator candidate set is invalid")
    rows = [dict(row) for row in rows]
    if {str(row.get("id")) for row in rows} != set(candidates):
        raise ValueError("primary comparator rows do not match the candidate set")
    return dict(select_configuration(rows))


def _payload_digest(payload: Mapping[str, object], *, digest_field: str) -> str:
    clean = {key: value for key, value in payload.items() if key != digest_field}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def validate_ablation_inventory(
    payload: Mapping[str, object],
    *,
    registry: Mapping[str, object],
    selected_config: Mapping[str, object],
    registry_digest: str,
) -> str:
    payload = dict(payload)
    if payload.get("registry_digest") != str(registry_digest):
        raise ValueError("ablation inventory registry digest mismatch")
    if payload.get("selected_configuration_id") != str(selected_config["id"]):
        raise ValueError("ablation inventory selected configuration mismatch")
    expected_models = [int(value) for value in registry["model_seeds"]]
    expected_seeds = [
        int(value) for value in registry["partitions"]["development"]
    ]
    if [int(value) for value in payload.get("model_seeds", [])] != expected_models:
        raise ValueError("ablation inventory model-seed block mismatch")
    if [int(value) for value in payload.get("source_seeds", [])] != expected_seeds:
        raise ValueError("ablation inventory source-seed block mismatch")
    expected_names = {str(value) for value in registry["required_ablations"]}
    ablations = payload.get("ablations")
    if not isinstance(ablations, dict) or set(ablations) != expected_names:
        raise ValueError("ablation set is incomplete or undeclared")
    for name in sorted(expected_names):
        row = ablations[name]
        if not isinstance(row, dict) or row.get("complete") is not True:
            raise ValueError(f"ablation block is incomplete: {name}")
        expected_overlay = json.loads(
            json.dumps(
                dict(ABLATION_CONTRACTS[name].overlay),
                sort_keys=True,
                ensure_ascii=True,
            )
        )
        observed_overlay = json.loads(
            json.dumps(
                row.get("overlay"),
                sort_keys=True,
                ensure_ascii=True,
            )
        )
        if observed_overlay != expected_overlay:
            raise ValueError(f"ablation overlay mismatch: {name}")
        if [int(value) for value in row.get("model_seeds", [])] != expected_models:
            raise ValueError(f"ablation model-seed block mismatch: {name}")
        if [int(value) for value in row.get("source_seeds", [])] != expected_seeds:
            raise ValueError(f"ablation source-seed block mismatch: {name}")
        if int(row.get("paired_observations", -1)) != len(expected_models) * len(
            expected_seeds
        ):
            raise ValueError(f"ablation paired block is incomplete: {name}")
        if not _is_sha256(row.get("artifact_sha256")):
            raise ValueError(f"ablation artifact digest is invalid: {name}")
        artifact_path = Path(str(row.get("artifact_path", "")))
        if not artifact_path.is_file():
            raise FileNotFoundError(f"ablation artifact is missing: {name}")
        if _sha256_file(artifact_path) != row["artifact_sha256"]:
            raise ValueError(f"ablation artifact digest mismatch: {name}")
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        if (
            artifact.get("registry_digest") != str(registry_digest)
            or artifact.get("selected_configuration_id")
            != str(selected_config["id"])
            or artifact.get("ablation") != name
        ):
            raise ValueError(f"ablation artifact identity mismatch: {name}")
        expected_model_keys = {str(value) for value in expected_models}
        checkpoint_lineage = row.get("checkpoint_digests_by_model")
        calibrator_lineage = row.get("calibrator_digests_by_model")
        if (
            not isinstance(checkpoint_lineage, dict)
            or set(checkpoint_lineage) != expected_model_keys
            or not isinstance(calibrator_lineage, dict)
            or set(calibrator_lineage) != expected_model_keys
        ):
            raise ValueError(f"ablation lineage mapping is incomplete: {name}")
        checkpoint_values = []
        expected_member_count = int(
            ABLATION_CONTRACTS[name].overlay.get(
                "ensemble_size",
                selected_config["ensemble_size"],
            )
        )
        for model_seed in sorted(expected_model_keys):
            digests = checkpoint_lineage[model_seed]
            if (
                not isinstance(digests, list)
                or not digests
                or len(digests) != len(set(digests))
                or not all(_is_sha256(value) for value in digests)
                or not _is_sha256(calibrator_lineage[model_seed])
            ):
                raise ValueError(f"ablation lineage mapping is invalid: {name}")
            if len(digests) != expected_member_count:
                raise ValueError(
                    f"ablation checkpoint member count mismatch: {name}"
                )
            checkpoint_values.extend(digests)
        if len(checkpoint_values) != len(set(checkpoint_values)):
            raise ValueError(f"ablation checkpoint lineage is not physical: {name}")
        if (
            artifact.get("checkpoint_digests_by_model") != checkpoint_lineage
            or artifact.get("calibrator_digests_by_model") != calibrator_lineage
        ):
            raise ValueError(f"ablation artifact lineage mapping mismatch: {name}")
        seed_results = list(artifact.get("seed_results", []))
        observed_pairs = [
            (int(result["model_seed"]), int(result["seed"]))
            for result in seed_results
        ]
        expected_pairs = {
            (model_seed, seed)
            for model_seed in expected_models
            for seed in expected_seeds
        }
        if (
            len(observed_pairs) != len(expected_pairs)
            or len(observed_pairs) != len(set(observed_pairs))
            or set(observed_pairs) != expected_pairs
        ):
            raise ValueError(f"ablation physical paired block is incomplete: {name}")
        for result in seed_results:
            try:
                objective = np.asarray(result["objective_outcome"], dtype=float)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"ablation physical block must contain four finite objectives: {name}"
                ) from exc
            if objective.shape != (4,) or not np.all(np.isfinite(objective)):
                raise ValueError(
                    f"ablation physical block must contain four finite objectives: {name}"
                )
            steps = result.get("steps")
            if not isinstance(steps, list) or not steps:
                raise ValueError(
                    f"ablation physical block lacks information-set steps: {name}"
                )
            if any(
                step.get("unexecuted_real_reward_queries") != 0
                for step in steps
                if isinstance(step, dict)
            ) or any(not isinstance(step, dict) for step in steps):
                raise ValueError(
                    f"ablation contains unexecuted real-reward queries: {name}"
                )
    expected_digest = payload.get("inventory_digest")
    observed_digest = _payload_digest(payload, digest_field="inventory_digest")
    if not isinstance(expected_digest, str) or expected_digest != observed_digest:
        raise ValueError("ablation inventory digest mismatch")
    return observed_digest


def validate_resumable_development_job(
    output_path: str | Path,
    *,
    metadata_path: str | Path,
    registry_digest: str,
    checkpoint_digests,
    calibrator_digest: str,
    configuration_id: str,
    seeds,
    rollout_steps: int,
    verify_output_digest: bool = True,
) -> dict[str, object]:
    output_path = Path(output_path)
    metadata_path = Path(metadata_path)
    if not output_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("resumable development output or metadata is missing")
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = {
        "registry_digest": str(registry_digest),
        "checkpoint_digests": [str(value) for value in checkpoint_digests],
        "calibrator_digest": str(calibrator_digest),
        "configuration_id": str(configuration_id),
        "seeds": [int(value) for value in seeds],
        "rollout_steps": int(rollout_steps),
    }
    labels = {
        "registry_digest": "registry digest",
        "checkpoint_digests": "checkpoint digests",
        "calibrator_digest": "calibrator digest",
        "configuration_id": "configuration identity",
        "seeds": "seed set",
        "rollout_steps": "rollout length",
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ValueError(f"resumable development {labels[field]} mismatch")
    if payload.get("registry_digest") != expected["registry_digest"]:
        raise ValueError("resumable development registry digest mismatch")
    if payload.get("checkpoint_digests") != expected["checkpoint_digests"]:
        raise ValueError("resumable development checkpoint digests mismatch")
    seed_results = list(payload.get("seed_results", []))
    observed_seeds = [int(row["seed"]) for row in seed_results]
    if sorted(observed_seeds) != sorted(expected["seeds"]):
        raise ValueError("resumable development seed set mismatch")
    if len(observed_seeds) != len(set(observed_seeds)):
        raise ValueError("resumable development seed set contains duplicates")
    if any(len(row.get("steps", [])) != int(rollout_steps) for row in seed_results):
        raise ValueError("resumable development rollout length mismatch")
    if verify_output_digest:
        expected_output_digest = metadata.get("output_sha256")
        if (
            not isinstance(expected_output_digest, str)
            or _sha256_file(output_path) != expected_output_digest
        ):
            raise ValueError("resumable development output digest mismatch")
    return payload


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _canonical_config_id(config: Mapping[str, object]) -> str:
    encoded = json.dumps(
        {key: config[key] for key in GRID_KEYS},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return f"pcc-{hashlib.sha256(encoded).hexdigest()[:16]}"


def _seed_spec(seeds: Sequence[int]) -> str:
    return ",".join(str(int(value)) for value in seeds)


def _development_job(
    *,
    registry_path: Path,
    registry_digest: str,
    prepared_dir: Path,
    output_dir: Path,
    device: str,
    inventory,
    config: Mapping[str, object],
    rung_index: int,
    rung: DevelopmentRung,
    model_seed: int,
) -> dict[str, object]:
    config_id = str(config["id"])
    ensemble_size = int(config["ensemble_size"])
    policy_round = int(config["policy_round"])
    joint_coverage = float(config["joint_coverage"])
    checkpoint_root = inventory.checkpoint_root(
        model_seed,
        ensemble_size,
        policy_round,
    )
    checkpoint_digests = inventory.checkpoint_digests(
        model_seed,
        ensemble_size,
        policy_round,
    )
    calibrator = inventory.calibrator(
        model_seed,
        ensemble_size,
        policy_round,
        joint_coverage,
    )
    calibrator_digest = inventory.calibrator_digest(
        model_seed,
        ensemble_size,
        policy_round,
        joint_coverage,
    )
    job_root = output_dir / f"rung-{rung_index + 1}" / config_id
    output_path = job_root / f"model-{int(model_seed)}.json"
    metadata_path = job_root / f"model-{int(model_seed)}.meta.json"
    command = (
        sys.executable,
        "-m",
        "paper10_geojepa_mpc.experiments.run_pcc_rollouts",
        "--registry",
        str(registry_path),
        "--mode",
        "development",
        "--policy",
        "pcc_matched",
        "--env-source",
        "paper9",
        "--prepared-dir",
        str(prepared_dir),
        "--checkpoint-root",
        str(checkpoint_root),
        "--calibrator",
        str(calibrator),
        "--model-seed",
        str(int(model_seed)),
        "--seeds",
        _seed_spec(rung.seeds),
        "--rollout-steps",
        str(int(rung.steps)),
        "--planning-horizon",
        str(int(config["planning_horizon"])),
        "--compute-mode",
        "matched",
        "--tolerance-scale",
        str(float(config["tolerance_scale"])),
        "--residual-window",
        str(int(config["residual_window"])),
        "--device",
        str(device),
        "--output",
        str(output_path),
    )
    return {
        "id": f"rung-{rung_index + 1}/{config_id}/model-{int(model_seed)}",
        "rung": int(rung_index + 1),
        "configuration_id": config_id,
        "model_seed": int(model_seed),
        "policy": "pcc_matched",
        "seeds": list(rung.seeds),
        "rollout_steps": int(rung.steps),
        "registry_digest": str(registry_digest),
        "checkpoint_digests": list(checkpoint_digests),
        "calibrator_digest": str(calibrator_digest),
        "output": str(output_path),
        "metadata": str(metadata_path),
        "command": list(command),
    }


def _comparator_job(
    *,
    registry: Mapping[str, object],
    registry_path: Path,
    registry_digest: str,
    prepared_dir: Path,
    output_dir: Path,
    device: str,
    inventory,
    config: Mapping[str, object] | None,
    policy: str,
    rung_index: int,
    rung: DevelopmentRung,
    model_seed: int,
) -> dict[str, object]:
    learned = policy in MODEL_DEPENDENT_BASELINES
    if learned and config is None:
        raise ValueError("learned comparator requires a development configuration")
    comparator_id = (
        f"baseline-{policy}-{config['id']}" if learned else f"baseline-{policy}"
    )
    output_root = output_dir / f"rung-{rung_index + 1}" / "baselines" / comparator_id
    output_path = output_root / f"model-{int(model_seed)}.json"
    metadata_path = output_root / f"model-{int(model_seed)}.meta.json"
    if learned:
        checkpoint_root = inventory.checkpoint_root(
            model_seed,
            int(config["ensemble_size"]),
            int(config["policy_round"]),
        )
        checkpoint_digests = inventory.checkpoint_digests(
            model_seed,
            int(config["ensemble_size"]),
            int(config["policy_round"]),
        )
    else:
        checkpoint_root = None
        checkpoint_digests = (
            str(registry["offline_reference_policy"]["checkpoint_sha256"]),
        )
    command = [
        sys.executable,
        "-m",
        "paper10_geojepa_mpc.experiments.run_pcc_rollouts",
        "--registry",
        str(registry_path),
        "--mode",
        "development",
        "--policy",
        str(policy),
        "--env-source",
        "paper9",
        "--prepared-dir",
        str(prepared_dir),
        "--model-seed",
        str(int(model_seed)),
        "--seeds",
        _seed_spec(rung.seeds),
        "--rollout-steps",
        str(int(rung.steps)),
        "--device",
        str(device),
        "--output",
        str(output_path),
    ]
    if checkpoint_root is not None:
        output_index = command.index("--output")
        command[output_index:output_index] = [
            "--checkpoint-root",
            str(checkpoint_root),
            "--planning-horizon",
            str(int(config["planning_horizon"])),
        ]
    return {
        "id": f"rung-{rung_index + 1}/{comparator_id}/model-{int(model_seed)}",
        "rung": int(rung_index + 1),
        "configuration_id": comparator_id,
        "model_seed": int(model_seed),
        "policy": str(policy),
        "seeds": list(rung.seeds),
        "rollout_steps": int(rung.steps),
        "registry_digest": str(registry_digest),
        "checkpoint_digests": list(checkpoint_digests),
        "calibrator_digest": "not-applicable",
        "output": str(output_path),
        "metadata": str(metadata_path),
        "command": command,
    }


def _anchored_policy_job(
    *,
    registry: Mapping[str, object],
    registry_path: Path,
    registry_digest: str,
    prepared_dir: Path,
    output_dir: Path,
    device: str,
    inventory,
    policy: str,
    phase: str,
    model_seed: int,
    seeds: Sequence[int],
    rollout_steps: int,
) -> dict[str, object]:
    anchor = registry["development_baseline_anchor"]
    checkpoint_root = None
    calibrator = None
    if policy in MODEL_DEPENDENT_BASELINES or policy == "pcc_matched":
        checkpoint_root = inventory.checkpoint_root(
            model_seed,
            int(anchor["ensemble_size"]),
            int(anchor["policy_round"]),
        )
        checkpoint_digests = inventory.checkpoint_digests(
            model_seed,
            int(anchor["ensemble_size"]),
            int(anchor["policy_round"]),
        )
    else:
        checkpoint_digests = (
            str(registry["offline_reference_policy"]["checkpoint_sha256"]),
        )
    if policy == "pcc_matched":
        calibrator = inventory.calibrator(
            model_seed,
            int(anchor["ensemble_size"]),
            int(anchor["policy_round"]),
            float(anchor["joint_coverage"]),
        )
        calibrator_digest = inventory.calibrator_digest(
            model_seed,
            int(anchor["ensemble_size"]),
            int(anchor["policy_round"]),
            float(anchor["joint_coverage"]),
        )
    else:
        calibrator_digest = "not-applicable"
    job_root = output_dir / phase / policy
    output_path = job_root / f"model-{int(model_seed)}.json"
    metadata_path = job_root / f"model-{int(model_seed)}.meta.json"
    command = [
        sys.executable,
        "-m",
        "paper10_geojepa_mpc.experiments.run_pcc_rollouts",
        "--registry",
        str(registry_path),
        "--mode",
        "development",
        "--policy",
        str(policy),
        "--env-source",
        "paper9",
        "--prepared-dir",
        str(prepared_dir),
        "--model-seed",
        str(int(model_seed)),
        "--seeds",
        _seed_spec(seeds),
        "--rollout-steps",
        str(int(rollout_steps)),
        "--planning-horizon",
        str(int(anchor["planning_horizon"])),
        "--tolerance-scale",
        str(float(anchor["tolerance_scale"])),
        "--residual-window",
        str(int(anchor["residual_window"])),
        "--risk-penalty",
        str(float(anchor["risk_penalty"])),
        "--expert-learning-rate",
        str(float(anchor["expert_learning_rate"])),
        "--device",
        str(device),
    ]
    if checkpoint_root is not None:
        command.extend(("--checkpoint-root", str(checkpoint_root)))
    if calibrator is not None:
        command.extend(("--calibrator", str(calibrator)))
    command.extend(("--output", str(output_path)))
    configuration_id = f"{phase}-{policy}"
    return {
        "id": f"{configuration_id}/model-{int(model_seed)}",
        "phase": str(phase),
        "configuration_id": configuration_id,
        "model_seed": int(model_seed),
        "policy": str(policy),
        "seeds": [int(value) for value in seeds],
        "rollout_steps": int(rollout_steps),
        "registry_digest": str(registry_digest),
        "checkpoint_digests": list(checkpoint_digests),
        "calibrator_digest": str(calibrator_digest),
        "output": str(output_path),
        "metadata": str(metadata_path),
        "command": command,
    }


def build_pre_grid_jobs(
    registry: Mapping[str, object],
    *,
    registry_path: str | Path,
    registry_digest: str,
    inventory,
    prepared_dir: str | Path,
    output_dir: str | Path,
    device: str,
) -> list[dict[str, object]]:
    registry_path = Path(registry_path).resolve()
    prepared_dir = Path(prepared_dir).resolve()
    output_dir = Path(output_dir).resolve()
    anchor = registry["development_baseline_anchor"]
    jobs = [
        _anchored_policy_job(
            registry=registry,
            registry_path=registry_path,
            registry_digest=registry_digest,
            prepared_dir=prepared_dir,
            output_dir=output_dir,
            device=device,
            inventory=inventory,
            policy="pcc_matched",
            phase="stage_a",
            model_seed=int(model_seed),
            seeds=anchor["stage_a_seeds"],
            rollout_steps=int(anchor["stage_a_rollout_steps"]),
        )
        for model_seed in registry["model_seeds"]
    ]
    for policy in anchor["candidates"]:
        policy_models = (
            registry["model_seeds"]
            if policy in MODEL_DEPENDENT_BASELINES
            else registry["model_seeds"][:1]
        )
        jobs.extend(
            _anchored_policy_job(
                registry=registry,
                registry_path=registry_path,
                registry_digest=registry_digest,
                prepared_dir=prepared_dir,
                output_dir=output_dir,
                device=device,
                inventory=inventory,
                policy=str(policy),
                phase="baseline_selection",
                model_seed=int(model_seed),
                seeds=anchor["baseline_seeds"],
                rollout_steps=int(anchor["baseline_rollout_steps"]),
            )
            for model_seed in policy_models
        )
    identifiers = [str(job["id"]) for job in jobs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("pre-grid development job IDs are duplicated")
    return jobs


def build_rung_jobs(
    registry: Mapping[str, object],
    *,
    registry_path: str | Path,
    registry_digest: str,
    inventory,
    prepared_dir: str | Path,
    output_dir: str | Path,
    device: str,
    configurations,
    rung_index: int,
    rung: DevelopmentRung,
    comparator: str = "paper9_mpc",
) -> list[dict[str, object]]:
    registry_path = Path(registry_path).resolve()
    prepared_dir = Path(prepared_dir).resolve()
    output_dir = Path(output_dir).resolve()
    configurations = [dict(row) for row in configurations]
    jobs = [
        _development_job(
            registry_path=registry_path,
            registry_digest=registry_digest,
            prepared_dir=prepared_dir,
            output_dir=output_dir,
            device=device,
            inventory=inventory,
            config=config,
            rung_index=rung_index,
            rung=rung,
            model_seed=int(model_seed),
        )
        for config in configurations
        for model_seed in registry["model_seeds"]
    ]
    comparator_configs = configurations if comparator in MODEL_DEPENDENT_BASELINES else [None]
    jobs.extend(
        _comparator_job(
            registry=registry,
            registry_path=registry_path,
            registry_digest=registry_digest,
            prepared_dir=prepared_dir,
            output_dir=output_dir,
            device=device,
            inventory=inventory,
            config=config,
            policy=comparator,
            rung_index=rung_index,
            rung=rung,
            model_seed=int(model_seed),
        )
        for config in comparator_configs
        for model_seed in registry["model_seeds"]
    )
    identifiers = [str(job["id"]) for job in jobs]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("development rung job IDs are duplicated")
    return jobs


def _validated_seed_rows(
    payload: Mapping[str, object],
    *,
    policy: str,
    model_seed: int,
    seeds: tuple[int, ...],
) -> list[dict[str, object]]:
    rows = [dict(row) for row in payload.get("seed_results", [])]
    if len(rows) != len(seeds):
        raise ValueError("development payload has an incomplete seed block")
    observed = []
    for row in rows:
        if str(row.get("policy")) != str(policy):
            raise ValueError("development payload policy identity mismatch")
        if int(row.get("model_seed", -1)) != int(model_seed):
            raise ValueError("development payload model-seed identity mismatch")
        observed.append(int(row["seed"]))
    if tuple(sorted(observed)) != tuple(sorted(seeds)) or len(observed) != len(
        set(observed)
    ):
        raise ValueError("development payload has an incomplete seed block")
    return rows


def aggregate_development_rung(
    configurations,
    *,
    jobs,
    payloads: Mapping[str, Mapping[str, object]],
    model_seeds,
    seeds,
    draws: int = 20000,
) -> list[dict[str, object]]:
    configurations = [dict(row) for row in configurations]
    jobs = [dict(row) for row in jobs]
    model_seeds = tuple(int(value) for value in model_seeds)
    seeds = tuple(int(value) for value in seeds)
    comparator_jobs: dict[tuple[str, int], dict[str, object]] = {}
    pcc_jobs: dict[tuple[str, int], dict[str, object]] = {}
    for job in jobs:
        key = (str(job["configuration_id"]), int(job["model_seed"]))
        destination = (
            pcc_jobs if str(job["policy"]) == "pcc_matched" else comparator_jobs
        )
        if key in destination:
            raise ValueError("development rung contains duplicate model jobs")
        destination[key] = job

    output = []
    for config in configurations:
        config_id = str(config["id"])
        comparator = str(config["primary_candidate"])
        combined_rows = []
        observed_models = set()
        for model_seed in model_seeds:
            pcc_job = pcc_jobs.get((config_id, model_seed))
            comparator_id = (
                f"baseline-{comparator}-{config_id}"
                if comparator in MODEL_DEPENDENT_BASELINES
                else f"baseline-{comparator}"
            )
            comparator_job = comparator_jobs.get((comparator_id, model_seed))
            if pcc_job is None or comparator_job is None:
                raise ValueError("development rung has an incomplete model-seed block")
            try:
                pcc_payload = payloads[str(pcc_job["id"])]
                comparator_payload = payloads[str(comparator_job["id"])]
            except KeyError as exc:
                raise ValueError(
                    "development rung has an incomplete model-seed block"
                ) from exc
            combined_rows.extend(
                _validated_seed_rows(
                    pcc_payload,
                    policy="pcc_matched",
                    model_seed=model_seed,
                    seeds=seeds,
                )
            )
            combined_rows.extend(
                _validated_seed_rows(
                    comparator_payload,
                    policy=comparator,
                    model_seed=model_seed,
                    seeds=seeds,
                )
            )
            observed_models.add(model_seed)
        if observed_models != set(model_seeds):
            raise ValueError("development rung has an incomplete model-seed block")
        row = development_row(config, combined_rows, draws=draws)
        row["model_seeds"] = list(model_seeds)
        row["source_seeds"] = list(seeds)
        output.append(row)
    return output


def aggregate_primary_comparators(
    *,
    jobs,
    payloads: Mapping[str, Mapping[str, object]],
    candidates,
    model_seeds,
    seeds,
    draws: int,
    bootstrap_seed: int,
) -> list[dict[str, object]]:
    candidates = tuple(str(value) for value in candidates)
    model_seeds = tuple(int(value) for value in model_seeds)
    seeds = tuple(int(value) for value in seeds)
    jobs_by_policy: dict[str, dict[int, dict[str, object]]] = {}
    for source in jobs:
        job = dict(source)
        if job.get("phase") != "baseline_selection":
            continue
        policy = str(job["policy"])
        model_seed = int(job["model_seed"])
        policy_jobs = jobs_by_policy.setdefault(policy, {})
        if model_seed in policy_jobs:
            raise ValueError("baseline selection contains duplicate model jobs")
        policy_jobs[model_seed] = job
    if set(jobs_by_policy) != set(candidates):
        raise ValueError("baseline selection jobs do not match the candidate set")

    mapped: dict[str, dict[tuple[int, int], dict[str, object]]] = {}
    physical_blocks = {}
    for policy in candidates:
        policy_jobs = jobs_by_policy[policy]
        expected_models = (
            model_seeds if policy in MODEL_DEPENDENT_BASELINES else None
        )
        if expected_models is not None and set(policy_jobs) != set(expected_models):
            raise ValueError("baseline has an incomplete model-seed block")
        if expected_models is None and len(policy_jobs) != 1:
            raise ValueError("shared baseline must have one physical model block")
        physical_blocks[policy] = len(policy_jobs)
        by_pair = {}
        for source_model, job in policy_jobs.items():
            try:
                payload = payloads[str(job["id"])]
            except KeyError as exc:
                raise ValueError("baseline selection payload is missing") from exc
            rows = _validated_seed_rows(
                payload,
                policy=policy,
                model_seed=source_model,
                seeds=seeds,
            )
            target_models = (
                (source_model,)
                if policy in MODEL_DEPENDENT_BASELINES
                else model_seeds
            )
            for target_model in target_models:
                for row in rows:
                    copied = dict(row)
                    copied["model_seed"] = int(target_model)
                    copied["source_model_seed"] = int(source_model)
                    key = (int(target_model), int(row["seed"]))
                    by_pair[key] = copied
        mapped[policy] = by_pair

    reference = mapped.get("paper9_mpc")
    if reference is None:
        raise ValueError("baseline candidate set must include paper9_mpc")
    expected_pairs = {
        (model_seed, seed) for model_seed in model_seeds for seed in seeds
    }
    if set(reference) != expected_pairs:
        raise ValueError("paper9 baseline pairing block is incomplete")
    output = []
    ordered_pairs = sorted(expected_pairs)
    for policy in candidates:
        if set(mapped[policy]) != expected_pairs:
            raise ValueError("baseline pairing block is incomplete")
        effects = np.stack(
            [
                np.asarray(mapped[policy][key]["objective_outcome"], dtype=np.float64)
                - np.asarray(reference[key]["objective_outcome"], dtype=np.float64)
                for key in ordered_pairs
            ],
            axis=0,
        )
        seed_effects = _mean_effects_by_rollout_seed(effects, ordered_pairs)
        lower = _one_sided_seed_bootstrap_lower(
            seed_effects,
            draws=int(draws),
            seed=int(bootstrap_seed),
        )
        evaluations = []
        for job in jobs_by_policy[policy].values():
            payload = payloads[str(job["id"])]
            for row in payload["seed_results"]:
                for step in row.get("steps", []):
                    value = float(step.get("member_evaluations", 0))
                    if not np.isfinite(value) or value < 0.0:
                        raise ValueError("baseline member evaluations are invalid")
                    evaluations.append(value)
        output.append(
            {
                "id": policy,
                "planning_gate_count": int(np.sum(lower[1:] >= 0.0)),
                "reward": float(effects[:, 0].mean()),
                "compute": float(np.mean(evaluations)) if evaluations else 0.0,
                "compute_unit": "mean_member_evaluations_per_step",
                "lower_95_one_sided": lower.tolist(),
                "paired_observations": int(effects.shape[0]),
                "bootstrap_rollout_seeds": int(seed_effects.shape[0]),
                "physical_model_blocks": int(physical_blocks[policy]),
                "model_seeds": list(model_seeds),
                "source_seeds": list(seeds),
            }
        )
    return output


def build_execution_plan(
    registry: dict[str, object],
    *,
    registry_path: str | Path,
    registry_digest: str,
    inventory,
    prepared_dir: str | Path,
    output_dir: str | Path,
    device: str,
) -> dict[str, object]:
    schedule = build_development_schedule(registry)
    configs = []
    for values in enumerate_grid(registry["grid"]):
        config = dict(values)
        config["id"] = _canonical_config_id(config)
        config["policy"] = "pcc_matched"
        config["primary_candidate"] = None
        config["development_bootstrap_seed"] = 20260710
        configs.append(config)
    if len({str(row["id"]) for row in configs}) != len(configs):
        raise ValueError("development configuration IDs are not unique")
    registry_path = Path(registry_path).resolve()
    prepared_dir = Path(prepared_dir).resolve()
    output_dir = Path(output_dir).resolve()
    pre_grid_jobs = build_pre_grid_jobs(
        registry,
        registry_path=registry_path,
        registry_digest=registry_digest,
        inventory=inventory,
        prepared_dir=prepared_dir,
        output_dir=output_dir,
        device=device,
    )
    return {
        "schema_version": 1,
        "protocol_id": str(registry["protocol_id"]),
        "registry_digest": str(registry_digest),
        "model_seeds": [int(value) for value in registry["model_seeds"]],
        "rungs": [
            {
                "rung": index + 1,
                "seeds": list(rung.seeds),
                "rollout_steps": int(rung.steps),
                "keep": int(rung.keep),
                "selection_required": index > 0,
            }
            for index, rung in enumerate(schedule)
        ],
        "configurations": configs,
        "phase": "pre_grid",
        "baseline_candidates": list(
            registry["development_baseline_anchor"]["candidates"]
        ),
        "grid_jobs_pending_primary_comparator": True,
        "jobs": pre_grid_jobs,
        "pending_rungs": [1, 2, 3],
    }


def _write_json_atomic(path: str | Path, payload: Mapping[str, object]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _selection_key(row: Mapping[str, object]):
    return (
        -int(row["planning_gate_count"]),
        -float(row["reward"]),
        float(row["compute"]),
        str(row["id"]),
    )


def retain_configurations(rows, *, keep: int) -> dict[str, object]:
    rows = list(rows)
    if int(keep) <= 0 or int(keep) > len(rows):
        raise ValueError("rung keep count is outside the available rows")
    select_configuration(rows)
    ranked = sorted(rows, key=_selection_key)
    retained = [dict(row) for row in ranked[: int(keep)]]
    rejected = [
        {
            "id": str(row["id"]),
            "rank": int(rank),
            "reason": f"outside_top_{int(keep)}",
        }
        for rank, row in enumerate(ranked[int(keep) :], start=int(keep) + 1)
    ]
    return {"retained": retained, "rejected": rejected}


def _job_metadata(job: Mapping[str, object]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "registry_digest": str(job["registry_digest"]),
        "checkpoint_digests": [
            str(value) for value in job["checkpoint_digests"]
        ],
        "calibrator_digest": str(job["calibrator_digest"]),
        "configuration_id": str(job["configuration_id"]),
        "seeds": [int(value) for value in job["seeds"]],
        "rollout_steps": int(job["rollout_steps"]),
        "output_sha256": None,
    }


def execute_development_job(
    job: Mapping[str, object],
    *,
    resume: bool = False,
    runner=subprocess.run,
) -> dict[str, object]:
    output_path = Path(str(job["output"]))
    metadata_path = Path(str(job["metadata"]))
    expected_metadata = _job_metadata(job)
    command = list(job["command"])
    if resume and metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        for field, value in expected_metadata.items():
            if field == "output_sha256":
                continue
            if metadata.get(field) != value:
                raise ValueError(
                    f"resumable development {field} mismatch"
                )
        if isinstance(metadata.get("output_sha256"), str):
            return validate_resumable_development_job(
                output_path,
                metadata_path=metadata_path,
                registry_digest=expected_metadata["registry_digest"],
                checkpoint_digests=expected_metadata["checkpoint_digests"],
                calibrator_digest=expected_metadata["calibrator_digest"],
                configuration_id=expected_metadata["configuration_id"],
                seeds=expected_metadata["seeds"],
                rollout_steps=expected_metadata["rollout_steps"],
            )
        if metadata.get("output_sha256") is not None:
            raise ValueError("resumable development output digest state is invalid")
        if output_path.is_file():
            partial = json.loads(output_path.read_text(encoding="utf-8"))
            if partial.get("registry_digest") != expected_metadata["registry_digest"]:
                raise ValueError("partial development registry digest mismatch")
            if partial.get("checkpoint_digests") != expected_metadata[
                "checkpoint_digests"
            ]:
                raise ValueError("partial development checkpoint digest mismatch")
            rows = list(partial.get("seed_results", []))
            observed = [int(row["seed"]) for row in rows]
            if (
                len(observed) != len(set(observed))
                or not set(observed).issubset(set(expected_metadata["seeds"]))
            ):
                raise ValueError("partial development seed set mismatch")
            if any(
                len(row.get("steps", []))
                != expected_metadata["rollout_steps"]
                for row in rows
            ):
                raise ValueError("partial development rollout length mismatch")
        if "--resume" not in command:
            command.append("--resume")
    elif output_path.exists() or metadata_path.exists():
        raise ValueError("development output exists without a valid resume request")
    else:
        _write_json_atomic(metadata_path, expected_metadata)
    completed = runner(command, check=False)
    if int(completed.returncode) != 0:
        raise RuntimeError(
            f"development worker failed with exit code {completed.returncode}"
        )
    if not output_path.is_file():
        raise FileNotFoundError("development worker did not write its output")
    expected_metadata["output_sha256"] = _sha256_file(output_path)
    _write_json_atomic(metadata_path, expected_metadata)
    return validate_resumable_development_job(
        output_path,
        metadata_path=metadata_path,
        registry_digest=expected_metadata["registry_digest"],
        checkpoint_digests=expected_metadata["checkpoint_digests"],
        calibrator_digest=expected_metadata["calibrator_digest"],
        configuration_id=expected_metadata["configuration_id"],
        seeds=expected_metadata["seeds"],
        rollout_steps=expected_metadata["rollout_steps"],
    )


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--calibration-root", required=True)
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--bootstrap-draws", type=int, default=20000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--freeze", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry_path = Path(args.registry).resolve()
    registry = load_registry(registry_path)
    validate_registry(registry)
    if registry.get("status") != "development":
        raise ValueError("development orchestrator requires a development registry")
    if args.dry_run and args.freeze:
        raise ValueError("dry-run cannot freeze the registry")
    registry_digest = _sha256_file(registry_path)
    inventory = build_inventory(
        args.checkpoint_root,
        calibrator_root=args.calibration_root,
        model_seeds=registry["model_seeds"],
        registry=registry,
        require_complete=True,
    )
    plan = build_execution_plan(
        registry,
        registry_path=registry_path,
        registry_digest=registry_digest,
        inventory=inventory,
        prepared_dir=args.prepared_dir,
        output_dir=args.output_dir,
        device=args.device,
    )
    plan_path = Path(args.output_dir).resolve() / "execution_plan.json"
    _write_json_atomic(plan_path, plan)
    if args.dry_run:
        print(json.dumps({"plan": str(plan_path), "jobs": len(plan["jobs"])}))
        return

    output_dir = Path(args.output_dir).resolve()
    pre_grid_jobs = [dict(job) for job in plan["jobs"]]
    pre_grid_payloads = {
        str(job["id"]): execute_development_job(
            job,
            resume=bool(args.resume),
        )
        for job in pre_grid_jobs
    }
    anchor = registry["development_baseline_anchor"]
    stage_jobs = [job for job in pre_grid_jobs if job["phase"] == "stage_a"]
    stage_payloads = {
        str(job["model_seed"]): pre_grid_payloads[str(job["id"])]
        for job in stage_jobs
    }
    stage_report = stage_a_report_from_payloads(
        stage_payloads,
        model_seeds=registry["model_seeds"],
        seeds=anchor["stage_a_seeds"],
        nominal_coverage=float(anchor["joint_coverage"]),
    )
    _write_json_atomic(output_dir / "stage_a_report.json", stage_report)
    if stage_report.get("passed") is not True:
        raise ValueError("Stage A failed; bounded development is blocked")

    baseline_jobs = [
        job for job in pre_grid_jobs if job["phase"] == "baseline_selection"
    ]
    baseline_rows = aggregate_primary_comparators(
        jobs=baseline_jobs,
        payloads=pre_grid_payloads,
        candidates=anchor["candidates"],
        model_seeds=registry["model_seeds"],
        seeds=anchor["baseline_seeds"],
        draws=int(args.bootstrap_draws),
        bootstrap_seed=20260710,
    )
    selected_comparator = select_primary_comparator(
        baseline_rows,
        candidates=anchor["candidates"],
    )
    comparator = str(selected_comparator["id"])
    baseline_report = {
        "schema_version": 1,
        "anchor": dict(anchor),
        "rows": baseline_rows,
        "selected": selected_comparator,
        "primary_comparator": comparator,
    }
    _write_json_atomic(output_dir / "baseline_selection.json", baseline_report)

    schedule = build_development_schedule(registry)
    active = [dict(row) for row in plan["configurations"]]
    for config in active:
        config["primary_candidate"] = comparator
    rung_summaries = []
    all_rejected = []
    for rung_index, rung in enumerate(schedule):
        jobs = build_rung_jobs(
            registry,
            registry_path=registry_path,
            registry_digest=registry_digest,
            inventory=inventory,
            prepared_dir=args.prepared_dir,
            output_dir=output_dir,
            device=args.device,
            configurations=active,
            rung_index=rung_index,
            rung=rung,
            comparator=comparator,
        )
        plan["jobs"] = jobs
        plan["phase"] = "grid"
        plan["primary_comparator"] = comparator
        plan["grid_jobs_pending_primary_comparator"] = False
        plan["active_rung"] = rung_index + 1
        plan["pending_rungs"] = list(range(rung_index + 2, len(schedule) + 1))
        _write_json_atomic(plan_path, plan)
        payloads = {
            str(job["id"]): execute_development_job(
                job,
                resume=bool(args.resume),
            )
            for job in jobs
        }
        rows = aggregate_development_rung(
            active,
            jobs=jobs,
            payloads=payloads,
            model_seeds=registry["model_seeds"],
            seeds=rung.seeds,
            draws=int(args.bootstrap_draws),
        )
        keep = (
            schedule[rung_index + 1].keep
            if rung_index + 1 < len(schedule)
            else 1
        )
        retention = retain_configurations(rows, keep=keep)
        rung_summary = {
            "rung": rung_index + 1,
            "seeds": list(rung.seeds),
            "rollout_steps": int(rung.steps),
            "evaluated": len(rows),
            "retained": len(retention["retained"]),
            "rows": rows,
            "rejected": retention["rejected"],
        }
        _write_json_atomic(
            output_dir / f"rung-{rung_index + 1}-summary.json",
            rung_summary,
        )
        rung_summaries.append(rung_summary)
        all_rejected.extend(
            {"rung": rung_index + 1, **row}
            for row in retention["rejected"]
        )
        retained_ids = {str(row["id"]) for row in retention["retained"]}
        active = [row for row in active if str(row["id"]) in retained_ids]

    winner_id = str(active[0]["id"])
    winner = next(
        dict(row)
        for row in rung_summaries[-1]["rows"]
        if str(row["id"]) == winner_id
    )
    summary = {
        "schema_version": 1,
        "protocol_id": str(registry["protocol_id"]),
        "registry_digest": registry_digest,
        "stage_a_report": stage_report,
        "baseline_selection": baseline_report,
        "primary_comparator": comparator,
        "rungs": [
            {
                key: row[key]
                for key in (
                    "rung",
                    "seeds",
                    "rollout_steps",
                    "evaluated",
                    "retained",
                )
            }
            for row in rung_summaries
        ],
        "winner": winner,
        "rejected": all_rejected,
    }
    summary_path = output_dir / "development_summary.json"
    _write_json_atomic(summary_path, summary)
    if args.freeze:
        ablation_path = output_dir / "ablation_inventory.json"
        if not ablation_path.is_file():
            raise FileNotFoundError(
                "freeze requires output-dir/ablation_inventory.json"
            )
        ablation_payload = json.loads(ablation_path.read_text(encoding="utf-8"))
        ablation_digest = validate_ablation_inventory(
            ablation_payload,
            registry=registry,
            selected_config=winner,
            registry_digest=registry_digest,
        )
        winner["development_artifact_digest"] = _sha256_file(summary_path)
        winner["ablation_inventory_digest"] = ablation_digest
        ensemble_size = int(winner["ensemble_size"])
        policy_round = int(winner["policy_round"])
        joint_coverage = float(winner["joint_coverage"])
        checkpoint_digests = []
        calibrator_digests = {}
        for model_seed in registry["model_seeds"]:
            checkpoint_digests.extend(
                inventory.checkpoint_digests(
                    int(model_seed),
                    ensemble_size,
                    policy_round,
                )
            )
            calibrator_digests[str(int(model_seed))] = (
                inventory.calibrator_digest(
                    int(model_seed),
                    ensemble_size,
                    policy_round,
                    joint_coverage,
                )
            )
        frozen = freeze_development(
            registry_path,
            development_rows=[winner],
            stage_a_report=stage_report,
            primary_comparator=comparator,
            checkpoint_digests=checkpoint_digests,
            calibrator_digest=calibrator_digests,
            expert_learning_rate=float(anchor["expert_learning_rate"]),
            compute_budget=int(
                registry["compute_budget"]["single_model_candidate_equivalents"]
            ),
            completed_ablations=ablation_payload["ablations"],
        )
        print(
            json.dumps(
                {
                    "summary": str(summary_path),
                    "winner": winner_id,
                    "frozen_digest": frozen["frozen_digest"],
                }
            )
        )
        return
    print(json.dumps({"summary": str(summary_path), "winner": winner_id}))


def enumerate_grid(grid: dict[str, list]) -> list[dict[str, object]]:
    if set(grid) != set(GRID_KEYS):
        raise ValueError("development grid fields do not match the locked protocol")
    return [
        dict(zip(GRID_KEYS, values))
        for values in product(*(grid[key] for key in GRID_KEYS))
    ]


def select_configuration(rows):
    rows = list(rows)
    if not rows:
        raise ValueError("development rows are empty")
    for row in rows:
        required = ("id", "planning_gate_count", "reward", "compute")
        if any(key not in row for key in required):
            raise ValueError("development row is missing a selection field")
        if not np.isfinite([row["reward"], row["compute"]]).all():
            raise ValueError("development selection values must be finite")
    return sorted(
        rows,
        key=lambda row: (
            -int(row["planning_gate_count"]),
            -float(row["reward"]),
            float(row["compute"]),
            str(row["id"]),
        ),
    )[0]


def binomial_acceptance_interval(
    n: int,
    probability: float,
    alpha: float = 0.05,
) -> tuple[int, int]:
    if int(n) <= 0 or not 0.0 < float(probability) < 1.0:
        raise ValueError("n must be positive and probability in (0, 1)")
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    probabilities = np.asarray(
        [
            math.comb(int(n), count)
            * float(probability) ** count
            * (1.0 - float(probability)) ** (int(n) - count)
            for count in range(int(n) + 1)
        ],
        dtype=np.float64,
    )
    cumulative = np.cumsum(probabilities)
    lower = int(np.searchsorted(cumulative, float(alpha) / 2.0, side="left"))
    upper = int(
        np.searchsorted(cumulative, 1.0 - float(alpha) / 2.0, side="left")
    )
    return lower, min(upper, int(n))


def _rankdata(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        average_rank = 0.5 * (start + end - 1)
        ranks[order[start:end]] = average_rank
        start = end
    return ranks


def stage_a_gate(
    *,
    uncertainty,
    absolute_error,
    covered_trajectories: int,
    n_trajectories: int,
    nominal_coverage: float,
) -> dict[str, object]:
    uncertainty = np.asarray(uncertainty, dtype=np.float64).reshape(-1)
    error = np.asarray(absolute_error, dtype=np.float64).reshape(-1)
    if uncertainty.shape != error.shape or uncertainty.size < 2:
        raise ValueError("uncertainty and error must share at least two observations")
    if not np.isfinite(uncertainty).all() or not np.isfinite(error).all():
        raise ValueError("Stage A arrays must be finite")
    ranked_uncertainty = _rankdata(uncertainty)
    ranked_error = _rankdata(error)
    if ranked_uncertainty.std() == 0.0 or ranked_error.std() == 0.0:
        correlation = 0.0
    else:
        correlation = float(np.corrcoef(ranked_uncertainty, ranked_error)[0, 1])
    lower, upper = binomial_acceptance_interval(
        int(n_trajectories),
        float(nominal_coverage),
    )
    coverage_passed = lower <= int(covered_trajectories) <= upper
    return {
        "passed": bool(correlation > 0.0 and coverage_passed),
        "spearman_uncertainty_error": correlation,
        "covered_trajectories": int(covered_trajectories),
        "n_trajectories": int(n_trajectories),
        "coverage_acceptance_interval": [lower, upper],
        "coverage_passed": bool(coverage_passed),
    }


def freeze_development(
    registry_path: str | Path,
    *,
    development_rows,
    stage_a_report: dict[str, object],
    primary_comparator: str,
    checkpoint_digests,
    calibrator_digest: Mapping[str, str],
    expert_learning_rate: float,
    compute_budget: int,
    completed_ablations,
) -> dict[str, object]:
    registry = load_registry(registry_path)
    validate_registry(registry)
    if stage_a_report.get("passed") is not True:
        raise ValueError("Stage A must pass before protocol freeze")
    primary_comparator = str(primary_comparator)
    if primary_comparator in set(registry.get("diagnostic_policies", [])):
        raise ValueError("oracle diagnostic cannot be the primary comparator")
    if primary_comparator not in set(registry["deployable_baselines"]):
        raise ValueError("primary comparator is not a deployable baseline")
    if primary_comparator in {"pcc_matched", "pcc_full"}:
        raise ValueError("PCC policy cannot be its own primary comparator")

    completed_ablations = [str(value) for value in completed_ablations]
    required_ablations = [str(value) for value in registry["required_ablations"]]
    if (
        len(completed_ablations) != len(set(completed_ablations))
        or set(completed_ablations) != set(required_ablations)
    ):
        raise ValueError("required ablation inventory is incomplete")

    selected = dict(select_configuration(development_rows))
    required_selected_fields = {
        "id",
        "ensemble_size",
        "joint_coverage",
        "tolerance_scale",
        "planning_horizon",
        "residual_window",
        "policy_round",
        "model_seeds",
        "source_seeds",
        "development_artifact_digest",
        "ablation_inventory_digest",
    }
    missing = sorted(required_selected_fields - set(selected))
    if missing:
        raise ValueError(f"selected development fields are missing: {missing}")
    expected_model_seeds = [int(value) for value in registry["model_seeds"]]
    if [int(value) for value in selected["model_seeds"]] != expected_model_seeds:
        raise ValueError("selected configuration has an incomplete model-seed block")
    expected_source_seeds = [
        int(value) for value in registry["partitions"]["development"]
    ]
    if [int(value) for value in selected["source_seeds"]] != expected_source_seeds:
        raise ValueError("selected configuration source seeds are not the final development block")
    for field in ("development_artifact_digest", "ablation_inventory_digest"):
        if not _is_sha256(selected[field]):
            raise ValueError(f"{field} must be SHA-256")

    checkpoint_digests = [str(value) for value in checkpoint_digests]
    expected_checkpoint_count = len(expected_model_seeds) * int(
        selected["ensemble_size"]
    )
    if (
        len(checkpoint_digests) != expected_checkpoint_count
        or len(set(checkpoint_digests)) != expected_checkpoint_count
        or not all(_is_sha256(value) for value in checkpoint_digests)
    ):
        raise ValueError(
            "checkpoint digests must cover the distinct 3 x K physical members"
        )
    calibrator_digest = {
        str(key): str(value) for key, value in dict(calibrator_digest).items()
    }
    expected_calibrator_keys = {str(value) for value in expected_model_seeds}
    if (
        set(calibrator_digest) != expected_calibrator_keys
        or not all(_is_sha256(value) for value in calibrator_digest.values())
    ):
        raise ValueError("calibrator digests must cover every model seed")
    if not np.isfinite(expert_learning_rate) or float(expert_learning_rate) <= 0.0:
        raise ValueError("expert learning rate must be positive")
    if int(compute_budget) != 50:
        raise ValueError("PCC matched compute budget is locked to 50")

    selected.update(
        {
            "primary_comparator": primary_comparator,
            "checkpoint_digests": checkpoint_digests,
            "calibrator_digest": calibrator_digest,
            "expert_learning_rate": float(expert_learning_rate),
            "compute_budget": int(compute_budget),
            "stage_a_report": dict(stage_a_report),
            "completed_ablations": sorted(completed_ablations),
        }
    )
    return freeze_registry(registry_path, selected_config=selected)
