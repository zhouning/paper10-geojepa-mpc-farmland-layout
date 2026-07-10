import argparse
import hashlib
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Callable, Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import oriented_outcome
from paper10_geojepa_mpc.experiments.value_label_generation import (
    _make_label_env,
    restore_env,
    snapshot_env,
)


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"


MetricReader = Callable[[object], dict[str, float]]
Policy = Callable[[object, np.random.Generator], int]


@dataclass(frozen=True)
class PairedObjectiveReturns:
    candidate: np.ndarray
    reference: np.ndarray
    candidate_next_block: np.ndarray
    candidate_next_global: np.ndarray
    reference_next_block: np.ndarray
    reference_next_global: np.ndarray


@dataclass(frozen=True)
class CandidateObjectiveRollout:
    objectives: np.ndarray
    next_block: np.ndarray
    next_global: np.ndarray


def _normalize_horizons(horizons: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(int(value) for value in horizons)
    if not normalized or any(value <= 0 for value in normalized):
        raise ValueError("horizons must contain positive integers")
    if tuple(sorted(set(normalized))) != normalized:
        raise ValueError("horizons must be strictly increasing and unique")
    return normalized


def build_neighbour_feature_matrix(env, block_features) -> np.ndarray:
    block_features = np.asarray(block_features, dtype=np.float32)
    if block_features.ndim != 2:
        raise ValueError("block_features must have shape [n_blocks, n_features]")
    if len(env.block_adj) != block_features.shape[0]:
        raise ValueError("block_adj length must equal n_blocks")

    rows = []
    for neighbours in env.block_adj:
        indexes = np.asarray(neighbours, dtype=np.int64).reshape(-1)
        if indexes.size == 0:
            rows.append(np.zeros(block_features.shape[1], dtype=np.float32))
        else:
            if indexes.min() < 0 or indexes.max() >= block_features.shape[0]:
                raise ValueError("block_adj contains an out-of-range block index")
            rows.append(block_features[indexes].mean(axis=0))
    return np.stack(rows).astype(np.float32)


def derive_continuation_seed(
    trajectory_seed: int,
    state_step: int,
    candidate_action: int,
) -> int:
    values = [int(trajectory_seed), int(state_step), int(candidate_action)]
    if any(value < 0 for value in values):
        raise ValueError("continuation seed components must be non-negative")
    seed = np.random.SeedSequence(values).generate_state(1, dtype=np.uint64)[0]
    return int(seed)


def _evaluate_candidate_rollout(
    *,
    env,
    candidate_action: int,
    horizons: Sequence[int],
    gamma: float,
    continuation_policy: Policy,
    rng: np.random.Generator,
    metric_reader: MetricReader,
    state_attrs: Sequence[str] | None = None,
) -> CandidateObjectiveRollout:
    horizons = _normalize_horizons(horizons)
    if not 0.0 <= float(gamma) <= 1.0:
        raise ValueError("gamma must be in [0, 1]")

    snapshot = snapshot_env(env, state_attrs=state_attrs)
    start = dict(metric_reader(env))
    rewards: list[float] = []
    outcomes: dict[int, np.ndarray] = {}
    last_outcome: np.ndarray | None = None
    next_block: np.ndarray | None = None
    next_global: np.ndarray | None = None
    done = False
    try:
        for step in range(1, horizons[-1] + 1):
            action = (
                int(candidate_action)
                if step == 1
                else int(continuation_policy(env, rng))
            )
            _, reward, terminated, truncated, _ = env.step(action)
            rewards.append(float(reward))
            if step == 1:
                next_block = np.asarray(
                    env._get_block_features(),
                    dtype=np.float32,
                ).copy()
                next_global = np.asarray(
                    env._get_global_features(),
                    dtype=np.float32,
                ).copy()
            discounted = sum(
                (float(gamma) ** index) * value
                for index, value in enumerate(rewards)
            )
            last_outcome = oriented_outcome(
                discounted,
                start,
                metric_reader(env),
            )
            if step in horizons:
                outcomes[step] = last_outcome
            done = bool(terminated or truncated)
            if done:
                break

        if last_outcome is None:
            raise RuntimeError("candidate evaluation executed no environment step")
        for horizon in horizons:
            if horizon not in outcomes:
                outcomes[horizon] = last_outcome.copy()
        if next_block is None or next_global is None:
            raise RuntimeError("candidate evaluation did not capture a next state")
        return CandidateObjectiveRollout(
            objectives=np.stack(
                [outcomes[horizon] for horizon in horizons]
            ).astype(np.float32),
            next_block=next_block,
            next_global=next_global,
        )
    finally:
        restore_env(env, snapshot)


def evaluate_candidate_objectives(
    *,
    env,
    candidate_action: int,
    horizons: Sequence[int],
    gamma: float,
    continuation_policy: Policy,
    rng: np.random.Generator,
    metric_reader: MetricReader,
    state_attrs: Sequence[str] | None = None,
) -> np.ndarray:
    return _evaluate_candidate_rollout(
        env=env,
        candidate_action=candidate_action,
        horizons=horizons,
        gamma=gamma,
        continuation_policy=continuation_policy,
        rng=rng,
        metric_reader=metric_reader,
        state_attrs=state_attrs,
    ).objectives


def evaluate_paired_objectives(
    *,
    env,
    candidate_action: int,
    reference_action: int,
    horizons: Sequence[int],
    gamma: float,
    continuation_policy: Policy,
    continuation_seed: int,
    metric_reader: MetricReader,
    state_attrs: Sequence[str] | None = None,
) -> PairedObjectiveReturns:
    candidate = _evaluate_candidate_rollout(
        env=env,
        candidate_action=candidate_action,
        horizons=horizons,
        gamma=gamma,
        continuation_policy=continuation_policy,
        rng=np.random.default_rng(continuation_seed),
        metric_reader=metric_reader,
        state_attrs=state_attrs,
    )
    reference = _evaluate_candidate_rollout(
        env=env,
        candidate_action=reference_action,
        horizons=horizons,
        gamma=gamma,
        continuation_policy=continuation_policy,
        rng=np.random.default_rng(continuation_seed),
        metric_reader=metric_reader,
        state_attrs=state_attrs,
    )
    return PairedObjectiveReturns(
        candidate=candidate.objectives,
        reference=reference.objectives,
        candidate_next_block=candidate.next_block,
        candidate_next_global=candidate.next_global,
        reference_next_block=reference.next_block,
        reference_next_global=reference.next_global,
    )


def _default_candidate_selector(env, valid, count, rng) -> np.ndarray:
    replace = len(valid) < int(count)
    return rng.choice(valid, size=int(count), replace=replace).astype(np.int64)


def generate_pcc_value_label_dataset(
    *,
    env,
    n_states: int,
    candidate_actions: int,
    horizons: Sequence[int],
    gamma: float,
    trajectory_seed: int,
    reference_policy: Policy,
    continuation_policy: Policy,
    candidate_selector=None,
    advance_policy: Policy | None = None,
    executable_target_mask_fn=None,
    metric_reader: MetricReader,
    state_attrs: Sequence[str] | None = None,
    reset: bool = True,
) -> dict[str, np.ndarray]:
    if int(n_states) <= 0 or int(candidate_actions) <= 0:
        raise ValueError("n_states and candidate_actions must be positive")
    horizons = _normalize_horizons(horizons)
    rng = np.random.default_rng(int(trajectory_seed))
    if reset:
        env.reset(seed=int(trajectory_seed))

    states_bf = []
    states_neighbor_bf = []
    states_gf = []
    actions_out = []
    objective_returns = []
    reference_actions = []
    reference_returns = []
    candidate_next_bf = []
    candidate_next_gf = []
    reference_next_bf = []
    reference_next_gf = []
    executable_targets = []
    continuation_seeds = []
    state_steps = []

    selector = candidate_selector or _default_candidate_selector
    for _ in range(int(n_states)):
        mask = np.asarray(env.action_masks(), dtype=bool)
        valid = np.flatnonzero(mask).astype(np.int64)
        if valid.size == 0:
            break

        state_step = int(getattr(env, "step_count", len(state_steps)))
        block = np.asarray(env._get_block_features(), dtype=np.float32).copy()
        global_features = np.asarray(
            env._get_global_features(),
            dtype=np.float32,
        ).copy()
        candidates = np.asarray(
            selector(env, valid.copy(), int(candidate_actions), rng),
            dtype=np.int64,
        ).reshape(-1)
        if candidates.shape[0] != int(candidate_actions):
            raise ValueError("candidate_selector returned the wrong number of actions")
        if not np.isin(candidates, valid).all():
            raise ValueError("candidate_selector returned a non-executable action")
        target_mask = (
            np.asarray(executable_target_mask_fn(env), dtype=bool)
            if executable_target_mask_fn is not None
            else mask
        )
        if target_mask.shape != mask.shape:
            raise ValueError("executable target mask must match the base action mask")

        reference_action = int(reference_policy(env, rng))
        if reference_action not in set(valid.tolist()):
            raise ValueError("reference_policy returned a non-executable action")

        candidate_rows = []
        reference_rows = []
        candidate_next_bf_rows = []
        candidate_next_gf_rows = []
        reference_next_bf_rows = []
        reference_next_gf_rows = []
        seed_rows = []
        for candidate_action in candidates:
            continuation_seed = derive_continuation_seed(
                trajectory_seed,
                state_step,
                int(candidate_action),
            )
            paired = evaluate_paired_objectives(
                env=env,
                candidate_action=int(candidate_action),
                reference_action=reference_action,
                horizons=horizons,
                gamma=gamma,
                continuation_policy=continuation_policy,
                continuation_seed=continuation_seed,
                metric_reader=metric_reader,
                state_attrs=state_attrs,
            )
            candidate_rows.append(paired.candidate)
            reference_rows.append(paired.reference)
            candidate_next_bf_rows.append(paired.candidate_next_block)
            candidate_next_gf_rows.append(paired.candidate_next_global)
            reference_next_bf_rows.append(paired.reference_next_block)
            reference_next_gf_rows.append(paired.reference_next_global)
            seed_rows.append(continuation_seed)

        states_bf.append(block)
        states_neighbor_bf.append(build_neighbour_feature_matrix(env, block))
        states_gf.append(global_features)
        actions_out.append(candidates)
        objective_returns.append(np.stack(candidate_rows))
        reference_actions.append(reference_action)
        reference_returns.append(np.stack(reference_rows))
        candidate_next_bf.append(np.stack(candidate_next_bf_rows))
        candidate_next_gf.append(np.stack(candidate_next_gf_rows))
        reference_next_bf.append(np.stack(reference_next_bf_rows))
        reference_next_gf.append(np.stack(reference_next_gf_rows))
        executable_targets.append(target_mask[candidates].astype(np.float32))
        continuation_seeds.append(np.asarray(seed_rows, dtype=np.uint64))
        state_steps.append(state_step)

        advance = advance_policy or reference_policy
        _, _, terminated, truncated, _ = env.step(int(advance(env, rng)))
        if terminated or truncated:
            break

    if not states_bf:
        raise RuntimeError("No PCC value-label states were generated")

    return {
        "states_bf": np.stack(states_bf).astype(np.float32),
        "states_neighbor_bf": np.stack(states_neighbor_bf).astype(np.float32),
        "states_gf": np.stack(states_gf).astype(np.float32),
        "actions": np.stack(actions_out).astype(np.int64),
        "objective_returns": np.stack(objective_returns).astype(np.float32),
        "reference_actions": np.asarray(reference_actions, dtype=np.int64),
        "reference_objective_returns": np.stack(reference_returns).astype(
            np.float32
        ),
        "candidate_next_bf": np.stack(candidate_next_bf).astype(np.float32),
        "candidate_next_gf": np.stack(candidate_next_gf).astype(np.float32),
        "reference_next_bf": np.stack(reference_next_bf).astype(np.float32),
        "reference_next_gf": np.stack(reference_next_gf).astype(np.float32),
        "executable_targets": np.stack(executable_targets).astype(np.float32),
        "continuation_seeds": np.stack(continuation_seeds).astype(np.uint64),
        "trajectory_ids": np.full(
            len(states_bf),
            int(trajectory_seed),
            dtype=np.int64,
        ),
        "state_steps": np.asarray(state_steps, dtype=np.int64),
        "horizons": np.asarray(horizons, dtype=np.int64),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_trajectory_artifact(
    output_dir: str | Path,
    trajectory_seed: int,
    dataset: dict[str, np.ndarray],
) -> dict[str, object]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"trajectory_{int(trajectory_seed)}.npz"
    temporary = path.with_suffix(".tmp.npz")
    np.savez_compressed(temporary, **dataset)
    temporary.replace(path)
    return {
        "trajectory_seed": int(trajectory_seed),
        "path": path.name,
        "sha256": _sha256_file(path),
        "n_states": int(dataset["states_bf"].shape[0]),
        "n_candidates": int(dataset["actions"].shape[1]),
    }


def _manifest_digest(payload: dict[str, object]) -> str:
    clean = {key: value for key, value in payload.items() if key != "manifest_digest"}
    canonical = json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def write_label_manifest(
    output_dir: str | Path,
    *,
    protocol_id: str,
    partition: str,
    artifacts: Sequence[dict[str, object]],
    continuation_policy: dict[str, object],
    horizons: Sequence[int],
) -> dict[str, object]:
    if "confirmation" in str(partition).lower():
        raise ValueError("confirmation partitions cannot be used for offline labels")
    if not artifacts:
        raise ValueError("at least one trajectory artifact is required")

    ordered = sorted(artifacts, key=lambda row: int(row["trajectory_seed"]))
    payload: dict[str, object] = {
        "schema_version": 1,
        "protocol_id": str(protocol_id),
        "partition": str(partition),
        "trajectory_seeds": [int(row["trajectory_seed"]) for row in ordered],
        "horizons": list(_normalize_horizons(horizons)),
        "continuation_policy": dict(continuation_policy),
        "artifacts": ordered,
    }
    payload["manifest_digest"] = _manifest_digest(payload)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "manifest.json"
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def generate_label_partition(
    *,
    registry: dict[str, object],
    partition: str,
    trajectory_seeds: Sequence[int] | None = None,
    output_dir: str | Path,
    env_factory,
    policy_factory,
    n_states: int,
    candidate_actions: int,
    horizons: Sequence[int],
    gamma: float,
    metric_reader: MetricReader,
    candidate_selector=None,
    continuation_policy_factory=None,
    advance_policy_factory=None,
    executable_target_mask_fn=None,
    continuation_policy_metadata: dict[str, object] | None = None,
    state_attrs: Sequence[str] | None = None,
) -> dict[str, object]:
    if "confirmation" in str(partition).lower():
        raise ValueError("confirmation partitions cannot be used for offline labels")
    partitions = registry.get("partitions", {})
    if partition not in partitions:
        raise ValueError(f"unknown registry partition: {partition}")
    declared_seeds = [int(value) for value in partitions[partition]]
    selected_seeds = (
        declared_seeds
        if trajectory_seeds is None
        else [int(value) for value in trajectory_seeds]
    )
    if not selected_seeds or len(selected_seeds) != len(set(selected_seeds)):
        raise ValueError("trajectory seed subset must be non-empty and unique")
    if not set(selected_seeds) <= set(declared_seeds):
        raise ValueError("trajectory seed is outside the declared partition")

    artifacts = []
    for trajectory_seed in selected_seeds:
        env = env_factory()
        reference_policy = policy_factory(env)
        continuation_policy = (
            continuation_policy_factory(env)
            if continuation_policy_factory is not None
            else reference_policy
        )
        advance_policy = (
            advance_policy_factory(env)
            if advance_policy_factory is not None
            else reference_policy
        )
        dataset = generate_pcc_value_label_dataset(
            env=env,
            n_states=n_states,
            candidate_actions=candidate_actions,
            horizons=horizons,
            gamma=gamma,
            trajectory_seed=trajectory_seed,
            reference_policy=reference_policy,
            continuation_policy=continuation_policy,
            candidate_selector=candidate_selector,
            advance_policy=advance_policy,
            executable_target_mask_fn=executable_target_mask_fn,
            metric_reader=metric_reader,
            state_attrs=state_attrs,
        )
        artifacts.append(
            write_trajectory_artifact(output_dir, trajectory_seed, dataset)
        )

    return write_label_manifest(
        output_dir,
        protocol_id=str(registry["protocol_id"]),
        partition=partition,
        artifacts=artifacts,
        continuation_policy=continuation_policy_metadata
        or {"name": "policy_factory"},
        horizons=horizons,
    )


def _default_metric_reader(env) -> dict[str, float]:
    return {
        "avg_slope": float(env.avg_farmland_slope),
        "contiguity": float(env.contiguity),
        "baimu_area_ha": float(env.baimu_total_area) / 10000.0,
    }


def _load_paper9_mpc_select_action():
    path = PAPER9_DIR / "private_source" / "mpc_plan.py"
    spec = importlib.util.spec_from_file_location("paper9_private_mpc_plan", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Paper9 MPC implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mpc_select_action


def build_checkpoint_reference_policy_factory(
    checkpoint: str | Path,
    *,
    device: str,
    horizon: int,
    top_k: int,
    gamma: float,
    action_mask_fn=None,
):
    from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter

    adapter = TorchCheckpointMPCAdapter.from_checkpoint(checkpoint, device=device)
    mpc_select_action = _load_paper9_mpc_select_action()

    def factory(env):
        adapter.assert_compatible(env.n_blocks)

        def policy(runtime_env, rng):
            action_mask = (
                np.asarray(action_mask_fn(runtime_env), dtype=bool)
                if action_mask_fn is not None
                else np.asarray(runtime_env.action_masks(), dtype=bool)
            )
            action, _ = mpc_select_action(
                adapter,
                runtime_env._get_block_features(),
                runtime_env._get_global_features(),
                action_mask,
                horizon=int(horizon),
                top_k=int(top_k),
                gamma=float(gamma),
                n_rollouts=1,
                continuation="random",
                scoring="reward",
                rng=rng,
            )
            return int(action)

        return policy

    return factory


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--partition", required=True)
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--env-source", choices=("paper9", "neijiang"), default="paper9")
    parser.add_argument("--prepared-dir", default=str(ROOT))
    parser.add_argument(
        "--reference-checkpoint",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "checkpoints"
            / "e0_bishan_rank_seed2028"
            / "rank_seed2028.pt"
        ),
    )
    parser.add_argument("--states-per-trajectory", type=int, default=50)
    parser.add_argument("--candidate-actions", type=int, default=16)
    parser.add_argument("--horizons", default="1,3,5")
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--planning-horizon", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def _parse_seed_spec(spec: str) -> list[int]:
    seeds = []
    for token in str(spec).split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start, end = int(start_text), int(end_text)
            if end < start:
                raise ValueError("seed range end must not precede start")
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(token))
    return seeds


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
        validate_registry,
    )
    from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask

    args = parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(PAPER9_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER9_DIR))

    registry = load_registry(args.registry)
    validate_registry(registry)
    checkpoint = Path(args.reference_checkpoint)

    def strict_executable_mask(env):
        base = np.asarray(env.action_masks(), dtype=bool)
        strict = np.asarray(executable_swap_mask(env), dtype=bool)
        if strict.shape != base.shape:
            raise ValueError("strict executable mask shape mismatch")
        return base & strict

    policy_factory = build_checkpoint_reference_policy_factory(
        checkpoint,
        device=args.device,
        horizon=args.planning_horizon,
        top_k=args.top_k,
        gamma=args.gamma,
        action_mask_fn=strict_executable_mask,
    )
    horizons = tuple(int(value) for value in args.horizons.split(","))
    manifest = generate_label_partition(
        registry=registry,
        partition=args.partition,
        trajectory_seeds=(
            _parse_seed_spec(args.seeds) if args.seeds is not None else None
        ),
        output_dir=args.output_dir,
        env_factory=lambda: _make_label_env(args.env_source, args.prepared_dir),
        policy_factory=policy_factory,
        n_states=args.states_per_trajectory,
        candidate_actions=args.candidate_actions,
        horizons=horizons,
        gamma=args.gamma,
        metric_reader=_default_metric_reader,
        continuation_policy_factory=policy_factory,
        advance_policy_factory=policy_factory,
        executable_target_mask_fn=strict_executable_mask,
        continuation_policy_metadata={
            "name": "paper9_mpc",
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": _sha256_file(checkpoint),
            "planning_horizon": int(args.planning_horizon),
            "top_k": int(args.top_k),
            "gamma": float(args.gamma),
        },
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
