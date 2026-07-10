from paper10_geojepa_mpc.experiments.pcc_information_set_audit import (
    audit_information_set,
)


def test_information_audit_accepts_complete_no_oracle_episode():
    payload = {
        "registry_digest": "registry",
        "seed_results": [
            {
                "seed": 4000,
                "environment_step_count": 2,
                "steps": [
                    {"action": 1, "unexecuted_real_reward_queries": 0},
                    {"action": 2, "unexecuted_real_reward_queries": 0},
                ],
            }
        ],
    }

    report = audit_information_set(payload, expected_registry_digest="registry")

    assert report["passed"] is True
    assert report["unexecuted_real_reward_queries"] == 0


def test_information_audit_rejects_unexecuted_query_and_step_mismatch():
    payload = {
        "registry_digest": "registry",
        "seed_results": [
            {
                "seed": 4000,
                "environment_step_count": 2,
                "steps": [
                    {"action": 1, "unexecuted_real_reward_queries": 1},
                ],
            }
        ],
    }

    report = audit_information_set(payload, expected_registry_digest="registry")

    assert report["passed"] is False
    assert "unexecuted_real_reward_query" in report["failure_reasons"]
    assert "environment_step_count_mismatch" in report["failure_reasons"]
