import json
from importlib import import_module
from pathlib import Path

import numpy as np
import pytest


def _labels_module():
    return import_module(
        "paper10_geojepa_mpc.experiments.pcc_v1_1_selected_labels"
    )


class _TinyPairedEnv:
    n_blocks = 3

    def __init__(self):
        self.value = 0
        self.step_count = 0
        self.real_step_calls = 0
        self.executed_actions = []

    def reset(self, seed=None):
        self.value = 0
        self.step_count = 0
        self.real_step_calls = 0
        self.executed_actions = []
        return self._get_global_features(), self.metrics()

    def metrics(self):
        return {
            "avg_slope": 10.0 - self.value,
            "contiguity": self.value / 10.0,
            "baimu_area_ha": 100.0 + self.value,
        }

    def action_masks(self):
        return np.ones(self.n_blocks, dtype=bool)

    def _get_block_features(self):
        return np.asarray(
            [[1.0, self.value], [2.0, self.value], [3.0, self.value]],
            dtype=np.float32,
        )

    def _get_global_features(self):
        return np.asarray([self.step_count, self.value], dtype=np.float32)

    def step(self, action):
        action = int(action)
        self.real_step_calls += 1
        self.executed_actions.append(action)
        self.value += action + 1
        self.step_count += 1
        return (
            self._get_global_features(),
            float(action + 1),
            False,
            False,
            self.metrics(),
        )


class _FixedBasePolicy:
    def __init__(
        self,
        *,
        selected: int,
        reference: int,
        query_count: int = 0,
        predicted_scale: float = 1.0,
    ):
        self.selected = int(selected)
        self.reference = int(reference)
        self.query_count = int(query_count)
        self.predicted_scale = float(predicted_scale)

    def __call__(self, env, rng):
        predicted = np.zeros((3, 4), dtype=np.float32)
        predicted[:, 0] = float(self.selected - self.reference)
        return self.selected, {
            "base_selected_action": self.selected,
            "reference_action": self.reference,
            "selected_predicted_delta": predicted.tolist(),
            "selected_predicted_scale": np.full(
                (3, 4),
                self.predicted_scale,
            ).tolist(),
            "selected_executable_probability": 1.0,
            "base_selection_reason": "reward_mean_among_mean_safe",
            "unexecuted_real_reward_queries": self.query_count,
        }


def _read_metrics(env):
    return env.metrics()


_TINY_STATE_ATTRS = (
    "value",
    "step_count",
    "real_step_calls",
    "executed_actions",
)


def test_selected_label_trajectory_evaluates_only_selected_and_reference():
    labels = _labels_module()
    env = _TinyPairedEnv()

    result = labels.generate_selected_label_trajectory(
        env=env,
        trajectory_seed=2000,
        n_states=2,
        horizons=(1, 3, 5),
        gamma=0.99,
        base_policy=_FixedBasePolicy(selected=2, reference=1),
        continuation_policy=lambda *_: 0,
        metric_reader=_read_metrics,
        state_attrs=_TINY_STATE_ATTRS,
    )

    assert env.real_step_calls == 2
    assert result["selected_actions"].tolist() == [2, 2]
    assert result["reference_actions"].tolist() == [1, 1]
    assert result["unexecuted_real_reward_queries"].tolist() == [0, 0]
    assert result["true_delta"].shape == (2, 3, 4)
    assert result["predicted_delta"].shape == (2, 3, 4)
    assert result["predicted_scale"].shape == (2, 3, 4)


def test_selected_label_generation_advances_on_reference_path():
    labels = _labels_module()
    env = _TinyPairedEnv()

    labels.generate_selected_label_trajectory(
        env=env,
        trajectory_seed=2000,
        n_states=2,
        horizons=(1, 3, 5),
        gamma=0.99,
        base_policy=_FixedBasePolicy(selected=2, reference=1),
        continuation_policy=lambda *_: 0,
        metric_reader=_read_metrics,
        state_attrs=_TINY_STATE_ATTRS,
    )

    assert env.executed_actions == [1, 1]


