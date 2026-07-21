import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_v1_1_selected_labels import (
    load_resumable_selected_manifest,
)
from paper10_geojepa_mpc.models.pcc_paired_delta import HORIZONS
from paper10_geojepa_mpc.planning.selected_conformal import (
    load_selected_planning_calibrator,
)


_GATE_ORDER = (
    "trajectory_coverage",
    "minimum_nonfallback_rate",
    "minimum_action_difference_rate",
    "positive_reward_delta",
    "nonnegative_planning_delta",
    "positive_uncertainty_error_association",
    "zero_unexecuted_real_reward_queries",
    "minimum_supporting_model_seeds",
)


def _rankdata(values) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1)
        start = end
    return ranks


def _spearman(left, right) -> float:
    left_ranks = _rankdata(left)
    right_ranks = _rankdata(right)
    if (
        left_ranks.size < 2
        or left_ranks.std() == 0.0
        or right_ranks.std() == 0.0
    ):
        return 0.0
    return float(np.corrcoef(left_ranks, right_ranks)[0, 1])


def _validated_contract(contract) -> dict[str, float | int]:
    required = {
        "coverage",
        "minimum_nonfallback_rate",
        "minimum_action_difference_rate",
        "minimum_reward_delta",
        "minimum_planning_delta",
        "minimum_supporting_model_seeds",
    }
    if not isinstance(contract, dict) or not required <= set(contract):
        raise ValueError("viability contract fields mismatch")
    values = {
        "coverage": float(contract["coverage"]),
        "minimum_nonfallback_rate": float(
            contract["minimum_nonfallback_rate"]
        ),
        "minimum_action_difference_rate": float(
            contract["minimum_action_difference_rate"]
        ),
        "minimum_reward_delta": float(contract["minimum_reward_delta"]),
        "minimum_planning_delta": float(
            contract["minimum_planning_delta"]
        ),
        "minimum_supporting_model_seeds": int(
            contract["minimum_supporting_model_seeds"]
        ),
    }
    if (
        not 0.0 < values["coverage"] < 1.0
        or not 0.0 <= values["minimum_nonfallback_rate"] <= 1.0
        or not 0.0 <= values["minimum_action_difference_rate"] <= 1.0
        or values["minimum_supporting_model_seeds"] <= 0
        or not all(
            np.isfinite(value)
            for key, value in values.items()
            if key != "minimum_supporting_model_seeds"
        )
    ):
        raise ValueError("viability contract values are invalid")
    return values


def _validated_row(row) -> dict[str, object]:
    required = {
        "model_seed",
        "trajectory_seed",
        "certificate_passed",
        "action_differs",
        "reward_delta",
        "planning_delta",
        "covered",
        "uncertainty",
        "absolute_error",
        "fallback_reason",
        "base_selection_reason",
        "unexecuted_real_reward_queries",
    }
    if not isinstance(row, dict) or not required <= set(row):
        raise ValueError("viability row fields mismatch")
    planning = np.asarray(row["planning_delta"], dtype=np.float64).reshape(-1)
    numeric = np.asarray(
        [row["reward_delta"], row["uncertainty"], row["absolute_error"]],
        dtype=np.float64,
    )
    if (
        planning.shape != (3,)
        or not np.isfinite(planning).all()
        or not np.isfinite(numeric).all()
        or numeric[1] < 0.0
        or numeric[2] < 0.0
    ):
        raise ValueError("viability row values are invalid")
    queries = int(row["unexecuted_real_reward_queries"])
    if queries < 0:
        raise ValueError("viability query count cannot be negative")
    return {
        "model_seed": int(row["model_seed"]),
        "trajectory_seed": int(row["trajectory_seed"]),
        "certificate_passed": bool(row["certificate_passed"]),
        "action_differs": bool(row["action_differs"]),
        "reward_delta": float(numeric[0]),
        "planning_delta": planning,
        "covered": bool(row["covered"]),
        "uncertainty": float(numeric[1]),
        "absolute_error": float(numeric[2]),
        "fallback_reason": (
            None
            if row["fallback_reason"] is None
            else str(row["fallback_reason"])
        ),
        "base_selection_reason": str(row["base_selection_reason"]),
        "unexecuted_real_reward_queries": queries,
    }


