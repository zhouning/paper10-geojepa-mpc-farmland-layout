import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Sequence

import numpy as np
import torch

from paper10_geojepa_mpc.experiments.pcc_objectives import oriented_outcome
from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    build_neighbour_feature_matrix,
)
from paper10_geojepa_mpc.planning.paper9_memory_efficient import (
    memory_efficient_mpc_select_action,
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


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"


def _observable_state(env, action_mask_fn=None) -> dict[str, np.ndarray]:
    block = np.asarray(env._get_block_features(), dtype=np.float32).copy()
    mask = (
        np.asarray(action_mask_fn(env), dtype=bool)
        if action_mask_fn is not None
        else np.asarray(env.action_masks(), dtype=bool)
    )
    return {
        "block_features": block,
        "neighbour_features": build_neighbour_feature_matrix(env, block),
        "global_features": np.asarray(
            env._get_global_features(),
            dtype=np.float32,
        ).copy(),
        "executable_mask": mask.copy(),
    }


def run_policy_episode(
    *,
    env,
    policy,
    seed: int,
    rollout_steps: int,
    metric_reader,
    action_mask_fn=None,
) -> dict[str, object]:
    if int(rollout_steps) <= 0:
        raise ValueError("rollout_steps must be positive")
    env.reset(seed=int(seed))
    initial_metrics = dict(metric_reader(env))
    steps = []
    total_reward = 0.0
    for step_index in range(int(rollout_steps)):
        before_metrics = dict(metric_reader(env))
        state = _observable_state(env, action_mask_fn=action_mask_fn)
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
    final_metrics = dict(metric_reader(env))
    return {
        "seed": int(seed),
        "steps": steps,
        "environment_step_count": int(getattr(env, "step_count", len(steps))),
        "total_reward": float(total_reward),
        "initial_metrics": initial_metrics,
        "final_metrics": final_metrics,
        "objective_outcome": oriented_outcome(
            total_reward,
            initial_metrics,
            final_metrics,
        ).tolist(),
    }


def _evaluate_true_rewards_with_restore(env, actions: np.ndarray) -> np.ndarray:
    from paper10_geojepa_mpc.experiments.rollout_candidate_diagnostics import (
        _restore,
        _snapshot,
    )

    snapshot = _snapshot(env)
    rewards = []
    for action in np.asarray(actions, dtype=np.int64):
        try:
            _, reward, _, _, _ = env.step(int(action))
            rewards.append(float(reward))
        finally:
            _restore(env, snapshot)
    return np.asarray(rewards, dtype=np.float64)


def run_oracle_diagnostic_episode(
    *,
    env,
    seed: int,
    rollout_steps: int,
    metric_reader,
    action_mask_fn=None,
    true_reward_evaluator=_evaluate_true_rewards_with_restore,
) -> dict[str, object]:
    if int(rollout_steps) <= 0:
        raise ValueError("rollout_steps must be positive")
    env.reset(seed=int(seed))
    initial_metrics = dict(metric_reader(env))
    steps = []
    total_reward = 0.0
    total_queries = 0
    for step_index in range(int(rollout_steps)):
        before_metrics = dict(metric_reader(env))
        mask = (
            np.asarray(action_mask_fn(env), dtype=bool)
            if action_mask_fn is not None
            else np.asarray(env.action_masks(), dtype=bool)
        )
        actions = np.flatnonzero(mask).astype(np.int64)
        if actions.size == 0:
            break
        before_step_count = int(getattr(env, "step_count", 0))
        true_rewards = np.asarray(
            true_reward_evaluator(env, actions),
            dtype=np.float64,
        )
        if int(getattr(env, "step_count", 0)) != before_step_count:
            raise RuntimeError("oracle diagnostic evaluator mutated the environment")
        if true_rewards.shape != actions.shape or not np.isfinite(true_rewards).all():
            raise ValueError("oracle diagnostic rewards must be finite per action")
        selected_index = int(np.argmax(true_rewards))
        action = int(actions[selected_index])
        query_count = int(actions.size)
        _, reward, terminated, truncated, environment_info = env.step(action)
        after_metrics = dict(metric_reader(env))
        observed_outcome = oriented_outcome(
            float(reward),
            before_metrics,
            after_metrics,
        )
        steps.append(
            {
                "step": int(step_index),
                "action": action,
                "reward": float(reward),
                "observed_outcome": observed_outcome.tolist(),
                "environment_info": dict(environment_info),
                "policy": "oracle_action_audit_diagnostic",
                "deployable": False,
                "diagnostic_role": "privileged_upper_bound",
                "unexecuted_real_reward_queries": query_count,
                "true_reward_query_count": query_count,
                "queried_actions": actions.tolist(),
                "queried_true_rewards": true_rewards.tolist(),
            }
        )
        total_reward += float(reward)
        total_queries += query_count
        if terminated or truncated:
            break
    final_metrics = dict(metric_reader(env))
    return {
        "seed": int(seed),
        "policy": "oracle_action_audit_diagnostic",
        "deployable": False,
        "diagnostic_role": "privileged_upper_bound",
        "unexecuted_real_reward_queries": int(total_queries),
        "steps": steps,
        "environment_step_count": int(getattr(env, "step_count", len(steps))),
        "total_reward": float(total_reward),
        "initial_metrics": initial_metrics,
        "final_metrics": final_metrics,
        "objective_outcome": oriented_outcome(
            total_reward,
            initial_metrics,
            final_metrics,
        ).tolist(),
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


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_paper9_mpc_select_action():
    path = PAPER9_DIR / "private_source" / "mpc_plan.py"
    spec = importlib.util.spec_from_file_location("paper9_private_mpc_plan", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Paper9 MPC implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mpc_select_action


def _select_paper9_reference_action(
    adapter,
    state,
    rng,
    *,
    horizon: int,
    top_k: int,
    gamma: float = 0.99,
    screening_batch_size: int = 64,
):
    action, info = memory_efficient_mpc_select_action(
        adapter,
        state["block_features"],
        state["global_features"],
        state["executable_mask"],
        horizon=int(horizon),
        top_k=int(top_k),
        gamma=float(gamma),
        n_rollouts=1,
        continuation="random",
        scoring="reward",
        screening_batch_size=int(screening_batch_size),
        rng=rng,
    )
    info = dict(info)
    info["unexecuted_real_reward_queries"] = 0
    return int(action), info


def _validate_ensemble_model_seed(ensemble, *, expected_model_seed: int) -> None:
    if not ensemble:
        raise ValueError("ensemble checkpoint lineage is empty")
    observed = []
    for _, checkpoint in ensemble:
        try:
            observed.append(int(checkpoint["model_seed"]))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("ensemble checkpoint lineage is missing model_seed") from error
    if set(observed) != {int(expected_model_seed)}:
        raise ValueError(
            "ensemble checkpoint lineage does not match declared --model-seed"
        )


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
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("seed list must be non-empty and unique")
    return seeds


def _metric_reader(env) -> dict[str, float]:
    return {
        "avg_slope": float(env.avg_farmland_slope),
        "contiguity": float(env.contiguity),
        "baimu_area_ha": float(env.baimu_total_area) / 10000.0,
    }


def _make_env(env_source: str, prepared_dir: str):
    from paper10_geojepa_mpc.experiments.value_label_generation import _make_label_env

    return _make_label_env(env_source, prepared_dir)


def _adapter_ranker(adapter, *, score_mode: str, value_weight: float = 0.5):
    from paper10_geojepa_mpc.planning.scoring import score_candidate_actions

    def rank(state):
        valid = np.flatnonzero(state["executable_mask"]).astype(np.int64)
        if valid.size == 0:
            return valid
        with torch.no_grad():
            scores = score_candidate_actions(
                adapter.model,
                torch.as_tensor(
                    state["block_features"],
                    dtype=torch.float32,
                    device=adapter.device,
                ),
                torch.as_tensor(
                    state["global_features"],
                    dtype=torch.float32,
                    device=adapter.device,
                ),
                torch.as_tensor(valid, dtype=torch.long, device=adapter.device),
                score_mode=score_mode,
                value_weight=value_weight,
            ).detach().cpu().numpy()
        order = np.lexsort((valid, -scores))
        return valid[order]

    return rank


def validate_rollout_request(
    registry: dict[str, object],
    *,
    mode: str,
    env_source: str,
    seeds,
) -> str:
    partition = {
        ("development", "paper9"): "development",
        ("confirmation", "paper9"): "confirmation",
        ("confirmation", "neijiang"): "dongxing_confirmation",
        ("diagnostic", "paper9"): "confirmation",
    }.get((str(mode), str(env_source)))
    if partition is None:
        raise ValueError("rollout mode and environment source are incompatible")
    observed = [int(value) for value in seeds]
    if not observed or len(observed) != len(set(observed)):
        raise ValueError("rollout seed request must be non-empty and unique")
    expected = {int(value) for value in registry["partitions"][partition]}
    if not set(observed).issubset(expected):
        label = partition.replace("_", " ")
        raise ValueError(f"seeds are outside the {label} partition")
    return partition


def validate_policy_role(args) -> dict[str, object]:
    diagnostic = str(args.policy) == "oracle_action_audit_diagnostic"
    if diagnostic and str(args.mode) != "diagnostic":
        raise ValueError("oracle action audit is diagnostic and not deployable")
    if str(args.mode) == "diagnostic" and not diagnostic:
        raise ValueError("diagnostic mode requires the oracle action audit policy")
    return {
        "deployable": not diagnostic,
        "diagnostic_role": "privileged_upper_bound" if diagnostic else None,
    }


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument(
        "--mode",
        choices=("diagnostic", "development", "confirmation"),
        default="diagnostic",
    )
    parser.add_argument(
        "--policy",
        choices=(
            "executable_random",
            "paper9_mpc",
            "legacy_value_filter",
            "model_reward_greedy",
            "rank_only",
            "distributional_risk",
            "online_expert_selector",
            "pcc_matched",
            "pcc_full",
            "oracle_action_audit_diagnostic",
        ),
        default="pcc_matched",
    )
    parser.add_argument("--env-source", choices=("paper9", "neijiang"), default="paper9")
    parser.add_argument("--prepared-dir", default=str(ROOT.parent))
    parser.add_argument("--checkpoint-root", default=None)
    parser.add_argument("--calibrator", default=None)
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
    parser.add_argument("--model-seed", type=int, default=5101)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--rollout-steps", type=int, default=3)
    parser.add_argument("--planning-horizon", type=int, default=3)
    parser.add_argument("--candidate-budget", type=int, default=None)
    parser.add_argument("--compute-mode", choices=("matched", "full"), default="matched")
    parser.add_argument("--tolerance-scale", type=float, default=0.05)
    parser.add_argument("--residual-window", type=int, default=10)
    parser.add_argument("--executable-threshold", type=float, default=0.95)
    parser.add_argument("--risk-penalty", type=float, default=1.0)
    parser.add_argument("--expert-learning-rate", type=float, default=0.1)
    parser.add_argument("--reference-horizon", type=int, default=5)
    parser.add_argument("--reference-top-k", type=int, default=50)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
        validate_registry,
        verify_frozen_registry,
    )
    from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
    from paper10_geojepa_mpc.planning.executed_feedback import ExecutedFeedbackScaler
    from paper10_geojepa_mpc.planning.paired_conformal import load_joint_calibrator
    from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
    from paper10_geojepa_mpc.planning.pcc_baselines import (
        PCCObservablePolicy,
        SelectorPolicy,
        matched_pool_size,
    )
    from paper10_geojepa_mpc.planning.pcc_selector import load_pcc_ensemble

    args = parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(PAPER9_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER9_DIR))
    registry_path = Path(args.registry)
    registry = load_registry(registry_path)
    validate_registry(registry)
    requested_seeds = _parse_seed_spec(args.seeds)
    validate_policy_role(args)
    validate_rollout_request(
        registry,
        mode=args.mode,
        env_source=args.env_source,
        seeds=requested_seeds,
    )
    if args.mode in {"confirmation", "diagnostic"}:
        registry_digest = verify_frozen_registry(registry)
    else:
        registry_digest = _sha256_file(registry_path)
    if args.mode == "confirmation":
        selected = registry["selected_config"]
        planning_horizon = int(selected["planning_horizon"])
        tolerance_scale = float(selected["tolerance_scale"])
        residual_window = int(selected["residual_window"])
    else:
        planning_horizon = int(args.planning_horizon)
        tolerance_scale = float(args.tolerance_scale)
        residual_window = int(args.residual_window)

    needs_ensemble = args.policy in {
        "distributional_risk",
        "online_expert_selector",
        "pcc_matched",
        "pcc_full",
    }
    if needs_ensemble and args.checkpoint_root is None:
        raise ValueError(f"--checkpoint-root is required for {args.policy}")
    ensemble = (
        load_pcc_ensemble(args.checkpoint_root, device=args.device)
        if needs_ensemble
        else []
    )
    if ensemble:
        _validate_ensemble_model_seed(
            ensemble,
            expected_model_seed=int(args.model_seed),
        )
    if args.policy.startswith("pcc_") and args.calibrator is None:
        raise ValueError(f"--calibrator is required for {args.policy}")
    calibrator = (
        load_joint_calibrator(args.calibrator)
        if args.policy.startswith("pcc_")
        else None
    )
    env = _make_env(args.env_source, args.prepared_dir)

    def strict_mask(runtime_env):
        return np.asarray(runtime_env.action_masks(), dtype=bool) & np.asarray(
            executable_swap_mask(runtime_env),
            dtype=bool,
        )

    if args.mode == "diagnostic":
        output_path = Path(args.output)
        checkpoint_digests = []
        existing = load_resumable_results(
            output_path,
            registry_digest=registry_digest,
            checkpoint_digests=checkpoint_digests,
        )
        completed = set(existing["completed_seeds"]) if args.resume else set()
        for seed in requested_seeds:
            if seed in completed:
                continue
            result = run_oracle_diagnostic_episode(
                env=env,
                seed=seed,
                rollout_steps=args.rollout_steps,
                metric_reader=_metric_reader,
                action_mask_fn=strict_mask,
            )
            result.update(
                {
                    "registry_digest": registry_digest,
                    "checkpoint_digests": checkpoint_digests,
                    "model_dependency": "none",
                }
            )
            write_seed_result_atomic(
                output_path,
                seed_result=result,
                registry_digest=registry_digest,
                checkpoint_digests=checkpoint_digests,
            )
        print(output_path.read_text(encoding="utf-8"))
        return

    reference_adapter = TorchCheckpointMPCAdapter.from_checkpoint(
        args.reference_checkpoint,
        device=args.device,
    )
    reference_adapter.assert_compatible(env.n_blocks)
    ensemble_size = len(ensemble)
    compute_mode = (
        "full" if args.policy == "pcc_full" else args.compute_mode
    )
    candidate_budget = (
        matched_pool_size(ensemble_size)
        if ensemble_size and compute_mode == "matched"
        else 50
    )
    if args.candidate_budget is not None:
        candidate_budget = int(args.candidate_budget)
    max_member_evaluations = (
        50 if ensemble_size and compute_mode == "matched" else None
    )
    if ensemble:
        horizon_index = (1, 3, 5).index(planning_horizon)
        objective_scale = np.asarray(
            ensemble[0][1]["objective_scaling"]["scale"],
            dtype=np.float64,
        )
        tolerances = objective_scale[horizon_index, 1:] * tolerance_scale
    else:
        tolerances = np.zeros(3, dtype=np.float64)

    reward_ranker = _adapter_ranker(reference_adapter, score_mode="reward")
    value_ranker = _adapter_ranker(reference_adapter, score_mode="value")
    checkpoint_paths = (
        sorted(Path(args.checkpoint_root).glob("member_*.pt"))
        if args.checkpoint_root is not None
        else []
    )
    checkpoint_digests = [_sha256_file(path) for path in checkpoint_paths]
    if not checkpoint_digests:
        checkpoint_digests = [_sha256_file(args.reference_checkpoint)]
    output_path = Path(args.output)
    existing = load_resumable_results(
        output_path,
        registry_digest=registry_digest,
        checkpoint_digests=checkpoint_digests,
    )
    completed = set(existing["completed_seeds"]) if args.resume else set()

    for seed in requested_seeds:
        if seed in completed:
            continue
        reference_rng = np.random.default_rng(seed + 17001)

        def reference_selector(state, rng):
            return _select_paper9_reference_action(
                reference_adapter,
                state,
                rng,
                horizon=int(args.reference_horizon),
                top_k=int(args.reference_top_k),
                gamma=0.99,
            )

        reference_policy = SelectorPolicy(
            reference_selector,
            reference_rng,
            "paper9_mpc",
        )
        from paper10_geojepa_mpc.planning.pcc_baselines import (
            DistributionalRiskPolicy,
            ExecutableRandomPolicy,
            GreedyRankingPolicy,
            OnlineExpertSelector,
        )
        if args.policy == "executable_random":
            policy = ExecutableRandomPolicy(np.random.default_rng(seed + 19001))
        elif args.policy == "paper9_mpc":
            policy = reference_policy
        elif args.policy == "legacy_value_filter":
            from paper10_geojepa_mpc.planning.value_filter_selector import (
                value_filter_mpc_select_action,
            )

            def value_filter_selector(state, rng):
                action, info = value_filter_mpc_select_action(
                    reference_adapter,
                    state["block_features"],
                    state["global_features"],
                    state["executable_mask"],
                    horizon=int(args.reference_horizon),
                    top_k=int(args.reference_top_k),
                    gamma=0.99,
                    n_rollouts=1,
                    continuation="random",
                    scoring="reward",
                    candidate_score_mode="value",
                    stable_candidate_order=True,
                    random_continuation_mode="common",
                    rng=rng,
                )
                info["unexecuted_real_reward_queries"] = 0
                return action, info

            policy = SelectorPolicy(
                value_filter_selector,
                np.random.default_rng(seed + 18001),
                "legacy_value_filter",
            )
        elif args.policy == "model_reward_greedy":
            policy = GreedyRankingPolicy(reward_ranker, "model_reward_greedy")
        elif args.policy == "rank_only":
            policy = GreedyRankingPolicy(value_ranker, "rank_only")
        else:
            risk_policy = DistributionalRiskPolicy(
                ensemble=ensemble,
                proposal_rankers=[reward_ranker, value_ranker],
                candidate_budget=candidate_budget,
                planning_horizon=planning_horizon,
                risk_penalty=float(args.risk_penalty),
                device=args.device,
            )
            if args.policy == "distributional_risk":
                policy = risk_policy
            elif args.policy == "online_expert_selector":
                policy = OnlineExpertSelector(
                    [
                        reference_policy,
                        GreedyRankingPolicy(reward_ranker, "model_reward_greedy"),
                        risk_policy,
                    ],
                    learning_rate=float(args.expert_learning_rate),
                    rng=np.random.default_rng(seed + 20001),
                )
            else:
                feedback = ExecutedFeedbackScaler(
                    window=residual_window,
                    q_joint=calibrator.q_joint,
                )
                policy = PCCObservablePolicy(
                    ensemble=ensemble,
                    calibrator=calibrator,
                    feedback_scaler=feedback,
                    reference_policy=reference_policy,
                    proposal_rankers=[reward_ranker, value_ranker],
                    candidate_budget=candidate_budget,
                    planning_horizon=planning_horizon,
                    tolerances=tolerances,
                    executable_threshold=float(args.executable_threshold),
                    device=args.device,
                    max_member_evaluations=max_member_evaluations,
                )
        result = run_policy_episode(
            env=env,
            policy=policy,
            seed=seed,
            rollout_steps=args.rollout_steps,
            metric_reader=_metric_reader,
            action_mask_fn=strict_mask,
        )
        result.update(
            {
                "policy": args.policy,
                "model_seed": int(args.model_seed),
                "registry_digest": registry_digest,
                "checkpoint_digests": checkpoint_digests,
            }
        )
        write_seed_result_atomic(
            output_path,
            seed_result=result,
            registry_digest=registry_digest,
            checkpoint_digests=checkpoint_digests,
        )
    print(output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
