import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    DEFAULT_REGISTRY,
    load_registry,
)
from paper10_geojepa_mpc.experiments.pcc_ablations import ABLATION_CONTRACTS
from paper10_geojepa_mpc.experiments.run_pcc_development import (
    aggregate_development_rung,
    aggregate_primary_comparators,
    binomial_acceptance_interval,
    build_rung_jobs,
    build_development_schedule,
    development_row,
    enumerate_grid,
    execute_development_job,
    freeze_development,
    main,
    retain_configurations,
    select_primary_comparator,
    select_configuration,
    stage_a_gate,
    stage_a_report_from_payloads,
    validate_ablation_inventory,
    validate_resumable_development_job,
)


def test_grid_contains_only_registry_declared_values():
    registry = load_registry()

    rows = enumerate_grid(registry["grid"])

    assert len(rows) == 144
    assert {row["ensemble_size"] for row in rows} == {3, 5}


def test_selection_prioritizes_planning_gates_then_reward_then_compute():
    rows = [
        {"id": "reward_only", "planning_gate_count": 2, "reward": 5.0, "compute": 10},
        {"id": "safe_slow", "planning_gate_count": 3, "reward": 1.0, "compute": 20},
        {"id": "safe_fast", "planning_gate_count": 3, "reward": 1.0, "compute": 10},
    ]

    assert select_configuration(rows)["id"] == "safe_fast"


def test_development_bootstrap_resamples_rollout_seeds_not_model_seed_pairs():
    rollout_effects = {-2: -2.0, 0: 0.0, 3: 3.0}
    model_offsets = {5101: -0.5, 5102: 0.0, 5103: 0.5}
    rows = []
    for seed, seed_effect in rollout_effects.items():
        for model_seed, model_offset in model_offsets.items():
            effect = seed_effect + model_offset
            rows.extend(
                [
                    {
                        "policy": "pcc_matched",
                        "model_seed": model_seed,
                        "seed": seed,
                        "objective_outcome": [effect] * 4,
                        "steps": [{"member_evaluations": 3}],
                    },
                    {
                        "policy": "paper9_mpc",
                        "model_seed": model_seed,
                        "seed": seed,
                        "objective_outcome": [0.0] * 4,
                        "steps": [],
                    },
                ]
            )
    draws = 2000
    bootstrap_seed = 17
    rng = np.random.default_rng(bootstrap_seed)
    seed_values = np.asarray(list(rollout_effects.values()), dtype=float)
    indexes = rng.integers(0, len(seed_values), size=(draws, len(seed_values)))
    expected_lower = float(np.quantile(seed_values[indexes].mean(axis=1), 0.05))

    result = development_row(
        {
            "id": "config",
            "policy": "pcc_matched",
            "primary_candidate": "paper9_mpc",
            "development_bootstrap_seed": bootstrap_seed,
        },
        rows,
        draws=draws,
    )

    np.testing.assert_allclose(result["lower_95_one_sided"], [expected_lower] * 4)
    assert result["bootstrap_rollout_seeds"] == 3
    assert result["paired_observations"] == 9


def test_stage_a_requires_positive_uncertainty_error_association_and_coverage():
    lower, upper = binomial_acceptance_interval(20, 0.9)
    covered = min(max(18, lower), upper)

    passing = stage_a_gate(
        uncertainty=np.arange(20, dtype=float),
        absolute_error=np.arange(20, dtype=float),
        covered_trajectories=covered,
        n_trajectories=20,
        nominal_coverage=0.9,
    )
    failing = stage_a_gate(
        uncertainty=np.arange(20, dtype=float),
        absolute_error=np.arange(20, 0, -1, dtype=float),
        covered_trajectories=covered,
        n_trajectories=20,
        nominal_coverage=0.9,
    )

    assert passing["passed"] is True
    assert failing["passed"] is False