def _seed_report(rows, *, contract) -> dict[str, object]:
    by_trajectory: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        by_trajectory.setdefault(int(row["trajectory_seed"]), []).append(row)
    if not by_trajectory:
        raise ValueError("model-seed viability block is empty")

    trajectory_covered = []
    nonfallback_rates = []
    action_difference_rates = []
    nonfallback_rewards = []
    executed_planning = []
    uncertainty = []
    absolute_error = []
    query_count = 0
    fallback_reasons = Counter()
    base_reasons = Counter()
    source_seeds = sorted(by_trajectory)
    for trajectory_seed in source_seeds:
        trajectory_rows = by_trajectory[trajectory_seed]
        passed = np.asarray(
            [row["certificate_passed"] for row in trajectory_rows],
            dtype=bool,
        )
        differs = np.asarray(
            [row["action_differs"] for row in trajectory_rows],
            dtype=bool,
        )
        reward = np.asarray(
            [row["reward_delta"] for row in trajectory_rows],
            dtype=np.float64,
        )
        planning = np.stack(
            [row["planning_delta"] for row in trajectory_rows]
        ).astype(np.float64)
        trajectory_covered.append(
            bool(all(row["covered"] for row in trajectory_rows))
        )
        nonfallback_rates.append(float(passed.mean()))
        action_difference_rates.append(float((passed & differs).mean()))
        if passed.any():
            nonfallback_rewards.append(float(reward[passed].mean()))
        executed_planning.append((planning * passed[:, None]).mean(axis=0))
        uncertainty.append(
            float(
                np.mean([row["uncertainty"] for row in trajectory_rows])
            )
        )
        absolute_error.append(
            float(
                np.mean([row["absolute_error"] for row in trajectory_rows])
            )
        )
        query_count += sum(
            int(row["unexecuted_real_reward_queries"])
            for row in trajectory_rows
        )
        for row in trajectory_rows:
            base_reasons[str(row["base_selection_reason"])] += 1
            if not row["certificate_passed"]:
                fallback_reasons[
                    str(row["fallback_reason"] or "unspecified_fallback")
                ] += 1

    covered_count = int(sum(trajectory_covered))
    n_trajectories = len(source_seeds)
    report = {
        "trajectory_coverage": float(covered_count / n_trajectories),
        "covered_trajectories": covered_count,
        "n_trajectories": n_trajectories,
        "nonfallback_rate": float(np.mean(nonfallback_rates)),
        "action_difference_rate": float(np.mean(action_difference_rates)),
        "mean_nonfallback_reward_delta": float(
            np.mean(nonfallback_rewards) if nonfallback_rewards else 0.0
        ),
        "mean_executed_planning_delta": np.mean(
            np.stack(executed_planning), axis=0
        ).astype(float).tolist(),
        "spearman_uncertainty_error": _spearman(
            uncertainty,
            absolute_error,
        ),
        "fallback_reasons": dict(sorted(fallback_reasons.items())),
        "base_selection_reasons": dict(sorted(base_reasons.items())),
        "unexecuted_real_reward_queries": int(query_count),
        "source_seeds": source_seeds,
    }
    planning_mean = np.asarray(
        report["mean_executed_planning_delta"], dtype=np.float64
    )
    report["gates"] = {
        "trajectory_coverage": bool(
            report["trajectory_coverage"] >= contract["coverage"]
        ),
        "minimum_nonfallback_rate": bool(
            report["nonfallback_rate"]
            >= contract["minimum_nonfallback_rate"]
        ),
        "minimum_action_difference_rate": bool(
            report["action_difference_rate"]
            >= contract["minimum_action_difference_rate"]
        ),
        "positive_reward_delta": bool(
            report["mean_nonfallback_reward_delta"]
            > contract["minimum_reward_delta"]
        ),
        "nonnegative_planning_delta": bool(
            np.all(planning_mean >= contract["minimum_planning_delta"])
        ),
        "positive_uncertainty_error_association": bool(
            report["spearman_uncertainty_error"] > 0.0
        ),
        "zero_unexecuted_real_reward_queries": query_count == 0,
    }
    report["supported"] = bool(all(report["gates"].values()))
    return report


