import hashlib
import json
from pathlib import Path

import numpy as np

from paper10_geojepa_mpc.planning.paper9_memory_efficient import (
    memory_efficient_mpc_select_action,
)


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


def build_pcc_policy_factory(
    *,
    ensemble,
    calibrator,
    reference_adapter,
    proposal_rankers,
    device: str,
    planning_horizon: int,
    candidate_budget: int,
    tolerance_scale: float,
    action_mask_fn,
    reference_horizon: int,
    reference_top_k: int,
    reference_gamma: float,
    executable_threshold: float = 0.95,
    screening_batch_size: int = 64,
):
    from paper10_geojepa_mpc.models.pcc_geojepa import HORIZONS
    from paper10_geojepa_mpc.planning.executed_feedback import (
        ExecutedFeedbackScaler,
    )
    from paper10_geojepa_mpc.planning.pcc_selector import pcc_select_action

    if not ensemble:
        raise ValueError("offline PCC policy requires a non-empty ensemble")
    if int(planning_horizon) not in HORIZONS:
        raise ValueError("offline PCC planning horizon must be 1, 3, or 5")
    if int(candidate_budget) <= 0:
        raise ValueError("offline PCC candidate budget must be positive")
    if not np.isfinite(tolerance_scale) or float(tolerance_scale) < 0.0:
        raise ValueError("offline PCC tolerance scale must be non-negative")
    objective_scale = np.asarray(
        ensemble[0][1]["objective_scaling"]["scale"],
        dtype=np.float64,
    )
    horizon_index = HORIZONS.index(int(planning_horizon))
    tolerances = objective_scale[horizon_index, 1:] * float(tolerance_scale)
    feedback = ExecutedFeedbackScaler(window=1, q_joint=calibrator.q_joint)

    def factory(env):
        reference_adapter.assert_compatible(env.n_blocks)

        def policy(runtime_env, rng):
            block = np.asarray(
                runtime_env._get_block_features(),
                dtype=np.float32,
            ).copy()
            state = {
                "block_features": block,
                "neighbour_features": build_neighbour_feature_matrix(
                    runtime_env,
                    block,
                ),
                "global_features": np.asarray(
                    runtime_env._get_global_features(),
                    dtype=np.float32,
                ).copy(),
                "executable_mask": np.asarray(
                    action_mask_fn(runtime_env),
                    dtype=bool,
                ).copy(),
            }
            reference_action, _ = memory_efficient_mpc_select_action(
                reference_adapter,
                state["block_features"],
                state["global_features"],
                state["executable_mask"],
                horizon=int(reference_horizon),
                top_k=int(reference_top_k),
                gamma=float(reference_gamma),
                n_rollouts=1,
                continuation="random",
                scoring="reward",
                screening_batch_size=int(screening_batch_size),
                rng=rng,
            )
            proposal_groups = [ranker(state) for ranker in proposal_rankers]
            action, _ = pcc_select_action(
                ensemble=ensemble,
                calibrator=calibrator,
                feedback_scaler=feedback,
                block_features=state["block_features"],
                neighbour_features=state["neighbour_features"],
                global_features=state["global_features"],
                executable_mask=state["executable_mask"],
                reference_policy=lambda: int(reference_action),
                proposal_groups=proposal_groups,
                candidate_budget=int(candidate_budget),
                planning_horizon=int(planning_horizon),
                tolerances=tolerances,
                executable_threshold=float(executable_threshold),
                device=str(device),
            )
            return int(action)

        return policy

    return factory


