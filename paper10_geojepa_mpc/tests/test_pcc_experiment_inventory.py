import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import pytest
import torch

from paper10_geojepa_mpc.experiments.pcc_experiment_inventory import (
    audit_checkpoint_only_inventory,
    build_adapted_inventory,
    build_inventory,
    main,
)
from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES
from paper10_geojepa_mpc.experiments.pcc_policy_iteration_lineage import (
    write_round_manifest,
)
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry
from paper10_geojepa_mpc.experiments.pcc_protocol_registry import freeze_registry
from paper10_geojepa_mpc.planning.paired_conformal import (
    JointPairedCalibrator,
    save_joint_calibrator,
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_inventory_fixture(
    root: Path,
    *,
    model_seeds=(5101, 5102, 5103),
    ensemble_sizes=(3,),
    member_indexes=None,
    rounds=(1, 2),
    coverages=(0.8, 0.9, 0.95),
    calibrator_overrides=None,
    checkpoint_overrides=None,
):
    registry = load_registry()
    calibration_seeds = tuple(registry["partitions"]["calibration"])
    overrides = dict(calibrator_overrides or {})
    checkpoint_overrides = dict(checkpoint_overrides or {})
    records = {}
    for model_seed in model_seeds:
        parent_digest = registry["offline_reference_policy"][
            "checkpoint_sha256"
        ]
        for round_index in rounds:
            train_digest = f"train-{model_seed}-{round_index}"
            calibration_digest = f"calibration-{model_seed}-{round_index}"
            if round_index > min(rounds):
                previous_sizes = sorted(
                    size
                    for seed, size, index in records
                    if seed == model_seed and index == round_index - 1
                )
                parent_size = 3 if 3 in previous_sizes else previous_sizes[0]
                parent_digest = records[
                    (model_seed, parent_size, round_index - 1)
                ]["manifest"]["round_digest"]
            for ensemble_size in ensemble_sizes:
                indexes = (
                    tuple(range(ensemble_size))
                    if member_indexes is None
                    else tuple(member_indexes)
                )
                # The misleading path makes filename-based lineage inference fail.
                checkpoint_root = (
                    root
                    / f"looks_like_seed_{model_seed + 77}"
                    / f"looks_like_round_{round_index + 5}"
                    / f"looks_like_k_{ensemble_size + 11}"
                    / "checkpoints"
                )
                checkpoint_root.mkdir(parents=True, exist_ok=True)
                checkpoint_paths = []
                for ordinal, member_index in enumerate(indexes):
                    checkpoint_path = checkpoint_root / f"blob_{ordinal}.pt"
                    torch.save(
                        {
                            "model_seed": int(model_seed),
                            "ensemble_size": int(
                                checkpoint_overrides.get(
                                    "ensemble_size", ensemble_size
                                )
                            ),
                            "member_seed": int(
                                model_seed * 1000
                                + round_index * 100
                                + ensemble_size * 10
                                + ordinal
                            ),
                            "member_index": int(member_index),
                            "bootstrap_trajectory_ids": [
                                *checkpoint_overrides.get(
                                    "bootstrap_trajectory_ids",
                                    (1000 + ordinal, 1001 + ordinal),
                                )
                            ],
                            "labels_manifest_digest": train_digest,
                            "registry_digest": checkpoint_overrides.get(
                                "registry_digest"
                            ),
                            "protocol_id": registry["protocol_id"],
                            "objective_names": list(OBJECTIVE_NAMES),
                            "objective_scaling": {"center": [], "scale": []},
                            "trainable_scope": "all",
                        },
                        checkpoint_path,
                    )
                    checkpoint_paths.append(checkpoint_path)
                checkpoint_digests = tuple(
                    _sha256_file(path) for path in checkpoint_paths
                )

                calibrators = {}
                calibrator_payloads = {}
                for coverage in coverages:
                    calibrator_path = (
                        root
                        / "calibration_blobs"
                        / (
                            f"artifact_{model_seed}_{ensemble_size}_"
                            f"{round_index}_{coverage}.json"
                        )
                    )
                    calibrator = JointPairedCalibrator(
                        coverage=float(overrides.get("coverage", coverage)),
                        q_joint=1.0,
                        trajectory_ids=np.asarray(
                            overrides.get("trajectory_ids", calibration_seeds)
                        ),
                        trajectory_scores=np.ones(len(calibration_seeds)),
                        objective_names=tuple(
                            overrides.get("objective_names", OBJECTIVE_NAMES)
                        ),
                        protocol_id=str(
                            overrides.get("protocol_id", registry["protocol_id"])
                        ),
                        calibration_seeds=tuple(
                            overrides.get("calibration_seeds", calibration_seeds)
                        ),
                        labels_manifest_digest=str(
                            overrides.get(
                                "labels_manifest_digest", calibration_digest
                            )
                        ),
                        checkpoint_digests=tuple(
                            overrides.get(
                                "checkpoint_digests", checkpoint_digests
                            )
                        ),
                    )
                    calibrator_payloads[coverage] = save_joint_calibrator(
                        calibrator_path,
                        calibrator,
                    )
                    calibrators[coverage] = calibrator_path

                primary_coverage = 0.9 if 0.9 in coverages else coverages[0]
                manifest_path = (
                    root
                    / "lineage_blobs"
                    / f"artifact_{model_seed}_{ensemble_size}_{round_index}.json"
                )
                if round_index == 1:
                    continuation_policy = {"name": "paper9_mpc"}
                else:
                    source = records[(model_seed, 3, 1)]["manifest"]
                    continuation_policy = {
                        "name": "pcc_round1",
                        "model_seed": model_seed,
                        "checkpoint_digests": list(
                            source["checkpoint_digests"]
                        ),
                        "calibrator_digest": source["calibrator_digest"],
                        "planning_horizon": 3,
                        "candidate_budget": 50,
                        "tolerance_scale": 0.05,
                        "joint_coverage": 0.9,
                    }
                manifest = write_round_manifest(
                    manifest_path,
                    model_seed=model_seed,
                    round_index=round_index,
                    parent_digest=parent_digest,
                    train_labels_digest=train_digest,
                    calibration_labels_digest=calibration_digest,
                    checkpoint_digests=list(checkpoint_digests),
                    calibrator_digest=calibrator_payloads[primary_coverage][
                        "calibrator_digest"
                    ],
                    continuation_policy=continuation_policy,
                )
                records[(model_seed, ensemble_size, round_index)] = {
                    "checkpoint_root": checkpoint_root,
                    "checkpoint_paths": checkpoint_paths,
                    "calibrators": calibrators,
                    "manifest_path": manifest_path,
                    "manifest": manifest,
                }
    return records


def test_inventory_resolves_every_model_seed_ensemble_round(tmp_path):
    create_inventory_fixture(tmp_path)

    inventory = build_inventory(
        tmp_path,
        model_seeds=(5101, 5102, 5103),
    )

    assert inventory.checkpoint_root(5102, 3, 2).name == "checkpoints"
    assert len(inventory.checkpoint_digests(5102, 3, 2)) == 3
    assert inventory.coverages(5102, 3, 2) == (0.8, 0.9, 0.95)
    assert len(inventory.calibrator_digest(5102, 3, 2, 0.9)) == 64
    assert len(inventory.records) == 6


def test_inventory_supports_separate_calibrator_root(tmp_path):
    checkpoint_root = tmp_path / "checkpoints"
    calibration_root = tmp_path / "calibration"
    create_inventory_fixture(
        checkpoint_root,
        model_seeds=(5101,),
        rounds=(1,),
    )
    calibration_root.mkdir()
    shutil.move(
        str(checkpoint_root / "calibration_blobs"),
        str(calibration_root / "calibration_blobs"),
    )

    inventory = build_inventory(
        checkpoint_root,
        calibrator_root=calibration_root,
        model_seeds=(5101,),
    )

    assert inventory.calibrator(5101, 3, 1, 0.9).is_relative_to(
        calibration_root
    )


def create_adapted_inventory_fixture(
    root: Path,
    *,
    first_checkpoint_overrides=None,
    omit_first_checkpoint_fields=(),
    adaptation_label_digests=None,
    calibration_label_digests=None,
    first_summary_overrides=None,
):
    checkpoint_root = root / "adapted"
    calibration_root = root / "calibration"
    registry_path = root / "registry.json"
    registry_path.write_text(json.dumps(load_registry()), encoding="utf-8")
    parent_digests = [f"{index + 1:064x}" for index in range(9)]
    frozen = freeze_registry(
        registry_path,
        selected_config={
            "ensemble_size": 3,
            "policy_round": 2,
            "joint_coverage": 0.9,
            "checkpoint_digests": parent_digests,
        },
    )
    calibration_seeds = tuple(frozen["partitions"]["dongxing_calibration"])
    adaptation_label_digests = dict(adaptation_label_digests or {})
    calibration_label_digests = dict(calibration_label_digests or {})
    for model_index, model_seed in enumerate(frozen["model_seeds"]):
        model_root = checkpoint_root / f"model-{model_seed}"
        model_root.mkdir(parents=True)
        paths = []
        checkpoint_digests = []
        for member_index in range(3):
            path = model_root / f"member_{member_index}.pt"
            checkpoint = {
                "model_seed": model_seed,
                "ensemble_size": 3,
                "member_seed": model_seed * 100 + member_index,
                "member_index": member_index,
                "bootstrap_trajectory_ids": [
                    6000 + ((member_index + offset) % 4)
                    for offset in range(4)
                ],
                "labels_manifest_digest": adaptation_label_digests.get(
                    model_seed, "adapt-dongxing"
                ),
                "adaptation_labels_manifest_digest": (
                    adaptation_label_digests.get(model_seed, "adapt-dongxing")
                ),
                "registry_digest": frozen["frozen_digest"],
                "protocol_id": frozen["protocol_id"],
                "objective_names": list(OBJECTIVE_NAMES),
                "trainable_scope": "objective_heads",
                "trainable_parameter_names": [
                    "immediate_head.weight",
                    "horizon_head.weight",
                ],
                "region": "dongxing",
                "parent_checkpoint_sha256": parent_digests[
                    model_index * 3 + member_index
                ],
            }
            if model_index == 0 and member_index == 0:
                checkpoint.update(first_checkpoint_overrides or {})
                for field in omit_first_checkpoint_fields:
                    checkpoint.pop(field, None)
            torch.save(checkpoint, path)
            paths.append(path)
            checkpoint_digests.append(_sha256_file(path))
        summary = {
            "protocol_id": frozen["protocol_id"],
            "registry_digest": frozen["frozen_digest"],
            "region": "dongxing",
            "model_seed": model_seed,
            "ensemble_size": 3,
            "trainable_scope": "objective_heads",
            "adaptation_hyperparameters": dict(
                frozen["dongxing_adaptation_training"]
            ),
            "parent_checkpoint_digests": parent_digests[
                model_index * 3 : (model_index + 1) * 3
            ],
            "checkpoints": [
                {"path": str(path), "sha256": digest}
                for path, digest in zip(paths, checkpoint_digests)
            ],
        }
        if model_index == 0:
            summary.update(first_summary_overrides or {})
        (model_root / "training_summary.json").write_text(
            json.dumps(summary),
            encoding="utf-8",
        )
        calibrator = JointPairedCalibrator(
            coverage=0.9,
            q_joint=1.0,
            trajectory_ids=np.asarray(calibration_seeds),
            trajectory_scores=np.ones(len(calibration_seeds)),
            objective_names=OBJECTIVE_NAMES,
            protocol_id=frozen["protocol_id"],
            calibration_seeds=calibration_seeds,
            labels_manifest_digest=calibration_label_digests.get(
                model_seed, "calibration-dongxing"
            ),
            checkpoint_digests=tuple(checkpoint_digests),
        )
        save_joint_calibrator(
            calibration_root / f"model-{model_seed}.json",
            calibrator,
        )
    return checkpoint_root, calibration_root, frozen


def test_adapted_inventory_resolves_only_frozen_dongxing_winner(tmp_path):
    checkpoint_root, calibration_root, frozen = (
        create_adapted_inventory_fixture(tmp_path)
    )

    inventory = build_adapted_inventory(
        checkpoint_root,
        calibrator_root=calibration_root,
        registry=frozen,
    )

    assert len(inventory.records) == 3
    assert len(inventory.checkpoint_digests(5102, 3, 2)) == 3
    assert inventory.coverages(5102, 3, 2) == (0.9,)


@pytest.mark.parametrize(
    ("overrides", "omitted_fields", "message"),
    [
        (
            {"parent_checkpoint_sha256": "f" * 64},
            (),
            "checkpoint lineage",
        ),
        (
            {"bootstrap_trajectory_ids": [8000]},
            (),
            "adaptation partition",
        ),
        ({}, ("objective_names",), "objective order"),
    ],
    ids=("parent-hash", "bootstrap-partition", "objective-order"),
)
def test_adapted_inventory_rejects_checkpoint_lineage_mismatch(
    tmp_path,
    overrides,
    omitted_fields,
    message,
):
    checkpoint_root, calibration_root, frozen = (
        create_adapted_inventory_fixture(
            tmp_path,
            first_checkpoint_overrides=overrides,
            omit_first_checkpoint_fields=omitted_fields,
        )
    )

    with pytest.raises(ValueError, match=message):
        build_adapted_inventory(
            checkpoint_root,
            calibrator_root=calibration_root,
            registry=frozen,
        )


@pytest.mark.parametrize(
    ("fixture_overrides", "message"),
    [
        (
            {
                "adaptation_label_digests": {
                    5101: "adapt-a",
                    5102: "adapt-b",
                    5103: "adapt-c",
                }
            },
            "shared adaptation label",
        ),
        (
            {
                "calibration_label_digests": {
                    5101: "calibration-a",
                    5102: "calibration-b",
                    5103: "calibration-c",
                }
            },
            "shared calibration label",
        ),
    ],
    ids=("adaptation-labels", "calibration-labels"),
)
def test_adapted_inventory_requires_shared_label_manifests(
    tmp_path,
    fixture_overrides,
    message,
):
    checkpoint_root, calibration_root, frozen = (
        create_adapted_inventory_fixture(tmp_path, **fixture_overrides)
    )

    with pytest.raises(ValueError, match=message):
        build_adapted_inventory(
            checkpoint_root,
            calibrator_root=calibration_root,
            registry=frozen,
        )


def test_adapted_inventory_rejects_training_hyperparameter_mismatch(tmp_path):
    checkpoint_root, calibration_root, frozen = (
        create_adapted_inventory_fixture(
            tmp_path,
            first_summary_overrides={
                "adaptation_hyperparameters": {
                    **load_registry()["dongxing_adaptation_training"],
                    "learning_rate": 0.01,
                }
            },
        )
    )

    with pytest.raises(ValueError, match="adaptation hyperparameters"):
        build_adapted_inventory(
            checkpoint_root,
            calibrator_root=calibration_root,
            registry=frozen,
        )


@pytest.mark.parametrize(
    "member_indexes",
    [(0, 0, 2), (0, 2)],
    ids=("duplicate", "missing"),
)
def test_inventory_rejects_duplicate_or_missing_member(
    tmp_path,
    member_indexes,
):
    create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        member_indexes=member_indexes,
        rounds=(1,),
    )

    with pytest.raises(ValueError, match="member indexes"):
        build_inventory(tmp_path, model_seeds=(5101,))


