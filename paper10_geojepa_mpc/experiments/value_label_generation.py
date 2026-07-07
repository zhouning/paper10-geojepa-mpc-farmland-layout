import argparse
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Callable, Iterable, Optional, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"


DEFAULT_STATE_ATTRS = (
    "land_use",
    "swapped",
    "budget_used",
    "step_count",
    "swaps_in_block",
    "n_farmland",
    "n_forest",
    "total_weighted_slope",
    "total_farm_area",
    "farmland_nbr_count",
    "total_farmland_adj",
    "_block_farm_avail",
    "_block_forest_avail",
    "baimu_count",
    "baimu_total_area",
    "prev_slope",
    "prev_cont",
    "prev_baimu_count",
    "prev_baimu_area",
)


ActionMaskFn = Callable[[object], np.ndarray]
CandidateSelectorFn = Callable[
    [object, np.ndarray, np.ndarray, np.ndarray, int, np.random.Generator],
    tuple[np.ndarray, Optional[np.ndarray]] | np.ndarray,
]
PolicyFn = Callable[
    [object, np.ndarray, np.ndarray, np.ndarray, np.random.Generator],
    int,
]
ProgressCallbackFn = Callable[[int, dict[str, np.ndarray]], None]


def discounted_return(rewards: Iterable[float], gamma: float) -> float:
    value = 0.0
    discount = 1.0
    for reward in rewards:
        value += discount * float(reward)
        discount *= float(gamma)
    return float(value)


def _state_attrs_for_env(
    env, state_attrs: Optional[Sequence[str]] = None
) -> list[str]:
    if state_attrs is not None:
        return [attr for attr in state_attrs if hasattr(env, attr)]

    attrs = [attr for attr in DEFAULT_STATE_ATTRS if hasattr(env, attr)]
    seen = set(attrs)
    for name, value in vars(env).items():
        if name in seen:
            continue
        if isinstance(value, (int, float, bool, np.integer, np.floating, np.bool_)):
            attrs.append(name)
            seen.add(name)
    return attrs


def snapshot_env(env, state_attrs: Optional[Sequence[str]] = None) -> dict:
    snap = {}
    for attr in _state_attrs_for_env(env, state_attrs):
        value = getattr(env, attr)
        if isinstance(value, np.ndarray):
            snap[attr] = value.copy()
        elif isinstance(value, (list, dict, set)):
            snap[attr] = value.copy()
        else:
            snap[attr] = value
    return snap


def restore_env(env, snap: dict) -> None:
    for attr, value in snap.items():
        current = getattr(env, attr, None)
        if isinstance(value, np.ndarray) and isinstance(current, np.ndarray):
            if current.shape == value.shape and current.dtype == value.dtype:
                current[...] = value
            else:
                setattr(env, attr, value.copy())
        elif isinstance(value, np.ndarray):
            setattr(env, attr, value.copy())
        elif isinstance(value, (list, dict, set)):
            setattr(env, attr, value.copy())
        else:
            setattr(env, attr, value)


def _default_action_mask(env) -> np.ndarray:
    return np.asarray(env.action_masks(), dtype=bool)


def _valid_actions(env, action_mask_fn: Optional[ActionMaskFn]) -> np.ndarray:
    mask_fn = action_mask_fn or _default_action_mask
    return np.where(np.asarray(mask_fn(env), dtype=bool))[0].astype(np.int64)


def _step_reward(env, action: int) -> tuple[float, bool]:
    _, reward, terminated, truncated, _ = env.step(int(action))
    return float(reward), bool(terminated or truncated)


def select_top_scored_actions(
    valid_actions: np.ndarray, scores: np.ndarray, candidate_actions: int
) -> tuple[np.ndarray, np.ndarray]:
    if candidate_actions <= 0:
        raise ValueError("candidate_actions must be positive")
    valid_actions = np.asarray(valid_actions, dtype=np.int64)
    scores = np.asarray(scores, dtype=np.float32)
    if valid_actions.shape[0] != scores.shape[0]:
        raise ValueError("valid_actions and scores must have the same length")
    if valid_actions.size == 0:
        raise ValueError("Cannot select from an empty valid action set")

    k = min(candidate_actions, valid_actions.size)
    order = np.argsort(scores)[::-1][:k]
    return valid_actions[order].astype(np.int64), scores[order].astype(np.float32)


