import numpy as np
import torch
import torch.nn as nn

from paper10_geojepa_mpc.models.pcc_geojepa import PCCModelOutput
from paper10_geojepa_mpc.planning.executed_feedback import ExecutedFeedbackScaler
from paper10_geojepa_mpc.planning.paired_conformal import fit_joint_calibrator
from paper10_geojepa_mpc.planning.pcc_selector import (
    build_candidate_pool,
    choose_from_bounds,
    paired_ensemble_statistics,
    pcc_select_action,
    predict_paired_ensemble,
)


def test_reward_positive_planning_harmful_action_is_rejected():
    actions = np.array([4, 7])
    lower = np.array(
        [[2.0, -0.1, 0.2, 1.0], [1.0, 0.1, 0.1, 0.1]]
    )

    chosen, info = choose_from_bounds(
        actions,
        lower,
        np.ones(2),
        np.array([0.2, 0.1]),
        reference_action=9,
        tolerances=np.zeros(3),
    )

    assert chosen == 7
    assert info["admissible_actions"] == [7]


def test_no_admissible_action_falls_back_exactly_to_reference():
    chosen, info = choose_from_bounds(
        np.array([4]),
        np.array([[-1.0, 1.0, 1.0, 1.0]]),
        np.ones(1),
        np.array([0.2]),
        reference_action=9,
        tolerances=np.zeros(3),
    )

    assert chosen == 9
    assert info["fallback"] is True


def test_tie_breaking_prefers_minimum_planning_bound_then_uncertainty_then_action():
    actions = np.array([8, 5, 3])
    lower = np.array(
        [
            [2.0, 0.1, 0.2, 0.3],
            [2.0, 0.2, 0.2, 0.2],
            [2.0, 0.2, 0.2, 0.2],
        ]
    )

    chosen, _ = choose_from_bounds(
        actions,
        lower,
        np.ones(3),
        np.array([0.01, 0.2, 0.1]),
        reference_action=9,
        tolerances=np.zeros(3),
    )

    assert chosen == 3


def test_non_finite_predictions_fail_closed():
    chosen, info = choose_from_bounds(
        np.array([4]),
        np.array([[np.nan, 1.0, 1.0, 1.0]]),
        np.ones(1),
        np.array([0.2]),
        reference_action=9,
        tolerances=np.zeros(3),
    )

    assert chosen == 9
    assert info["fallback_reason"] == "non_finite_prediction"


def test_paired_scale_uses_member_delta_variance_and_both_aleatoric_terms():
    candidate_mean = np.array([[[3.0]], [[5.0]]])
    reference_mean = np.array([[1.0], [2.0]])
    candidate_log_scale = np.zeros_like(candidate_mean)
    reference_log_scale = np.zeros_like(reference_mean)

    statistics = paired_ensemble_statistics(
        candidate_mean,
        candidate_log_scale,
        reference_mean,
        reference_log_scale,
    )

    np.testing.assert_allclose(statistics.mean_delta, [[2.5]])
    np.testing.assert_allclose(statistics.epistemic_variance, [[0.5]])
    np.testing.assert_allclose(statistics.aleatoric_variance, [[2.0]])
    np.testing.assert_allclose(statistics.paired_scale, [[np.sqrt(2.5)]])


def test_candidate_pool_is_deduplicated_budgeted_and_keeps_reference():
    pool = build_candidate_pool(
        reference_action=9,
        proposal_groups=[[4, 7, 9], [7, 3, 2]],
        executable_mask=np.array(
            [False, False, True, True, True, False, False, True, False, True]
        ),
        candidate_budget=4,
    )

    assert pool.tolist() == [9, 4, 7, 3]


class _FakeMember(nn.Module):
    def __init__(self, member_offset: float):
        super().__init__()
        self.member_offset = float(member_offset)

    def forward(self, block, neighbour, global_features, actions):
        batch = actions.shape[0]
        normalized = actions.float()[:, None, None] + self.member_offset
        horizon_mean = normalized.expand(batch, 3, 4).clone()
        horizon_log_scale = torch.zeros_like(horizon_mean)
        immediate_mean = horizon_mean[:, 0]
        immediate_log_scale = torch.zeros_like(immediate_mean)
        return PCCModelOutput(
            next_block=block,
            next_global=global_features,
            immediate_mean=immediate_mean,
            immediate_log_scale=immediate_log_scale,
            horizon_mean=horizon_mean,
            horizon_log_scale=horizon_log_scale,
            executable_logit=torch.full((batch,), 10.0),
            latent=torch.zeros(batch, 2),
        )


def _fake_ensemble():
    scaling = {
        "center": np.zeros((3, 4)).tolist(),
        "scale": np.tile(np.array([2.0, 3.0, 4.0, 5.0]), (3, 1)).tolist(),
    }
    return [
        (_FakeMember(0.0), {"objective_scaling": scaling}),
        (_FakeMember(1.0), {"objective_scaling": scaling}),
    ]


def test_ensemble_prediction_denormalizes_and_reuses_reference_batch_row():
    prediction = predict_paired_ensemble(
        _fake_ensemble(),
        block_features=np.zeros((3, 2), dtype=np.float32),
        neighbour_features=np.zeros((3, 2), dtype=np.float32),
        global_features=np.zeros(2, dtype=np.float32),
        actions=np.array([0, 1, 2]),
        reference_action=0,
        planning_horizon=3,
        device="cpu",
    )

    np.testing.assert_allclose(prediction.mean_delta[1], [2.0, 3.0, 4.0, 5.0])
    np.testing.assert_allclose(
        prediction.paired_scale[1],
        np.sqrt(2.0) * np.array([2.0, 3.0, 4.0, 5.0]),
    )
    assert prediction.member_evaluations == 6
    assert prediction.model_forward_count == 2


def test_complete_selector_calls_reference_once_and_returns_feedback_prediction():
    calls = []
    target = np.zeros((3, 1, 4))
    calibrator = fit_joint_calibrator(
        target,
        target,
        np.ones_like(target),
        np.arange(3),
        coverage=0.8,
    )
    feedback = ExecutedFeedbackScaler(window=10, q_joint=calibrator.q_joint)

    action, info = pcc_select_action(
        ensemble=_fake_ensemble(),
        calibrator=calibrator,
        feedback_scaler=feedback,
        block_features=np.zeros((3, 2), dtype=np.float32),
        neighbour_features=np.zeros((3, 2), dtype=np.float32),
        global_features=np.zeros(2, dtype=np.float32),
        executable_mask=np.ones(3, dtype=bool),
        reference_policy=lambda: calls.append("reference") or 0,
        proposal_groups=[[2, 1]],
        candidate_budget=3,
        planning_horizon=3,
        tolerances=np.zeros(3),
        executable_threshold=0.95,
        device="cpu",
    )

    assert action == 2
    assert calls == ["reference"]
    assert info["reference_action"] == 0
    assert len(info["selected_predicted_mean"]) == 4
    assert len(info["selected_base_scale"]) == 4
    assert info["unexecuted_real_reward_queries"] == 0
