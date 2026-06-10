from types import SimpleNamespace
import json
import sys

import numpy as np

from paper10_geojepa_mpc.experiments import run_e0_env_rollout_smoke
from paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke import (
    _build_multiseed_result,
    _partial_output_path,
    _run_episode,
    _write_multiseed_progress,
)


class TinyRolloutEnv:
    def __init__(self):
        self.max_steps = 3
        self.n_blocks = 4
        self.step_count = 0

    def reset(self, seed=None):
        self.step_count = 0

    def _get_block_features(self):
        return np.zeros((self.n_blocks, 17), dtype=np.float32)

    def _get_global_features(self):
        return np.zeros(12, dtype=np.float32)

    def action_masks(self):
        return np.ones(self.n_blocks, dtype=bool)

    def step(self, action):
        self.step_count += 1
        terminated = self.step_count >= self.max_steps
        truncated = False
        info = {
            "completed_swaps": 1,
            "slope_change_pct": -float(self.step_count),
            "cont_change": 0.1,
            "baimu_area_change_ha": -2.0,
        }
        return None, float(action), terminated, truncated, info


def test_run_episode_passes_scoring_mode_to_mpc_selector():
    seen = {}

    def fake_mpc_select_action(
        adapter,
        block_features,
        global_features,
        action_mask,
        horizon,
        top_k,
        gamma,
        n_rollouts,
        continuation,
        scoring,
        rng,
    ):
        seen["scoring"] = scoring
        return 2, {"n_valid": int(action_mask.sum()), "n_candidates": top_k, "best_cumrew": 1.0}

    args = SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=5,
        top_k=2,
        gamma=0.99,
        mask_mode="base",
        scoring="slope",
        model_score_mode="reward",
        model_value_weight=0.5,
    )

    result = _run_episode(
        TinyRolloutEnv(),
        adapter=object(),
        mpc_select_action=fake_mpc_select_action,
        args=args,
        seed=0,
        rollout_limit=1,
    )

    assert seen["scoring"] == "slope"
    assert result["scoring"] == "slope"


def test_run_episode_passes_n_rollouts_to_mpc_selector():
    seen = {}

    def fake_mpc_select_action(
        adapter,
        block_features,
        global_features,
        action_mask,
        horizon,
        top_k,
        gamma,
        n_rollouts,
        continuation,
        scoring,
        rng,
    ):
        seen["n_rollouts"] = n_rollouts
        return 2, {"n_valid": int(action_mask.sum()), "n_candidates": top_k, "best_cumrew": 1.0}

    args = SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=5,
        top_k=2,
        gamma=0.99,
        n_rollouts=3,
        mask_mode="base",
        scoring="reward",
        model_score_mode="reward",
        model_value_weight=0.5,
    )

    result = _run_episode(
        TinyRolloutEnv(),
        adapter=object(),
        mpc_select_action=fake_mpc_select_action,
        args=args,
        seed=0,
        rollout_limit=1,
    )

    assert seen["n_rollouts"] == 3
    assert result["n_rollouts"] == 3


def test_run_episode_records_model_score_mode_metadata():
    def fake_mpc_select_action(
        adapter,
        block_features,
        global_features,
        action_mask,
        horizon,
        top_k,
        gamma,
        n_rollouts,
        continuation,
        scoring,
        rng,
    ):
        return 1, {"n_valid": int(action_mask.sum()), "n_candidates": top_k, "best_cumrew": 2.0}

    args = SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=1,
        top_k=2,
        gamma=0.99,
        mask_mode="base",
        scoring="reward",
        model_score_mode="blend",
        model_value_weight=0.25,
    )

    result = _run_episode(
        TinyRolloutEnv(),
        adapter=object(),
        mpc_select_action=fake_mpc_select_action,
        args=args,
        seed=0,
        rollout_limit=1,
    )

    assert result["model_score_mode"] == "blend"
    assert result["model_value_weight"] == 0.25


def test_run_episode_passes_value_filter_candidate_scoring_metadata():
    seen = {}

    def fake_value_filter_select_action(
        adapter,
        block_features,
        global_features,
        action_mask,
        horizon,
        top_k,
        gamma,
        n_rollouts,
        continuation,
        scoring,
        candidate_score_mode,
        candidate_value_weight,
        random_continuation_mode,
        stable_candidate_order,
        rng,
    ):
        seen["candidate_score_mode"] = candidate_score_mode
        seen["candidate_value_weight"] = candidate_value_weight
        seen["random_continuation_mode"] = random_continuation_mode
        seen["stable_candidate_order"] = stable_candidate_order
        return 1, {
            "selector": "value_filter",
            "n_valid": int(action_mask.sum()),
            "n_candidates": top_k,
            "best_cumrew": 2.0,
        }

    args = SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=3,
        top_k=2,
        gamma=0.99,
        mask_mode="base",
        scoring="reward",
        model_score_mode="reward",
        model_value_weight=0.5,
        selector="value_filter",
        candidate_score_mode="value",
        candidate_value_weight=0.75,
        random_continuation_mode="common",
        stable_candidate_order=True,
    )

    result = _run_episode(
        TinyRolloutEnv(),
        adapter=object(),
        mpc_select_action=fake_value_filter_select_action,
        args=args,
        seed=0,
        rollout_limit=1,
    )

    assert seen["candidate_score_mode"] == "value"
    assert seen["candidate_value_weight"] == 0.75
    assert result["selector"] == "value_filter"
    assert result["candidate_score_mode"] == "value"
    assert result["candidate_value_weight"] == 0.75
    assert seen["random_continuation_mode"] == "common"
    assert result["random_continuation_mode"] == "common"
    assert seen["stable_candidate_order"] is True
    assert result["stable_candidate_order"] is True


