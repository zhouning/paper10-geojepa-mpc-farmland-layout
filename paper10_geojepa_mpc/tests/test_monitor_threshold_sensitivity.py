from paper10_geojepa_mpc.experiments.monitor_threshold_sensitivity import (
    DEFAULT_THRESHOLD_SET,
    MonitorThresholdSet,
    classify_monitor_at_thresholds,
    monitor_threshold_sensitivity_report,
    monitors_from_stage1_matrix,
    summarize_monitor_sensitivity,
)


def _monitor(name, regret, overlap, one_step, decision="stop", top_k=5):
    return {
        "name": name,
        "decision": decision,
        "top_k": top_k,
        "metrics": {
            "candidate_topk_regret": regret,
            "candidate_topk_overlap": overlap,
            "one_step_topk_regret": one_step,
        },
    }


def test_classify_monitor_at_thresholds_records_failed_metrics():
    monitor = _monitor("bad_candidate", 0.40, 0.45, 0.10)

    result = classify_monitor_at_thresholds(monitor, DEFAULT_THRESHOLD_SET)

    assert result["passes"] is False
    assert result["failed_metrics"] == [
        "candidate_topk_regret",
        "candidate_topk_overlap",
        "one_step_topk_regret",
    ]


def test_summarize_monitor_sensitivity_flags_threshold_sensitive_pass():
    monitor = _monitor("near_pass", 0.24, 0.51, 0.30, decision="continue")
    threshold_sets = [
        MonitorThresholdSet("strict", 0.20, 0.55, 0.50),
        DEFAULT_THRESHOLD_SET,
        MonitorThresholdSet("lenient", 0.30, 0.45, 0.10),
    ]

    result = summarize_monitor_sensitivity([monitor], threshold_sets)
    row = result["rows"][0]

    assert row["name"] == "near_pass"
    assert row["default_pass"] is True
    assert row["pass_count"] == 2
    assert row["threshold_count"] == 3
    assert row["pass_fraction"] == 2 / 3
    assert row["stability_class"] == "threshold_sensitive_pass"


def test_summarize_monitor_sensitivity_flags_robust_stop():
    monitor = _monitor("hard_stop", 0.80, 0.20, 0.05)
    threshold_sets = [
        MonitorThresholdSet("strict", 0.20, 0.55, 0.50),
        DEFAULT_THRESHOLD_SET,
        MonitorThresholdSet("lenient", 0.30, 0.45, 0.10),
    ]

    result = summarize_monitor_sensitivity([monitor], threshold_sets)
    row = result["rows"][0]

    assert row["default_pass"] is False
    assert row["pass_count"] == 0
    assert row["stability_class"] == "robust_stop"


def test_summarize_monitor_sensitivity_records_threshold_provenance():
    monitor = _monitor("historical_pilot", 0.49, 0.50, 1.29, decision="continue")
    monitor["thresholds"] = {
        "candidate_topk_regret_max": 0.75,
        "candidate_topk_overlap_min": 0.40,
        "one_step_topk_regret_min": 0.50,
    }

    result = summarize_monitor_sensitivity([monitor])
    row = result["rows"][0]

    assert row["recorded_decision"] == "continue"
    assert row["recorded_threshold_pass"] is True
    assert row["default_pass"] is False
    assert row["threshold_provenance"] == "historical_thresholds"
    assert row["decision_alignment"] == "recorded_continue_current_default_stop"

def test_monitor_threshold_sensitivity_report_keeps_audit_boundary():
    monitors = [
        _monitor("near_pass", 0.24, 0.51, 0.30, decision="continue"),
        _monitor("hard_stop", 0.80, 0.20, 0.05),
    ]
    result = summarize_monitor_sensitivity(monitors)

    text = monitor_threshold_sensitivity_report(result)

    assert "# Monitor-threshold sensitivity audit" in text
    assert "This audit reruns gate classification only" in text
    assert "| near_pass | yes | 0.667 | threshold_sensitive_pass |" in text
    assert "| hard_stop | no | 0.000 | robust_stop |" in text

def test_monitors_from_stage1_matrix_flattens_50state_rows():
    matrix = {
        "runs": [
            {
                "run_name": "frontier_random050_50x16_h5_seed48_f050",
                "monitors": [
                    {
                        "top_k": 6,
                        "monitor_decision": "continue",
                        "candidate_topk_regret": 0.2469,
                        "candidate_topk_overlap": 0.64,
                        "one_step_topk_regret": 2.3227,
                    }
                ],
            }
        ]
    }

    monitors = monitors_from_stage1_matrix(matrix)

    assert monitors == [
        {
            "name": "frontier_random050_50x16_h5_seed48_f050_top6",
            "decision": "continue",
            "top_k": 6,
            "metrics": {
                "candidate_topk_regret": 0.2469,
                "candidate_topk_overlap": 0.64,
                "one_step_topk_regret": 2.3227,
            },
        }
    ]
