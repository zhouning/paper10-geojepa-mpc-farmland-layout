import numpy as np

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    write_label_manifest,
    write_trajectory_artifact,
)
from paper10_geojepa_mpc.experiments.run_pcc_label_jobs import (
    merge_seed_manifests,
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
