import argparse
import json
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_confirmation_artifacts import (
    MODEL_INDEPENDENT_POLICIES,
    REFERENCE_CHECKPOINT_POLICIES,
    complete_policy_block,
    load_confirmation_artifacts,
    seed_level_rows as _seed_level_rows,
    verify_model_dependent_checkpoints as _verify_model_dependent_checkpoints,
    verify_reference_policy_checkpoints as _verify_reference_policy_checkpoints,
    write_confirmation_outputs as _write_outputs,
)
from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


def _validated_differences(differences) -> np.ndarray:
    values = np.asarray(differences, dtype=np.float64)
    if values.ndim != 3 or values.shape[-1] != len(OBJECTIVE_NAMES):
        raise ValueError(
            "differences must have shape [training_seeds, rollout_seeds, 4]"
        )
    if min(values.shape[:2]) <= 0 or not np.isfinite(values).all():
        raise ValueError("differences must be non-empty and finite")
    return values


def hierarchical_bootstrap(differences, draws: int, seed: int) -> np.ndarray:
    values = _validated_differences(differences)
    if int(draws) <= 0:
        raise ValueError("draws must be positive")
    rng = np.random.default_rng(int(seed))
    sampled = np.empty((int(draws), values.shape[-1]), dtype=np.float64)
    for draw in range(int(draws)):
        training_indexes = rng.integers(
            0,
            values.shape[0],
            size=values.shape[0],
        )
        blocks = []
        for training_index in training_indexes:
            rollout_indexes = rng.integers(
                0,
                values.shape[1],
                size=values.shape[1],
            )
            blocks.append(values[training_index, rollout_indexes])
        sampled[draw] = np.concatenate(blocks, axis=0).mean(axis=0)
    return sampled


