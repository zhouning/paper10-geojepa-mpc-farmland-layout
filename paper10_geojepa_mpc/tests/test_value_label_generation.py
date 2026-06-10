import numpy as np
import pytest

from paper10_geojepa_mpc.experiments import value_label_generation
from paper10_geojepa_mpc.experiments.value_label_generation import (
    build_adapter_generation_components,
    discounted_return,
    evaluate_first_action_return,
    generate_value_label_dataset,
    make_adapter_candidate_selector,
    make_frontier_random_candidate_selector,
    make_adapter_top1_policy,
    make_npz_progress_callback,
    requires_adapter_for_generation,
    select_top_scored_actions,
)


class TinyValueEnv:
    def __init__(self):
        self.n_blocks = 4
        self.max_steps = 5
        self.step_count = 0
        self.score = 0.0
        self.land_use = np.array([1, 2, 1, 2], dtype=np.int64)

    def reset(self, seed=None):
        self.step_count = 0
        self.score = 0.0
        return self._get_obs(), {}

    def _get_obs(self):
        return np.array([self.step_count, self.score], dtype=np.float32)

    def _get_block_features(self):
        out = np.zeros((self.n_blocks, 17), dtype=np.float32)
        out[:, 0] = np.arange(self.n_blocks, dtype=np.float32)
        out[:, 1] = self.step_count
        out[:, 2] = self.score
        return out

    def _get_global_features(self):
        out = np.zeros(12, dtype=np.float32)
        out[0] = self.step_count
        out[1] = self.score
        return out

    def action_masks(self):
        mask = np.ones(self.n_blocks, dtype=bool)
        if self.step_count >= self.max_steps:
            mask[:] = False
        return mask

    def step(self, action):
        reward = float(action) - 1.0
        self.score += reward
        self.step_count += 1
        terminated = self.step_count >= self.max_steps
        truncated = False
        info = {"score": self.score}
        return self._get_obs(), reward, terminated, truncated, info


def test_discounted_return_sums_rewards_with_gamma():
    assert discounted_return([2.0, 3.0, 4.0], gamma=0.5) == pytest.approx(4.5)


def test_evaluate_first_action_return_restores_env_after_rollout():
    env = TinyValueEnv()
    env.reset(seed=3)
    env.step(2)
    before_bf = env._get_block_features().copy()
    before_gf = env._get_global_features().copy()

    value = evaluate_first_action_return(
        env,
        first_action=3,
        horizon=3,
        gamma=0.5,
        rng=np.random.default_rng(7),
        action_mask_fn=lambda e: e.action_masks(),
    )

    assert value >= 0.0
    np.testing.assert_array_equal(env._get_block_features(), before_bf)
    np.testing.assert_array_equal(env._get_global_features(), before_gf)
    assert env.step_count == 1
    assert env.score == 1.0


def test_generate_value_label_dataset_has_training_schema():
    env = TinyValueEnv()

    dataset = generate_value_label_dataset(
        env,
        n_states=3,
        candidate_actions=2,
        label_horizon=2,
        gamma=0.9,
        seed=11,
        action_mask_fn=lambda e: e.action_masks(),
    )

    assert set(dataset) == {
        "states_bf",
        "states_gf",
        "actions",
        "returns",
        "one_step_rewards",
        "state_steps",
        "n_valid_actions",
    }
    assert dataset["states_bf"].shape == (3, 4, 17)
    assert dataset["states_gf"].shape == (3, 12)
    assert dataset["actions"].shape == (3, 2)
    assert dataset["returns"].shape == (3, 2)
    assert dataset["one_step_rewards"].shape == (3, 2)
    assert dataset["actions"].dtype == np.int64
    assert dataset["returns"].dtype == np.float32
    assert np.all(np.isfinite(dataset["returns"]))


def test_select_top_scored_actions_returns_actions_sorted_by_score():
    valid_actions = np.array([10, 11, 12, 13], dtype=np.int64)
    scores = np.array([0.1, 0.9, 0.2, 0.8], dtype=np.float32)

    actions, selected_scores = select_top_scored_actions(
        valid_actions, scores, candidate_actions=3
    )

    np.testing.assert_array_equal(actions, np.array([11, 13, 12], dtype=np.int64))
    np.testing.assert_allclose(selected_scores, np.array([0.9, 0.8, 0.2]))


