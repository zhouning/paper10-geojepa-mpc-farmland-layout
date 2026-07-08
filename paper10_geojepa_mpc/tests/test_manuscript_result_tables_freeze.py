import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.manuscript_result_tables_freeze import (
    DATE,
    build_manuscript_result_tables_freeze,
    markdown_report,
    parse_args,
    write_manuscript_result_tables_freeze,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
STAGE3 = RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"
CLAIM_AUDIT = RESULTS / "e0_paper10_claim_source_consistency_audit_2026-06-18.json"
ANCHOR_RAW_AUDIT = (
    RESULTS / "e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json"
)
TRUE_REWARD_GUARD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_manuscript_result_tables_freeze_derives_tables_from_audited_sources():
    payload = build_manuscript_result_tables_freeze(
        stage3_payload=_load(STAGE3),
        claim_audit_payload=_load(CLAIM_AUDIT),
        anchor_raw_audit_payload=_load(ANCHOR_RAW_AUDIT),
        true_reward_guard_payload=_load(TRUE_REWARD_GUARD),
        date=DATE,
    )

    assert payload["date"] == "2026-06-19"
    assert payload["status"] == "source-derived table freeze"
    assert payload["source_boundary"]["new_experimental_claim"] is False
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert payload["raw_rollout_consistency"]["overall_consistency_pass"] is True

    anchor_table = payload["tables"]["table_bishan_anchor_vs_matched_baseline"]
    assert [row["row_id"] for row in anchor_table] == [
        "matched_paper9_rank_seed2028_baseline",
        "bishan_20x16_top5_frozen_anchor",
    ]
    baseline, anchor = anchor_table
    assert baseline["mean_reward"] == pytest.approx(67.5436698503176)
    assert baseline["std_sample"] == pytest.approx(7.22455439874099)
    assert anchor["mean_reward"] == pytest.approx(69.47054604253474)
    assert anchor["std_sample"] == pytest.approx(1.0003610285842477)
    assert anchor["delta_vs_baseline"] == pytest.approx(1.9268761922171365)
    assert anchor["raw_rollout_consistency_pass"] is True
    assert "positive anchor" in anchor["interpretation"]

    stage3_table = payload["tables"]["table_stage3_boundary"]
    assert [row["run_name"] for row in stage3_table] == [
        "frontier_random050_50x16_h5_seed48_f050",
        "frontier_random050_50x24_h5_seed47_f075",
        "frontier_random050_50x24_h5_seed48_f075",
    ]
    assert [row["role"] for row in stage3_table] == [
        "confirmatory_pass",
        "confirmatory_pass",
        "diagnostic_near_pass",
    ]
    assert [row["states"] for row in stage3_table] == [50, 50, 50]
    assert [row["candidates"] for row in stage3_table] == [16, 24, 24]
    assert [row["selected_top_k"] for row in stage3_table] == [6, 12, 12]
    assert [row["mean_reward"] for row in stage3_table] == pytest.approx(
        [64.29600411367917, 66.25436421527586, 67.49131359932167]
    )
    assert [row["delta_vs_baseline"] for row in stage3_table] == pytest.approx(
        [-3.2476657366384245, -1.2893056350417424, -0.05235625099592767]
    )
    assert "boundary evidence" in stage3_table[0]["interpretation"]
    assert "must not be pooled" in stage3_table[2]["interpretation"]

    guard_table = payload["tables"]["table_true_reward_guard_readiness"]
    assert len(guard_table) == 1
    guard = guard_table[0]
    assert guard["row_id"] == "true_reward_margin_guard_m150_audit7x7_20seed"
    assert guard["setting"] == "bishan_20x16_top5"
    assert guard["baseline_mean_reward"] == pytest.approx(65.8876435268697)
    assert guard["guard_mean_reward"] == pytest.approx(72.17733781116401)
    assert guard["mean_delta_vs_baseline"] == pytest.approx(6.289694284294315)
    assert guard["seed_wins"] == 20
    assert guard["n_seeds"] == 20
    assert guard["bootstrap_95ci_delta_lower"] == pytest.approx(4.164250399042407)
    assert guard["switch_rate"] == pytest.approx(0.0855)
    assert "setting-specific guard" in guard["interpretation"]

    claim_table = payload["tables"]["table_claim_status"]
    claim_status = {row["claim_id"]: row for row in claim_table}
    assert claim_status["bishan_anchor"]["status"] == "supported"
    assert claim_status["stage3_confirmatory_50state"]["status"] == "not supported"
    assert claim_status["diagnostic_near_pass"]["status"] == "not pooled"
    assert claim_status["dongxing_return_label_scaling"]["status"] == "supported descriptively"
    assert claim_status["robust_transfer_superiority"]["status"] == "not supported"


def test_markdown_report_freezes_claim_bounded_manuscript_tables():
    payload = build_manuscript_result_tables_freeze(
        stage3_payload=_load(STAGE3),
        claim_audit_payload=_load(CLAIM_AUDIT),
        anchor_raw_audit_payload=_load(ANCHOR_RAW_AUDIT),
        true_reward_guard_payload=_load(TRUE_REWARD_GUARD),
        date=DATE,
    )

    text = markdown_report(payload)

    assert "Paper10 manuscript result tables freeze" in text
    assert "source-derived table freeze" in text
    assert "does not add a new experimental claim" in text
    assert "raw-rollout consistency: PASS" in text
    for token in [
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "64.2960",
        "66.2544",
        "67.4913",
        "72.1773",
        "65.8876",
        "6.2897",
        "20 / 20",
        "4.1643",
    ]:
        assert token in text
    assert "boundary evidence" in text
    assert "diagnostic near-pass only; must not be pooled" in text
    assert "robust transfer superiority | not supported" in text
    assert "Algorithm-readiness addendum: current true-reward guard" in text
    assert "setting-specific guard only" in text
    forbidden = [
        "direct 50-state success",
        "50-state success",
        "successful scale-up",
        "p value",
        "p-value",
        "confidence interval",
        "statistically significant",
        "formal superiority",
    ]
    lowered = text.lower()
    for phrase in forbidden:
        assert phrase not in lowered


def test_write_manuscript_result_tables_freeze_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "tables.json"
    output_md = tmp_path / "tables.md"

    payload = write_manuscript_result_tables_freeze(
        stage3_json=STAGE3,
        claim_audit_json=CLAIM_AUDIT,
        anchor_raw_audit_json=ANCHOR_RAW_AUDIT,
        true_reward_guard_json=TRUE_REWARD_GUARD,
        output_json=output_json,
        output_md=output_md,
        date=DATE,
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)
    assert str(STAGE3) in payload["source_files"]["stage3_json"]
    assert str(CLAIM_AUDIT) in payload["source_files"]["claim_audit_json"]
    assert str(ANCHOR_RAW_AUDIT) in payload["source_files"]["anchor_raw_audit_json"]
    assert str(TRUE_REWARD_GUARD) in payload["source_files"]["true_reward_guard_json"]


def test_cli_accepts_manuscript_table_freeze_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "manuscript_result_tables_freeze",
            "--stage3-json",
            "stage3.json",
            "--claim-audit-json",
            "claim.json",
            "--anchor-raw-audit-json",
            "anchor.json",
            "--true-reward-guard-json",
            "guard.json",
            "--output-json",
            "tables.json",
            "--output-md",
            "tables.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.stage3_json == "stage3.json"
    assert args.claim_audit_json == "claim.json"
    assert args.anchor_raw_audit_json == "anchor.json"
    assert args.true_reward_guard_json == "guard.json"
    assert args.output_json == "tables.json"
    assert args.output_md == "tables.md"
    assert args.date == "2026-06-19"
