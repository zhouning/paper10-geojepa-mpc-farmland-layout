from dataclasses import dataclass

import numpy as np
import pytest
import torch
import torch.nn as nn

from paper10_geojepa_mpc.models.pcc_paired_delta import PairedDeltaOutput
from paper10_geojepa_mpc.models.pcc_paired_delta import PCCPairedDeltaMember
from paper10_geojepa_mpc.planning import pcc_v1_1_selector as selector


def test_direct_paired_statistics_use_direct_aleatoric_scale():
    means = np.array(
        [
            [[[1.0, 0.0, 0.0, 0.0]]],
            [[[3.0, 0.0, 0.0, 0.0]]],
        ]
    )
    log_scales = np.log(np.full_like(means, 2.0))

    statistics = selector.direct_paired_statistics(means, log_scales)

    np.testing.assert_allclose(statistics.mean_delta[..., 0], 2.0)
    np.testing.assert_allclose(
        statistics.paired_scale[..., 0],
        np.sqrt(np.var([1.0, 3.0], ddof=1) + 4.0),
    )
    np.testing.assert_allclose(statistics.aleatoric_variance[..., 0], 4.0)


def test_base_selector_optimizes_reward_mean_without_reward_lcb():
    actions = np.array([10, 20, 30])
    means = np.array(
        [
            [0.2, 0.0, 0.0, 0.0],
            [0.7, 0.1, 0.1, 0.1],
            [1.0, -0.2, 0.1, 0.1],
        ]
    )
    scales = np.ones_like(means)
    scales[1, 0] = 100.0

    selected, info = selector.choose_base_candidate(
        actions,
        means,
        scales=scales,
        executable_probability=np.ones(3),
        tolerances=np.zeros(3),
        executable_threshold=0.95,
    )

    assert selected == 20
    assert info["base_selection_reason"] == "reward_mean_among_mean_safe"
    assert info["mean_safe_actions"] == [10, 20]


def test_base_selector_keeps_reference_when_all_safe_rewards_are_negative():
    selected, info = selector.choose_base_candidate(
        np.array([10, 20]),
        np.array(
            [
                [-0.2, 0.1, 0.1, 0.1],
                [-0.1, 0.2, 0.2, 0.2],
            ]
        ),
        scales=np.ones((2, 4)),
        executable_probability=np.ones(2),
        tolerances=np.zeros(3),
        executable_threshold=0.95,
    )

    assert selected is None
    assert info["base_selection_reason"] == "reference_reward_dominates"
    assert info["mean_safe_actions"] == [10, 20]


@pytest.mark.parametrize(
    ("probability", "planning", "expected_reason"),
    [
        (0.2, [0.0, 0.0, 0.0], "no_executable_alternative"),
        (1.0, [-0.1, 0.0, 0.0], "no_mean_safe_candidate"),
    ],
)
def test_base_selector_has_stable_empty_reasons(
    probability,
    planning,
    expected_reason,
):
    selected, info = selector.choose_base_candidate(
        np.array([4]),
        np.array([[1.0, *planning]]),
        scales=np.ones((1, 4)),
        executable_probability=np.array([probability]),
        tolerances=np.zeros(3),
        executable_threshold=0.95,
    )

    assert selected is None
    assert info["base_selection_reason"] == expected_reason


def test_candidate_budget_and_pool_are_stable_and_exclude_reference():
    mask = np.array(
        [False, False, True, True, True, False, False, True, False, True]
    )

    matched = selector.build_v1_1_candidate_pool(
        reference_action=9,
        proposal_groups=[[4, 7, 9], [7, 3, 2]],
        executable_mask=mask,
        compute_mode="matched",
        ensemble_size=12,
    )
    full = selector.build_v1_1_candidate_pool(
        reference_action=9,
        proposal_groups=[[4, 7, 9], [7, 3, 2]],
        executable_mask=mask,
        compute_mode="full",
        ensemble_size=12,
    )

    assert selector.candidate_budget(compute_mode="matched", ensemble_size=3) == 16
    assert selector.candidate_budget(compute_mode="full", ensemble_size=3) == 50
    assert matched.tolist() == [4, 7, 3, 2]
    assert full.tolist() == [4, 7, 3, 2]
    assert 9 not in matched


class _FakePairedMember(nn.Module):
    def __init__(self, member_offset: float):
        super().__init__()
        self.member_offset = float(member_offset)

    def forward(
        self,
        block,
        neighbour,
        global_features,
        candidate_actions,
        reference_actions,
    ):
        assert torch.all(reference_actions == 0)
        batch = candidate_actions.shape[0]
        normalized = (
            candidate_actions.float()[:, None, None] + self.member_offset
        )
        delta_mean = normalized.expand(batch, 3, 4).clone()
        delta_log_scale = torch.zeros_like(delta_mean)
        absolute_mean = (
            candidate_actions.float()[:, None] + self.member_offset
        ).expand(batch, 4).clone()
        return PairedDeltaOutput(
            delta_mean=delta_mean,
            delta_log_scale=delta_log_scale,
            candidate_absolute_mean=absolute_mean,
            candidate_absolute_log_scale=torch.zeros_like(absolute_mean),
            executable_logit=torch.full((batch,), 10.0),
            candidate_latent=torch.zeros(batch, 2),
            reference_latent=torch.zeros(batch, 2),
        )


