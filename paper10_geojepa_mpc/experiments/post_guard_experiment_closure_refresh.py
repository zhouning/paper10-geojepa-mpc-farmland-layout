"""Source-derived post-guard closure refresh for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_TRUE_REWARD_GUARD_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
DEFAULT_TRUE_REWARD_GUARD_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)
DEFAULT_TABLE_FREEZE_JSON = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)
DEFAULT_TABLE_FREEZE_MD = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"
)
DEFAULT_EXPERIMENT_FREEZE_MD = (
    RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md"
)
DEFAULT_CLOSURE_REGISTER_MD = (
    RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md"
)
DEFAULT_SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)


OPEN_SUBMISSION_BLOCKERS = [
    "repository DOI or anonymous reviewer link",
    "code licence",
    "generated-data rights and checkpoint or model-weight rights",
    "full Bishan Tool2 data access route",
    "GPKG-root geospatial input access route",
    "Dongxing/Neijiang prepared-data access route",
    "citation policy for local-only sources, preprints, and final reference style",
    "statistical reporting policy for descriptive results versus hypothesis tests",
    "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
]


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _require_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _guard_values(
    true_reward_guard: dict[str, Any],
    table_freeze: dict[str, Any],
) -> dict[str, Any]:
    primary = true_reward_guard["primary_guard"]
    stats = true_reward_guard["primary_paired_stats"]
    guard_stats = stats["candidate_guard_summary"]
    table_rows = table_freeze["tables"]["table_true_reward_guard_readiness"]
    table_row = table_rows[0]
    return {
        "audit_set": primary["audit_set"],
        "switch_margin": float(primary["switch_margin"]),
        "n_seeds": int(primary["n_seeds"]),
        "guard_mean_reward": float(primary["candidate_mean_reward"]),
        "baseline_mean_reward": float(primary["baseline_mean_reward"]),
        "mean_delta_vs_baseline": float(stats["mean_delta"]),
        "seed_wins": int(primary["seed_wins"]),
        "bootstrap_95ci_delta_lower": float(stats["bootstrap_95ci_delta"][0]),
        "mean_audit_action_count": float(guard_stats["mean_audit_action_count"]),
        "dual7x7_mean_audit_action_count": float(
            table_row["dual7x7_mean_audit_action_count"]
        ),
    }


def build_post_guard_experiment_closure_refresh(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    true_reward_guard_md: str | Path = DEFAULT_TRUE_REWARD_GUARD_MD,
    table_freeze_json: str | Path = DEFAULT_TABLE_FREEZE_JSON,
    table_freeze_md: str | Path = DEFAULT_TABLE_FREEZE_MD,
    experiment_freeze_md: str | Path = DEFAULT_EXPERIMENT_FREEZE_MD,
    closure_register_md: str | Path = DEFAULT_CLOSURE_REGISTER_MD,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    true_reward_guard_path = Path(true_reward_guard_json)
    true_reward_guard_md_path = Path(true_reward_guard_md)
    table_freeze_json_path = Path(table_freeze_json)
    table_freeze_md_path = Path(table_freeze_md)
    experiment_freeze_path = Path(experiment_freeze_md)
    closure_register_path = Path(closure_register_md)
    submission_boundary_path = Path(submission_boundary_md)

    true_reward_guard = _load_json(true_reward_guard_path)
    table_freeze = _load_json(table_freeze_json_path)
    for path in (
        true_reward_guard_md_path,
        table_freeze_md_path,
        experiment_freeze_path,
        closure_register_path,
        submission_boundary_path,
    ):
        _require_text(path)

    return {
        "date": output_date,
        "status": "post_guard_experiment_closure_refresh",
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "reran_training": False,
            "source": "tracked Paper10 guard and closure artifacts only",
        },
        "source_files": {
            "true_reward_guard_json": true_reward_guard_path.as_posix(),
            "true_reward_guard_md": true_reward_guard_md_path.as_posix(),
            "table_freeze_json": table_freeze_json_path.as_posix(),
            "table_freeze_md": table_freeze_md_path.as_posix(),
            "experiment_freeze_md": experiment_freeze_path.as_posix(),
            "closure_register_md": closure_register_path.as_posix(),
            "submission_boundary_md": submission_boundary_path.as_posix(),
        },
        "primary_guard": _guard_values(true_reward_guard, table_freeze),
        "closure_decision": {
            "default_next_phase": "bounded_manuscript_assembly",
            "resume_broad_algorithm_redesign": False,
            "historical_june_records_mutated": False,
        },
        "submission_boundary": {
            "status": "not_submission_ready",
            "open_blockers": OPEN_SUBMISSION_BLOCKERS,
        },
        "claim_locks": {
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_supported": False,
            "universal_fixed_margin_supported": False,
            "final_submission_readiness_supported": False,
        },
    }


def post_guard_experiment_closure_refresh_markdown(payload: dict[str, Any]) -> str:
    guard = payload["primary_guard"]
    lines = [
        "# Paper10 post-guard experiment-closure refresh",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: post_guard_experiment_closure_refresh",
        "",
        "Status note: source-derived; no rollout or training rerun.",
        "",
        "This refresh is a closure update, not a new experiment.",
        (
            "It records how the July 8 true-reward guard readiness evidence "
            "changes the bounded Paper10 experiment-closure reading without "
            "mutating historical June records."
        ),
        "",
        "## Source basis",
        "",
    ]
    for source in payload["source_files"].values():
        lines.append(f"- `{Path(source).name}`")
    lines.extend(
        [
            "",
            "## Current primary guard",
            "",
            (
                "The current primary true-reward guard is "
                "`rewardtop7 margin=1.50` for Bishan 20x16/top5."
            ),
            "",
            "| metric | value |",
            "|---|---:|",
            f"| baseline mean reward | {guard['baseline_mean_reward']:.4f} |",
            f"| guard mean reward | {guard['guard_mean_reward']:.4f} |",
            f"| mean delta vs baseline | {guard['mean_delta_vs_baseline']:.4f} |",
            f"| seed wins | {guard['seed_wins']} / {guard['n_seeds']} |",
            (
                "| bootstrap 95% CI lower | "
                f"{guard['bootstrap_95ci_delta_lower']:.4f} |"
            ),
            f"| mean audited actions | {guard['mean_audit_action_count']:.4f} |",
            (
                "| dual7x7 mean audited actions | "
                f"{guard['dual7x7_mean_audit_action_count']:.4f} |"
            ),
            "",
            "## Closure decision",
            "",
            "Default next phase: `bounded_manuscript_assembly`.",
            "",
            "Do not resume broad algorithm redesign for the bounded route.",
            (
                "Do not rewrite the June experiment-freeze audit or closure "
                "register as if those records originally included this July 8 "
                "guard."
            ),
            "",
            "## Submission boundary",
            "",
            (
                "Submission status remains `not_submission_ready`; this is not "
                "final submission readiness."
            ),
            "",
            "Open blockers remain:",
        ]
    )
    for blocker in payload["submission_boundary"]["open_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## Claim locks",
            "",
            "Do not claim a universal fixed switch margin.",
            "Do not claim direct 50-state Bishan scale-up success.",
            "Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "Do not claim deployment-ready cadastral planning.",
            "Do not treat this refresh as final submission readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def write_post_guard_experiment_closure_refresh(
    *,
    true_reward_guard_json: str | Path = DEFAULT_TRUE_REWARD_GUARD_JSON,
    true_reward_guard_md: str | Path = DEFAULT_TRUE_REWARD_GUARD_MD,
    table_freeze_json: str | Path = DEFAULT_TABLE_FREEZE_JSON,
    table_freeze_md: str | Path = DEFAULT_TABLE_FREEZE_MD,
    experiment_freeze_md: str | Path = DEFAULT_EXPERIMENT_FREEZE_MD,
    closure_register_md: str | Path = DEFAULT_CLOSURE_REGISTER_MD,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    payload = build_post_guard_experiment_closure_refresh(
        true_reward_guard_json=true_reward_guard_json,
        true_reward_guard_md=true_reward_guard_md,
        table_freeze_json=table_freeze_json,
        table_freeze_md=table_freeze_md,
        experiment_freeze_md=experiment_freeze_md,
        closure_register_md=closure_register_md,
        submission_boundary_md=submission_boundary_md,
        output_date=output_date,
    )
    output_json_path = Path(output_json)
    output_md_path = Path(output_md)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path.write_text(
        post_guard_experiment_closure_refresh_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 post-guard experiment-closure refresh."
    )
    parser.add_argument(
        "--true-reward-guard-json",
        default=str(DEFAULT_TRUE_REWARD_GUARD_JSON),
    )
    parser.add_argument(
        "--true-reward-guard-md",
        default=str(DEFAULT_TRUE_REWARD_GUARD_MD),
    )
    parser.add_argument("--table-freeze-json", default=str(DEFAULT_TABLE_FREEZE_JSON))
    parser.add_argument("--table-freeze-md", default=str(DEFAULT_TABLE_FREEZE_MD))
    parser.add_argument(
        "--experiment-freeze-md",
        default=str(DEFAULT_EXPERIMENT_FREEZE_MD),
    )
    parser.add_argument(
        "--closure-register-md",
        default=str(DEFAULT_CLOSURE_REGISTER_MD),
    )
    parser.add_argument(
        "--submission-boundary-md",
        default=str(DEFAULT_SUBMISSION_BOUNDARY_MD),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-08")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_post_guard_experiment_closure_refresh(
        true_reward_guard_json=args.true_reward_guard_json,
        true_reward_guard_md=args.true_reward_guard_md,
        table_freeze_json=args.table_freeze_json,
        table_freeze_md=args.table_freeze_md,
        experiment_freeze_md=args.experiment_freeze_md,
        closure_register_md=args.closure_register_md,
        submission_boundary_md=args.submission_boundary_md,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