def evaluate_viability(rows, *, contract) -> dict[str, object]:
    contract = _validated_contract(contract)
    rows = [_validated_row(row) for row in rows]
    if not rows:
        raise ValueError("viability rows must be non-empty")
    by_model_seed: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        by_model_seed.setdefault(int(row["model_seed"]), []).append(row)
    per_seed = {
        seed: _seed_report(seed_rows, contract=contract)
        for seed, seed_rows in sorted(by_model_seed.items())
    }
    supporting = [
        seed for seed, report in per_seed.items() if report["supported"]
    ]
    minimum_support = int(contract["minimum_supporting_model_seeds"])
    failed = []
    component_gates = _GATE_ORDER[:-1]
    for gate in component_gates:
        passing_count = sum(
            bool(report["gates"][gate]) for report in per_seed.values()
        )
        if passing_count < minimum_support:
            failed.append(gate)
    if len(supporting) < minimum_support:
        failed.append("minimum_supporting_model_seeds")
    failed = [gate for gate in _GATE_ORDER if gate in set(failed)]

    reports = list(per_seed.values())
    covered = sum(int(report["covered_trajectories"]) for report in reports)
    n_trajectories = sum(int(report["n_trajectories"]) for report in reports)
    fallback_reasons = Counter()
    base_selection_reasons = Counter()
    for report in reports:
        fallback_reasons.update(report["fallback_reasons"])
        base_selection_reasons.update(report["base_selection_reasons"])
    query_count = sum(
        int(report["unexecuted_real_reward_queries"]) for report in reports
    )
    if query_count != 0:
        failed.append("zero_unexecuted_real_reward_queries")
        failed = [gate for gate in _GATE_ORDER if gate in set(failed)]
    return {
        "passed": not failed,
        "contract": dict(contract),
        "coverage": float(contract["coverage"]),
        "trajectory_coverage": float(covered / n_trajectories),
        "covered_trajectories": int(covered),
        "n_trajectories": int(n_trajectories),
        "nonfallback_rate": float(
            np.mean([report["nonfallback_rate"] for report in reports])
        ),
        "action_difference_rate": float(
            np.mean([report["action_difference_rate"] for report in reports])
        ),
        "mean_nonfallback_reward_delta": float(
            np.mean(
                [report["mean_nonfallback_reward_delta"] for report in reports]
            )
        ),
        "mean_executed_planning_delta": np.mean(
            np.asarray(
                [report["mean_executed_planning_delta"] for report in reports],
                dtype=np.float64,
            ),
            axis=0,
        ).astype(float).tolist(),
        "spearman_uncertainty_error": float(
            np.mean(
                [report["spearman_uncertainty_error"] for report in reports]
            )
        ),
        "supporting_model_seeds": supporting,
        "per_model_seed": {str(seed): report for seed, report in per_seed.items()},
        "fallback_reasons": dict(sorted(fallback_reasons.items())),
        "base_selection_reasons": dict(
            sorted(base_selection_reasons.items())
        ),
        "unexecuted_real_reward_queries": int(query_count),
        "failed_gates": failed,
    }


def select_viable_coverage(reports, *, declared) -> float | None:
    declared = tuple(float(value) for value in declared)
    if not declared or tuple(sorted(set(declared))) != declared:
        raise ValueError("declared coverages must be sorted and unique")
    normalized = {float(key): value for key, value in reports.items()}
    if set(normalized) != set(declared):
        raise ValueError("coverage report inventory mismatch")
    for coverage, report in normalized.items():
        if float(report.get("coverage", float("nan"))) != coverage:
            raise ValueError("coverage report identity mismatch")
    passing = [
        coverage for coverage in declared if bool(normalized[coverage].get("passed"))
    ]
    return max(passing) if passing else None


