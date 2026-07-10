import json

import numpy as np
import pytest
import torch
import torch.nn as nn

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    write_label_manifest,
    write_trajectory_artifact,
)
from paper10_geojepa_mpc.models.pcc_geojepa import PCCModelOutput
from paper10_geojepa_mpc.planning.paired_conformal import (
    audit_joint_coverage,
    fit_calibrator_from_artifacts,
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


class _ExactDeltaMember(nn.Module):
    def forward(self, block, neighbour, global_features, actions):
        batch = actions.shape[0]
        mean = actions.float()[:, None, None].expand(batch, 3, 4).clone()
        zeros = torch.zeros_like(mean)
        return PCCModelOutput(
            next_block=block,
            next_global=global_features,
            immediate_mean=mean[:, 0],
            immediate_log_scale=zeros[:, 0],
            horizon_mean=mean,
            horizon_log_scale=zeros,
            executable_logit=torch.full((batch,), 10.0),
            latent=torch.zeros(batch, 2),
        )


def test_artifact_fitting_preserves_candidate_reference_and_trajectory_axes(tmp_path):
    labels = tmp_path / "labels"
    actions = np.asarray([[1, 2]], dtype=np.int64)
    objective = np.stack(
        [
            np.full((3, 4), 1.0, dtype=np.float32),
            np.full((3, 4), 2.0, dtype=np.float32),
        ],
        axis=0,
    )[None, ...]
    dataset = {
        "states_bf": np.zeros((1, 3, 2), dtype=np.float32),
        "states_neighbor_bf": np.zeros((1, 3, 2), dtype=np.float32),
        "states_gf": np.zeros((1, 2), dtype=np.float32),
        "actions": actions,
        "objective_returns": objective,
        "reference_actions": np.asarray([0], dtype=np.int64),
        "reference_objective_returns": np.zeros_like(objective),
        "trajectory_ids": np.asarray([2000], dtype=np.int64),
        "state_steps": np.asarray([0], dtype=np.int64),
        "horizons": np.asarray([1, 3, 5], dtype=np.int64),
    }
    artifact = write_trajectory_artifact(labels, 2000, dataset)
    manifest = write_label_manifest(
        labels,
        protocol_id="fixture",
        partition="calibration",
        artifacts=[artifact],
        continuation_policy={"name": "fixture"},
        horizons=(1, 3, 5),
    )
    scaling = {
        "center": np.zeros((3, 4)).tolist(),
        "scale": np.ones((3, 4)).tolist(),
    }
    ensemble = [(_ExactDeltaMember(), {"objective_scaling": scaling})]

    calibrator = fit_calibrator_from_artifacts(
        labels / "manifest.json",
        ensemble=ensemble,
        coverage=0.8,
        output_path=tmp_path / "calibrator.json",
        device="cpu",
        checkpoint_digests=["a" * 64],
    )

    assert calibrator.trajectory_ids.tolist() == [2000]
    assert calibrator.trajectory_scores.tolist() == [0.0]
    assert calibrator.q_joint == 0.0
    assert calibrator.labels_manifest_digest == manifest["manifest_digest"]
    assert calibrator.checkpoint_digests == ("a" * 64,)
    loaded = load_joint_calibrator(tmp_path / "calibrator.json")
    assert loaded.labels_manifest_digest == manifest["manifest_digest"]
    assert loaded.checkpoint_digests == ("a" * 64,)
