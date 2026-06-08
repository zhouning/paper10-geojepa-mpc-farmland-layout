from paper10_geojepa_mpc.experiments.summarize_value_head_rollouts import RUN_FILES


def test_summary_includes_value_filter_candidate_blend010_run():
    path = RUN_FILES.get("independent_value_h5_value_filter_candidate_blend010_reward_rollout")

    assert path is not None
    assert path.name == (
        "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_"
        "h5_k50_seed0_value_filter_candidate_blend010.json"
    )