def _validate_adapter_score_request(score_mode: str, value_weight: float) -> None:
    if score_mode not in {"reward", "value", "blend", "zscore_blend"}:
        raise ValueError(
            "score_mode must be 'reward', 'value', 'blend', or 'zscore_blend'"
        )
    if not 0.0 <= value_weight <= 1.0:
        raise ValueError("value_weight must be in [0, 1]")


def _zscore_1d(scores: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    centered = scores - np.mean(scores)
    scale = float(np.sqrt(np.mean(centered * centered)))
    if scale <= eps:
        return np.zeros_like(scores, dtype=np.float32)
    return (centered / scale).astype(np.float32)


def _zscore_blend_adapter_scores(
    rewards: np.ndarray,
    values: np.ndarray,
    value_weight: float,
) -> np.ndarray:
    if rewards.shape != values.shape:
        raise ValueError("adapter aux['value'] must match rewards shape")
    return (
        (1.0 - float(value_weight)) * _zscore_1d(rewards)
        + float(value_weight) * _zscore_1d(values)
    ).astype(np.float32)


def _scalar_scores_from_adapter_output(
    rewards: np.ndarray,
    aux: dict,
    score_mode: str,
    value_weight: float,
) -> np.ndarray:
    _validate_adapter_score_request(score_mode, value_weight)

    rewards = np.asarray(rewards, dtype=np.float32).reshape(-1)
    if score_mode == "reward":
        return rewards
    if "value" not in aux:
        raise ValueError("score_mode requires adapter aux['value']")
    values = np.asarray(aux["value"], dtype=np.float32).reshape(-1)
    if values.shape != rewards.shape:
        raise ValueError("adapter aux['value'] must match rewards shape")
    if score_mode == "value":
        return values
    if score_mode == "zscore_blend":
        return _zscore_blend_adapter_scores(rewards, values, value_weight)
    return (1.0 - float(value_weight)) * rewards + float(value_weight) * values


def _score_actions_with_adapter(
    adapter,
    block_features: np.ndarray,
    global_features: np.ndarray,
    valid_actions: np.ndarray,
    score_batch_size: int = 512,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> np.ndarray:
    if score_batch_size <= 0:
        raise ValueError("score_batch_size must be positive")
    _validate_adapter_score_request(score_mode, value_weight)

    valid_actions = np.asarray(valid_actions, dtype=np.int64)
    scores = []
    reward_chunks = []
    value_chunks = []
    for start in range(0, valid_actions.shape[0], score_batch_size):
        chunk = valid_actions[start : start + score_batch_size]
        bf_batch = np.repeat(block_features[np.newaxis], chunk.shape[0], axis=0)
        gf_batch = np.repeat(global_features[np.newaxis], chunk.shape[0], axis=0)
        _, _, rewards, aux = adapter.batch_predict(bf_batch, gf_batch, chunk)
        if score_mode == "zscore_blend":
            if "value" not in aux:
                raise ValueError("score_mode requires adapter aux['value']")
            reward_chunks.append(np.asarray(rewards, dtype=np.float32).reshape(-1))
            value_chunks.append(np.asarray(aux["value"], dtype=np.float32).reshape(-1))
            continue
        scores.append(
            _scalar_scores_from_adapter_output(
                rewards,
                aux,
                score_mode=score_mode,
                value_weight=value_weight,
            )
        )
    if score_mode == "zscore_blend":
        return _zscore_blend_adapter_scores(
            np.concatenate(reward_chunks),
            np.concatenate(value_chunks),
            value_weight,
        )
    return np.concatenate(scores).astype(np.float32)


def make_adapter_candidate_selector(
    adapter,
    score_batch_size: int = 512,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> CandidateSelectorFn:
    def selector(
        env,
        block_features: np.ndarray,
        global_features: np.ndarray,
        valid_actions: np.ndarray,
        candidate_actions: int,
        rng: np.random.Generator,
    ) -> tuple[np.ndarray, np.ndarray]:
        scores = _score_actions_with_adapter(
            adapter,
            block_features,
            global_features,
            valid_actions,
            score_batch_size=score_batch_size,
            score_mode=score_mode,
            value_weight=value_weight,
        )
        return select_top_scored_actions(valid_actions, scores, candidate_actions)

    return selector


def make_frontier_random_candidate_selector(
    adapter,
    frontier_fraction: float = 0.5,
    score_batch_size: int = 512,
    score_mode: str = "reward",
    value_weight: float = 0.5,
) -> CandidateSelectorFn:
    if not 0.0 < frontier_fraction <= 1.0:
        raise ValueError("frontier_fraction must be in (0, 1]")

    def selector(
        env,
        block_features: np.ndarray,
        global_features: np.ndarray,
        valid_actions: np.ndarray,
        candidate_actions: int,
        rng: np.random.Generator,
    ) -> tuple[np.ndarray, np.ndarray]:
        scores = _score_actions_with_adapter(
            adapter,
            block_features,
            global_features,
            valid_actions,
            score_batch_size=score_batch_size,
            score_mode=score_mode,
            value_weight=value_weight,
        )
        frontier_count = max(1, int(round(candidate_actions * frontier_fraction)))
        frontier_count = min(frontier_count, candidate_actions, valid_actions.size)
        frontier_actions, _ = select_top_scored_actions(
            valid_actions, scores, frontier_count
        )

        remaining_count = candidate_actions - frontier_actions.shape[0]
        if remaining_count <= 0:
            selected_actions = frontier_actions
        else:
            frontier_set = set(int(action) for action in frontier_actions)
            exploration_pool = np.asarray(
                [action for action in valid_actions if int(action) not in frontier_set],
                dtype=np.int64,
            )
            if exploration_pool.size == 0:
                exploration_pool = np.asarray(frontier_actions, dtype=np.int64)
            replace = exploration_pool.size < remaining_count
            random_actions = rng.choice(
                exploration_pool,
                size=remaining_count,
                replace=replace,
            ).astype(np.int64)
            selected_actions = np.concatenate([frontier_actions, random_actions])

        score_by_action = {
            int(action): float(score)
            for action, score in zip(valid_actions.tolist(), scores.tolist())
        }
        selected_scores = np.asarray(
            [score_by_action[int(action)] for action in selected_actions],
            dtype=np.float32,
        )
        return selected_actions.astype(np.int64), selected_scores

    return selector


def make_adapter_top1_policy(adapter, score_batch_size: int = 512) -> PolicyFn:
    def policy(
        env,
        block_features: np.ndarray,
        global_features: np.ndarray,
        valid_actions: np.ndarray,
        rng: np.random.Generator,
    ) -> int:
        scores = _score_actions_with_adapter(
            adapter,
            block_features,
            global_features,
            valid_actions,
            score_batch_size=score_batch_size,
        )
        return int(valid_actions[int(np.argmax(scores))])

    return policy


def build_adapter_generation_components(
    adapter,
    candidate_mode: str,
    advance_policy_name: str,
    continuation_policy_name: str,
    score_batch_size: int = 512,
    frontier_fraction: float = 0.5,
    candidate_score_mode: str = "reward",
    candidate_value_weight: float = 0.5,
) -> tuple[Optional[CandidateSelectorFn], Optional[PolicyFn], Optional[PolicyFn]]:
    if candidate_mode not in {"random", "frontier", "frontier_random"}:
        raise ValueError(
            "candidate_mode must be 'random', 'frontier', or 'frontier_random'"
        )
    if advance_policy_name not in {"random", "model_top1"}:
        raise ValueError("advance_policy must be 'random' or 'model_top1'")
    if continuation_policy_name not in {"random", "model_top1"}:
        raise ValueError("continuation_policy must be 'random' or 'model_top1'")

    if candidate_mode == "frontier":
        candidate_selector = make_adapter_candidate_selector(
            adapter,
            score_batch_size=score_batch_size,
            score_mode=candidate_score_mode,
            value_weight=candidate_value_weight,
        )
    elif candidate_mode == "frontier_random":
        candidate_selector = make_frontier_random_candidate_selector(
            adapter,
            frontier_fraction=frontier_fraction,
            score_batch_size=score_batch_size,
            score_mode=candidate_score_mode,
            value_weight=candidate_value_weight,
        )
    else:
        candidate_selector = None
    advance_policy = (
        make_adapter_top1_policy(adapter, score_batch_size=score_batch_size)
        if advance_policy_name == "model_top1"
        else None
    )
    continuation_policy = (
        make_adapter_top1_policy(adapter, score_batch_size=score_batch_size)
        if continuation_policy_name == "model_top1"
        else None
    )
    return candidate_selector, advance_policy, continuation_policy


def requires_adapter_for_generation(
    candidate_mode: str,
    advance_policy_name: str,
    continuation_policy_name: str,
) -> bool:
    return (
        candidate_mode in {"frontier", "frontier_random"}
        or advance_policy_name == "model_top1"
        or continuation_policy_name == "model_top1"
    )


def _make_label_env(env_source: str, prepared_dir: str):
    if env_source == "paper9":
        from private_source.blocks_env import make_env

        return make_env(prepared_dir=prepared_dir)

    if env_source == "neijiang":
        env_script = Path(prepared_dir) / "county_env_neijiang.py"
        if not env_script.exists():
            raise FileNotFoundError(f"Neijiang env wrapper not found: {env_script}")
        spec = importlib.util.spec_from_file_location(
            "neijiang_cross_region_county_env",
            env_script,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load Neijiang env wrapper: {env_script}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.make_neijiang_env()

    raise ValueError(f"Unsupported env_source: {env_source}")


def _rollout_return_from_first_action(
    env,
    first_action: int,
    horizon: int,
    gamma: float,
    rng: np.random.Generator,
    action_mask_fn: Optional[ActionMaskFn] = None,
    continuation_policy: Optional[PolicyFn] = None,
) -> tuple[float, float]:
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    rewards = []
    reward, done = _step_reward(env, first_action)
    rewards.append(reward)
    one_step_reward = reward

    for _ in range(1, horizon):
        if done:
            break
        valid = _valid_actions(env, action_mask_fn)
        if valid.size == 0:
            break
        if continuation_policy is None:
            action = int(rng.choice(valid))
        else:
            action = int(
                continuation_policy(
                    env,
                    env._get_block_features(),
                    env._get_global_features(),
                    valid,
                    rng,
                )
            )
        reward, done = _step_reward(env, action)
        rewards.append(reward)

    return discounted_return(rewards, gamma=gamma), one_step_reward


def evaluate_first_action_return(
    env,
    first_action: int,
    horizon: int,
    gamma: float,
    rng: np.random.Generator,
    action_mask_fn: Optional[ActionMaskFn] = None,
    continuation_policy: Optional[PolicyFn] = None,
    state_attrs: Optional[Sequence[str]] = None,
) -> float:
    snap = snapshot_env(env, state_attrs=state_attrs)
    try:
        value, _ = _rollout_return_from_first_action(
            env,
            first_action=first_action,
            horizon=horizon,
            gamma=gamma,
            rng=rng,
            action_mask_fn=action_mask_fn,
            continuation_policy=continuation_policy,
        )
        return value
    finally:
        restore_env(env, snap)


def _sample_candidate_actions(
    valid_actions: np.ndarray, candidate_actions: int, rng: np.random.Generator
) -> np.ndarray:
    if candidate_actions <= 0:
        raise ValueError("candidate_actions must be positive")
    if valid_actions.size == 0:
        raise ValueError("Cannot sample candidate actions from an empty valid set")
    replace = valid_actions.size < candidate_actions
    return rng.choice(valid_actions, size=candidate_actions, replace=replace).astype(
        np.int64
    )


def _select_candidates(
    env,
    block_features: np.ndarray,
    global_features: np.ndarray,
    valid_actions: np.ndarray,
    candidate_actions: int,
    rng: np.random.Generator,
    candidate_selector: Optional[CandidateSelectorFn] = None,
) -> tuple[np.ndarray, Optional[np.ndarray]]:
    if candidate_selector is None:
        return _sample_candidate_actions(valid_actions, candidate_actions, rng), None

    selected = candidate_selector(
        env,
        block_features,
        global_features,
        valid_actions,
        candidate_actions,
        rng,
    )
    if isinstance(selected, tuple):
        actions, scores = selected
    else:
        actions, scores = selected, None
    actions = np.asarray(actions, dtype=np.int64)
    if actions.size == 0:
        raise ValueError("candidate_selector returned no actions")
    if scores is not None:
        scores = np.asarray(scores, dtype=np.float32)
        if scores.shape[0] != actions.shape[0]:
            raise ValueError("candidate_selector scores must match selected actions")
    return actions, scores


def _advance_env_one_step(
    env,
    valid_actions: np.ndarray,
    rng: np.random.Generator,
    advance_policy: Optional[PolicyFn] = None,
) -> bool:
    if valid_actions.size == 0:
        return True
    if advance_policy is None:
        action = int(rng.choice(valid_actions))
    else:
        action = int(
            advance_policy(
                env,
                env._get_block_features(),
                env._get_global_features(),
                valid_actions,
                rng,
            )
        )
    _, done = _step_reward(env, action)
    return done


def _dataset_from_parts(
    states_bf: list[np.ndarray],
    states_gf: list[np.ndarray],
    actions_out: list[np.ndarray],
    returns_out: list[np.ndarray],
    one_step_out: list[np.ndarray],
    candidate_scores_out: list[np.ndarray],
    state_steps: list[int],
    n_valid_actions: list[int],
) -> dict[str, np.ndarray]:
    dataset = {
        "states_bf": np.stack(states_bf).astype(np.float32),
        "states_gf": np.stack(states_gf).astype(np.float32),
        "actions": np.stack(actions_out).astype(np.int64),
        "returns": np.stack(returns_out).astype(np.float32),
        "one_step_rewards": np.stack(one_step_out).astype(np.float32),
        "state_steps": np.asarray(state_steps, dtype=np.int64),
        "n_valid_actions": np.asarray(n_valid_actions, dtype=np.int64),
    }
    if candidate_scores_out:
        dataset["candidate_scores"] = np.stack(candidate_scores_out).astype(np.float32)
    return dataset


def make_npz_progress_callback(output_path: str | Path) -> ProgressCallbackFn:
    output_path = Path(output_path)

    def callback(generated_states: int, partial_dataset: dict[str, np.ndarray]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            output_path,
            **partial_dataset,
            partial_generated_states=np.asarray([generated_states], dtype=np.int64),
        )

    return callback


def generate_value_label_dataset(
    env,
    n_states: int,
    candidate_actions: int,
    label_horizon: int,
    gamma: float,
    seed: int,
    action_mask_fn: Optional[ActionMaskFn] = None,
    candidate_selector: Optional[CandidateSelectorFn] = None,
    advance_policy: Optional[PolicyFn] = None,
    continuation_policy: Optional[PolicyFn] = None,
    state_attrs: Optional[Sequence[str]] = None,
    reset: bool = True,
    progress_callback: Optional[ProgressCallbackFn] = None,
    progress_every: int = 0,
) -> dict[str, np.ndarray]:
    if n_states <= 0:
        raise ValueError("n_states must be positive")
    if label_horizon <= 0:
        raise ValueError("label_horizon must be positive")
    if progress_every < 0:
        raise ValueError("progress_every must be non-negative")

    rng = np.random.default_rng(seed)
    if reset:
        env.reset(seed=seed)

    states_bf = []
    states_gf = []
    actions_out = []
    returns_out = []
    one_step_out = []
    candidate_scores_out = []
    state_steps = []
    n_valid_actions = []

    for _ in range(n_states):
        valid = _valid_actions(env, action_mask_fn)
        if valid.size == 0:
            break

        block_features = env._get_block_features().astype(np.float32, copy=True)
        global_features = env._get_global_features().astype(np.float32, copy=True)
        candidates, candidate_scores = _select_candidates(
            env,
            block_features,
            global_features,
            valid,
            candidate_actions,
            rng,
            candidate_selector=candidate_selector,
        )

        values = []
        one_step_rewards = []
        snap = snapshot_env(env, state_attrs=state_attrs)
        try:
            for action in candidates:
                restore_env(env, snap)
                value, first_reward = _rollout_return_from_first_action(
                    env,
                    first_action=int(action),
                    horizon=label_horizon,
                    gamma=gamma,
                    rng=rng,
                    action_mask_fn=action_mask_fn,
                    continuation_policy=continuation_policy,
                )
                values.append(value)
                one_step_rewards.append(first_reward)
        finally:
            restore_env(env, snap)

        states_bf.append(block_features)
        states_gf.append(global_features)
        actions_out.append(candidates)
        returns_out.append(np.asarray(values, dtype=np.float32))
        one_step_out.append(np.asarray(one_step_rewards, dtype=np.float32))
        if candidate_scores is not None:
            candidate_scores_out.append(candidate_scores.astype(np.float32))
        state_steps.append(int(getattr(env, "step_count", len(state_steps))))
        n_valid_actions.append(int(valid.size))
        generated = len(states_bf)
        if (
            progress_callback is not None
            and progress_every > 0
            and generated % progress_every == 0
        ):
            progress_callback(
                generated,
                _dataset_from_parts(
                    states_bf,
                    states_gf,
                    actions_out,
                    returns_out,
                    one_step_out,
                    candidate_scores_out,
                    state_steps,
                    n_valid_actions,
                ),
            )

        done = _advance_env_one_step(
            env,
            valid,
            rng,
            advance_policy=advance_policy,
        )
        if done:
            break

    if not states_bf:
        raise RuntimeError("No value-label states were generated")

    dataset = _dataset_from_parts(
        states_bf,
        states_gf,
        actions_out,
        returns_out,
        one_step_out,
        candidate_scores_out,
        state_steps,
        n_valid_actions,
    )
    if progress_callback is not None and len(states_bf) % max(progress_every, 1) != 0:
        progress_callback(len(states_bf), dataset)
    return dataset


def _summary(dataset: dict[str, np.ndarray], elapsed_sec: float, args) -> dict:
    returns = dataset["returns"]
    one_step = dataset["one_step_rewards"]
    summary = {
        "output": str(args.output),
        "partial_output": str(args.partial_output) if args.partial_output else None,
        "prepared_dir": str(args.prepared_dir),
        "checkpoint": str(args.checkpoint) if args.checkpoint else None,
        "env_source": args.env_source,
        "mask_mode": args.mask_mode,
        "candidate_mode": args.candidate_mode,
        "candidate_score_mode": args.candidate_score_mode,
        "candidate_value_weight": float(args.candidate_value_weight),
        "frontier_fraction": float(args.frontier_fraction),
        "advance_policy": args.advance_policy,
        "continuation_policy": args.continuation_policy,
        "score_batch_size": int(args.score_batch_size),
        "n_states_requested": int(args.n_states),
        "n_states_generated": int(returns.shape[0]),
        "candidate_actions": int(returns.shape[1]),
        "label_horizon": int(args.label_horizon),
        "gamma": float(args.gamma),
        "seed": int(args.seed),
        "progress_every": int(args.progress_every),
        "elapsed_sec": float(elapsed_sec),
        "return_mean": float(returns.mean()),
        "return_std": float(returns.std()),
        "one_step_reward_mean": float(one_step.mean()),
        "one_step_reward_std": float(one_step.std()),
    }
    if "candidate_scores" in dataset:
        scores = dataset["candidate_scores"]
        summary["candidate_score_mean"] = float(scores.mean())
        summary["candidate_score_std"] = float(scores.std())
    return summary


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--prepared-dir", default=str(ROOT))
    parser.add_argument(
        "--env-source",
        choices=("paper9", "neijiang"),
        default="paper9",
        help="Environment factory: paper9 prepared layout or Neijiang cross-region wrapper.",
    )
    parser.add_argument("--n-states", type=int, default=20)
    parser.add_argument("--candidate-actions", type=int, default=20)
    parser.add_argument("--label-horizon", type=int, default=3)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--mask-mode", choices=("base", "executable"), default="executable")
    parser.add_argument(
        "--candidate-mode",
        choices=("random", "frontier", "frontier_random"),
        default="random",
    )
    parser.add_argument(
        "--candidate-score-mode",
        choices=("reward", "value", "blend", "zscore_blend"),
        default="reward",
    )
    parser.add_argument("--candidate-value-weight", type=float, default=0.5)
    parser.add_argument("--frontier-fraction", type=float, default=0.5)
    parser.add_argument("--advance-policy", choices=("random", "model_top1"), default="random")
    parser.add_argument(
        "--continuation-policy", choices=("random", "model_top1"), default="random"
    )
    parser.add_argument("--score-batch-size", type=int, default=512)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--partial-output", default=None)
    parser.add_argument("--progress-every", type=int, default=0)
    parser.add_argument(
        "--output",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "results"
            / "e0_value_labels_smoke.npz"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = perf_counter()

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(PAPER9_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER9_DIR))

    from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
    env = _make_label_env(args.env_source, args.prepared_dir)
    needs_adapter = requires_adapter_for_generation(
        args.candidate_mode,
        args.advance_policy,
        args.continuation_policy,
    )
    if needs_adapter:
        if args.checkpoint is None:
            raise ValueError(
                "--checkpoint is required for frontier candidates or model_top1 policies"
            )
        from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter

        adapter = TorchCheckpointMPCAdapter.from_checkpoint(
            args.checkpoint, device=args.device
        )
        adapter.assert_compatible(env.n_blocks)
    else:
        adapter = None

    def action_mask_fn(runtime_env):
        base_mask = np.asarray(runtime_env.action_masks(), dtype=bool)
        if args.mask_mode == "base":
            return base_mask
        return base_mask & executable_swap_mask(runtime_env)

    candidate_selector, advance_policy, continuation_policy = (
        build_adapter_generation_components(
            adapter,
            candidate_mode=args.candidate_mode,
            advance_policy_name=args.advance_policy,
            continuation_policy_name=args.continuation_policy,
            score_batch_size=args.score_batch_size,
            frontier_fraction=args.frontier_fraction,
            candidate_score_mode=args.candidate_score_mode,
            candidate_value_weight=args.candidate_value_weight,
        )
    )
    progress_callback = (
        make_npz_progress_callback(args.partial_output)
        if args.partial_output
        else None
    )
    dataset = generate_value_label_dataset(
        env,
        n_states=args.n_states,
        candidate_actions=args.candidate_actions,
        label_horizon=args.label_horizon,
        gamma=args.gamma,
        seed=args.seed,
        action_mask_fn=action_mask_fn,
        candidate_selector=candidate_selector,
        advance_policy=advance_policy,
        continuation_policy=continuation_policy,
        progress_callback=progress_callback,
        progress_every=args.progress_every,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, **dataset)

    print(json.dumps(_summary(dataset, perf_counter() - started, args), indent=2))


if __name__ == "__main__":
    main()
