import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    freeze_registry,
    load_registry,
    validate_registry,
    verify_frozen_registry,
)


def test_registry_rejects_partition_overlap():
    payload = {
        "protocol_id": "pcc_v1",
        "status": "development",
        "partitions": {
            "train": [1000],
            "calibration": [1000],
            "development": [3000],
            "confirmation": [4000],
        },
        "model_seeds": [5101, 5102, 5103],
    }

    with pytest.raises(ValueError, match="overlap"):
        validate_registry(payload)


def test_registry_rejects_model_seed_used_as_data_seed():
    payload = load_registry()
    payload["model_seeds"][0] = payload["partitions"]["train"][0]

    with pytest.raises(ValueError, match="model seed overlaps"):
        validate_registry(payload)


def test_pcc_v1_rejects_any_change_to_locked_seed_namespaces():
    payload = load_registry()
    payload["partitions"]["confirmation"] = payload["partitions"]["confirmation"][:-1]

    with pytest.raises(ValueError, match="locked partition mismatch"):
        validate_registry(payload)


def test_registry_contains_locked_scientific_contract():
    payload = load_registry()

    assert payload["online_information_set"]["unexecuted_real_reward_queries"] == 0
    assert payload["compute_budget"]["single_model_candidate_equivalents"] == 50
    assert payload["success_gates"]["minimum_jointly_supporting_model_seeds"] == 2
    assert payload["success_gates"]["bishan"]["reward_lower_bound_strictly_positive"] is True
    assert payload["success_gates"]["dongxing"]["reward_lower_bound_minimum"] == 0.0
    assert "oracle_action_audit_diagnostic" not in payload["deployable_baselines"]
    assert payload["offline_sampling"]["train"] == {
        "states_per_trajectory": 20,
        "candidate_actions": 8,
    }
    assert payload["offline_sampling"]["calibration"] == {
        "states_per_trajectory": 10,
        "candidate_actions": 8,
    }
    assert payload["offline_reference_policy"]["planning_horizon"] == 5
    assert payload["offline_reference_policy"]["top_k"] == 50
    assert len(payload["offline_reference_policy"]["checkpoint_sha256"]) == 64


def test_pcc_v1_rejects_missing_locked_scientific_contract():
    payload = load_registry()
    del payload["online_information_set"]

    with pytest.raises(ValueError, match="scientific contract"):
        validate_registry(payload)


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (
            lambda payload: payload["online_information_set"].__setitem__(
                "unexecuted_real_reward_queries", 1
            ),
            "scientific contract",
        ),
        (
            lambda payload: payload["grid"]["joint_coverage"].append(0.99),
            "scientific contract",
        ),
        (
            lambda payload: payload["compute_budget"].__setitem__(
                "single_model_candidate_equivalents", 100
            ),
            "scientific contract",
        ),
    ],
)
def test_pcc_v1_rejects_changes_to_locked_scientific_values(mutate, match):
    payload = load_registry()
    mutate(payload)

    with pytest.raises(ValueError, match=match):
        validate_registry(payload)


def test_frozen_registry_has_stable_digest_and_cannot_be_refrozen(tmp_path: Path):
    source = tmp_path / "registry.json"
    source.write_text(json.dumps(load_registry()), encoding="utf-8")

    frozen = freeze_registry(source, selected_config={"ensemble_size": 3})

    assert frozen["status"] == "frozen"
    assert len(frozen["frozen_digest"]) == 64
    assert verify_frozen_registry(load_registry(source)) == frozen["frozen_digest"]
    with pytest.raises(ValueError, match="already frozen"):
        freeze_registry(source, selected_config={"ensemble_size": 5})


def test_frozen_registry_verification_detects_scientific_mutation(tmp_path: Path):
    source = tmp_path / "registry.json"
    source.write_text(json.dumps(load_registry()), encoding="utf-8")
    frozen = freeze_registry(source, selected_config={"ensemble_size": 3})
    frozen["selected_config"]["ensemble_size"] = 5

    with pytest.raises(ValueError, match="digest mismatch"):
        verify_frozen_registry(frozen)
