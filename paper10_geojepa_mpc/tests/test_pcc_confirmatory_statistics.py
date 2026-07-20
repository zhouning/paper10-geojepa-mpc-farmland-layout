import json

import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_confirmatory_statistics import (
    _verify_model_dependent_checkpoints,
    complete_policy_block,
    evaluate_locked_confirmation,
    evaluate_success,
    hierarchical_bootstrap,
    holm_adjust,
    load_confirmation_artifacts,
    main,
    manuscript_claim_gate,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
)


def _rollout_payload(
    registry_digest,
    policy,
    model_seed,
    rollout_seeds,
    outcome,
    checkpoint_digests,
):
    return {
        "schema_version": 1,
        "registry_digest": registry_digest,
        "checkpoint_digests": list(checkpoint_digests),
        "seed_results": [
            {
                "seed": int(seed),
                "policy": policy,
                "model_seed": int(model_seed),
                "registry_digest": registry_digest,
                "checkpoint_digests": list(checkpoint_digests),
                "objective_outcome": list(outcome),
                "environment_step_count": 1,
                "steps": [{"unexecuted_real_reward_queries": 0}],
            }
            for seed in rollout_seeds
        ],
    }


def _write_payload(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _frozen_registry(tmp_path):
    registry_path = tmp_path / "pcc_v1.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    frozen = freeze_registry(
        registry_path,
        selected_config={
            "primary_comparator": "paper9_mpc",
            "checkpoint_digests": ["a" * 64, "b" * 64, "c" * 64],
        },
    )
    return registry_path, frozen


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


def test_failed_confirmation_emits_exact_failed_gate_without_retuning():
    primary = np.ones((3, 20, 4), dtype=float)
    primary[:, :, 3] = -1.0
    matched = np.ones((3, 20, 4), dtype=float)
    dongxing = np.zeros((3, 20, 4), dtype=float)
    locked = evaluate_locked_confirmation(
        primary,
        matched,
        dongxing,
        information_audit_passed=True,
        bootstrap_seed=7,
        draws=1000,
    )

    claim = manuscript_claim_gate({"locked_confirmation": locked})

    assert claim["primary_success"] is False
    assert claim["failed_gates"] == ["bishan.connected_area_benefit"]
    assert "retun" not in json.dumps(claim).lower()
    assert claim["allow_performance_breakthrough_claim"] is False


def test_holm_adjustment_is_monotone_in_sorted_p_values():
    adjusted = holm_adjust([0.01, 0.04, 0.03])

    np.testing.assert_allclose(adjusted, [0.03, 0.06, 0.06])


def test_artifact_loader_rejects_duplicate_policy_model_rollout_rows(tmp_path):
    _, frozen = _frozen_registry(tmp_path)
    payload = _rollout_payload(
        frozen["frozen_digest"],
        "pcc_full",
        5101,
        [4000],
        [1.0, 1.0, 1.0, 1.0],
        frozen["selected_config"]["checkpoint_digests"],
    )
    root = tmp_path / "confirmation"
    _write_payload(root / "first.json", payload)
    _write_payload(root / "second.json", payload)

    with pytest.raises(ValueError, match="duplicate"):
        load_confirmation_artifacts(
            root,
            expected_registry_digest=frozen["frozen_digest"],
            allowed_policies=set(frozen["deployable_baselines"]),
        )


def test_artifact_loader_explicitly_excludes_oracle_diagnostic(tmp_path):
    _, frozen = _frozen_registry(tmp_path)
    root = tmp_path / "confirmation"
    _write_payload(
        root / "paper9.json",
        _rollout_payload(
            frozen["frozen_digest"],
            "paper9_mpc",
            5101,
            [4000],
            [0.0, 0.0, 0.0, 0.0],
            [frozen["offline_reference_policy"]["checkpoint_sha256"]],
        ),
    )
    _write_payload(
        root / "oracle.json",
        _rollout_payload(
            frozen["frozen_digest"],
            "oracle_action_audit_diagnostic",
            5101,
            [4000],
            [10.0, 10.0, 10.0, 10.0],
            [frozen["offline_reference_policy"]["checkpoint_sha256"]],
        ),
    )

    artifacts = load_confirmation_artifacts(
        root,
        expected_registry_digest=frozen["frozen_digest"],
        allowed_policies=set(frozen["deployable_baselines"]),
        excluded_policies=set(frozen["diagnostic_policies"]),
    )

    assert set(artifacts["outcomes"]) == {"paper9_mpc"}


def test_model_dependent_checkpoint_verification_rejects_pseudoreplication():
    repeated = ("a" * 64,)
    artifacts = {
        "checkpoint_digests": {
            "pcc_full": {5101: repeated, 5102: repeated, 5103: repeated}
        }
    }

    with pytest.raises(ValueError, match="pseudoreplication"):
        _verify_model_dependent_checkpoints(
            artifacts,
            policy="pcc_full",
            model_seeds=[5101, 5102, 5103],
        )


