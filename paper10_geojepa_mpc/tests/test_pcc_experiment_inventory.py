import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from paper10_geojepa_mpc.experiments.pcc_experiment_inventory import (
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
    member_indexes=(0, 1, 2),
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
            # The misleading path makes filename-based seed/round inference fail.
            checkpoint_root = (
                root
                / f"looks_like_seed_{model_seed + 77}"
                / f"looks_like_round_{round_index + 5}"
                / "checkpoints"
            )
            checkpoint_root.mkdir(parents=True, exist_ok=True)
            checkpoint_paths = []
            for ordinal, member_index in enumerate(member_indexes):
                checkpoint_path = checkpoint_root / f"blob_{ordinal}.pt"
                torch.save(
                    {
                        "model_seed": int(model_seed),
                        "member_seed": int(model_seed * 100 + ordinal),
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
                    / f"artifact_{model_seed}_{round_index}_{coverage}.json"
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
                / f"artifact_{model_seed}_{round_index}.json"
            )
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
                continuation_policy={
                    "name": (
                        "paper9_mpc" if round_index == 1 else "pcc_round1"
                    )
                },
            )
            parent_digest = manifest["round_digest"]
            records[(model_seed, len(member_indexes), round_index)] = {
                "checkpoint_root": checkpoint_root,
                "checkpoint_paths": checkpoint_paths,
                "calibrators": calibrators,
                "manifest_path": manifest_path,
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
    assert len(inventory.records) == 6


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
        rounds=(1,),
    )

    main(["--root", str(tmp_path), "--model-seeds", "5101"])

    report = json.loads(capsys.readouterr().out)
    assert report["passed"] is True
    assert report["model_seeds"] == [5101]
    assert report["n_records"] == 1
    record = report["records"][0]
    assert record["checkpoint_root"] == str(
        fixture[(5101, 3, 1)]["checkpoint_root"].resolve()
    )
    assert record["member_indexes"] == [0, 1, 2]
    assert set(record["calibrators"]) == {"0.8", "0.9", "0.95"}
