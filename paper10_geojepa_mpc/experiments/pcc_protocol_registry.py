import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


DEFAULT_REGISTRY = Path(__file__).with_name("protocols") / "pcc_v1.json"
LOCKED_PCC_V1_PARTITIONS = {
    "train": tuple(range(1000, 1008)),
    "calibration": tuple(range(2000, 2020)),
    "development": tuple(range(3000, 3010)),
    "confirmation": tuple(range(4000, 4020)),
    "dongxing_adaptation": tuple(range(6000, 6004)),
    "dongxing_calibration": tuple(range(7000, 7020)),
    "dongxing_confirmation": tuple(range(8000, 8020)),
}
LOCKED_PCC_V1_MODEL_SEEDS = (5101, 5102, 5103)
LOCKED_PCC_V1_CONTRACT = {
    "horizons": [1, 3, 5],
    "offline_sampling": {
        "train": {"states_per_trajectory": 20, "candidate_actions": 8},
        "calibration": {"states_per_trajectory": 10, "candidate_actions": 8},
        "dongxing_adaptation": {
            "states_per_trajectory": 20,
            "candidate_actions": 8,
        },
        "dongxing_calibration": {
            "states_per_trajectory": 10,
            "candidate_actions": 8,
        },
    },
    "offline_reference_policy": {
        "name": "paper9_mpc",
        "checkpoint_sha256": "fd3cdeeb827dc59a30e559a36fc95166db77447dc6e7d1d4b5b4c081704c947f",
        "planning_horizon": 5,
        "top_k": 50,
        "gamma": 0.99,
        "continuation": "paper9_mpc",
    },
    "grid": {
        "ensemble_size": [3, 5],
        "joint_coverage": [0.8, 0.9, 0.95],
        "tolerance_scale": [0.0, 0.05, 0.1],
        "planning_horizon": [3, 5],
        "residual_window": [10, 20],
        "policy_round": [1, 2],
    },
    "development_baseline_anchor": {
        "ensemble_size": 3,
        "policy_round": 1,
        "joint_coverage": 0.9,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "residual_window": 10,
        "risk_penalty": 1.0,
        "expert_learning_rate": 0.1,
        "stage_a_seeds": [3000, 3001, 3002, 3003, 3004],
        "stage_a_rollout_steps": 3,
        "baseline_seeds": [
            3000,
            3001,
            3002,
            3003,
            3004,
            3005,
            3006,
            3007,
            3008,
            3009,
        ],
        "baseline_rollout_steps": 100,
        "candidates": [
            "executable_random",
            "paper9_mpc",
            "legacy_value_filter",
            "model_reward_greedy",
            "rank_only",
            "distributional_risk",
            "online_expert_selector",
        ],
    },
    "confirmation": {
        "rollout_steps": 100,
        "one_sided_confidence": 0.95,
        "primary_comparison_count": 1,
        "objective_noninferiority_margin": 0.0,
    },
    "online_information_set": {
        "current_observable_state": True,
        "executable_action_mask": True,
        "frozen_models_calibrators_and_policies": True,
        "executed_action_outcomes_only": True,
        "unexecuted_real_reward_queries": 0,
        "environment_clone_rewind_or_restore": False,
        "confirmation_weight_updates": False,
    },
    "deployable_baselines": [
        "executable_random",
        "paper9_mpc",
        "legacy_value_filter",
        "model_reward_greedy",
        "rank_only",
        "distributional_risk",
        "online_expert_selector",
        "pcc_matched",
        "pcc_full",
    ],
    "diagnostic_policies": ["oracle_action_audit_diagnostic"],
    "required_ablations": [
        "county_specific_action_embedding",
        "single_model",
        "no_aleatoric_scale",
        "uncalibrated_ensemble_scale",
        "reward_only",
        "no_executed_feedback",
        "no_reference_fallback",
        "one_policy_improvement_round",
    ],
    "compute_budget": {
        "single_model_candidate_equivalents": 50,
        "matched_ensemble_pool_rule": "floor(50 / ensemble_size)",
        "maximum_excess_candidate_equivalents": 1,
    },
    "success_gates": {
        "minimum_jointly_supporting_model_seeds": 2,
        "matched_compute_must_reach_same_conclusion": True,
        "bishan": {
            "reward_lower_bound_strictly_positive": True,
            "planning_lower_bound_minimum": 0.0,
        },
        "dongxing": {
            "reward_lower_bound_minimum": 0.0,
            "planning_lower_bound_minimum": 0.0,
        },
        "information_audit_requires_zero_unexecuted_real_reward_queries": True,
    },
}


def _canonical(payload: dict[str, Any]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "frozen_digest"}
    return json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def load_registry(path: str | Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_registry(payload: dict[str, Any]) -> None:
    roles = payload["partitions"]
    observed: dict[int, str] = {}
    for role, seeds in roles.items():
        for raw_seed in seeds:
            seed = int(raw_seed)
            if seed in observed:
                raise ValueError(
                    f"partition overlap: seed {seed} in {observed[seed]} and {role}"
                )
            if 0 <= seed <= 19:
                raise ValueError(f"historical seed forbidden: {seed}")
            observed[seed] = role

    model_seeds = tuple(map(int, payload["model_seeds"]))
    if len(set(model_seeds)) != len(model_seeds):
        raise ValueError("model seed overlap")
    overlap = set(model_seeds) & set(observed)
    if overlap:
        raise ValueError(f"model seed overlaps data partition: {sorted(overlap)}")

    if payload.get("protocol_id") == "pcc_v1":
        actual = {role: tuple(map(int, seeds)) for role, seeds in roles.items()}
        if actual != LOCKED_PCC_V1_PARTITIONS:
            raise ValueError("locked partition mismatch for pcc_v1")
        if model_seeds != LOCKED_PCC_V1_MODEL_SEEDS:
            raise ValueError("locked model seed mismatch for pcc_v1")
        for field, expected in LOCKED_PCC_V1_CONTRACT.items():
            if payload.get(field) != expected:
                raise ValueError(
                    f"locked scientific contract mismatch for pcc_v1: {field}"
                )


def freeze_registry(
    path: str | Path,
    selected_config: dict[str, Any],
) -> dict[str, Any]:
    path = Path(path)
    payload = load_registry(path)
    validate_registry(payload)
    if payload.get("status") != "development":
        raise ValueError("registry is already frozen")
    payload["status"] = "frozen"
    payload["selected_config"] = selected_config
    payload["frozen_digest"] = _digest(payload)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return payload


def verify_frozen_registry(payload: dict[str, Any]) -> str:
    if payload.get("status") != "frozen":
        raise ValueError("registry is not frozen")
    expected = payload.get("frozen_digest")
    observed = _digest(payload)
    if not isinstance(expected, str) or observed != expected:
        raise ValueError("frozen registry digest mismatch")
    validate_registry(payload)
    return observed


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify-development", action="store_true")
    group.add_argument("--verify-frozen", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    registry_path = Path(args.registry)
    payload = load_registry(registry_path)
    validate_registry(payload)
    if args.verify_frozen:
        registry_hash = verify_frozen_registry(payload)
    else:
        if payload.get("status") != "development":
            raise ValueError("registry is not in development")
        registry_hash = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "status": payload["status"],
                "registry_file_sha256": registry_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
