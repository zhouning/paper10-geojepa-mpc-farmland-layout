import json

import numpy as np
import pytest

from paper10_geojepa_mpc.planning.paired_conformal import (
    audit_joint_coverage,
    fit_joint_calibrator,
    load_joint_calibrator,
    save_joint_calibrator,
)


def test_joint_score_uses_maximum_across_rows_horizons_and_objectives():
    target = np.zeros((4, 2, 4))
    predicted = np.zeros_like(target)
    scale = np.ones_like(target)
    target[1, 1, 3] = 2.0
    trajectory = np.array([10, 10, 11, 11])

    calibrator = fit_joint_calibrator(
        target,
        predicted,
        scale,
        trajectory,
        coverage=0.5,
    )

    assert calibrator.trajectory_ids.tolist() == [10, 11]
    assert calibrator.trajectory_scores.tolist() == [2.0, 0.0]
    assert calibrator.q_joint == 2.0


def test_lower_bounds_share_one_joint_multiplier():
    target = np.zeros((3, 1, 4))
    calibrator = fit_joint_calibrator(
        target,
        target,
        np.ones_like(target),
        np.arange(3),
        coverage=0.8,
    )

    lower = calibrator.lower_bounds(np.ones(4), np.full(4, 0.5))

    np.testing.assert_allclose(
        lower,
        np.ones(4) - calibrator.q_joint * 0.5,
    )


def test_calibration_rejects_shape_mismatch_and_nonpositive_scale():
    target = np.zeros((3, 1, 4))
    with pytest.raises(ValueError, match="shape"):
        fit_joint_calibrator(
            target,
            target[:, :, :3],
            np.ones_like(target),
            np.arange(3),
            coverage=0.8,
        )
    with pytest.raises(ValueError, match="scale"):
        fit_joint_calibrator(
            target,
            target,
            np.zeros_like(target),
            np.arange(3),
            coverage=0.8,
        )


def test_coverage_audit_counts_complete_trajectories_not_rows():
    target = np.zeros((4, 1, 4))
    predicted = np.zeros_like(target)
    scale = np.ones_like(target)
    trajectory = np.array([10, 10, 11, 11])
    calibrator = fit_joint_calibrator(
        target,
        predicted,
        scale,
        trajectory,
        coverage=0.5,
    )
    target[1, 0, 0] = calibrator.q_joint + 1.0

    audit = audit_joint_coverage(
        calibrator,
        target,
        predicted,
        scale,
        trajectory,
    )

    assert audit["n_trajectories"] == 2
    assert audit["covered_trajectories"] == 1
    assert audit["joint_coverage"] == 0.5


def test_serialized_calibrator_digest_detects_mutation(tmp_path):
    target = np.zeros((3, 1, 4))
    calibrator = fit_joint_calibrator(
        target,
        target,
        np.ones_like(target),
        np.arange(3),
        coverage=0.8,
        protocol_id="pcc_v1",
        calibration_seeds=[2000, 2001, 2002],
    )
    path = tmp_path / "calibrator.json"
    saved = save_joint_calibrator(path, calibrator)

    loaded = load_joint_calibrator(path)
    assert loaded.q_joint == calibrator.q_joint
    saved["q_joint"] += 1.0
    path.write_text(json.dumps(saved), encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        load_joint_calibrator(path)
