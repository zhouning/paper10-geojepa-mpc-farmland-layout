import argparse
import json
from pathlib import Path
from typing import Callable, Sequence

from paper10_geojepa_mpc.experiments.pcc_policy_iteration_execution import (
    DEFAULT_REFERENCE_CHECKPOINT,
    build_iteration_command_plan,
    execute_policy_iteration,
)
from paper10_geojepa_mpc.experiments.pcc_policy_iteration_lineage import (
    ROUND1_LABEL_POLICY_CONFIG,
    PolicyRound,
    build_policy_rounds,
    verify_policy_iteration_root,
    verify_round_manifest,
    write_round_manifest,
)


def run_two_round_policy_iteration(
    *,
    rounds: int,
    round0_train_labels,
    round0_calibration_labels,
    round1_checkpoints,
    validate_labels: Callable,
    calibrate: Callable,
    generate_labels: Callable,
    train: Callable,
) -> dict[str, object]:
    if int(rounds) != 2:
        raise ValueError("PCC requires exactly two policy-improvement rounds")

    validate_labels(1, round0_train_labels)
    round1_calibrator = calibrate(
        1,
        round0_calibration_labels,
        round1_checkpoints,
    )
    round2_train_labels = generate_labels(
        "train_labels",
        2,
        "pcc_round1",
        dict(ROUND1_LABEL_POLICY_CONFIG),
    )
    round2_calibration_labels = generate_labels(
        "calibration_labels",
        2,
        "pcc_round1",
        dict(ROUND1_LABEL_POLICY_CONFIG),
    )
    round2_checkpoints = train(
        2,
        round2_train_labels,
        {
            "round1_checkpoints": round1_checkpoints,
            "round1_calibrator": round1_calibrator,
        },
    )
    round2_calibrator = calibrate(
        2,
        round2_calibration_labels,
        round2_checkpoints,
    )
    return {
        "round1_calibrator": round1_calibrator,
        "round2_train_labels": round2_train_labels,
        "round2_calibration_labels": round2_calibration_labels,
        "round2_checkpoints": round2_checkpoints,
        "round2_calibrator": round2_calibrator,
    }


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--input-root", default=None)
    parser.add_argument("--round0-train-labels", default=None)
    parser.add_argument("--round0-calibration-labels", default=None)
    parser.add_argument("--round1-checkpoints", default=None)
    parser.add_argument("--round1-iteration-ensemble-size", type=int, default=3)
    parser.add_argument("--round1-iteration-coverage", type=float, default=0.90)
    parser.add_argument(
        "--round1-iteration-tolerance-scale",
        type=float,
        default=0.05,
    )
    parser.add_argument("--round1-iteration-horizon", type=int, default=3)
    parser.add_argument(
        "--round1-iteration-candidate-budget",
        type=int,
        default=50,
    )
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument(
        "--env-source",
        choices=("paper9", "neijiang"),
        default="paper9",
    )
    parser.add_argument(
        "--prepared-dir",
        default=str(Path(__file__).resolve().parents[3]),
    )
    parser.add_argument(
        "--reference-checkpoint",
        default=str(DEFAULT_REFERENCE_CHECKPOINT),
    )
    parser.add_argument("--reference-horizon", type=int, default=5)
    parser.add_argument("--reference-top-k", type=int, default=50)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--max-label-workers", type=int, default=4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
    )

    args = parse_args(argv)
    registry = load_registry(args.registry)
    if args.verify_only:
        if args.input_root is None:
            raise ValueError("--verify-only requires --input-root")
        report = verify_policy_iteration_root(args.input_root, registry=registry)
    else:
        report = execute_policy_iteration(args, registry=registry)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
