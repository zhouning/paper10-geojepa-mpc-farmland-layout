import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
    load_registry,
    validate_registry,
)
from paper10_geojepa_mpc.experiments.pcc_v1_1_selected_labels import (
    generate_selected_label_trajectory,
    load_resumable_selected_manifest,
    write_selected_manifest,
    write_selected_trajectory_artifact,
)
from paper10_geojepa_mpc.models.pcc_paired_delta import HORIZONS


ROOT = Path(__file__).resolve().parents[2]
PAPER9_DIR = ROOT / "arcgis_toolbox_paper9"


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_digest(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument(
        "--partition",
        required=True,
        choices=("calibration", "development"),
    )
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--checkpoint-root", required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--ensemble-size", type=int, required=True)
    parser.add_argument("--policy-round", type=int, required=True)
    parser.add_argument(
        "--compute-mode",
        choices=("matched", "full"),
        required=True,
    )
    parser.add_argument("--reference-checkpoint", required=True)
    parser.add_argument("--env-source", choices=("paper9",), required=True)
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--states-per-trajectory", type=int, required=True)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-root", required=True)
    return parser.parse_args(argv)


def _seed_artifact_for_root(
    seed: int,
    seed_manifest: dict[str, object],
) -> dict[str, object]:
    artifact = dict(seed_manifest["artifacts"][0])
    artifact["path"] = (
        Path(f"seed_{int(seed)}") / str(artifact["path"])
    ).as_posix()
    return artifact


def _load_completed_seed(
    output_root: Path,
    seed: int,
    lineage: dict[str, object],
) -> dict[str, object] | None:
    manifest_path = output_root / f"seed_{int(seed)}" / "manifest.json"
    if not manifest_path.exists():
        return None
    payload = load_resumable_selected_manifest(
        manifest_path,
        expected_lineage=lineage,
    )
    if payload["trajectory_seeds"] != [int(seed)]:
        raise ValueError("resumable selected-label seed manifest mismatch")
    return payload


def _generate_seed(
    *,
    output_root: Path,
    lineage: dict[str, object],
    trajectory_seed: int,
    n_states: int,
    horizons: Sequence[int],
    gamma: float,
    env_factory,
    base_policy_factory,
    continuation_policy_factory,
    metric_reader,
    state_attrs,
) -> dict[str, object]:
    env = env_factory()
    dataset = generate_selected_label_trajectory(
        env=env,
        trajectory_seed=trajectory_seed,
        n_states=n_states,
        horizons=horizons,
        gamma=gamma,
        base_policy=base_policy_factory(env),
        continuation_policy=continuation_policy_factory(env),
        metric_reader=metric_reader,
        state_attrs=state_attrs,
    )
    root_artifact = write_selected_trajectory_artifact(
        output_root,
        trajectory_seed,
        dataset,
    )
    seed_dir = output_root / f"seed_{int(trajectory_seed)}"
    seed_artifact = {
        **root_artifact,
        "path": Path(str(root_artifact["path"])).name,
    }
    return write_selected_manifest(
        seed_dir,
        lineage=lineage,
        artifacts=[seed_artifact],
    )


