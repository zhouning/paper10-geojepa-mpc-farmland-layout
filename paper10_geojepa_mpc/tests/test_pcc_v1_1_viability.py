import json
from importlib import import_module
from pathlib import Path

import numpy as np
import pytest


def _viability():
    return import_module(
        "paper10_geojepa_mpc.experiments.pcc_v1_1_viability"
    )


def _contract(coverage: float = 0.9) -> dict[str, object]:
    return {
        "coverage": float(coverage),
        "minimum_nonfallback_rate": 0.1,
        "minimum_action_difference_rate": 0.1,
        "minimum_reward_delta": 0.0,
        "minimum_planning_delta": 0.0,
        "minimum_supporting_model_seeds": 2,
    }


def _rows_for_seed(
    model_seed: int,
    *,
    certificate_passed: bool,
    action_differs: bool,
    reward_delta: float,
    planning_delta=(0.1, 0.1, 0.1),
    covered: bool = True,
) -> list[dict[str, object]]:
    rows = []
    for offset in range(3):
        rows.append(
            {
                "model_seed": int(model_seed),
                "trajectory_seed": 3000 + offset,
                "certificate_passed": bool(certificate_passed),
                "action_differs": bool(action_differs),
                "reward_delta": float(reward_delta),
                "planning_delta": list(map(float, planning_delta)),
                "covered": bool(covered),
                "uncertainty": float(offset + 1),
                "absolute_error": float(offset + 1),
                "fallback_reason": (
                    None if certificate_passed else "planning_certificate_rejected"
                ),
                "base_selection_reason": "reward_mean_among_mean_safe",
                "unexecuted_real_reward_queries": 0,
            }
        )
    return rows


def test_all_fallback_pilot_is_ineligible_even_with_perfect_planning():
    viability = _viability()
    rows = []
    for model_seed in (5101, 5102, 5103):
        rows.extend(
            _rows_for_seed(
                model_seed,
                certificate_passed=False,
                action_differs=False,
                reward_delta=0.0,
                planning_delta=(0.0, 0.0, 0.0),
                covered=True,
            )
        )

    report = viability.evaluate_viability(rows, contract=_contract())

    assert report["passed"] is False
    assert "minimum_nonfallback_rate" in report["failed_gates"]
    assert "minimum_action_difference_rate" in report["failed_gates"]
    assert "positive_reward_delta" in report["failed_gates"]


def test_highest_coverage_passing_every_gate_is_selected():
    viability = _viability()
    reports = {
        0.80: {"passed": True, "coverage": 0.80},
        0.90: {"passed": True, "coverage": 0.90},
        0.95: {
            "passed": False,
            "coverage": 0.95,
            "failed_gates": ["trajectory_coverage"],
        },
    }

    selected = viability.select_viable_coverage(
        reports,
        declared=(0.80, 0.90, 0.95),
    )

    assert selected == 0.90


def test_pilot_requires_two_supporting_model_seeds():
    viability = _viability()
    rows = []
    for model_seed, supported in {
        5101: True,
        5102: False,
        5103: False,
    }.items():
        rows.extend(
            _rows_for_seed(
                model_seed,
                certificate_passed=True,
                action_differs=True,
                reward_delta=1.0 if supported else -1.0,
            )
        )

    report = viability.evaluate_viability(rows, contract=_contract())

    assert report["passed"] is False
    assert report["supporting_model_seeds"] == [5101]
    assert "minimum_supporting_model_seeds" in report["failed_gates"]


def test_any_unexecuted_real_reward_query_fails_the_whole_pilot():
    viability = _viability()
    rows = []
    for model_seed in (5101, 5102, 5103):
        rows.extend(
            _rows_for_seed(
                model_seed,
                certificate_passed=True,
                action_differs=True,
                reward_delta=1.0,
            )
        )
    rows[0]["unexecuted_real_reward_queries"] = 1

    report = viability.evaluate_viability(rows, contract=_contract())

    assert report["passed"] is False
    assert report["unexecuted_real_reward_queries"] == 1
    assert "zero_unexecuted_real_reward_queries" in report["failed_gates"]


def _development_lineage() -> dict[str, object]:
    return {
        "protocol_id": "pcc_v1_1",
        "registry_digest": "a" * 64,
        "partition": "development",
        "model_seed": 5101,
        "ensemble_size": 3,
        "policy_round": 1,
        "compute_mode": "matched",
        "checkpoint_digests": ["b" * 64, "c" * 64, "d" * 64],
        "candidate_generator_digest": "e" * 64,
        "base_selector_digest": "f" * 64,
        "reference_checkpoint_digest": "9" * 64,
    }


def _development_dataset(seed: int, *, queries: int = 0):
    true = np.zeros((2, 3, 4), dtype=np.float32)
    predicted = np.zeros_like(true)
    true[0, 1] = [0.5, 0.2, 0.2, 0.2]
    predicted[0, 1] = true[0, 1]
    return {
        "selected_actions": np.array([2, 1], dtype=np.int64),
        "reference_actions": np.array([1, 1], dtype=np.int64),
        "predicted_delta": predicted,
        "predicted_scale": np.concatenate(
            [
                np.full((1, 3, 4), 0.1, dtype=np.float32),
                np.zeros((1, 3, 4), dtype=np.float32),
            ],
            axis=0,
        ),
        "true_delta": true,
        "executable_probability": np.ones(2, dtype=np.float32),
        "base_selection_reason": np.array(
            ["reward_mean_among_mean_safe", "reference_reward_dominates"],
            dtype="U64",
        ),
        "state_steps": np.array([0, 1], dtype=np.int64),
        "trajectory_ids": np.full(2, seed, dtype=np.int64),
        "continuation_seeds": np.array([11, 12], dtype=np.uint64),
        "unexecuted_real_reward_queries": np.array(
            [queries, 0], dtype=np.int64
        ),
    }


