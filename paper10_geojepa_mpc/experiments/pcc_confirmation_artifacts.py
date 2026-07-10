import csv
import json
from pathlib import Path

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


REFERENCE_CHECKPOINT_POLICIES = {
    "executable_random",
    "paper9_mpc",
    "legacy_value_filter",
    "model_reward_greedy",
    "rank_only",
}
MODEL_INDEPENDENT_POLICIES = REFERENCE_CHECKPOINT_POLICIES


def _json_files(source: str | Path) -> list[Path]:
    source = Path(source)
    if source.is_file():
        return [source]
    if not source.is_dir():
        raise FileNotFoundError(f"confirmation artifact path does not exist: {source}")
    return sorted(source.rglob("*.json"))


def _checkpoint_digest_tuple(payload, *, path: Path) -> tuple[str, ...]:
    digests = tuple(str(value) for value in payload.get("checkpoint_digests", []))
    if not digests or len(set(digests)) != len(digests):
        raise ValueError(f"checkpoint digests are missing or duplicated: {path}")
    if any(len(value) != 64 for value in digests):
        raise ValueError(f"checkpoint digest must be SHA-256: {path}")
    return digests


def load_confirmation_artifacts(
    source: str | Path,
    *,
    expected_registry_digest: str,
    allowed_policies,
    excluded_policies=(),
) -> dict[str, object]:
    allowed_policies = {str(value) for value in allowed_policies}
    excluded_policies = {str(value) for value in excluded_policies}
    if allowed_policies & excluded_policies:
        raise ValueError("allowed and excluded policy sets must be disjoint")
    outcomes: dict[str, dict[int, dict[int, np.ndarray]]] = {}
    checkpoint_digests: dict[str, dict[int, tuple[str, ...]]] = {}
    source_files = []
    information_audit_passed = True

    for path in _json_files(source):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "seed_results" not in payload:
            continue
        if payload.get("registry_digest") != str(expected_registry_digest):
            raise ValueError(f"registry digest mismatch: {path}")
        rows = payload.get("seed_results")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"rollout artifact has no seed results: {path}")
        digests = _checkpoint_digest_tuple(payload, path=path)
        file_included = False

        for row in rows:
            if row.get("registry_digest") != str(expected_registry_digest):
                raise ValueError(f"seed result registry digest mismatch: {path}")
            if tuple(map(str, row.get("checkpoint_digests", []))) != digests:
                raise ValueError(f"seed result checkpoint digest mismatch: {path}")
            policy = str(row.get("policy", ""))
            if policy in excluded_policies:
                continue
            if policy not in allowed_policies:
                raise ValueError(f"undeclared or diagnostic policy in confirmation: {policy}")
            file_included = True
            try:
                model_seed = int(row["model_seed"])
                rollout_seed = int(row["seed"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"invalid model or rollout seed: {path}") from error
            policy_digests = checkpoint_digests.setdefault(policy, {})
            existing_digests = policy_digests.setdefault(model_seed, digests)
            if existing_digests != digests:
                raise ValueError(
                    "inconsistent checkpoint digests for policy/model seed "
                    f"{policy}/{model_seed}"
                )
            objective = np.asarray(row.get("objective_outcome"), dtype=np.float64)
            if objective.shape != (len(OBJECTIVE_NAMES),) or not np.isfinite(
                objective
            ).all():
                raise ValueError(f"invalid objective outcome: {path}")
            seed_rows = outcomes.setdefault(policy, {}).setdefault(model_seed, {})
            if rollout_seed in seed_rows:
                raise ValueError(
                    "duplicate policy/model-seed/rollout-seed row: "
                    f"{policy}/{model_seed}/{rollout_seed}"
                )
            seed_rows[rollout_seed] = objective

            steps = row.get("steps", [])
            if int(row.get("environment_step_count", -1)) != len(steps):
                information_audit_passed = False
            for step in steps:
                if int(step.get("unexecuted_real_reward_queries", -1)) != 0:
                    information_audit_passed = False

        if file_included:
            source_files.append(path.as_posix())

    if not source_files:
        raise ValueError(f"no rollout JSON artifacts found under {source}")
    return {
        "outcomes": outcomes,
        "checkpoint_digests": checkpoint_digests,
        "source_files": source_files,
        "information_audit_passed": information_audit_passed,
    }


def complete_policy_block(
    artifacts: dict[str, object],
    *,
    policy: str,
    model_seeds,
    rollout_seeds,
    allow_shared_model_block: bool,
) -> np.ndarray:
    expected_models = tuple(map(int, model_seeds))
    expected_rollouts = tuple(map(int, rollout_seeds))
    policy_rows = artifacts["outcomes"].get(str(policy))
    if not policy_rows:
        raise ValueError(f"policy is missing from confirmation artifacts: {policy}")
    observed_models = set(map(int, policy_rows))
    if observed_models == set(expected_models):
        source_models = expected_models
    elif (
        allow_shared_model_block
        and len(observed_models) == 1
        and observed_models.issubset(set(expected_models))
    ):
        source_models = (next(iter(observed_models)),) * len(expected_models)
    else:
        raise ValueError(
            f"policy {policy} does not provide a complete model-seed block"
        )

    output = []
    expected_rollout_set = set(expected_rollouts)
    for source_model in source_models:
        rows = policy_rows[int(source_model)]
        if set(map(int, rows)) != expected_rollout_set:
            raise ValueError(
                f"policy {policy} does not provide a complete rollout-seed block"
            )
        output.append(np.stack([rows[seed] for seed in expected_rollouts], axis=0))
    return np.stack(output, axis=0)


def verify_model_dependent_checkpoints(
    artifacts: dict[str, object],
    *,
    policy: str,
    model_seeds,
    expected_flat_digests=None,
) -> dict[int, tuple[str, ...]]:
    expected_models = set(map(int, model_seeds))
    observed = artifacts["checkpoint_digests"].get(str(policy), {})
    if set(map(int, observed)) != expected_models:
        raise ValueError(f"checkpoint model-seed block is incomplete for policy {policy}")
    ordered = {seed: tuple(observed[seed]) for seed in map(int, model_seeds)}
    digest_blocks = list(ordered.values())
    if len(set(digest_blocks)) != len(digest_blocks):
        raise ValueError(f"checkpoint pseudoreplication detected for policy {policy}")
    flattened = [digest for block in digest_blocks for digest in block]
    if len(flattened) != len(set(flattened)):
        raise ValueError(f"checkpoint reused across training seeds for policy {policy}")
    if expected_flat_digests is not None and set(flattened) != set(
        map(str, expected_flat_digests)
    ):
        raise ValueError(f"frozen checkpoint digest mismatch for policy {policy}")
    return ordered


def verify_reference_policy_checkpoints(
    artifacts: dict[str, object],
    *,
    policy: str,
    expected_digests,
) -> None:
    observed = artifacts["checkpoint_digests"].get(str(policy), {})
    expected = tuple(map(str, expected_digests))
    if not observed or any(tuple(value) != expected for value in observed.values()):
        raise ValueError(f"frozen checkpoint digest mismatch for policy {policy}")


def seed_level_rows(
    *,
    region: str,
    policy: str,
    comparator: str,
    policy_block: np.ndarray,
    comparator_block: np.ndarray,
    model_seeds,
    rollout_seeds,
) -> list[dict[str, object]]:
    rows = []
    for model_index, model_seed in enumerate(model_seeds):
        for rollout_index, rollout_seed in enumerate(rollout_seeds):
            for objective_index, objective in enumerate(OBJECTIVE_NAMES):
                policy_value = float(
                    policy_block[model_index, rollout_index, objective_index]
                )
                comparator_value = float(
                    comparator_block[model_index, rollout_index, objective_index]
                )
                rows.append(
                    {
                        "region": str(region),
                        "policy": str(policy),
                        "comparator": str(comparator),
                        "model_seed": int(model_seed),
                        "rollout_seed": int(rollout_seed),
                        "objective": objective,
                        "policy_outcome": policy_value,
                        "comparator_outcome": comparator_value,
                        "paired_difference": policy_value - comparator_value,
                    }
                )
    return rows


def write_confirmation_outputs(
    output_prefix: str | Path,
    *,
    report: dict[str, object],
    seed_rows: list[dict[str, object]],
) -> None:
    prefix = Path(output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_suffix(".json")
    markdown_path = prefix.with_suffix(".md")
    csv_path = prefix.with_name(prefix.name + "_seed_level.csv")

    temporary_json = json_path.with_suffix(".tmp.json")
    temporary_json.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary_json.replace(json_path)

    locked = report["locked_confirmation"]

    def block_row(label, block, success):
        lower = block["lower_95_one_sided"]
        return (
            f"| {label} | {lower['reward']:.8g} | "
            f"{lower['slope_benefit']:.8g} | "
            f"{lower['contiguity_benefit']:.8g} | "
            f"{lower['connected_area_benefit']:.8g} | {success} |"
        )

    markdown = [
        "# PCC-GeoJEPA-MPC locked confirmation",
        "",
        f"- Registry digest: `{report['registry_digest']}`",
        f"- Primary policy: `{report['primary_policy']}`",
        f"- Primary comparator: `{report['primary_comparator']}`",
        f"- Information audit: `{locked['information_audit_passed']}`",
        f"- Overall success: `{locked['overall_success']}`",
        "",
        (
            "| Block | Reward lower bound | Slope lower bound | "
            "Contiguity lower bound | Connected-area lower bound | Success |"
        ),
        "| --- | ---: | ---: | ---: | ---: | --- |",
        block_row(
            "Bishan primary",
            locked["primary"],
            locked["primary"]["primary_success"],
        ),
        block_row(
            "Bishan matched compute",
            locked["matched_compute"],
            locked["matched_compute"]["primary_success"],
        ),
        block_row(
            "Dongxing external",
            locked["dongxing"],
            locked["dongxing"]["directional_success"],
        ),
        "",
    ]
    temporary_markdown = markdown_path.with_suffix(".tmp.md")
    temporary_markdown.write_text("\n".join(markdown), encoding="utf-8")
    temporary_markdown.replace(markdown_path)

    fieldnames = [
        "region",
        "policy",
        "comparator",
        "model_seed",
        "rollout_seed",
        "objective",
        "policy_outcome",
        "comparator_outcome",
        "paired_difference",
    ]
    temporary_csv = csv_path.with_suffix(".tmp.csv")
    with temporary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(seed_rows)
    temporary_csv.replace(csv_path)
