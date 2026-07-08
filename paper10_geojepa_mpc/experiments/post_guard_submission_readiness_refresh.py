"""Source-derived post-guard submission-readiness refresh for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_POST_GUARD_CLOSURE_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
DEFAULT_POST_GUARD_CLOSURE_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
DEFAULT_SUBMISSION_BLOCKER_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
DEFAULT_DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
DEFAULT_SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
DEFAULT_FINAL_EXPORT_PACKAGE = (
    RESULTS / "e0_paper10_final_figure_table_export_package_2026-06-20.md"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md"
)


AUTHOR_DECISION_FIELDS = [
    {
        "field": "repository_doi_or_anonymous_reviewer_link",
        "label": "repository DOI or anonymous reviewer link",
        "required_input": (
            "Archive platform, persistent identifier or anonymous reviewer link, "
            "version, access timing, and anonymity status."
        ),
    },
    {
        "field": "code_licence",
        "label": "code licence",
        "required_input": (
            "Named software licence or institutional restriction covering only "
            "licensable code and scripts."
        ),
    },
    {
        "field": "generated_data_and_checkpoint_model_weight_rights",
        "label": "generated-data and checkpoint/model-weight rights",
        "required_input": (
            "Rights terms for generated JSON, Markdown, CSV, NPZ labels, "
            "checkpoints, model weights, and shareable source-data files."
        ),
    },
    {
        "field": "full_bishan_tool2_access_route",
        "label": "full Bishan Tool2 route",
        "required_input": (
            "Public DOI or controlled-access route for full transitions and "
            "pairwise files, including owner, eligibility, and reviewer route."
        ),
    },
    {
        "field": "gpkg_root_geospatial_input_access_route",
        "label": "GPKG-root geospatial route",
        "required_input": (
            "Public DOI or controlled-access route for GPKG-root geospatial "
            "inputs, block products, and township inputs."
        ),
    },
    {
        "field": "dongxing_neijiang_prepared_data_access_route",
        "label": "Dongxing/Neijiang prepared-data route",
        "required_input": (
            "Public DOI or controlled-access route for prepared external-region "
            "products, parcel assignments, environment files, and slope-enriched "
            "inputs."
        ),
    },
    {
        "field": "reviewer_data_access",
        "label": "reviewer data access",
        "required_input": (
            "Whether reviewers receive public downloads, private links, or "
            "controlled-access credentials."
        ),
    },
    {
        "field": "citation_policy",
        "label": "citation policy",
        "required_input": (
            "Acceptable source types, local-only source replacement route, "
            "preprint policy, and final reference style."
        ),
    },
    {
        "field": "statistical_reporting_policy",
        "label": "statistical reporting policy",
        "required_input": (
            "Descriptive-only reporting decision or defined tests, comparison "
            "groups, multiplicity handling, and precision policy."
        ),
    },
    {
        "field": "main_figure_1_and_journal_export_rules",
        "label": "Main Figure 1 / journal export rules",
        "required_input": (
            "Final schematic artwork and journal-specific figure/table count, "
            "source-data naming, and PDF/SVG/raster export rules."
        ),
    },
]


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _require_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _author_decision_fields() -> list[dict[str, Any]]:
    return [
        {
            **field,
            "status": "unresolved",
            "must_be_author_supplied": True,
            "closeout_required_before_submission": True,
        }
        for field in AUTHOR_DECISION_FIELDS
    ]


def build_post_guard_submission_readiness_refresh(
    *,
    post_guard_closure_json: str | Path = DEFAULT_POST_GUARD_CLOSURE_JSON,
    post_guard_closure_md: str | Path = DEFAULT_POST_GUARD_CLOSURE_MD,
    submission_blocker_packet: str | Path = DEFAULT_SUBMISSION_BLOCKER_PACKET,
    data_access_rights_register: str | Path = DEFAULT_DATA_ACCESS_RIGHTS_REGISTER,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    final_export_package: str | Path = DEFAULT_FINAL_EXPORT_PACKAGE,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    closure_json_path = Path(post_guard_closure_json)
    closure_md_path = Path(post_guard_closure_md)
    blocker_path = Path(submission_blocker_packet)
    rights_path = Path(data_access_rights_register)
    boundary_path = Path(submission_boundary_md)
    export_path = Path(final_export_package)

    closure = _load_json(closure_json_path)
    for path in (
        closure_md_path,
        blocker_path,
        rights_path,
        boundary_path,
        export_path,
    ):
        _require_text(path)

    guard = closure["primary_guard"]
    return {
        "date": output_date,
        "refresh_type": "post_guard_submission_readiness_refresh",
        "status": "not_submission_ready",
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "reran_training": False,
            "submission_approval": False,
            "source": (
                "tracked Paper10 post-guard closure and submission blocker "
                "artifacts only"
            ),
        },
        "source_files": {
            "post_guard_closure_json": closure_json_path.as_posix(),
            "post_guard_closure_md": closure_md_path.as_posix(),
            "submission_blocker_packet": blocker_path.as_posix(),
            "data_access_rights_register": rights_path.as_posix(),
            "submission_boundary_md": boundary_path.as_posix(),
            "final_export_package": export_path.as_posix(),
        },
        "algorithm_state": {
            "post_guard_bounded_algorithm_closure_current": True,
            "resume_broad_algorithm_redesign": False,
            "primary_guard": {
                "audit_set": guard["audit_set"],
                "switch_margin": float(guard["switch_margin"]),
                "n_seeds": int(guard["n_seeds"]),
                "mean_delta_vs_baseline": float(guard["mean_delta_vs_baseline"]),
            },
        },
        "submission_state": {
            "final_submission_blocked": True,
            "status_reason": "author decisions unresolved",
            "preflight_pass_does_not_mean_submission_ready": True,
        },
        "author_decision_fields": _author_decision_fields(),
        "claim_locks": {
            "final_submission_readiness_supported": False,
            "direct_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "deployment_ready_supported": False,
            "universal_fixed_margin_supported": False,
        },
    }


def post_guard_submission_readiness_refresh_markdown(payload: dict[str, Any]) -> str:
    guard = payload["algorithm_state"]["primary_guard"]
    lines = [
        "# Paper10 post-guard submission-readiness refresh",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: not_submission_ready",
        "",
        (
            "Status note: source-derived; no rollout or training rerun; "
            "no submission approval."
        ),
        "",
        "This refresh is not final submission readiness.",
        (
            "It records that post-guard bounded algorithm closure is current, "
            "while final submission remains blocked by unresolved author "
            "decisions."
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
            "## Algorithm state",
            "",
            (
                "The post-guard bounded algorithm closure is current under "
                f"`{guard['audit_set']} margin={guard['switch_margin']:.2f}`."
            ),
            f"- seeds: {guard['n_seeds']}",
            f"- mean delta vs baseline: {guard['mean_delta_vs_baseline']:.4f}",
            "- broad algorithm redesign: not resumed for the bounded route",
            "",
            "## Submission state",
            "",
            "The final submission remains blocked.",
            (
                "Passing repository preflight means the no-go boundary is "
                "tracked and guarded; it does not mean the paper is ready to "
                "submit."
            ),
            "",
            "## Author-decision intake",
            "",
            "| field | status | required author input |",
            "|---|---|---|",
        ]
    )
    for field in payload["author_decision_fields"]:
        lines.append(
            f"| {field['label']} | {field['status']} | "
            f"{field['required_input']} |"
        )
    lines.extend(
        [
            "",
            "## Claim locks",
            "",
            "Do not treat this refresh as final submission readiness.",
            "Do not claim direct 50-state Bishan scale-up success.",
            "Do not claim robust Bishan-to-Dongxing transfer superiority.",
            "Do not claim deployment-ready cadastral planning.",
            "Do not claim a universal fixed switch margin.",
            "",
        ]
    )
    return "\n".join(lines)


def write_post_guard_submission_readiness_refresh(
    *,
    post_guard_closure_json: str | Path = DEFAULT_POST_GUARD_CLOSURE_JSON,
    post_guard_closure_md: str | Path = DEFAULT_POST_GUARD_CLOSURE_MD,
    submission_blocker_packet: str | Path = DEFAULT_SUBMISSION_BLOCKER_PACKET,
    data_access_rights_register: str | Path = DEFAULT_DATA_ACCESS_RIGHTS_REGISTER,
    submission_boundary_md: str | Path = DEFAULT_SUBMISSION_BOUNDARY_MD,
    final_export_package: str | Path = DEFAULT_FINAL_EXPORT_PACKAGE,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-08",
) -> dict[str, Any]:
    payload = build_post_guard_submission_readiness_refresh(
        post_guard_closure_json=post_guard_closure_json,
        post_guard_closure_md=post_guard_closure_md,
        submission_blocker_packet=submission_blocker_packet,
        data_access_rights_register=data_access_rights_register,
        submission_boundary_md=submission_boundary_md,
        final_export_package=final_export_package,
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
        post_guard_submission_readiness_refresh_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 post-guard submission-readiness refresh."
    )
    parser.add_argument(
        "--post-guard-closure-json",
        default=str(DEFAULT_POST_GUARD_CLOSURE_JSON),
    )
    parser.add_argument(
        "--post-guard-closure-md",
        default=str(DEFAULT_POST_GUARD_CLOSURE_MD),
    )
    parser.add_argument(
        "--submission-blocker-packet",
        default=str(DEFAULT_SUBMISSION_BLOCKER_PACKET),
    )
    parser.add_argument(
        "--data-access-rights-register",
        default=str(DEFAULT_DATA_ACCESS_RIGHTS_REGISTER),
    )
    parser.add_argument(
        "--submission-boundary-md",
        default=str(DEFAULT_SUBMISSION_BOUNDARY_MD),
    )
    parser.add_argument(
        "--final-export-package",
        default=str(DEFAULT_FINAL_EXPORT_PACKAGE),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-08")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_post_guard_submission_readiness_refresh(
        post_guard_closure_json=args.post_guard_closure_json,
        post_guard_closure_md=args.post_guard_closure_md,
        submission_blocker_packet=args.submission_blocker_packet,
        data_access_rights_register=args.data_access_rights_register,
        submission_boundary_md=args.submission_boundary_md,
        final_export_package=args.final_export_package,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