def _write_development_fixture(root: Path, *, queries: int = 0):
    labels = import_module(
        "paper10_geojepa_mpc.experiments.pcc_v1_1_selected_labels"
    )
    conformal = import_module(
        "paper10_geojepa_mpc.planning.selected_conformal"
    )
    artifacts = [
        labels.write_selected_trajectory_artifact(
            root,
            seed,
            _development_dataset(seed, queries=queries),
        )
        for seed in (3000, 3001)
    ]
    manifest = labels.write_selected_manifest(
        root,
        lineage=_development_lineage(),
        artifacts=artifacts,
    )
    calibrator = conformal.fit_selected_planning_calibrator(
        trajectory_scores=[0.0, 0.0],
        trajectory_ids=[2000, 2001],
        coverage=0.8,
        lineage={
            "planning_horizon": 3,
            "model_seed": 5101,
            "ensemble_size": 3,
            "policy_round": 1,
            "compute_mode": "matched",
            "checkpoint_digests": _development_lineage()[
                "checkpoint_digests"
            ],
            "selected_labels_manifest_digest": "8" * 64,
            "candidate_generator_digest": "e" * 64,
            "base_selector_digest": "f" * 64,
        },
    )
    calibrator_path = root / "calibrator.json"
    conformal.save_selected_planning_calibrator(calibrator_path, calibrator)
    return root / "manifest.json", manifest, calibrator_path


def test_development_loader_derives_certificate_and_reference_fallback(tmp_path):
    viability = _viability()
    manifest_path, manifest, calibrator_path = _write_development_fixture(
        tmp_path / "development"
    )

    rows = viability.load_development_rows(
        manifest_path,
        calibrator_path,
        expected_lineage=_development_lineage(),
        expected_coverage=0.8,
        expected_planning_horizon=3,
        expected_trajectory_seeds=(3000, 3001),
    )

    assert len(rows) == 4
    assert [row["certificate_passed"] for row in rows] == [
        True,
        False,
        True,
        False,
    ]
    assert rows[1]["fallback_reason"] == "reference_reward_dominates"
    assert all(row["selected_manifest_digest"] == manifest["manifest_digest"] for row in rows)


def test_development_loader_rejects_unexecuted_real_reward_query(tmp_path):
    viability = _viability()
    manifest_path, _, calibrator_path = _write_development_fixture(
        tmp_path / "development",
        queries=1,
    )

    with pytest.raises(ValueError, match="unexecuted real-reward"):
        viability.load_development_rows(
            manifest_path,
            calibrator_path,
            expected_lineage=_development_lineage(),
            expected_coverage=0.8,
            expected_planning_horizon=3,
            expected_trajectory_seeds=(3000, 3001),
        )


def test_viability_outputs_are_deterministic_and_complete(tmp_path):
    viability = _viability()
    rows = []
    for model_seed in (5101, 5102, 5103):
        rows.extend(
            _rows_for_seed(
                model_seed,
                certificate_passed=True,
                action_differs=True,
                reward_delta=1.0,
            )
        )
    report = viability.evaluate_viability(rows, contract=_contract(0.8))
    payload = viability.build_closeout_payload(
        registry_digest="a" * 64,
        reports={0.8: report},
        declared_coverages=(0.8,),
        input_digests=[
            {"kind": "selected_development", "sha256": "b" * 64}
        ],
    )
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"

    viability.write_viability_outputs(output_json, output_md, payload)
    first_json = output_json.read_bytes()
    first_md = output_md.read_bytes()
    viability.write_viability_outputs(output_json, output_md, payload)

    assert output_json.read_bytes() == first_json
    assert output_md.read_bytes() == first_md
    loaded = json.loads(first_json)
    assert loaded["status"] == "viable"
    markdown = first_md.decode("utf-8")
    assert "minimum_supporting_model_seeds" in markdown
    assert "5101" in markdown
    assert "3000" in markdown
    assert "b" * 64 in markdown
    assert "reward_mean_among_mean_safe" in markdown


def test_closeout_cli_serializes_scientific_failure_with_zero_exit(
    tmp_path,
    monkeypatch,
):
    viability = _viability()
    registry = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "protocols"
        / "pcc_v1_1.json"
    )

    def fake_inputs(**kwargs):
        rows = []
        for model_seed in (5101, 5102, 5103):
            rows.extend(
                _rows_for_seed(
                    model_seed,
                    certificate_passed=False,
                    action_differs=False,
                    reward_delta=0.0,
                    planning_delta=(0.0, 0.0, 0.0),
                )
            )
        return rows, [
            {
                "kind": "fixture",
                "coverage": kwargs["coverage"],
                "sha256": "b" * 64,
            }
        ]

    monkeypatch.setattr(viability, "_load_coverage_inputs", fake_inputs)
    result = viability.main(
        [
            "--registry",
            str(registry),
            "--selected-development-root",
            str(tmp_path / "development"),
            "--calibrator-root",
            str(tmp_path / "calibrators"),
            "--coverages",
            "0.80,0.90,0.95",
            "--output-json",
            str(tmp_path / "closeout.json"),
            "--output-md",
            str(tmp_path / "closeout.md"),
        ]
    )

    assert result["passed"] is False
    assert result["status"] == "scientific_failure"
    assert result["selected_coverage"] is None
    assert (tmp_path / "closeout.json").is_file()
    assert (tmp_path / "closeout.md").is_file()
