import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    build_checkpoint_reference_policy_factory,
    build_neighbour_feature_matrix,
    derive_continuation_seed,
    evaluate_candidate_objectives,
    evaluate_paired_objectives,
    generate_label_partition,
    generate_pcc_value_label_dataset,
    write_label_manifest,
    write_trajectory_artifact,
)


class BatchTrackingReferenceAdapter:
    def __init__(self):
        self.batch_sizes = []

    def assert_compatible(self, n_blocks):
        assert int(n_blocks) == 6

    def batch_predict(self, block_features, global_features, actions):
        actions = np.asarray(actions, dtype=np.int64)
        self.batch_sizes.append(len(actions))
        return (
            np.asarray(block_features, dtype=np.float32).copy(),
            np.asarray(global_features, dtype=np.float32).copy(),
            actions.astype(np.float32),
            {},
        )


class SixActionReferenceEnv:
    n_blocks = 6

    def _get_block_features(self):
        return np.zeros((6, 2), dtype=np.float32)

    def _get_global_features(self):
        return np.zeros(5, dtype=np.float32)

    def action_masks(self):
        return np.ones(6, dtype=bool)


def test_checkpoint_reference_factory_uses_bounded_screening_batches(monkeypatch):
    from paper10_geojepa_mpc.planning.paper9_adapter import (
        TorchCheckpointMPCAdapter,
    )

    adapter = BatchTrackingReferenceAdapter()
    monkeypatch.setattr(
        TorchCheckpointMPCAdapter,
        "from_checkpoint",
        classmethod(lambda cls, checkpoint, device: adapter),
    )
    factory = build_checkpoint_reference_policy_factory(
        "unused.pt",
        device="cpu",
        horizon=1,
        top_k=3,
        gamma=0.99,
        screening_batch_size=2,
    )

    action = factory(SixActionReferenceEnv())(
        SixActionReferenceEnv(),
        np.random.default_rng(4),
    )

    assert action == 5
    assert max(adapter.batch_sizes) <= 3


class TinyObjectiveEnv:
    def __init__(self):
        self.n_blocks = 3
        self.block_adj = [
            np.array([1]),
            np.array([0, 2]),
            np.array([], dtype=np.int64),
        ]
        self.value = 0
        self.step_count = 0
        self.max_steps = 8

    def reset(self, seed=None):
        self.value = 0
        self.step_count = 0
        return self._get_global_features(), self.metrics()

    def metrics(self):
        return {
            "avg_slope": 10.0 - self.value,
            "contiguity": self.value / 10.0,
            "baimu_area_ha": 100.0 + self.value,
        }

    def _get_block_features(self):
        return np.asarray(
            [
                [1.0, self.value],
                [3.0, self.value],
                [8.0, self.value],
            ],
            dtype=np.float32,
        )

    def _get_global_features(self):
        return np.asarray([self.step_count, self.value], dtype=np.float32)

    def action_masks(self):
        return np.ones(self.n_blocks, dtype=bool)

    def step(self, action):
        self.value += int(action)
        self.step_count += 1
        terminated = self.step_count >= self.max_steps
        return None, float(action), terminated, False, self.metrics()


