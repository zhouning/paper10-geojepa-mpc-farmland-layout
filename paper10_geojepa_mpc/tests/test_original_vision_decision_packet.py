import csv
import json

from paper10_geojepa_mpc.experiments.original_vision_decision_packet import (
    build_packet,
    choose_decision,
    write_decision_packet,
)


def test_choose_decision_prefers_confirmatory_rollouts_when_any_row_passes():
    assert choose_decision({"pass": 1, "near_pass": 0, "fail": 5}) == (
        "proceed_to_stage3_confirmatory_rollouts"
    )


def test_choose_decision_expands_seed_matrix_when_only_near_pass_exists():
    assert choose_decision({"pass": 0, "near_pass": 2, "fail": 4}) == (
        "run_stage1_optional_seed49_50_expansion"
    )


def test_choose_decision_keeps_conservative_theme_when_no_row_is_close():
    assert choose_decision({"pass": 0, "near_pass": 0, "fail": 6}) == (
        "keep_conservative_ceus_theme"
    )


def test_build_packet_includes_stage1_counts_stage2_effects_and_decision():
    packet = build_packet(
        stage1_payload={
            "decision_counts": {"pass": 0, "near_pass": 1, "fail": 5},
            "runs": [],
        },
        stage2_comparisons=[
            {
                "comparison_key": "return_50x16_h5",
                "reward_effect_transfer_minus_scratch": "-4.1141",
                "interpretation": "scratch_higher_reward",
            }
        ],
    )

    assert "| pass | 0 |" in packet
    assert "| near_pass | 1 |" in packet
    assert "| return_50x16_h5 | -4.1141 | scratch_higher_reward |" in packet
    assert "Decision: run_stage1_optional_seed49_50_expansion" in packet
    assert "direct 50-state success" not in packet.lower()
    assert "robust transfer superiority" not in packet.lower()


def test_write_decision_packet_reads_json_and_csv(tmp_path):
    stage1 = tmp_path / "stage1.json"
    stage2 = tmp_path / "stage2.csv"
    output = tmp_path / "packet.md"
    stage1.write_text(
        json.dumps({"decision_counts": {"pass": 1, "near_pass": 0, "fail": 5}, "runs": []}),
        encoding="utf-8",
    )
    with stage2.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "comparison_key",
                "reward_effect_transfer_minus_scratch",
                "interpretation",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "comparison_key": "low_budget_20",
                "reward_effect_transfer_minus_scratch": "4.2484",
                "interpretation": "transfer_higher_reward",
            }
        )

    text = write_decision_packet(stage1, stage2, output)

    assert output.exists()
    assert text == output.read_text(encoding="utf-8")
    assert "Decision: proceed_to_stage3_confirmatory_rollouts" in text