def test_inventory_binds_manifest_to_physical_checkpoint_hashes(tmp_path):
    fixture = create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        rounds=(1,),
    )
    checkpoint_path = fixture[(5101, 3, 1)]["checkpoint_paths"][0]
    with checkpoint_path.open("ab") as handle:
        handle.write(b"mutated-after-manifest")

    with pytest.raises(ValueError, match="checkpoint digest"):
        build_inventory(tmp_path, model_seeds=(5101,))


def test_inventory_rejects_duplicate_bootstrap_membership(tmp_path):
    create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        rounds=(1,),
        checkpoint_overrides={"bootstrap_trajectory_ids": (1000, 1001)},
    )

    with pytest.raises(ValueError, match="bootstrap"):
        build_inventory(tmp_path, model_seeds=(5101,))


def test_inventory_rejects_checkpoint_ensemble_size_mismatch(tmp_path):
    create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        rounds=(1,),
        checkpoint_overrides={"ensemble_size": 5},
    )

    with pytest.raises(ValueError, match="ensemble size"):
        build_inventory(tmp_path, model_seeds=(5101,))


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"protocol_id": "other_protocol"}, "protocol"),
        ({"calibration_seeds": (2000, 2001)}, "seed block"),
        ({"trajectory_ids": (2000, 2001)}, "trajectory IDs"),
        ({"labels_manifest_digest": "other-labels"}, "label lineage"),
        ({"checkpoint_digests": ("wrong",)}, "checkpoint lineage"),
        ({"coverage": 0.77}, "coverage"),
        ({"objective_names": tuple(reversed(OBJECTIVE_NAMES))}, "objective order"),
    ],
)
def test_inventory_rejects_calibrator_lineage_mismatch(
    tmp_path,
    overrides,
    message,
):
    create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        rounds=(1,),
        coverages=(0.9,),
        calibrator_overrides=overrides,
    )

    with pytest.raises(ValueError, match=message):
        build_inventory(tmp_path, model_seeds=(5101,))