def test_complete_block_broadcasts_only_model_independent_policy(tmp_path):
    _, frozen = _frozen_registry(tmp_path)
    root = tmp_path / "confirmation"
    payload = _rollout_payload(
        frozen["frozen_digest"],
        "paper9_mpc",
        5101,
        frozen["partitions"]["confirmation"],
        [0.0, 0.0, 0.0, 0.0],
        [frozen["offline_reference_policy"]["checkpoint_sha256"]],
    )
    _write_payload(root / "paper9.json", payload)
    artifacts = load_confirmation_artifacts(
        root,
        expected_registry_digest=frozen["frozen_digest"],
        allowed_policies=set(frozen["deployable_baselines"]),
    )

    block = complete_policy_block(
        artifacts,
        policy="paper9_mpc",
        model_seeds=frozen["model_seeds"],
        rollout_seeds=frozen["partitions"]["confirmation"],
        allow_shared_model_block=True,
    )

    assert block.shape == (3, 20, 4)
    with pytest.raises(ValueError, match="complete"):
        complete_policy_block(
            artifacts,
            policy="paper9_mpc",
            model_seeds=frozen["model_seeds"],
            rollout_seeds=frozen["partitions"]["confirmation"],
            allow_shared_model_block=False,
        )


def test_confirmation_cli_writes_locked_json_markdown_and_seed_csv(tmp_path):
    registry_path, frozen = _frozen_registry(tmp_path)
    digest = frozen["frozen_digest"]
    model_seeds = frozen["model_seeds"]
    bishan_seeds = frozen["partitions"]["confirmation"]
    dongxing_seeds = frozen["partitions"]["dongxing_confirmation"]
    pcc_digests = frozen["selected_config"]["checkpoint_digests"]
    reference_digest = frozen["offline_reference_policy"]["checkpoint_sha256"]
    bishan_root = tmp_path / "bishan"
    dongxing_root = tmp_path / "dongxing"

    for model_index, model_seed in enumerate(model_seeds):
        model_digests = [pcc_digests[model_index]]
        dongxing_digests = [chr(ord("d") + model_index) * 64]
        _write_payload(
            bishan_root / f"pcc_full_{model_seed}.json",
            _rollout_payload(
                digest,
                "pcc_full",
                model_seed,
                bishan_seeds,
                [1.0, 1.0, 1.0, 1.0],
                model_digests,
            ),
        )
        _write_payload(
            bishan_root / f"pcc_matched_{model_seed}.json",
            _rollout_payload(
                digest,
                "pcc_matched",
                model_seed,
                bishan_seeds,
                [0.5, 0.5, 0.5, 0.5],
                model_digests,
            ),
        )
        _write_payload(
            dongxing_root / f"pcc_full_{model_seed}.json",
            _rollout_payload(
                digest,
                "pcc_full",
                model_seed,
                dongxing_seeds,
                [0.0, 0.0, 0.0, 0.0],
                dongxing_digests,
            ),
        )
    _write_payload(
        bishan_root / "paper9.json",
        _rollout_payload(
            digest,
            "paper9_mpc",
            model_seeds[0],
            bishan_seeds,
            [0.0, 0.0, 0.0, 0.0],
            [reference_digest],
        ),
    )
    _write_payload(
        dongxing_root / "paper9.json",
        _rollout_payload(
            digest,
            "paper9_mpc",
            model_seeds[0],
            dongxing_seeds,
            [0.0, 0.0, 0.0, 0.0],
            [reference_digest],
        ),
    )
    output_prefix = tmp_path / "results" / "confirmatory"

    main(
        [
            "--registry",
            str(registry_path),
            "--bishan-root",
            str(bishan_root),
            "--dongxing-json",
            str(dongxing_root),
            "--draws",
            "200",
            "--bootstrap-seed",
            "7",
            "--output-prefix",
            str(output_prefix),
        ]
    )

    report = json.loads(output_prefix.with_suffix(".json").read_text())
    assert report["primary_comparator"] == "paper9_mpc"
    assert report["locked_confirmation"]["overall_success"] is True
    assert len(report["policy_checkpoint_digests"]["bishan"]["pcc_full"]) == 3
    assert output_prefix.with_suffix(".md").exists()
    markdown = output_prefix.with_suffix(".md").read_text(encoding="utf-8")
    assert "Connected-area lower bound" in markdown
    seed_csv = output_prefix.with_name("confirmatory_seed_level.csv")
    assert seed_csv.exists()
    assert len(seed_csv.read_text().splitlines()) == 3 * 20 * 4 * 3 + 1
