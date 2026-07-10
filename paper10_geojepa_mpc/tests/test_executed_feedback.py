import numpy as np
import pytest

from paper10_geojepa_mpc.planning.executed_feedback import ExecutedFeedbackScaler


def test_scaler_never_shrinks_offline_intervals():
    scaler = ExecutedFeedbackScaler(window=3, q_joint=2.0)
    scaler.update(np.zeros(4), np.ones(4), np.full(4, 0.5))

    assert np.all(scaler.multiplier() >= 1.0)


def test_scaler_widens_and_clips_after_large_executed_error():
    scaler = ExecutedFeedbackScaler(window=2, q_joint=1.0)
    scaler.update(np.full(4, 100.0), np.zeros(4), np.ones(4))

    assert scaler.multiplier().tolist() == [3.0, 3.0, 3.0, 3.0]


def test_scaler_uses_componentwise_executed_prediction_error():
    scaler = ExecutedFeedbackScaler(window=2, q_joint=2.0)
    scaler.update(
        observed=np.array([2.0, 0.0, 0.0, 0.0]),
        predicted=np.zeros(4),
        base_scale=np.array([0.5, 1.0, 1.0, 1.0]),
    )

    np.testing.assert_allclose(scaler.multiplier(), [2.0, 1.0, 1.0, 1.0])


def test_non_finite_executed_feedback_is_rejected():
    scaler = ExecutedFeedbackScaler(window=2, q_joint=1.0)

    with pytest.raises(ValueError, match="finite"):
        scaler.update(np.array([np.nan, 0.0, 0.0, 0.0]), np.zeros(4), np.ones(4))


def test_scaler_state_round_trip_preserves_window():
    scaler = ExecutedFeedbackScaler(window=2, q_joint=2.0)
    scaler.update(np.array([2.0, 1.0, 0.0, 0.0]), np.zeros(4), np.ones(4))

    restored = ExecutedFeedbackScaler.from_state_dict(scaler.state_dict())

    np.testing.assert_allclose(restored.multiplier(), scaler.multiplier())
