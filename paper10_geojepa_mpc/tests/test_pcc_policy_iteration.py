import json

import pytest

from paper10_geojepa_mpc.experiments.run_pcc_policy_iteration import (
    ROUND1_LABEL_POLICY_CONFIG,
    PolicyRound,
    build_policy_rounds,
    run_two_round_policy_iteration,
    verify_round_manifest,
    write_round_manifest,
)


def test_policy_iteration_has_exactly_two_improvement_rounds():
    rounds = build_policy_rounds(reference_policy="paper9_mpc")

    assert [row.round_index for row in rounds] == [0, 1, 2]
    assert rounds[0].label_policy == "paper9_mpc"
    assert rounds[1].label_policy == "pcc_round1"
    assert rounds[2].label_policy == "pcc_round2"


def test_third_improvement_round_is_forbidden():
    with pytest.raises(ValueError, match="exactly two"):
        PolicyRound(round_index=3, label_policy="pcc_round3", parent_digest="abc")


def test_round1_label_policy_is_predeclared_and_disables_online_feedback():
    assert ROUND1_LABEL_POLICY_CONFIG == {
        "ensemble_size": 3,
        "joint_coverage": 0.90,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "executed_feedback": False,
        "reference_policy": "paper9_mpc",
    }


def test_two_round_orchestration_uses_round_specific_calibration_labels():
    calls = []

    result = run_two_round_policy_iteration(
        rounds=2,
        round0_train_labels="round0_labels",
        round0_calibration_labels="round0_calibration_labels",
        round1_checkpoints="round1_checkpoints",
        validate_labels=lambda round_index, labels: calls.append(
            ("validate", round_index, labels)
        ),
        calibrate=lambda round_index, labels, checkpoints: calls.append(
            ("calibrate", round_index, labels)
        )
        or f"calibrator_{round_index}",
        generate_labels=lambda kind, round_index, policy, config: calls.append(
            (kind, round_index, policy)
        )
        or f"{kind}_{round_index}",
        train=lambda round_index, labels, parent: calls.append(
            ("train", round_index)
        )
        or "round2_checkpoints",
    )

    assert calls == [
        ("validate", 1, "round0_labels"),
        ("calibrate", 1, "round0_calibration_labels"),
        ("train_labels", 2, "pcc_round1"),
        ("calibration_labels", 2, "pcc_round1"),
        ("train", 2),
        ("calibrate", 2, "calibration_labels_2"),
    ]
    assert result["round2_calibrator"] == "calibrator_2"


def test_policy_iteration_rejects_any_round_count_other_than_two():
    with pytest.raises(ValueError, match="exactly two"):
        run_two_round_policy_iteration(
            rounds=3,
            round0_train_labels="labels",
            round0_calibration_labels="calibration",
            round1_checkpoints="checkpoints",
            validate_labels=lambda *_: None,
            calibrate=lambda *_: None,
            generate_labels=lambda *_: None,
            train=lambda *_: None,
        )


def test_round_manifest_digest_detects_lineage_mutation(tmp_path):
    path = tmp_path / "round.json"
    payload = write_round_manifest(
        path,
        round_index=2,
        parent_digest="parent",
        train_labels_digest="train",
        calibration_labels_digest="calibration",
        checkpoint_digests=["member0", "member1", "member2"],
        continuation_policy=ROUND1_LABEL_POLICY_CONFIG,
    )

    assert verify_round_manifest(json.loads(path.read_text(encoding="utf-8"))) == payload[
        "round_digest"
    ]
    payload["parent_digest"] = "changed"
    with pytest.raises(ValueError, match="digest mismatch"):
        verify_round_manifest(payload)