def test_selected_label_generation_rejects_real_reward_query_counter():
    labels = _labels_module()
    env = _TinyPairedEnv()

    with pytest.raises(ValueError, match="unexecuted real-reward"):
        labels.generate_selected_label_trajectory(
            env=env,
            trajectory_seed=2000,
            n_states=1,
            horizons=(1, 3, 5),
            gamma=0.99,
            base_policy=_FixedBasePolicy(
                selected=2,
                reference=1,
                query_count=1,
            ),
            continuation_policy=lambda *_: 0,
            metric_reader=_read_metrics,
        )

    assert env.executed_actions == []


def test_reference_selected_label_has_exact_zero_delta_and_scale():
    labels = _labels_module()

    result = labels.generate_selected_label_trajectory(
        env=_TinyPairedEnv(),
        trajectory_seed=2000,
        n_states=1,
        horizons=(1, 3, 5),
        gamma=0.99,
        base_policy=_FixedBasePolicy(
            selected=1,
            reference=1,
            predicted_scale=0.0,
        ),
        continuation_policy=lambda *_: 0,
        metric_reader=_read_metrics,
        state_attrs=_TINY_STATE_ATTRS,
    )

    np.testing.assert_array_equal(result["true_delta"], 0.0)
    np.testing.assert_array_equal(result["predicted_delta"], 0.0)
    np.testing.assert_array_equal(result["predicted_scale"], 0.0)


def _selected_lineage() -> dict[str, object]:
    return {
        "protocol_id": "pcc_v1_1",
        "registry_digest": "a" * 64,
        "partition": "calibration",
        "model_seed": 5101,
        "ensemble_size": 3,
        "policy_round": 1,
        "compute_mode": "matched",
        "checkpoint_digests": ["b" * 64, "c" * 64, "d" * 64],
        "candidate_generator_digest": "e" * 64,
        "base_selector_digest": "f" * 64,
        "reference_checkpoint_digest": "9" * 64,
    }


def _selected_dataset():
    return {
        "selected_actions": np.array([2, 2], dtype=np.int64),
        "reference_actions": np.array([1, 1], dtype=np.int64),
        "predicted_delta": np.zeros((2, 3, 4), dtype=np.float32),
        "predicted_scale": np.ones((2, 3, 4), dtype=np.float32),
        "true_delta": np.zeros((2, 3, 4), dtype=np.float32),
        "executable_probability": np.ones(2, dtype=np.float32),
        "base_selection_reason": np.array(
            ["reward_mean_among_mean_safe"] * 2,
            dtype="U64",
        ),
        "state_steps": np.array([0, 1], dtype=np.int64),
        "trajectory_ids": np.array([2000, 2000], dtype=np.int64),
        "continuation_seeds": np.array([11, 12], dtype=np.uint64),
        "unexecuted_real_reward_queries": np.zeros(2, dtype=np.int64),
    }


def _write_selected_fixture(root: Path):
    labels = _labels_module()
    artifact = labels.write_selected_trajectory_artifact(
        root,
        2000,
        _selected_dataset(),
    )
    payload = labels.write_selected_manifest(
        root,
        lineage=_selected_lineage(),
        artifacts=[artifact],
    )
    return root / "manifest.json", payload


def test_selected_manifest_is_coverage_independent_and_resumable(tmp_path):
    labels = _labels_module()
    path, payload = _write_selected_fixture(tmp_path / "selected")

    loaded = labels.load_resumable_selected_manifest(
        path,
        expected_lineage=_selected_lineage(),
    )

    assert loaded == payload
    assert loaded["trajectory_seeds"] == [2000]
    assert "coverage" not in loaded
    assert len(loaded["manifest_digest"]) == 64


def test_selected_manifest_resume_rejects_lineage_change(tmp_path):
    labels = _labels_module()
    path, _ = _write_selected_fixture(tmp_path / "selected")
    expected = _selected_lineage()
    expected["compute_mode"] = "full"

    with pytest.raises(ValueError, match="lineage"):
        labels.load_resumable_selected_manifest(
            path,
            expected_lineage=expected,
        )


def test_selected_manifest_resume_rejects_artifact_mutation(tmp_path):
    labels = _labels_module()
    path, payload = _write_selected_fixture(tmp_path / "selected")
    artifact_path = path.parent / payload["artifacts"][0]["path"]
    artifact_path.write_bytes(b"different")

    with pytest.raises(ValueError, match="artifact digest"):
        labels.load_resumable_selected_manifest(
            path,
            expected_lineage=_selected_lineage(),
        )


