import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.ceus_baseline_inference_hardening import (
    build_baseline_hardening_audit,
    classify_secondary_tradeoffs,
    hardening_markdown_report,
    paired_reward_summary,
    two_sided_sign_test_pvalue,
    write_baseline_hardening_audit,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
CURRENT_5SEED = (
    RESULTS / "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
)
MECHANISM_PACKET = RESULTS / "e0_paper10_mechanism_ablation_packet_2026-06-20.json"


def _matched_payload() -> dict:
    return {
        "date": "2026-06-27",
        "policies": {
            "baseline": {
                "aggregate": {
                    "total_reward_mean": 10.0,
                    "total_reward_std_sample": 4.0,
                },
            },
            "candidate": {
                "aggregate": {
                    "total_reward_mean": 11.0,
                    "total_reward_std_sample": 1.0,
                },
            },
        },
        "paired_comparison": {
            "matched_seeds": [0, 1, 2, 3, 4],
            "per_seed": [
                {
                    "seed": 0,
                    "baseline_total_reward": 12.0,
                    "candidate_total_reward": 10.0,
                    "total_reward_delta_candidate_minus_baseline": -2.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.10,
                        "cont_change": 0.02,
                        "baimu_area_change_ha": 5.0,
                    },
                },
                {
                    "seed": 1,
                    "baseline_total_reward": 8.0,
                    "candidate_total_reward": 11.0,
                    "total_reward_delta_candidate_minus_baseline": 3.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.20,
                        "cont_change": -0.01,
                        "baimu_area_change_ha": 2.0,
                    },
                },
                {
                    "seed": 2,
                    "baseline_total_reward": 9.0,
                    "candidate_total_reward": 14.0,
                    "total_reward_delta_candidate_minus_baseline": 5.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.30,
                        "cont_change": 0.01,
                        "baimu_area_change_ha": 1.0,
                    },
                },
                {
                    "seed": 3,
                    "baseline_total_reward": 7.0,
                    "candidate_total_reward": 13.0,
                    "total_reward_delta_candidate_minus_baseline": 6.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.15,
                        "cont_change": -0.02,
                        "baimu_area_change_ha": 3.0,
                    },
                },
                {
                    "seed": 4,
                    "baseline_total_reward": 14.0,
                    "candidate_total_reward": 7.0,
                    "total_reward_delta_candidate_minus_baseline": -7.0,
                    "final_metric_deltas": {
                        "slope_change_pct": -0.05,
                        "cont_change": 0.03,
                        "baimu_area_change_ha": -4.0,
                    },
                },
            ],
        },
    }


