import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.run_pcc_rollouts import (
    _load_paper9_mpc_select_action,
)
from paper10_geojepa_mpc.planning.paper9_memory_efficient import (
    memory_efficient_mpc_select_action,
)


class TrackingAdapter:
    def __init__(self):
        self.batch_sizes = []

    def batch_predict(self, block_features, global_features, actions):
        actions = np.asarray(actions, dtype=np.int64)
        self.batch_sizes.append(len(actions))
        next_block = np.asarray(block_features, dtype=np.float32).copy()
        next_global = np.asarray(global_features, dtype=np.float32).copy()
        rewards = actions.astype(np.float32)
        return next_block, next_global, rewards, {}


class StatefulAdapter:
    def batch_predict(self, block_features, global_features, actions):
        block = np.asarray(block_features, dtype=np.float32).copy()
        global_state = np.asarray(global_features, dtype=np.float32).copy()
        actions = np.asarray(actions, dtype=np.int64)
        rows = np.arange(len(actions))
        selected = block[rows, actions, 0].copy()
        rewards = (
            0.7 * actions.astype(np.float32)
            + global_state[:, 0]
            - 0.2 * selected
        )
        block[rows, actions, 0] += 0.1 * (actions + 1)
        global_state[:, 0] += 0.05 * (actions + 1)
        global_state[:, 4] += 0.01 * ((actions % 3) - 1)
        return block, global_state, rewards, {}


def test_chunked_screening_limits_state_replication_and_selects_best_action():
    adapter = TrackingAdapter()
    block = np.zeros((6, 2), dtype=np.float32)
    global_features = np.zeros(5, dtype=np.float32)

    action, _ = memory_efficient_mpc_select_action(
        adapter,
        block,
        global_features,
        np.ones(6, dtype=bool),
        horizon=1,
        top_k=3,
        screening_batch_size=2,
        rng=np.random.default_rng(1),
    )

    assert action == 5
    assert max(adapter.batch_sizes) <= 3


def test_chunked_selector_matches_original_paper9_action():
    block = np.zeros((6, 2), dtype=np.float32)
    global_features = np.zeros(5, dtype=np.float32)
    mask = np.ones(6, dtype=bool)
    original = _load_paper9_mpc_select_action()

    expected, _ = original(
        TrackingAdapter(),
        block,
        global_features,
        mask,
        horizon=3,
        top_k=3,
        gamma=0.99,
        n_rollouts=1,
        continuation="random",
        scoring="reward",
        rng=np.random.default_rng(9),
    )
    observed, _ = memory_efficient_mpc_select_action(
        TrackingAdapter(),
        block,
        global_features,
        mask,
        horizon=3,
        top_k=3,
        gamma=0.99,
        n_rollouts=1,
        continuation="random",
        scoring="reward",
        screening_batch_size=2,
        rng=np.random.default_rng(9),
    )

    assert observed == expected


@pytest.mark.parametrize(
    ("continuation", "scoring", "n_rollouts"),
    [
        ("random", "reward", 1),
        ("random", "slope", 2),
        ("greedy", "reward", 2),
    ],
)
def test_chunked_selector_preserves_stateful_paper9_semantics(
    continuation,
    scoring,
    n_rollouts,
):
    rng = np.random.default_rng(13)
    block = rng.normal(size=(8, 3)).astype(np.float32)
    global_features = rng.normal(size=5).astype(np.float32)
    mask = np.array([True, False, True, True, False, True, True, True])
    original = _load_paper9_mpc_select_action()
    kwargs = {
        "horizon": 4,
        "top_k": 4,
        "gamma": 0.93,
        "n_rollouts": n_rollouts,
        "continuation": continuation,
        "greedy_sample": 3,
        "scoring": scoring,
    }

    expected_action, expected_info = original(
        StatefulAdapter(),
        block,
        global_features,
        mask,
        rng=np.random.default_rng(29),
        **kwargs,
    )
    observed_action, observed_info = memory_efficient_mpc_select_action(
        StatefulAdapter(),
        block,
        global_features,
        mask,
        screening_batch_size=2,
        rng=np.random.default_rng(29),
        **kwargs,
    )

    assert observed_action == expected_action
    np.testing.assert_allclose(
        [observed_info["best_cumrew"], observed_info["mean_cumrew"]],
        [expected_info["best_cumrew"], expected_info["mean_cumrew"]],
        rtol=0.0,
        atol=0.0,
    )
