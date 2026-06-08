from paper10_geojepa_mpc.experiments.rollout_summary import (
    aggregate_rollout_summaries,
    build_rollout_step_record,
    parse_seed_list,
    resolve_rollout_limit,
    summarize_rollout,
)


def test_summarize_rollout_counts_repeats_and_penalties():
    result = {
        "horizon": 3,
        "top_k": 20,
        "seed": 0,
        "total_reward": 1.5,
        "elapsed_sec": 9.0,
        "steps": [
            {
                "step": 1,
                "action": 7,
                "reward": 2.0,
                "completed_swaps": 5,
                "select_time_sec": 0.1,
                "slope_change_pct": -0.1,
                "cont_change": 0.01,
                "baimu_area_change_ha": -2.0,
            },
            {
                "step": 2,
                "action": 7,
                "reward": -1.0,
                "completed_swaps": 0,
                "select_time_sec": 0.2,
                "slope_change_pct": -0.1,
                "cont_change": 0.01,
                "baimu_area_change_ha": -2.0,
            },
            {
                "step": 3,
                "action": 4,
                "reward": 0.5,
                "completed_swaps": 3,
                "select_time_sec": 0.3,
                "slope_change_pct": -0.2,
                "cont_change": 0.02,
                "baimu_area_change_ha": -3.0,
            },
        ],
    }

    summary = summarize_rollout(result)

    assert summary["steps_run"] == 3
    assert summary["unique_actions"] == 2
    assert summary["repeated_action_count"] == 1
    assert summary["max_action_repeat"] == 2
    assert summary["top_repeated_actions"] == [{"action": 7, "count": 2}]
    assert summary["negative_reward_steps"] == 1
    assert summary["zero_swap_steps"] == 1
    assert summary["negative_zero_swap_steps"] == 1
    assert summary["mean_select_time_sec"] == 0.2
    assert summary["final_metrics"] == {
        "slope_change_pct": -0.2,
        "cont_change": 0.02,
        "baimu_area_change_ha": -3.0,
    }


def test_summarize_rollout_handles_missing_completed_swaps_for_legacy_logs():
    result = {
        "steps": [
            {"step": 1, "action": 1, "reward": -1.0, "select_time_sec": 0.5},
            {"step": 2, "action": 2, "reward": 1.0, "select_time_sec": 0.7},
        ]
    }

    summary = summarize_rollout(result)

    assert summary["steps_run"] == 2
    assert summary["negative_reward_steps"] == 1
    assert summary["zero_swap_steps"] is None
    assert summary["negative_zero_swap_steps"] is None


def test_build_rollout_step_record_preserves_completed_swaps():
    record = build_rollout_step_record(
        step_idx=0,
        action=12,
        reward=-1.0,
        mpc_info={
            "n_valid": 100,
            "n_candidates": 20,
            "best_cumrew": 1.25,
            "n_base_valid": 120,
            "n_executable_valid": 100,
        },
        select_time_sec=0.4,
        env_info={
            "completed_swaps": 0,
            "slope_change_pct": -0.5,
            "cont_change": 0.03,
            "baimu_area_change_ha": -4.0,
        },
    )

    assert record["step"] == 1
    assert record["action"] == 12
    assert record["completed_swaps"] == 0
    assert record["n_valid"] == 100
    assert record["n_base_valid"] == 120
    assert record["n_executable_valid"] == 100
    assert record["best_cumrew"] == 1.25


def test_build_rollout_step_record_preserves_selector_timing_fields():
    record = build_rollout_step_record(
        step_idx=0,
        action=12,
        reward=1.0,
        mpc_info={
            "n_valid": 100,
            "n_candidates": 20,
            "best_cumrew": 1.25,
            "score_time_sec": 0.1,
            "first_step_time_sec": 0.2,
            "rollout_time_sec": 0.3,
        },
        select_time_sec=0.7,
        env_info={},
    )

    assert record["score_time_sec"] == 0.1
    assert record["first_step_time_sec"] == 0.2
    assert record["rollout_time_sec"] == 0.3


def test_resolve_rollout_limit_keeps_env_horizon_when_rollout_steps_is_smaller():
    env = type("Env", (), {"max_steps": 100})()

    limit = resolve_rollout_limit(env, env_max_steps=None, rollout_steps=35)

    assert env.max_steps == 100
    assert limit == 35


def test_resolve_rollout_limit_can_cap_env_max_steps_for_smoke_semantics():
    env = type("Env", (), {"max_steps": 100})()

    limit = resolve_rollout_limit(env, env_max_steps=12, rollout_steps=None)

    assert env.max_steps == 12
    assert limit == 12


def test_parse_seed_list_accepts_commas_and_ranges():
    assert parse_seed_list("0,2,4") == [0, 2, 4]
    assert parse_seed_list("1-3") == [1, 2, 3]
    assert parse_seed_list("0,2-4") == [0, 2, 3, 4]


def test_aggregate_rollout_summaries_reports_mean_metrics():
    summaries = [
        {
            "total_reward": 10.0,
            "zero_swap_steps": 0,
            "negative_zero_swap_steps": 0,
            "final_metrics": {
                "slope_change_pct": -1.0,
                "cont_change": 0.1,
                "baimu_area_change_ha": -10.0,
            },
        },
        {
            "total_reward": 14.0,
            "zero_swap_steps": 2,
            "negative_zero_swap_steps": 1,
            "final_metrics": {
                "slope_change_pct": -2.0,
                "cont_change": 0.3,
                "baimu_area_change_ha": -20.0,
            },
        },
    ]

    aggregate = aggregate_rollout_summaries(summaries)

    assert aggregate["n_episodes"] == 2
    assert aggregate["total_reward_mean"] == 12.0
    assert aggregate["slope_change_pct_mean"] == -1.5
    assert aggregate["cont_change_mean"] == 0.2
    assert aggregate["baimu_area_change_ha_mean"] == -15.0
    assert aggregate["zero_swap_steps_sum"] == 2
    assert aggregate["negative_zero_swap_steps_sum"] == 1
