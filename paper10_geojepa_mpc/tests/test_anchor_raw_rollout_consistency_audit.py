import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.anchor_raw_rollout_consistency_audit import (
    DATE,
    audit_anchor_raw_rollout_consistency,
    build_anchor_raw_rollout_consistency_audit,
    markdown_report,
    parse_args,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
RAW_SEED0 = (
    RESULTS
    / "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json"
)
RAW_SEEDS1_4 = (
    RESULTS
    / "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json"
)
SUMMARY = (
    RESULTS
    / "e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json"
)
STAGE3 = RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"

EXPECTED_REWARDS = [
    67.7134969354234,
    70.2252087804031,
    69.7218379673849,
    69.82450306303002,
    69.86768346643231,
]


def test_build_anchor_raw_rollout_consistency_audit_recomputes_tracked_anchor_from_steps():
    payload = build_anchor_raw_rollout_consistency_audit(
        raw_rollout_payloads=[
            (RAW_SEED0.name, json.loads(RAW_SEED0.read_text(encoding="utf-8"))),
            (RAW_SEEDS1_4.name, json.loads(RAW_SEEDS1_4.read_text(encoding="utf-8"))),
        ],
        summary_payload=json.loads(SUMMARY.read_text(encoding="utf-8")),
        stage3_payload=json.loads(STAGE3.read_text(encoding="utf-8")),
        date=DATE,
    )

    assert payload["status"] == "source-derived consistency audit"
    assert payload["date"] == "2026-06-19"
    assert payload["source_boundary"]["new_experimental_claim"] is False
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert [row["seed"] for row in payload["raw_seed_summaries"]] == [0, 1, 2, 3, 4]
    assert [row["steps_run"] for row in payload["raw_seed_summaries"]] == [100] * 5
    assert [
        row["total_reward_from_steps"] for row in payload["raw_seed_summaries"]
    ] == pytest.approx(EXPECTED_REWARDS)
    assert [
        row["reported_total_reward"] for row in payload["raw_seed_summaries"]
    ] == pytest.approx(EXPECTED_REWARDS)
    assert payload["raw_aggregate"]["n_episodes"] == 5
    assert payload["raw_aggregate"]["total_reward_mean"] == pytest.approx(
        69.47054604253474
    )
    assert payload["raw_aggregate"]["total_reward_std_sample"] == pytest.approx(
        1.0003610285842477
    )
    assert payload["summary_consistency"]["aggregate_deltas"]["elapsed_sec_mean"] == pytest.approx(0.0)
    assert payload["summary_consistency"]["matches_raw"] is True
    assert payload["summary_consistency"]["seed_rewards"] == pytest.approx(
        EXPECTED_REWARDS
    )
    assert payload["stage3_consistency"]["aggregate_deltas"]["elapsed_sec_mean"] == pytest.approx(0.0)
    assert payload["stage3_consistency"]["matches_raw"] is True
    assert payload["stage3_consistency"]["anchor_role"] == "frozen_anchor"
    assert payload["stage3_consistency"]["seed_rewards"] == pytest.approx(
        EXPECTED_REWARDS
    )


def test_markdown_report_states_audit_boundary_and_key_anchor_numbers():
    payload = build_anchor_raw_rollout_consistency_audit(
        raw_rollout_payloads=[
            (RAW_SEED0.name, json.loads(RAW_SEED0.read_text(encoding="utf-8"))),
            (RAW_SEEDS1_4.name, json.loads(RAW_SEEDS1_4.read_text(encoding="utf-8"))),
        ],
        summary_payload=json.loads(SUMMARY.read_text(encoding="utf-8")),
        stage3_payload=json.loads(STAGE3.read_text(encoding="utf-8")),
        date=DATE,
    )

    text = markdown_report(payload)

    assert "Paper10 anchor raw-rollout consistency audit" in text
    assert "source-derived consistency audit" in text
    assert "does not add a new experimental claim" in text
    assert "No rollout was rerun" in text
    assert "Summary match: PASS" in text
    assert "Stage 3 frozen-anchor match: PASS" in text
    assert "69.4705" in text
    assert "1.0004" in text
    assert "| 0 | 100 | 67.7135 | 67.7135 | 0.0000 |" in text
    assert "direct 50-state success" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
    assert "p value" not in text.lower()


def test_audit_anchor_raw_rollout_consistency_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "anchor_audit.json"
    output_md = tmp_path / "anchor_audit.md"

    payload = audit_anchor_raw_rollout_consistency(
        raw_rollout_paths=[RAW_SEED0, RAW_SEEDS1_4],
        summary_path=SUMMARY,
        stage3_path=STAGE3,
        output_json=output_json,
        output_md=output_md,
        date=DATE,
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)


def test_cli_accepts_anchor_audit_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "anchor_raw_rollout_consistency_audit",
            "--raw-rollout",
            "seed0.json",
            "--raw-rollout",
            "seeds1-4.json",
            "--summary-json",
            "summary.json",
            "--stage3-json",
            "stage3.json",
            "--output-json",
            "anchor.json",
            "--output-md",
            "anchor.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.raw_rollout == ["seed0.json", "seeds1-4.json"]
    assert args.summary_json == "summary.json"
    assert args.stage3_json == "stage3.json"
    assert args.date == "2026-06-19"