def test_inventory_requires_same_ensemble_round_keys_for_each_model_seed(tmp_path):
    create_inventory_fixture(tmp_path, model_seeds=(5101,), rounds=(1, 2))
    create_inventory_fixture(tmp_path, model_seeds=(5102,), rounds=(1,))

    with pytest.raises(ValueError, match="inventory keys"):
        build_inventory(tmp_path, model_seeds=(5101, 5102))


def test_complete_inventory_requires_declared_ensemble_round_factorial(tmp_path):
    create_inventory_fixture(
        tmp_path,
        ensemble_sizes=(3,),
        rounds=(1, 2),
    )

    with pytest.raises(ValueError, match="factorial"):
        build_inventory(
            tmp_path,
            model_seeds=(5101, 5102, 5103),
            require_complete=True,
        )


def test_complete_inventory_requires_every_declared_coverage(tmp_path):
    create_inventory_fixture(
        tmp_path,
        ensemble_sizes=(3, 5),
        rounds=(1, 2),
        coverages=(0.9,),
    )

    with pytest.raises(ValueError, match="coverage factorial"):
        build_inventory(
            tmp_path,
            model_seeds=(5101, 5102, 5103),
            require_complete=True,
        )


def test_complete_inventory_binds_round2_to_round1_k3_parent(tmp_path):
    fixture = create_inventory_fixture(
        tmp_path,
        ensemble_sizes=(3, 5),
        rounds=(1, 2),
    )
    record = fixture[(5101, 5, 2)]
    round1_k5 = fixture[(5101, 5, 1)]["manifest"]
    manifest = record["manifest"]
    write_round_manifest(
        record["manifest_path"],
        model_seed=5101,
        round_index=2,
        parent_digest=round1_k5["round_digest"],
        train_labels_digest=manifest["train_labels_digest"],
        calibration_labels_digest=manifest["calibration_labels_digest"],
        checkpoint_digests=manifest["checkpoint_digests"],
        calibrator_digest=manifest["calibrator_digest"],
        continuation_policy=manifest["continuation_policy"],
    )

    with pytest.raises(ValueError, match="round-1 K=3 parent"):
        build_inventory(
            tmp_path,
            model_seeds=(5101, 5102, 5103),
            require_complete=True,
        )