def run_selected_label_partition(
    *,
    output_root: str | Path,
    lineage: dict[str, object],
    trajectory_seeds: Sequence[int],
    n_states: int,
    horizons: Sequence[int],
    gamma: float,
    env_factory,
    base_policy_factory,
    continuation_policy_factory,
    metric_reader,
    max_workers: int,
    resume: bool,
    state_attrs: Sequence[str] | None = None,
) -> dict[str, object]:
    output_root = Path(output_root)
    seeds = [int(value) for value in trajectory_seeds]
    if not seeds or len(seeds) != len(set(seeds)) or seeds != sorted(seeds):
        raise ValueError("selected-label seeds must be unique and sorted")
    if int(n_states) <= 0 or int(max_workers) <= 0:
        raise ValueError("selected-label state and worker counts must be positive")
    if tuple(int(value) for value in horizons) != HORIZONS:
        raise ValueError("selected labels require horizons 1, 3, and 5")

    root_manifest = output_root / "manifest.json"
    occupied_seed_dirs = [
        output_root / f"seed_{seed}"
        for seed in seeds
        if (output_root / f"seed_{seed}").exists()
    ]
    if not resume and (root_manifest.exists() or occupied_seed_dirs):
        raise ValueError(
            "selected-label output already exists; use --resume with matching lineage"
        )
    if resume and root_manifest.exists():
        payload = load_resumable_selected_manifest(
            root_manifest,
            expected_lineage=lineage,
        )
        if payload["trajectory_seeds"] != seeds:
            raise ValueError("resumable selected-label partition seed mismatch")
        return payload

    completed: dict[int, dict[str, object]] = {}
    if resume:
        for seed in seeds:
            payload = _load_completed_seed(output_root, seed, lineage)
            if payload is not None:
                completed[seed] = payload
    pending = [seed for seed in seeds if seed not in completed]
    with ThreadPoolExecutor(max_workers=int(max_workers)) as executor:
        futures = {
            executor.submit(
                _generate_seed,
                output_root=output_root,
                lineage=lineage,
                trajectory_seed=seed,
                n_states=int(n_states),
                horizons=horizons,
                gamma=float(gamma),
                env_factory=env_factory,
                base_policy_factory=base_policy_factory,
                continuation_policy_factory=continuation_policy_factory,
                metric_reader=metric_reader,
                state_attrs=state_attrs,
            ): seed
            for seed in pending
        }
        for future in as_completed(futures):
            completed[futures[future]] = future.result()

    artifacts = [
        _seed_artifact_for_root(seed, completed[seed]) for seed in seeds
    ]
    return write_selected_manifest(
        output_root,
        lineage=lineage,
        artifacts=artifacts,
    )


