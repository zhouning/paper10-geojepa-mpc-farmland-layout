import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.value_label_diagnostics import (
    markdown_report,
    value_label_diagnostics,
)


def test_value_label_diagnostics_reports_one_step_return_disagreement():
    dataset = {
        "returns": np.array(
            [
                [3.0, 2.0, 1.0],
                [1.0, 3.0, 2.0],
            ],
            dtype=np.float32,
        ),
        "one_step_rewards": np.array(
            [
                [1.0, 2.0, 3.0],
                [1.0, 2.0, 3.0],
            ],
            dtype=np.float32,
        ),
    }

    report = value_label_diagnostics(dataset, top_k=2)

    assert report["n_states"] == 2
    assert report["n_candidates"] == 3
    assert report["top_k"] == 2
    assert report["label_variation"]["return_state_std_mean"] > 0.0
    assert report["label_variation"]["residual_state_std_mean"] > 0.0
    assert report["one_step_vs_return"]["top1_disagreement_rate"] == 1.0
    assert report["one_step_vs_return"]["topk_overlap_fraction_mean"] == pytest.approx(
        0.75
    )
    assert report["one_step_vs_return"]["one_step_top1_return_regret_mean"] == 1.5
    assert report["one_step_vs_return"]["pairwise_disagreement_rate_mean"] == (
        pytest.approx(2.0 / 3.0)
    )


def test_value_label_diagnostics_scores_optional_candidate_scores():
    dataset = {
        "returns": np.array(
            [
                [3.0, 2.0, 1.0],
                [1.0, 3.0, 2.0],
            ],
            dtype=np.float32,
        ),
        "one_step_rewards": np.array(
            [
                [1.0, 2.0, 3.0],
                [1.0, 2.0, 3.0],
            ],
            dtype=np.float32,
        ),
        "candidate_scores": np.array(
            [
                [3.0, 2.0, 1.0],
                [1.0, 3.0, 2.0],
            ],
            dtype=np.float32,
        ),
    }

    report = value_label_diagnostics(dataset, top_k=1)

    score_report = report["candidate_score_vs_return"]
    assert score_report["pearson_flat"] == pytest.approx(1.0)
    assert score_report["top1_disagreement_rate"] == 0.0
    assert score_report["candidate_top1_return_regret_mean"] == 0.0


def test_value_label_diagnostics_rejects_mismatched_arrays():
    dataset = {
        "returns": np.zeros((2, 3), dtype=np.float32),
        "one_step_rewards": np.zeros((2, 2), dtype=np.float32),
    }

    with pytest.raises(ValueError, match="same shape"):
        value_label_diagnostics(dataset)


def test_value_label_diagnostics_markdown_summarizes_key_metrics():
    report = value_label_diagnostics(
        {
            "returns": np.array([[3.0, 2.0, 1.0]], dtype=np.float32),
            "one_step_rewards": np.array([[1.0, 2.0, 3.0]], dtype=np.float32),
        },
        top_k=2,
    )

    text = markdown_report(report)

    assert "# Value-label diagnostics" in text
    assert "| top1_disagreement_rate | 1.0000 |" in text
    assert "| one_step_top1_return_regret_mean | 2.0000 |" in text