def test_stage_a_report_uses_only_executed_action_predictions():
    payloads = {}
    for model_seed in (5101, 5102, 5103):
        payloads[str(model_seed)] = {
            "seed_results": [
                {
                    "model_seed": model_seed,
                    "seed": seed,
                    "steps": [
                        {
                            "observed_outcome": [scale * 0.5] * 4,
                            "selected_predicted_mean": [0.0] * 4,
                            "selected_base_scale": [scale] * 4,
                            "joint_q": 1.0,
                            "unexecuted_real_reward_queries": 0,
                        }
                    ],
                }
                for seed, scale in zip(range(3000, 3005), range(1, 6))
            ]
        }

    report = stage_a_report_from_payloads(
        payloads,
        model_seeds=(5101, 5102, 5103),
        seeds=tuple(range(3000, 3005)),
        nominal_coverage=0.9,
    )

    assert report["passed"] is True
    assert report["n_trajectories"] == 5
    assert report["covered_trajectories"] == 5
    assert report["unexecuted_real_reward_queries"] == 0


def test_primary_comparator_selection_excludes_pcc_and_oracle():
    rows = [
        {"id": "paper9_mpc", "planning_gate_count": 3, "reward": 0.0, "compute": 0},
        {
            "id": "distributional_risk",
            "planning_gate_count": 3,
            "reward": 1.0,
            "compute": 50,
        },
    ]

    selected = select_primary_comparator(
        rows,
        candidates=("paper9_mpc", "distributional_risk"),
    )

    assert selected["id"] == "distributional_risk"
    with pytest.raises(ValueError, match="candidate set"):
        select_primary_comparator(
            rows,
            candidates=("paper9_mpc", "pcc_matched"),
        )


def test_baseline_aggregation_maps_shared_blocks_without_extra_rows():
    jobs = []
    payloads = {}
    for policy, model_seeds in (
        ("paper9_mpc", (5101,)),
        ("distributional_risk", (5101, 5102, 5103)),
    ):
        for model_seed in model_seeds:
            job_id = f"{policy}-{model_seed}"
            jobs.append(
                {
                    "id": job_id,
                    "phase": "baseline_selection",
                    "policy": policy,
                    "model_seed": model_seed,
                }
            )
            payloads[job_id] = {
                "seed_results": [
                    {
                        "policy": policy,
                        "model_seed": model_seed,
                        "seed": seed,
                        "objective_outcome": [
                            2.0 if policy == "distributional_risk" else 1.0,
                            0.2,
                            0.3,
                            0.4,
                        ],
                        "steps": [{"member_evaluations": 3}],
                    }
                    for seed in (3000, 3001)
                ]
            }

    rows = aggregate_primary_comparators(
        jobs=jobs,
        payloads=payloads,
        candidates=("paper9_mpc", "distributional_risk"),
        model_seeds=(5101, 5102, 5103),
        seeds=(3000, 3001),
        draws=100,
        bootstrap_seed=7,
    )

    selected = select_primary_comparator(
        rows,
        candidates=("paper9_mpc", "distributional_risk"),
    )
    assert selected["id"] == "distributional_risk"
    assert selected["paired_observations"] == 6
    assert selected["compute_unit"] == "mean_member_evaluations_per_step"
    assert selected["compute"] == 3.0


def _complete_ablation_inventory(
    artifact_root,
    registry_digest="r" * 64,
    winner="winner",
    ensemble_size=3,
):
    registry = load_registry()
    artifact_root = Path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "registry_digest": registry_digest,
        "selected_configuration_id": winner,
        "model_seeds": registry["model_seeds"],
        "source_seeds": registry["partitions"]["development"],
        "ablations": {},
    }
    for index, name in enumerate(registry["required_ablations"], start=1):
        ablation_ensemble_size = 1 if name == "single_model" else ensemble_size
        checkpoint_digests_by_model = {
            str(model_seed): [
                f"{index:02x}{model_seed:04x}{member_index:02x}".ljust(64, "0")
                for member_index in range(ablation_ensemble_size)
            ]
            for model_seed in registry["model_seeds"]
        }
        calibrator_digests_by_model = {
            str(model_seed): f"{index:02x}{model_seed:04x}".ljust(64, "f")
            for model_seed in registry["model_seeds"]
        }
        artifact = {
            "schema_version": 1,
            "registry_digest": registry_digest,
            "selected_configuration_id": winner,
            "ablation": name,
            "checkpoint_digests_by_model": checkpoint_digests_by_model,
            "calibrator_digests_by_model": calibrator_digests_by_model,
            "seed_results": [
                {
                    "model_seed": model_seed,
                    "seed": seed,
                    "objective_outcome": [1.0, 0.2, 0.3, 0.4],
                    "steps": [{"unexecuted_real_reward_queries": 0}],
                }
                for model_seed in registry["model_seeds"]
                for seed in registry["partitions"]["development"]
            ],
        }
        artifact_path = artifact_root / f"{name}.json"
        artifact_path.write_text(
            json.dumps(artifact, sort_keys=True),
            encoding="utf-8",
        )
        payload["ablations"][name] = {
            "complete": True,
            "overlay": dict(ABLATION_CONTRACTS[name].overlay),
            "model_seeds": registry["model_seeds"],
            "source_seeds": registry["partitions"]["development"],
            "paired_observations": 30,
            "artifact_path": str(artifact_path),
            "artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
            "checkpoint_digests_by_model": checkpoint_digests_by_model,
            "calibrator_digests_by_model": calibrator_digests_by_model,
        }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    payload["inventory_digest"] = hashlib.sha256(canonical).hexdigest()
    return payload