def load_development_rows(
    selected_manifest: str | Path,
    calibrator_path: str | Path,
    *,
    expected_lineage: dict[str, object],
    expected_coverage: float,
    expected_planning_horizon: int,
    expected_trajectory_seeds: Sequence[int],
    planning_tolerances=(0.0, 0.0, 0.0),
) -> list[dict[str, object]]:
    manifest_path = Path(selected_manifest)
    manifest = load_resumable_selected_manifest(
        manifest_path,
        expected_lineage=expected_lineage,
    )
    expected_seeds = [int(value) for value in expected_trajectory_seeds]
    if manifest["trajectory_seeds"] != expected_seeds:
        raise ValueError("development selected-label trajectory seeds mismatch")
    if expected_lineage.get("partition") != "development":
        raise ValueError("viability requires development selected labels")

    calibrator = load_selected_planning_calibrator(calibrator_path)
    expected_planning_horizon = int(expected_planning_horizon)
    expected_coverage = float(expected_coverage)
    calibrator_lineage = {
        "model_seed": int(calibrator.model_seed),
        "ensemble_size": int(calibrator.ensemble_size),
        "policy_round": int(calibrator.policy_round),
        "compute_mode": str(calibrator.compute_mode),
        "checkpoint_digests": list(calibrator.checkpoint_digests),
        "candidate_generator_digest": str(calibrator.candidate_generator_digest),
        "base_selector_digest": str(calibrator.base_selector_digest),
    }
    expected_calibrator_lineage = {
        field: expected_lineage[field]
        for field in (
            "model_seed",
            "ensemble_size",
            "policy_round",
            "compute_mode",
            "checkpoint_digests",
            "candidate_generator_digest",
            "base_selector_digest",
        )
    }
    if calibrator_lineage != expected_calibrator_lineage:
        raise ValueError("development calibrator lineage mismatch")
    if (
        calibrator.coverage != expected_coverage
        or calibrator.planning_horizon != expected_planning_horizon
    ):
        raise ValueError("development calibrator coverage or horizon mismatch")
    if expected_planning_horizon not in HORIZONS:
        raise ValueError("development planning horizon is invalid")
    tolerances = np.asarray(planning_tolerances, dtype=np.float64).reshape(-1)
    if (
        tolerances.shape != (3,)
        or not np.isfinite(tolerances).all()
        or np.any(tolerances < 0.0)
    ):
        raise ValueError("development planning tolerances are invalid")

    horizon_index = HORIZONS.index(expected_planning_horizon)
    rows = []
    required_arrays = {
        "selected_actions",
        "reference_actions",
        "predicted_delta",
        "predicted_scale",
        "true_delta",
        "executable_probability",
        "base_selection_reason",
        "state_steps",
        "trajectory_ids",
        "continuation_seeds",
        "unexecuted_real_reward_queries",
    }
    for artifact in manifest["artifacts"]:
        artifact_path = manifest_path.parent / str(artifact["path"])
        with np.load(artifact_path, allow_pickle=False) as arrays:
            if not required_arrays <= set(arrays.files):
                raise ValueError("development selected-label artifact schema mismatch")
            selected = np.asarray(arrays["selected_actions"], dtype=np.int64)
            reference = np.asarray(arrays["reference_actions"], dtype=np.int64)
            predicted = np.asarray(arrays["predicted_delta"], dtype=np.float64)
            scale = np.asarray(arrays["predicted_scale"], dtype=np.float64)
            true = np.asarray(arrays["true_delta"], dtype=np.float64)
            probability = np.asarray(
                arrays["executable_probability"], dtype=np.float64
            )
            reasons = np.asarray(arrays["base_selection_reason"]).astype(str)
            state_steps = np.asarray(arrays["state_steps"], dtype=np.int64)
            trajectory_ids = np.asarray(
                arrays["trajectory_ids"], dtype=np.int64
            )
            queries = np.asarray(
                arrays["unexecuted_real_reward_queries"], dtype=np.int64
            )
        n_states = int(artifact["n_states"])
        vectors = (
            selected,
            reference,
            probability,
            reasons,
            state_steps,
            trajectory_ids,
            queries,
        )
        if (
            any(value.shape != (n_states,) for value in vectors)
            or predicted.shape != (n_states, len(HORIZONS), 4)
            or scale.shape != predicted.shape
            or true.shape != predicted.shape
            or not all(
                np.isfinite(value).all()
                for value in (predicted, scale, true, probability)
            )
            or np.any(scale < 0.0)
            or np.any((probability < 0.0) | (probability > 1.0))
            or np.any(queries < 0)
        ):
            raise ValueError("development selected-label arrays are invalid")
        if np.any(queries != 0):
            raise ValueError(
                "development labels contain an unexecuted real-reward query"
            )
        seed = int(artifact["trajectory_seed"])
        if not np.all(trajectory_ids == seed) or np.unique(state_steps).size != n_states:
            raise ValueError("development trajectory identity is invalid")

        for index in range(n_states):
            selected_action = int(selected[index])
            reference_action = int(reference[index])
            is_reference = selected_action == reference_action
            if is_reference and (
                np.any(predicted[index] != 0.0)
                or np.any(scale[index] != 0.0)
                or np.any(true[index] != 0.0)
            ):
                raise ValueError("reference-selected development delta is not zero")
            normalized = (
                predicted[index, horizon_index, 1:]
                - true[index, horizon_index, 1:]
            ) / np.maximum(scale[index, horizon_index, 1:], 1e-6)
            state_score = float(max(0.0, float(np.max(normalized))))
            lower = (
                predicted[index, horizon_index, 1:]
                - float(calibrator.q_planning)
                * scale[index, horizon_index, 1:]
            )
            certificate_passed = bool(
                not is_reference and np.all(lower >= -tolerances)
            )
            fallback_reason = None
            if not certificate_passed:
                fallback_reason = (
                    str(reasons[index])
                    if is_reference
                    else "planning_certificate_rejected"
                )
            planning_error = np.abs(
                predicted[index, horizon_index, 1:]
                - true[index, horizon_index, 1:]
            )
            rows.append(
                {
                    "model_seed": int(expected_lineage["model_seed"]),
                    "trajectory_seed": seed,
                    "state_step": int(state_steps[index]),
                    "selected_action": selected_action,
                    "reference_action": reference_action,
                    "certificate_passed": certificate_passed,
                    "action_differs": selected_action != reference_action,
                    "reward_delta": float(true[index, horizon_index, 0]),
                    "planning_delta": true[index, horizon_index, 1:].tolist(),
                    "covered": state_score <= float(calibrator.q_planning),
                    "uncertainty": float(
                        np.max(scale[index, horizon_index, 1:])
                    ),
                    "absolute_error": float(np.max(planning_error)),
                    "fallback_reason": fallback_reason,
                    "base_selection_reason": str(reasons[index]),
                    "unexecuted_real_reward_queries": int(queries[index]),
                    "selected_manifest_digest": str(
                        manifest["manifest_digest"]
                    ),
                    "calibration_manifest_digest": str(
                        calibrator.selected_labels_manifest_digest
                    ),
                }
            )
    return rows