def test_candidate_labels_record_horizons_and_restore_environment():
    env = TinyObjectiveEnv()

    result = evaluate_candidate_objectives(
        env=env,
        candidate_action=2,
        horizons=(1, 3, 5),
        gamma=1.0,
        continuation_policy=lambda *_: 1,
        rng=np.random.default_rng(7),
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    assert result.shape == (3, 4)
    assert result[:, 0].tolist() == [2.0, 4.0, 6.0]
    assert env.value == 0 and env.step_count == 0


def test_neighbour_features_are_built_from_block_adjacency():
    env = TinyObjectiveEnv()
    block = env._get_block_features()[:, :1]

    neighbour = build_neighbour_feature_matrix(env, block)

    np.testing.assert_allclose(neighbour, [[3.0], [4.5], [0.0]])


def test_continuation_seed_is_stable_and_action_specific():
    first = derive_continuation_seed(1000, 3, 7)
    second = derive_continuation_seed(1000, 3, 7)

    assert first == second
    assert first != derive_continuation_seed(1000, 3, 8)


def test_candidate_and_reference_use_common_continuation_random_numbers():
    env = TinyObjectiveEnv()
    draws = []

    def stochastic_policy(runtime_env, rng):
        action = int(rng.integers(0, runtime_env.n_blocks))
        draws.append(action)
        return action

    paired = evaluate_paired_objectives(
        env=env,
        candidate_action=2,
        reference_action=0,
        horizons=(1, 3),
        gamma=1.0,
        continuation_policy=stochastic_policy,
        continuation_seed=derive_continuation_seed(1000, 0, 2),
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    assert paired.candidate.shape == (2, 4)
    assert paired.reference.shape == (2, 4)
    assert draws[:2] == draws[2:]
    assert env.value == 0 and env.step_count == 0


def test_generated_dataset_has_paired_multi_objective_schema():
    env = TinyObjectiveEnv()

    dataset = generate_pcc_value_label_dataset(
        env=env,
        n_states=2,
        candidate_actions=2,
        horizons=(1, 3),
        gamma=1.0,
        trajectory_seed=1000,
        candidate_selector=lambda runtime_env, valid, count, rng: valid[-count:],
        reference_policy=lambda *_: 0,
        continuation_policy=lambda *_: 1,
        advance_policy=lambda *_: 1,
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    assert dataset["states_bf"].shape == (2, 3, 2)
    assert dataset["states_neighbor_bf"].shape == (2, 3, 2)
    assert dataset["states_gf"].shape == (2, 2)
    assert dataset["actions"].shape == (2, 2)
    assert dataset["objective_returns"].shape == (2, 2, 2, 4)
    assert dataset["reference_objective_returns"].shape == (2, 2, 2, 4)
    assert dataset["candidate_next_bf"].shape == (2, 2, 3, 2)
    assert dataset["candidate_next_gf"].shape == (2, 2, 2)
    assert dataset["reference_next_bf"].shape == (2, 2, 3, 2)
    assert dataset["reference_next_gf"].shape == (2, 2, 2)
    assert dataset["executable_targets"].shape == (2, 2)
    assert dataset["continuation_seeds"].shape == (2, 2)
    np.testing.assert_array_equal(dataset["trajectory_ids"], [1000, 1000])
    np.testing.assert_array_equal(dataset["state_steps"], [0, 1])
    np.testing.assert_array_equal(dataset["horizons"], [1, 3])
    assert np.isfinite(dataset["objective_returns"]).all()


def test_executable_targets_can_include_stricter_negative_actions():
    env = TinyObjectiveEnv()

    dataset = generate_pcc_value_label_dataset(
        env=env,
        n_states=1,
        candidate_actions=2,
        horizons=(1,),
        gamma=1.0,
        trajectory_seed=1000,
        candidate_selector=lambda runtime_env, valid, count, rng: valid[-count:],
        reference_policy=lambda *_: 0,
        continuation_policy=lambda *_: 1,
        executable_target_mask_fn=lambda runtime_env: np.array(
            [True, False, True]
        ),
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    np.testing.assert_array_equal(dataset["actions"], [[1, 2]])
    np.testing.assert_array_equal(dataset["executable_targets"], [[0.0, 1.0]])


def test_trajectory_artifact_and_manifest_record_content_digests(tmp_path):
    env = TinyObjectiveEnv()
    dataset = generate_pcc_value_label_dataset(
        env=env,
        n_states=1,
        candidate_actions=2,
        horizons=(1, 3),
        gamma=1.0,
        trajectory_seed=1000,
        candidate_selector=lambda runtime_env, valid, count, rng: valid[-count:],
        reference_policy=lambda *_: 0,
        continuation_policy=lambda *_: 1,
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    artifact = write_trajectory_artifact(tmp_path, 1000, dataset)
    manifest = write_label_manifest(
        tmp_path,
        protocol_id="fixture",
        partition="train",
        artifacts=[artifact],
        continuation_policy={"name": "paper9_mpc", "digest": "abc"},
        horizons=(1, 3),
    )

    assert len(artifact["sha256"]) == 64
    assert (tmp_path / artifact["path"]).exists()
    assert len(manifest["manifest_digest"]) == 64
    assert manifest["trajectory_seeds"] == [1000]
    assert (tmp_path / "manifest.json").exists()


def test_manifest_rejects_confirmation_partition(tmp_path):
    with pytest.raises(ValueError, match="confirmation"):
        write_label_manifest(
            tmp_path,
            protocol_id="pcc_v1",
            partition="confirmation",
            artifacts=[],
            continuation_policy={"name": "paper9_mpc", "digest": "abc"},
            horizons=(1, 3, 5),
        )


def test_partition_generation_uses_each_declared_trajectory_once(tmp_path):
    registry = {
        "protocol_id": "fixture",
        "partitions": {"train": [1000, 1001]},
    }
    created = []

    def env_factory():
        created.append(TinyObjectiveEnv())
        return created[-1]

    manifest = generate_label_partition(
        registry=registry,
        partition="train",
        output_dir=tmp_path,
        env_factory=env_factory,
        policy_factory=lambda env: (lambda *_: 0),
        n_states=1,
        candidate_actions=2,
        horizons=(1, 3),
        gamma=1.0,
        candidate_selector=lambda runtime_env, valid, count, rng: valid[-count:],
        continuation_policy_factory=lambda env: (lambda *_: 1),
        advance_policy_factory=lambda env: (lambda *_: 1),
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    assert len(created) == 2
    assert manifest["trajectory_seeds"] == [1000, 1001]
    assert len(manifest["artifacts"]) == 2


def test_partition_generation_allows_only_declared_smoke_subset(tmp_path):
    registry = {
        "protocol_id": "fixture",
        "partitions": {"train": [1000, 1001]},
    }
    created = []

    manifest = generate_label_partition(
        registry=registry,
        partition="train",
        trajectory_seeds=[1001],
        output_dir=tmp_path,
        env_factory=lambda: created.append(TinyObjectiveEnv()) or created[-1],
        policy_factory=lambda env: (lambda *_: 0),
        n_states=1,
        candidate_actions=1,
        horizons=(1,),
        gamma=1.0,
        metric_reader=lambda runtime_env: runtime_env.metrics(),
        state_attrs=("value", "step_count"),
    )

    assert len(created) == 1
    assert manifest["trajectory_seeds"] == [1001]
    with pytest.raises(ValueError, match="declared partition"):
        generate_label_partition(
            registry=registry,
            partition="train",
            trajectory_seeds=[9999],
            output_dir=tmp_path / "bad",
            env_factory=TinyObjectiveEnv,
            policy_factory=lambda env: (lambda *_: 0),
            n_states=1,
            candidate_actions=1,
            horizons=(1,),
            gamma=1.0,
            metric_reader=lambda runtime_env: runtime_env.metrics(),
            state_attrs=("value", "step_count"),
        )