def test_frozen_registry_accepts_checkpoints_trained_before_freeze(tmp_path):
    create_inventory_fixture(
        tmp_path / "artifacts",
        model_seeds=(5101,),
        rounds=(1,),
    )
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(load_registry(), indent=2) + "\n",
        encoding="utf-8",
    )
    frozen = freeze_registry(
        registry_path,
        selected_config={"id": "fixture"},
    )

    inventory = build_inventory(
        tmp_path / "artifacts",
        model_seeds=(5101,),
        registry=frozen,
    )

    assert len(inventory.records) == 1


def test_inventory_cli_emits_digest_bound_json_summary(tmp_path, capsys):
    fixture = create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        ensemble_sizes=(3, 5),
        rounds=(1, 2),
    )

    main(["--root", str(tmp_path), "--model-seeds", "5101"])

    report = json.loads(capsys.readouterr().out)
    assert report["passed"] is True
    assert report["model_seeds"] == [5101]
    assert report["n_records"] == 4
    record = report["records"][0]
    assert record["checkpoint_root"] == str(
        fixture[(5101, 3, 1)]["checkpoint_root"].resolve()
    )
    assert record["member_indexes"] == [0, 1, 2]
    assert set(record["calibrators"]) == {"0.8", "0.9", "0.95"}


