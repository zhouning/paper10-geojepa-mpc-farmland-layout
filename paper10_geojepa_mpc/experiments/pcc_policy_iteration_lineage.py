import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

ROUND1_LABEL_POLICY_CONFIG = {
    "ensemble_size": 3,
    "joint_coverage": 0.90,
    "tolerance_scale": 0.05,
    "planning_horizon": 3,
    "executed_feedback": False,
    "reference_policy": "paper9_mpc",
}


@dataclass(frozen=True)
class PolicyRound:
    round_index: int
    label_policy: str
    parent_digest: str | None

    def __post_init__(self):
        if self.round_index not in {0, 1, 2}:
            raise ValueError("PCC uses exactly two policy-improvement rounds")
        if self.round_index == 0 and self.parent_digest is not None:
            raise ValueError("round 0 cannot have a parent digest")
        if self.round_index > 0 and not self.parent_digest:
            raise ValueError("improvement rounds require a parent digest")


def build_policy_rounds(reference_policy: str) -> tuple[PolicyRound, ...]:
    return (
        PolicyRound(0, str(reference_policy), None),
        PolicyRound(1, "pcc_round1", "resolved_after_round0"),
        PolicyRound(2, "pcc_round2", "resolved_after_round1"),
    )


def _canonical(payload: dict[str, object]) -> bytes:
    clean = {key: value for key, value in payload.items() if key != "round_digest"}
    return json.dumps(
        clean,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _round_digest(payload: dict[str, object]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def write_round_manifest(
    path: str | Path,
    *,
    model_seed: int,
    round_index: int,
    parent_digest: str,
    train_labels_digest: str,
    calibration_labels_digest: str,
    checkpoint_digests: list[str],
    calibrator_digest: str,
    continuation_policy: dict[str, object],
) -> dict[str, object]:
    PolicyRound(
        round_index=int(round_index),
        label_policy=f"pcc_round{int(round_index)}",
        parent_digest=str(parent_digest),
    )
    if len(checkpoint_digests) == 0 or len(set(checkpoint_digests)) != len(
        checkpoint_digests
    ):
        raise ValueError("checkpoint digests must be non-empty and distinct")
    if not str(calibrator_digest):
        raise ValueError("calibrator digest is required")
    payload: dict[str, object] = {
        "schema_version": 1,
        "model_seed": int(model_seed),
        "round_index": int(round_index),
        "parent_digest": str(parent_digest),
        "train_labels_digest": str(train_labels_digest),
        "calibration_labels_digest": str(calibration_labels_digest),
        "checkpoint_digests": list(checkpoint_digests),
        "calibrator_digest": str(calibrator_digest),
        "continuation_policy": dict(continuation_policy),
    }
    payload["round_digest"] = _round_digest(payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def verify_round_manifest(payload: dict[str, object]) -> str:
    expected = payload.get("round_digest")
    observed = _round_digest(payload)
    if not isinstance(expected, str) or observed != expected:
        raise ValueError("policy round digest mismatch")
    PolicyRound(
        round_index=int(payload["round_index"]),
        label_policy=f"pcc_round{int(payload['round_index'])}",
        parent_digest=str(payload["parent_digest"]),
    )
    int(payload["model_seed"])
    if not str(payload.get("calibrator_digest", "")):
        raise ValueError("policy round calibrator digest is missing")
    return observed


def verify_policy_iteration_root(
    input_root: str | Path,
    *,
    registry: dict[str, object],
) -> dict[str, object]:
    from paper10_geojepa_mpc.experiments.pcc_experiment_inventory import (
        build_inventory,
    )
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        validate_registry,
        verify_frozen_registry,
    )

    validate_registry(registry)
    if registry.get("status") == "frozen":
        verify_frozen_registry(registry)
    root = Path(input_root)
    if not root.is_dir():
        raise FileNotFoundError(f"policy iteration root does not exist: {root}")
    if list(root.rglob("round3")) or list(root.rglob("*round3*.json")):
        raise ValueError("round 3 artifact is forbidden")
    expected_keys = {
        (int(ensemble_size), int(round_index))
        for ensemble_size in registry["grid"]["ensemble_size"]
        for round_index in registry["grid"]["policy_round"]
    }
    observed_by_seed = {
        int(model_seed): set() for model_seed in registry["model_seeds"]
    }
    required = {
        "round_digest",
        "round_index",
        "model_seed",
        "checkpoint_digests",
        "calibrator_digest",
    }
    for path in sorted(root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict) or not required.issubset(payload):
            continue
        verify_round_manifest(payload)
        model_seed = int(payload["model_seed"])
        if model_seed in observed_by_seed:
            observed_by_seed[model_seed].add(
                (len(payload["checkpoint_digests"]), int(payload["round_index"]))
            )
    if any(keys != expected_keys for keys in observed_by_seed.values()):
        raise ValueError("policy iteration factorial is incomplete")

    inventory = build_inventory(
        root,
        model_seeds=registry["model_seeds"],
        registry=registry,
        require_complete=True,
    )
    inventory_report = inventory.report()
    return {
        "passed": True,
        "protocol_id": registry["protocol_id"],
        "model_seeds": [int(value) for value in registry["model_seeds"]],
        "ensemble_sizes": [
            int(value) for value in registry["grid"]["ensemble_size"]
        ],
        "policy_rounds": [
            int(value) for value in registry["grid"]["policy_round"]
        ],
        "coverages": [
            float(value) for value in registry["grid"]["joint_coverage"]
        ],
        "n_records": len(inventory.records),
        "n_checkpoints": sum(
            len(record.checkpoint_paths) for record in inventory.records
        ),
        "n_calibrators": sum(
            len(record.calibrators) for record in inventory.records
        ),
        "records": inventory_report["records"],
    }
