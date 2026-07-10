import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.ceus_review_response_experiment_package import (
    build_ceus_review_response_experiment_package,
    ceus_review_response_experiment_package_markdown,
    write_ceus_review_response_experiment_package,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
BASELINE_HARDENING_JSON = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json"
)
MECHANISM_AUDIT_JSON = (
    RESULTS / "e0_paper10_ceus_mechanism_claim_audit_2026-06-27.json"
)
GUARD_INFORMATION_SET_JSON = (
    RESULTS / "e0_paper10_guard_information_set_audit_2026-07-09.json"
)


def test_build_ceus_review_response_package_records_guard_as_oracle_action_audit_evidence():
    payload = build_ceus_review_response_experiment_package(output_date="2026-07-09")

    assert payload["status"] == "ceus_review_response_algorithm_experiment_package"
    assert payload["source_boundary"] == {
        "source": "tracked Paper10 guard, baseline, and mechanism artifacts only",
        "reran_training": False,
        "reran_rollouts": False,
        "algorithm_reselection_from_tracked_evidence": True,
        "reviewer_driven_claim_reclassification": True,
    }

    primary = payload["primary_algorithm_evidence"]
    assert primary["algorithm"] == "true_reward_margin_guard"
    assert primary["setting"] == "bishan_20x16_top5"
    assert primary["audit_set"] == "rewardtop7"
    assert primary["switch_margin"] == pytest.approx(1.5)
    assert primary["n_seeds"] == 20
    assert primary["seed_wins"] == 20
    assert primary["seed_losses"] == 0
    assert primary["baseline_mean_reward"] == pytest.approx(65.8876435268697)
    assert primary["guard_mean_reward"] == pytest.approx(72.19178534319884)
    assert primary["mean_delta_vs_baseline"] == pytest.approx(6.304141816329158)
    assert primary["min_seed_delta_vs_baseline"] == pytest.approx(
        0.0028808405276095073
    )
    assert primary["bootstrap_95ci_delta"] == pytest.approx(
        [4.140109129548553, 8.50555044466635]
    )
    assert primary["switch_rate"] == pytest.approx(0.086)
    assert primary["mean_audit_action_count"] == pytest.approx(7.7605)
    assert primary["dual7x7_mean_audit_action_count"] == pytest.approx(8.1905)
    assert primary["audit_action_count_delta_vs_dual7x7"] == pytest.approx(-0.43)

    legacy = payload["legacy_value_filter_anchor"]
    assert legacy["role"] == "historical_descriptive_anchor_not_primary"
    assert legacy["n_seeds"] == 5
    assert legacy["candidate_win_count"] == 3
    assert legacy["candidate_loss_count"] == 2
    assert legacy["sign_test_p_value"] == pytest.approx(1.0)
    assert legacy["primary_claim_allowed"] is False

    assert payload["secondary_metric_assessment"]["classification"] == (
        "reward_primary_secondary_mixed"
    )
    assert payload["mechanism_boundary"]["monitor_gate_direct_reward_gain_supported"] is False
    assert payload["mechanism_boundary"]["monitor_gate_evidence_control_supported"] is True
    assert payload["mechanism_boundary"]["executable_mask_necessity_supported"] is True

    info = payload["guard_information_set_boundary"]
    assert info["information_set_boundary"]["allowed_primary_role"] == "oracle/action-audit guard"
    assert info["information_set_boundary"]["deployable_without_reward_oracle"] is False
    assert info["claim_gates"]["proxy_guard_rollout_superiority_supported"] is False
    assert info["claim_gates"]["dynamic_baseline_suite_complete"] is False
    assert "executable_random_20seed_rollout" in info["missing_dynamic_baselines"]

    gates = payload["claim_gates"]
    assert gates["primary_guard_confirmatory_20seed_supported"] is True
    assert gates["old_5seed_value_filter_primary_claim_blocked"] is True
    assert gates["secondary_metrics_uniformly_aligned"] is False
    assert gates["monitor_gate_online_reward_gain_supported"] is False
    assert gates["direct_50state_scaleup_supported"] is False
    assert gates["robust_transfer_superiority_supported"] is False
    assert gates["submission_story_should_use_guard_as_primary"] is False
    assert gates["submission_story_should_use_guard_as_oracle_action_audit_evidence"] is True
    assert gates["primary_guard_promoted_to_main_algorithm_candidate"] is False
    assert gates["primary_guard_recorded_as_oracle_action_audit_reward_evidence"] is True
    assert gates["true_reward_guard_deployable_without_oracle"] is False
    assert gates["proxy_guard_rollout_superiority_supported"] is False
    assert gates["dynamic_baseline_suite_complete"] is False


def test_ceus_review_response_markdown_records_algorithmic_change_and_guardrails():
    payload = build_ceus_review_response_experiment_package(output_date="2026-07-09")
    text = ceus_review_response_experiment_package_markdown(payload)

    for token in [
        "# Paper10 CEUS review-response algorithm experiment package",
        "Status: ceus_review_response_algorithm_experiment_package",
        "`rewardtop7 margin=1.50`",
        "true-reward margin guard",
        "20 / 20",
        "72.1918",
        "65.8876",
        "6.3041",
        "4.1401",
        "8.5056",
        "switch rate",
        "7.7605",
        "8.1905",
        "historical descriptive anchor, not the primary claim",
        "3 / 5",
        "2 / 5",
        "diagnostic sign-test p=1.0000",
        "reward_primary_secondary_mixed",
        "monitor gate as evidence control",
        "Primary Oracle Action-Audit Reward Evidence",
        "submission_story_should_use_guard_as_oracle_action_audit_evidence",
        "Do not claim uniform secondary-metric improvement.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "oracle/action-audit guard",
        "not a standalone deployable no-oracle planner",
        "proxy_guard_rollout_superiority_supported",
    ]:
        assert token in text


def test_write_ceus_review_response_package_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "package.json"
    output_md = tmp_path / "package.md"

    payload = write_ceus_review_response_experiment_package(
        true_reward_guard_json=TRUE_REWARD_GUARD_JSON,
        baseline_hardening_json=BASELINE_HARDENING_JSON,
        mechanism_audit_json=MECHANISM_AUDIT_JSON,
        guard_information_set_json=GUARD_INFORMATION_SET_JSON,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-09",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        ceus_review_response_experiment_package_markdown(payload)
    )