def test_selected_manifest_rejects_confirmation_partition(tmp_path):
    labels = _labels_module()
    artifact = labels.write_selected_trajectory_artifact(
        tmp_path,
        2000,
        _selected_dataset(),
    )
    lineage = _selected_lineage()
    lineage["partition"] = "confirmation"

    with pytest.raises(ValueError, match="confirmation"):
        labels.write_selected_manifest(
            tmp_path,
            lineage=lineage,
            artifacts=[artifact],
        )


def _runner_module():
    return import_module(
        "paper10_geojepa_mpc.experiments.run_pcc_v1_1_selected_labels"
    )


def _runner_cli_args(tmp_path: Path, *, partition: str) -> list[str]:
    return [
        "--registry",
        str(tmp_path / "registry.json"),
        "--partition",
        partition,
        "--seeds",
        "2000",
        "--checkpoint-root",
        str(tmp_path / "checkpoints"),
        "--model-seed",
        "5101",
        "--ensemble-size",
        "3",
        "--policy-round",
        "1",
        "--compute-mode",
        "matched",
        "--reference-checkpoint",
        str(tmp_path / "reference.pt"),
        "--env-source",
        "paper9",
        "--prepared-dir",
        str(tmp_path),
        "--states-per-trajectory",
        "2",
        "--max-workers",
        "1",
        "--device",
        "cpu",
        "--output-root",
        str(tmp_path / "selected"),
    ]


def test_selected_label_parser_rejects_confirmation_before_runtime_load(tmp_path):
    runner = _runner_module()

    with pytest.raises(SystemExit):
        runner.parse_args(
            _runner_cli_args(tmp_path, partition="confirmation")
        )


def test_selected_label_partition_is_atomic_and_resumes_without_environment(
    tmp_path,
):
    runner = _runner_module()
    root = tmp_path / "selected"
    env_calls = []

    def env_factory():
        env_calls.append("created")
        return _TinyPairedEnv()

    kwargs = {
        "output_root": root,
        "lineage": _selected_lineage(),
        "trajectory_seeds": [2000],
        "n_states": 2,
        "horizons": (1, 3, 5),
        "gamma": 0.99,
        "env_factory": env_factory,
        "base_policy_factory": lambda _env: _FixedBasePolicy(
            selected=2,
            reference=1,
        ),
        "continuation_policy_factory": lambda _env: (lambda *_: 0),
        "metric_reader": _read_metrics,
        "state_attrs": _TINY_STATE_ATTRS,
        "max_workers": 1,
    }
    payload = runner.run_selected_label_partition(**kwargs, resume=False)

    assert payload["trajectory_seeds"] == [2000]
    assert env_calls == ["created"]
    assert (root / "seed_2000" / "trajectory_2000.npz").is_file()
    assert (root / "seed_2000" / "manifest.json").is_file()

    kwargs["env_factory"] = lambda: pytest.fail(
        "resume must not load an environment for a completed seed"
    )
    resumed = runner.run_selected_label_partition(**kwargs, resume=True)

    assert resumed == payload


def test_selected_label_partition_refuses_nonresume_overwrite_before_generation(
    tmp_path,
):
    runner = _runner_module()
    root = tmp_path / "selected"
    kwargs = {
        "output_root": root,
        "lineage": _selected_lineage(),
        "trajectory_seeds": [2000],
        "n_states": 1,
        "horizons": (1, 3, 5),
        "gamma": 0.99,
        "env_factory": _TinyPairedEnv,
        "base_policy_factory": lambda _env: _FixedBasePolicy(
            selected=2,
            reference=1,
        ),
        "continuation_policy_factory": lambda _env: (lambda *_: 0),
        "metric_reader": _read_metrics,
        "state_attrs": _TINY_STATE_ATTRS,
        "max_workers": 1,
    }
    runner.run_selected_label_partition(**kwargs, resume=False)
    artifact = root / "seed_2000" / "trajectory_2000.npz"
    original = artifact.read_bytes()
    kwargs["env_factory"] = lambda: pytest.fail(
        "occupied output must be rejected before environment creation"
    )

    with pytest.raises(ValueError, match="already exists"):
        runner.run_selected_label_partition(**kwargs, resume=False)

    assert artifact.read_bytes() == original