def _mechanism_payload() -> dict:
    return {
        "condition_comparisons": {
            "full_gated_masked": {
                "condition": "full_gated_masked",
                "mean_reward": 69.0,
                "std_sample": 1.0,
                "slope_change_pct_mean": -1.25,
                "cont_change_mean": 0.019,
                "baimu_area_change_ha_mean": -207.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
            "heuristic_paper9_masked": {
                "condition": "heuristic_paper9_masked",
                "mean_reward": 67.0,
                "std_sample": 7.0,
                "slope_change_pct_mean": -1.26,
                "cont_change_mean": 0.020,
                "baimu_area_change_ha_mean": -211.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
            "no_mask": {
                "condition": "no_mask",
                "mean_reward": 40.0,
                "std_sample": 10.0,
                "slope_change_pct_mean": -1.09,
                "cont_change_mean": 0.014,
                "baimu_area_change_ha_mean": -195.0,
                "zero_swap_steps_sum": 100.0,
                "negative_zero_swap_steps_sum": 98.0,
            },
            "ungated_top4": {
                "condition": "ungated_top4",
                "mean_reward": 69.0,
                "std_sample": 1.0,
                "slope_change_pct_mean": -1.25,
                "cont_change_mean": 0.019,
                "baimu_area_change_ha_mean": -207.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
        },
        "stage3_boundary": {
            "best_value_filter": {
                "run": "existing blend010",
                "mean_total_reward": 67.4913,
                "delta_vs_paper9": -0.0524,
            }
        },
    }


def test_two_sided_sign_test_for_three_wins_two_losses_is_diagnostic_only():
    assert two_sided_sign_test_pvalue(3, 2) == pytest.approx(1.0)
    assert two_sided_sign_test_pvalue(5, 0) == pytest.approx(0.0625)
    assert two_sided_sign_test_pvalue(0, 0) == pytest.approx(1.0)


def test_paired_reward_summary_classifies_mixed_seed_result():
    summary = paired_reward_summary(_matched_payload())

    assert summary["n_seeds"] == 5
    assert summary["candidate_win_count"] == 3
    assert summary["candidate_loss_count"] == 2
    assert summary["tie_count"] == 0
    assert summary["paired_mean_delta"] == pytest.approx(1.0)
    assert summary["paired_median_delta"] == pytest.approx(3.0)
    assert summary["paired_min_delta"] == pytest.approx(-7.0)
    assert summary["paired_max_delta"] == pytest.approx(6.0)
    assert summary["all_seeds_improve"] is False
    assert summary["uniform_superiority_supported"] is False
    assert summary["inferential_superiority_supported"] is False
    assert summary["descriptive_mean_reward_anchor_supported"] is True
    assert summary["sign_test"]["classification"] == "diagnostic_only"
    assert summary["sign_test"]["p_value"] == pytest.approx(1.0)


def test_secondary_tradeoffs_capture_reward_gain_and_metric_mixture():
    tradeoffs = classify_secondary_tradeoffs(_mechanism_payload())

    assert tradeoffs["classification"] == "reward_descriptive_secondary_mixed"
    assert tradeoffs["reward_delta_vs_matched_paper9"] == pytest.approx(2.0)
    assert tradeoffs["std_delta_vs_matched_paper9"] == pytest.approx(-6.0)
    assert tradeoffs["no_mask_negative_zero_swap_steps"] == pytest.approx(98.0)
    assert tradeoffs["ungated_reward_delta_vs_full"] == pytest.approx(0.0)
    assert "cont_change_mean" in tradeoffs["tradeoff_metrics"]
    assert tradeoffs["executable_mask_necessity_supported"] is True
    assert tradeoffs["monitor_gate_direct_reward_gain_supported"] is False


def test_build_current_tracked_hardening_audit_locks_claim_gates():
    audit = build_baseline_hardening_audit(
        matched_5seed=json.loads(CURRENT_5SEED.read_text(encoding="utf-8")),
        mechanism_packet=json.loads(MECHANISM_PACKET.read_text(encoding="utf-8")),
        matched_5seed_source=str(CURRENT_5SEED.relative_to(ROOT)),
        mechanism_packet_source=str(MECHANISM_PACKET.relative_to(ROOT)),
        date="2026-07-06",
    )

    summary = audit["paired_reward_summary"]
    assert audit["status"] == "source-derived CEUS baseline and inference hardening audit"
    assert summary["n_seeds"] == 5
    assert summary["candidate_win_count"] == 3
    assert summary["candidate_loss_count"] == 2
    assert summary["uniform_superiority_supported"] is False
    assert summary["inferential_superiority_supported"] is False
    assert summary["descriptive_mean_reward_anchor_supported"] is True
    assert summary["sign_test"]["p_value"] == pytest.approx(1.0)
    assert summary["paired_mean_delta"] == pytest.approx(1.9268761922171436)
    assert summary["paired_median_delta"] == pytest.approx(3.613740374883278)
    assert audit["secondary_metric_tradeoffs"]["classification"] == (
        "reward_descriptive_secondary_mixed"
    )
    assert audit["claim_gates"]["stage3_50state_scaleup_supported"] is False
    assert audit["claim_gates"]["robust_transfer_superiority_supported"] is False
    assert audit["source_provenance"]["matched_5seed_audit"].endswith(
        "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
    )


def test_markdown_report_uses_hardened_ceus_wording():
    audit = build_baseline_hardening_audit(
        matched_5seed=_matched_payload(),
        mechanism_packet=_mechanism_payload(),
        matched_5seed_source="matched.json",
        mechanism_packet_source="mechanism.json",
        date="2026-07-06",
    )

    text = hardening_markdown_report(audit)

    assert "# Paper10 CEUS baseline and inference hardening audit" in text
    assert "diagnostic_only" in text
    assert "mixed seed-wise outcome" in text
    assert "uniform superiority is not supported" in text
    assert "inferential superiority is not supported" in text
    assert "executable-mask necessity" in text
    assert "monitor gate as evidence control" in text
    assert "statistically significant" not in text
    assert "robustly superior" not in text


def test_write_baseline_hardening_audit_writes_json_and_markdown(tmp_path):
    matched = tmp_path / "matched.json"
    mechanism = tmp_path / "mechanism.json"
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    matched.write_text(json.dumps(_matched_payload()), encoding="utf-8")
    mechanism.write_text(json.dumps(_mechanism_payload()), encoding="utf-8")

    audit = write_baseline_hardening_audit(
        matched_5seed_json=matched,
        mechanism_packet_json=mechanism,
        output_json=output_json,
        output_md=output_md,
        date="2026-07-06",
    )

    assert output_json.exists()
    assert output_md.exists()
    assert json.loads(output_json.read_text(encoding="utf-8")) == audit
    assert output_md.read_text(encoding="utf-8") == hardening_markdown_report(audit)
