import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.run_pcc_rollouts import (
    load_resumable_results,
    run_policy_episode,
    select_without_execution,
    write_seed_result_atomic,
)


class SpyEnv:
    def __init__(self):
        self.n_blocks = 3
        self.block_adj = [np.array([1]), np.array([0, 2]), np.array([1])]
        self.step_calls = []
        self.step_count = 0
        self.value = 0
        self.max_steps = 3

    def reset(self, seed=None):
        self.step_calls = []
        self.step_count = 0
        self.value = 0
        return None, self.metrics()

    def metrics(self):
        return {
            "avg_slope": 10.0 - self.value,
            "contiguity": self.value / 10.0,
            "baimu_area_ha": 100.0 + self.value,
        }

    def _get_block_features(self):
        return np.asarray([[1.0], [2.0], [3.0]], dtype=np.float32)

    def _get_global_features(self):
        return np.asarray([self.step_count, self.value], dtype=np.float32)

    def action_masks(self):
        return np.ones(self.n_blocks, dtype=bool)

    def step(self, action):
        self.step_calls.append(int(action))
        self.value += int(action)
        self.step_count += 1
        done = self.step_count >= self.max_steps
        return None, float(action), done, False, self.metrics()


def test_selection_never_steps_real_environment():
    env = SpyEnv()

    action, info = select_without_execution(
        env=env,
        selector=lambda **_: (2, {"fallback": False}),
    )

    assert action == 2
    assert info["fallback"] is False
    assert env.step_calls == []


def test_selection_guard_blocks_counterfactual_step_from_closure():
    env = SpyEnv()

    with pytest.raises(RuntimeError, match="selection"):
        select_without_execution(
            env=env,
            selector=lambda **_: (env.step(1), {}),
        )
    assert env.step_calls == []


class RecordingPolicy:
    def __init__(self):
        self.observed = []

    def select(self, state):
        return 2, {
            "reference_action": 0,
            "fallback": False,
            "joint_q": 1.0,
            "online_multiplier": [1.0] * 4,
            "member_evaluations": 3,
            "model_forward_count": 1,
            "selected_predicted_mean": [0.0] * 4,
            "selected_base_scale": [1.0] * 4,
            "unexecuted_real_reward_queries": 0,
        }

    def observe(self, transition):
        self.observed.append(transition)


def test_episode_executes_one_step_per_selection_and_observes_only_executed_action():
    env = SpyEnv()
    policy = RecordingPolicy()

    result = run_policy_episode(
        env=env,
        policy=policy,
        seed=4000,
        rollout_steps=2,
        metric_reader=lambda runtime_env: runtime_env.metrics(),
    )

    assert env.step_calls == [2, 2]
    assert len(result["steps"]) == 2
    assert len(policy.observed) == 2
    assert all(row["action"] == 2 for row in policy.observed)
    assert all("reference_outcome" not in row for row in policy.observed)


def test_seed_result_is_atomic_and_resume_checks_digests(tmp_path):
    path = tmp_path / "rollouts.json"
    write_seed_result_atomic(
        path,
        seed_result={"seed": 4000, "steps": []},
        registry_digest="registry",
        checkpoint_digests=["member0"],
    )

    loaded = load_resumable_results(
        path,
        registry_digest="registry",
        checkpoint_digests=["member0"],
    )

    assert loaded["completed_seeds"] == [4000]
    with pytest.raises(ValueError, match="digest"):
        load_resumable_results(
            path,
            registry_digest="changed",
            checkpoint_digests=["member0"],
        )