def _fake_direct_ensemble():
    delta_scale = np.tile(np.array([2.0, 3.0, 4.0, 5.0]), (3, 1))
    checkpoint = {
        "delta_scaling": {
            "center": np.zeros((3, 4)).tolist(),
            "scale": delta_scale.tolist(),
        },
        "absolute_scaling": {
            "center": [100.0, 200.0, 300.0, 400.0],
            "scale": [10.0, 20.0, 30.0, 40.0],
        },
    }
    return [
        (_FakePairedMember(0.0), checkpoint),
        (_FakePairedMember(1.0), checkpoint),
    ]


def test_direct_ensemble_prediction_denormalizes_before_statistics():
    prediction = selector.predict_direct_paired_ensemble(
        _fake_direct_ensemble(),
        block_features=np.zeros((3, 2), dtype=np.float32),
        neighbour_features=np.zeros((3, 2), dtype=np.float32),
        global_features=np.zeros(2, dtype=np.float32),
        actions=np.array([1, 2]),
        reference_action=0,
        compute_mode="matched",
        device="cpu",
    )

    objective_scale = np.array([2.0, 3.0, 4.0, 5.0])
    np.testing.assert_allclose(
        prediction.mean_delta[0],
        np.tile(1.5 * objective_scale, (3, 1)),
    )
    np.testing.assert_allclose(
        prediction.paired_scale[0],
        np.tile(np.sqrt(1.5) * objective_scale, (3, 1)),
    )
    np.testing.assert_allclose(
        prediction.candidate_absolute_mean[0],
        [115.0, 230.0, 345.0, 460.0],
    )
    assert prediction.reference_action == 0
    assert prediction.compute_mode == "matched"
    assert prediction.member_evaluations == 4
    assert prediction.model_forward_count == 2


def test_direct_ensemble_rejects_inconsistent_member_scaling():
    ensemble = _fake_direct_ensemble()
    changed = {
        **ensemble[1][1],
        "delta_scaling": {
            **ensemble[1][1]["delta_scaling"],
            "center": np.ones((3, 4)).tolist(),
        },
    }
    ensemble[1] = (ensemble[1][0], changed)

    with pytest.raises(ValueError, match="inconsistent delta_scaling"):
        selector.predict_direct_paired_ensemble(
            ensemble,
            block_features=np.zeros((3, 2), dtype=np.float32),
            neighbour_features=np.zeros((3, 2), dtype=np.float32),
            global_features=np.zeros(2, dtype=np.float32),
            actions=np.array([1, 2]),
            reference_action=0,
            compute_mode="matched",
            device="cpu",
        )


@dataclass(frozen=True)
class _Calibrator:
    q_planning: float
    coverage: float
    planning_horizon: int = 3


def _fixed_prediction():
    means = np.zeros((2, 3, 4), dtype=np.float64)
    means[0, :, :] = [0.2, 0.0, 0.0, 0.0]
    means[1, :, :] = [0.7, 2.0, 2.0, 2.0]
    return selector.DirectEnsemblePrediction(
        actions=np.array([10, 20]),
        reference_action=0,
        mean_delta=means,
        paired_scale=np.ones_like(means),
        executable_probability=np.ones(2),
        candidate_absolute_mean=np.zeros((2, 4)),
        candidate_absolute_scale=np.ones((2, 4)),
        compute_mode="matched",
        member_evaluations=6,
        model_forward_count=3,
    )


def test_coverage_changes_certificate_but_never_base_candidate():
    prediction = _fixed_prediction()

    loose_action, loose_info = selector.select_with_certificate(
        prediction,
        _Calibrator(q_planning=0.5, coverage=0.8),
    )
    strict_action, strict_info = selector.select_with_certificate(
        prediction,
        _Calibrator(q_planning=4.0, coverage=0.95),
    )

    assert loose_info["base_selected_action"] == 20
    assert strict_info["base_selected_action"] == 20
    assert loose_action == 20
    assert loose_info["decision_reason"] == "selected_candidate"
    assert strict_action == prediction.reference_action
    assert strict_info["decision_reason"] == "planning_certificate_rejected"


def test_certificate_uses_planning_objectives_only():
    prediction = _fixed_prediction()
    scales = prediction.paired_scale.copy()
    scales[1, :, 0] = 1_000.0
    scales[1, :, 1:] = 0.1
    prediction = selector.DirectEnsemblePrediction(
        **{**prediction.__dict__, "paired_scale": scales}
    )

    action, info = selector.select_with_certificate(
        prediction,
        _Calibrator(q_planning=4.0, coverage=0.95),
    )

    assert action == 20
    np.testing.assert_allclose(info["planning_lower_bounds"], [1.6, 1.6, 1.6])


