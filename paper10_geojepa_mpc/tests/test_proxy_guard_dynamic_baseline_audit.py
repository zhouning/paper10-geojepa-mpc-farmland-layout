import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.proxy_guard_dynamic_baseline_audit import (
    build_proxy_guard_dynamic_baseline_audit,
    proxy_guard_dynamic_baseline_audit_markdown,
    write_proxy_guard_dynamic_baseline_audit,
)


def _write_value_filter(path: Path) -> None:
    payload = {
        "aggregate": {
            "n_episodes": 2,
            "total_reward_mean": 10.0,
            "total_reward_std_sample": 1.0,
        },
        "seed_summaries": [
            {"seed": 0, "total_reward": 11.0},
            {"seed": 1, "total_reward": 9.0},
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _episode(seed: int, total_reward: float, rows: list[dict]) -> dict:
    return {
        "seed": seed,
        "steps_run": len(rows),
        "total_reward": total_reward,
        "audit_rows": rows,
    }


def _row(
    *,
    selected: int,
    executed: int,
    selected_reward: float,
    model_reward: float,
    candidate_reward: float,
) -> dict:
    return {
        "selected_action": selected,
        "execution_action": executed,
        "selected_true_reward": selected_reward,
        "model_reward_top1_action": 2,
        "model_reward_top1_true_reward": model_reward,
        "candidate_top1_action": 3,
        "candidate_top1_true_reward": candidate_reward,
    }


def _write_proxy(path: Path, *, policy: str, rewards: list[float]) -> None:
    payload = {
        "execution_policy": policy,
        "true_reward_switch_margin": 0.1,
        "audit_top_reward": 1 if policy == "model_reward_margin_guard" else 0,
        "audit_top_candidate": 1 if policy == "candidate_score_margin_guard" else 0,
        "audit_random_sample": 0,
        "seeds": [0, 1],
        "steps": 2,
        "episodes": [
            _episode(
                0,
                rewards[0],
                [
                    _row(
                        selected=1,
                        executed=2 if policy == "model_reward_margin_guard" else 3,
                        selected_reward=1.0,
                        model_reward=2.0,
                        candidate_reward=3.0,
                    ),
                    _row(
                        selected=1,
                        executed=1,
                        selected_reward=2.0,
                        model_reward=1.0,
                        candidate_reward=1.0,
                    ),
                ],
            ),
            _episode(
                1,
                rewards[1],
                [
                    _row(
                        selected=1,
                        executed=2 if policy == "model_reward_margin_guard" else 3,
                        selected_reward=4.0,
                        model_reward=3.0,
                        candidate_reward=2.0,
                    ),
                    _row(
                        selected=1,
                        executed=1,
                        selected_reward=1.0,
                        model_reward=1.0,
                        candidate_reward=1.0,
                    ),
                ],
            ),
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_proxy_guard_dynamic_baseline_audit_blocks_proxy_superiority(tmp_path):
    value_filter = tmp_path / "value_filter.json"
    model_proxy = tmp_path / "model_proxy.json"
    candidate_proxy = tmp_path / "candidate_proxy.json"
    _write_value_filter(value_filter)
    _write_proxy(
        model_proxy,
        policy="model_reward_margin_guard",
        rewards=[9.0, 8.0],
    )
    _write_proxy(
        candidate_proxy,
        policy="candidate_score_margin_guard",
        rewards=[7.0, 6.0],
    )

    payload = build_proxy_guard_dynamic_baseline_audit(
        value_filter_summary_json=value_filter,
        model_proxy_json=model_proxy,
        candidate_proxy_json=candidate_proxy,
        output_date="2026-07-09",
    )

    assert payload["status"] == "proxy_guard_dynamic_baseline_stress_audit"
    assert payload["source_boundary"]["reran_rollouts"] is True
    assert payload["source_boundary"]["reran_training"] is False

    model = payload["proxy_guard_rollouts"][0]
    candidate = payload["proxy_guard_rollouts"][1]
    assert model["total_reward_mean"] == pytest.approx(8.5)
    assert model["delta_vs_value_filter_5seed_mean"] == pytest.approx(-1.5)
    assert model["switch_rate"] == pytest.approx(0.5)
    assert model["switches_with_higher_immediate_true_reward"] == 1
    assert model["switches_with_lower_immediate_true_reward"] == 1
    assert candidate["total_reward_mean"] == pytest.approx(6.5)
    assert candidate["delta_vs_value_filter_5seed_mean"] == pytest.approx(-3.5)

    gates = payload["claim_gates"]
    assert gates["model_reward_proxy_beats_value_filter_5seed_mean"] is False
    assert gates["candidate_score_proxy_beats_value_filter_5seed_mean"] is False
    assert gates["no_oracle_proxy_guard_superiority_supported"] is False
    assert gates["true_reward_guard_remains_oracle_action_audit"] is True
    assert gates["manuscript_should_not_promote_proxy_guard"] is True


def test_proxy_guard_dynamic_baseline_markdown_records_claim_locks(tmp_path):
    value_filter = tmp_path / "value_filter.json"
    model_proxy = tmp_path / "model_proxy.json"
    candidate_proxy = tmp_path / "candidate_proxy.json"
    _write_value_filter(value_filter)
    _write_proxy(
        model_proxy,
        policy="model_reward_margin_guard",
        rewards=[9.0, 8.0],
    )
    _write_proxy(
        candidate_proxy,
        policy="candidate_score_margin_guard",
        rewards=[7.0, 6.0],
    )
    payload = build_proxy_guard_dynamic_baseline_audit(
        value_filter_summary_json=value_filter,
        model_proxy_json=model_proxy,
        candidate_proxy_json=candidate_proxy,
    )

    text = proxy_guard_dynamic_baseline_audit_markdown(payload)

    assert "# Paper10 proxy guard dynamic baseline stress audit" in text
    assert "model_reward_proxy_guard_m010" in text
    assert "candidate_score_proxy_guard_m010" in text
    assert "Do not claim proxy-guard rollout superiority." in text
    assert "deployable no-oracle policy" in text


def test_write_proxy_guard_dynamic_baseline_audit_writes_outputs(tmp_path):
    value_filter = tmp_path / "value_filter.json"
    model_proxy = tmp_path / "model_proxy.json"
    candidate_proxy = tmp_path / "candidate_proxy.json"
    output_json = tmp_path / "out.json"
    output_md = tmp_path / "out.md"
    _write_value_filter(value_filter)
    _write_proxy(
        model_proxy,
        policy="model_reward_margin_guard",
        rewards=[9.0, 8.0],
    )
    _write_proxy(
        candidate_proxy,
        policy="candidate_score_margin_guard",
        rewards=[7.0, 6.0],
    )

    payload = write_proxy_guard_dynamic_baseline_audit(
        value_filter_summary_json=value_filter,
        model_proxy_json=model_proxy,
        candidate_proxy_json=candidate_proxy,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-09",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        proxy_guard_dynamic_baseline_audit_markdown(payload)
    )
