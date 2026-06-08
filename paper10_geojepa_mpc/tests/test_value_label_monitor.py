import numpy as np

from paper10_geojepa_mpc.experiments.value_label_monitor import (
    monitor_value_labels,
    monitor_markdown_report,
)


def _repeat_rows(row, n_states):
    return np.repeat(np.asarray(row, dtype=np.float32)[np.newaxis, :], n_states, axis=0)


def test_monitor_value_labels_waits_until_minimum_states():
    dataset = {
        "returns": _repeat_rows([4.0, 3.0, 2.0, 1.0], 2),
        "one_step_rewards": _repeat_rows([1.0, 4.0, 3.0, 2.0], 2),
        "candidate_scores": _repeat_rows([3.0, 4.0, 2.0, 1.0], 2),
    }

    result = monitor_value_labels(dataset, top_k=2, min_states=3)

    assert result["decision"] == "wait_more_states"
    assert result["diagnostics"]["n_states"] == 2
    assert "Need at least 3 states" in result["reasons"][0]


def test_monitor_value_labels_continues_when_topk_signal_is_usable():
    dataset = {
        "returns": _repeat_rows([4.0, 3.0, 2.0, 1.0], 4),
        "one_step_rewards": _repeat_rows([1.0, 4.0, 3.0, 2.0], 4),
        "candidate_scores": _repeat_rows([3.0, 4.0, 2.0, 1.0], 4),
    }

    result = monitor_value_labels(
        dataset,
        top_k=2,
        min_states=3,
        candidate_topk_regret_max=0.01,
        candidate_topk_overlap_min=0.5,
        one_step_topk_regret_min=0.5,
    )

    assert result["decision"] == "continue"
    assert result["diagnostics"]["candidate_score_vs_return"][
        "topk_best_return_regret_mean"
    ] == 0.0
    assert result["diagnostics"]["one_step_vs_return"][
        "topk_best_return_regret_mean"
    ] == 1.0


def test_monitor_value_labels_stops_when_candidate_topk_misses_return_winners():
    dataset = {
        "returns": _repeat_rows([4.0, 3.0, 2.0, 1.0], 4),
        "one_step_rewards": _repeat_rows([1.0, 4.0, 3.0, 2.0], 4),
        "candidate_scores": _repeat_rows([1.0, 2.0, 3.0, 4.0], 4),
    }

    result = monitor_value_labels(
        dataset,
        top_k=2,
        min_states=3,
        candidate_topk_regret_max=0.01,
        candidate_topk_overlap_min=0.5,
        one_step_topk_regret_min=0.5,
    )

    assert result["decision"] == "stop"
    assert any("candidate top-k regret" in reason for reason in result["reasons"])
    assert any("candidate top-k overlap" in reason for reason in result["reasons"])


def test_monitor_markdown_report_summarizes_decision():
    dataset = {
        "returns": _repeat_rows([4.0, 3.0, 2.0, 1.0], 4),
        "one_step_rewards": _repeat_rows([1.0, 4.0, 3.0, 2.0], 4),
        "candidate_scores": _repeat_rows([3.0, 4.0, 2.0, 1.0], 4),
    }
    result = monitor_value_labels(dataset, top_k=2, min_states=3)

    text = monitor_markdown_report(result)

    assert "# Value-label monitor" in text
    assert "Decision: `continue`" in text
    assert "| candidate_topk_regret | 0.0000 |" in text
