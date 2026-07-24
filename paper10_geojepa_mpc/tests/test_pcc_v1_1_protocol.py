from copy import deepcopy
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)


REGISTRY = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "protocols"
    / "pcc_v1_1.json"
)
ROOT = Path(__file__).resolve().parents[2]


def test_pcc_protocol_registry_line_endings_are_digest_stable():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert (
        "paper10_geojepa_mpc/experiments/protocols/*.json text eol=lf"
        in attributes.splitlines()
    )


def test_pcc_v1_1_locks_source_protocol_and_selected_risk_contract():
    payload = load_registry(REGISTRY)
    validate_registry(payload)

    assert payload["protocol_id"] == "pcc_v1_1"
    assert payload["status"] == "development"
    assert payload["source_inputs"]["protocol_id"] == "pcc_v1"
    assert payload["selected_conformal"]["score"] == (
        "one_sided_selected_trajectory_planning_max"
    )
    assert payload["selected_conformal"]["objectives"] == [
        "slope_benefit",
        "contiguity_benefit",
        "connected_area_benefit",
    ]
    assert payload["compute_modes"] == {
        "matched": "floor(50 / ensemble_size)",
        "full": 50,
    }
    assert payload["viability"]["development_seeds"] == list(range(3000, 3010))
    assert payload["viability"]["states_per_trajectory"] == 20


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("source_inputs", "protocol_id"), "pcc_v1_1"),
        (("viability", "minimum_nonfallback_rate"), 0.0),
        (("viability", "minimum_action_difference_rate"), 0.0),
        (("selected_conformal", "score"), "absolute_all_candidate_max"),
    ],
)
def test_pcc_v1_1_rejects_scientific_contract_mutation(path, value):
    payload = deepcopy(load_registry(REGISTRY))
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    with pytest.raises(ValueError, match="pcc_v1_1"):
        validate_registry(payload)


def test_pcc_v1_locked_contract_remains_unchanged():
    legacy = load_registry()
    validate_registry(legacy)

    assert legacy["protocol_id"] == "pcc_v1"