def build_closeout_payload(
    *,
    registry_digest: str,
    reports,
    declared_coverages,
    input_digests,
) -> dict[str, object]:
    declared = tuple(float(value) for value in declared_coverages)
    selected = select_viable_coverage(reports, declared=declared)
    normalized_reports = {float(key): value for key, value in reports.items()}
    inputs = [dict(row) for row in input_digests]
    if not isinstance(registry_digest, str) or len(registry_digest) != 64:
        raise ValueError("closeout registry digest is invalid")
    if not inputs or any(
        not isinstance(row.get("sha256"), str)
        or len(str(row["sha256"])) != 64
        for row in inputs
    ):
        raise ValueError("closeout input digests are invalid")
    failed = sorted(
        {
            gate
            for report in normalized_reports.values()
            for gate in report.get("failed_gates", [])
        },
        key=lambda gate: _GATE_ORDER.index(gate),
    )
    return {
        "schema_version": 1,
        "protocol_id": "pcc_v1_1",
        "registry_digest": registry_digest,
        "status": "viable" if selected is not None else "scientific_failure",
        "passed": selected is not None,
        "selected_coverage": selected,
        "declared_coverages": list(declared),
        "coverage_selection": "highest_passing",
        "reports": {
            f"{coverage:.2f}": normalized_reports[coverage]
            for coverage in declared
        },
        "failed_gates": [] if selected is not None else failed,
        "input_digests": sorted(
            inputs,
            key=lambda row: (
                str(row.get("kind", "")),
                str(row.get("path", "")),
                str(row["sha256"]),
            ),
        ),
    }


def _gate_value(report, gate: str):
    contract = report["contract"]
    if gate == "trajectory_coverage":
        return report["trajectory_coverage"], report["coverage"]
    if gate == "minimum_nonfallback_rate":
        return (
            report["nonfallback_rate"],
            f">= {contract['minimum_nonfallback_rate']}",
        )
    if gate == "minimum_action_difference_rate":
        return (
            report["action_difference_rate"],
            f">= {contract['minimum_action_difference_rate']}",
        )
    if gate == "positive_reward_delta":
        return (
            report["mean_nonfallback_reward_delta"],
            f"> {contract['minimum_reward_delta']}",
        )
    if gate == "nonnegative_planning_delta":
        return (
            report["mean_executed_planning_delta"],
            f">= {contract['minimum_planning_delta']} each",
        )
    if gate == "positive_uncertainty_error_association":
        return report["spearman_uncertainty_error"], "> 0"
    if gate == "zero_unexecuted_real_reward_queries":
        return report["unexecuted_real_reward_queries"], "= 0"
    return (
        len(report["supporting_model_seeds"]),
        f">= {contract['minimum_supporting_model_seeds']}",
    )


