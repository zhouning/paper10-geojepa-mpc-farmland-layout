import json

from paper10_geojepa_mpc.experiments.real_env_longhorizon_pilot_audit import (
    build_longhorizon_pilot_audit,
    markdown_report,
    parse_args,
    write_longhorizon_pilot_audit,
)


def _baseline_rollout():
    return {
        "checkpoint": "rank_seed2028.pt",
        "prepared_dir": "D:\\test",
        "env_source": "paper9",
        "seed": 0,
        "horizon": 5,
        "top_k": 50,
        "rollout_steps": 3,
        "steps_run": 3,
        "total_reward": 2.5,
        "elapsed_sec": 10.0,
        "mask_mode": "executable",
        "selector": "paper9",
        "scoring": "reward",
        "terminated": True,
        "truncated": False,
        "steps": [
            {
                "step": 1,
                "action": 10,
                "reward": 1.0,
                "n_base_valid": 100,
                "n_executable_valid": 90,
                "n_candidates": 50,
                "slope_change_pct": -0.10,
                "cont_change": 0.01,
                "baimu_area_change_ha": -1.0,
            },
            {
                "step": 2,
                "action": 20,
                "reward": -0.5,
                "n_base_valid": 99,
                "n_executable_valid": 89,
                "n_candidates": 50,
                "slope_change_pct": -0.20,
                "cont_change": 0.02,
                "baimu_area_change_ha": -5.0,
            },
            {
                "step": 3,
                "action": 30,
                "reward": 2.0,
                "n_base_valid": 98,
                "n_executable_valid": 88,
                "n_candidates": 50,
                "slope_change_pct": -0.30,
                "cont_change": 0.03,
                "baimu_area_change_ha": -10.0,
            },
        ],
    }


def _candidate_rollout():
    rollout = _baseline_rollout()
    rollout.update(
        {
            "checkpoint": "value_head_seed3044.pt",
            "selector": "value_filter",
            "candidate_score_mode": "blend",
            "candidate_value_weight": 0.1,
            "total_reward": 1.5,
            "elapsed_sec": 8.0,
        }
    )
    rollout["steps"] = [
        {
            "step": 1,
            "action": 10,
            "reward": 0.5,
            "n_base_valid": 100,
            "n_executable_valid": 90,
            "n_candidates": 50,
            "slope_change_pct": -0.08,
            "cont_change": 0.015,
            "baimu_area_change_ha": -1.0,
        },
        {
            "step": 2,
            "action": 20,
            "reward": 0.5,
            "n_base_valid": 99,
            "n_executable_valid": 89,
            "n_candidates": 50,
            "slope_change_pct": -0.16,
            "cont_change": 0.025,
            "baimu_area_change_ha": -4.0,
        },
        {
            "step": 3,
            "action": 40,
            "reward": 0.5,
            "n_base_valid": 98,
            "n_executable_valid": 88,
            "n_candidates": 50,
            "slope_change_pct": -0.20,
            "cont_change": 0.05,
            "baimu_area_change_ha": -12.0,
        },
    ]
    return rollout


def test_build_longhorizon_pilot_audit_reports_seed0_deltas_and_trace_divergence():
    audit = build_longhorizon_pilot_audit(
        baseline_name="matched_paper9",
        baseline_source="reviewer_outputs\\paper9_100step.json",
        baseline_payload=_baseline_rollout(),
        candidate_name="matched_value_filter",
        candidate_source="reviewer_outputs\\value_filter_100step.json",
        candidate_payload=_candidate_rollout(),
        date="2026-06-27",
    )

    assert audit["date"] == "2026-06-27"
    assert audit["status"] == "locked seed0 long-horizon pilot audit"
    assert audit["source_boundary"]["reran_rollouts"] is False
    assert audit["runs"][0]["selector"] == "paper9"
    assert audit["runs"][1]["selector"] == "value_filter"
    assert audit["runs"][0]["negative_reward_steps"] == 1
    assert audit["runs"][1]["negative_reward_steps"] == 0
    assert audit["comparison"]["total_reward_delta_candidate_minus_baseline"] == -1.0
    assert audit["comparison"]["candidate_reward_greater"] is False
    assert audit["comparison"]["final_metric_deltas"]["slope_change_pct"] == 0.1
    assert audit["comparison"]["final_metric_deltas"]["cont_change"] == 0.02
    assert audit["comparison"]["final_metric_deltas"]["baimu_area_change_ha"] == -2.0
    assert audit["comparison"]["first_action_divergence_step"] == 3
    assert audit["comparison"]["shared_prefix_steps"] == 2
    assert audit["comparison"]["position_action_overlap_count"] == 2
    assert audit["comparison"]["unique_action_overlap_count"] == 2
    assert audit["evidence_boundary"]["planning_quality_result"] is False
    assert audit["evidence_boundary"]["final_performance_evidence"] is False
    assert audit["evidence_boundary"]["value_filter_superiority_supported"] is False
    assert audit["evidence_boundary"]["confirmatory_next_step"] == "matched seeds 0-4"


def test_markdown_report_keeps_pilot_boundary_and_no_superiority_claim():
    text = markdown_report(
        build_longhorizon_pilot_audit(
            baseline_name="matched_paper9",
            baseline_source="reviewer_outputs\\paper9_100step.json",
            baseline_payload=_baseline_rollout(),
            candidate_name="matched_value_filter",
            candidate_source="reviewer_outputs\\value_filter_100step.json",
            candidate_payload=_candidate_rollout(),
            date="2026-06-27",
        )
    )

    assert "Paper10 real-data long-horizon seed0 pilot audit" in text
    assert "not final planning-quality evidence" in text
    assert "value-filter superiority is not supported" in text
    assert "matched seeds `0-4`" in text
    assert "| total reward | 2.5000 | 1.5000 | -1.0000 |" in text
    assert "| first action divergence step | 3 |" in text
    assert "p value" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
    assert "direct 50-state success" not in text.lower()


def test_write_longhorizon_pilot_audit_writes_json_and_markdown(tmp_path):
    baseline = tmp_path / "paper9.json"
    candidate = tmp_path / "value_filter.json"
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    baseline.write_text(json.dumps(_baseline_rollout()), encoding="utf-8")
    candidate.write_text(json.dumps(_candidate_rollout()), encoding="utf-8")

    payload = write_longhorizon_pilot_audit(
        baseline_name="matched_paper9",
        baseline_json=baseline,
        candidate_name="matched_value_filter",
        candidate_json=candidate,
        output_json=output_json,
        output_md=output_md,
        date="2026-06-27",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)


def test_cli_accepts_longhorizon_pilot_inputs(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "real_env_longhorizon_pilot_audit",
            "--baseline-name",
            "matched_paper9",
            "--baseline-json",
            "paper9.json",
            "--candidate-name",
            "matched_value_filter",
            "--candidate-json",
            "value_filter.json",
            "--output-json",
            "audit.json",
            "--output-md",
            "audit.md",
            "--date",
            "2026-06-27",
        ],
    )

    args = parse_args()

    assert args.baseline_name == "matched_paper9"
    assert args.baseline_json == "paper9.json"
    assert args.candidate_name == "matched_value_filter"
    assert args.candidate_json == "value_filter.json"
    assert args.date == "2026-06-27"
