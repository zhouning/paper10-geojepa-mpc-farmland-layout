import argparse
import json
from pathlib import Path
import sys

import torch


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper10_geojepa_mpc.training.e0_training import (
    evaluate_candidate_action_metrics,
    load_e0_checkpoint,
    load_npz_arrays,
)


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
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--batch-states", type=int, default=4)
    parser.add_argument("--max-states", type=int, default=1000)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model, checkpoint = load_e0_checkpoint(args.checkpoint, device=args.device)
    pairwise = load_npz_arrays(args.pairwise, max_rows=args.max_states)
    device = torch.device(args.device)

    metrics = evaluate_candidate_action_metrics(
        model,
        torch.tensor(pairwise["states_bf"], device=device, dtype=torch.float32),
        torch.tensor(pairwise["states_gf"], device=device, dtype=torch.float32),
        torch.tensor(pairwise["actions"], device=device, dtype=torch.long),
        torch.tensor(pairwise["rewards"], device=device, dtype=torch.float32),
        top_k=args.top_k,
        batch_states=args.batch_states,
        max_states=args.max_states,
    )
    metrics["checkpoint"] = str(args.checkpoint)
    metrics["checkpoint_epoch"] = checkpoint["epoch"]
    metrics["checkpoint_metric"] = checkpoint["checkpoint_metric"]
    metrics["checkpoint_value"] = checkpoint["checkpoint_value"]

    text = json.dumps(metrics, indent=2, sort_keys=True)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text)


if __name__ == "__main__":
    main()
