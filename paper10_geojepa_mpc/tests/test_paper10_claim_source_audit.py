import csv
import json

import pytest

from paper10_geojepa_mpc.experiments.paper10_claim_source_audit import (
    audit_paper10_claim_sources,
    build_dongxing_claim_audit,
    build_stage3_claim_audit,
    markdown_report,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_stage3_claim_audit_computes_anchor_and_50state_boundary():
    audit = build_stage3_claim_audit(
        {
            "paper9_baseline": {
                "aggregate": {
                    "total_reward_mean": 10.0,
                    "total_reward_std_sample": 4.0,
                }
            },
            "rows": [
                {
                    "role": "frozen_anchor",
                    "run_name": "anchor",
                    "aggregate": {
                        "total_reward_mean": 12.0,
                        "total_reward_std_sample": 2.0,
                    },
                    "matched_paper9_baseline_delta": {
                        "total_reward_mean": 2.0,
                    },
                },
                {
                    "role": "confirmatory_pass",
                    "run_name": "confirm_a",
                    "aggregate": {"total_reward_mean": 9.0},
                    "matched_paper9_baseline_delta": {
                        "total_reward_mean": -1.0,
                    },
                },
                {
                    "role": "confirmatory_pass",
                    "run_name": "confirm_b",
                    "aggregate": {"total_reward_mean": 9.5},
                    "matched_paper9_baseline_delta": {
                        "total_reward_mean": -0.5,
                    },
                },
                {
                    "role": "diagnostic_near_pass",
                    "run_name": "near",
                    "aggregate": {"total_reward_mean": 9.9},
                    "matched_paper9_baseline_delta": {
                        "total_reward_mean": -0.1,
                    },
                },
            ],
        }
    )

    assert audit["baseline_reward_mean"] == 10.0
    assert audit["anchor"]["reward_delta_vs_baseline"] == 2.0
    assert audit["anchor"]["std_delta_vs_baseline"] == -2.0
    assert audit["claims"]["bishan_anchor_improves_reward_and_stability"]["supported"] is True
    assert audit["claims"]["confirmatory_50state_rows_beat_baseline"]["supported"] is False
    assert audit["diagnostic_near_pass"]["pooled_with_confirmatory"] is False


def test_dongxing_claim_audit_keeps_transfer_superiority_bounded():
    audit = build_dongxing_claim_audit(
        return_label_rows=[
            {
                "label_type": "pairwise_1000s",
                "family": "transfer",
                "episodes": "15",
                "mean_reward": "30.0",
            },
            {
                "label_type": "pairwise_1000s",
                "family": "scratch",
                "episodes": "15",
                "mean_reward": "35.0",
            },
            {
                "label_type": "return_50x16_h5",
                "family": "transfer",
                "episodes": "15",
                "mean_reward": "45.0",
            },
            {
                "label_type": "return_50x16_h5",
                "family": "scratch",
                "episodes": "15",
                "mean_reward": "50.0",
            },
        ],
        low_budget_rows=[
            {
                "budget": "5",
                "family": "transfer",
                "episodes": "15",
                "reward_mean": "40.0",
            },
            {
                "budget": "5",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "55.0",
            },
            {
                "budget": "20",
                "family": "transfer",
                "episodes": "15",
                "reward_mean": "60.0",
            },
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "50.0",
            },
        ],
    )

    assert audit["claims"]["return_label_scaling_improves_transfer_family"]["supported"] is True
    assert audit["claims"]["return_label_scaling_improves_scratch_family"]["supported"] is True
    assert audit["claims"]["robust_transfer_superiority"]["supported"] is False
    assert audit["low_budget_comparisons"]["5"]["reward_effect_transfer_minus_scratch"] == -15.0
    assert audit["low_budget_comparisons"]["20"]["reward_effect_transfer_minus_scratch"] == 10.0


def test_audit_paper10_claim_sources_writes_json_and_markdown(tmp_path):
    stage3_json = tmp_path / "stage3.json"
    return_csv = tmp_path / "return.csv"
    low_csv = tmp_path / "low.csv"
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"

    stage3_json.write_text(
        json.dumps(
            {
                "paper9_baseline": {
                    "aggregate": {
                        "total_reward_mean": 10.0,
                        "total_reward_std_sample": 4.0,
                    }
                },
                "rows": [
                    {
                        "role": "frozen_anchor",
                        "run_name": "anchor",
                        "aggregate": {
                            "total_reward_mean": 12.0,
                            "total_reward_std_sample": 2.0,
                        },
                        "matched_paper9_baseline_delta": {
                            "total_reward_mean": 2.0,
                        },
                    },
                    {
                        "role": "confirmatory_pass",
                        "run_name": "confirm",
                        "aggregate": {"total_reward_mean": 9.0},
                        "matched_paper9_baseline_delta": {
                            "total_reward_mean": -1.0,
                        },
                    },
                    {
                        "role": "diagnostic_near_pass",
                        "run_name": "near",
                        "aggregate": {"total_reward_mean": 9.9},
                        "matched_paper9_baseline_delta": {
                            "total_reward_mean": -0.1,
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        return_csv,
        [
            {"label_type": "pairwise_1000s", "family": "transfer", "episodes": "15", "mean_reward": "30.0"},
            {"label_type": "pairwise_1000s", "family": "scratch", "episodes": "15", "mean_reward": "35.0"},
            {"label_type": "return_50x16_h5", "family": "transfer", "episodes": "15", "mean_reward": "45.0"},
            {"label_type": "return_50x16_h5", "family": "scratch", "episodes": "15", "mean_reward": "50.0"},
        ],
    )
    _write_csv(
        low_csv,
        [
            {"budget": "5", "family": "transfer", "episodes": "15", "reward_mean": "40.0"},
            {"budget": "5", "family": "scratch", "episodes": "15", "reward_mean": "55.0"},
        ],
    )

    payload = audit_paper10_claim_sources(stage3_json, return_csv, low_csv, output_json, output_md)

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    text = output_md.read_text(encoding="utf-8")
    assert text == markdown_report(payload)
    assert "## Regeneration command" in text
    assert "paper10_geojepa_mpc.experiments.paper10_claim_source_audit" in text
    assert "confirmatory 50-state rows do not beat the matched baseline" in text
    assert "robust Bishan-to-Dongxing transfer superiority" in text
    assert "direct 50-state success" not in text.lower()