def _per_training_seed_lower_bounds(
    values: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(int(seed))
    output = []
    for training_index in range(values.shape[0]):
        sampled = np.empty((int(draws), values.shape[-1]), dtype=np.float64)
        for draw in range(int(draws)):
            rollout_indexes = rng.integers(
                0,
                values.shape[1],
                size=values.shape[1],
            )
            sampled[draw] = values[training_index, rollout_indexes].mean(axis=0)
        output.append(np.quantile(sampled, 0.05, axis=0))
    return np.stack(output, axis=0)


def evaluate_success(
    differences,
    *,
    bootstrap_seed: int = 20260710,
    draws: int = 20000,
) -> dict[str, object]:
    values = _validated_differences(differences)
    bootstrap = hierarchical_bootstrap(values, draws=draws, seed=bootstrap_seed)
    lower = np.quantile(bootstrap, 0.05, axis=0)
    descriptive_lower = np.quantile(bootstrap, 0.025, axis=0)
    descriptive_upper = np.quantile(bootstrap, 0.975, axis=0)
    per_training_lower = _per_training_seed_lower_bounds(
        values,
        draws=draws,
        seed=int(bootstrap_seed) + 1,
    )
    support_by_training = (per_training_lower[:, 0] > 0.0) & np.all(
        per_training_lower[:, 1:] >= 0.0,
        axis=1,
    )
    planning = {
        name: bool(lower[index] >= 0.0)
        for index, name in enumerate(OBJECTIVE_NAMES[1:], start=1)
    }
    reward_superiority = bool(lower[0] > 0.0)
    primary_success = bool(
        reward_superiority
        and all(planning.values())
        and int(support_by_training.sum()) >= 2
    )
    wins = (values > 0.0).sum(axis=(0, 1))
    losses = (values < 0.0).sum(axis=(0, 1))
    ties = (values == 0.0).sum(axis=(0, 1))
    return {
        "n_training_seeds": int(values.shape[0]),
        "n_rollout_seeds": int(values.shape[1]),
        "mean_effect": dict(zip(OBJECTIVE_NAMES, values.mean(axis=(0, 1)).tolist())),
        "median_effect": dict(
            zip(OBJECTIVE_NAMES, np.median(values, axis=(0, 1)).tolist())
        ),
        "lower_95_one_sided": dict(zip(OBJECTIVE_NAMES, lower.tolist())),
        "interval_95_two_sided": {
            name: [float(descriptive_lower[index]), float(descriptive_upper[index])]
            for index, name in enumerate(OBJECTIVE_NAMES)
        },
        "wins": dict(zip(OBJECTIVE_NAMES, wins.astype(int).tolist())),
        "losses": dict(zip(OBJECTIVE_NAMES, losses.astype(int).tolist())),
        "ties": dict(zip(OBJECTIVE_NAMES, ties.astype(int).tolist())),
        "reward_superiority": reward_superiority,
        "planning_noninferiority": planning,
        "per_training_seed_lower_95_one_sided": per_training_lower.tolist(),
        "training_seed_support": support_by_training.tolist(),
        "training_seed_joint_support": int(support_by_training.sum()),
        "primary_success": primary_success,
    }


def _directional_external_success(
    differences: np.ndarray,
    *,
    bootstrap_seed: int,
    draws: int,
) -> dict[str, object]:
    bootstrap = hierarchical_bootstrap(
        differences,
        draws=draws,
        seed=bootstrap_seed,
    )
    lower = np.quantile(bootstrap, 0.05, axis=0)
    gates = {name: bool(value >= 0.0) for name, value in zip(OBJECTIVE_NAMES, lower)}
    return {
        "lower_95_one_sided": dict(zip(OBJECTIVE_NAMES, lower.tolist())),
        "directional_gates": gates,
        "directional_success": bool(all(gates.values())),
    }


def evaluate_locked_confirmation(
    primary_differences,
    matched_compute_differences,
    dongxing_differences,
    *,
    information_audit_passed: bool,
    bootstrap_seed: int = 20260710,
    draws: int = 20000,
) -> dict[str, object]:
    arrays = [
        _validated_differences(primary_differences),
        _validated_differences(matched_compute_differences),
        _validated_differences(dongxing_differences),
    ]
    if any(values.shape != (3, 20, 4) for values in arrays):
        raise ValueError("locked confirmation requires complete 3 x 20 x 4 blocks")
    primary = evaluate_success(
        arrays[0],
        bootstrap_seed=bootstrap_seed,
        draws=draws,
    )
    matched = evaluate_success(
        arrays[1],
        bootstrap_seed=int(bootstrap_seed) + 1000,
        draws=draws,
    )
    dongxing = _directional_external_success(
        arrays[2],
        bootstrap_seed=int(bootstrap_seed) + 2000,
        draws=draws,
    )
    overall = bool(
        primary["primary_success"]
        and matched["primary_success"]
        and dongxing["directional_success"]
        and information_audit_passed
    )
    return {
        "primary": primary,
        "matched_compute": matched,
        "dongxing": dongxing,
        "information_audit_passed": bool(information_audit_passed),
        "overall_success": overall,
    }


def manuscript_claim_gate(report: dict[str, object]) -> dict[str, object]:
    locked = report.get("locked_confirmation", report)
    primary = locked["primary"]
    matched = locked["matched_compute"]
    dongxing = locked["dongxing"]
    failures = []

    primary_atomic_failed = False
    if primary.get("reward_superiority") is not True:
        failures.append("bishan.reward")
        primary_atomic_failed = True
    for objective, passed in primary.get("planning_noninferiority", {}).items():
        if passed is not True:
            failures.append(f"bishan.{objective}")
            primary_atomic_failed = True
    if (
        not primary_atomic_failed
        and int(primary.get("training_seed_joint_support", 0)) < 2
    ):
        failures.append("bishan.minimum_supporting_model_seeds")

    matched_atomic_failed = False
    if matched.get("reward_superiority") is not True:
        failures.append("matched_compute.reward")
        matched_atomic_failed = True
    for objective, passed in matched.get("planning_noninferiority", {}).items():
        if passed is not True:
            failures.append(f"matched_compute.{objective}")
            matched_atomic_failed = True
    if (
        not matched_atomic_failed
        and int(matched.get("training_seed_joint_support", 0)) < 2
    ):
        failures.append("matched_compute.minimum_supporting_model_seeds")

    for objective, passed in dongxing.get("directional_gates", {}).items():
        if passed is not True:
            failures.append(f"dongxing.{objective}")
    if locked.get("information_audit_passed") is not True:
        failures.append("information_set.zero_unexecuted_real_reward_queries")

    success = bool(locked.get("overall_success") is True and not failures)
    return {
        "primary_success": success,
        "failed_gates": failures,
        "allow_performance_breakthrough_claim": success,
        "allowed_claims": (
            ["locked PCC improvement with planning non-inferiority"]
            if success
            else ["locked confirmation did not satisfy every primary condition"]
        ),
        "forbidden_claims": (
            []
            if success
            else [
                "overall PCC performance breakthrough",
                "reuse of PCC v1 confirmation seeds for a redesigned study",
            ]
        ),
    }


def holm_adjust(p_values) -> np.ndarray:
    values = np.asarray(p_values, dtype=np.float64).reshape(-1)
    if not np.isfinite(values).all() or np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("p-values must be finite and in [0, 1]")
    if values.size == 0:
        return values.copy()
    order = np.argsort(values, kind="mergesort")
    adjusted_sorted = np.empty(values.size, dtype=np.float64)
    running = 0.0
    for rank, index in enumerate(order):
        candidate = min(1.0, (values.size - rank) * values[index])
        running = max(running, candidate)
        adjusted_sorted[rank] = running
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted


def _centered_hierarchical_p_values(
    differences: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> np.ndarray:
    values = _validated_differences(differences)
    observed = np.abs(values.mean(axis=(0, 1)))
    centered = values - values.mean(axis=(0, 1), keepdims=True)
    null_draws = hierarchical_bootstrap(centered, draws=draws, seed=seed)
    exceedances = (np.abs(null_draws) >= observed).sum(axis=0)
    return (exceedances + 1.0) / (int(draws) + 1.0)


def _secondary_comparisons(
    artifacts: dict[str, object],
    *,
    pcc_block: np.ndarray,
    model_seeds,
    rollout_seeds,
    draws: int,
    bootstrap_seed: int,
) -> list[dict[str, object]]:
    comparisons = []
    raw_p_values = []
    for comparison_index, policy in enumerate(sorted(artifacts["outcomes"])):
        if policy == "pcc_full":
            continue
        block = complete_policy_block(
            artifacts,
            policy=policy,
            model_seeds=model_seeds,
            rollout_seeds=rollout_seeds,
            allow_shared_model_block=policy in MODEL_INDEPENDENT_POLICIES,
        )
        differences = pcc_block - block
        p_values = _centered_hierarchical_p_values(
            differences,
            draws=draws,
            seed=int(bootstrap_seed) + 10000 + comparison_index,
        )
        for objective_index, objective in enumerate(OBJECTIVE_NAMES):
            comparisons.append(
                {
                    "policy": policy,
                    "objective": objective,
                    "mean_effect": float(differences[:, :, objective_index].mean()),
                    "raw_p_value": float(p_values[objective_index]),
                }
            )
            raw_p_values.append(float(p_values[objective_index]))
    adjusted = holm_adjust(raw_p_values)
    for row, value in zip(comparisons, adjusted):
        row["holm_adjusted_p_value"] = float(value)
    return comparisons


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--bishan-root", required=True)
    parser.add_argument("--dongxing-json", required=True)
    parser.add_argument("--draws", type=int, default=20000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260710)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
        validate_registry,
        verify_frozen_registry,
    )

    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    registry_digest = verify_frozen_registry(registry)
    selected = registry.get("selected_config", {})
    primary_comparator = str(selected.get("primary_comparator", ""))
    if primary_comparator not in registry["deployable_baselines"]:
        raise ValueError("frozen primary comparator is missing or undeclared")
    if primary_comparator in {"pcc_full", "pcc_matched"}:
        raise ValueError("PCC policy cannot be its own primary comparator")

    allowed = set(registry["deployable_baselines"])
    bishan = load_confirmation_artifacts(
        args.bishan_root,
        expected_registry_digest=registry_digest,
        allowed_policies=allowed,
        excluded_policies=set(registry.get("diagnostic_policies", [])),
    )
    dongxing = load_confirmation_artifacts(
        args.dongxing_json,
        expected_registry_digest=registry_digest,
        allowed_policies=allowed,
        excluded_policies=set(registry.get("diagnostic_policies", [])),
    )
    model_seeds = tuple(map(int, registry["model_seeds"]))
    bishan_seeds = tuple(map(int, registry["partitions"]["confirmation"]))
    dongxing_seeds = tuple(
        map(int, registry["partitions"]["dongxing_confirmation"])
    )
    frozen_pcc_digests = tuple(map(str, selected.get("checkpoint_digests", [])))
    if not frozen_pcc_digests:
        raise ValueError("frozen PCC checkpoint digests are missing")
    bishan_full_checkpoint_map = _verify_model_dependent_checkpoints(
        bishan,
        policy="pcc_full",
        model_seeds=model_seeds,
        expected_flat_digests=frozen_pcc_digests,
    )
    bishan_matched_checkpoint_map = _verify_model_dependent_checkpoints(
        bishan,
        policy="pcc_matched",
        model_seeds=model_seeds,
    )
    if bishan_matched_checkpoint_map != bishan_full_checkpoint_map:
        raise ValueError("pcc_full and pcc_matched checkpoint lineage mismatch")
    dongxing_full_checkpoint_map = _verify_model_dependent_checkpoints(
        dongxing,
        policy="pcc_full",
        model_seeds=model_seeds,
    )
    if primary_comparator in REFERENCE_CHECKPOINT_POLICIES:
        expected_reference = [
            registry["offline_reference_policy"]["checkpoint_sha256"]
        ]
        _verify_reference_policy_checkpoints(
            bishan,
            policy=primary_comparator,
            expected_digests=expected_reference,
        )
        _verify_reference_policy_checkpoints(
            dongxing,
            policy=primary_comparator,
            expected_digests=expected_reference,
        )
    else:
        bishan_comparator_checkpoint_map = _verify_model_dependent_checkpoints(
            bishan,
            policy=primary_comparator,
            model_seeds=model_seeds,
        )
        if bishan_comparator_checkpoint_map != bishan_full_checkpoint_map:
            raise ValueError("primary comparator checkpoint lineage mismatch")
        dongxing_comparator_checkpoint_map = _verify_model_dependent_checkpoints(
            dongxing,
            policy=primary_comparator,
            model_seeds=model_seeds,
        )
        if dongxing_comparator_checkpoint_map != dongxing_full_checkpoint_map:
            raise ValueError("Dongxing comparator checkpoint lineage mismatch")

    primary_block = complete_policy_block(
        bishan,
        policy="pcc_full",
        model_seeds=model_seeds,
        rollout_seeds=bishan_seeds,
        allow_shared_model_block=False,
    )
    matched_block = complete_policy_block(
        bishan,
        policy="pcc_matched",
        model_seeds=model_seeds,
        rollout_seeds=bishan_seeds,
        allow_shared_model_block=False,
    )
    comparator_block = complete_policy_block(
        bishan,
        policy=primary_comparator,
        model_seeds=model_seeds,
        rollout_seeds=bishan_seeds,
        allow_shared_model_block=primary_comparator in MODEL_INDEPENDENT_POLICIES,
    )
    dongxing_primary = complete_policy_block(
        dongxing,
        policy="pcc_full",
        model_seeds=model_seeds,
        rollout_seeds=dongxing_seeds,
        allow_shared_model_block=False,
    )
    dongxing_comparator = complete_policy_block(
        dongxing,
        policy=primary_comparator,
        model_seeds=model_seeds,
        rollout_seeds=dongxing_seeds,
        allow_shared_model_block=primary_comparator in MODEL_INDEPENDENT_POLICIES,
    )

    information_audit_passed = bool(
        bishan["information_audit_passed"]
        and dongxing["information_audit_passed"]
    )
    locked = evaluate_locked_confirmation(
        primary_block - comparator_block,
        matched_block - comparator_block,
        dongxing_primary - dongxing_comparator,
        information_audit_passed=information_audit_passed,
        bootstrap_seed=int(args.bootstrap_seed),
        draws=int(args.draws),
    )
    secondary = _secondary_comparisons(
        bishan,
        pcc_block=primary_block,
        model_seeds=model_seeds,
        rollout_seeds=bishan_seeds,
        draws=int(args.draws),
        bootstrap_seed=int(args.bootstrap_seed),
    )
    seed_rows = []
    seed_rows.extend(
        _seed_level_rows(
            region="bishan",
            policy="pcc_full",
            comparator=primary_comparator,
            policy_block=primary_block,
            comparator_block=comparator_block,
            model_seeds=model_seeds,
            rollout_seeds=bishan_seeds,
        )
    )
    seed_rows.extend(
        _seed_level_rows(
            region="bishan",
            policy="pcc_matched",
            comparator=primary_comparator,
            policy_block=matched_block,
            comparator_block=comparator_block,
            model_seeds=model_seeds,
            rollout_seeds=bishan_seeds,
        )
    )
    seed_rows.extend(
        _seed_level_rows(
            region="dongxing",
            policy="pcc_full",
            comparator=primary_comparator,
            policy_block=dongxing_primary,
            comparator_block=dongxing_comparator,
            model_seeds=model_seeds,
            rollout_seeds=dongxing_seeds,
        )
    )
    report = {
        "schema_version": 1,
        "protocol_id": registry["protocol_id"],
        "registry_digest": registry_digest,
        "primary_policy": "pcc_full",
        "matched_compute_policy": "pcc_matched",
        "primary_comparator": primary_comparator,
        "bootstrap_seed": int(args.bootstrap_seed),
        "bootstrap_draws": int(args.draws),
        "policy_checkpoint_digests": {
            "bishan": {
                policy: {
                    str(model_seed): list(digests)
                    for model_seed, digests in sorted(by_model.items())
                }
                for policy, by_model in sorted(
                    bishan["checkpoint_digests"].items()
                )
            },
            "dongxing": {
                policy: {
                    str(model_seed): list(digests)
                    for model_seed, digests in sorted(by_model.items())
                }
                for policy, by_model in sorted(
                    dongxing["checkpoint_digests"].items()
                )
            },
        },
        "locked_confirmation": locked,
        "manuscript_claim_gate": manuscript_claim_gate(
            {"locked_confirmation": locked}
        ),
        "secondary_comparisons_holm": secondary,
        "source_files": {
            "bishan": bishan["source_files"],
            "dongxing": dongxing["source_files"],
        },
    }
    _write_outputs(args.output_prefix, report=report, seed_rows=seed_rows)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