def test_complete_selector_logs_empty_alternative_fallback():
    calls = []

    action, info = selector.pcc_v1_1_select_action(
        ensemble=_fake_direct_ensemble(),
        calibrator=_Calibrator(q_planning=0.5, coverage=0.8),
        block_features=np.zeros((3, 2), dtype=np.float32),
        neighbour_features=np.zeros((3, 2), dtype=np.float32),
        global_features=np.zeros(2, dtype=np.float32),
        executable_mask=np.array([True, False, False]),
        reference_policy=lambda: calls.append("reference") or 0,
        proposal_groups=[[]],
        compute_mode="matched",
        tolerances=np.zeros(3),
        executable_threshold=0.95,
        device="cpu",
    )

    assert calls == ["reference"]
    assert action == 0
    assert info["decision_reason"] == "no_executable_alternative"
    assert info["candidate_count"] == 0
    assert info["member_evaluations"] == 0
    assert info["model_forward_count"] == 0
    assert info["planning_lower_bounds"] == [None, None, None]
    assert info["unexecuted_real_reward_queries"] == 0


def test_complete_selector_fails_closed_with_v1_1_reason_prefix():
    ensemble = _fake_direct_ensemble()
    ensemble[1] = (
        ensemble[1][0],
        {
            **ensemble[1][1],
            "absolute_scaling": {
                "center": [0.0, 0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0, 1.0],
            },
        },
    )

    action, info = selector.pcc_v1_1_select_action(
        ensemble=ensemble,
        calibrator=_Calibrator(q_planning=0.5, coverage=0.8),
        block_features=np.zeros((3, 2), dtype=np.float32),
        neighbour_features=np.zeros((3, 2), dtype=np.float32),
        global_features=np.zeros(2, dtype=np.float32),
        executable_mask=np.array([True, True, True]),
        reference_policy=lambda: 0,
        proposal_groups=[[2, 1]],
        compute_mode="matched",
        tolerances=np.zeros(3),
        executable_threshold=0.95,
        device="cpu",
    )

    assert action == 0
    assert info["decision_reason"].startswith("invalid_pcc_v1_1_state:")
    assert info["reference_action"] == 0
    assert info["candidate_count"] == 2
    assert info["unexecuted_real_reward_queries"] == 0


def _write_member_checkpoint(
    path,
    *,
    member_index: int,
    ensemble_size: int,
    transfer_digest: str = "c" * 64,
):
    model = PCCPairedDeltaMember(2, 2, hidden_dim=8)
    torch.save(
        {
            "model_class": "PCCPairedDeltaMember",
            "protocol_id": "pcc_v1_1",
            "source_protocol_id": "pcc_v1",
            "registry_digest": "a" * 64,
            "source_manifest_digest": "b" * 64,
            "transfer_checkpoint_sha256": transfer_digest,
            "model_seed": 5101,
            "ensemble_size": ensemble_size,
            "member_index": member_index,
            "model_kwargs": model.model_kwargs(),
            "objective_names": [
                "reward",
                "slope_benefit",
                "contiguity_benefit",
                "connected_area_benefit",
            ],
            "horizons": [1, 3, 5],
            "delta_scaling": {
                "center": np.zeros((3, 4)).tolist(),
                "scale": np.ones((3, 4)).tolist(),
            },
            "absolute_scaling": {
                "center": np.zeros(4).tolist(),
                "scale": np.ones(4).tolist(),
            },
            "state_dict": model.state_dict(),
        },
        path,
    )


def test_load_direct_ensemble_requires_complete_member_inventory(tmp_path):
    _write_member_checkpoint(
        tmp_path / "member_0.pt",
        member_index=0,
        ensemble_size=2,
    )
    _write_member_checkpoint(
        tmp_path / "member_1.pt",
        member_index=1,
        ensemble_size=2,
    )

    ensemble = selector.load_pcc_v1_1_ensemble(tmp_path)

    assert [row[1]["member_index"] for row in ensemble] == [0, 1]
    (tmp_path / "member_1.pt").unlink()
    with pytest.raises(ValueError, match="incomplete"):
        selector.load_pcc_v1_1_ensemble(tmp_path)


def test_load_direct_ensemble_rejects_mixed_internal_lineage(tmp_path):
    _write_member_checkpoint(
        tmp_path / "member_0.pt",
        member_index=0,
        ensemble_size=2,
    )
    _write_member_checkpoint(
        tmp_path / "member_1.pt",
        member_index=1,
        ensemble_size=2,
        transfer_digest="d" * 64,
    )

    with pytest.raises(ValueError, match="lineage"):
        selector.load_pcc_v1_1_ensemble(tmp_path)
