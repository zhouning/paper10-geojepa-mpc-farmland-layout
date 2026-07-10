import json

from paper10_geojepa_mpc.experiments.pcc_information_set_audit import (
    audit_information_set,
    audit_rollout_directory,
    main,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
)


def _frozen_registry(tmp_path):
    path = tmp_path / "pcc_v1.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")
    return path, freeze_registry(path, selected_config={"id": "fixture"})


def _rollout_payload(registry_digest, policy="paper9_mpc", seed=4000):
    return {
        "registry_digest": registry_digest,
        "checkpoint_digests": ["a" * 64],
        "seed_results": [
            {
                "seed": seed,
                "policy": policy,
                "model_seed": 5101,
                "environment_step_count": 1,
                "steps": [
                    {"action": 1, "unexecuted_real_reward_queries": 0}
                ],
            }
        ],
    }


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


def test_directory_audit_rejects_duplicate_policy_model_rollout_seed(tmp_path):
    _, registry = _frozen_registry(tmp_path)
    root = tmp_path / "rollouts"
    root.mkdir()
    payload = _rollout_payload(registry["frozen_digest"])
    (root / "first.json").write_text(json.dumps(payload), encoding="utf-8")
    (root / "second.json").write_text(json.dumps(payload), encoding="utf-8")

    report = audit_rollout_directory(root, registry=registry)

    assert report["passed"] is False
    assert "duplicate_policy_model_rollout_seed" in report["failure_reasons"]


def test_information_audit_cli_excludes_declared_diagnostic_and_writes_reports(
    tmp_path,
):
    registry_path, registry = _frozen_registry(tmp_path)
    root = tmp_path / "rollouts"
    root.mkdir()
    (root / "deployable.json").write_text(
        json.dumps(_rollout_payload(registry["frozen_digest"])),
        encoding="utf-8",
    )
    (root / "oracle.json").write_text(
        json.dumps(
            _rollout_payload(
                registry["frozen_digest"],
                policy="oracle_action_audit_diagnostic",
            )
        ),
        encoding="utf-8",
    )
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"

    main(
        [
            "--registry",
            str(registry_path),
            "--input-root",
            str(root),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ]
    )

    report = json.loads(output_json.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["audited_seed_results"] == 1
    assert report["excluded_diagnostic_seed_results"] == 1
    assert "Overall pass: `True`" in output_md.read_text(encoding="utf-8")
