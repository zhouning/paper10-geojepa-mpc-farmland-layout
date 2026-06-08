import pytest

from paper10_geojepa_mpc.experiments.value_filter_candidate_overlap import (
    candidate_overlap_metrics,
    summarize_overlap_rows,
)


def test_candidate_overlap_metrics_reports_topk_exclusion_and_reward_regret():
    reward_scores = [10.0, 8.0, 5.0, 0.0]
    candidate_scores = [0.0, 1.0, 2.0, 3.0]
    actions = [100, 101, 102, 103]

    metrics = candidate_overlap_metrics(
        reward_scores,
        candidate_scores,
        top_k=2,
        actions=actions,
    )

    assert metrics["topk_overlap_count"] == 0
    assert metrics["topk_overlap_fraction"] == 0.0
    assert metrics["reward_top1_in_candidate_topk"] == 0.0
    assert metrics["candidate_top1_in_reward_topk"] == 0.0
    assert metrics["candidate_top1_reward_regret"] == 10.0
    assert metrics["candidate_topk_best_reward_regret"] == 5.0
    assert metrics["reward_top1_action"] == 100
    assert metrics["candidate_top1_action"] == 103


def test_candidate_overlap_metrics_reports_partial_overlap():
    reward_scores = [10.0, 8.0, 5.0, 0.0]
    candidate_scores = [1.0, 3.0, 2.0, 0.0]

    metrics = candidate_overlap_metrics(
        reward_scores,
        candidate_scores,
        top_k=2,
    )

    assert metrics["topk_overlap_count"] == 1
    assert metrics["topk_overlap_fraction"] == 0.5
    assert metrics["reward_top1_in_candidate_topk"] == 0.0
    assert metrics["candidate_top1_in_reward_topk"] == 1.0
    assert metrics["candidate_top1_reward_regret"] == 2.0
    assert metrics["candidate_topk_best_reward_regret"] == 2.0


def test_summarize_overlap_rows_averages_metrics():
    rows = [
        {
            "topk_overlap_fraction": 0.25,
            "topk_jaccard": 0.2,
            "reward_top1_in_candidate_topk": 0.0,
            "candidate_top1_in_reward_topk": 1.0,
            "candidate_top1_reward_regret": 2.0,
            "candidate_topk_best_reward_regret": 1.0,
            "score_pearson": 0.5,
            "score_spearman": 0.4,
        },
        {
            "topk_overlap_fraction": 0.75,
            "topk_jaccard": 0.6,
            "reward_top1_in_candidate_topk": 1.0,
            "candidate_top1_in_reward_topk": 0.0,
            "candidate_top1_reward_regret": 0.0,
            "candidate_topk_best_reward_regret": 0.0,
            "score_pearson": 0.7,
            "score_spearman": 0.8,
        },
    ]

    summary = summarize_overlap_rows(rows)

    assert summary["states"] == 2
    assert summary["topk_overlap_fraction_mean"] == pytest.approx(0.5)
    assert summary["topk_jaccard_mean"] == pytest.approx(0.4)
    assert summary["reward_top1_in_candidate_topk_rate"] == pytest.approx(0.5)
    assert summary["candidate_top1_reward_regret_mean"] == pytest.approx(1.0)
