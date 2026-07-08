import json
from pathlib import Path

from paper10_geojepa_mpc.experiments.post_guard_submission_readiness_refresh import (
    build_post_guard_submission_readiness_refresh,
    post_guard_submission_readiness_refresh_markdown,
    write_post_guard_submission_readiness_refresh,
)


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
POST_GUARD_CLOSURE_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
POST_GUARD_CLOSURE_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
SUBMISSION_BLOCKER_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
SUBMISSION_BOUNDARY_MD = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
FINAL_EXPORT_PACKAGE = (
    RESULTS / "e0_paper10_final_figure_table_export_package_2026-06-20.md"
)


EXPECTED_FIELDS = [
    "repository_doi_or_anonymous_reviewer_link",
    "code_licence",
    "generated_data_and_checkpoint_model_weight_rights",
    "full_bishan_tool2_access_route",
    "gpkg_root_geospatial_input_access_route",
    "dongxing_neijiang_prepared_data_access_route",
    "reviewer_data_access",
    "citation_policy",
    "statistical_reporting_policy",
    "main_figure_1_and_journal_export_rules",
]


def test_build_post_guard_submission_refresh_keeps_submission_blocked():
    payload = build_post_guard_submission_readiness_refresh(output_date="2026-07-08")

    assert payload["date"] == "2026-07-08"
    assert payload["refresh_type"] == "post_guard_submission_readiness_refresh"
    assert payload["status"] == "not_submission_ready"
    assert payload["source_boundary"] == {
        "new_experimental_claim": False,
        "reran_rollouts": False,
        "reran_training": False,
        "submission_approval": False,
        "source": (
            "tracked Paper10 post-guard closure and submission blocker "
            "artifacts only"
        ),
    }
    assert payload["source_files"]["post_guard_closure_json"].endswith(
        "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
    )
    assert payload["source_files"]["submission_boundary_md"].endswith(
        "e0_paper10_submission_readiness_boundary_2026-06-26.md"
    )

    algorithm = payload["algorithm_state"]
    assert algorithm["post_guard_bounded_algorithm_closure_current"] is True
    assert algorithm["resume_broad_algorithm_redesign"] is False
    assert algorithm["primary_guard"] == {
        "audit_set": "rewardtop7",
        "switch_margin": 1.5,
        "n_seeds": 20,
        "mean_delta_vs_baseline": 6.304141816329158,
    }

    submission = payload["submission_state"]
    assert submission == {
        "final_submission_blocked": True,
        "status_reason": "author decisions unresolved",
        "preflight_pass_does_not_mean_submission_ready": True,
    }

    fields = payload["author_decision_fields"]
    assert [field["field"] for field in fields] == EXPECTED_FIELDS
    for field in fields:
        assert field["status"] == "unresolved"
        assert field["must_be_author_supplied"] is True
        assert field["closeout_required_before_submission"] is True

    assert payload["claim_locks"] == {
        "final_submission_readiness_supported": False,
        "direct_50state_scaleup_supported": False,
        "robust_transfer_superiority_supported": False,
        "deployment_ready_supported": False,
        "universal_fixed_margin_supported": False,
    }


def test_post_guard_submission_refresh_markdown_reports_unresolved_author_fields():
    payload = build_post_guard_submission_readiness_refresh(output_date="2026-07-08")
    text = post_guard_submission_readiness_refresh_markdown(payload)

    for token in [
        "# Paper10 post-guard submission-readiness refresh",
        "Status: not_submission_ready",
        "source-derived; no rollout or training rerun; no submission approval",
        "post-guard bounded algorithm closure is current",
        "rewardtop7 margin=1.50",
        "final submission remains blocked",
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data and checkpoint/model-weight rights",
        "full Bishan Tool2 route",
        "GPKG-root geospatial route",
        "Dongxing/Neijiang prepared-data route",
        "reviewer data access",
        "citation policy",
        "statistical reporting policy",
        "Main Figure 1 / journal export rules",
        "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json",
        "e0_submission_blocker_decision_packet_2026-06-11.md",
        "e0_data_access_and_rights_decision_register_2026-06-09.md",
        "e0_paper10_submission_readiness_boundary_2026-06-26.md",
        "e0_paper10_final_figure_table_export_package_2026-06-20.md",
        "not final submission readiness",
        "Do not treat this refresh as final submission readiness.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not claim a universal fixed switch margin.",
    ]:
        assert token in text


def test_write_post_guard_submission_refresh_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "submission_refresh.json"
    output_md = tmp_path / "submission_refresh.md"

    payload = write_post_guard_submission_readiness_refresh(
        post_guard_closure_json=POST_GUARD_CLOSURE_JSON,
        post_guard_closure_md=POST_GUARD_CLOSURE_MD,
        submission_blocker_packet=SUBMISSION_BLOCKER_PACKET,
        data_access_rights_register=DATA_ACCESS_RIGHTS_REGISTER,
        submission_boundary_md=SUBMISSION_BOUNDARY_MD,
        final_export_package=FINAL_EXPORT_PACKAGE,
        output_json=output_json,
        output_md=output_md,
        output_date="2026-07-08",
    )

    assert json.loads(output_json.read_text(encoding="utf-8")) == payload
    assert output_md.read_text(encoding="utf-8") == (
        post_guard_submission_readiness_refresh_markdown(payload)
    )
