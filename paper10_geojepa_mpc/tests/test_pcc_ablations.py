import numpy as np
import pytest
import torch

from paper10_geojepa_mpc.experiments.pcc_ablations import (
    ABLATION_CONTRACTS,
    apply_ablation,
    differing_paths,
    frozen_development_config,
    resolve_ablation_ensemble,
)
from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry
from paper10_geojepa_mpc.models.pcc_geojepa import PCCGeoJEPAMember
from paper10_geojepa_mpc.planning.pcc_baselines import PCCObservablePolicy
from paper10_geojepa_mpc.planning.pcc_selector import (
    calibrated_lower_bounds,
    choose_from_bounds,
    paired_ensemble_statistics,
)


@pytest.mark.parametrize("name", load_registry()["required_ablations"])
def test_ablation_changes_only_declared_fields(name):
    base = frozen_development_config()

    changed = apply_ablation(base, name)

    allowed = set(ABLATION_CONTRACTS[name].changed_fields)
    assert changed["ablation"] == name
    assert differing_paths(base, changed) == allowed | {"ablation"}
    assert "ablation" not in base


def test_ablation_contracts_exactly_match_the_locked_registry():
    assert set(ABLATION_CONTRACTS) == set(load_registry()["required_ablations"])


def test_single_model_ablation_uses_one_member_without_mutating_input():
    ensemble = [(object(), {"member_index": index}) for index in range(3)]

    selected = resolve_ablation_ensemble(ensemble, ensemble_size=1)

    assert selected == ensemble[:1]
    assert len(ensemble) == 3


def test_no_aleatoric_scale_retains_only_member_delta_variance():
    candidate_mean = np.array([[[3.0]], [[5.0]]])
    reference_mean = np.array([[1.0], [2.0]])

    statistics = paired_ensemble_statistics(
        candidate_mean,
        np.zeros_like(candidate_mean),
        reference_mean,
        np.zeros_like(reference_mean),
        use_aleatoric_scale=False,
    )

    np.testing.assert_allclose(statistics.epistemic_variance, [[0.5]])
    np.testing.assert_allclose(statistics.aleatoric_variance, [[0.0]])
    np.testing.assert_allclose(statistics.paired_scale, [[np.sqrt(0.5)]])


class _FixedCalibrator:
    q_joint = 7.0


def test_uncalibrated_ensemble_scale_uses_unit_not_joint_multiplier():
    mean = np.array([[5.0, 4.0, 3.0, 2.0]])
    scale = np.ones_like(mean)
    multiplier = np.full(4, 2.0)

    calibrated = calibrated_lower_bounds(
        mean,
        scale,
        calibrator=_FixedCalibrator(),
        online_multiplier=multiplier,
        use_conformal=True,
    )
    raw_scale = calibrated_lower_bounds(
        mean,
        scale,
        calibrator=_FixedCalibrator(),
        online_multiplier=multiplier,
        use_conformal=False,
    )

    np.testing.assert_allclose(calibrated, mean - 14.0)
    np.testing.assert_allclose(raw_scale, mean - 2.0)


def test_reward_only_ablation_does_not_apply_planning_gates():
    actions = np.array([4, 7])
    lower = np.array(
        [[2.0, -10.0, -10.0, -10.0], [1.0, 0.1, 0.1, 0.1]]
    )

    chosen, info = choose_from_bounds(
        actions,
        lower,
        np.ones(2),
        np.array([0.1, 0.2]),
        reference_action=9,
        tolerances=np.zeros(3),
        pareto_objectives=("reward",),
    )

    assert chosen == 4
    assert info["pareto_objectives"] == ["reward"]


def test_no_reference_fallback_selects_best_executable_failed_gate_candidate():
    actions = np.array([4, 7])
    lower = np.array(
        [[-2.0, 0.5, 0.5, 0.5], [-1.0, -0.5, 0.5, 0.5]]
    )

    chosen, info = choose_from_bounds(
        actions,
        lower,
        np.ones(2),
        np.array([0.2, 0.1]),
        reference_action=9,
        tolerances=np.zeros(3),
        reference_fallback=False,
    )

    assert chosen == 7
    assert info["fallback"] is False
    assert info["fallback_reason"] == "reference_fallback_disabled"


