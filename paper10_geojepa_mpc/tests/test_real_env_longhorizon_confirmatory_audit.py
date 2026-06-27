import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.real_env_longhorizon_confirmatory_audit import (
    DATE,
    build_real_env_longhorizon_confirmatory_audit,
    markdown_report,
    parse_args,
    write_real_env_longhorizon_confirmatory_audit,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
PAPER9_5SEED = RESULTS / "e0_env_rollout_5seed_h5_k50_executable_mask.json"
VALUE_SEED0 = (
    RESULTS
    / "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json"
)
VALUE_SEEDS1_4 = (
    RESULTS
    / "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json"
)
SEED0_PILOT_AUDIT = (
    RESULTS / "e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.json"
)


def _episode(seed: int, rewards: list[float], actions: list[int]) -> dict:
    return {
        "seed": seed,
        "horizon": 5,
        "top_k": 50,
        "rollout_steps": len(rewards),
        "steps_run": len(rewards),
        "terminated": True,
        "truncated": False,
        "total_reward": sum(rewards),
        "steps": [
            {
                "step": index,
                "action": action,
                "reward": reward,
                "slope_change_pct": -0.1 * index,
                "cont_change": 0.01 * index,
                "baimu_area_change_ha": -1.0 * index,
            }
            for index, (reward, action) in enumerate(zip(rewards, actions), start=1)
        ],
    }


def _paper9_payload() -> dict:
    return {
        "checkpoint": "rank_seed2028.pt",
        "prepared_dir": "D:\\test",
        "horizon": 5,
        "top_k": 50,
        "rollout_steps": 2,
        "mask_mode": "executable",
        "episodes": [
            _episode(seed=0, rewards=[1.0, 1.0], actions=[10, 20]),
            _episode(seed=1, rewards=[3.0, 1.0], actions=[30, 40]),
        ],
    }


def _value_payloads() -> list[tuple[str, dict]]:
    seed0 = _episode(seed=0, rewards=[2.0, 1.0], actions=[10, 25])
    seed0.update(
        {
            "checkpoint": "value_head_seed3044.pt",
            "prepared_dir": "D:\\test",
            "selector": "value_filter",
            "candidate_score_mode": "blend",
            "candidate_value_weight": 0.1,
            "mask_mode": "executable",
        }
    )
    seeds1 = {
        "checkpoint": "value_head_seed3044.pt",
        "prepared_dir": "D:\\test",
        "selector": "value_filter",
        "candidate_score_mode": "blend",
        "candidate_value_weight": 0.1,
        "mask_mode": "executable",
        "episodes": [
            _episode(seed=1, rewards=[4.0, 2.0], actions=[31, 40]),
        ],
    }
    return [("value_seed0.json", seed0), ("value_seed1.json", seeds1)]


def test_build_confirmatory_audit_reports_matched_5seed_style_deltas():
    audit = build_real_env_longhorizon_confirmatory_audit(
        baseline_payloads=[("paper9.json", _paper9_payload())],
        candidate_payloads=_value_payloads(),
        seed0_pilot_payload=None,
        date="2026-06-27",
    )

    assert audit["date"] == "2026-06-27"
    assert audit["status"] == "locked matched 5-seed real-data audit"
    assert audit["source_boundary"]["reran_rollouts"] is False
    assert audit["policies"]["baseline"]["selector"] == "paper9"
    assert audit["policies"]["candidate"]["selector"] == "value_filter"
    assert audit["policies"]["baseline"]["aggregate"]["total_reward_mean"] == pytest.approx(3.0)
    assert audit["policies"]["candidate"]["aggregate"]["total_reward_mean"] == pytest.approx(4.5)
    assert audit["paired_comparison"]["total_reward_delta_mean"] == pytest.approx(1.5)
    assert audit["paired_comparison"]["candidate_win_count"] == 2
    assert audit["paired_comparison"]["candidate_win_fraction"] == pytest.approx(1.0)
    assert audit["paired_comparison"]["per_seed"][0]["seed"] == 0
    assert audit["paired_comparison"]["per_seed"][0]["first_action_divergence_step"] == 2
    assert audit["paired_comparison"]["per_seed"][1]["first_action_divergence_step"] == 1
    assert audit["evidence_boundary"]["descriptive_matched_5seed_mean_reward_higher"] is True
    assert audit["evidence_boundary"]["inferential_superiority_supported"] is False
    assert audit["evidence_boundary"]["post_hoc_tuning_allowed"] is False


def test_build_confirmatory_audit_locks_real_tracked_5seed_numbers_and_seed0_linkage():
    audit = build_real_env_longhorizon_confirmatory_audit(
        baseline_payloads=[
            (PAPER9_5SEED.name, json.loads(PAPER9_5SEED.read_text(encoding="utf-8")))
        ],
        candidate_payloads=[
            (VALUE_SEED0.name, json.loads(VALUE_SEED0.read_text(encoding="utf-8"))),
            (
                VALUE_SEEDS1_4.name,
                json.loads(VALUE_SEEDS1_4.read_text(encoding="utf-8")),
            ),
        ],
        seed0_pilot_payload=json.loads(SEED0_PILOT_AUDIT.read_text(encoding="utf-8")),
        date=DATE,
    )

    assert audit["policies"]["baseline"]["aggregate"]["total_reward_mean"] == pytest.approx(
        67.5436698503176
    )
    assert audit["policies"]["baseline"]["aggregate"]["total_reward_std_sample"] == pytest.approx(
        7.22455439874099
    )
    assert audit["policies"]["candidate"]["aggregate"]["total_reward_mean"] == pytest.approx(
        69.47054604253474
    )
    assert audit["policies"]["candidate"]["aggregate"]["total_reward_std_sample"] == pytest.approx(
        1.0003610285842477
    )
    assert audit["paired_comparison"]["total_reward_delta_mean"] == pytest.approx(
        1.9268761922171436
    )
    assert audit["paired_comparison"]["total_reward_delta_std_sample"] == pytest.approx(
        7.512208608270984
    )
    assert audit["paired_comparison"]["candidate_win_count"] == 3
    assert audit["paired_comparison"]["candidate_loss_count"] == 2
    assert [
        row["total_reward_delta_candidate_minus_baseline"]
        for row in audit["paired_comparison"]["per_seed"]
    ] == pytest.approx(
        [
            -3.2408477615812643,
            3.613740374883278,
            8.424238053365706,
            9.062029496163603,
            -8.224779201745605,
        ]
    )
    assert audit["seed0_pilot_linkage"]["matches_pilot_audit"] is True
    assert audit["seed0_pilot_linkage"]["baseline_action_trace_match"] is True
    assert audit["seed0_pilot_linkage"]["candidate_action_trace_match"] is True
    assert audit["evidence_boundary"]["descriptive_matched_5seed_mean_reward_higher"] is True
    assert audit["evidence_boundary"]["variance_lower_in_matched_5seed"] is True
    assert audit["evidence_boundary"]["inferential_superiority_supported"] is False
    assert audit["evidence_boundary"]["direct_50_state_scaleup_success_supported"] is False


def test_markdown_report_states_confirmatory_result_without_inferential_claims():
    payload = build_real_env_longhorizon_confirmatory_audit(
        baseline_payloads=[("paper9.json", _paper9_payload())],
        candidate_payloads=_value_payloads(),
        seed0_pilot_payload=None,
        date="2026-06-27",
    )

    text = markdown_report(payload)

    assert "Paper10 real-data long-horizon matched 5-seed audit" in text
    assert "descriptive matched 5-seed result" in text
    assert "| total reward mean | 3.0000 | 4.5000 | 1.5000 |" in text
    assert "| candidate win count | 0 | 2 | 2 |" in text
    assert "inferential superiority is not supported" in text
    assert "post-hoc tuning" in text
    assert "p value" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
    assert "direct 50-state success" not in text.lower()


def test_write_confirmatory_audit_writes_json_and_markdown(tmp_path):
    baseline = tmp_path / "paper9.json"
    value_seed0 = tmp_path / "value_seed0.json"
    value_seed1 = tmp_path / "value_seed1.json"
    output_json = tmp_path / "confirmatory.json"
    output_md = tmp_path / "confirmatory.md"

    baseline.write_text(json.dumps(_paper9_payload()), encoding="utf-8")
    for path, payload in zip(
        [value_seed0, value_seed1],
        [payload for _, payload in _value_payloads()],
    ):
        path.write_text(json.dumps(payload), encoding="utf-8")

    payload = write_real_env_longhorizon_confirmatory_audit(
        baseline_json=[baseline],
        candidate_json=[value_seed0, value_seed1],
        seed0_pilot_json=None,
        output_json=output_json,
        output_md=output_md,
        date="2026-06-27",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    assert output_md.read_text(encoding="utf-8") == markdown_report(payload)


def test_cli_accepts_confirmatory_audit_paths(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "real_env_longhorizon_confirmatory_audit",
            "--baseline-json",
            "paper9.json",
            "--candidate-json",
            "value_seed0.json",
            "--candidate-json",
            "value_seeds1-4.json",
            "--seed0-pilot-json",
            "pilot.json",
            "--output-json",
            "confirmatory.json",
            "--output-md",
            "confirmatory.md",
            "--date",
            "2026-06-27",
        ],
    )

    args = parse_args()

    assert args.baseline_json == ["paper9.json"]
    assert args.candidate_json == ["value_seed0.json", "value_seeds1-4.json"]
    assert args.seed0_pilot_json == "pilot.json"
    assert args.date == "2026-06-27"
