import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.true_reward_guard_readiness import (
    build_true_reward_guard_readiness_audit,
    true_reward_guard_readiness_markdown,
    write_true_reward_guard_readiness_audit,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
PRIMARY_20X16 = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-07.json"
)
PRIMARY_20X16_STATS = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_20seed_paired_stats_2026-07-07.json"
)
LEGACY_PRIMARY_20X16 = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_vs_blend010_20seed_100step_comparison_2026-07-07.json"
)
LEGACY_PRIMARY_20X16_STATS = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_20seed_paired_stats_2026-07-07.json"
)
SMALL_10X12 = (
    RESULTS
    / "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_20seed_paired_stats_2026-07-08.json"
)


def test_build_readiness_audit_promotes_20x16_guard_without_universal_margin_claim():
    audit = build_true_reward_guard_readiness_audit(output_date="2026-07-08")

    assert audit["status"] == "source-derived true-reward guard readiness audit"
    assert audit["source_boundary"] == {
        "reran_training": False,
        "reran_rollouts": False,
        "algorithm_redesign_performed": False,
        "source": "tracked JSON result artifacts only",
    }

    assert audit["source_provenance"]["primary_20x16_comparison"].endswith(
        "rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-07.json"
    )

    primary = audit["primary_guard"]
    assert primary["setting"] == "bishan_20x16_top5"
    assert primary["audit_set"] == "rewardtop7"
    assert primary["switch_margin"] == 1.5
    assert primary["seed_wins"] == 20
    assert primary["n_seeds"] == 20
    assert primary["candidate_mean_reward"] == pytest.approx(72.19178534319884)
    assert primary["baseline_mean_reward"] == pytest.approx(65.8876435268697)
    assert primary["mean_delta_vs_baseline"] == pytest.approx(6.30414181632915)
    assert primary["min_seed_delta_vs_baseline"] == pytest.approx(0.0028808405276095073)

    stats = audit["primary_paired_stats"]
    assert stats["n"] == 20
    assert stats["wins"] == 20
    assert stats["losses"] == 0
    assert stats["mean_delta"] == pytest.approx(6.304141816329158)
    assert stats["bootstrap_95ci_delta"][0] == pytest.approx(4.140109129548553)
    assert stats["candidate_guard_summary"]["switch_rate"] == pytest.approx(0.086)
    assert stats["candidate_guard_summary"]["mean_audit_action_count"] == pytest.approx(7.7605)
    assert stats["dual7x7_guard_summary"]["mean_audit_action_count"] == pytest.approx(8.1905)
    assert stats["mean_delta_vs_dual7x7"] == pytest.approx(0.01444753203484197)
    assert stats["wins_vs_dual7x7"] == 1
    assert stats["losses_vs_dual7x7"] == 1
    assert stats["ties_vs_dual7x7"] == 18

    small = audit["small_scale_guard"]
    assert small["setting"] == "bishan_10x12_top4"
    assert small["audit_set"] == "rewardtop7"
    assert small["switch_margin"] == 1.6
    assert small["seed_wins"] == 18
    assert small["seed_losses"] == 2
    assert small["n_seeds"] == 20
    assert small["mean_delta_vs_baseline"] == pytest.approx(6.035409141890397)
    assert small["min_seed_delta_vs_baseline"] == pytest.approx(-0.7662044920856914)
    assert small["bootstrap_95ci_delta"][0] == pytest.approx(3.6257886178706804)

    gates = audit["claim_gates"]
    assert gates["primary_algorithm_candidate_supported"] is True
    assert gates["small_scale_consistency_supported"] is True
    assert gates["universal_fixed_margin_supported"] is False
    assert gates["direct_50state_scaleup_supported"] is False
    assert gates["robust_transfer_superiority_supported"] is False
    assert gates["deployment_ready_cadastral_planning_supported"] is False


def test_readiness_audit_accepts_legacy_paired_stats_schema():
    audit = build_true_reward_guard_readiness_audit(
        primary_comparison_path=LEGACY_PRIMARY_20X16,
        primary_stats_path=LEGACY_PRIMARY_20X16_STATS,
        small_scale_stats_path=SMALL_10X12,
        output_date="2026-07-08",
    )

    assert audit["primary_guard"]["audit_set"] == "audit7x7"
    stats = audit["primary_paired_stats"]
    assert stats["wins"] == 20
    assert stats["losses"] == 0
    assert stats["ties"] == 0
    assert stats["mean_delta"] == pytest.approx(6.289694284294315)
    assert stats["bootstrap_95ci_delta"][0] == pytest.approx(4.164250399042407)


def test_readiness_markdown_reports_evidence_and_negative_guardrails():
    audit = build_true_reward_guard_readiness_audit(output_date="2026-07-08")

    text = true_reward_guard_readiness_markdown(audit)

    assert "# Paper10 true-reward guard readiness audit" in text
    assert "Status: source-derived true-reward guard readiness audit." in text
    assert "`rewardtop7 margin=1.50`" in text
    assert "`rewardtop7 margin=1.60`" in text
    assert "20 / 20" in text
    assert "18 / 20" in text
    assert "2 / 20" in text
    assert "## Primary Paired Statistics" in text
    assert "bootstrap 95% CI lower" in text
    assert "switch rate" in text
    assert "simplified robust default" in text
    assert "mean audited actions" in text
    assert "Do not claim a universal fixed switch margin." in text
    assert "Do not claim direct 50-state Bishan scale-up success." in text
    assert "not final submission readiness" in text


def test_write_readiness_audit_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "readiness.json"
    output_md = tmp_path / "readiness.md"

    audit = write_true_reward_guard_readiness_audit(
        primary_comparison_path=PRIMARY_20X16,
        primary_stats_path=PRIMARY_20X16_STATS,
        small_scale_stats_path=SMALL_10X12,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == audit
    assert output_md.read_text(encoding="utf-8") == (
        true_reward_guard_readiness_markdown(audit)
    )
