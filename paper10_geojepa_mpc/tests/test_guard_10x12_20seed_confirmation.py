import json

import pytest

from paper10_geojepa_mpc.experiments.guard_10x12_20seed_confirmation import (
    build_confirmation_packet,
    markdown_report,
    write_outputs,
)


def rollout_payload(seeds, rewards):
    episodes = [
        {
            "seed": seed,
            "horizon": 5,
            "top_k": 50,
            "total_reward": reward,
            "steps": [
                {
                    "step": 1,
                    "action": seed,
                    "reward": reward,
                    "select_time_sec": 0.1,
                    "slope_change_pct": 1.0 + seed,
                    "cont_change": 0.1,
                    "baimu_area_change_ha": 2.0,
                }
            ],
        }
        for seed, reward in zip(seeds, rewards, strict=True)
    ]
    return {
        "checkpoint": "checkpoint.pt",
        "prepared_dir": "D:\\test",
        "seeds": list(seeds),
        "horizon": 5,
        "top_k": 50,
        "candidate_score_mode": "blend",
        "candidate_value_weight": 0.1,
        "random_continuation_mode": "independent",
        "stable_candidate_order": False,
        "episodes": episodes,
    }


def test_build_confirmation_packet_merges_matched_seed_batches():
    baseline_0_4 = rollout_payload([0, 1], [10.0, 20.0])
    baseline_5_19 = rollout_payload([2, 3], [30.0, 40.0])
    guard_0_4 = rollout_payload([0, 1], [11.0, 22.0])
    guard_5_19 = rollout_payload([2, 3], [33.0, 44.0])

    packet = build_confirmation_packet(
        baseline_batches=[baseline_0_4, baseline_5_19],
        guard_batches=[guard_0_4, guard_5_19],
        expected_seeds=[0, 1, 2, 3],
    )

    assert packet["status"] == "descriptive_confirmation"
    assert packet["seed_count"] == 4
    assert packet["comparison"]["aggregate_delta"]["total_reward_mean"] == pytest.approx(2.5)
    assert packet["paired_stats"]["wins"] == 4
    assert packet["paired_stats"]["losses"] == 0
    assert packet["paired_stats"]["mean_delta"] == pytest.approx(2.5)
    assert packet["small_scale_guard"]["switch_margin"] == 1.6


def test_build_confirmation_packet_rejects_unmatched_seeds():
    baseline = rollout_payload([0, 1], [10.0, 20.0])
    guard = rollout_payload([0, 2], [11.0, 22.0])

    with pytest.raises(ValueError, match="expected matched seeds"):
        build_confirmation_packet(
            baseline_batches=[baseline],
            guard_batches=[guard],
            expected_seeds=[0, 1],
        )


def test_markdown_report_preserves_setting_specific_claim_boundary():
    packet = build_confirmation_packet(
        baseline_batches=[rollout_payload([0, 1], [10.0, 20.0])],
        guard_batches=[rollout_payload([0, 1], [11.0, 22.0])],
        expected_seeds=[0, 1],
    )

    text = markdown_report(packet)

    assert "10x12/top4" in text
    assert "rewardtop7 margin=1.60" in text
    assert "setting-specific" in text
    assert "Do not claim a universal fixed switch margin." in text
    assert "Do not claim direct 50-state Bishan scale-up success." in text
    assert "final submission readiness" in text


def test_write_outputs_creates_json_and_markdown_files(tmp_path):
    packet = build_confirmation_packet(
        baseline_batches=[rollout_payload([0, 1], [10.0, 20.0])],
        guard_batches=[rollout_payload([0, 1], [11.0, 22.0])],
        expected_seeds=[0, 1],
    )

    paths = write_outputs(packet, tmp_path)

    for key in (
        "baseline_combined_json",
        "guard_combined_json",
        "comparison_json",
        "comparison_md",
        "paired_stats_json",
        "triage_md",
    ):
        assert paths[key].exists()
    stats = json.loads(paths["paired_stats_json"].read_text(encoding="utf-8"))
    assert stats["n"] == 2
