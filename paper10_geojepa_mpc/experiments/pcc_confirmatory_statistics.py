import numpy as np

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