def _write_json_once(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != payload:
            raise ValueError(f"refusing to replace incompatible {path.name}")
        return
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _validate_contract(registry, args) -> list[int]:
    if registry.get("protocol_id") != "pcc_v1_1":
        raise ValueError("selected labels require the PCC v1.1 registry")
    if int(args.model_seed) not in {
        int(value) for value in registry["model_seeds"]
    }:
        raise ValueError("selected-label model seed is outside the registry")
    if int(args.ensemble_size) <= 0 or int(args.policy_round) <= 0:
        raise ValueError("selected-label ensemble size and policy round are invalid")
    if args.compute_mode not in registry["compute_modes"]:
        raise ValueError("selected-label compute mode is outside the registry")
    declared = [int(value) for value in registry["partitions"][args.partition]]
    seeds = _parse_seed_spec(args.seeds)
    if (
        not seeds
        or seeds != sorted(seeds)
        or len(seeds) != len(set(seeds))
        or not set(seeds) <= set(declared)
    ):
        raise ValueError("selected-label seeds must be a sorted partition subset")
    return seeds


def _rule_digests(registry, *, ensemble_size: int, compute_mode: str):
    anchor = registry["development_baseline_anchor"]
    candidate_payload = {
        "schema_version": 1,
        "protocol_id": registry["protocol_id"],
        "proposal_order": registry["candidate_selection"]["proposal_order"],
        "compute_mode": str(compute_mode),
        "ensemble_size": int(ensemble_size),
        "matched_pool_rule": registry["compute_budget"][
            "matched_ensemble_pool_rule"
        ],
        "full_candidate_budget": registry["compute_budget"][
            "single_model_candidate_equivalents"
        ],
        "deduplication": "stable_first_occurrence",
    }
    selector_payload = {
        "schema_version": 1,
        "protocol_id": registry["protocol_id"],
        "base_rule": registry["candidate_selection"]["base_rule"],
        "tie_break": registry["candidate_selection"]["tie_break"],
        "executable_probability_threshold": registry["candidate_selection"][
            "executable_probability_threshold"
        ],
        "planning_horizon": int(anchor["planning_horizon"]),
        "tolerance_scale": float(anchor["tolerance_scale"]),
        "fallback": "paper9_reference",
        "conformal_coverage": None,
    }
    return _canonical_digest(candidate_payload), _canonical_digest(selector_payload)


def _build_runtime(registry, args, *, registry_digest: str):
    from paper10_geojepa_mpc.experiments.pcc_offline_policy import (
        _adapter_ranker,
        build_neighbour_feature_matrix,
    )
    from paper10_geojepa_mpc.experiments.pcc_value_labels import (
        _default_metric_reader,
        build_checkpoint_reference_policy_factory,
    )
    from paper10_geojepa_mpc.experiments.value_label_generation import (
        _make_label_env,
    )
    from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask
    from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
    from paper10_geojepa_mpc.planning.paper9_memory_efficient import (
        memory_efficient_mpc_select_action,
    )
    from paper10_geojepa_mpc.planning.pcc_v1_1_selector import (
        build_v1_1_candidate_pool,
        choose_base_candidate,
        load_pcc_v1_1_ensemble,
        predict_direct_paired_ensemble,
    )

    ensemble = load_pcc_v1_1_ensemble(args.checkpoint_root, device=args.device)
    if len(ensemble) != int(args.ensemble_size):
        raise ValueError("selected-label ensemble size mismatch")
    for _, checkpoint in ensemble:
        if (
            int(checkpoint.get("model_seed", -1)) != int(args.model_seed)
            or checkpoint.get("registry_digest") != registry_digest
            or checkpoint.get("protocol_id") != "pcc_v1_1"
        ):
            raise ValueError("selected-label checkpoint lineage mismatch")
    if int(args.policy_round) != int(registry["viability"]["policy_round"]):
        raise ValueError("selected-label policy round is outside the pilot contract")

    reference_path = Path(args.reference_checkpoint)
    reference_contract = registry["offline_reference_policy"]
    reference_digest = _sha256_file(reference_path)
    if reference_digest != reference_contract["checkpoint_sha256"]:
        raise ValueError("selected-label reference checkpoint digest mismatch")
    if any(
        checkpoint.get("transfer_checkpoint_sha256") != reference_digest
        for _, checkpoint in ensemble
    ):
        raise ValueError("selected-label transfer checkpoint lineage mismatch")
    checkpoint_paths = sorted(Path(args.checkpoint_root).glob("member_*.pt"))
    checkpoint_digests = [_sha256_file(path) for path in checkpoint_paths]

    adapter = TorchCheckpointMPCAdapter.from_checkpoint(
        reference_path,
        device=args.device,
    )
    reference_factory = build_checkpoint_reference_policy_factory(
        reference_path,
        device=args.device,
        horizon=int(reference_contract["planning_horizon"]),
        top_k=int(reference_contract["top_k"]),
        gamma=float(reference_contract["gamma"]),
        action_mask_fn=lambda env: (
            np.asarray(env.action_masks(), dtype=bool)
            & np.asarray(executable_swap_mask(env), dtype=bool)
        ),
    )
    proposal_rankers = (
        _adapter_ranker(adapter, score_mode="reward"),
        _adapter_ranker(adapter, score_mode="value"),
    )
    anchor = registry["development_baseline_anchor"]
    planning_horizon = int(anchor["planning_horizon"])
    horizon_index = HORIZONS.index(planning_horizon)
    objective_scale = np.asarray(
        ensemble[0][1]["delta_scaling"]["scale"],
        dtype=np.float64,
    )
    tolerances = (
        objective_scale[horizon_index, 1:] * float(anchor["tolerance_scale"])
    )
    executable_threshold = float(
        registry["candidate_selection"]["executable_probability_threshold"]
    )

    def strict_mask(env):
        base = np.asarray(env.action_masks(), dtype=bool)
        strict = np.asarray(executable_swap_mask(env), dtype=bool)
        if base.shape != strict.shape:
            raise ValueError("strict executable mask shape mismatch")
        return base & strict

    def base_policy_factory(env):
        adapter.assert_compatible(env.n_blocks)
        reference_policy = reference_factory(env)

        def policy(runtime_env, rng):
            mask = strict_mask(runtime_env)
            reference_action = int(reference_policy(runtime_env, rng))
            block = np.asarray(
                runtime_env._get_block_features(), dtype=np.float32
            )
            state = {
                "block_features": block,
                "neighbour_features": build_neighbour_feature_matrix(
                    runtime_env, block
                ),
                "global_features": np.asarray(
                    runtime_env._get_global_features(), dtype=np.float32
                ),
                "executable_mask": mask,
            }
            proposal_groups = [ranker(state) for ranker in proposal_rankers]
            actions = build_v1_1_candidate_pool(
                reference_action=reference_action,
                proposal_groups=proposal_groups,
                executable_mask=mask,
                compute_mode=args.compute_mode,
                ensemble_size=len(ensemble),
            )
            if actions.size == 0:
                selected_action = reference_action
                reason = "no_executable_alternative"
                mean = np.zeros((len(HORIZONS), 4), dtype=np.float64)
                scale = np.zeros_like(mean)
                probability = 1.0
            else:
                prediction = predict_direct_paired_ensemble(
                    ensemble,
                    block_features=state["block_features"],
                    neighbour_features=state["neighbour_features"],
                    global_features=state["global_features"],
                    actions=actions,
                    reference_action=reference_action,
                    compute_mode=args.compute_mode,
                    device=args.device,
                )
                selected_action, selection = choose_base_candidate(
                    prediction.actions,
                    prediction.mean_delta[:, horizon_index],
                    scales=prediction.paired_scale[:, horizon_index],
                    executable_probability=prediction.executable_probability,
                    tolerances=tolerances,
                    executable_threshold=executable_threshold,
                )
                reason = str(selection["base_selection_reason"])
                if selected_action is None:
                    selected_action = reference_action
                    mean = np.zeros((len(HORIZONS), 4), dtype=np.float64)
                    scale = np.zeros_like(mean)
                    probability = 1.0
                else:
                    index = int(
                        np.flatnonzero(prediction.actions == selected_action)[0]
                    )
                    mean = prediction.mean_delta[index]
                    scale = prediction.paired_scale[index]
                    probability = float(
                        prediction.executable_probability[index]
                    )
            return int(selected_action), {
                "base_selected_action": int(selected_action),
                "reference_action": reference_action,
                "selected_predicted_delta": mean.tolist(),
                "selected_predicted_scale": scale.tolist(),
                "selected_executable_probability": probability,
                "base_selection_reason": reason,
                "unexecuted_real_reward_queries": 0,
            }

        return policy

    return {
        "checkpoint_digests": checkpoint_digests,
        "reference_checkpoint_digest": reference_digest,
        "env_factory": lambda: _make_label_env(
            args.env_source, args.prepared_dir
        ),
        "base_policy_factory": base_policy_factory,
        "continuation_policy_factory": reference_factory,
        "metric_reader": _default_metric_reader,
    }


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    seeds = _validate_contract(registry, args)
    registry_digest = _sha256_file(args.registry)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(PAPER9_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER9_DIR))
    runtime = _build_runtime(registry, args, registry_digest=registry_digest)
    candidate_digest, selector_digest = _rule_digests(
        registry,
        ensemble_size=args.ensemble_size,
        compute_mode=args.compute_mode,
    )
    lineage = {
        "protocol_id": "pcc_v1_1",
        "registry_digest": registry_digest,
        "partition": str(args.partition),
        "model_seed": int(args.model_seed),
        "ensemble_size": int(args.ensemble_size),
        "policy_round": int(args.policy_round),
        "compute_mode": str(args.compute_mode),
        "checkpoint_digests": runtime["checkpoint_digests"],
        "candidate_generator_digest": candidate_digest,
        "base_selector_digest": selector_digest,
        "reference_checkpoint_digest": runtime[
            "reference_checkpoint_digest"
        ],
    }
    execution_plan = {
        "schema_version": 1,
        **lineage,
        "trajectory_seeds": seeds,
        "states_per_trajectory": int(args.states_per_trajectory),
        "max_workers": int(args.max_workers),
        "device": str(args.device),
    }
    output_root = Path(args.output_root)
    _write_json_once(output_root / "execution_plan.json", execution_plan)
    manifest = run_selected_label_partition(
        output_root=output_root,
        lineage=lineage,
        trajectory_seeds=seeds,
        n_states=args.states_per_trajectory,
        horizons=HORIZONS,
        gamma=float(registry["offline_reference_policy"]["gamma"]),
        env_factory=runtime["env_factory"],
        base_policy_factory=runtime["base_policy_factory"],
        continuation_policy_factory=runtime["continuation_policy_factory"],
        metric_reader=runtime["metric_reader"],
        max_workers=args.max_workers,
        resume=args.resume,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == "__main__":
    main()
