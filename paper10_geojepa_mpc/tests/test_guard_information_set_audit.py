import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.guard_information_set_audit import (
    build_guard_information_set_audit,
    guard_information_set_audit_markdown,
    write_guard_information_set_audit,
)


def _write_synthetic_audit(path: Path) -> None:
    payload = {
        "execution_policy": "margin_true_reward_guard",
        "true_reward_switch_margin": 1.5,
        "audit_top_reward": 7,
        "audit_top_candidate": 0,
        "audit_random_sample": 0,
        "seeds": [0],
        "steps": 2,
        "episodes": [
            {
                "seed": 0,
                "audit_rows": [
                    {
                        "selected_action": 10,
                        "execution_action": 11,
                        "audit_best_action": 11,
                        "selected_true_reward": 0.0,
                        "audit_best_true_reward": 2.0,
                        "model_reward_top1_action": 11,
                        "model_reward_top1_true_reward": 2.0,
                        "candidate_top1_action": 12,
                        "candidate_top1_true_reward": 1.0,
                        "selected_model_reward_score": 0.1,
                        "model_reward_top1_model_reward_score": 0.9,
                        "selected_candidate_score": 0.2,
                        "candidate_top1_candidate_score": 0.7,
                        "selected_true_reward_regret": 2.0,
                        "selected_is_audit_true_best": 0.0,
                        "audit_true_best_in_model_reward_topk": 1.0,
                        "audit_true_best_in_candidate_topk": 0.0,
                        "audit_action_count": 3,
                        "true_reward_time_sec": 0.5,
                        "n_valid": 100,
                    },
                    {
                        "selected_action": 20,
                        "execution_action": 20,
                        "audit_best_action": 21,
                        "selected_true_reward": 1.0,
                        "audit_best_true_reward": 1.4,
                        "model_reward_top1_action": 21,
                        "model_reward_top1_true_reward": 1.4,
                        "candidate_top1_action": 20,
                        "candidate_top1_true_reward": 1.0,
                        "selected_model_reward_score": 0.3,
                        "model_reward_top1_model_reward_score": 0.4,
                        "selected_candidate_score": 0.8,
                        "candidate_top1_candidate_score": 0.8,
                        "selected_true_reward_regret": 0.4,
                        "selected_is_audit_true_best": 0.0,
                        "audit_true_best_in_model_reward_topk": 1.0,
                        "audit_true_best_in_candidate_topk": 0.0,
                        "audit_action_count": 3,
                        "true_reward_time_sec": 0.25,
                        "n_valid": 90,
                    },
                ],
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_guard_information_set_audit_quantifies_oracle_and_proxy_boundaries(tmp_path):
    audit_json = tmp_path / "audit.json"
    _write_synthetic_audit(audit_json)

    payload = build_guard_information_set_audit(
        audit_rollout_json=audit_json,
        output_date="2026-07-09",
    )

    assert payload["status"] == "guard_information_set_and_baseline_stress_audit"
    assert payload["source_boundary"]["reran_rollouts"] is False
    assert payload["source_boundary"]["source"] == "tracked action-audit rollout rows"

    info = payload["information_set_boundary"]
    assert info["primary_guard_information_set"] == (
        "privileged_immediate_true_reward_action_audit"
    )
    assert info["deployable_without_reward_oracle"] is False
    assert info["allowed_primary_role"] == "oracle/action-audit guard"

    summary = payload["statewise_audit_summary"]
    assert summary["audited_states"] == 2
    assert summary["switches"] == 1
    assert summary["switch_rate"] == pytest.approx(0.5)
    assert summary["mean_audited_actions"] == pytest.approx(3.0)

    selected = payload["one_step_policy_diagnostics"]["selected_value_filter"]
    model_top1 = payload["one_step_policy_diagnostics"]["model_reward_top1_proxy"]
    candidate_top1 = payload["one_step_policy_diagnostics"]["candidate_score_top1_proxy"]
    audit_best = payload["one_step_policy_diagnostics"]["audit_true_best_upper_bound"]
    assert selected["mean_true_reward"] == pytest.approx(0.5)
    assert model_top1["mean_true_reward"] == pytest.approx(1.7)
    assert candidate_top1["mean_true_reward"] == pytest.approx(1.0)
    assert audit_best["mean_true_reward"] == pytest.approx(1.7)
    assert model_top1["mean_delta_vs_selected"] == pytest.approx(1.2)
    assert candidate_top1["mean_delta_vs_selected"] == pytest.approx(0.5)

    gates = payload["claim_gates"]
    assert gates["true_reward_guard_deployable_without_oracle"] is False
    assert gates["proxy_guard_rollout_superiority_supported"] is False
    assert gates["dynamic_baseline_suite_complete"] is False
    assert "executable_random_20seed_rollout" in payload["missing_dynamic_baselines"]


def test_guard_information_set_markdown_records_no_oracle_boundary(tmp_path):
    audit_json = tmp_path / "audit.json"
    _write_synthetic_audit(audit_json)
    payload = build_guard_information_set_audit(audit_rollout_json=audit_json)

    text = guard_information_set_audit_markdown(payload)

    assert "# Paper10 guard information-set and baseline stress audit" in text
    assert "oracle/action-audit guard" in text
    assert "not a standalone deployable no-oracle planner" in text
    assert "model_reward_top1_proxy" in text
    assert "executable_random_20seed_rollout" in text
    assert "Do not claim proxy-guard rollout superiority." in text


def test_write_guard_information_set_audit_writes_json_and_markdown(tmp_path):
    audit_json = tmp_path / "audit.json"
    _write_synthetic_audit(audit_json)
    output_json = tmp_path / "out.json"
    output_md = tmp_path / "out.md"

    payload = write_guard_information_set_audit(
        audit_rollout_json=audit_json,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-09",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        guard_information_set_audit_markdown(payload)
    )
