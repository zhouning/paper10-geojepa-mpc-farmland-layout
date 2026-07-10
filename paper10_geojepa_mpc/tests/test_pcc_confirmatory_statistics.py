import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_confirmatory_statistics import (
    evaluate_locked_confirmation,
    evaluate_success,
    hierarchical_bootstrap,
)


def test_reward_gain_cannot_pass_when_one_planning_gate_fails():
    differences = np.ones((3, 20, 4), dtype=float)
    differences[:, :, 3] = -1.0

    report = evaluate_success(differences, bootstrap_seed=20260710, draws=2000)

    assert report["reward_superiority"] is True
    assert report["planning_noninferiority"]["connected_area_benefit"] is False
    assert report["primary_success"] is False


def test_pairing_is_preserved_within_training_seed():
    differences = np.zeros((3, 20, 4), dtype=float)
    differences[:, :, 0] = np.arange(20)

    bootstrap = hierarchical_bootstrap(differences, draws=100, seed=4)
    report = evaluate_success(differences, bootstrap_seed=4, draws=100)

    assert bootstrap.shape == (100, 4)
    assert report["n_training_seeds"] == 3
    assert report["n_rollout_seeds"] == 20


def test_primary_success_requires_two_jointly_supporting_training_seeds():
    differences = np.ones((3, 20, 4), dtype=float)
    differences[2] = -0.1

    report = evaluate_success(differences, bootstrap_seed=9, draws=2000)

    assert report["training_seed_joint_support"] == 2
    assert report["primary_success"] is True


def test_locked_confirmation_requires_matched_external_and_information_gates():
    primary = np.ones((3, 20, 4), dtype=float)
    matched = np.ones((3, 20, 4), dtype=float)
    dongxing = np.zeros((3, 20, 4), dtype=float)

    passing = evaluate_locked_confirmation(
        primary,
        matched,
        dongxing,
        information_audit_passed=True,
        bootstrap_seed=7,
        draws=1000,
    )
    failing = evaluate_locked_confirmation(
        primary,
        matched,
        dongxing,
        information_audit_passed=False,
        bootstrap_seed=7,
        draws=1000,
    )

    assert passing["overall_success"] is True
    assert failing["overall_success"] is False


def test_locked_confirmation_rejects_incomplete_seed_blocks():
    with pytest.raises(ValueError, match="3 x 20"):
        evaluate_locked_confirmation(
            np.ones((3, 19, 4)),
            np.ones((3, 20, 4)),
            np.ones((3, 20, 4)),
            information_audit_passed=True,
            bootstrap_seed=7,
            draws=100,
        )