def test_inventory_cli_rejects_partial_development_factorial(tmp_path):
    create_inventory_fixture(
        tmp_path,
        model_seeds=(5101,),
        ensemble_sizes=(3,),
        rounds=(1, 2),
    )

    with pytest.raises(ValueError, match="factorial"):
        main(["--root", str(tmp_path), "--model-seeds", "5101"])


def create_checkpoint_only_fixture(
    root: Path,
    *,
    duplicate_across_k=False,
    external_first_checkpoint=False,
):
    registry = load_registry()
    label_digest = "train-labels"
    for model_seed in registry["model_seeds"]:
        k3_paths = []
        for ensemble_size in (3, 5):
            block = root / f"seed{model_seed}_k{ensemble_size}"
            block.mkdir(parents=True)
            rows = []
            for member_index in range(ensemble_size):
                path = block / f"member_{member_index}.pt"
                if duplicate_across_k and ensemble_size == 5 and member_index < 3:
                    shutil.copy2(k3_paths[member_index], path)
                else:
                    torch.save(
                        {
                            "model_seed": model_seed,
                            "ensemble_size": ensemble_size,
                            "member_seed": (
                                model_seed * 1000
                                + ensemble_size * 10
                                + member_index
                            ),
                            "member_index": member_index,
                            "bootstrap_trajectory_ids": [
                                1000 + ((member_index + offset) % 8)
                                for offset in range(8)
                            ],
                            "labels_manifest_digest": label_digest,
                            "protocol_id": registry["protocol_id"],
                            "objective_names": list(OBJECTIVE_NAMES),
                            "region": "bishan",
                            "trainable_scope": "all",
                        },
                        path,
                    )
                if (
                    external_first_checkpoint
                    and model_seed == 5101
                    and ensemble_size == 3
                    and member_index == 0
                ):
                    external_path = root.parent / "external_member.pt"
                    shutil.copy2(path, external_path)
                    path = external_path
                rows.append({"path": str(path), "sha256": _sha256_file(path)})
                if ensemble_size == 3:
                    k3_paths.append(path)
            (block / "training_summary.json").write_text(
                json.dumps(
                    {
                        "protocol_id": registry["protocol_id"],
                        "registry_digest": None,
                        "model_seed": model_seed,
                        "ensemble_size": ensemble_size,
                        "region": "bishan",
                        "parent_checkpoint_digests": [],
                        "trainable_scope": "all",
                        "representation": "action_relative",
                        "county_action_count": None,
                        "checkpoints": rows,
                    }
                ),
                encoding="utf-8",
            )


def test_checkpoint_only_inventory_audits_declared_training_factorial(tmp_path):
    create_checkpoint_only_fixture(tmp_path)

    report = audit_checkpoint_only_inventory(
        tmp_path,
        registry=load_registry(),
        model_seeds=(5101, 5102, 5103),
    )

    assert report["passed"] is True
    assert report["n_summaries"] == 6
    assert report["n_checkpoints"] == 24
    assert report["ensemble_sizes"] == [3, 5]


def test_checkpoint_only_inventory_rejects_cross_k_checkpoint_reuse(tmp_path):
    create_checkpoint_only_fixture(tmp_path, duplicate_across_k=True)

    with pytest.raises(ValueError, match="reused|ensemble size"):
        audit_checkpoint_only_inventory(
            tmp_path,
            registry=load_registry(),
            model_seeds=(5101, 5102, 5103),
        )


def test_checkpoint_only_inventory_rejects_checkpoint_outside_root(tmp_path):
    root = tmp_path / "inventory"
    create_checkpoint_only_fixture(root, external_first_checkpoint=True)

    with pytest.raises(ValueError, match="outside the inventory root"):
        audit_checkpoint_only_inventory(
            root,
            registry=load_registry(),
            model_seeds=(5101, 5102, 5103),
        )