def test_run_episode_reports_step_progress_at_interval_and_final_step():
    progress = []

    def fake_mpc_select_action(
        adapter,
        block_features,
        global_features,
        action_mask,
        horizon,
        top_k,
        gamma,
        n_rollouts,
        continuation,
        scoring,
        rng,
    ):
        return 1, {"n_valid": int(action_mask.sum()), "n_candidates": top_k, "best_cumrew": 2.0}

    args = SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=1,
        top_k=2,
        gamma=0.99,
        mask_mode="base",
        scoring="reward",
        model_score_mode="reward",
        model_value_weight=0.5,
    )

    _run_episode(
        TinyRolloutEnv(),
        adapter=object(),
        mpc_select_action=fake_mpc_select_action,
        args=args,
        seed=7,
        rollout_limit=3,
        progress_callback=progress.append,
        progress_interval=2,
    )

    assert [item["step"] for item in progress] == [2, 3]
    assert progress[-1]["seed"] == 7
    assert progress[-1]["rollout_limit"] == 3
    assert progress[-1]["total_reward"] == 3.0


def _tiny_episode(seed: int) -> dict:
    return {
        "seed": seed,
        "horizon": 5,
        "top_k": 50,
        "total_reward": 1.5 + seed,
        "elapsed_sec": 0.25,
        "steps": [
            {
                "step": 1,
                "action": seed + 10,
                "reward": 1.5 + seed,
                "completed_swaps": 1,
                "select_time_sec": 0.1,
                "slope_change_pct": -1.0 - seed,
                "cont_change": 0.01,
                "baimu_area_change_ha": -20.0,
            }
        ],
    }


def _multiseed_args(tmp_path):
    return SimpleNamespace(
        checkpoint="checkpoint.pt",
        prepared_dir="prepared",
        horizon=5,
        top_k=50,
        n_rollouts=1,
        mask_mode="executable",
        scoring="reward",
        selector="value_filter",
        model_score_mode="reward",
        model_value_weight=0.5,
        candidate_score_mode="blend",
        candidate_value_weight=0.1,
        random_continuation_mode="independent",
        stable_candidate_order=False,
        output=str(tmp_path / "rollout.json"),
    )


def test_partial_output_path_uses_partial_json_name(tmp_path):
    path = _partial_output_path(str(tmp_path / "rollout.json"))

    assert path == tmp_path / "rollout.partial.json"


def test_multiseed_result_tracks_completed_and_pending_seeds(tmp_path):
    result = _build_multiseed_result(
        _multiseed_args(tmp_path),
        seeds=[0, 1, 2],
        rollout_limit=100,
        env_max_steps=100,
        episodes=[_tiny_episode(0), _tiny_episode(2)],
        started_at=0.0,
        complete=False,
    )

    assert result["complete"] is False
    assert result["completed_seeds"] == [0, 2]
    assert result["pending_seeds"] == [1]
    assert result["aggregate"]["n_episodes"] == 2


def test_write_multiseed_progress_writes_partial_file(tmp_path):
    path = _write_multiseed_progress(
        _multiseed_args(tmp_path),
        seeds=[0, 1],
        rollout_limit=100,
        env_max_steps=100,
        episodes=[_tiny_episode(0)],
        started_at=0.0,
        complete=False,
    )

    assert path == tmp_path / "rollout.partial.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["complete"] is False
    assert data["completed_seeds"] == [0]
    assert data["pending_seeds"] == [1]


def test_parse_args_accepts_neijiang_env_source(monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_e0_env_rollout_smoke.py",
            "--env-source",
            "neijiang",
            "--prepared-dir",
            str(tmp_path),
        ],
    )

    args = run_e0_env_rollout_smoke.parse_args()

    assert args.env_source == "neijiang"
    assert args.prepared_dir == str(tmp_path)


def test_make_rollout_env_can_load_neijiang_env_factory(tmp_path):
    env_script = tmp_path / "county_env_neijiang.py"
    env_script.write_text(
        "class TinyEnv:\n"
        "    n_blocks = 3711\n"
        "def make_neijiang_env(**kwargs):\n"
        "    return TinyEnv()\n",
        encoding="utf-8",
    )
    args = SimpleNamespace(env_source="neijiang", prepared_dir=str(tmp_path))

    env = run_e0_env_rollout_smoke._make_rollout_env(args)

    assert env.n_blocks == 3711
