import json
from pathlib import Path

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import oriented_outcome
from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    build_neighbour_feature_matrix,
)


def select_without_execution(*, env, selector, **selector_kwargs):
    before_step_count = int(getattr(env, "step_count", 0))
    instance_dict = vars(env)
    had_instance_step = "step" in instance_dict
    original_instance_step = instance_dict.get("step")
    original_step = getattr(env, "step")

    def forbidden_step(*args, **kwargs):
        raise RuntimeError("real environment step is forbidden during selection")

    guard_installed = False
    try:
        setattr(env, "step", forbidden_step)
        guard_installed = True
        action, info = selector(**selector_kwargs)
    finally:
        if guard_installed:
            if had_instance_step:
                setattr(env, "step", original_instance_step)
            else:
                delattr(env, "step")
    after_step_count = int(getattr(env, "step_count", 0))
    if before_step_count != after_step_count:
        raise RuntimeError("selector mutated the real environment")
    if getattr(env, "step") != original_step:
        raise RuntimeError("environment step method was not restored after selection")
    return int(action), dict(info)


def _observable_state(env) -> dict[str, np.ndarray]:
    block = np.asarray(env._get_block_features(), dtype=np.float32).copy()
    return {
        "block_features": block,
        "neighbour_features": build_neighbour_feature_matrix(env, block),
        "global_features": np.asarray(
            env._get_global_features(),
            dtype=np.float32,
        ).copy(),
        "executable_mask": np.asarray(env.action_masks(), dtype=bool).copy(),
    }


def run_policy_episode(
    *,
    env,
    policy,
    seed: int,
    rollout_steps: int,
    metric_reader,
) -> dict[str, object]:
    if int(rollout_steps) <= 0:
        raise ValueError("rollout_steps must be positive")
    env.reset(seed=int(seed))
    steps = []
    total_reward = 0.0
    for step_index in range(int(rollout_steps)):
        before_metrics = dict(metric_reader(env))
        state = _observable_state(env)
        action, selection_info = select_without_execution(
            env=env,
            selector=policy.select,
            state=state,
        )
        _, reward, terminated, truncated, environment_info = env.step(action)
        after_metrics = dict(metric_reader(env))
        observed_outcome = oriented_outcome(
            float(reward),
            before_metrics,
            after_metrics,
        )
        transition = {
            "action": int(action),
            "reward": float(reward),
            "observed_outcome": observed_outcome.tolist(),
            "predicted_mean": selection_info.get("selected_predicted_mean"),
            "base_scale": selection_info.get("selected_base_scale"),
            "terminated": bool(terminated),
            "truncated": bool(truncated),
        }
        observe = getattr(policy, "observe", None)
        if observe is not None:
            observe(transition)
        record = {
            "step": int(step_index),
            "action": int(action),
            "reward": float(reward),
            "observed_outcome": observed_outcome.tolist(),
            "environment_info": dict(environment_info),
            **selection_info,
        }
        record.setdefault("unexecuted_real_reward_queries", 0)
        steps.append(record)
        total_reward += float(reward)
        if terminated or truncated:
            break
    return {
        "seed": int(seed),
        "steps": steps,
        "environment_step_count": int(getattr(env, "step_count", len(steps))),
        "total_reward": float(total_reward),
        "final_metrics": dict(metric_reader(env)),
    }


def load_resumable_results(
    path: str | Path,
    *,
    registry_digest: str,
    checkpoint_digests,
) -> dict[str, object]:
    path = Path(path)
    if not path.exists():
        return {
            "schema_version": 1,
            "registry_digest": str(registry_digest),
            "checkpoint_digests": list(checkpoint_digests),
            "completed_seeds": [],
            "seed_results": [],
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("registry_digest") != str(registry_digest):
        raise ValueError("registry digest mismatch in resumable rollout")
    if payload.get("checkpoint_digests") != list(checkpoint_digests):
        raise ValueError("checkpoint digest mismatch in resumable rollout")
    completed = [int(row["seed"]) for row in payload.get("seed_results", [])]
    if len(completed) != len(set(completed)):
        raise ValueError("duplicate seed in resumable rollout")
    payload["completed_seeds"] = sorted(completed)
    return payload


def write_seed_result_atomic(
    path: str | Path,
    *,
    seed_result: dict[str, object],
    registry_digest: str,
    checkpoint_digests,
) -> dict[str, object]:
    path = Path(path)
    payload = load_resumable_results(
        path,
        registry_digest=registry_digest,
        checkpoint_digests=checkpoint_digests,
    )
    seed = int(seed_result["seed"])
    rows = [
        row for row in payload["seed_results"] if int(row["seed"]) != seed
    ]
    rows.append(dict(seed_result))
    rows.sort(key=lambda row: int(row["seed"]))
    payload["seed_results"] = rows
    payload["completed_seeds"] = [int(row["seed"]) for row in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload
