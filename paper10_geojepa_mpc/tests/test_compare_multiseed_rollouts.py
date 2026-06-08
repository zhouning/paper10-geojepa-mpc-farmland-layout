import pytest

from paper10_geojepa_mpc.experiments.compare_multiseed_rollouts import (
    compare_rollout_runs,
    markdown_report,
    summarize_run,
)


def _episode(seed, reward, slope, cont, baimu, select_time, score_time=None):
    step = {
        "select_time_sec": select_time,
        "slope_change_pct": slope,
        "cont_change": cont,
        "baimu_area_change_ha": baimu,
    }
    if score_time is not None:
        step["score_time_sec"] = score_time
    return {
        "seed": seed,
        "total_reward": reward,
        "steps": [step],
    }


def test_summarize_run_uses_multiseed_aggregate_and_step_timing():
    data = {
        "aggregate": {
            "n_episodes": 2,
            "total_reward_mean": 11.0,
            "slope_change_pct_mean": -1.5,
            "cont_change_mean": 0.25,
            "baimu_area_change_ha_mean": -15.0,
        },
        "episode_summaries": [
            {"seed": 0, "total_reward": 10.0, "mean_select_time_sec": 1.0},
            {"seed": 1, "total_reward": 12.0, "mean_select_time_sec": 3.0},
        ],
        "episodes": [
            _episode(0, 10.0, -1.0, 0.2, -10.0, 1.0, score_time=0.5),
            _episode(1, 12.0, -2.0, 0.3, -20.0, 3.0, score_time=1.5),
        ],
    }

    summary = summarize_run("candidate", data)

    assert summary["name"] == "candidate"
    assert summary["aggregate"]["total_reward_mean"] == 11.0
    assert summary["timing"]["mean_select_time_sec"] == 2.0
    assert summary["timing"]["mean_score_time_sec"] == 1.0
    assert summary["seeds"][0]["final_metrics"]["slope_change_pct"] == -1.0


def test_compare_rollout_runs_reports_aggregate_and_seed_deltas():
    baseline = {
        "aggregate": {
            "n_episodes": 2,
            "total_reward_mean": 10.0,
            "slope_change_pct_mean": -1.0,
            "cont_change_mean": 0.2,
            "baimu_area_change_ha_mean": -10.0,
        },
        "episode_summaries": [
            {
                "seed": 0,
                "total_reward": 9.0,
                "mean_select_time_sec": 1.0,
                "final_metrics": {
                    "slope_change_pct": -0.9,
                    "cont_change": 0.2,
                    "baimu_area_change_ha": -8.0,
                },
            },
            {
                "seed": 1,
                "total_reward": 11.0,
                "mean_select_time_sec": 1.5,
                "final_metrics": {
                    "slope_change_pct": -1.1,
                    "cont_change": 0.3,
                    "baimu_area_change_ha": -12.0,
                },
            },
        ],
    }
    candidate = {
        "aggregate": {
            "n_episodes": 2,
            "total_reward_mean": 8.0,
            "slope_change_pct_mean": -1.2,
            "cont_change_mean": 0.25,
            "baimu_area_change_ha_mean": -9.0,
        },
        "episode_summaries": [
            {
                "seed": 0,
                "total_reward": 7.0,
                "mean_select_time_sec": 4.0,
                "final_metrics": {
                    "slope_change_pct": -1.0,
                    "cont_change": 0.1,
                    "baimu_area_change_ha": -6.0,
                },
            },
            {
                "seed": 1,
                "total_reward": 9.0,
                "mean_select_time_sec": 5.0,
                "final_metrics": {
                    "slope_change_pct": -1.4,
                    "cont_change": 0.4,
                    "baimu_area_change_ha": -12.0,
                },
            },
        ],
    }

    comparison = compare_rollout_runs("baseline", baseline, "candidate", candidate)

    assert comparison["aggregate_delta"]["total_reward_mean"] == -2.0
    assert comparison["aggregate_delta"]["slope_change_pct_mean"] == pytest.approx(-0.2)
    assert comparison["seed_deltas"][0]["total_reward_delta"] == -2.0
    assert comparison["seed_deltas"][1]["mean_select_time_sec_delta"] == 3.5


def test_markdown_report_contains_comparison_table():
    comparison = {
        "baseline": {
            "name": "baseline",
            "aggregate": {
                "total_reward_mean": 10.0,
                "slope_change_pct_mean": -1.0,
                "cont_change_mean": 0.2,
                "baimu_area_change_ha_mean": -10.0,
            },
            "timing": {"mean_select_time_sec": 1.0},
        },
        "candidate": {
            "name": "candidate",
            "aggregate": {
                "total_reward_mean": 8.0,
                "slope_change_pct_mean": -1.2,
                "cont_change_mean": 0.25,
                "baimu_area_change_ha_mean": -9.0,
            },
            "timing": {"mean_select_time_sec": 4.0},
        },
        "aggregate_delta": {
            "total_reward_mean": -2.0,
            "slope_change_pct_mean": -0.2,
            "cont_change_mean": 0.05,
            "baimu_area_change_ha_mean": 1.0,
            "mean_select_time_sec": 3.0,
        },
        "seed_deltas": [],
    }

    text = markdown_report(comparison)

    assert "# Multiseed rollout comparison" in text
    assert "| total_reward_mean | 10.0000 | 8.0000 | -2.0000 |" in text
    assert "| mean_select_time_sec | 1.0000 | 4.0000 | 3.0000 |" in text
