import math
from itertools import product
from pathlib import Path

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import freeze_registry


GRID_KEYS = (
    "ensemble_size",
    "joint_coverage",
    "tolerance_scale",
    "planning_horizon",
    "residual_window",
    "policy_round",
)


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
    calibrator_digest: str,
    expert_learning_rate: float,
    compute_budget: int,
) -> dict[str, object]:
    if stage_a_report.get("passed") is not True:
        raise ValueError("Stage A must pass before protocol freeze")
    if str(primary_comparator) == "oracle_action_audit_diagnostic":
        raise ValueError("oracle diagnostic cannot be the primary comparator")
    checkpoint_digests = [str(value) for value in checkpoint_digests]
    if not checkpoint_digests or len(set(checkpoint_digests)) != len(
        checkpoint_digests
    ):
        raise ValueError("checkpoint digests must be complete and distinct")
    if not calibrator_digest:
        raise ValueError("calibrator digest is required")
    if not np.isfinite(expert_learning_rate) or float(expert_learning_rate) <= 0.0:
        raise ValueError("expert learning rate must be positive")
    if int(compute_budget) != 50:
        raise ValueError("PCC matched compute budget is locked to 50")

    selected = dict(select_configuration(development_rows))
    selected.update(
        {
            "primary_comparator": str(primary_comparator),
            "checkpoint_digests": checkpoint_digests,
            "calibrator_digest": str(calibrator_digest),
            "expert_learning_rate": float(expert_learning_rate),
            "compute_budget": int(compute_budget),
            "stage_a_report": dict(stage_a_report),
        }
    )
    return freeze_registry(registry_path, selected_config=selected)