def _reseal_ablation_artifact(payload, name, artifact):
    row = payload["ablations"][name]
    artifact_path = Path(row["artifact_path"])
    artifact_path.write_text(
        json.dumps(artifact, sort_keys=True),
        encoding="utf-8",
    )
    row["artifact_sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    clean = {key: value for key, value in payload.items() if key != "inventory_digest"}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    payload["inventory_digest"] = hashlib.sha256(canonical).hexdigest()


def test_ablation_inventory_requires_digest_bound_complete_mechanism_blocks(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)

    digest = validate_ablation_inventory(
        payload,
        registry=load_registry(),
        selected_config={"id": "winner", "ensemble_size": 3},
        registry_digest="r" * 64,
    )

    assert digest == payload["inventory_digest"]
    del payload["ablations"]["single_model"]
    with pytest.raises(ValueError, match="ablation set"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_rejects_missing_physical_artifact(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)
    Path(payload["ablations"]["single_model"]["artifact_path"]).unlink()

    with pytest.raises(FileNotFoundError, match="ablation artifact"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_rejects_incomplete_physical_pair_block(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)
    name = "single_model"
    artifact_path = Path(payload["ablations"][name]["artifact_path"])
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["seed_results"].pop()
    _reseal_ablation_artifact(payload, name, artifact)

    with pytest.raises(ValueError, match="physical paired block"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_rejects_nonfinite_physical_objectives(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)
    name = "single_model"
    artifact_path = Path(payload["ablations"][name]["artifact_path"])
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["seed_results"][0]["objective_outcome"] = [1.0, 0.2, np.nan, 0.4]
    _reseal_ablation_artifact(payload, name, artifact)

    with pytest.raises(ValueError, match="four finite objectives"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_rejects_unexecuted_reward_queries(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)
    name = "single_model"
    artifact_path = Path(payload["ablations"][name]["artifact_path"])
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["seed_results"][0]["steps"][0]["unexecuted_real_reward_queries"] = 1
    _reseal_ablation_artifact(payload, name, artifact)

    with pytest.raises(ValueError, match="unexecuted real-reward queries"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_requires_complete_checkpoint_calibrator_lineage(tmp_path):
    payload = _complete_ablation_inventory(tmp_path)
    name = "single_model"
    payload["ablations"][name]["checkpoint_digests_by_model"].pop("5103")
    clean = {key: value for key, value in payload.items() if key != "inventory_digest"}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    payload["inventory_digest"] = hashlib.sha256(canonical).hexdigest()

    with pytest.raises(ValueError, match="lineage mapping"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_ablation_inventory_requires_mechanism_specific_member_count(tmp_path):
    payload = _complete_ablation_inventory(tmp_path, ensemble_size=3)
    name = "no_aleatoric_scale"
    artifact_path = Path(payload["ablations"][name]["artifact_path"])
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    payload["ablations"][name]["checkpoint_digests_by_model"]["5101"].pop()
    artifact["checkpoint_digests_by_model"]["5101"].pop()
    _reseal_ablation_artifact(payload, name, artifact)

    with pytest.raises(ValueError, match="checkpoint member count"):
        validate_ablation_inventory(
            payload,
            registry=load_registry(),
            selected_config={"id": "winner", "ensemble_size": 3},
            registry_digest="r" * 64,
        )


def test_successive_halving_never_uses_confirmation_seeds():
    registry = load_registry()

    schedule = build_development_schedule(registry)

    assert schedule[0].seeds == (3000, 3001)
    assert schedule[0].steps == 20
    assert schedule[0].keep == 144
    assert schedule[1].keep == 36
    assert schedule[1].seeds == tuple(range(3000, 3005))
    assert schedule[1].steps == 50
    assert schedule[2].keep == 8
    assert schedule[2].seeds == tuple(range(3000, 3010))
    assert schedule[2].steps == 100
    assert not set().union(*(set(row.seeds) for row in schedule)) & set(
        registry["partitions"]["confirmation"]
    )


class _FakeInventory:
    def checkpoint_root(self, model_seed, ensemble_size, policy_round):
        return Path(
            f"checkpoints/seed-{model_seed}/k-{ensemble_size}/round-{policy_round}"
        )

    def checkpoint_digests(self, model_seed, ensemble_size, policy_round):
        return tuple(
            f"{model_seed:04d}{ensemble_size}{policy_round}{index}".ljust(64, "0")
            for index in range(ensemble_size)
        )

    def calibrator(
        self,
        model_seed,
        ensemble_size,
        policy_round,
        coverage,
    ):
        return Path(
            "calibration"
            f"/seed-{model_seed}/k-{ensemble_size}/round-{policy_round}"
            f"/coverage-{coverage}.json"
        )

    def calibrator_digest(
        self,
        model_seed,
        ensemble_size,
        policy_round,
        coverage,
    ):
        return hashlib.sha256(
            f"{model_seed}/{ensemble_size}/{policy_round}/{coverage}".encode()
        ).hexdigest()


def test_development_dry_run_writes_single_policy_worker_commands(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.build_inventory",
        lambda *args, **kwargs: _FakeInventory(),
    )

    main(
        [
            "--registry",
            str(DEFAULT_REGISTRY),
            "--checkpoint-root",
            str(tmp_path / "checkpoints"),
            "--calibration-root",
            str(tmp_path / "calibration"),
            "--prepared-dir",
            str(tmp_path),
            "--output-dir",
            str(tmp_path / "development"),
            "--dry-run",
        ]
    )

    plan = json.loads(
        (tmp_path / "development" / "execution_plan.json").read_text()
    )
    assert plan["rungs"][0]["seeds"] == [3000, 3001]
    assert plan["jobs"]
    assert plan["phase"] == "pre_grid"
    assert set(plan["baseline_candidates"]) == set(
        load_registry()["development_baseline_anchor"]["candidates"]
    )
    assert all(row["phase"] in {"stage_a", "baseline_selection"} for row in plan["jobs"])
    assert plan["grid_jobs_pending_primary_comparator"] is True
    assert len({row["id"] for row in plan["jobs"]}) == len(plan["jobs"])
    assert all("--model-seed" in row["command"] for row in plan["jobs"])
    assert all("--model-seeds" not in row["command"] for row in plan["jobs"])
    assert all(row["command"].count("--policy") == 1 for row in plan["jobs"])
    assert all("--mode" in row["command"] for row in plan["jobs"])
    assert all(
        row["command"][row["command"].index("--mode") + 1] == "development"
        for row in plan["jobs"]
    )


def test_development_cli_executes_all_three_successive_halving_rungs(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.build_inventory",
        lambda *args, **kwargs: _FakeInventory(),
    )

    preferred_configuration = None
    seen_configurations = []

    def fake_execute(job, **kwargs):
        policy = job["policy"]
        nonlocal preferred_configuration, seen_configurations
        if (
            policy == "pcc_matched"
            and job.get("phase") != "stage_a"
            and job["configuration_id"] not in seen_configurations
        ):
            seen_configurations.append(job["configuration_id"])
            if len(seen_configurations) == 2:
                preferred_configuration = job["configuration_id"]
        policy_reward = (
            3.0
            if job["configuration_id"] == preferred_configuration
            else 2.0
        )
        return {
            "seed_results": [
                {
                    "policy": policy,
                    "model_seed": job["model_seed"],
                    "seed": seed,
                    "objective_outcome": [
                        policy_reward if policy == "pcc_matched" else 1.0,
                        0.2,
                        0.3,
                        0.4,
                    ],
                    "steps": [
                        {
                            "member_evaluations": 3,
                            **(
                                {
                                    "observed_outcome": [0.5 * (index + 1)] * 4,
                                    "selected_predicted_mean": [0.0] * 4,
                                    "selected_base_scale": [float(index + 1)] * 4,
                                    "joint_q": 1.0,
                                    "unexecuted_real_reward_queries": 0,
                                }
                                if job.get("phase") == "stage_a"
                                else {}
                            ),
                        }
                        for index in range(job["rollout_steps"])
                    ],
                }
                for seed in job["seeds"]
            ]
        }

    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.execute_development_job",
        fake_execute,
    )

    main(
        [
            "--registry",
            str(DEFAULT_REGISTRY),
            "--checkpoint-root",
            str(tmp_path / "checkpoints"),
            "--calibration-root",
            str(tmp_path / "calibration"),
            "--prepared-dir",
            str(tmp_path),
            "--output-dir",
            str(tmp_path / "development"),
            "--bootstrap-draws",
            "100",
        ]
    )

    summary = json.loads(
        (tmp_path / "development" / "development_summary.json").read_text()
    )
    assert [row["evaluated"] for row in summary["rungs"]] == [144, 36, 8]
    assert [row["retained"] for row in summary["rungs"]] == [36, 8, 1]
    assert summary["winner"]["model_seeds"] == [5101, 5102, 5103]
    assert summary["winner"]["source_seeds"] == list(range(3000, 3010))
    assert summary["winner"]["id"] == preferred_configuration
    assert summary["stage_a_report"]["passed"] is True
    assert summary["primary_comparator"] in load_registry()[
        "development_baseline_anchor"
    ]["candidates"]


def test_freeze_cli_consumes_digest_bound_development_and_ablation_audits(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    inventory = _FakeInventory()
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.build_inventory",
        lambda *args, **kwargs: inventory,
    )

    def fake_execute(job, **kwargs):
        policy = job["policy"]
        return {
            "seed_results": [
                {
                    "policy": policy,
                    "model_seed": job["model_seed"],
                    "seed": seed,
                    "objective_outcome": [
                        2.0 if policy == "pcc_matched" else 1.0,
                        0.2,
                        0.3,
                        0.4,
                    ],
                    "steps": [
                        {
                            "member_evaluations": 3,
                            **(
                                {
                                    "observed_outcome": [float(index + 1)] * 4,
                                    "selected_predicted_mean": [0.0] * 4,
                                    "selected_base_scale": [float(index + 1)] * 4,
                                    "joint_q": 1.0,
                                    "unexecuted_real_reward_queries": 0,
                                }
                                if job.get("phase") == "stage_a"
                                else {}
                            ),
                        }
                        for index in range(job["rollout_steps"])
                    ],
                }
                for seed in job["seeds"]
            ]
        }

    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.execute_development_job",
        fake_execute,
    )
    output_dir = tmp_path / "development"
    ablations = _complete_ablation_inventory(
        tmp_path / "ablation-artifacts",
        registry_digest=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        winner="placeholder",
    )
    output_dir.mkdir()
    (output_dir / "ablation_inventory.json").write_text(
        json.dumps(ablations),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="selected configuration"):
        main(
            [
                "--registry",
                str(registry_path),
                "--checkpoint-root",
                str(tmp_path / "checkpoints"),
                "--calibration-root",
                str(tmp_path / "calibration"),
                "--prepared-dir",
                str(tmp_path),
                "--output-dir",
                str(output_dir),
                "--bootstrap-draws",
                "100",
                "--freeze",
            ]
        )


def test_freeze_cli_writes_per_model_lineage_after_valid_ablation_audit(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    inventory = _FakeInventory()
    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.build_inventory",
        lambda *args, **kwargs: inventory,
    )

    def fake_execute(job, **kwargs):
        policy = job["policy"]
        return {
            "seed_results": [
                {
                    "policy": policy,
                    "model_seed": job["model_seed"],
                    "seed": seed,
                    "objective_outcome": [
                        2.0 if policy == "pcc_matched" else 1.0,
                        0.2,
                        0.3,
                        0.4,
                    ],
                    "steps": [
                        {
                            "member_evaluations": 3,
                            **(
                                {
                                    "observed_outcome": [float(index + 1)] * 4,
                                    "selected_predicted_mean": [0.0] * 4,
                                    "selected_base_scale": [float(index + 1)] * 4,
                                    "joint_q": 1.0,
                                    "unexecuted_real_reward_queries": 0,
                                }
                                if job.get("phase") == "stage_a"
                                else {}
                            ),
                        }
                        for index in range(job["rollout_steps"])
                    ],
                }
                for seed in job["seeds"]
            ]
        }

    monkeypatch.setattr(
        "paper10_geojepa_mpc.experiments.run_pcc_development.execute_development_job",
        fake_execute,
    )
    output_dir = tmp_path / "development"
    output_dir.mkdir()
    common_args = [
        "--registry",
        str(registry_path),
        "--checkpoint-root",
        str(tmp_path / "checkpoints"),
        "--calibration-root",
        str(tmp_path / "calibration"),
        "--prepared-dir",
        str(tmp_path),
        "--output-dir",
        str(output_dir),
        "--bootstrap-draws",
        "100",
    ]
    main(common_args)
    winner = json.loads(
        (output_dir / "development_summary.json").read_text()
    )["winner"]
    payload = _complete_ablation_inventory(
        tmp_path / "ablation-artifacts",
        registry_digest=hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        winner=winner["id"],
        ensemble_size=winner["ensemble_size"],
    )
    (output_dir / "ablation_inventory.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    main([*common_args, "--resume", "--freeze"])

    selected = load_registry(registry_path)["selected_config"]
    assert len(selected["checkpoint_digests"]) == (
        3 * selected["ensemble_size"]
    )
    assert set(selected["calibrator_digest"]) == {"5101", "5102", "5103"}
    assert selected["completed_ablations"] == sorted(
        load_registry()["required_ablations"]
    )


def test_resume_requires_every_bound_job_identity(tmp_path):
    output = tmp_path / "rollout.json"
    output.write_text(
        json.dumps(
            {
                "registry_digest": "registry",
                "checkpoint_digests": ["member"],
                "seed_results": [
                    {
                        "seed": 3000,
                        "policy": "pcc_matched",
                        "model_seed": 5101,
                        "steps": [{}, {}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    metadata = tmp_path / "rollout.meta.json"
    metadata.write_text(
        json.dumps(
            {
                "registry_digest": "registry",
                "checkpoint_digests": ["member"],
                "calibrator_digest": "calibrator",
                "configuration_id": "config",
                "seeds": [3000],
                "rollout_steps": 2,
                "output_sha256": "ignored-by-fixture",
            }
        ),
        encoding="utf-8",
    )

    validate_resumable_development_job(
        output,
        metadata_path=metadata,
        registry_digest="registry",
        checkpoint_digests=("member",),
        calibrator_digest="calibrator",
        configuration_id="config",
        seeds=(3000,),
        rollout_steps=2,
        verify_output_digest=False,
    )

    with pytest.raises(ValueError, match="configuration"):
        validate_resumable_development_job(
            output,
            metadata_path=metadata,
            registry_digest="registry",
            checkpoint_digests=("member",),
            calibrator_digest="calibrator",
            configuration_id="changed",
            seeds=(3000,),
            rollout_steps=2,
            verify_output_digest=False,
        )

    with pytest.raises(ValueError, match="rollout length"):
        validate_resumable_development_job(
            output,
            metadata_path=metadata,
            registry_digest="registry",
            checkpoint_digests=("member",),
            calibrator_digest="calibrator",
            configuration_id="config",
            seeds=(3000,),
            rollout_steps=3,
            verify_output_digest=False,
        )


def test_job_metadata_exists_before_worker_and_binds_output_digest(tmp_path):
    output = tmp_path / "rollout.json"
    metadata = tmp_path / "rollout.meta.json"
    job = {
        "registry_digest": "registry",
        "checkpoint_digests": ["member"],
        "calibrator_digest": "calibrator",
        "configuration_id": "config",
        "seeds": [3000],
        "rollout_steps": 2,
        "output": str(output),
        "metadata": str(metadata),
        "command": ["worker"],
    }

    def fake_runner(command, **kwargs):
        assert command == ["worker"]
        assert metadata.exists()
        planned = json.loads(metadata.read_text())
        assert planned["configuration_id"] == "config"
        assert planned["output_sha256"] is None
        output.write_text(
            json.dumps(
                {
                    "registry_digest": "registry",
                    "checkpoint_digests": ["member"],
                    "seed_results": [{"seed": 3000, "steps": [{}, {}]}],
                }
            ),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0)

    execute_development_job(job, runner=fake_runner)

    completed = json.loads(metadata.read_text())
    assert len(completed["output_sha256"]) == 64


def test_job_resume_continues_digest_bound_partial_output(tmp_path):
    output = tmp_path / "rollout.json"
    metadata = tmp_path / "rollout.meta.json"
    job = {
        "registry_digest": "registry",
        "checkpoint_digests": ["member"],
        "calibrator_digest": "calibrator",
        "configuration_id": "config",
        "seeds": [3000, 3001],
        "rollout_steps": 2,
        "output": str(output),
        "metadata": str(metadata),
        "command": ["worker", "--output", str(output)],
    }
    output.write_text(
        json.dumps(
            {
                "registry_digest": "registry",
                "checkpoint_digests": ["member"],
                "seed_results": [{"seed": 3000, "steps": [{}, {}]}],
            }
        ),
        encoding="utf-8",
    )
    metadata.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registry_digest": "registry",
                "checkpoint_digests": ["member"],
                "calibrator_digest": "calibrator",
                "configuration_id": "config",
                "seeds": [3000, 3001],
                "rollout_steps": 2,
                "output_sha256": None,
            }
        ),
        encoding="utf-8",
    )

    def fake_runner(command, **kwargs):
        assert "--resume" in command
        output.write_text(
            json.dumps(
                {
                    "registry_digest": "registry",
                    "checkpoint_digests": ["member"],
                    "seed_results": [
                        {"seed": 3000, "steps": [{}, {}]},
                        {"seed": 3001, "steps": [{}, {}]},
                    ],
                }
            ),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0)

    payload = execute_development_job(job, resume=True, runner=fake_runner)

    assert [row["seed"] for row in payload["seed_results"]] == [3000, 3001]
    assert len(json.loads(metadata.read_text())["output_sha256"]) == 64


def test_rung_retention_records_every_rejected_configuration():
    rows = [
        {"id": "third", "planning_gate_count": 1, "reward": 9.0, "compute": 1},
        {"id": "first", "planning_gate_count": 3, "reward": 1.0, "compute": 9},
        {"id": "second", "planning_gate_count": 2, "reward": 5.0, "compute": 2},
    ]

    result = retain_configurations(rows, keep=2)

    assert [row["id"] for row in result["retained"]] == ["first", "second"]
    assert result["rejected"] == [
        {"id": "third", "rank": 3, "reason": "outside_top_2"}
    ]


def test_rung_aggregation_requires_three_model_seed_blocks():
    config = {
        "id": "config",
        "policy": "pcc_matched",
        "primary_candidate": "paper9_mpc",
        "development_bootstrap_seed": 7,
    }
    jobs = []
    payloads = {}
    for model_seed in (5101, 5102, 5103):
        for policy, configuration_id in (
            ("pcc_matched", "config"),
            ("paper9_mpc", "baseline-paper9_mpc"),
        ):
            job_id = f"{policy}-{model_seed}"
            jobs.append(
                {
                    "id": job_id,
                    "policy": policy,
                    "configuration_id": configuration_id,
                    "model_seed": model_seed,
                }
            )
            payloads[job_id] = {
                "seed_results": [
                    {
                        "policy": policy,
                        "model_seed": model_seed,
                        "seed": 3000,
                        "objective_outcome": [
                            2.0 if policy == "pcc_matched" else 1.0,
                            0.2,
                            0.3,
                            0.4,
                        ],
                        "steps": [{"member_evaluations": 3}],
                    }
                ]
            }

    rows = aggregate_development_rung(
        [config],
        jobs=jobs,
        payloads=payloads,
        model_seeds=(5101, 5102, 5103),
        seeds=(3000,),
        draws=100,
    )

    assert len(rows) == 1
    assert rows[0]["paired_observations"] == 3
    assert rows[0]["model_seeds"] == [5101, 5102, 5103]
    assert rows[0]["source_seeds"] == [3000]

    del payloads["pcc_matched-5103"]
    with pytest.raises(ValueError, match="model-seed block"):
        aggregate_development_rung(
            [config],
            jobs=jobs,
            payloads=payloads,
            model_seeds=(5101, 5102, 5103),
            seeds=(3000,),
            draws=100,
        )

def test_development_row_uses_paired_objectives_and_compute():
    rows = []
    for seed, policy_reward, comparator_reward in (
        (3000, 2.0, 1.0),
        (3001, 4.0, 1.0),
    ):
        rows.extend(
            [
                {
                    "policy": "pcc_matched",
                    "model_seed": 5101,
                    "seed": seed,
                    "objective_outcome": [policy_reward, 0.2, 0.3, 0.4],
                    "steps": [{"member_evaluations": 3}],
                },
                {
                    "policy": "paper9_mpc",
                    "model_seed": 5101,
                    "seed": seed,
                    "objective_outcome": [comparator_reward, 0.1, 0.2, 0.3],
                    "steps": [{"member_evaluations": 0}],
                },
            ]
        )

    result = development_row(
        {
            "id": "config",
            "policy": "pcc_matched",
            "primary_candidate": "paper9_mpc",
            "development_bootstrap_seed": 7,
        },
        rows,
        draws=100,
    )

    assert result["planning_gate_count"] == 3
    assert result["reward"] == 2.0
    assert result["compute"] == 6


def test_development_row_rejects_unpaired_policy_seed():
    rows = [
        {
            "policy": "pcc_matched",
            "model_seed": 5101,
            "seed": 3000,
            "objective_outcome": [1.0, 0.2, 0.3, 0.4],
            "steps": [{"member_evaluations": 3}],
        }
    ]

    with pytest.raises(ValueError, match="paired"):
        development_row(
            {
                "id": "config",
                "policy": "pcc_matched",
                "primary_candidate": "paper9_mpc",
                "development_bootstrap_seed": 7,
            },
            rows,
            draws=100,
        )


def test_freeze_writes_selected_config_and_primary_comparator(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")
    row = {
        "id": "winner",
        "planning_gate_count": 3,
        "reward": 1.0,
        "compute": 48,
        "ensemble_size": 3,
        "joint_coverage": 0.9,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "residual_window": 10,
        "policy_round": 2,
        "model_seeds": [5101, 5102, 5103],
        "source_seeds": list(range(3000, 3010)),
        "development_artifact_digest": "d" * 64,
        "ablation_inventory_digest": "a" * 64,
    }

    frozen = freeze_development(
        path,
        development_rows=[row],
        stage_a_report={"passed": True},
        primary_comparator="distributional_risk",
        checkpoint_digests=[f"{index:064x}" for index in range(1, 10)],
        calibrator_digest={
            str(seed): f"{seed:064x}" for seed in (5101, 5102, 5103)
        },
        expert_learning_rate=0.1,
        compute_budget=50,
        completed_ablations=load_registry()["required_ablations"],
    )

    assert frozen["status"] == "frozen"
    assert frozen["selected_config"]["id"] == "winner"
    assert frozen["selected_config"]["primary_comparator"] == "distributional_risk"


def test_freeze_rejects_failed_stage_a(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")

    with pytest.raises(ValueError, match="Stage A"):
        freeze_development(
            path,
            development_rows=[],
            stage_a_report={"passed": False},
            primary_comparator="paper9_mpc",
            checkpoint_digests=[],
            calibrator_digest={},
            expert_learning_rate=0.1,
            compute_budget=50,
            completed_ablations=[],
        )


def test_freeze_rejects_incomplete_ablation_or_model_seed_block(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(load_registry()), encoding="utf-8")
    row = {
        "id": "incomplete",
        "planning_gate_count": 3,
        "reward": 1.0,
        "compute": 48,
        "ensemble_size": 3,
        "joint_coverage": 0.9,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "residual_window": 10,
        "policy_round": 2,
        "model_seeds": [5101],
        "source_seeds": list(range(3000, 3010)),
        "development_artifact_digest": "d" * 64,
        "ablation_inventory_digest": "a" * 64,
    }

    with pytest.raises(ValueError, match="model-seed block"):
        freeze_development(
            path,
            development_rows=[row],
            stage_a_report={"passed": True},
            primary_comparator="paper9_mpc",
            checkpoint_digests=[f"{index:064x}" for index in range(1, 4)],
            calibrator_digest={"5101": f"{5101:064x}"},
            expert_learning_rate=0.1,
            compute_budget=50,
            completed_ablations=load_registry()["required_ablations"],
        )
