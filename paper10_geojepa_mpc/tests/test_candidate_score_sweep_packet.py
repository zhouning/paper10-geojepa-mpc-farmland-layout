import pytest

from paper10_geojepa_mpc.experiments.candidate_score_sweep_packet import (
    CandidateScoreConfig,
    build_score_sweep_packet,
    parse_score_config_specs,
    render_score_sweep_markdown,
)


def test_parse_score_config_specs_builds_stable_keys():
    configs = parse_score_config_specs(
        ["value:0.50", "blend:0.10", "zscore_blend:0.20"]
    )

    assert [config.key for config in configs] == [
        "value_w0p50",
        "blend_w0p10",
        "zscore_blend_w0p20",
    ]
    assert configs[2].mode == "zscore_blend"
    assert configs[2].value_weight == pytest.approx(0.20)


def test_parse_score_config_specs_rejects_invalid_entries():
    with pytest.raises(ValueError, match="mode:weight"):
        parse_score_config_specs(["blend"])

    with pytest.raises(ValueError, match="value_weight"):
        parse_score_config_specs(["blend:1.50"])


def test_build_score_sweep_packet_ranks_low_regret_then_overlap():
    blend = CandidateScoreConfig("blend", 0.10)
    zscore = CandidateScoreConfig("zscore_blend", 0.50)
    rows_by_config = {
        blend.key: [
            {
                "topk_overlap_fraction": 0.25,
                "topk_jaccard": 0.2,
                "reward_top1_in_candidate_topk": 0.0,
                "candidate_top1_in_reward_topk": 0.0,
                "candidate_top1_reward_regret": 2.0,
                "candidate_topk_best_reward_regret": 1.0,
                "score_pearson": 0.2,
                "score_spearman": 0.2,
            },
        ],
        zscore.key: [
            {
                "topk_overlap_fraction": 0.75,
                "topk_jaccard": 0.6,
                "reward_top1_in_candidate_topk": 1.0,
                "candidate_top1_in_reward_topk": 1.0,
                "candidate_top1_reward_regret": 0.0,
                "candidate_topk_best_reward_regret": 0.0,
                "score_pearson": 0.8,
                "score_spearman": 0.9,
            },
        ],
    }

    packet = build_score_sweep_packet(
        configs=[blend, zscore],
        rows_by_config=rows_by_config,
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        seed=0,
        steps_requested=5,
        steps_run=1,
        top_k=50,
        reward_top1_policy_total_reward=12.5,
        elapsed_sec=1.25,
    )

    assert packet["recommended_config"]["key"] == "zscore_blend_w0p50"
    assert packet["ranking"][0]["key"] == "zscore_blend_w0p50"
    assert packet["ranking"][1]["key"] == "blend_w0p10"
    assert packet["source_boundary"]["diagnostic_type"] == "candidate_score_sweep"
    assert packet["source_boundary"]["reran_rollouts"] is False


def test_render_score_sweep_markdown_includes_recommended_rollout_command():
    blend = CandidateScoreConfig("blend", 0.10)
    packet = build_score_sweep_packet(
        configs=[blend],
        rows_by_config={
            blend.key: [
                {
                    "topk_overlap_fraction": 1.0,
                    "topk_jaccard": 1.0,
                    "reward_top1_in_candidate_topk": 1.0,
                    "candidate_top1_in_reward_topk": 1.0,
                    "candidate_top1_reward_regret": 0.0,
                    "candidate_topk_best_reward_regret": 0.0,
                    "score_pearson": 1.0,
                    "score_spearman": 1.0,
                },
            ],
        },
        checkpoint="paper10_geojepa_mpc/experiments/checkpoints/model.pt",
        prepared_dir=".",
        seed=7,
        steps_requested=5,
        steps_run=1,
        top_k=50,
        reward_top1_policy_total_reward=3.0,
        elapsed_sec=0.5,
    )

    text = render_score_sweep_markdown(packet)

    assert "# Candidate score sweep diagnostic" in text
    assert "| blend_w0p10 | blend | 0.1000 |" in text
    assert "--selector value_filter" in text
    assert "--candidate-score-mode blend" in text
    assert "--candidate-value-weight 0.10" in text
