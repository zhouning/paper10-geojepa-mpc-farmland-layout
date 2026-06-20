import json

from paper10_geojepa_mpc.experiments.mechanism_ablation_packet import (
    build_packet,
    classify_monitor_gate,
    compare_conditions,
    markdown_report,
    write_packet,
)


def _rollout(mean_reward, std_reward=1.0, mean_select_time=0.25):
    return {
        "aggregate": {
            "total_reward_mean": mean_reward,
            "total_reward_std_sample": std_reward,
            "slope_change_pct_mean": -1.2,
            "cont_change_mean": 0.02,
            "baimu_area_change_ha_mean": -180.0,
            "zero_swap_steps_sum": 0,
            "negative_zero_swap_steps_sum": 0,
        },
        "episode_summaries": [
            {
                "seed": 0,
                "total_reward": mean_reward,
                "mean_select_time_sec": mean_select_time,
                "final_metrics": {
                    "slope_change_pct": -1.2,
                    "cont_change": 0.02,
                    "baimu_area_change_ha": -180.0,
                },
            }
        ],
    }


def test_classify_monitor_gate_distinguishes_pass_and_stop():
    passed = classify_monitor_gate(
        {
            "decision": "continue",
            "top_k": 5,
            "metrics": {
                "candidate_topk_regret": 0.18,
                "candidate_topk_overlap": 0.63,
                "one_step_topk_regret": 2.4,
            },
        }
    )
    stopped = classify_monitor_gate(
        {
            "decision": "stop",
            "top_k": 4,
            "metrics": {
                "candidate_topk_regret": 0.46,
                "candidate_topk_overlap": 0.48,
                "one_step_topk_regret": 2.4,
            },
        }
    )

    assert passed["gate_class"] == "pass"
    assert stopped["gate_class"] == "stop"
    assert stopped["failed_metrics"] == [
        "candidate_topk_regret",
        "candidate_topk_overlap",
    ]


def test_compare_conditions_reports_deltas_against_full_condition():
    rows = compare_conditions(
        baseline_name="full_gated_masked",
        condition_payloads={
            "full_gated_masked": _rollout(70.0, 1.0),
            "heuristic_paper9_masked": _rollout(67.0, 7.0),
            "no_mask": _rollout(65.0, 2.0),
        },
    )

    assert rows["full_gated_masked"]["delta_vs_baseline_reward"] == 0.0
    assert rows["heuristic_paper9_masked"]["delta_vs_baseline_reward"] == -3.0
    assert rows["no_mask"]["std_sample"] == 2.0
    assert rows["no_mask"]["zero_swap_steps_sum"] == 0.0


def test_compare_conditions_preserves_mask_failure_counts():
    rollout = _rollout(40.0, 2.0)
    rollout["aggregate"]["zero_swap_steps_sum"] = 100
    rollout["aggregate"]["negative_zero_swap_steps_sum"] = 98

    rows = compare_conditions(
        baseline_name="full_gated_masked",
        condition_payloads={
            "full_gated_masked": _rollout(70.0, 1.0),
            "no_mask": rollout,
        },
    )

    assert rows["no_mask"]["zero_swap_steps_sum"] == 100.0
    assert rows["no_mask"]["negative_zero_swap_steps_sum"] == 98.0


def test_compare_conditions_computes_std_from_episode_summaries_when_missing():
    rollout = _rollout(70.0, 0.0)
    del rollout["aggregate"]["total_reward_std_sample"]
    rollout["episode_summaries"] = [
        {"seed": 0, "total_reward": 68.0, "final_metrics": {}},
        {"seed": 1, "total_reward": 70.0, "final_metrics": {}},
        {"seed": 2, "total_reward": 72.0, "final_metrics": {}},
    ]

    rows = compare_conditions(
        baseline_name="full_gated_masked",
        condition_payloads={"full_gated_masked": rollout},
    )

    assert rows["full_gated_masked"]["std_sample"] == 2.0


def test_build_packet_keeps_claim_boundaries():
    packet = build_packet(
        monitors={
            "gated_top5": {
                "decision": "continue",
                "top_k": 5,
                "metrics": {
                    "candidate_topk_regret": 0.18,
                    "candidate_topk_overlap": 0.63,
                    "one_step_topk_regret": 2.4,
                },
            },
            "ungated_top4": {
                "decision": "stop",
                "top_k": 4,
                "metrics": {
                    "candidate_topk_regret": 0.46,
                    "candidate_topk_overlap": 0.48,
                    "one_step_topk_regret": 2.4,
                },
            },
        },
        condition_payloads={
            "full_gated_masked": _rollout(70.0, 1.0),
            "heuristic_paper9_masked": _rollout(67.0, 7.0),
        },
        stage3_boundary={"best_variant": {"mean_reward": 67.49}},
        training_metrics={"ungated_top4": {"elapsed_sec": 12.0}},
    )

    assert packet["claim_boundary"]["geo_jepa_prior_art_guard"] is True
    assert packet["monitor_gates"]["ungated_top4"]["gate_class"] == "stop"
    assert "full_gated_masked" in packet["condition_comparisons"]
    assert "direct 50-state success" not in markdown_report(packet).lower()
    assert "robust transfer superiority" not in markdown_report(packet).lower()
    assert "submission-ready" not in markdown_report(packet).lower()


def test_write_packet_writes_json_and_markdown(tmp_path):
    monitor = tmp_path / "monitor.json"
    full = tmp_path / "full.json"
    heuristic = tmp_path / "heuristic.json"
    stage3 = tmp_path / "stage3.json"
    output_json = tmp_path / "packet.json"
    output_md = tmp_path / "packet.md"

    monitor.write_text(
        json.dumps(
            {
                "decision": "continue",
                "top_k": 5,
                "metrics": {
                    "candidate_topk_regret": 0.18,
                    "candidate_topk_overlap": 0.63,
                    "one_step_topk_regret": 2.4,
                },
            }
        ),
        encoding="utf-8",
    )
    full.write_text(json.dumps(_rollout(70.0, 1.0)), encoding="utf-8")
    heuristic.write_text(json.dumps(_rollout(67.0, 7.0)), encoding="utf-8")
    stage3.write_text(
        json.dumps({"best_variant": {"mean_reward": 67.49}}),
        encoding="utf-8",
    )

    packet = write_packet(
        monitor_jsons={"gated_top5": monitor},
        condition_jsons={
            "full_gated_masked": full,
            "heuristic_paper9_masked": heuristic,
        },
        stage3_boundary_json=stage3,
        training_metric_jsons={},
        output_json=output_json,
        output_md=output_md,
    )

    assert output_json.exists()
    assert output_md.exists()
    assert packet["condition_comparisons"]["heuristic_paper9_masked"][
        "delta_vs_baseline_reward"
    ] == -3.0
