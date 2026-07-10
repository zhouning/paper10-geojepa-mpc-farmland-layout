import json

import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry
from paper10_geojepa_mpc.experiments.run_pcc_development import (
    binomial_acceptance_interval,
    enumerate_grid,
    freeze_development,
    select_configuration,
    stage_a_gate,
)


def test_grid_contains_only_registry_declared_values():
    registry = load_registry()

    rows = enumerate_grid(registry["grid"])

    assert len(rows) == 144
    assert {row["ensemble_size"] for row in rows} == {3, 5}


def test_selection_prioritizes_planning_gates_then_reward_then_compute():
    rows = [
        {"id": "reward_only", "planning_gate_count": 2, "reward": 5.0, "compute": 10},
        {"id": "safe_slow", "planning_gate_count": 3, "reward": 1.0, "compute": 20},
        {"id": "safe_fast", "planning_gate_count": 3, "reward": 1.0, "compute": 10},
    ]

    assert select_configuration(rows)["id"] == "safe_fast"


def test_stage_a_requires_positive_uncertainty_error_association_and_coverage():
    lower, upper = binomial_acceptance_interval(20, 0.9)
    covered = min(max(18, lower), upper)

    passing = stage_a_gate(
        uncertainty=np.arange(20, dtype=float),
        absolute_error=np.arange(20, dtype=float),
        covered_trajectories=covered,
        n_trajectories=20,
        nominal_coverage=0.9,
    )
    failing = stage_a_gate(
        uncertainty=np.arange(20, dtype=float),
        absolute_error=np.arange(20, 0, -1, dtype=float),
        covered_trajectories=covered,
        n_trajectories=20,
        nominal_coverage=0.9,
    )

    assert passing["passed"] is True
    assert failing["passed"] is False


def test_freeze_writes_selected_config_and_primary_comparator(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")
    row = {
        "id": "winner",
        "planning_gate_count": 3,
        "reward": 1.0,
        "compute": 48,
        "ensemble_size": 3,
        "joint_coverage": 0.9,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "residual_window": 10,
        "policy_round": 2,
    }

    frozen = freeze_development(
        path,
        development_rows=[row],
        stage_a_report={"passed": True},
        primary_comparator="distributional_risk",
        checkpoint_digests=["member0", "member1", "member2"],
        calibrator_digest="calibrator",
        expert_learning_rate=0.1,
        compute_budget=50,
    )

    assert frozen["status"] == "frozen"
    assert frozen["selected_config"]["id"] == "winner"
    assert frozen["selected_config"]["primary_comparator"] == "distributional_risk"


def test_freeze_rejects_failed_stage_a(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")

    with pytest.raises(ValueError, match="Stage A"):
        freeze_development(
            path,
            development_rows=[],
            stage_a_report={"passed": False},
            primary_comparator="paper9_mpc",
            checkpoint_digests=[],
            calibrator_digest="",
            expert_learning_rate=0.1,
            compute_budget=50,
        )