def _adapter_ranker(adapter, *, score_mode: str):
    import torch

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
                torch.as_tensor(
                    valid,
                    dtype=torch.long,
                    device=adapter.device,
                ),
                score_mode=score_mode,
            ).detach().cpu().numpy()
        order = np.lexsort((valid, -scores))
        return valid[order]

    return rank


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_pcc_policy_metadata(
    *,
    model_seed: int,
    checkpoint_digests,
    calibrator_digest: str,
    joint_coverage: float,
    planning_horizon: int,
    candidate_budget: int,
    tolerance_scale: float,
    reference_checkpoint_sha256: str,
    reference_horizon: int,
    reference_top_k: int,
    reference_gamma: float,
) -> dict[str, object]:
    return {
        "name": "pcc_round1",
        "model_seed": int(model_seed),
        "checkpoint_digests": list(map(str, checkpoint_digests)),
        "calibrator_digest": str(calibrator_digest),
        "joint_coverage": float(joint_coverage),
        "planning_horizon": int(planning_horizon),
        "candidate_budget": int(candidate_budget),
        "tolerance_scale": float(tolerance_scale),
        "executed_feedback": False,
        "reference_policy": {
            "name": "paper9_mpc",
            "checkpoint_sha256": str(reference_checkpoint_sha256),
            "planning_horizon": int(reference_horizon),
            "top_k": int(reference_top_k),
            "gamma": float(reference_gamma),
        },
    }


def build_pcc_checkpoint_policy_factory(
    *,
    checkpoint_root: str | Path,
    calibrator_path: str | Path,
    reference_checkpoint: str | Path,
    model_seed: int,
    device: str,
    planning_horizon: int,
    candidate_budget: int,
    tolerance_scale: float,
    action_mask_fn,
    reference_horizon: int,
    reference_top_k: int,
    reference_gamma: float,
    executable_threshold: float = 0.95,
):
    from paper10_geojepa_mpc.planning.paired_conformal import (
        load_joint_calibrator,
    )
    from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
    from paper10_geojepa_mpc.planning.pcc_selector import load_pcc_ensemble

    checkpoint_root = Path(checkpoint_root)
    checkpoint_paths = sorted(checkpoint_root.glob("member_*.pt"))
    if not checkpoint_paths:
        raise ValueError(f"no PCC checkpoints found under {checkpoint_root}")
    ensemble = load_pcc_ensemble(checkpoint_root, device=device)
    observed_model_seeds = {
        int(checkpoint.get("model_seed", -1)) for _, checkpoint in ensemble
    }
    if observed_model_seeds != {int(model_seed)}:
        raise ValueError("offline PCC checkpoint lineage mismatch")
    calibrator = load_joint_calibrator(calibrator_path)
    checkpoint_digests = tuple(_sha256_file(path) for path in checkpoint_paths)
    if tuple(calibrator.checkpoint_digests) != checkpoint_digests:
        raise ValueError("offline PCC calibrator checkpoint lineage mismatch")
    reference_adapter = TorchCheckpointMPCAdapter.from_checkpoint(
        reference_checkpoint,
        device=device,
    )
    factory = build_pcc_policy_factory(
        ensemble=ensemble,
        calibrator=calibrator,
        reference_adapter=reference_adapter,
        proposal_rankers=[
            _adapter_ranker(reference_adapter, score_mode="reward"),
            _adapter_ranker(reference_adapter, score_mode="value"),
        ],
        device=device,
        planning_horizon=planning_horizon,
        candidate_budget=candidate_budget,
        tolerance_scale=tolerance_scale,
        action_mask_fn=action_mask_fn,
        reference_horizon=reference_horizon,
        reference_top_k=reference_top_k,
        reference_gamma=reference_gamma,
        executable_threshold=executable_threshold,
    )
    calibrator_payload = json.loads(Path(calibrator_path).read_text(encoding="utf-8"))
    metadata = build_pcc_policy_metadata(
        model_seed=model_seed,
        checkpoint_digests=checkpoint_digests,
        calibrator_digest=str(calibrator_payload["calibrator_digest"]),
        joint_coverage=calibrator.coverage,
        planning_horizon=planning_horizon,
        candidate_budget=candidate_budget,
        tolerance_scale=tolerance_scale,
        reference_checkpoint_sha256=_sha256_file(Path(reference_checkpoint)),
        reference_horizon=reference_horizon,
        reference_top_k=reference_top_k,
        reference_gamma=reference_gamma,
    )
    return factory, metadata
