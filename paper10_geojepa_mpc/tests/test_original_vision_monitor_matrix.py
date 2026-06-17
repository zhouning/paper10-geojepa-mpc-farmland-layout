import json

from paper10_geojepa_mpc.experiments.original_vision_monitor_matrix import (
    classify_monitor,
    classify_run,
    markdown_report,
    summarize_ablation,
)


def _monitor(top_k, decision, regret, overlap, one_step):
    return {
        "top_k": top_k,
        "decision": decision,
        "metrics": {
            "candidate_topk_regret": regret,
            "candidate_topk_overlap": overlap,
            "one_step_topk_regret": one_step,
        },
    }


def test_classify_monitor_passes_only_continue_rows():
    result = classify_monitor(_monitor(5, "continue", 0.24, 0.51, 0.26))

    assert result["decision_class"] == "pass"
    assert result["failed_metrics"] == []


def test_classify_monitor_marks_single_close_miss_as_near_pass():
    result = classify_monitor(_monitor(8, "stop", 0.29, 0.60, 0.40))

    assert result["decision_class"] == "near_pass"
    assert result["failed_metrics"] == ["candidate_topk_regret"]


def test_classify_monitor_rejects_multiple_misses():
    result = classify_monitor(_monitor(10, "stop", 0.40, 0.30, 0.10))

    assert result["decision_class"] == "fail"
    assert result["failed_metrics"] == [
        "candidate_topk_regret",
        "candidate_topk_overlap",
        "one_step_topk_regret",
    ]


def test_classify_run_prefers_pass_over_near_pass():
    run = {
        "run_name": "frontier_random050_50x16_h5_seed47_f050",
        "n_states": 50,
        "candidate_actions": 16,
        "label_horizon": 5,
        "frontier_fraction": 0.5,
        "label_seed": 47,
        "monitors": [
            _monitor(5, "stop", 0.29, 0.60, 0.40),
            _monitor(6, "continue", 0.20, 0.55, 0.30),
        ],
    }

    result = classify_run(run)

    assert result["row_decision"] == "pass"
    assert result["selected_top_k"] == 6
    assert result["near_pass_top_ks"] == [5]


def test_summarize_ablation_writes_json_and_markdown(tmp_path):
    summary_path = tmp_path / "summary.json"
    output_json = tmp_path / "matrix.json"
    output_md = tmp_path / "matrix.md"
    summary_path.write_text(
        json.dumps(
            {
                "run_root": str(tmp_path),
                "gate_topks": [5, 6],
                "runs": [
                    {
                        "run_name": "frontier_random050_50x16_h5_seed47_f050",
                        "n_states": 50,
                        "candidate_actions": 16,
                        "label_horizon": 5,
                        "frontier_fraction": 0.5,
                        "label_seed": 47,
                        "monitors": [
                            _monitor(5, "stop", 0.29, 0.60, 0.40),
                            _monitor(6, "continue", 0.20, 0.55, 0.30),
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = summarize_ablation(summary_path, output_json, output_md)

    assert payload["decision_counts"] == {"pass": 1, "near_pass": 0, "fail": 0}
    assert output_json.exists()
    assert output_md.exists()
    assert "| frontier_random050_50x16_h5_seed47_f050 | pass | 6 | 5 |" in output_md.read_text(
        encoding="utf-8"
    )


def test_markdown_report_includes_no_positive_scale_claim():
    text = markdown_report(
        {
            "source_summary": "summary.json",
            "decision_counts": {"pass": 0, "near_pass": 1, "fail": 1},
            "runs": [
                {
                    "run_name": "frontier_random050_50x16_h5_seed47_f050",
                    "row_decision": "near_pass",
                    "selected_top_k": None,
                    "near_pass_top_ks": [8],
                    "best_candidate_topk_regret": 0.29,
                    "best_candidate_topk_overlap": 0.60,
                    "best_one_step_topk_regret": 0.40,
                }
            ],
        }
    )

    assert "positive 50-state" not in text.lower()
    assert "robust transfer" not in text.lower()