def _closeout_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# PCC v1.1 Viability Closeout",
        "",
        f"- Status: `{payload['status']}`",
        f"- Passed: `{str(bool(payload['passed'])).lower()}`",
        f"- Selected coverage: `{payload['selected_coverage']}`",
        f"- Registry digest: `{payload['registry_digest']}`",
        "",
        "## Input Digests",
        "",
        "| kind | path | sha256 |",
        "|---|---|---|",
    ]
    for row in payload["input_digests"]:
        lines.append(
            f"| {row.get('kind', '')} | {row.get('path', '')} | `{row['sha256']}` |"
        )
    for coverage, report in payload["reports"].items():
        lines.extend(
            [
                "",
                f"## Coverage {coverage}",
                "",
                "| gate | observed | threshold | pass |",
                "|---|---:|---|---|",
            ]
        )
        failed = set(report["failed_gates"])
        for gate in _GATE_ORDER:
            observed, threshold = _gate_value(report, gate)
            lines.append(
                f"| {gate} | {observed} | {threshold} | "
                f"{'FAIL' if gate in failed else 'PASS'} |"
            )
        lines.extend(
            [
                "",
                "### Model Seeds",
                "",
                "| model seed | coverage | nonfallback | action difference | reward delta | planning delta | Spearman | supported | source seeds |",
                "|---:|---:|---:|---:|---:|---|---:|---|---|",
            ]
        )
        for model_seed, seed_report in report["per_model_seed"].items():
            lines.append(
                f"| {model_seed} | {seed_report['trajectory_coverage']} | "
                f"{seed_report['nonfallback_rate']} | "
                f"{seed_report['action_difference_rate']} | "
                f"{seed_report['mean_nonfallback_reward_delta']} | "
                f"{seed_report['mean_executed_planning_delta']} | "
                f"{seed_report['spearman_uncertainty_error']} | "
                f"{seed_report['supported']} | {seed_report['source_seeds']} |"
            )
        lines.extend(
            [
                "",
                "### Fallback Reasons",
                "",
                "| reason | count |",
                "|---|---:|",
            ]
        )
        for reason, count in report["fallback_reasons"].items():
            lines.append(f"| {reason} | {count} |")
        lines.extend(
            [
                "",
                "### Base Selection Reasons",
                "",
                "| reason | count |",
                "|---|---:|",
            ]
        )
        for reason, count in report["base_selection_reasons"].items():
            lines.append(f"| {reason} | {count} |")
    return "\n".join(lines) + "\n"


