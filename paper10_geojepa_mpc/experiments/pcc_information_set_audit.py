import argparse
import json
from pathlib import Path
from typing import Sequence


def audit_information_set(
    payload: dict[str, object],
    *,
    expected_registry_digest: str,
) -> dict[str, object]:
    reasons = set()
    if payload.get("registry_digest") != str(expected_registry_digest):
        reasons.add("registry_digest_mismatch")
    query_count = 0
    n_steps = 0
    for seed_result in payload.get("seed_results", []):
        steps = seed_result.get("steps", [])
        n_steps += len(steps)
        if int(seed_result.get("environment_step_count", -1)) != len(steps):
            reasons.add("environment_step_count_mismatch")
        for step in steps:
            queries = int(step.get("unexecuted_real_reward_queries", -1))
            if queries != 0:
                reasons.add("unexecuted_real_reward_query")
            query_count += max(queries, 0)
    return {
        "passed": not reasons,
        "failure_reasons": sorted(reasons),
        "unexecuted_real_reward_queries": int(query_count),
        "audited_steps": int(n_steps),
    }


def _json_files(input_root: str | Path) -> list[Path]:
    root = Path(input_root)
    if root.is_file():
        return [root]
    if not root.is_dir():
        raise FileNotFoundError(f"audit input does not exist: {root}")
    return sorted(root.rglob("*.json"))


def audit_rollout_directory(
    input_root: str | Path,
    *,
    registry: dict[str, object],
) -> dict[str, object]:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import (
        validate_registry,
        verify_frozen_registry,
    )

    validate_registry(registry)
    registry_digest = verify_frozen_registry(registry)
    deployable = {str(value) for value in registry["deployable_baselines"]}
    diagnostics = {str(value) for value in registry["diagnostic_policies"]}
    if deployable & diagnostics:
        raise ValueError("deployable and diagnostic policy sets must be disjoint")

    reasons = set()
    seen = set()
    file_reports = []
    rollout_files = 0
    audited_seed_results = 0
    excluded_diagnostic_seed_results = 0
    audited_steps = 0
    query_count = 0

    for path in _json_files(input_root):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "seed_results" not in payload:
            continue
        rollout_files += 1
        rows = payload.get("seed_results")
        if not isinstance(rows, list) or not rows:
            reasons.add("empty_seed_results")
            file_reports.append(
                {
                    "path": path.as_posix(),
                    "passed": False,
                    "failure_reasons": ["empty_seed_results"],
                    "audited_seed_results": 0,
                    "audited_steps": 0,
                }
            )
            continue

        deployable_rows = []
        file_policies = set()
        for row in rows:
            policy = str(row.get("policy", ""))
            file_policies.add(policy)
            if policy in diagnostics:
                excluded_diagnostic_seed_results += 1
                continue
            if policy not in deployable:
                reasons.add("unknown_policy")
                continue
            try:
                identity = (
                    policy,
                    int(row["model_seed"]),
                    int(row["seed"]),
                )
            except (KeyError, TypeError, ValueError):
                reasons.add("invalid_policy_model_rollout_identity")
                continue
            if identity in seen:
                reasons.add("duplicate_policy_model_rollout_seed")
            seen.add(identity)
            deployable_rows.append(row)

        if not deployable_rows:
            continue
        deployable_payload = dict(payload)
        deployable_payload["seed_results"] = deployable_rows
        file_report = audit_information_set(
            deployable_payload,
            expected_registry_digest=registry_digest,
        )
        reasons.update(file_report["failure_reasons"])
        audited_seed_results += len(deployable_rows)
        audited_steps += int(file_report["audited_steps"])
        query_count += int(file_report["unexecuted_real_reward_queries"])
        file_reports.append(
            {
                "path": path.as_posix(),
                "policies": sorted(file_policies & deployable),
                "passed": bool(file_report["passed"]),
                "failure_reasons": list(file_report["failure_reasons"]),
                "audited_seed_results": len(deployable_rows),
                "audited_steps": int(file_report["audited_steps"]),
            }
        )

    if rollout_files == 0:
        reasons.add("no_rollout_artifacts")
    if audited_seed_results == 0:
        reasons.add("no_deployable_seed_results")
    return {
        "schema_version": 1,
        "protocol_id": registry["protocol_id"],
        "registry_digest": registry_digest,
        "input_root": Path(input_root).as_posix(),
        "passed": not reasons,
        "failure_reasons": sorted(reasons),
        "rollout_files": int(rollout_files),
        "audited_seed_results": int(audited_seed_results),
        "excluded_diagnostic_seed_results": int(
            excluded_diagnostic_seed_results
        ),
        "audited_steps": int(audited_steps),
        "unexecuted_real_reward_queries": int(query_count),
        "file_reports": file_reports,
    }


def _write_audit_outputs(
    report: dict[str, object],
    *,
    output_json: str | Path,
    output_md: str | Path,
) -> None:
    json_path = Path(output_json)
    markdown_path = Path(output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_json = json_path.with_suffix(".tmp.json")
    temporary_json.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary_json.replace(json_path)

    reasons = ", ".join(report["failure_reasons"]) or "none"
    markdown = [
        "# PCC information-set audit",
        "",
        f"- Registry digest: `{report['registry_digest']}`",
        f"- Overall pass: `{report['passed']}`",
        f"- Failure reasons: `{reasons}`",
        f"- Audited deployable seed results: {report['audited_seed_results']}",
        f"- Excluded diagnostic seed results: {report['excluded_diagnostic_seed_results']}",
        f"- Audited environment steps: {report['audited_steps']}",
        (
            "- Unexecuted real-reward queries: "
            f"{report['unexecuted_real_reward_queries']}"
        ),
        "",
        "| Artifact | Seed results | Steps | Pass |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in report["file_reports"]:
        markdown.append(
            f"| `{row['path']}` | {row['audited_seed_results']} | "
            f"{row['audited_steps']} | {row['passed']} |"
        )
    markdown.append("")
    temporary_markdown = markdown_path.with_suffix(".tmp.md")
    temporary_markdown.write_text("\n".join(markdown), encoding="utf-8")
    temporary_markdown.replace(markdown_path)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    from paper10_geojepa_mpc.experiments.pcc_protocol_registry import load_registry

    args = parse_args(argv)
    report = audit_rollout_directory(
        args.input_root,
        registry=load_registry(args.registry),
    )
    _write_audit_outputs(
        report,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
