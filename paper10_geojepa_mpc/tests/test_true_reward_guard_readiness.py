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
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_vs_blend010_10seed_100step_comparison_2026-07-07.json"
)
SMALL_10X12 = (
    RESULTS
    / "e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_5seed_paired_stats_2026-07-07.json"
)


def test_build_readiness_audit_promotes_20x16_guard_without_universal_margin_claim():
    audit = build_true_reward_guard_readiness_audit(
        primary_comparison_path=PRIMARY_20X16,
        small_scale_stats_path=SMALL_10X12,
        output_date="2026-07-08",
    )

    assert audit["status"] == "source-derived true-reward guard readiness audit"
    assert audit["source_boundary"] == {
        "reran_training": False,
        "reran_rollouts": False,
        "algorithm_redesign_performed": False,
        "source": "tracked JSON result artifacts only",
    }

    primary = audit["primary_guard"]
    assert primary["setting"] == "bishan_20x16_top5"
    assert primary["audit_set"] == "audit7x7"
    assert primary["switch_margin"] == 1.5
    assert primary["seed_wins"] == 10
    assert primary["n_seeds"] == 10
    assert primary["candidate_mean_reward"] == pytest.approx(73.0649023539798)
    assert primary["baseline_mean_reward"] == pytest.approx(68.80149357954322)
    assert primary["mean_delta_vs_baseline"] == pytest.approx(4.263408774436584)
    assert primary["min_seed_delta_vs_baseline"] == pytest.approx(0.0028808405276095073)

    small = audit["small_scale_guard"]
    assert small["setting"] == "bishan_10x12_top4"
    assert small["audit_set"] == "rewardtop7"
    assert small["switch_margin"] == 1.6
    assert small["seed_wins"] == 5
    assert small["n_seeds"] == 5
    assert small["mean_delta_vs_baseline"] == pytest.approx(7.02534672003666)

    gates = audit["claim_gates"]
    assert gates["primary_algorithm_candidate_supported"] is True
    assert gates["small_scale_consistency_supported"] is True
    assert gates["universal_fixed_margin_supported"] is False
    assert gates["direct_50state_scaleup_supported"] is False
    assert gates["robust_transfer_superiority_supported"] is False
    assert gates["deployment_ready_cadastral_planning_supported"] is False


def test_readiness_markdown_reports_evidence_and_negative_guardrails():
    audit = build_true_reward_guard_readiness_audit(
        primary_comparison_path=PRIMARY_20X16,
        small_scale_stats_path=SMALL_10X12,
        output_date="2026-07-08",
    )

    text = true_reward_guard_readiness_markdown(audit)

    assert "# Paper10 true-reward guard readiness audit" in text
    assert "Status: source-derived true-reward guard readiness audit." in text
    assert "`audit7x7 margin=1.50`" in text
    assert "`rewardtop7 margin=1.60`" in text
    assert "10 / 10" in text
    assert "Do not claim a universal fixed switch margin." in text
    assert "Do not claim direct 50-state Bishan scale-up success." in text
    assert "not final submission readiness" in text


def test_write_readiness_audit_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "readiness.json"
    output_md = tmp_path / "readiness.md"

    audit = write_true_reward_guard_readiness_audit(
        primary_comparison_path=PRIMARY_20X16,
        small_scale_stats_path=SMALL_10X12,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == audit
    assert output_md.read_text(encoding="utf-8") == (
        true_reward_guard_readiness_markdown(audit)
    )