def write_viability_outputs(
    output_json: str | Path,
    output_md: str | Path,
    payload: dict[str, object],
) -> None:
    json_path = Path(output_json)
    markdown_path = Path(output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_temporary = json_path.with_suffix(".tmp.json")
    markdown_temporary = markdown_path.with_suffix(".tmp.md")
    json_temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    markdown_temporary.write_text(
        _closeout_markdown(payload),
        encoding="utf-8",
    )
    json_temporary.replace(json_path)
    markdown_temporary.replace(markdown_path)


def _sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _coverage_directory(coverage: float) -> str:
    return f"coverage_{float(coverage):.2f}"


def _load_coverage_inputs(
    *,
    registry,
    registry_digest: str,
    selected_development_root: str | Path,
    calibrator_root: str | Path,
    coverage: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    selected_root = Path(selected_development_root)
    calibrator_root = Path(calibrator_root)
    rows = []
    input_digests = []
    viability = registry["viability"]
    for raw_model_seed in registry["model_seeds"]:
        model_seed = int(raw_model_seed)
        family = f"model_seed_{model_seed}"
        manifest_path = selected_root / family / "manifest.json"
        calibrator_path = (
            calibrator_root
            / family
            / _coverage_directory(coverage)
            / "calibrator.json"
        )
        try:
            raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            raw_calibrator = json.loads(
                calibrator_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"viability input is missing or unreadable for model seed {model_seed}"
            ) from exc
        expected_lineage = {
            "protocol_id": "pcc_v1_1",
            "registry_digest": str(registry_digest),
            "partition": "development",
            "model_seed": model_seed,
            "ensemble_size": int(viability["ensemble_size"]),
            "policy_round": int(viability["policy_round"]),
            "compute_mode": "matched",
            "checkpoint_digests": raw_manifest.get("checkpoint_digests"),
            "candidate_generator_digest": raw_manifest.get(
                "candidate_generator_digest"
            ),
            "base_selector_digest": raw_manifest.get("base_selector_digest"),
            "reference_checkpoint_digest": registry[
                "offline_reference_policy"
            ]["checkpoint_sha256"],
        }
        rows.extend(
            load_development_rows(
                manifest_path,
                calibrator_path,
                expected_lineage=expected_lineage,
                expected_coverage=coverage,
                expected_planning_horizon=int(
                    registry["development_baseline_anchor"]["planning_horizon"]
                ),
                expected_trajectory_seeds=viability["development_seeds"],
            )
        )
        input_digests.extend(
            [
                {
                    "kind": "selected_development_manifest",
                    "model_seed": model_seed,
                    "path": str(manifest_path.resolve()),
                    "sha256": _sha256_file(manifest_path),
                    "manifest_digest": raw_manifest.get("manifest_digest"),
                },
                {
                    "kind": "selected_calibrator",
                    "model_seed": model_seed,
                    "coverage": float(coverage),
                    "path": str(calibrator_path.resolve()),
                    "sha256": _sha256_file(calibrator_path),
                    "calibrator_digest": raw_calibrator.get(
                        "calibrator_digest"
                    ),
                },
            ]
        )
        for artifact in raw_manifest.get("artifacts", []):
            artifact_path = manifest_path.parent / str(artifact["path"])
            observed = _sha256_file(artifact_path)
            if observed != str(artifact.get("sha256")):
                raise ValueError("viability selected-label artifact digest mismatch")
            input_digests.append(
                {
                    "kind": "selected_development_artifact",
                    "model_seed": model_seed,
                    "trajectory_seed": int(artifact["trajectory_seed"]),
                    "path": str(artifact_path.resolve()),
                    "sha256": observed,
                }
            )
    return rows, input_digests


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--selected-development-root", required=True)
    parser.add_argument("--calibrator-root", required=True)
    parser.add_argument("--coverages", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args(argv)


def _parse_coverages(spec: str) -> tuple[float, ...]:
    values = tuple(
        float(token.strip())
        for token in str(spec).split(",")
        if token.strip()
    )
    if not values or tuple(sorted(set(values))) != values:
        raise ValueError("coverages must be sorted and unique")
    return values


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        load_registry,
        validate_registry,
    )

    args = parse_args(argv)
    registry = load_registry(args.registry)
    validate_registry(registry)
    if registry.get("protocol_id") != "pcc_v1_1":
        raise ValueError("viability closeout requires the PCC v1.1 registry")
    coverages = _parse_coverages(args.coverages)
    declared = tuple(
        float(value) for value in registry["selected_conformal"]["coverages"]
    )
    if coverages != declared:
        raise ValueError("viability coverages must match the registry exactly")
    registry_digest = _sha256_file(args.registry)
    reports = {}
    inputs = [
        {
            "kind": "registry",
            "path": str(Path(args.registry).resolve()),
            "sha256": registry_digest,
        }
    ]
    for coverage in coverages:
        rows, coverage_inputs = _load_coverage_inputs(
            registry=registry,
            registry_digest=registry_digest,
            selected_development_root=args.selected_development_root,
            calibrator_root=args.calibrator_root,
            coverage=coverage,
        )
        contract = {
            **registry["viability"],
            "coverage": coverage,
        }
        reports[coverage] = evaluate_viability(rows, contract=contract)
        inputs.extend(coverage_inputs)
    unique_inputs = {
        (
            str(row.get("kind", "")),
            str(row.get("path", "")),
            str(row["sha256"]),
            str(row.get("coverage", "")),
        ): row
        for row in inputs
    }
    payload = build_closeout_payload(
        registry_digest=registry_digest,
        reports=reports,
        declared_coverages=coverages,
        input_digests=list(unique_inputs.values()),
    )
    write_viability_outputs(args.output_json, args.output_md, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


if __name__ == "__main__":
    main()