def test_generate_value_label_dataset_can_use_frontier_candidates_and_policies():
    env = TinyValueEnv()

    def candidate_selector(runtime_env, block_features, global_features, valid, k, rng):
        scores = valid.astype(np.float32)
        return select_top_scored_actions(valid, scores, k)

    def choose_best(runtime_env, block_features, global_features, valid, rng):
        return int(valid.max())

    dataset = generate_value_label_dataset(
        env,
        n_states=3,
        candidate_actions=2,
        label_horizon=2,
        gamma=1.0,
        seed=13,
        action_mask_fn=lambda e: e.action_masks(),
        candidate_selector=candidate_selector,
        advance_policy=choose_best,
        continuation_policy=choose_best,
    )

    np.testing.assert_array_equal(
        dataset["actions"],
        np.array([[3, 2], [3, 2], [3, 2]], dtype=np.int64),
    )
    np.testing.assert_allclose(
        dataset["candidate_scores"],
        np.array([[3.0, 2.0], [3.0, 2.0], [3.0, 2.0]], dtype=np.float32),
    )
    np.testing.assert_array_equal(dataset["state_steps"], np.array([0, 1, 2]))
    np.testing.assert_allclose(dataset["returns"][0], np.array([4.0, 3.0]))


def test_generate_value_label_dataset_reports_partial_prefixes_by_interval():
    env = TinyValueEnv()
    partials = []

    dataset = generate_value_label_dataset(
        env,
        n_states=3,
        candidate_actions=2,
        label_horizon=2,
        gamma=0.9,
        seed=11,
        action_mask_fn=lambda e: e.action_masks(),
        progress_callback=lambda generated, prefix: partials.append(
            (generated, prefix)
        ),
        progress_every=2,
    )

    assert [generated for generated, _ in partials] == [2, 3]
    assert partials[0][1]["returns"].shape == (2, 2)
    assert partials[1][1]["returns"].shape == (3, 2)
    np.testing.assert_allclose(partials[-1][1]["returns"], dataset["returns"])


def test_npz_progress_callback_writes_partial_dataset(tmp_path):
    output = tmp_path / "labels.partial.npz"
    callback = make_npz_progress_callback(output)
    partial = {
        "states_bf": np.zeros((2, 4, 17), dtype=np.float32),
        "states_gf": np.zeros((2, 12), dtype=np.float32),
        "actions": np.ones((2, 3), dtype=np.int64),
        "returns": np.ones((2, 3), dtype=np.float32),
        "one_step_rewards": np.zeros((2, 3), dtype=np.float32),
        "state_steps": np.array([0, 1], dtype=np.int64),
        "n_valid_actions": np.array([4, 4], dtype=np.int64),
    }

    callback(2, partial)

    with np.load(output) as data:
        assert int(data["partial_generated_states"][0]) == 2
        assert data["returns"].shape == (2, 3)


class ActionScoreAdapter:
    def batch_predict(self, block_features, global_features, actions):
        rewards = np.asarray(actions, dtype=np.float32) * 0.5
        return block_features, global_features, rewards, {}


class ActionRewardValueAdapter:
    def batch_predict(self, block_features, global_features, actions):
        action_array = np.asarray(actions, dtype=np.int64)
        reward_lookup = np.asarray([0.0, 10.0, 5.0], dtype=np.float32)
        value_lookup = np.asarray([20.0, 1.0, 15.0], dtype=np.float32)
        rewards = reward_lookup[action_array]
        values = value_lookup[action_array]
        return block_features, global_features, rewards, {"value": values}


def test_adapter_candidate_selector_scores_valid_actions():
    selector = make_adapter_candidate_selector(ActionScoreAdapter())
    env = TinyValueEnv()
    valid = np.array([0, 2, 3], dtype=np.int64)

    actions, scores = selector(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        2,
        np.random.default_rng(17),
    )

    np.testing.assert_array_equal(actions, np.array([3, 2], dtype=np.int64))
    np.testing.assert_allclose(scores, np.array([1.5, 1.0], dtype=np.float32))


