import json

from paper10_geojepa_mpc.experiments.real_env_smoke_report import (
    build_smoke_report,
    markdown_report,
    write_smoke_report,
)


def _rollout_payload():
    return {
        "checkpoint": "ckpt.pt",
        "prepared_dir": "D:\\test",
        "env_source": "paper9",
        "seed": 0,
        "horizon": 3,
        "top_k": 20,
        "rollout_steps": 5,
        "steps_run": 2,
        "total_reward": 1.5,
        "elapsed_sec": 9.0,
        "mask_mode": "executable",
        "selector": "paper9",
        "scoring": "reward",
        "terminated": False,
        "truncated": False,
        "steps": [
            {
                "step": 1,
                "action": 10,
                "reward": 0.5,
                "n_valid": 100,
                "n_base_valid": 110,
                "n_executable_valid": 100,
                "n_candidates": 20,
                "completed_swaps": 5,
                "select_time_sec": 1.2,
                "slope_change_pct": -0.1,
                "cont_change": 0.01,
                "baimu_area_change_ha": 0.0,
            },
            {
                "step": 2,
                "action": 20,
                "reward": 1.0,
                "n_valid": 99,
                "n_base_valid": 110,
                "n_executable_valid": 99,
                "n_candidates": 20,
                "completed_swaps": 4,
                "select_time_sec": 0.8,
                "slope_change_pct": -0.2,
                "cont_change": 0.02,
                "baimu_area_change_ha": -1.0,
            },
        ],
    }


def test_build_smoke_report_extracts_controlled_fields():
    report = build_smoke_report(
        _rollout_payload(),
        command="python -m smoke",
        raw_output="reviewer_outputs/raw.json",
        date="2026-06-18",
    )

    assert report["date"] == "2026-06-18"
    assert report["command"] == "python -m smoke"
    assert report["raw_output"] == "reviewer_outputs/raw.json"
    assert report["configuration"]["prepared_dir"] == "D:\\test"
    assert report["outcome"]["steps_run"] == 2
    assert report["outcome"]["total_reward"] == 1.5
    assert report["outcome"]["min_executable_valid"] == 99
    assert report["outcome"]["mean_select_time_sec"] == 1.0
    assert report["final_metrics"]["slope_change_pct"] == -0.2
    assert len(report["steps"]) == 2


def test_markdown_report_keeps_smoke_boundary():
    text = markdown_report(
        build_smoke_report(
            _rollout_payload(),
            command="python -m smoke",
            raw_output="reviewer_outputs/raw.json",
            date="2026-06-18",
        )
    )

    assert "Paper10 real-environment rollout smoke" in text
    assert "not a planning-quality result" in text
    assert "reviewer_outputs/raw.json" in text
    assert "| 2 | 20 | 1.0000 | 99 | 20 |" in text
    assert "direct 50-state success" not in text.lower()
    assert "robust transfer superiority" not in text.lower()


def test_write_smoke_report_writes_json_and_markdown(tmp_path):
    raw = tmp_path / "raw.json"
    output_json = tmp_path / "summary.json"
    output_md = tmp_path / "summary.md"
    raw.write_text(json.dumps(_rollout_payload()), encoding="utf-8")

    payload = write_smoke_report(
        raw,
        output_json,
        output_md,
        command="python -m smoke",
        date="2026-06-18",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)
