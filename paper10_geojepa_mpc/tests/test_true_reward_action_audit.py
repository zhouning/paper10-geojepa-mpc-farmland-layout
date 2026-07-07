import numpy as np

from paper10_geojepa_mpc.experiments.true_reward_action_audit import (
    action_audit_metrics,
    build_audit_action_set,
    choose_execution_action,
)


def test_build_audit_action_set_keeps_required_actions_and_unique_sample():
    valid_actions = np.array([10, 11, 12, 13, 14, 15], dtype=np.int64)
    model_reward_scores = np.array([0.1, 0.9, 0.2, 0.7, 0.3, 0.4])
    candidate_scores = np.array([0.8, 0.2, 0.1, 0.4, 0.95, 0.6])
    rng = np.random.default_rng(123)

    audit_actions = build_audit_action_set(
        valid_actions=valid_actions,
        selected_action=12,
        model_reward_scores=model_reward_scores,
        candidate_scores=candidate_scores,
        top_reward_count=2,
        top_candidate_count=2,
        random_sample_count=2,
        rng=rng,
    )

    assert len(audit_actions) == len(set(audit_actions.tolist()))
    assert 12 in audit_actions
    assert {11, 13}.issubset(set(audit_actions.tolist()))
    assert {14, 10}.issubset(set(audit_actions.tolist()))
    assert set(audit_actions.tolist()).issubset(set(valid_actions.tolist()))


def test_action_audit_metrics_reports_selected_true_reward_regret_and_ranks():
    actions = np.array([20, 21, 22, 23], dtype=np.int64)
    true_rewards = np.array([1.0, 4.0, -2.0, 3.0])
    model_reward_scores = np.array([0.2, 0.1, 0.9, 0.8])
    candidate_scores = np.array([0.3, 0.4, 0.2, 0.95])

    metrics = action_audit_metrics(
        actions=actions,
        true_rewards=true_rewards,
        model_reward_scores=model_reward_scores,
        candidate_scores=candidate_scores,
        selected_action=22,
        top_k=2,
    )

    assert metrics["selected_action"] == 22
    assert metrics["selected_true_reward"] == -2.0
    assert metrics["audit_best_true_reward"] == 4.0
    assert metrics["selected_true_reward_regret"] == 6.0
    assert metrics["selected_true_reward_rank"] == 4
    assert metrics["selected_is_audit_true_best"] == 0.0
    assert metrics["model_reward_top1_action"] == 22
    assert metrics["candidate_top1_action"] == 23
    assert metrics["audit_true_best_in_model_reward_topk"] == 0.0
    assert metrics["audit_true_best_in_candidate_topk"] == 1.0

def test_choose_execution_action_supports_value_filter_and_audit_true_best():
    metrics = {
        "selected_action": 22,
        "audit_best_action": 21,
    }

    assert choose_execution_action(metrics, "value_filter") == 22
    assert choose_execution_action(metrics, "audit_true_best") == 21


def test_choose_execution_action_supports_margin_true_reward_guard():
    metrics = {
        "selected_action": 22,
        "selected_true_reward": 1.0,
        "audit_best_action": 21,
        "audit_best_true_reward": 2.4,
    }

    assert (
        choose_execution_action(
            metrics,
            "margin_true_reward_guard",
            true_reward_switch_margin=1.5,
        )
        == 22
    )
    assert (
        choose_execution_action(
            metrics,
            "margin_true_reward_guard",
            true_reward_switch_margin=1.0,
        )
        == 21
    )