def test_adapter_candidate_selector_can_score_by_value_head():
    selector = make_adapter_candidate_selector(
        ActionRewardValueAdapter(),
        score_mode="value",
    )
    env = TinyValueEnv()
    valid = np.array([0, 1, 2], dtype=np.int64)

    actions, scores = selector(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        2,
        np.random.default_rng(31),
    )

    np.testing.assert_array_equal(actions, np.array([0, 2], dtype=np.int64))
    np.testing.assert_allclose(scores, np.array([20.0, 15.0], dtype=np.float32))


def test_frontier_random_candidate_selector_mixes_scored_frontier_and_random_actions():
    selector = make_frontier_random_candidate_selector(
        ActionScoreAdapter(),
        frontier_fraction=0.5,
    )
    env = TinyValueEnv()
    valid = np.array([0, 1, 2, 3, 4, 5], dtype=np.int64)

    actions, scores = selector(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        4,
        np.random.default_rng(23),
    )

    np.testing.assert_array_equal(actions[:2], np.array([5, 4], dtype=np.int64))
    assert set(actions[2:].tolist()) == {0, 2}
    np.testing.assert_allclose(scores, actions.astype(np.float32) * 0.5)


def test_adapter_top1_policy_returns_best_scored_action():
    policy = make_adapter_top1_policy(ActionScoreAdapter())
    env = TinyValueEnv()
    valid = np.array([1, 3, 2], dtype=np.int64)

    action = policy(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        np.random.default_rng(19),
    )

    assert action == 3


def test_build_adapter_generation_components_maps_modes_to_callables():
    selector, advance_policy, continuation_policy = build_adapter_generation_components(
        ActionScoreAdapter(),
        candidate_mode="frontier",
        advance_policy_name="model_top1",
        continuation_policy_name="random",
        score_batch_size=4,
    )
    env = TinyValueEnv()
    valid = np.array([0, 1, 3], dtype=np.int64)

    actions, scores = selector(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        2,
        np.random.default_rng(23),
    )

    np.testing.assert_array_equal(actions, np.array([3, 1], dtype=np.int64))
    np.testing.assert_allclose(scores, np.array([1.5, 0.5], dtype=np.float32))
    assert advance_policy(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        np.random.default_rng(29),
    ) == 3
    assert continuation_policy is None


def test_build_adapter_generation_components_maps_frontier_random_mode():
    selector, advance_policy, continuation_policy = build_adapter_generation_components(
        ActionScoreAdapter(),
        candidate_mode="frontier_random",
        advance_policy_name="random",
        continuation_policy_name="random",
        frontier_fraction=0.5,
    )
    env = TinyValueEnv()
    valid = np.array([0, 1, 2, 3, 4, 5], dtype=np.int64)

    actions, scores = selector(
        env,
        env._get_block_features(),
        env._get_global_features(),
        valid,
        4,
        np.random.default_rng(23),
    )

    np.testing.assert_array_equal(actions[:2], np.array([5, 4], dtype=np.int64))
    assert set(actions[2:].tolist()) == {0, 2}
    np.testing.assert_allclose(scores, actions.astype(np.float32) * 0.5)
    assert advance_policy is None
    assert continuation_policy is None


def test_make_label_env_can_load_neijiang_env_factory(tmp_path):
    env_script = tmp_path / "county_env_neijiang.py"
    env_script.write_text(
        "class TinyEnv:\n"
        "    n_blocks = 3711\n"
        "def make_neijiang_env(**kwargs):\n"
        "    return TinyEnv()\n",
        encoding="utf-8",
    )

    env = value_label_generation._make_label_env("neijiang", str(tmp_path))

    assert env.n_blocks == 3711


def test_build_adapter_generation_components_rejects_unknown_modes():
    with pytest.raises(ValueError, match="candidate_mode"):
        build_adapter_generation_components(
            ActionScoreAdapter(),
            candidate_mode="bad",
            advance_policy_name="random",
            continuation_policy_name="random",
        )


def test_requires_adapter_for_generation_includes_frontier_random_mode_and_model_policies():
    assert requires_adapter_for_generation("frontier", "random", "random")
    assert requires_adapter_for_generation("frontier_random", "random", "random")
    assert requires_adapter_for_generation("random", "model_top1", "random")
    assert requires_adapter_for_generation("random", "random", "model_top1")
    assert not requires_adapter_for_generation("random", "random", "random")
