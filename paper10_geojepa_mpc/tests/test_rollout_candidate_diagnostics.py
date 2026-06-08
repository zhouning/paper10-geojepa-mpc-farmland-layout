import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.rollout_candidate_diagnostics import (
    summarize_candidate_diagnostics,
    topk_metrics_from_scores,
)


def test_topk_metrics_from_scores_reports_regret_and_hit():
    true_rewards = np.array([1.0, 3.0, 2.0, 0.0])
    pred_scores = np.array([0.1, 0.2, 0.9, 0.0])

    metrics = topk_metrics_from_scores(true_rewards, pred_scores, top_k=2)

    assert metrics["top1_hit"] == 0.0
    assert metrics["top1_regret"] == 1.0
    assert metrics["top2_hit"] == 1.0
    assert metrics["top2_regret"] == 0.0
    assert metrics["true_best_reward"] == 3.0


def test_summarize_candidate_diagnostics_averages_step_metrics():
    rows = [
        {
            "top1_hit": 0.0,
            "top1_regret": 1.0,
            "top5_hit": 1.0,
            "top5_regret": 0.0,
            "negative_reward_fraction": 0.2,
        },
        {
            "top1_hit": 1.0,
            "top1_regret": 0.0,
            "top5_hit": 1.0,
            "top5_regret": 0.0,
            "negative_reward_fraction": 0.4,
        },
    ]

    summary = summarize_candidate_diagnostics(rows, top_k=5)

    assert summary["states"] == 2
    assert summary["top1_hit_rate"] == 0.5
    assert summary["top1_regret_mean"] == 0.5
    assert summary["top5_hit_rate"] == 1.0
    assert summary["top5_regret_mean"] == 0.0
    assert summary["negative_reward_fraction_mean"] == pytest.approx(0.3)
