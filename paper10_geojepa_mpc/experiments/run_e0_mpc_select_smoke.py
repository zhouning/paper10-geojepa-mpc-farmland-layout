import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.planning.paper9_adapter import TorchCheckpointMPCAdapter
from paper10_geojepa_mpc.planning.scoring import score_candidate_actions, select_topk_actions
from paper10_geojepa_mpc.training.e0_training import load_npz_arrays


def _load_paper9_mpc_select_action():
    path = ROOT / "arcgis_toolbox_paper9" / "private_source" / "mpc_plan.py"
    spec = importlib.util.spec_from_file_location("paper9_private_mpc_plan", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.mpc_select_action


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default=str(
            ROOT
            / "paper10_geojepa_mpc"
            / "experiments"
            / "checkpoints"
            / "e0_bishan_rank_seed2028"
            / "rank_seed2028.pt"
        ),
    )
    parser.add_argument("--pairwise", default=str(ROOT / "tool2" / "pairwise.npz"))
    parser.add_argument("--state-index", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--horizon", type=int, default=1)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter = TorchCheckpointMPCAdapter.from_checkpoint(args.checkpoint, device=args.device)
    pairwise = load_npz_arrays(args.pairwise, max_rows=args.state_index + 1)
    bf = pairwise["states_bf"][args.state_index]
    gf = pairwise["states_gf"][args.state_index]
    candidate_actions = pairwise["actions"][args.state_index]
    candidate_rewards = pairwise["rewards"][args.state_index]

    action_mask = np.zeros(adapter.n_blocks, dtype=bool)
    action_mask[candidate_actions] = True

    mpc_select_action = _load_paper9_mpc_select_action()
    chosen_action, info = mpc_select_action(
        adapter,
        bf,
        gf,
        action_mask,
        horizon=args.horizon,
        top_k=args.top_k,
        gamma=args.gamma,
        n_rollouts=1,
        continuation="random",
        scoring="reward",
        rng=np.random.default_rng(12345),
    )

    with torch.no_grad():
        scores = score_candidate_actions(
            adapter.model,
            torch.tensor(bf, dtype=torch.float32, device=adapter.device),
            torch.tensor(gf, dtype=torch.float32, device=adapter.device),
            torch.tensor(candidate_actions, dtype=torch.long, device=adapter.device),
        ).cpu()
    top_actions, top_scores = select_topk_actions(
        torch.tensor(candidate_actions, dtype=torch.long), scores, args.top_k
    )

    chosen_positions = np.where(candidate_actions == chosen_action)[0]
    chosen_true_reward = (
        float(candidate_rewards[chosen_positions[0]]) if len(chosen_positions) else None
    )
    true_best_pos = int(np.argmax(candidate_rewards))
    true_best_reward = float(candidate_rewards[true_best_pos])

    result = {
        "checkpoint": str(args.checkpoint),
        "state_index": args.state_index,
        "horizon": args.horizon,
        "top_k": args.top_k,
        "n_candidate_actions": int(len(candidate_actions)),
        "chosen_action": int(chosen_action),
        "chosen_true_reward": chosen_true_reward,
        "true_best_action": int(candidate_actions[true_best_pos]),
        "true_best_reward": true_best_reward,
        "one_step_regret": (
            true_best_reward - chosen_true_reward if chosen_true_reward is not None else None
        ),
        "model_top_actions": [int(x) for x in top_actions.tolist()],
        "model_top_scores": [float(x) for x in top_scores.tolist()],
        "mpc_info": info,
    }

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text)


if __name__ == "__main__":
    main()
