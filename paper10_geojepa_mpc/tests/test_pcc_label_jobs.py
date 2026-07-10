import numpy as np

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    write_label_manifest,
    write_trajectory_artifact,
)
from paper10_geojepa_mpc.experiments.run_pcc_label_jobs import (
    _build_seed_command,
    merge_seed_manifests,
    parse_args,
    valid_completed_seeds,
)


def _write_seed(root, seed):
    seed_dir = root / f"seed_{seed}"
    dataset = {
        "states_bf": np.zeros((1, 2, 1), dtype=np.float32),
        "actions": np.zeros((1, 1), dtype=np.int64),
    }
    artifact = write_trajectory_artifact(seed_dir, seed, dataset)
    write_label_manifest(
        seed_dir,
        protocol_id="fixture",
        partition="train",
        artifacts=[artifact],
        continuation_policy={"name": "fixture"},
        horizons=(1, 3, 5),
    )


def test_merge_seed_manifests_preserves_relative_artifact_paths(tmp_path):
    _write_seed(tmp_path, 1000)
    _write_seed(tmp_path, 1001)

    manifest = merge_seed_manifests(
        tmp_path,
        expected_protocol_id="fixture",
        expected_partition="train",
        expected_seeds=[1000, 1001],
    )

    assert manifest["trajectory_seeds"] == [1000, 1001]
    assert [row["path"] for row in manifest["artifacts"]] == [
        "seed_1000/trajectory_1000.npz",
        "seed_1001/trajectory_1001.npz",
    ]


def test_completed_seed_detection_rejects_missing_artifact(tmp_path):
    _write_seed(tmp_path, 1000)
    (tmp_path / "seed_1000" / "trajectory_1000.npz").unlink()

    assert valid_completed_seeds(tmp_path, [1000, 1001]) == set()


def test_completed_seed_detection_rejects_wrong_continuation_lineage(tmp_path):
    _write_seed(tmp_path, 1000)

    assert valid_completed_seeds(
        tmp_path,
        [1000],
        expected_policy="pcc",
        expected_model_seed=5101,
    ) == set()


def test_pcc_seed_job_command_carries_checkpoint_calibrator_and_model_seed(tmp_path):
    args = parse_args(
        [
            "--registry",
            "registry.json",
            "--partition",
            "train",
            "--prepared-dir",
            str(tmp_path),
            "--policy",
            "pcc",
            "--pcc-checkpoint-root",
            "checkpoints",
            "--pcc-calibrator",
            "calibrator.json",
            "--pcc-model-seed",
            "5101",
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    command = _build_seed_command(args, seed=1000, states=20, candidates=8)

    assert command[command.index("--policy") + 1] == "pcc"
    assert command[command.index("--pcc-checkpoint-root") + 1] == "checkpoints"
    assert command[command.index("--pcc-calibrator") + 1] == "calibrator.json"
    assert command[command.index("--pcc-model-seed") + 1] == "5101"
