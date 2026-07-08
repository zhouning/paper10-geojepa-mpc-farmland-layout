import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.post_guard_experiment_closure_refresh import (
    build_post_guard_experiment_closure_refresh,
    post_guard_experiment_closure_refresh_markdown,
    write_post_guard_experiment_closure_refresh,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
TRUE_REWARD_GUARD_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)
TABLE_FREEZE_JSON = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)
TABLE_FREEZE_MD = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"
)
EXPERIMENT_FREEZE_MD = (
    RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md"
)
CLOSURE_REGISTER_MD = (
    RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md"
)
SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)


def test_build_post_guard_refresh_derives_guard_values_and_locks_claims():
    payload = build_post_guard_experiment_closure_refresh(output_date="2026-07-08")

    assert payload["date"] == "2026-07-08"
    assert payload["status"] == "post_guard_experiment_closure_refresh"
    assert payload["source_boundary"] == {
        "new_experimental_claim": False,
        "reran_rollouts": False,
        "reran_training": False,
        "source": "tracked Paper10 guard and closure artifacts only",
    }
    assert payload["source_files"]["true_reward_guard_json"].endswith(
        "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
    )

    guard = payload["primary_guard"]
    assert guard["audit_set"] == "rewardtop7"
    assert guard["switch_margin"] == pytest.approx(1.5)
    assert guard["n_seeds"] == 20
    assert guard["guard_mean_reward"] == pytest.approx(72.19178534319884)
    assert guard["baseline_mean_reward"] == pytest.approx(65.8876435268697)
    assert guard["mean_delta_vs_baseline"] == 6.304141816329158
    assert guard["seed_wins"] == 20
    assert guard["bootstrap_95ci_delta_lower"] == pytest.approx(4.140109129548553)
    assert guard["mean_audit_action_count"] == pytest.approx(7.7605)
    assert guard["dual7x7_mean_audit_action_count"] == pytest.approx(8.1905)

    assert payload["closure_decision"] == {
        "default_next_phase": "bounded_manuscript_assembly",
        "resume_broad_algorithm_redesign": False,
        "historical_june_records_mutated": False,
    }
    assert payload["submission_boundary"]["status"] == "not_submission_ready"
    assert (
        "repository DOI or anonymous reviewer link"
        in payload["submission_boundary"]["open_blockers"]
    )
    assert payload["claim_locks"] == {
        "direct_50state_scaleup_supported": False,
        "robust_transfer_superiority_supported": False,
        "deployment_ready_supported": False,
        "universal_fixed_margin_supported": False,
        "final_submission_readiness_supported": False,
    }


def test_post_guard_refresh_markdown_reports_sources_values_and_negative_guardrails():
    payload = build_post_guard_experiment_closure_refresh(output_date="2026-07-08")
    text = post_guard_experiment_closure_refresh_markdown(payload)

    for token in [
        "# Paper10 post-guard experiment-closure refresh",
        "Status: post_guard_experiment_closure_refresh",
        "source-derived; no rollout or training rerun",
        "rewardtop7 margin=1.50",
        "72.1918",
        "65.8876",
        "6.3041",
        "20 / 20",
        "4.1401",
        "7.7605",
        "8.1905",
        "e0_paper10_true_reward_guard_readiness_2026-07-08.json",
        "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        "e0_paper10_experiment_closure_register_2026-06-27.md",
        "e0_paper10_submission_readiness_boundary_2026-06-26.md",
        "closure update, not a new experiment",
        "not final submission readiness",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
    ]:
        assert token in text


def test_write_post_guard_refresh_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "refresh.json"
    output_md = tmp_path / "refresh.md"

    payload = write_post_guard_experiment_closure_refresh(
        true_reward_guard_json=TRUE_REWARD_GUARD_JSON,
        true_reward_guard_md=TRUE_REWARD_GUARD_MD,
        table_freeze_json=TABLE_FREEZE_JSON,
        table_freeze_md=TABLE_FREEZE_MD,
        experiment_freeze_md=EXPERIMENT_FREEZE_MD,
        closure_register_md=CLOSURE_REGISTER_MD,
        submission_boundary_md=SUBMISSION_BOUNDARY_MD,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        post_guard_experiment_closure_refresh_markdown(payload)
    )
