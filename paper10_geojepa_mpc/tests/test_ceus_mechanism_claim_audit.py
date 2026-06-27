import json

from paper10_geojepa_mpc.experiments.ceus_mechanism_claim_audit import (
    audit_mechanism_claims,
    mechanism_claim_audit_report,
    write_mechanism_claim_audit,
)


def _condition(
    mean_reward,
    std_sample,
    slope=-1.20,
    cont=0.020,
    baimu=-200.0,
    zero_swaps=0.0,
    negative_zero_swaps=0.0,
):
    return {
        "mean_reward": mean_reward,
        "std_sample": std_sample,
        "slope_change_pct_mean": slope,
        "cont_change_mean": cont,
        "baimu_area_change_ha_mean": baimu,
        "zero_swap_steps_sum": zero_swaps,
        "negative_zero_swap_steps_sum": negative_zero_swaps,
    }


def _packet():
    return {
        "monitor_gates": {
            "gated_top5": {"gate_class": "pass"},
            "ungated_top4": {"gate_class": "stop"},
        },
        "condition_comparisons": {
            "full_gated_masked": _condition(
                70.0,
                1.0,
                slope=-1.19,
                cont=0.018,
                baimu=-198.0,
            ),
            "heuristic_paper9_masked": _condition(
                67.0,
                7.0,
                slope=-1.21,
                cont=0.020,
                baimu=-205.0,
            ),
            "no_mask": _condition(
                40.0,
                10.0,
                zero_swaps=100.0,
                negative_zero_swaps=98.0,
            ),
            "ungated_top4": _condition(70.0, 1.0),
        },
        "stage3_boundary": {
            "best_value_filter": {
                "run": "existing blend010",
                "mean_total_reward": 67.49,
                "delta_vs_paper9": -0.05,
            },
            "best_overall": {
                "run": "paper9 baseline",
                "mean_total_reward": 67.54,
            },
        },
    }


def test_audit_mechanism_claims_separates_supported_and_rejected_claims():
    audit = audit_mechanism_claims(_packet())

    assert audit["baseline_policy"]["default_comparator"] == "matched_paper9_masked"
    assert audit["claims"]["matched_paper9_reward_stability"]["status"] == (
        "descriptive_support"
    )
    assert audit["claims"]["executable_mask_necessity"]["status"] == "supported"
    assert audit["claims"]["value_filter_superiority_vs_ungated"]["status"] == (
        "not_supported_equal_reward"
    )
    assert audit["claims"]["direct_monitor_gate_reward_gain"]["status"] == (
        "not_supported_equal_reward"
    )
    assert audit["claims"]["stage3_50state_positive_scaleup"]["status"] == (
        "not_supported_boundary"
    )
    assert audit["secondary_metric_tradeoffs"]["classification"] == "mixed"
    assert "cont_change_mean" in audit["secondary_metric_tradeoffs"]["tradeoff_metrics"]


def test_mechanism_claim_audit_report_keeps_ceus_boundaries():
    text = mechanism_claim_audit_report(audit_mechanism_claims(_packet()))

    assert "# CEUS mechanism-claim audit" in text
    assert "matched Paper9" in text
    assert "pairwise-only" in text
    assert "not a new rollout" in text
    assert "submission-ready" not in text.lower()
    assert "robust transfer superiority" not in text.lower()


def test_write_mechanism_claim_audit_writes_json_and_markdown(tmp_path):
    packet_path = tmp_path / "packet.json"
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    packet_path.write_text(json.dumps(_packet()), encoding="utf-8")

    audit = write_mechanism_claim_audit(
        packet_json=packet_path,
        output_json=output_json,
        output_md=output_md,
    )

    assert output_json.exists()
    assert output_md.exists()
    assert audit["claims"]["executable_mask_necessity"]["status"] == "supported"