class _FeedbackSpy:
    def __init__(self):
        self.updates = []

    def update(self, *args):
        self.updates.append(args)


def _observable_policy(feedback, *, executed_feedback):
    return PCCObservablePolicy(
        ensemble=[],
        calibrator=object(),
        feedback_scaler=feedback,
        reference_policy=object(),
        proposal_rankers=[],
        candidate_budget=1,
        planning_horizon=3,
        tolerances=np.zeros(3),
        executable_threshold=0.95,
        executed_feedback=executed_feedback,
    )


def test_no_executed_feedback_ablation_does_not_update_scaler():
    feedback = _FeedbackSpy()
    policy = _observable_policy(feedback, executed_feedback=False)

    policy.observe(
        {
            "observed_outcome": np.ones(4),
            "predicted_mean": np.zeros(4),
            "base_scale": np.ones(4),
        }
    )

    assert feedback.updates == []


def test_feedback_enabled_updates_scaler_from_executed_transition():
    feedback = _FeedbackSpy()
    policy = _observable_policy(feedback, executed_feedback=True)

    policy.observe(
        {
            "observed_outcome": np.ones(4),
            "predicted_mean": np.zeros(4),
            "base_scale": np.ones(4),
        }
    )

    assert len(feedback.updates) == 1


def test_observable_policy_logs_and_forwards_explicit_mechanisms(monkeypatch):
    captured = {}

    def fake_select_action(**kwargs):
        captured.update(kwargs)
        return 2, {"unexecuted_real_reward_queries": 0}

    monkeypatch.setattr(
        "paper10_geojepa_mpc.planning.pcc_selector.pcc_select_action",
        fake_select_action,
    )

    class Reference:
        def select(self, state):
            return 0, {"policy": "reference"}

    policy = PCCObservablePolicy(
        ensemble=[object()],
        calibrator=object(),
        feedback_scaler=_FeedbackSpy(),
        reference_policy=Reference(),
        proposal_rankers=[lambda state: [2]],
        candidate_budget=3,
        planning_horizon=3,
        tolerances=np.zeros(3),
        executable_threshold=0.95,
        use_aleatoric_scale=False,
        use_conformal=False,
        pareto_objectives=("reward",),
        executed_feedback=False,
        reference_fallback=False,
    )

    action, info = policy.select(
        {
            "block_features": np.zeros((3, 2)),
            "neighbour_features": np.zeros((3, 2)),
            "global_features": np.zeros(2),
            "executable_mask": np.ones(3, dtype=bool),
        }
    )

    assert action == 2
    assert captured["use_aleatoric_scale"] is False
    assert captured["use_conformal"] is False
    assert captured["pareto_objectives"] == ("reward",)
    assert captured["reference_fallback"] is False
    assert info["executed_feedback"] is False


def test_county_specific_embedding_is_explicit_and_action_space_bound():
    model = PCCGeoJEPAMember(
        block_feature_dim=3,
        k_global=2,
        hidden_dim=8,
        representation="county_specific_action_embedding",
        county_action_count=4,
    )
    assert any("action_embedding" in name for name, _ in model.named_parameters())
    block = torch.zeros(1, 5, 3)
    neighbour = torch.zeros_like(block)
    global_features = torch.zeros(1, 2)

    with pytest.raises(ValueError, match="county action space"):
        model(block, neighbour, global_features, torch.tensor([4]))


def test_action_relative_representation_remains_default_and_unbounded_by_county():
    model = PCCGeoJEPAMember(block_feature_dim=3, k_global=2, hidden_dim=8)
    assert model.representation == "action_relative"
    assert all("action_embedding" not in name for name, _ in model.named_parameters())
