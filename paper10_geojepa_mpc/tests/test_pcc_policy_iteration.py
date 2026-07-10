import json

import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.run_pcc_policy_iteration import (
    ROUND1_LABEL_POLICY_CONFIG,
    PolicyRound,
    build_iteration_command_plan,
    build_policy_rounds,
    parse_args,
    run_two_round_policy_iteration,
    verify_policy_iteration_root,
    verify_round_manifest,
    write_round_manifest,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry
from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.planning.paired_conformal import (
    JointPairedCalibrator,
    save_joint_calibrator,
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
        model_seed=5101,
        round_index=2,
        parent_digest="parent",
        train_labels_digest="train",
        calibration_labels_digest="calibration",
        checkpoint_digests=["member0", "member1", "member2"],
        calibrator_digest="calibrator",
        continuation_policy=ROUND1_LABEL_POLICY_CONFIG,
    )

    assert verify_round_manifest(json.loads(path.read_text(encoding="utf-8"))) == payload[
        "round_digest"
    ]
    payload["parent_digest"] = "changed"
    with pytest.raises(ValueError, match="digest mismatch"):
        verify_round_manifest(payload)


def test_policy_iteration_parser_accepts_declared_execution_command(tmp_path):
    args = parse_args(
        [
            "--registry",
            "registry.json",
            "--round0-train-labels",
            "train.json",
            "--round0-calibration-labels",
            "calibration.json",
            "--round1-checkpoints",
            "checkpoints",
            "--round1-iteration-ensemble-size",
            "3",
            "--round1-iteration-coverage",
            "0.9",
            "--round1-iteration-tolerance-scale",
            "0.05",
            "--round1-iteration-horizon",
            "3",
            "--rounds",
            "2",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert args.rounds == 2
    assert args.round1_iteration_ensemble_size == 3


def test_iteration_command_plan_carries_model_seed_lineage(tmp_path):
    args = parse_args(
        [
            "--registry",
            "registry.json",
            "--round0-train-labels",
            "train.json",
            "--round0-calibration-labels",
            "calibration.json",
            "--round1-checkpoints",
            "checkpoints",
            "--rounds",
            "2",
            "--output-dir",
            str(tmp_path),
        ]
    )

    plan = build_iteration_command_plan(
        args,
        model_seed=5101,
        round1_checkpoint_root=tmp_path / "round1_checkpoints",
    )

    assert set(plan) == {
        "round1_calibration",
        "round2_train_labels",
        "round2_calibration_labels",
        "round2_training",
        "round2_calibration",
    }
    label_command = plan["round2_train_labels"]
    assert label_command[label_command.index("--policy") + 1] == "pcc"
    assert label_command[label_command.index("--pcc-model-seed") + 1] == "5101"
    assert "paper10_geojepa_mpc.experiments.run_pcc_train" in plan[
        "round2_training"
    ]


def test_verify_only_requires_complete_three_seed_two_round_lineage(tmp_path):
    registry = load_registry()
    calibration_seeds = registry["partitions"]["calibration"]
    for model_seed in registry["model_seeds"]:
        seed_root = tmp_path / f"seed_{model_seed}"
        parent = registry["offline_reference_policy"]["checkpoint_sha256"]
        for round_index in (1, 2):
            round_root = seed_root / f"round{round_index}"
            calibration_digest = f"cal-{model_seed}-{round_index}"
            checkpoint_digests = [
                f"{model_seed}-{round_index}-member-{index}"
                for index in range(3)
            ]
            calibrator = JointPairedCalibrator(
                coverage=0.9,
                q_joint=1.0,
                trajectory_ids=np.asarray(calibration_seeds),
                trajectory_scores=np.ones(len(calibration_seeds)),
                objective_names=OBJECTIVE_NAMES,
                calibration_seeds=tuple(calibration_seeds),
                labels_manifest_digest=calibration_digest,
                checkpoint_digests=tuple(checkpoint_digests),
            )
            calibrator_payload = save_joint_calibrator(
                round_root / "calibration" / "calibrator.json",
                calibrator,
            )
            manifest = write_round_manifest(
                round_root / "round_manifest.json",
                model_seed=model_seed,
                round_index=round_index,
                parent_digest=parent,
                train_labels_digest=f"train-{model_seed}-{round_index}",
                calibration_labels_digest=calibration_digest,
                checkpoint_digests=checkpoint_digests,
                calibrator_digest=calibrator_payload["calibrator_digest"],
                continuation_policy={
                    "name": "paper9_mpc" if round_index == 1 else "pcc_round1",
                    "model_seed": model_seed,
                },
            )
            parent = manifest["round_digest"]

    report = verify_policy_iteration_root(tmp_path, registry=registry)

    assert report["passed"] is True
    assert report["model_seeds"] == registry["model_seeds"]
    assert len(report["rounds"]) == 6
