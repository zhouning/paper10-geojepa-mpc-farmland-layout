import json

from paper10_geojepa_mpc.experiments.real_env_smoke_boundary_audit import (
    build_boundary_audit,
    markdown_report,
    parse_args,
    write_boundary_audit,
)


def _paper9_smoke():
    return {
        "date": "2026-06-18",
        "command": "python -m paper9-smoke",
        "raw_output": "reviewer_outputs\\paper10_real_env_smoke_5step_h3_k20_seed0.json",
        "configuration": {
            "checkpoint": "paper10_geojepa_mpc\\experiments\\checkpoints\\e0_bishan_rank_seed2028\\rank_seed2028.pt",
            "prepared_dir": "D:\\test",
            "env_source": "paper9",
            "seed": 0,
            "horizon": 3,
            "top_k": 20,
            "rollout_steps": 5,
            "mask_mode": "executable",
            "selector": "paper9",
            "scoring": "reward",
        },
        "outcome": {
            "steps_run": 5,
            "total_reward": 7.646638186195446,
            "elapsed_sec": 7.36,
            "terminated": False,
            "truncated": False,
            "min_base_valid": 2381,
            "min_executable_valid": 2313,
            "mean_select_time_sec": 1.31,
            "positive_reward_steps": 5,
            "negative_reward_steps": 0,
        },
        "final_metrics": {
            "slope_change_pct": -0.07470047209533646,
            "cont_change": 0.0016273806799396162,
            "baimu_area_change_ha": -7.826418488866091,
        },
    }


def _value_filter_smoke():
    return {
        "date": "2026-06-19",
        "command": "python -m value-filter-smoke",
        "raw_output": "reviewer_outputs\\paper10_real_env_value_filter_smoke_5step_h5_k50_seed0.json",
        "configuration": {
            "checkpoint": "paper10_geojepa_mpc\\experiments\\checkpoints\\e0_frontier_random050_value_head_20x16_h5_seed44_top5\\value_head_seed3044.pt",
            "prepared_dir": "D:\\test",
            "env_source": "paper9",
            "seed": 0,
            "horizon": 5,
            "top_k": 50,
            "n_rollouts": 1,
            "rollout_steps": 5,
            "mask_mode": "executable",
            "selector": "value_filter",
            "scoring": "reward",
            "candidate_score_mode": "blend",
            "candidate_value_weight": 0.1,
            "random_continuation_mode": "independent",
            "stable_candidate_order": False,
        },
        "outcome": {
            "steps_run": 5,
            "total_reward": 2.4253884392585983,
            "elapsed_sec": 1.87,
            "terminated": False,
            "truncated": False,
            "min_base_valid": 2381,
            "min_executable_valid": 2312,
            "mean_select_time_sec": 0.063,
            "positive_reward_steps": 4,
            "negative_reward_steps": 1,
        },
        "final_metrics": {
            "slope_change_pct": -0.10330620803581785,
            "cont_change": 0.0007628346937216257,
            "baimu_area_change_ha": -24.969707818043233,
        },
    }


def test_build_boundary_audit_records_non_comparability_reasons():
    audit = build_boundary_audit(
        [
            ("paper9_selector", "paper9_report.json", _paper9_smoke()),
            ("value_filter_selector", "value_filter_report.json", _value_filter_smoke()),
        ],
        date="2026-06-19",
    )

    assert audit["date"] == "2026-06-19"
    assert audit["status"] == "execution-chain boundary audit"
    assert audit["comparability"]["performance_comparison_valid"] is False
    assert audit["comparability"]["planning_quality_result"] is False
    assert audit["comparability"]["short_horizon_performance_comparison"] is False
    assert "checkpoint" in audit["comparability"]["different_fields"]
    assert "selector" in audit["comparability"]["different_fields"]
    assert "horizon" in audit["comparability"]["different_fields"]
    assert "top_k" in audit["comparability"]["different_fields"]
    assert "single seed and five executed steps" in audit["comparability"]["reasons"]
    assert "value-filter run includes one negative reward step" in audit["comparability"]["reasons"]
    assert len(audit["smokes"]) == 2
    assert audit["smokes"][0]["selector"] == "paper9"
    assert audit["smokes"][1]["selector"] == "value_filter"
    assert audit["smokes"][1]["negative_reward_steps"] == 1


def test_markdown_report_keeps_boundary_language_and_shows_key_smoke_rows():
    text = markdown_report(
        build_boundary_audit(
            [
                ("paper9_selector", "paper9_report.json", _paper9_smoke()),
                ("value_filter_selector", "value_filter_report.json", _value_filter_smoke()),
            ],
            date="2026-06-19",
        )
    )

    assert "Paper10 real-environment smoke boundary audit" in text
    assert "not a planning-quality result" in text
    assert "not a short-horizon performance comparison" in text
    assert "different checkpoint, selector, horizon, and top_k settings" in text
    assert "value-filter run includes one negative reward step" in text
    assert "| paper9_selector | `paper9` | 3 | 20 | 5 | 7.6466 | 5 | 0 | 2313 |" in text
    assert "| value_filter_selector | `value_filter` | 5 | 50 | 5 | 2.4254 | 4 | 1 | 2312 |" in text
    assert "direct 50-state success" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
    assert "p value" not in text.lower()


def test_write_boundary_audit_writes_json_and_markdown(tmp_path):
    paper9 = tmp_path / "paper9.json"
    value_filter = tmp_path / "value_filter.json"
    output_json = tmp_path / "boundary.json"
    output_md = tmp_path / "boundary.md"
    paper9.write_text(json.dumps(_paper9_smoke()), encoding="utf-8")
    value_filter.write_text(json.dumps(_value_filter_smoke()), encoding="utf-8")

    payload = write_boundary_audit(
        [
            ("paper9_selector", paper9),
            ("value_filter_selector", value_filter),
        ],
        output_json,
        output_md,
        date="2026-06-19",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)


def test_cli_accepts_named_smoke_reports(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "real_env_smoke_boundary_audit",
            "--smoke",
            "paper9_selector=paper9.json",
            "--smoke",
            "value_filter_selector=value_filter.json",
            "--output-json",
            "boundary.json",
            "--output-md",
            "boundary.md",
            "--date",
            "2026-06-19",
        ],
    )

    args = parse_args()

    assert args.smoke == [
        "paper9_selector=paper9.json",
        "value_filter_selector=value_filter.json",
    ]
    assert args.date == "2026-06-19"
