"""Preflight checks for the Paper10 submission/reviewer archive package."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"

README = Path("README.md")
REPRODUCIBILITY = Path("REPRODUCIBILITY.md")
MANIFEST = Path("MANIFEST.md")
DATA_AVAILABILITY = Path("DATA_AVAILABILITY.md")
ARCHIVE_MANIFEST = RESULTS / "e0_archive_manifest_2026-06-09.csv"
SELF_CONTAINED_MANUSCRIPT = (
    RESULTS
    / "e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md"
)
INTEGRATED_MANUSCRIPT = (
    RESULTS / "e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md"
)
DATA_CODE_AVAILABILITY = RESULTS / "e0_data_code_availability_draft_2026-06-09.md"
DATA_ACCESS_RIGHTS_REGISTER = (
    RESULTS / "e0_data_access_and_rights_decision_register_2026-06-09.md"
)
ARCHIVE_METADATA_TEMPLATES = (
    RESULTS / "e0_archive_metadata_templates_2026-06-09.md"
)
SMOKE_PROTOCOL = RESULTS / "e0_reviewer_smoke_replication_protocol_2026-06-09.md"
SMOKE_LOG = RESULTS / "e0_reviewer_smoke_verification_log_2026-06-10.md"
INTEGRATED_DONGXING_SCAFFOLD = (
    RESULTS / "e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md"
)
INTEGRATED_DONGXING_TABLES = (
    RESULTS / "e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md"
)
INTEGRATED_DONGXING_FIGURE_PLAN = (
    RESULTS / "e0_integrated_dongxing_figure_plan_2026-06-11.md"
)
INTEGRATED_DONGXING_SOURCE_DATA_MAP = (
    RESULTS / "e0_source_data_map_with_dongxing_2026-06-11.md"
)
INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE = (
    RESULTS / "e0_integrated_figure_table_numbering_freeze_2026-06-11.md"
)
SUBMISSION_BLOCKER_DECISION_PACKET = (
    RESULTS / "e0_submission_blocker_decision_packet_2026-06-11.md"
)
INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST = (
    RESULTS
    / "e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md"
)
INTEGRATED_CITATION_STATISTICS_POLICY = (
    RESULTS / "e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md"
)
CEUS_REVIEWER_IMPROVEMENT_PACKET = (
    RESULTS / "e0_ceus_reviewer_improvement_packet_2026-06-12.md"
)
CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_ceus_research_article_manuscript_draft_2026-06-12.md"
)
CEUS_STAGE3_MANUSCRIPT_REFRAME = (
    RESULTS / "e0_ceus_stage3_manuscript_reframe_2026-06-18.md"
)
CEUS_STAGE3_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_ceus_stage3_manuscript_draft_2026-06-18.md"
)
PROJECT_PROPOSAL_REPORT = (
    RESULTS / "e0_paper10_project_proposal_opening_report_2026-06-18.md"
)
AUTHOR_DECISION_MATRIX = (
    RESULTS / "e0_paper10_author_decision_matrix_2026-06-18.md"
)
FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT = (
    RESULTS / "e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md"
)
PAPER10_CLAIM_SOURCE_AUDIT_MD = (
    RESULTS / "e0_paper10_claim_source_consistency_audit_2026-06-18.md"
)
PAPER10_CLAIM_SOURCE_AUDIT_JSON = (
    RESULTS / "e0_paper10_claim_source_consistency_audit_2026-06-18.json"
)
PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD = (
    RESULTS / "e0_paper10_figure_table_source_coverage_audit_2026-06-19.md"
)
PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON = (
    RESULTS / "e0_paper10_figure_table_source_coverage_audit_2026-06-19.json"
)
PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD = (
    RESULTS / "e0_paper10_figure_table_caption_claim_packet_2026-06-19.md"
)
PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON = (
    RESULTS / "e0_paper10_figure_table_caption_claim_packet_2026-06-19.json"
)
PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE = (
    RESULTS / "e0_paper10_final_figure_table_export_package_2026-06-20.md"
)
PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD = (
    RESULTS / "e0_paper10_archive_source_data_closeout_2026-07-09.md"
)
PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON = (
    RESULTS / "e0_paper10_archive_source_data_closeout_2026-07-09.json"
)
PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD = (
    RESULTS / "e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md"
)
PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON = (
    RESULTS / "e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.json"
)
PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD = (
    RESULTS / "e0_paper10_ceus_submission_policy_verification_2026-07-09.md"
)
PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON = (
    RESULTS / "e0_paper10_ceus_submission_policy_verification_2026-07-09.json"
)
PAPER10_MAIN_FIGURE1_FINAL_ASSET_DIR = (
    RESULTS / "ceus_submission_assets" / "main_figure1_workflow"
)
PAPER10_MAIN_FIGURE1_FINAL_SVG = (
    PAPER10_MAIN_FIGURE1_FINAL_ASSET_DIR
    / "figure_1_monitor_gated_geojepa_mpc_workflow.svg"
)
PAPER10_MAIN_FIGURE1_FINAL_PDF = (
    PAPER10_MAIN_FIGURE1_FINAL_ASSET_DIR
    / "figure_1_monitor_gated_geojepa_mpc_workflow.pdf"
)
PAPER10_MAIN_FIGURE1_FINAL_PNG = (
    PAPER10_MAIN_FIGURE1_FINAL_ASSET_DIR
    / "figure_1_monitor_gated_geojepa_mpc_workflow.png"
)
PAPER10_SUBMISSION_READINESS_BOUNDARY = (
    RESULTS / "e0_paper10_submission_readiness_boundary_2026-06-26.md"
)
PAPER10_FORMAL_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_paper10_formal_manuscript_draft_2026-06-20.md"
)
PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT = (
    RESULTS / "e0_paper10_bounded_manuscript_assembly_draft_2026-06-27.md"
)
PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD = (
    RESULTS / "e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md"
)
PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON = (
    RESULTS / "e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.json"
)
PAPER10_MECHANISM_ABLATION_PACKET_MD = (
    RESULTS / "e0_paper10_mechanism_ablation_packet_2026-06-20.md"
)
PAPER10_MECHANISM_ABLATION_PACKET_JSON = (
    RESULTS / "e0_paper10_mechanism_ablation_packet_2026-06-20.json"
)
PAPER10_CEUS_MECHANISM_CLAIM_AUDIT_MD = (
    RESULTS / "e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md"
)
PAPER10_CEUS_MECHANISM_CLAIM_AUDIT_JSON = (
    RESULTS / "e0_paper10_ceus_mechanism_claim_audit_2026-06-27.json"
)
PAPER10_MONITOR_GATED_TOP5_JSON = (
    RESULTS / "e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json"
)
PAPER10_MONITOR_UNGATED_TOP4_JSON = (
    RESULTS / "e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top4.json"
)
PAPER10_MECHANISM_FULL_GATED_MASKED_JSON = (
    RESULTS / "e0_mechanism_full_gated_masked_20x16_top5_2026-06-20.json"
)
PAPER10_MECHANISM_HEURISTIC_PAPER9_MASKED_JSON = (
    RESULTS / "e0_mechanism_heuristic_paper9_masked_2026-06-20.json"
)
PAPER10_MECHANISM_NO_MASK_JSON = (
    RESULTS / "e0_mechanism_no_mask_20x16_top5_2026-06-20.json"
)
PAPER10_MECHANISM_UNGATED_TOP4_ROLLOUT_JSON = (
    RESULTS / "e0_mechanism_ungated_top4_20x16_h5_seed44_2026-06-20.json"
)
PAPER10_MECHANISM_UNGATED_TOP4_TRAIN_JSON = (
    RESULTS / "e0_mechanism_ungated_top4_train_20x16_h5_seed44_2026-06-20.json"
)
PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD = (
    RESULTS / "e0_paper10_real_data_availability_audit_2026-06-18.md"
)
PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON = (
    RESULTS / "e0_paper10_real_data_availability_audit_2026-06-18.json"
)
PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD = (
    RESULTS / "e0_paper10_real_data_integrity_smoke_2026-06-18.md"
)
PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON = (
    RESULTS / "e0_paper10_real_data_integrity_smoke_2026-06-18.json"
)
PAPER10_REAL_ENV_SMOKE_MD = (
    RESULTS / "e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.md"
)
PAPER10_REAL_ENV_SMOKE_JSON = (
    RESULTS / "e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.json"
)
PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD = (
    RESULTS
    / "e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.md"
)
PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON = (
    RESULTS
    / "e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.json"
)
PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD = (
    RESULTS / "e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md"
)
PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON = (
    RESULTS / "e0_paper10_real_env_smoke_boundary_audit_2026-06-19.json"
)
PAPER10_CEUS_REALDATA_LONGHORIZON_PROTOCOL = (
    RESULTS / "e0_paper10_ceus_realdata_longhorizon_protocol_2026-06-27.md"
)
PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER = (
    RESULTS / "e0_paper10_ceus_review_optimization_register_2026-06-27.md"
)
PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD = (
    RESULTS / "e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.md"
)
PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON = (
    RESULTS / "e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.json"
)
PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD = (
    RESULTS / "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md"
)
PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON = (
    RESULTS / "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
)
PAPER10_CEUS_BASELINE_HARDENING_MD = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md"
)
PAPER10_CEUS_BASELINE_HARDENING_JSON = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json"
)
PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD = (
    RESULTS / "e0_paper10_ceus_review_response_experiment_package_2026-07-09.md"
)
PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON = (
    RESULTS / "e0_paper10_ceus_review_response_experiment_package_2026-07-09.json"
)
PAPER10_GUARD_INFORMATION_SET_AUDIT_MD = (
    RESULTS / "e0_paper10_guard_information_set_audit_2026-07-09.md"
)
PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON = (
    RESULTS / "e0_paper10_guard_information_set_audit_2026-07-09.json"
)
PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_MD = (
    RESULTS / "e0_paper10_proxy_guard_dynamic_baseline_audit_2026-07-09.md"
)
PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON = (
    RESULTS / "e0_paper10_proxy_guard_dynamic_baseline_audit_2026-07-09.json"
)
PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH = (
    RESULTS / "e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md"
)
PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_ASSEMBLY_DRAFT = (
    RESULTS / "e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md"
)
PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT = (
    RESULTS / "e0_paper10_ceus_clean_main_manuscript_draft_2026-07-06.md"
)
PAPER10_CEUS_HIGHLIGHTS = (
    RESULTS / "e0_paper10_ceus_highlights_2026-07-06.txt"
)
PAPER10_TRUE_REWARD_GUARD_READINESS_MD = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.md"
)
PAPER10_TRUE_REWARD_GUARD_READINESS_JSON = (
    RESULTS / "e0_paper10_true_reward_guard_readiness_2026-07-08.json"
)
PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md"
)
PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON = (
    RESULTS / "e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json"
)
PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD = (
    RESULTS / "e0_paper10_author_decision_closeout_form_2026-07-08.md"
)
PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON = (
    RESULTS / "e0_paper10_author_decision_closeout_form_2026-07-08.json"
)
PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md"
)
PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON = (
    RESULTS / "e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json"
)
PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD = (
    RESULTS / "e0_paper10_public_release_rights_gate_2026-07-09.md"
)
PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON = (
    RESULTS / "e0_paper10_public_release_rights_gate_2026-07-09.json"
)
PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD = (
    RESULTS / "e0_paper10_dltb_leakage_evidence_audit_2026-07-09.md"
)
PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON = (
    RESULTS / "e0_paper10_dltb_leakage_evidence_audit_2026-07-09.json"
)
PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD = (
    RESULTS / "e0_paper10_ceus_confidential_dltb_acceptance_packet_2026-07-09.md"
)
PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON = (
    RESULTS / "e0_paper10_ceus_confidential_dltb_acceptance_packet_2026-07-09.json"
)
PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD = (
    RESULTS / "e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md"
)
PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON = (
    RESULTS / "e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json"
)
PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.md"
)
PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON = (
    RESULTS / "e0_paper10_manuscript_result_tables_freeze_2026-06-19.json"
)
PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD = (
    RESULTS / "e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md"
)
PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON = (
    RESULTS / "e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.json"
)
DONGXING_PLOT_SCRIPT = Path("scripts") / "paper10" / "plot_integrated_dongxing_figures.py"
ORIGINAL_VISION_DESIGN = (
    Path("docs")
    / "superpowers"
    / "specs"
    / "2026-06-17-paper10-original-vision-validation-design.md"
)
ORIGINAL_VISION_REGISTRY = (
    RESULTS / "e0_original_vision_validation_registry_2026-06-17.md"
)
ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET = (
    RESULTS / "e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md"
)
ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD = (
    RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md"
)
ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON = (
    RESULTS / "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json"
)

REQUIRED_PATHS = (
    Path("LICENSE"),
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    Path("DATA_AVAILABILITY.md"),
    Path("requirements.txt"),
    Path("county_env.py"),
    Path("paper10_geojepa_mpc"),
    Path("arcgis_toolbox_paper9") / "private_source",
    Path("arcgis_toolbox_paper9")
    / "_scratch"
    / "tool1_smoke"
    / "prepared"
    / "tool2"
    / "transitions.npz",
    Path("arcgis_toolbox_paper9")
    / "_scratch"
    / "tool1_smoke"
    / "prepared"
    / "tool2"
    / "pairwise.npz",
    ARCHIVE_MANIFEST,
    DATA_CODE_AVAILABILITY,
    DATA_ACCESS_RIGHTS_REGISTER,
    ARCHIVE_METADATA_TEMPLATES,
    SELF_CONTAINED_MANUSCRIPT,
    SMOKE_PROTOCOL,
    SMOKE_LOG,
    INTEGRATED_DONGXING_SCAFFOLD,
    INTEGRATED_DONGXING_TABLES,
    INTEGRATED_DONGXING_FIGURE_PLAN,
    INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    SUBMISSION_BLOCKER_DECISION_PACKET,
    INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
    INTEGRATED_CITATION_STATISTICS_POLICY,
    CEUS_REVIEWER_IMPROVEMENT_PACKET,
    CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    CEUS_STAGE3_MANUSCRIPT_REFRAME,
    CEUS_STAGE3_MANUSCRIPT_DRAFT,
    PROJECT_PROPOSAL_REPORT,
    AUTHOR_DECISION_MATRIX,
    FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    PAPER10_FORMAL_MANUSCRIPT_DRAFT,
    PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT,
    PAPER10_CLAIM_SOURCE_AUDIT_MD,
    PAPER10_CLAIM_SOURCE_AUDIT_JSON,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON,
    PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD,
    PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON,
    PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD,
    PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON,
    PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD,
    PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON,
    PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD,
    PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON,
    PAPER10_MAIN_FIGURE1_FINAL_SVG,
    PAPER10_MAIN_FIGURE1_FINAL_PDF,
    PAPER10_MAIN_FIGURE1_FINAL_PNG,
    PAPER10_SUBMISSION_READINESS_BOUNDARY,
    PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD,
    PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON,
    PAPER10_MECHANISM_ABLATION_PACKET_MD,
    PAPER10_MECHANISM_ABLATION_PACKET_JSON,
    PAPER10_CEUS_MECHANISM_CLAIM_AUDIT_MD,
    PAPER10_CEUS_MECHANISM_CLAIM_AUDIT_JSON,
    PAPER10_MONITOR_GATED_TOP5_JSON,
    PAPER10_MONITOR_UNGATED_TOP4_JSON,
    PAPER10_MECHANISM_FULL_GATED_MASKED_JSON,
    PAPER10_MECHANISM_HEURISTIC_PAPER9_MASKED_JSON,
    PAPER10_MECHANISM_NO_MASK_JSON,
    PAPER10_MECHANISM_UNGATED_TOP4_ROLLOUT_JSON,
    PAPER10_MECHANISM_UNGATED_TOP4_TRAIN_JSON,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON,
    PAPER10_REAL_ENV_SMOKE_MD,
    PAPER10_REAL_ENV_SMOKE_JSON,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON,
    PAPER10_CEUS_REALDATA_LONGHORIZON_PROTOCOL,
    PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
    PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD,
    PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON,
    PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD,
    PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON,
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENING_JSON,
    PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD,
    PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_ASSEMBLY_DRAFT,
    PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
    PAPER10_CEUS_HIGHLIGHTS,
    PAPER10_TRUE_REWARD_GUARD_READINESS_MD,
    PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
    PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
    PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD,
    PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
    PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
    PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD,
    PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON,
    PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD,
    PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON,
    PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD,
    PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON,
    DONGXING_PLOT_SCRIPT,
    ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
    ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
    Path("references") / "paper10_verified_references_2026-06-09.bib",
    Path("references") / "paper10_local_sources_2026-06-09.bib",
    Path("references") / "paper10_citation_map_2026-06-09.md",
)

FORBIDDEN_50_STATE_PATTERNS = (
    r"generally scales to 50 states",
    r"scales to 50 states",
    r"50-state success",
    r"successful 50-state",
    r"successful scale-up evidence",
    r"successful scale-up",
)

PUBLIC_PLACEHOLDER_PATTERN = re.compile(
    r"\[[A-Z0-9 /_-]+(?:TO BE ADDED|TO BE ASSIGNED|TO BE SELECTED|IF AVAILABLE)\]"
)

PUBLIC_SUBMISSION_DOCS = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    Path("DATA_AVAILABILITY.md"),
    INTEGRATED_MANUSCRIPT,
    SELF_CONTAINED_MANUSCRIPT,
    CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    CEUS_STAGE3_MANUSCRIPT_REFRAME,
    CEUS_STAGE3_MANUSCRIPT_DRAFT,
    PROJECT_PROPOSAL_REPORT,
    AUTHOR_DECISION_MATRIX,
    FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    PAPER10_FORMAL_MANUSCRIPT_DRAFT,
    PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT,
    PAPER10_CLAIM_SOURCE_AUDIT_MD,
    PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
    PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD,
    PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD,
    PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON,
    PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD,
    PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON,
    PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD,
    PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON,
    PAPER10_SUBMISSION_READINESS_BOUNDARY,
    PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
    PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
    PAPER10_REAL_ENV_SMOKE_MD,
    PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
    PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD,
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_ASSEMBLY_DRAFT,
    PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
    PAPER10_CEUS_HIGHLIGHTS,
    PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD,
    PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
    PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD,
    PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD,
    PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD,
)

PUBLIC_VAGUE_DATA_ROUTE_PATTERN = re.compile(
    r"available upon(?: reasonable)? request"
    r"|temporary cloud"
    r"|personal web(?:site| link)"
    r"|drive link"
    r"|cloud link",
    re.IGNORECASE,
)

UNSUPPORTED_INFERENTIAL_STATS_PATTERN = re.compile(
    r"statistically significant"
    r"|significant at"
    r"|\bp\s*[<=>]\s*\d"
    r"|p-value"
    r"|p value"
    r"|confidence interval"
    r"|formal superiority"
    r"|non[- ]inferiority"
    r"|equivalence test",
    re.IGNORECASE,
)

ARCHIVE_REQUIRED_FIELDS = (
    "record_id",
    "path_or_pattern",
    "access_route",
    "archive_action",
    "status",
)

INCLUDED_ARCHIVE_ACTIONS = {"include", "include_after_rights_check"}
EXCLUDED_ARCHIVE_ACTIONS = {"exclude", "exclude_unless_selected", "exclude_from_git"}
ALLOWED_TRACKED_EXCLUDED_PATHS = {
    "tool2/README.md",
    "dem_slope_analysis/output/README.md",
    "results_real/blocks/README.md",
}

SMOKE_LINK_DOCS = (
    Path("README.md"),
    Path("REPRODUCIBILITY.md"),
    Path("MANIFEST.md"),
    RESULTS / "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
    RESULTS / "e0_submission_readiness_checklist_2026-06-09.md",
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def nested_value(payload: dict, keys: tuple[str, ...]):
    value = payload
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def iter_markdown_files(root: Path) -> list[Path]:
    targets = [
        root / "README.md",
        root / "MANIFEST.md",
        root / "DATA_AVAILABILITY.md",
        root / "REPRODUCIBILITY.md",
    ]
    result_dir = root / RESULTS
    if result_dir.exists():
        targets.extend(sorted(result_dir.glob("*.md")))
    return [path for path in targets if path.exists()]


def check_required_paths_exist(root: Path) -> CheckResult:
    missing = [str(path) for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        return CheckResult(
            "required_paths_exist",
            False,
            "missing required paths: " + ", ".join(missing),
        )
    return CheckResult(
        "required_paths_exist",
        True,
        f"{len(REQUIRED_PATHS)} required paths found",
    )


def check_archive_manifest_required_fields(root: Path) -> CheckResult:
    path = root / ARCHIVE_MANIFEST
    if not path.exists():
        return CheckResult(
            "archive_manifest_required_fields",
            False,
            f"missing archive manifest: {ARCHIVE_MANIFEST}",
        )

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    missing_rows = []
    for index, row in enumerate(rows, start=2):
        missing_fields = [field for field in ARCHIVE_REQUIRED_FIELDS if not row.get(field)]
        if missing_fields:
            missing_rows.append(f"line {index}: {','.join(missing_fields)}")

    if missing_rows:
        return CheckResult(
            "archive_manifest_required_fields",
            False,
            "; ".join(missing_rows),
        )
    return CheckResult(
        "archive_manifest_required_fields",
        True,
        f"{len(rows)} rows contain required fields",
    )


def read_archive_manifest_rows(root: Path) -> tuple[list[dict[str, str]], str | None]:
    path = root / ARCHIVE_MANIFEST
    if not path.exists():
        return [], f"missing archive manifest: {ARCHIVE_MANIFEST}"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle)), None


def normalize_manifest_pattern(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def has_glob(pattern: str) -> bool:
    return any(char in pattern for char in "*?[")


def manifest_path_matches(root: Path, pattern: str) -> list[Path]:
    normalized = normalize_manifest_pattern(pattern)
    if not normalized:
        return []
    if has_glob(normalized):
        return [path for path in root.glob(normalized) if path.exists()]
    candidate = root / normalized.rstrip("/")
    return [candidate] if candidate.exists() else []


def check_archive_manifest_included_paths_resolve(root: Path) -> CheckResult:
    rows, error = read_archive_manifest_rows(root)
    if error:
        return CheckResult("archive_manifest_included_paths_resolve", False, error)

    missing = []
    checked = 0
    for index, row in enumerate(rows, start=2):
        if row.get("record_id") != "record1_code_evidence":
            continue
        if row.get("archive_action") not in INCLUDED_ARCHIVE_ACTIONS:
            continue

        checked += 1
        pattern = row.get("path_or_pattern", "")
        if not manifest_path_matches(root, pattern):
            missing.append(f"line {index}: {pattern}")

    if missing:
        return CheckResult(
            "archive_manifest_included_paths_resolve",
            False,
            "included paths do not resolve: " + "; ".join(missing),
        )
    return CheckResult(
        "archive_manifest_included_paths_resolve",
        True,
        f"{checked} Record 1 include/include_after_rights_check paths resolve",
    )


def git_tracked_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [
        line.strip().replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def tracked_file_matches_pattern(tracked_path: str, pattern: str) -> bool:
    normalized = normalize_manifest_pattern(pattern)
    if not normalized:
        return False
    if has_glob(normalized):
        return PurePosixPath(tracked_path).match(normalized)
    prefix = normalized.rstrip("/")
    return tracked_path == prefix or tracked_path.startswith(prefix + "/")


def check_excluded_paths_not_tracked(root: Path) -> CheckResult:
    rows, error = read_archive_manifest_rows(root)
    if error:
        return CheckResult("excluded_paths_not_tracked", False, error)

    tracked = git_tracked_files(root)
    violations = []
    checked = 0
    for index, row in enumerate(rows, start=2):
        if row.get("record_id") != "excluded_or_local":
            continue
        if row.get("archive_action") not in EXCLUDED_ARCHIVE_ACTIONS:
            continue

        checked += 1
        pattern = row.get("path_or_pattern", "")
        for tracked_path in tracked:
            if tracked_path in ALLOWED_TRACKED_EXCLUDED_PATHS:
                continue
            if tracked_file_matches_pattern(tracked_path, pattern):
                violations.append(f"line {index}: {tracked_path}")

    if violations:
        return CheckResult(
            "excluded_paths_not_tracked",
            False,
            "excluded/local paths tracked by Git: " + "; ".join(violations),
        )
    return CheckResult(
        "excluded_paths_not_tracked",
        True,
        f"{checked} excluded/local manifest patterns have no tracked payload files",
    )


def check_public_submission_placeholders_absent(root: Path) -> CheckResult:
    hits = []
    checked = 0
    for rel_path in PUBLIC_SUBMISSION_DOCS:
        path = root / rel_path
        if not path.exists():
            continue

        checked += 1
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            for match in PUBLIC_PLACEHOLDER_PATTERN.finditer(line):
                hits.append(f"{rel_path}:{line_no}: {match.group(0)}")

    if hits:
        return CheckResult(
            "public_submission_placeholders_absent",
            False,
            "public-facing placeholder tokens found: " + " | ".join(hits),
        )
    return CheckResult(
        "public_submission_placeholders_absent",
        True,
        f"{checked} public-facing docs contain no unresolved bracket placeholders",
    )


def check_public_data_route_wording_specific(root: Path) -> CheckResult:
    hits = []
    checked = 0
    for rel_path in PUBLIC_SUBMISSION_DOCS:
        path = root / rel_path
        if not path.exists():
            continue

        checked += 1
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            match = PUBLIC_VAGUE_DATA_ROUTE_PATTERN.search(line)
            if match:
                hits.append(f"{rel_path}:{line_no}: {match.group(0)}")

    if hits:
        return CheckResult(
            "public_data_route_wording_specific",
            False,
            "vague public data-route wording found: " + " | ".join(hits),
        )
    return CheckResult(
        "public_data_route_wording_specific",
        True,
        f"{checked} public-facing docs use specific data/access-route wording",
    )


def check_forbidden_50_state_claims(root: Path) -> CheckResult:
    pattern = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    hits = []
    for path in iter_markdown_files(root):
        rel = path.relative_to(root)
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            if pattern.search(line):
                hits.append(f"{rel}:{line_no}: {line.strip()}")

    if hits:
        return CheckResult(
            "forbidden_50_state_claims",
            False,
            "forbidden wording found: " + " | ".join(hits),
        )
    return CheckResult(
        "forbidden_50_state_claims",
        True,
        "no prohibited positive 50-state wording found",
    )


def check_self_contained_manuscript_no_paper9_placeholder(root: Path) -> CheckResult:
    path = root / SELF_CONTAINED_MANUSCRIPT
    if not path.exists():
        return CheckResult(
            "self_contained_manuscript_no_paper9_placeholder",
            False,
            f"missing manuscript: {SELF_CONTAINED_MANUSCRIPT}",
        )

    text = read_text(path)
    if "@zhou2026paper9_local" in text:
        return CheckResult(
            "self_contained_manuscript_no_paper9_placeholder",
            False,
            "self-contained manuscript body still cites @zhou2026paper9_local",
        )
    return CheckResult(
        "self_contained_manuscript_no_paper9_placeholder",
        True,
        "self-contained manuscript has no @zhou2026paper9_local citation",
    )


def bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,\s]+)", text))


def cited_keys(text: str) -> set[str]:
    return set(re.findall(r"@([A-Za-z0-9_:-]+)", text))


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    heading_level = len(heading) - len(heading.lstrip("#"))
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""

    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if not line.startswith("#"):
            continue
        level = len(line) - len(line.lstrip("#"))
        if level <= heading_level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def markdown_section_outside_code_fences(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    heading_level = len(heading) - len(heading.lstrip("#"))
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == heading:
            start = index + 1
            break
    if start is None:
        return ""

    end = len(lines)
    in_fence = False
    for index in range(start, len(lines)):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped.startswith("#"):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        if level <= heading_level:
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def has_markdown_heading_outside_code_fences(text: str, heading: str) -> bool:
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence and stripped == heading:
            return True
    return False


def markdown_heading_positions_outside_code_fences(
    text: str, headings: tuple[str, ...]
) -> dict[str, int]:
    heading_set = set(headings)
    positions = {}
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence and stripped in heading_set and stripped not in positions:
            positions[stripped] = line_no
    return positions


def markdown_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def check_citation_keys_resolve(root: Path) -> CheckResult:
    bib_paths = [
        root / "references" / "paper10_verified_references_2026-06-09.bib",
        root / "references" / "paper10_local_sources_2026-06-09.bib",
    ]
    keys: set[str] = set()
    for path in bib_paths:
        if not path.exists():
            return CheckResult(
                "citation_keys_resolve",
                False,
                f"missing bibliography: {path.relative_to(root)}",
            )
        keys.update(bib_keys(read_text(path)))

    cite_paths = [
        root / RESULTS / "e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md",
        root
        / RESULTS
        / "e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md",
        root / CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        root / PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
        root / "references" / "paper10_citation_map_2026-06-09.md",
        root / RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
    ]
    cited: set[str] = set()
    for path in cite_paths:
        if path.exists():
            cited.update(cited_keys(read_text(path)))

    missing = sorted(key for key in cited if key not in keys)
    if missing:
        return CheckResult(
            "citation_keys_resolve",
            False,
            "missing bibliography keys: " + ", ".join(missing),
        )
    return CheckResult(
        "citation_keys_resolve",
        True,
        f"{len(cited)} cited keys resolve against {len(keys)} bibliography keys",
    )


def check_reviewer_smoke_protocol_links(root: Path) -> CheckResult:
    missing = []
    protocol_name = SMOKE_PROTOCOL.name
    log_name = SMOKE_LOG.name
    for rel_path in SMOKE_LINK_DOCS:
        path = root / rel_path
        if not path.exists():
            missing.append(f"{rel_path}: missing file")
            continue
        text = read_text(path)
        if protocol_name not in text:
            missing.append(f"{rel_path}: missing {protocol_name}")
        if log_name not in text:
            missing.append(f"{rel_path}: missing {log_name}")

    if missing:
        return CheckResult(
            "reviewer_smoke_protocol_links",
            False,
            "; ".join(missing),
        )
    return CheckResult(
        "reviewer_smoke_protocol_links",
        True,
        f"{len(SMOKE_LINK_DOCS)} docs link smoke protocol and verification log",
    )


def check_integrated_dongxing_source_data_links(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        DONGXING_PLOT_SCRIPT,
        RESULTS / "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        RESULTS / "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_dongxing_source_data_links",
            False,
            "missing Dongxing source-data files: " + ", ".join(missing),
        )

    figure_plan = read_text(root / INTEGRATED_DONGXING_FIGURE_PLAN)
    source_map = read_text(root / INTEGRATED_DONGXING_SOURCE_DATA_MAP)
    plot_script = read_text(root / DONGXING_PLOT_SCRIPT)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    tables = read_text(root / INTEGRATED_DONGXING_TABLES)

    source_tokens = [
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing_tokens = []
    for label, text in [
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_SCAFFOLD), scaffold),
        (str(INTEGRATED_DONGXING_TABLES), tables),
    ]:
        for token in source_tokens:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    for label, text in [
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_SCAFFOLD), scaffold),
    ]:
        for token in ["Figure 4", "Figure 5"]:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    script_tokens = [
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "dongxing_return_label_scaling",
        "dongxing_low_label_budget_stress_test",
    ]
    for token in script_tokens:
        if token not in plot_script:
            missing_tokens.append(f"{DONGXING_PLOT_SCRIPT}: {token}")

    for token in [
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        str(DONGXING_PLOT_SCRIPT).replace("\\", "/"),
        "not robustly supported",
    ]:
        if token not in source_map.replace("\\", "/"):
            missing_tokens.append(f"{INTEGRATED_DONGXING_SOURCE_DATA_MAP}: {token}")
        if token not in figure_plan.replace("\\", "/"):
            missing_tokens.append(f"{INTEGRATED_DONGXING_FIGURE_PLAN}: {token}")

    if missing_tokens:
        return CheckResult(
            "integrated_dongxing_source_data_links",
            False,
            "missing Dongxing cross-links: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_dongxing_source_data_links",
        True,
        "Dongxing figure plan, source-data map, scaffold, tables, and plotting script are cross-linked",
    )


def check_dongxing_data_availability_routes(root: Path) -> CheckResult:
    required_files = [
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        RESULTS / "e0_dongxing_local_data_cross_region_audit_2026-06-10.md",
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "dongxing_data_availability_routes",
            False,
            "missing Dongxing availability files: " + ", ".join(missing),
        )

    availability = read_text(root / DATA_CODE_AVAILABILITY)
    rights_register = read_text(root / DATA_ACCESS_RIGHTS_REGISTER)

    required_tokens = [
        "Dongxing/Neijiang",
        "e0_source_data_map_with_dongxing_2026-06-11.md",
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "3711-block",
        "76,376",
        "public deposit",
        "controlled-access",
        "[DONGXING/NEIJIANG DATA DOI TO BE ADDED]",
        "[DONGXING/NEIJIANG CONTROLLED-ACCESS RECORD TO BE ADDED]",
    ]
    missing_tokens = []
    for label, text in [
        (str(DATA_CODE_AVAILABILITY), availability),
        (str(DATA_ACCESS_RIGHTS_REGISTER), rights_register),
    ]:
        normalized_text = " ".join(text.split())
        for token in required_tokens:
            if token not in normalized_text:
                missing_tokens.append(f"{label}: {token}")

    local_path_patterns = [
        r"D:\\test\\neijiang_cross_region",
        r"D:\\test\\dongxing",
    ]
    for pattern in local_path_patterns:
        if re.search(pattern, availability):
            missing_tokens.append(f"{DATA_CODE_AVAILABILITY}: public statement leaks {pattern}")

    if missing_tokens:
        return CheckResult(
            "dongxing_data_availability_routes",
            False,
            "Dongxing availability route gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "dongxing_data_availability_routes",
        True,
        "Data/Code Availability and rights register cover Dongxing public/control access routes",
    )


def check_paper10_data_publication_boundary_backfill_current(root: Path) -> CheckResult:
    required_files = [
        DATA_AVAILABILITY,
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        ARCHIVE_METADATA_TEMPLATES,
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD,
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_data_publication_boundary_backfill_current",
            False,
            "missing Paper10 data-publication boundary backfill files: "
            + ", ".join(missing),
        )

    doc_tokens = {
        DATA_AVAILABILITY: [
            "Paper10 author data/code publication boundary",
            "Apache-2.0",
            "CC0-1.0",
            "Original Bishan and Dongxing DLTB inputs are confidential",
            "4open README.md direct reviewer link",
            "code is licensed under Apache-2.0",
            "CC0-1.0",
            "confidential",
            "cannot be shared externally",
            PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD.name,
        ],
        DATA_CODE_AVAILABILITY: [
            "Paper10 author data/code publication boundary",
            "Apache-2.0",
            "CC0-1.0",
            "Original Bishan and Dongxing DLTB inputs are confidential",
            "full Bishan Tool2 transition and pairwise files are treated as derived artifacts",
            "DLTB-leakage check",
            "are not publicly redistributable",
            "cannot be shared externally",
            "Apache-2.0",
            "CC0-1.0",
            "cannot be shared externally",
            "4open README.md direct reviewer link has been author-confirmed available",
        ],
        DATA_ACCESS_RIGHTS_REGISTER: [
            "Author closeout update (2026-07-08)",
            "Apache-2.0",
            "CC0-1.0",
            "confidential",
            "Apache-2.0",
            "confidential_no_external_access",
            "split_route_original_dongxing_dltb_restricted_derived_non_dltb_public_pending_leakage_check_and_controlled_route",
        ],
        ARCHIVE_METADATA_TEMPLATES: [
            "Author publication boundary update (2026-07-09)",
            "Apache-2.0",
            "CC0-1.0",
            "confidential",
            "Do not place original Bishan or Dongxing DLTB inputs in Record 1",
            "DLTB-leakage check",
            "Apache-2.0",
            "confidential_no_external_access",
        ],
    }

    missing_tokens = []
    for rel_path, tokens in doc_tokens.items():
        doc_text = read_text(root / rel_path)
        normalized_doc = " ".join(doc_text.split())
        for token in tokens:
            if token not in normalized_doc:
                missing_tokens.append(f"{rel_path}: {token}")

    if missing_tokens:
        return CheckResult(
            "paper10_data_publication_boundary_backfill_current",
            False,
            "Paper10 data-publication boundary backfill gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_data_publication_boundary_backfill_current",
        True,
        "Paper10 data-publication boundary is backfilled into availability and archive materials",
    )


def check_integrated_figure_table_numbering_frozen(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_figure_table_numbering_frozen",
            False,
            "missing integrated numbering files: " + ", ".join(missing),
        )

    freeze = read_text(root / INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    tables = read_text(root / INTEGRATED_DONGXING_TABLES)
    figure_plan = read_text(root / INTEGRATED_DONGXING_FIGURE_PLAN)
    source_map = read_text(root / INTEGRATED_DONGXING_SOURCE_DATA_MAP)

    freeze_tokens = [
        "not a target-journal final layout",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_DONGXING_FIGURE_PLAN.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
        "Supplementary Table S1",
        "Supplementary Table S2",
        "Internal Control Table C1",
        "failed monitor gates",
        "do not support robust Bishan-to-Dongxing transfer superiority",
        "e0_frontier_random050_seedwise_rewards_2026-06-09.csv",
        "e0_frontier_random050_topk_diagnostics_2026-06-09.csv",
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
    ]
    missing_tokens = []
    for token in freeze_tokens:
        if token not in freeze:
            missing_tokens.append(f"{INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE}: {token}")

    freeze_name = INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name
    linked_docs = [
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    doc_text = {
        str(INTEGRATED_DONGXING_SCAFFOLD): scaffold,
        str(INTEGRATED_DONGXING_TABLES): tables,
        str(INTEGRATED_DONGXING_FIGURE_PLAN): figure_plan,
        str(INTEGRATED_DONGXING_SOURCE_DATA_MAP): source_map,
    }
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        text = doc_text.get(str(rel_path), read_text(path))
        if freeze_name not in text:
            missing_tokens.append(f"{rel_path}: {freeze_name}")

    for label, text in [
        (str(INTEGRATED_DONGXING_SOURCE_DATA_MAP), source_map),
        (str(INTEGRATED_DONGXING_FIGURE_PLAN), figure_plan),
        (str(INTEGRATED_DONGXING_TABLES), tables),
    ]:
        for token in ["Main Figure 4", "Supplementary Figure S1", "Main Table 3"]:
            if token not in text:
                missing_tokens.append(f"{label}: {token}")

    if missing_tokens:
        return CheckResult(
            "integrated_figure_table_numbering_frozen",
            False,
            "figure/table numbering freeze gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_figure_table_numbering_frozen",
        True,
        "integrated main/supplementary figure and table numbering is frozen and cross-linked",
    )


def check_submission_blocker_decision_packet_current(root: Path) -> CheckResult:
    required_files = [
        SUBMISSION_BLOCKER_DECISION_PACKET,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "submission_blocker_decision_packet_current",
            False,
            "missing submission blocker decision files: " + ", ".join(missing),
        )

    packet = read_text(root / SUBMISSION_BLOCKER_DECISION_PACKET)
    required_tokens = [
        "not a final manuscript",
        "Do not submit until",
        "Target journal and article type",
        "Repository DOI or reviewer link",
        "Code licence",
        "Generated-data rights",
        "Full Bishan Tool2 data access route",
        "GPKG-root geospatial inputs access route",
        "Dongxing/Neijiang prepared data access route",
        "Citation policy",
        "Statistical reporting policy",
        "Current status: unresolved",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        "e0_integrated_figure_table_numbering_freeze_2026-06-11.md",
        "e0_data_code_availability_draft_2026-06-09.md",
        "e0_data_access_and_rights_decision_register_2026-06-09.md",
        "e0_archive_release_and_doi_backfill_checklist_2026-06-09.md",
        "e0_source_data_map_with_dongxing_2026-06-11.md",
    ]
    missing_tokens = []
    for token in required_tokens:
        if token not in packet:
            missing_tokens.append(f"{SUBMISSION_BLOCKER_DECISION_PACKET}: {token}")

    packet_name = SUBMISSION_BLOCKER_DECISION_PACKET.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    if missing_tokens:
        return CheckResult(
            "submission_blocker_decision_packet_current",
            False,
            "submission blocker decision packet gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "submission_blocker_decision_packet_current",
        True,
        "submission blocker decision packet is current and cross-linked",
    )


def check_integrated_target_venue_conversion_checklist_current(
    root: Path,
) -> CheckResult:
    required_files = [
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_target_venue_conversion_checklist_current",
            False,
            "missing integrated target-venue conversion files: " + ", ".join(missing),
        )

    checklist = read_text(root / INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST)
    required_tokens = [
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        "Dongxing/Neijiang",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        "Target journal and article type",
        "Repository DOI or reviewer link",
        "Dongxing/Neijiang prepared data access route",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in checklist:
            missing_tokens.append(f"{INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST}: {token}")

    checklist_name = INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md",
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if checklist_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {checklist_name}")

    if missing_tokens:
        return CheckResult(
            "integrated_target_venue_conversion_checklist_current",
            False,
            "integrated target-venue checklist gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_target_venue_conversion_checklist_current",
        True,
        "integrated target-venue/manuscript conversion checklist is current and cross-linked",
    )


def check_integrated_citation_statistics_policy_current(root: Path) -> CheckResult:
    required_files = [
        INTEGRATED_CITATION_STATISTICS_POLICY,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
        Path("references") / "paper10_citation_map_2026-06-09.md",
        Path("references") / "paper10_verified_references_2026-06-09.bib",
        Path("references") / "paper10_local_sources_2026-06-09.bib",
        Path("references") / "paper10_paper9_local_source_status_2026-06-09.md",
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "integrated_citation_statistics_policy_current",
            False,
            "missing citation/statistics policy files: " + ", ".join(missing),
        )

    policy = read_text(root / INTEGRATED_CITATION_STATISTICS_POLICY)
    required_tokens = [
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "not a final reference style",
        "not a target-journal statistical-analysis plan",
        "references/paper10_citation_map_2026-06-09.md",
        "references/paper10_verified_references_2026-06-09.bib",
        "references/paper10_local_sources_2026-06-09.bib",
        "references/paper10_paper9_local_source_status_2026-06-09.md",
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        "Target journal and article type",
        "Citation policy",
        "Statistical reporting policy",
        "zhou2026paper9_local",
        "local-only",
        "self-contained Paper10 Methods route",
        "maes2026leworldmodel",
        "2026 arXiv preprint",
        "No formal hypothesis tests have been run",
        "Do not use `statistically significant`",
        "p-values",
        "descriptive means",
        "sample standard deviations",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]

    missing_tokens = []
    for token in required_tokens:
        if token not in policy:
            missing_tokens.append(f"{INTEGRATED_CITATION_STATISTICS_POLICY}: {token}")

    policy_name = INTEGRATED_CITATION_STATISTICS_POLICY.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        RESULTS / "e0_post_dongxing_submission_gap_audit_2026-06-10.md",
        RESULTS / "e0_citation_and_claim_checklist_2026-06-09.md",
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        Path("references") / "paper10_citation_map_2026-06-09.md",
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if policy_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {policy_name}")

    inferential_docs = [
        SELF_CONTAINED_MANUSCRIPT,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    ]
    for rel_path in inferential_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), start=1):
            match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
            if match:
                missing_tokens.append(
                    f"{rel_path}:{line_no}: unsupported inferential wording "
                    f"{match.group(0)}"
                )

    if missing_tokens:
        return CheckResult(
            "integrated_citation_statistics_policy_current",
            False,
            "citation/statistical reporting policy gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "integrated_citation_statistics_policy_current",
        True,
        "citation and statistical-reporting policy is current and cross-linked",
    )


def check_ceus_reviewer_improvement_packet_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_reviewer_improvement_packet_current",
            False,
            "missing CEUS reviewer-improvement files: " + ", ".join(missing),
        )

    packet = read_text(root / CEUS_REVIEWER_IMPROVEMENT_PACKET)
    scaffold = read_text(root / INTEGRATED_DONGXING_SCAFFOLD)
    target_checklist = read_text(root / INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST)

    packet_tokens = [
        "CEUS Research Article candidate",
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        "D:\\test\\tool2\\transitions.npz",
        "D:\\test\\dem_slope_analysis\\output\\DLTB_with_slope.gpkg",
        "D:\\test\\results_real\\blocks",
        "D:\\test\\neijiang_cross_region",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP",
        "candidate-value-weight=1.0",
        "external optimizer baseline",
        "No new full Bishan rerun was run in this pass",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    scaffold_tokens = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "candidate-value-weight=1.0",
        "Constrained MDP, CPO, or RCPO",
    ]
    checklist_tokens = [
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "CEUS Research Article candidate route",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "Soft training and hard inference",
        "candidate-value-weight=1.0",
    ]

    missing_tokens = []
    for token in packet_tokens:
        if token not in packet:
            missing_tokens.append(f"{CEUS_REVIEWER_IMPROVEMENT_PACKET}: {token}")
    for token in scaffold_tokens:
        if token not in scaffold:
            missing_tokens.append(f"{INTEGRATED_DONGXING_SCAFFOLD}: {token}")
    for token in checklist_tokens:
        if token not in target_checklist:
            missing_tokens.append(
                f"{INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST}: {token}"
            )

    packet_name = CEUS_REVIEWER_IMPROVEMENT_PACKET.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_DONGXING_SCAFFOLD,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    if missing_tokens:
        return CheckResult(
            "ceus_reviewer_improvement_packet_current",
            False,
            "CEUS reviewer-improvement packet gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_reviewer_improvement_packet_current",
        True,
        "CEUS reviewer-improvement packet is current and cross-linked",
    )


def check_ceus_research_article_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        INTEGRATED_DONGXING_SCAFFOLD,
        INTEGRATED_DONGXING_TABLES,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_research_article_manuscript_draft_current",
            False,
            "missing CEUS manuscript draft files: " + ", ".join(missing),
        )

    path = root / CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT
    text = read_text(path)
    missing_tokens = []

    required_tokens = [
        "CEUS Research Article candidate",
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        INTEGRATED_DONGXING_SCAFFOLD.name,
        INTEGRATED_DONGXING_TABLES.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        "Title",
        "Highlights",
        "Abstract",
        "Keywords",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and Table List",
        "Claim-Evidence and Unresolved Blockers",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP, CPO, or RCPO",
        "candidate-value-weight=1.0",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: @zhou2026paper9_local"
        )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: missing ## Abstract section"
        )
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: abstract has "
            f"{abstract_words} words"
        )

    highlights = [
        line[2:].strip()
        for line in markdown_section(text, "## Highlights").splitlines()
        if line.startswith("- ")
    ]
    if not 3 <= len(highlights) <= 5:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: "
            f"{len(highlights)} highlight bullets"
        )
    long_highlights = [
        item
        for item in highlights
        if len(item) > 85
    ]
    if long_highlights:
        missing_tokens.append(
            f"{CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT}: highlights over 85 chars: "
            + " | ".join(long_highlights)
        )

    if missing_tokens:
        return CheckResult(
            "ceus_research_article_manuscript_draft_current",
            False,
            "CEUS manuscript draft gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_research_article_manuscript_draft_current",
        True,
        (
            "CEUS manuscript draft is current, abstract/highlights fit limits, "
            "and claim boundaries are guarded"
        ),
    )


def check_ceus_stage3_manuscript_reframe_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        ORIGINAL_VISION_STAGE1_STAGE2_DECISION_PACKET,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_stage3_manuscript_reframe_current",
            False,
            "missing CEUS Stage 3 manuscript reframe files: " + ", ".join(missing),
        )

    text = read_text(root / CEUS_STAGE3_MANUSCRIPT_REFRAME)
    missing_tokens = []
    reframe_name = CEUS_STAGE3_MANUSCRIPT_REFRAME.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if reframe_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {reframe_name}")

    required_tokens = [
        "CEUS Stage 3 manuscript reframe",
        "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md",
        "e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json",
        "e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md",
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "Paper10 now solves",
        "monitor-gated value labels",
        "Bishan 20x16/top5",
        "69.4705",
        "matched Paper9 baseline",
        "67.5437",
        "Stage 3 confirmatory 50-state rows did not beat the matched Paper9 baseline",
        "frontier_random050_50x16_h5_seed48_f050",
        "64.2960",
        "frontier_random050_50x24_h5_seed47_f075",
        "66.2544",
        "diagnostic_near_pass",
        "67.4913",

        "must not be pooled",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
        "Title replacement",
        "Abstract replacement",
        "Results replacement",
        "Discussion replacement",
        "Conclusion replacement",
        "Claim-evidence map",
        "Current blockers before final submission",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: {token}")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract replacement")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: missing ## Abstract replacement section"
        )
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_REFRAME}: abstract replacement has "
            f"{abstract_words} words"
        )

    if missing_tokens:
        return CheckResult(
            "ceus_stage3_manuscript_reframe_current",
            False,
            "CEUS Stage 3 manuscript reframe gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_stage3_manuscript_reframe_current",
        True,
        "CEUS Stage 3 manuscript reframe is current and claim-bounded",
    )


def check_ceus_stage3_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "ceus_stage3_manuscript_draft_current",
            False,
            "missing CEUS Stage 3 manuscript draft files: " + ", ".join(missing),
        )

    text = read_text(root / CEUS_STAGE3_MANUSCRIPT_DRAFT)
    missing_tokens = []
    draft_name = CEUS_STAGE3_MANUSCRIPT_DRAFT.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if draft_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {draft_name}")

    required_tokens = [
        "CEUS Stage 3 manuscript draft",
        "not a final submission package",
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "Paper9 has not been formally submitted",
        "self-contained Paper10 Methods route",
        "One-Sentence Argument",
        "Terminology Ledger",
        "Title",
        "Highlights",
        "Abstract",
        "Keywords",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and Table List",
        "Claim-Evidence and Unresolved Blockers",
        "Bishan 20x16/top5",
        "69.4705",
        "matched Paper9 baseline",
        "67.5437",
        "frontier_random050_50x16_h5_seed48_f050",
        "64.2960",
        "frontier_random050_50x24_h5_seed47_f075",
        "66.2544",
        "diagnostic_near_pass",
        "67.4913",

        "must not be pooled",
        "pairwise-only baseline policy remains unresolved",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "soft training and hard inference",
        "Constrained MDP, CPO, or RCPO",
        "candidate-value-weight=1.0",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 3",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim direct 50-state Bishan scale-up success",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    abstract = markdown_section(text, "## Abstract")
    abstract_words = markdown_word_count(abstract)
    if not abstract:
        missing_tokens.append(f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: missing ## Abstract")
    elif abstract_words > 250:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: abstract has {abstract_words} words"
        )

    highlights = [
        line[2:].strip()
        for line in markdown_section(text, "## Highlights").splitlines()
        if line.startswith("- ")
    ]
    if not 3 <= len(highlights) <= 5:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: {len(highlights)} highlight bullets"
        )
    long_highlights = [item for item in highlights if len(item) > 85]
    if long_highlights:
        missing_tokens.append(
            f"{CEUS_STAGE3_MANUSCRIPT_DRAFT}: highlights over 85 chars: "
            + " | ".join(long_highlights)
        )

    if missing_tokens:
        return CheckResult(
            "ceus_stage3_manuscript_draft_current",
            False,
            "CEUS Stage 3 manuscript draft gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "ceus_stage3_manuscript_draft_current",
        True,
        "CEUS Stage 3 manuscript draft is current and claim-bounded",
    )


def check_paper10_project_proposal_report_current(root: Path) -> CheckResult:
    required_files = [
        PROJECT_PROPOSAL_REPORT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_CITATION_STATISTICS_POLICY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_project_proposal_report_current",
            False,
            "missing Paper10 project proposal report files: " + ", ".join(missing),
        )

    text = read_text(root / PROJECT_PROPOSAL_REPORT)
    missing_tokens = []
    report_name = PROJECT_PROPOSAL_REPORT.name
    linked_docs = [Path("README.md"), Path("MANIFEST.md")]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if report_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {report_name}")

    required_tokens = [
        "Paper10 课题立项/开题报告替代稿",
        "课题立项临时材料",
        "不是正式投稿论文",
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "基于 monitor-gated value labels 的 GeoJEPA-MPC 农田布局规划方法研究",
        "拟解决的核心问题",
        "研究目标",
        "研究内容与技术路线",
        "已有工作基础与阶段性结果",
        "初步结论",
        "创新点",
        "可行性基础",
        "后续研究计划",
        "预期成果",
        "风险、边界与待决事项",
        "Bishan 20x16/top5",
        "69.4705",
        "67.5437",
        "1.9269",
        "64.2960",
        "66.2544",
        "67.4913",

        "must not be pooled",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "block-level planning-unit abstraction",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "pairwise-only baseline policy",
        "repository DOI",
        "statistical reporting policy",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{PROJECT_PROPOSAL_REPORT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{PROJECT_PROPOSAL_REPORT}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PROJECT_PROPOSAL_REPORT}:{line_no}: positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PROJECT_PROPOSAL_REPORT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    section_count = sum(1 for line in text.splitlines() if line.startswith("## "))
    if section_count < 10:
        missing_tokens.append(
            f"{PROJECT_PROPOSAL_REPORT}: only {section_count} level-2 sections"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_project_proposal_report_current",
            False,
            "Paper10 project proposal report gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_project_proposal_report_current",
        True,
        "Paper10 project proposal report is current and claim-bounded",
    )


def check_paper10_author_decision_matrix_current(root: Path) -> CheckResult:
    required_files = [
        AUTHOR_DECISION_MATRIX,
        PROJECT_PROPOSAL_REPORT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_author_decision_matrix_current",
            False,
            "missing Paper10 author decision matrix files: " + ", ".join(missing),
        )

    text = read_text(root / AUTHOR_DECISION_MATRIX)
    missing_tokens = []
    matrix_name = AUTHOR_DECISION_MATRIX.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if matrix_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {matrix_name}")

    required_tokens = [
        "Paper10 author decision and formal-submission conversion matrix",
        "author-decision control document",
        "not a final manuscript",
        PROJECT_PROPOSAL_REPORT.name,
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        "One-sentence conversion argument",
        "Decision matrix",
        "Recommended decision order",
        "Default manuscript route if no new author decision arrives",
        "Claim-evidence locks for conversion",
        "Completion checklist",
        "Target venue and article type",
        "Comparator and pairwise-only baseline policy",
        "Repository DOI or reviewer link",
        "Code licence",
        "Generated-output and checkpoint rights",
        "Full Bishan Tool2 access route",
        "GPKG-root geospatial input route",
        "Dongxing/Neijiang prepared-data route",
        "Citation policy",
        "Statistical reporting policy",
        "Final figure/table export package",
        "Claim boundary",
        "matched Paper9 `rank_seed2028`",
        "self-contained Paper10 Methods route",
        "20x16/top5 mean reward `69.4705`",
        "matched Paper9 baseline `67.5437`",
        "`64.2960` and `66.2544`",
        "`67.4913`",
        "must not be pooled",
        "Do not claim direct 50-state Bishan scale-up success",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "Constrained MDP/CPO/RCPO",
        "does not mean the paper is ready for final submission",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{AUTHOR_DECISION_MATRIX}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{AUTHOR_DECISION_MATRIX}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{AUTHOR_DECISION_MATRIX}:{line_no}: positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{AUTHOR_DECISION_MATRIX}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    checklist_items = [
        line
        for line in markdown_section(text, "## Completion checklist").splitlines()
        if line.startswith("- [ ]")
    ]
    if len(checklist_items) < 12:
        missing_tokens.append(
            f"{AUTHOR_DECISION_MATRIX}: {len(checklist_items)} checklist items"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_author_decision_matrix_current",
            False,
            "Paper10 author decision matrix gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_author_decision_matrix_current",
        True,
        "Paper10 author decision matrix is current and claim-bounded",
    )


def check_paper10_formal_manuscript_blueprint_current(root: Path) -> CheckResult:
    required_files = [
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
        PROJECT_PROPOSAL_REPORT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_formal_manuscript_blueprint_current",
            False,
            "missing Paper10 formal manuscript blueprint files: " + ", ".join(missing),
        )

    text = read_text(root / FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT)
    missing_tokens = []
    blueprint_name = FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if blueprint_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {blueprint_name}")

    required_tokens = [
        "Paper10 formal manuscript assembly blueprint",
        "not a final manuscript",
        "one-sentence argument",
        "Terminology ledger",
        "Section assembly plan",
        "Evidence-first drafting order",
        "Title and abstract",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and table assembly map",
        "Claim-evidence map",
        "Author-decision blockers",
        "Next manuscript-editing sequence",
        AUTHOR_DECISION_MATRIX.name,
        PROJECT_PROPOSAL_REPORT.name,
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP.name,
        "Bishan 20x16/top5",
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "64.2960",
        "66.2544",
        "67.4913",

        "must not be pooled",
        "matched Paper9 `rank_seed2028`",
        "self-contained Paper10 Methods route",
        "pairwise-only baseline policy",
        "repository DOI or reviewer link",
        "full Bishan Tool2",
        "GPKG-root",
        "Dongxing/Neijiang prepared data",
        "area-tolerance matching",
        "shared-perimeter-weighted contiguity",
        "Constrained MDP/CPO/RCPO",
        "Do not claim direct 50-state Bishan scale-up success",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(
            f"{FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT}: @zhou2026paper9_local"
        )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    section_count = sum(1 for line in text.splitlines() if line.startswith("## "))
    if section_count < 9:
        missing_tokens.append(
            f"{FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT}: only {section_count} "
            "level-2 sections"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_formal_manuscript_blueprint_current",
            False,
            "Paper10 formal manuscript blueprint gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_formal_manuscript_blueprint_current",
        True,
        "Paper10 formal manuscript blueprint is current and claim-bounded",
    )


def check_paper10_formal_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_FORMAL_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON,
        PAPER10_MECHANISM_ABLATION_PACKET_MD,
        PAPER10_MECHANISM_ABLATION_PACKET_JSON,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST,
        INTEGRATED_CITATION_STATISTICS_POLICY,
        CEUS_REVIEWER_IMPROVEMENT_PACKET,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_formal_manuscript_draft_current",
            False,
            "missing Paper10 formal manuscript draft files: " + ", ".join(missing),
        )

    text = read_text(root / PAPER10_FORMAL_MANUSCRIPT_DRAFT)
    normalized_text = " ".join(text.split())
    normalized_casefold_text = normalized_text.casefold()
    missing_tokens = []
    draft_name = PAPER10_FORMAL_MANUSCRIPT_DRAFT.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if draft_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {draft_name}")

    required_tokens = [
        "Paper10 formal manuscript draft",
        "not a final submission package",
        "One-Sentence Argument",
        "Terminology Ledger",
        "Title",
        "Highlights",
        "Abstract",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "Conclusion",
        "Data and Code Availability",
        "Figure and Table List",
        "Claim-Evidence and Unresolved Blockers",
        "Chinese Author Notes",
        CEUS_RESEARCH_ARTICLE_MANUSCRIPT_DRAFT.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD.name,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON.name,
        PAPER10_MECHANISM_ABLATION_PACKET_MD.name,
        PAPER10_MECHANISM_ABLATION_PACKET_JSON.name,
        INTEGRATED_TARGET_VENUE_CONVERSION_CHECKLIST.name,
        INTEGRATED_CITATION_STATISTICS_POLICY.name,
        CEUS_REVIEWER_IMPROVEMENT_PACKET.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "monitor-gated value labels",
        "Executable masks are rollout-critical",
        "Bishan 20x16/top5",
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "40.3515",
        "64.2960",
        "66.2544",
        "67.4913",
        "candidate-score sweep",
        "blend0.10",
        "must not be pooled",
        "candidate-value-weight=1.0",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "irregular cadastral parcel deployment",
        "Repository DOI or anonymous reviewer link is pending",
        "software licence and generated-output rights terms remain pending",
        "formal hypothesis-test language requires a predefined statistical plan",
    ]
    for token in required_tokens:
        if token.casefold() not in normalized_casefold_text:
            missing_tokens.append(f"{PAPER10_FORMAL_MANUSCRIPT_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(f"{PAPER10_FORMAL_MANUSCRIPT_DRAFT}: @zhou2026paper9_local")

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_FORMAL_MANUSCRIPT_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_FORMAL_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_formal_manuscript_draft_current",
            False,
            "Paper10 formal manuscript draft gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_formal_manuscript_draft_current",
        True,
        "Paper10 formal manuscript draft is current and claim-bounded",
    )


def _is_unguarded_every_seed_claim(line: str) -> bool:
    negative_guardrail = re.compile(
        r"\b(does not|do not|must not|cannot|can't|should not|not supported|unsupported|not uniform|mixed)\b",
        re.IGNORECASE,
    )
    targets = (
        re.compile(
            r"\bevery[- ]seed\b.{0,100}\b(improv(?:e|es|ed|ement)?|win(?:s)?|beat(?:s)?|superior(?:ity)?)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\buniform\b.{0,100}\b(seed|per[- ]seed)\b.{0,100}\b(improv(?:e|es|ed|ement)?|win(?:s)?|beat(?:s)?|superior(?:ity)?)\b",
            re.IGNORECASE,
        ),
    )
    for clause in re.split(r"[;.!?]+", line):
        if not clause.strip():
            continue
        if negative_guardrail.search(clause):
            continue
        if any(target.search(clause) for target in targets):
            return True
    return False


def check_paper10_bounded_manuscript_assembly_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT,
        PAPER10_FORMAL_MANUSCRIPT_DRAFT,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON,
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
        PAPER10_MECHANISM_ABLATION_PACKET_MD,
        PAPER10_MECHANISM_ABLATION_PACKET_JSON,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON,
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_bounded_manuscript_assembly_current",
            False,
            "missing Paper10 bounded manuscript assembly files: " + ", ".join(missing),
        )

    text = read_text(root / PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT)
    normalized_text = " ".join(text.split())
    normalized_casefold_text = normalized_text.casefold()
    missing_tokens = []
    draft_name = PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT.name
    linked_docs = [Path("README.md"), Path("MANIFEST.md")]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if draft_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {draft_name}")

    required_tokens = [
        "Paper10 bounded manuscript assembly draft",
        "not a final submission package",
        PAPER10_FORMAL_MANUSCRIPT_DRAFT.name,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD.name,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON.name,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD.name,
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER.name,
        "descriptive matched 5-seed result",
        "wins only 3/5 seeds",
        "seed0",
        "seed4",
        "-3.2408",
        "-8.2248",
        "inferential superiority is not supported",
        "uniform per-seed superiority",
        "post-hoc tuning",
        "69.4705",
        "67.5437",
        "1.9269",
        "1.0004",
        "7.2246",
        "40.3515",
        "64.2960",
        "66.2544",
        "67.4913",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "formal hypothesis-test language requires a predefined statistical plan",
    ]
    for token in required_tokens:
        if token.casefold() not in normalized_casefold_text:
            missing_tokens.append(f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}: {token}")

    if "@zhou2026paper9_local" in text:
        missing_tokens.append(
            f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}: @zhou2026paper9_local"
        )

    figure_table_lines = {
        line.split("|")[1].strip(): line
        for line in text.splitlines()
        if line.startswith("| Main Figure 2 |") or line.startswith("| Main Table 2 |")
    }
    five_seed_sources = [
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD.name,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON.name,
    ]
    for item in ("Main Figure 2", "Main Table 2"):
        line = figure_table_lines.get(item, "")
        if not line or not all(source in line for source in five_seed_sources):
            missing_tokens.append(
                f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}: "
                f"{item} 5-seed source route"
            )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}:{line_no}: "
                "positive 50-state wording"
            )
        if _is_unguarded_every_seed_claim(line):
            missing_tokens.append(
                f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}:{line_no}: "
                f"forbidden every-seed wording {line.strip()}"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_bounded_manuscript_assembly_current",
            False,
            "Paper10 bounded manuscript assembly gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_bounded_manuscript_assembly_current",
        True,
        "Paper10 bounded manuscript assembly is current and claim-bounded",
    )


def check_paper10_mechanism_ablation_packet_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_MECHANISM_ABLATION_PACKET_MD,
        PAPER10_MECHANISM_ABLATION_PACKET_JSON,
        PAPER10_MONITOR_GATED_TOP5_JSON,
        PAPER10_MONITOR_UNGATED_TOP4_JSON,
        PAPER10_MECHANISM_FULL_GATED_MASKED_JSON,
        PAPER10_MECHANISM_HEURISTIC_PAPER9_MASKED_JSON,
        PAPER10_MECHANISM_NO_MASK_JSON,
        PAPER10_MECHANISM_UNGATED_TOP4_ROLLOUT_JSON,
        PAPER10_MECHANISM_UNGATED_TOP4_TRAIN_JSON,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_JSON,
        PAPER10_FORMAL_MANUSCRIPT_DRAFT,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_mechanism_ablation_packet_current",
            False,
            "missing Paper10 mechanism ablation packet files: " + ", ".join(missing),
        )

    text = read_text(root / PAPER10_MECHANISM_ABLATION_PACKET_MD)
    normalized_text = " ".join(text.split())
    normalized_casefold_text = normalized_text.casefold()
    try:
        payload = json.loads(read_text(root / PAPER10_MECHANISM_ABLATION_PACKET_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_mechanism_ablation_packet_current",
            False,
            f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    packet_name = PAPER10_MECHANISM_ABLATION_PACKET_MD.name
    for rel_path in [PAPER10_FORMAL_MANUSCRIPT_DRAFT]:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    required_tokens = [
        "Paper10 mechanism ablation evidence packet",
        "not a manuscript claim",
        "Claim Boundary",
        "Monitor Gates",
        "Matched Bishan Mechanism Conditions",
        "Stage 3 Boundary Link",
        "Interpretation",
        "GeoJEPA itself is prior art",
        "monitor-gated value labels plus executable masks plus value-filtered MPC",
        "50-state evidence remains boundary evidence",
        "gated_top5",
        "ungated_top4",
        "full_gated_masked",
        "heuristic_paper9_masked",
        "no_mask",
        "69.4705",
        "67.5437",
        "40.3515",
        "100.0000",
        "98.0000",
        "must not be written as positive 50-state scale-up evidence",
    ]
    for token in required_tokens:
        if token.casefold() not in normalized_casefold_text:
            missing_tokens.append(f"{PAPER10_MECHANISM_ABLATION_PACKET_MD}: {token}")

    def payload_value(path: tuple[str, ...]):
        value = payload
        for key in path:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: {'.'.join(path)}"
                )
                return None
            value = value[key]
        return value

    expected_values = [
        (("packet",), "paper10_mechanism_ablation"),
        (("baseline_condition",), "full_gated_masked"),
        (("claim_boundary", "geo_jepa_prior_art_guard"), True),
        (("claim_boundary", "do_not_claim_geo_jepa_invention"), True),
        (("claim_boundary", "do_not_claim_direct_50_state_success"), True),
        (("claim_boundary", "do_not_claim_robust_transfer_superiority"), True),
        (("monitor_gates", "gated_top5", "decision"), "continue"),
        (("monitor_gates", "gated_top5", "gate_class"), "pass"),
        (("monitor_gates", "gated_top5", "top_k"), 5),
        (("monitor_gates", "ungated_top4", "decision"), "stop"),
        (("monitor_gates", "ungated_top4", "gate_class"), "stop"),
        (("monitor_gates", "ungated_top4", "top_k"), 4),
        (("stage3_boundary", "best_overall", "run"), "paper9 baseline"),
        (("stage3_boundary", "best_value_filter", "run"), "existing blend010"),
    ]
    for path, expected in expected_values:
        value = payload_value(path)
        if value is not None and value != expected:
            missing_tokens.append(
                f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
                f"{'.'.join(path)}={value!r}"
            )

    failed_metrics = payload_value(("monitor_gates", "ungated_top4", "failed_metrics"))
    if not isinstance(failed_metrics, list):
        missing_tokens.append(
            f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
            "monitor_gates.ungated_top4.failed_metrics"
        )
    else:
        for metric in ("candidate_topk_regret", "candidate_topk_overlap"):
            if metric not in failed_metrics:
                missing_tokens.append(
                    f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
                    f"monitor_gates.ungated_top4.failed_metrics.{metric}"
                )

    expected_condition_values = [
        (("condition_comparisons", "full_gated_masked", "mean_reward"), 69.4705),
        (("condition_comparisons", "full_gated_masked", "std_sample"), 1.0004),
        (("condition_comparisons", "heuristic_paper9_masked", "mean_reward"), 67.5437),
        (("condition_comparisons", "heuristic_paper9_masked", "std_sample"), 7.2246),
        (("condition_comparisons", "no_mask", "mean_reward"), 40.3515),
        (("condition_comparisons", "no_mask", "zero_swap_steps_sum"), 100.0),
        (("condition_comparisons", "no_mask", "negative_zero_swap_steps_sum"), 98.0),
        (("condition_comparisons", "ungated_top4", "mean_reward"), 69.4705),
    ]
    for path, expected in expected_condition_values:
        value = payload_value(path)
        if value is None:
            continue
        try:
            rounded = round(float(value), 4)
        except (TypeError, ValueError):
            missing_tokens.append(
                f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
                f"{'.'.join(path)}={value!r}"
            )
            continue
        if rounded != expected:
            missing_tokens.append(
                f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
                f"{'.'.join(path)}={rounded!r}"
            )

    source_data = payload_value(("stage3_boundary", "source_data"))
    if not isinstance(source_data, list) or len(source_data) < 6:
        missing_tokens.append(
            f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: stage3_boundary.source_data"
        )

    checkpoint_path = payload_value(
        ("training_metrics", "ungated_top4", "checkpoint_path")
    )
    if not isinstance(checkpoint_path, str) or "e0_mechanism_ungated_top4" not in checkpoint_path:
        missing_tokens.append(
            f"{PAPER10_MECHANISM_ABLATION_PACKET_JSON}: "
            "training_metrics.ungated_top4.checkpoint_path"
        )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    allowed_negative_context = (
        "do not",
        "must not",
        "not supported",
        "did not support",
        "boundary",
        "unless",
    )
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if forbidden_50_state.search(line):
            if not any(token in lowered for token in allowed_negative_context):
                missing_tokens.append(
                    f"{PAPER10_MECHANISM_ABLATION_PACKET_MD}:{line_no}: "
                    "positive 50-state wording"
                )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_MECHANISM_ABLATION_PACKET_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )
    for forbidden in ("invented geojepa", "submission-ready"):
        if forbidden in text.casefold():
            missing_tokens.append(
                f"{PAPER10_MECHANISM_ABLATION_PACKET_MD}: {forbidden}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_mechanism_ablation_packet_current",
            False,
            "Paper10 mechanism ablation packet gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_mechanism_ablation_packet_current",
        True,
        "Paper10 mechanism ablation packet is current and claim-bounded",
    )

def check_paper10_claim_source_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CLAIM_SOURCE_AUDIT_MD,
        PAPER10_CLAIM_SOURCE_AUDIT_JSON,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        RESULTS / "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        RESULTS / "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_claim_source_audit_current",
            False,
            "missing Paper10 claim-source audit files: " + ", ".join(missing),
        )

    text = read_text(root / PAPER10_CLAIM_SOURCE_AUDIT_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_CLAIM_SOURCE_AUDIT_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_claim_source_audit_current",
            False,
            f"{PAPER10_CLAIM_SOURCE_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_CLAIM_SOURCE_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 claim-source consistency audit",
        "source-derived audit",
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "Bishan 20x16/top5 anchor improves reward and stability",
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "frontier_random050_50x16_h5_seed48_f050 delta -3.2477",
        "frontier_random050_50x24_h5_seed47_f075 delta -1.2893",
        "frontier_random050_50x24_h5_seed48_f075 mean 67.4913",
        "must not be pooled",
        "Return-label scaling improves transfer family",
        "gain versus pairwise 13.7289",
        "Return-label scaling improves scratch family",
        "gain versus pairwise 15.5214",
        "Robust Bishan-to-Dongxing transfer superiority",
        "50x16 transfer minus scratch -4.1141",
        "budget 5: -8.7274",
        "budget 10: -3.4588",
        "budget 20: 4.2484",
        "Not supported: broad confirmatory 50-state baseline beating.",
        "Not supported: robust Bishan-to-Dongxing transfer superiority.",
        "Not supported: direct positive scale-up under the 50-state confirmatory protocol",
        "paper10_geojepa_mpc.experiments.paper10_claim_source_audit",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{PAPER10_CLAIM_SOURCE_AUDIT_MD}: {token}")

    expected_flags = {
        ("stage3", "claims", "bishan_anchor_improves_reward_and_stability", "supported"): True,
        ("stage3", "claims", "confirmatory_50state_rows_beat_baseline", "supported"): False,
        ("stage3", "claims", "diagnostic_near_pass_strengthens_confirmatory_claim", "supported"): False,
        ("dongxing", "claims", "return_label_scaling_improves_transfer_family", "supported"): True,
        ("dongxing", "claims", "return_label_scaling_improves_scratch_family", "supported"): True,
        ("dongxing", "claims", "robust_transfer_superiority", "supported"): False,
    }
    for path_keys, expected in expected_flags.items():
        value = payload
        for key in path_keys:
            value = value[key]
        if value is not expected:
            missing_tokens.append(
                f"{PAPER10_CLAIM_SOURCE_AUDIT_JSON}: {'.'.join(path_keys)}={value}"
            )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_CLAIM_SOURCE_AUDIT_MD}:{line_no}: positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_CLAIM_SOURCE_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_claim_source_audit_current",
            False,
            "Paper10 claim-source audit gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_claim_source_audit_current",
        True,
        "Paper10 claim-source audit is source-derived and claim-bounded",
    )


def check_paper10_figure_table_source_coverage_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON,
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        Path("README.md"),
        MANIFEST,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_figure_table_source_coverage_audit_current",
            False,
            "missing Paper10 figure/table source coverage audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_figure_table_source_coverage_audit_current",
            False,
            f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        MANIFEST,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 figure/table source coverage audit",
        "source-derived figure/table source coverage audit",
        "does not add a new experimental claim",
        "No rollout was rerun",
        "overall source coverage: PASS",
        "submission-ready figure/table package: NO",
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
        "blocked_pending_artwork",
        "scripted_preview_available",
        "frozen_table_available",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority is not supported",
        "Algorithm-readiness addendum",
        "setting-specific guard only",
        "e0_paper10_true_reward_guard_readiness_2026-07-08.json",
        "PASS does not mean the formal manuscript is ready for submission",
        "paper10_geojepa_mpc.experiments.figure_table_source_coverage_audit",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "source-derived figure/table source coverage audit",
        ("overall_source_coverage_pass",): True,
        ("submission_ready",): False,
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_files", "blueprint"): FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT.as_posix(),
        ("source_files", "numbering_freeze"): INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.as_posix(),
        ("source_files", "source_data_map"): INTEGRATED_DONGXING_SOURCE_DATA_MAP.as_posix(),
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    expected_items = [
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
    ]
    coverage_checks = payload.get("coverage_checks", {})
    if coverage_checks.get("expected_items") != expected_items:
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
            f"coverage_checks.expected_items={coverage_checks.get('expected_items')}"
        )
    for key in (
        "missing_blueprint_items",
        "missing_numbering_freeze_items",
        "missing_boundary_tokens",
    ):
        if coverage_checks.get(key) != []:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                f"coverage_checks.{key}={coverage_checks.get(key)}"
            )

    items = payload.get("items")
    if not isinstance(items, list) or len(items) != len(expected_items):
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: items"
        )
        items = []
    observed_items = [row.get("item") for row in items if isinstance(row, dict)]
    if observed_items != expected_items:
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
            f"items={observed_items}"
        )

    by_item = {row.get("item"): row for row in items if isinstance(row, dict)}
    expected_generation_status = {
        "Main Figure 1": "blocked_pending_artwork",
        "Main Figure 2": "scripted_preview_available",
        "Main Figure 3": "scripted_preview_available",
        "Main Figure 4": "scripted_preview_available",
        "Supplementary Figure S1": "scripted_preview_available",
        "Main Table 1": "table_source_available",
        "Main Table 2": "frozen_table_available",
        "Main Table 3": "table_source_available",
    }
    expected_required_paths = {
        "Main Figure 2": [
            "paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv",
            "scripts/paper10/plot_frontier_random050_figures.py",
        ],
        "Main Figure 3": [
            "paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json",
            "scripts/paper10/plot_frontier_random050_figures.py",
        ],
        "Main Figure 4": [
            "paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_family_summary_2026-06-10.csv",
            "scripts/paper10/plot_integrated_dongxing_figures.py",
        ],
        "Main Table 2": [
            "paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.md",
            "paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md",
            "paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.json",
        ],
    }
    expected_item_tokens = {
        "Main Table 2": [
            "Algorithm-readiness addendum records the current true-reward guard evidence",
            "setting-specific guard only; not final submission readiness",
        ],
    }
    for item_name in expected_items:
        row = by_item.get(item_name)
        if not isinstance(row, dict):
            continue
        if row.get("source_coverage_pass") is not True:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                f"{item_name}.source_coverage_pass={row.get('source_coverage_pass')}"
            )
        for key in ("missing_source_files", "missing_generation_scripts"):
            if row.get(key) != []:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                    f"{item_name}.{key}={row.get(key)}"
                )
        if row.get("generation_status") != expected_generation_status[item_name]:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                f"{item_name}.generation_status={row.get('generation_status')}"
            )
        row_paths = set(row.get("source_files", []) + row.get("generation_scripts", []))
        for required_path in expected_required_paths.get(item_name, []):
            if required_path not in row_paths:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                    f"{item_name}.{required_path}"
                )
        combined = " ".join(
            [
                " ".join(row.get("source_files", [])),
                " ".join(row.get("claim_boundaries", [])),
            ]
        )
        for token in expected_item_tokens.get(item_name, []):
            if token not in combined:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                    f"{item_name}.{token}"
                )

    blockers = payload.get("submission_blockers")
    if not isinstance(blockers, list) or len(blockers) < 4:
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: submission_blockers"
        )
    else:
        for token in (
            "final schematic artwork for Main Figure 1",
            "target-journal figure dimensions and export formats",
            "journal-specific captions and table placement",
        ):
            if token not in blockers:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON}: "
                    f"submission_blockers.{token}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            if "must not be used to claim" not in line and "is not supported" not in line:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD}:{line_no}: "
                    "positive 50-state wording"
                )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_figure_table_source_coverage_audit_current",
            False,
            "Paper10 figure/table source coverage audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_figure_table_source_coverage_audit_current",
        True,
        "Paper10 figure/table source coverage audit is current and bounded",
    )


def check_paper10_figure_table_caption_claim_packet_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD,
        PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON,
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        Path("README.md"),
        MANIFEST,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_figure_table_caption_claim_packet_current",
            False,
            "missing Paper10 figure/table caption-claim packet files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_figure_table_caption_claim_packet_current",
            False,
            f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    packet_name = PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD.name
    for rel_path in [
        Path("README.md"),
        MANIFEST,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
    ]:
        path = root / rel_path
        if packet_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {packet_name}")

    required_text_tokens = [
        "Paper10 figure/table caption-claim packet",
        "source-derived figure/table caption-claim packet",
        "journal-neutral draft captions",
        "does not add a new experimental claim",
        "No rollout was rerun",
        "caption-claim packet: PASS",
        "submission-ready figure/table package: NO",
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
        "target-journal caption length",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "diagnostic near-pass must not be pooled",
        "Algorithm-readiness addendum",
        "setting-specific guard only",
        "Do not treat the guard addendum as final submission readiness.",
        "Do not claim a universal fixed switch margin.",
        "paper10_geojepa_mpc.experiments.figure_table_caption_claim_packet",
    ]
    for token in required_text_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "source-derived figure/table caption-claim packet",
        ("caption_claim_packet_pass",): True,
        ("submission_ready",): False,
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        (
            "source_files",
            "source_coverage_audit_json",
        ): PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_JSON.as_posix(),
        (
            "source_files",
            "result_tables_freeze_json",
        ): PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON.as_posix(),
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    expected_items = [
        "Main Figure 1",
        "Main Figure 2",
        "Main Figure 3",
        "Main Figure 4",
        "Supplementary Figure S1",
        "Main Table 1",
        "Main Table 2",
        "Main Table 3",
    ]
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != len(expected_items):
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: items"
        )
        items = []
    observed_items = [row.get("item") for row in items if isinstance(row, dict)]
    if observed_items != expected_items:
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
            f"items={observed_items}"
        )

    by_item = {row.get("item"): row for row in items if isinstance(row, dict)}
    expected_artwork = {
        "Main Figure 1": "pending",
        "Main Figure 2": "preview_available",
        "Main Figure 3": "preview_available",
        "Main Figure 4": "preview_available",
        "Supplementary Figure S1": "preview_available",
        "Main Table 1": "preview_available",
        "Main Table 2": "preview_available",
        "Main Table 3": "preview_available",
    }
    required_item_tokens = {
        "Main Figure 1": ["workflow schematic only", "final schematic artwork"],
        "Main Figure 2": ["69.4705", "67.5437", "Bishan 20x16/top5"],
        "Main Figure 3": [
            "direct 50-state Bishan scale-up success",
            "diagnostic near-pass must not be pooled",
        ],
        "Main Figure 4": [
            "calibration",
            "robust Bishan-to-Dongxing transfer superiority",
        ],
        "Main Table 2": [
            "Table 1 is the only positive Bishan performance anchor",
            "Stage 3 rows are boundary evidence",
            "Algorithm-readiness addendum",
            "72.1918",
            "65.8876",
            "6.3041",
            "20 / 20",
            "4.1401",
            "7.7605",
            "setting-specific guard only",
            "Do not treat the guard addendum as final submission readiness.",
            "Do not claim a universal fixed switch margin.",
            "e0_paper10_true_reward_guard_readiness_2026-07-08.json",
        ],
        "Main Table 3": [
            "return-label scaling is descriptive calibration evidence",
            "robust Bishan-to-Dongxing transfer superiority",
        ],
    }
    for item_name in expected_items:
        row = by_item.get(item_name)
        if not isinstance(row, dict):
            continue
        if row.get("source_coverage_pass") is not True:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                f"{item_name}.source_coverage_pass={row.get('source_coverage_pass')}"
            )
        if row.get("final_artwork_status") != expected_artwork[item_name]:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                f"{item_name}.final_artwork_status={row.get('final_artwork_status')}"
            )
        for key in (
            "draft_caption",
            "allowed_claims",
            "forbidden_claims",
            "unresolved_manuscript_fields",
            "source_files",
        ):
            value = row.get(key)
            if value == "" or value == [] or value is None:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                    f"{item_name}.{key}"
                )
        unresolved = row.get("unresolved_manuscript_fields", [])
        if isinstance(unresolved, list) and len(unresolved) != len(set(unresolved)):
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                f"{item_name}.duplicate_unresolved_fields"
            )
        combined = " ".join(
            [
                str(row.get("draft_caption", "")),
                " ".join(row.get("allowed_claims", [])),
                " ".join(row.get("forbidden_claims", [])),
                " ".join(row.get("unresolved_manuscript_fields", [])),
                " ".join(row.get("source_files", [])),
            ]
        )
        for token in required_item_tokens.get(item_name, []):
            if token not in combined:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                    f"{item_name}.{token}"
                )

    blockers = payload.get("submission_blockers")
    if not isinstance(blockers, list) or len(blockers) < 4:
        missing_tokens.append(
            f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: submission_blockers"
        )
    else:
        for token in (
            "target-journal caption length",
            "final figure/table export package",
            "final schematic artwork for Main Figure 1",
            "final main-versus-supplementary placement",
        ):
            if token not in blockers:
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_JSON}: "
                    f"submission_blockers.{token}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    allowed_negative_context = (
        "do not",
        "must not",
        "not supported",
        "did not support",
        "boundary",
    )
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if forbidden_50_state.search(line):
            if not any(token in lowered for token in allowed_negative_context):
                missing_tokens.append(
                    f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD}:{line_no}: "
                    "positive 50-state wording"
                )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_figure_table_caption_claim_packet_current",
            False,
            "Paper10 figure/table caption-claim packet gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_figure_table_caption_claim_packet_current",
        True,
        "Paper10 figure/table caption-claim packet is current and bounded",
    )


def check_paper10_final_figure_table_export_package_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD,
        PAPER10_MAIN_FIGURE1_FINAL_SVG,
        PAPER10_MAIN_FIGURE1_FINAL_PDF,
        PAPER10_MAIN_FIGURE1_FINAL_PNG,
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
        PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        INTEGRATED_DONGXING_FIGURE_PLAN,
        SUBMISSION_BLOCKER_DECISION_PACKET,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_final_figure_table_export_package_current",
            False,
            "missing Paper10 final figure/table export package files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE)
    normalized_text = " ".join(text.split())
    missing_tokens = []
    required_tokens = [
        "Paper10 final figure/table export package",
        "frozen export contract",
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD.name,
        PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD.name,
        INTEGRATED_FIGURE_TABLE_NUMBERING_FREEZE.name,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT.name,
        INTEGRATED_DONGXING_FIGURE_PLAN.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "reviewer_outputs/",
        "e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md",
        "ceus_submission_assets/main_figure1_workflow/",
        "exported_final_candidate",
        "Do not change claim wording",
        "does not create new experimental evidence",
        "does not change the manuscript claim boundary",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE}: {token}"
            )

    expected_rows = {
        "Main Figure 1": "exported_final_candidate",
        "Main Figure 2": "export_ready",
        "Main Figure 3": "export_ready",
        "Main Figure 4": "export_ready",
        "Supplementary Figure S1": "export_ready",
        "Main Tables 1-3": "export_ready",
    }
    lines = text.splitlines()
    for item_name, expected_status in expected_rows.items():
        row_line = next(
            (line.strip() for line in lines if line.startswith(f"| {item_name} |")),
            None,
        )
        if row_line is None:
            missing_tokens.append(
                f"{PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE}: {item_name}"
            )
            continue
        if expected_status not in row_line:
            missing_tokens.append(
                f"{PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE}: "
                f"{item_name}.{expected_status}"
            )

    five_seed_export_token = (
        "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md/JSON"
    )
    for item_name in ("Main Figure 2", "Main Tables 1-3"):
        row_line = next(
            (line.strip() for line in lines if line.startswith(f"| {item_name} |")),
            "",
        )
        if five_seed_export_token not in row_line:
            missing_tokens.append(
                f"{PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE}: "
                f"{item_name} 5-seed export source"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_final_figure_table_export_package_current",
            False,
            "Paper10 final figure/table export package gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_final_figure_table_export_package_current",
        True,
        "Paper10 final figure/table export package is current and export-bounded",
    )

def check_paper10_archive_source_data_closeout_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD,
        PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON,
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD,
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON,
        PAPER10_MAIN_FIGURE1_FINAL_SVG,
        PAPER10_MAIN_FIGURE1_FINAL_PDF,
        PAPER10_MAIN_FIGURE1_FINAL_PNG,
        ARCHIVE_MANIFEST,
        ARCHIVE_METADATA_TEMPLATES,
        INTEGRATED_DONGXING_SOURCE_DATA_MAP,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
        PAPER10_FIGURE_TABLE_CAPTION_CLAIM_PACKET_MD,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD,
        PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD,
        PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_archive_source_data_closeout_current",
            False,
            "missing Paper10 archive/source-data closeout files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_archive_source_data_closeout_current",
            False,
            f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    normalized_text = " ".join(text.split())
    required_tokens = [
        "Paper10 archive source-data closeout",
        "Status: archive_source_data_closeout_prepared_not_submission_ready",
        "Record 1 public package",
        "FAIR and DataCite closeout",
        "DataCite fields prepared",
        "Main Figure 1",
        "exported_final_candidate",
        "e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md",
        "Supplementary Figure S1",
        "not_visible_on_platform",
        "confidential_no_external_access",
        "Apache-2.0",
        "CC0-1.0",
        "not final submission approval",
        "Formal submission remains blocked",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD}: {token}")

    expected_values = {
        ("artifact_type",): "paper10_archive_source_data_closeout",
        ("date",): "2026-07-09",
        ("status",): "archive_source_data_closeout_prepared_not_submission_ready",
        ("target_journal",): "Computers, Environment and Urban Systems",
        ("source_boundary", "git_commit_scanned"): "3df9429fb8785539020aa7c7dbce1c925ca18d9b",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("record1_public_package", "code_licence"): "Apache-2.0",
        ("record1_public_package", "generated_non_dltb_rights"): "CC0-1.0",
        ("record1_public_package", "source_data_map_current"): True,
        ("record1_public_package", "main_figure1_final_artwork_closeout"): "paper10_geojepa_mpc/experiments/results/e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md",
        ("record1_public_package", "archive_metadata_templates_current"): True,
        ("record1_public_package", "record1_has_code_tests_smoke_data_outputs_tables_checkpoints_metadata"): True,
        ("record1_public_package", "record1_excludes_original_bishan_dltb"): True,
        ("record1_public_package", "record1_excludes_original_dongxing_dltb"): True,
        ("figure_table_source_data_alignment", "main_figure_1"): "final artwork candidate exported; SVG/PDF/PNG tracked; journal file-format confirmation remains open",
        ("figure_table_source_data_alignment", "caption_claim_packet_current"): True,
        ("figure_table_source_data_alignment", "source_coverage_audit_current"): True,
        ("figure_table_source_data_alignment", "numbering_freeze_current"): True,
        ("figure_table_source_data_alignment", "main_figure1_final_artwork_closeout_current"): True,
        ("fair_metadata_audit", "record1_has_public_metadata"): True,
        ("fair_metadata_audit", "data_cite_fields_prepared"): True,
        ("fair_metadata_audit", "identifier_or_reviewer_link_recorded"): True,
        ("fair_metadata_audit", "licence_or_rights_terms_recorded"): True,
        ("fair_metadata_audit", "source_data_to_figures_and_tables_mapped"): True,
        ("fair_metadata_audit", "restricted_raw_dltb_boundary_recorded"): True,
        ("fair_metadata_audit", "original_dltb_not_relicensed"): True,
        ("fair_metadata_audit", "public_record_metadata_can_remain_public_if_raw_dltb_restricted"): True,
        ("resolved_submission_fields", "main_figure_1_final_artwork"): "exported_final_candidate",
        ("unresolved_submission_fields", "target_journal_editor_acceptance"): "not_recorded",
        ("unresolved_submission_fields", "exact_4open_snapshot_identifier"): "not_visible_on_platform",
        ("unresolved_submission_fields", "final_public_archive_identifier"): "anonymous_readme_direct_link_only",
        ("unresolved_submission_fields", "final_journal_dimensions_and_file_formats"): "not_finalized",
        ("unresolved_submission_fields", "final_declarations"): "pending_author_decision",
        ("submission_gate", "formal_submission_blocked"): True,
        ("submission_gate", "preflight_pass_does_not_mean_submission_ready"): True,
        ("claim_locks", "archive_source_data_closeout_prepared"): True,
        ("claim_locks", "record1_public_metadata_aligned"): True,
        ("claim_locks", "main_figure_1_artwork_candidate_exported"): True,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("claim_locks", "main_figure_1_artwork_complete"): True,
        ("claim_locks", "target_journal_acceptance_recorded"): False,
        ("claim_locks", "exact_4open_snapshot_identifier_backfilled"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    if payload.get("status") == "submission_ready":
        missing_tokens.append(
            f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: not final submission approval"
        )
    if nested_value(payload, ("submission_gate", "formal_submission_blocked")) is not True:
        missing_tokens.append(
            f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: not final submission approval"
        )

    required_before = payload.get("required_before_formal_submission")
    if not isinstance(required_before, list) or len(required_before) < 5:
        missing_tokens.append(
            f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: required_before_formal_submission"
        )
    else:
        for token in (
            "Main Figure 1",
            "CEUS/editor acceptance",
            "visible-snapshot limitation",
            "final public archive identifier",
            "declarations",
        ):
            if not any(token in item for item in required_before):
                missing_tokens.append(
                    f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_JSON}: required_before_formal_submission missing {token}"
                )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_ARCHIVE_SOURCE_DATA_CLOSEOUT_MD}:{line_no}: {line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_archive_source_data_closeout_current",
            False,
            "forbidden archive/source-data closeout wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_archive_source_data_closeout_current",
            False,
            "Paper10 archive/source-data closeout gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_archive_source_data_closeout_current",
        True,
        "Paper10 archive/source-data closeout is current and no-go guarded",
    )



def check_paper10_main_figure1_final_artwork_closeout_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD,
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON,
        PAPER10_MAIN_FIGURE1_FINAL_SVG,
        PAPER10_MAIN_FIGURE1_FINAL_PDF,
        PAPER10_MAIN_FIGURE1_FINAL_PNG,
        Path("scripts") / "paper10" / "plot_main_figure1_workflow.py",
        RESULTS / "e0_paper10_main_figure1_artwork_preview_2026-06-27.md",
        PAPER10_FIGURE_TABLE_SOURCE_COVERAGE_AUDIT_MD,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_main_figure1_final_artwork_closeout_current",
            False,
            "missing Paper10 Main Figure 1 final artwork closeout files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_main_figure1_final_artwork_closeout_current",
            False,
            f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: invalid JSON: {exc}",
        )

    svg_text = read_text(root / PAPER10_MAIN_FIGURE1_FINAL_SVG)
    normalized_text = " ".join(text.split())
    missing_tokens = []
    required_tokens = [
        "Paper10 Main Figure 1 final artwork closeout",
        "Status: final_artwork_candidate_exported_not_submission_ready",
        "Backend: Python/matplotlib",
        "workflow artwork, not a new experiment",
        "exported_final_candidate",
        "supersedes the earlier `pending_artwork` status for Main Figure 1 only",
        "Formal submission remains blocked",
        "not final submission approval",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_MD}: {token}"
            )

    expected_values = {
        ("artifact_type",): "paper10_main_figure1_final_artwork_closeout",
        ("date",): "2026-07-09",
        ("status",): "final_artwork_candidate_exported_not_submission_ready",
        ("target_journal",): "Computers, Environment and Urban Systems",
        ("backend",): "python_matplotlib",
        ("variant",): "final",
        ("source_boundary", "script"): "scripts/paper10/plot_main_figure1_workflow.py",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "claim_boundary_changed"): False,
        ("source_boundary", "submission_approval"): False,
        ("assets", "svg"): PAPER10_MAIN_FIGURE1_FINAL_SVG.as_posix(),
        ("assets", "pdf"): PAPER10_MAIN_FIGURE1_FINAL_PDF.as_posix(),
        ("assets", "png"): PAPER10_MAIN_FIGURE1_FINAL_PNG.as_posix(),
        ("asset_qa", "png_size"): [3870, 1968],
        ("asset_qa", "png_non_white_bbox"): [115, 199, 3806, 1776],
        ("asset_qa", "preview_title_removed"): True,
        ("asset_qa", "source_footer_removed"): True,
        ("asset_qa", "svg_contains_final_reporting_note"): True,
        ("asset_qa", "panel_labels_lowercase"): True,
        ("asset_qa", "caption_title_externalized"): True,
        ("asset_qa", "python_backend_exclusive"): True,
        ("claim_locks", "main_figure_1_artwork_candidate_exported"): True,
        ("claim_locks", "supersedes_pending_artwork_for_main_figure_1"): True,
        ("claim_locks", "new_experimental_evidence_created"): False,
        ("claim_locks", "claim_boundary_changed"): False,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("unresolved_submission_fields", "target_journal_editor_acceptance"): "not_recorded",
        ("unresolved_submission_fields", "exact_4open_snapshot_identifier"): "not_visible_on_platform",
        ("unresolved_submission_fields", "final_public_archive_identifier"): "anonymous_readme_direct_link_only",
        ("unresolved_submission_fields", "final_journal_dimensions_and_file_formats"): "not_finalized",
        ("unresolved_submission_fields", "final_declarations"): "pending_author_decision",
        ("submission_gate", "formal_submission_blocked"): True,
        ("submission_gate", "preflight_pass_does_not_mean_submission_ready"): True,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    byte_expectations = {
        "svg_bytes": PAPER10_MAIN_FIGURE1_FINAL_SVG,
        "pdf_bytes": PAPER10_MAIN_FIGURE1_FINAL_PDF,
        "png_bytes": PAPER10_MAIN_FIGURE1_FINAL_PNG,
    }
    for key, rel_path in byte_expectations.items():
        observed = nested_value(payload, ("asset_qa", key))
        actual = (root / rel_path).stat().st_size
        if observed != actual:
            missing_tokens.append(
                f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: "
                f"asset_qa.{key}={observed}, actual={actual}"
            )

    required_svg_tokens = [
        "Constrained task",
        "Monitor gate",
        "decision=continue",
        "Stop as diagnostics",
        "No training on failed labels",
        "selector=value_filter",
        "workflow artwork, not a new experiment",
    ]
    for token in required_svg_tokens:
        if token not in svg_text:
            missing_tokens.append(f"{PAPER10_MAIN_FIGURE1_FINAL_SVG}: {token}")

    forbidden_svg_tokens = [
        "Monitor-gated GeoJEPA-MPC value filtering workflow",
        "Only monitor-passing labels train the value head",
        "Source modules:",
        ">1a<",
    ]
    for token in forbidden_svg_tokens:
        if token in svg_text:
            missing_tokens.append(
                f"{PAPER10_MAIN_FIGURE1_FINAL_SVG}: preview-only text {token}"
            )

    if "<dc:date>2026-07-09</dc:date>" not in svg_text:
        missing_tokens.append(
            f"{PAPER10_MAIN_FIGURE1_FINAL_SVG}: deterministic SVG date metadata"
        )
    if any(line != line.rstrip() for line in svg_text.splitlines()):
        missing_tokens.append(
            f"{PAPER10_MAIN_FIGURE1_FINAL_SVG}: SVG trailing whitespace"
        )

    if payload.get("status") == "submission_ready":
        missing_tokens.append(
            f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: not final submission approval"
        )
    if nested_value(payload, ("submission_gate", "formal_submission_blocked")) is not True:
        missing_tokens.append(
            f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: not final submission approval"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_main_figure1_final_artwork_closeout_current",
            False,
            "Paper10 Main Figure 1 final artwork closeout gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_main_figure1_final_artwork_closeout_current",
        True,
        "Paper10 Main Figure 1 final artwork closeout is current and no-go guarded",
    )



def check_paper10_ceus_submission_policy_verification_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD,
        PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON,
        PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
        PAPER10_CEUS_HIGHLIGHTS,
        PAPER10_MAIN_FIGURE1_FINAL_PDF,
        PAPER10_MAIN_FIGURE1_FINAL_PNG,
        PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_submission_policy_verification_current",
            False,
            "missing Paper10 CEUS submission policy verification files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD)
    clean_text = read_text(root / PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT)
    try:
        payload = json.loads(
            read_text(root / PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON)
        )
        figure1_payload = json.loads(
            read_text(root / PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_ceus_submission_policy_verification_current",
            False,
            f"invalid JSON: {exc}",
        )

    missing_tokens = []
    required_text_tokens = [
        "Status: ceus_policy_verified_submission_packet_ready",
        "Computers, Environment and Urban Systems",
        "Research Data Policy Option B",
        "does not require pre-submission editor acceptance",
        "3870 px wide PNG",
        "remaining author actions are submission-system fields",
    ]
    normalized_text = " ".join(text.split())
    for token in required_text_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_MD}: {token}"
            )

    expected_values = {
        ("artifact_type",): "paper10_ceus_submission_policy_verification",
        ("date",): "2026-07-09",
        ("status",): "ceus_policy_verified_submission_packet_ready",
        ("target_journal",): "Computers, Environment and Urban Systems",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "author_decisions_invented"): False,
        ("source_boundary", "policy_verification_only"): True,
        ("policy_findings", "research_data_policy_label"): "Option B",
        ("policy_findings", "data_deposit_encouraged_not_absolute"): True,
        ("policy_findings", "editor_preacceptance_required_for_restricted_dltb"): False,
        ("policy_findings", "data_statement_can_disclose_no_external_raw_dltb"): True,
        ("policy_findings", "exact_4open_snapshot_identifier_required_by_ceus_before_submission"): False,
        ("policy_findings", "reviewer_readme_direct_link_author_confirmed"): True,
        ("policy_findings", "figure1_pdf_vector_available"): True,
        ("policy_findings", "figure1_png_width_px"): 3870,
        ("policy_findings", "figure1_png_height_px"): 1968,
        ("policy_findings", "figure1_png_meets_elsevier_combination_fullpage_width_px"): True,
        ("policy_findings", "highlights_count"): 5,
        ("policy_findings", "highlights_each_under_85_chars"): True,
        ("policy_findings", "double_anonymous_title_page_separation_required"): True,
        ("policy_findings", "title_page_separation_prepared"): True,
        ("submission_packet_decision", "algorithm_model_experiments_complete_for_bounded_ceus_submission"): True,
        ("submission_packet_decision", "archive_and_source_data_package_complete_for_bounded_ceus_submission"): True,
        ("submission_packet_decision", "main_figure1_artwork_complete_for_ceus_submission"): True,
        ("submission_packet_decision", "formal_submission_not_blocked_by_external_policy_verification"): True,
        ("submission_packet_decision", "current_submission_status"): "ready_for_author_upload_and_submission_system_fields",
        ("remaining_submission_system_fields", "author_declarations"): "fill_in_submission_system",
        ("claim_locks", "ceus_policy_blockers_closed"): True,
        ("claim_locks", "confidential_raw_dltb_disclosure_ready"): True,
        ("claim_locks", "final_submission_readiness_supported"): True,
        ("claim_locks", "new_experimental_evidence_created"): False,
        ("claim_locks", "claim_boundary_changed"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    if nested_value(payload, ("official_sources_checked", "ceus_guide_for_authors")) != (
        "https://www.elsevier.com/journals/"
        "computers-environment-and-urban-systems/0198-9715/guide-for-authors"
    ):
        missing_tokens.append(
            f"{PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON}: CEUS guide URL"
        )
    if nested_value(payload, ("policy_findings", "reviewer_readme_direct_link")) != (
        "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md"
    ):
        missing_tokens.append(
            f"{PAPER10_CEUS_SUBMISSION_POLICY_VERIFICATION_JSON}: reviewer README link"
        )

    figure1_size = nested_value(figure1_payload, ("asset_qa", "png_size"))
    if figure1_size != [3870, 1968]:
        missing_tokens.append(
            f"{PAPER10_MAIN_FIGURE1_FINAL_ARTWORK_CLOSEOUT_JSON}: png_size={figure1_size}"
        )
    if (root / PAPER10_MAIN_FIGURE1_FINAL_PDF).stat().st_size <= 0:
        missing_tokens.append(f"{PAPER10_MAIN_FIGURE1_FINAL_PDF}: empty PDF")
    if (root / PAPER10_MAIN_FIGURE1_FINAL_PNG).stat().st_size <= 0:
        missing_tokens.append(f"{PAPER10_MAIN_FIGURE1_FINAL_PNG}: empty PNG")

    highlights = [
        line.strip()
        for line in read_text(root / PAPER10_CEUS_HIGHLIGHTS).splitlines()
        if line.strip()
    ]
    if len(highlights) != 5:
        missing_tokens.append(f"{PAPER10_CEUS_HIGHLIGHTS}: highlight count={len(highlights)}")
    too_long = [line for line in highlights if len(line) > 85]
    if too_long:
        missing_tokens.append(f"{PAPER10_CEUS_HIGHLIGHTS}: over 85 chars")

    required_clean_tokens = [
        "Article type: Research Article candidate for Computers, Environment and Urban Systems.",
        "CEUS/Elsevier Research Data Policy Option B",
        "does not require pre-submission editor acceptance",
        "suitable for formal CEUS submission as a bounded manuscript package",
    ]
    for token in required_clean_tokens:
        if token not in clean_text:
            missing_tokens.append(f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: {token}")
    forbidden_clean_tokens = [
        "Computers and Electronics in Agriculture",
        "target-journal/editor acceptance is not recorded",
        "The target journal must accept this confidential raw-DLTB limitation",
        "not suitable as a final submission package until",
    ]
    for token in forbidden_clean_tokens:
        if token in clean_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: outdated blocker {token}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_submission_policy_verification_current",
            False,
            "Paper10 CEUS submission policy verification gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_submission_policy_verification_current",
        True,
        "Paper10 CEUS submission policy blockers are verified closed for bounded submission",
    )
def check_paper10_submission_readiness_boundary_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
        PAPER10_FORMAL_MANUSCRIPT_DRAFT,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
        PAPER10_BOUNDED_MANUSCRIPT_ASSEMBLY_DRAFT,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON,
        PAPER10_MECHANISM_ABLATION_PACKET_MD,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "missing Paper10 submission readiness boundary files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_SUBMISSION_READINESS_BOUNDARY)
    normalized_text = " ".join(text.split())
    missing_tokens = []
    required_tokens = [
        "Paper10 submission-readiness boundary",
        "Status: not_submission_ready",
        "Preflight passing does not mean final submission readiness",
        PAPER10_FORMAL_MANUSCRIPT_DRAFT.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
        PAPER10_MECHANISM_ABLATION_PACKET_MD.name,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD.name,
        PAPER10_STAGE3_50X24_CANDIDATE_SCORE_SWEEP_MD.name,
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data rights and checkpoint or model-weight rights",
        "full Bishan Tool2 data access route",
        "GPKG-root geospatial input access route",
        "Dongxing/Neijiang prepared-data access route",
        "citation policy for local-only sources, preprints, and final reference style",
        "statistical reporting policy for descriptive results versus hypothesis tests",
        "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
        "5-seed figure/table source routing is locked",
        "bounded assembly routes Main Figure 2 and Main Table 2 through the 5-seed confirmatory audit",
        "final export package routes Main Figure 2 and Main Tables 1-3 through the 5-seed confirmatory audit",
        "does not close Main Figure 1 artwork",
        "does not close repository DOI, licence, full-data access, citation, statistical-reporting, or journal-specific export blockers",
        "Do not claim direct 50-state Bishan scale-up success",
        "Do not claim robust Bishan-to-Dongxing transfer superiority",
        "Do not claim solved irregular cadastral parcel deployment",
        "Do not claim a full Constrained MDP, CPO, or RCPO solver",
        "Do not claim Paper10 invented GeoJEPA",
        "does not mean the paper is ready to submit",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_SUBMISSION_READINESS_BOUNDARY}: {token}"
            )

    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        if PAPER10_SUBMISSION_READINESS_BOUNDARY.name not in read_text(root / doc):
            missing_tokens.append(f"{doc}: {PAPER10_SUBMISSION_READINESS_BOUNDARY.name}")

    hits = []
    paragraph_start = None
    paragraph_lines = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped:
            if paragraph_start is None:
                paragraph_start = line_no
            paragraph_lines.append(stripped)
            continue
        if paragraph_lines:
            paragraph = " ".join(paragraph_lines)
            if is_submission_readiness_positive_claim(paragraph):
                hits.append(
                    f"{PAPER10_SUBMISSION_READINESS_BOUNDARY}:{paragraph_start}: {paragraph}"
                )
            paragraph_start = None
            paragraph_lines = []
    if paragraph_lines:
        paragraph = " ".join(paragraph_lines)
        if is_submission_readiness_positive_claim(paragraph):
            hits.append(
                f"{PAPER10_SUBMISSION_READINESS_BOUNDARY}:{paragraph_start}: {paragraph}"
            )
    if hits:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "forbidden submission-readiness wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_submission_readiness_boundary_current",
            False,
            "Paper10 submission readiness boundary gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_submission_readiness_boundary_current",
        True,
        "Paper10 submission-readiness boundary is current and no-go guarded",
    )

def check_paper10_real_data_availability_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_data_availability_audit_current",
            False,
            "missing Paper10 real-data availability audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_data_availability_audit_current",
            False,
            f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 real-data availability audit",
        "external-dependency audit",
        "not a data-rights approval",
        "raw geospatial data are not copied into Git",
        "Full Bishan Tool2 arrays",
        "Bishan slope-enriched geospatial root",
        "Bishan prepared block and township inputs",
        "Dongxing/Neijiang primary prepared-results directory",
        "Dongxing/Neijiang alternate prepared-results directory",
        "Dongxing/Neijiang local prepared-results directory",
        "Full Bishan Tool2 access route",
        "GPKG-root geospatial input route",
        "Dongxing/Neijiang prepared-data route",
        "paper10_geojepa_mpc.experiments.real_data_availability_audit",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD}: {token}"
            )

    expected_family_ids = {
        "bishan_tool2_full",
        "bishan_gpkg_root",
        "bishan_rollout_inputs",
        "dongxing_cloud_primary",
        "dongxing_cloud_alternate",
        "dongxing_local_candidate",
    }
    families = payload.get("families")
    if not isinstance(families, list):
        missing_tokens.append(f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: families")
        families = []
    observed_ids = {row.get("family_id") for row in families if isinstance(row, dict)}
    for family_id in sorted(expected_family_ids - observed_ids):
        missing_tokens.append(
            f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: {family_id}"
        )

    summary = payload.get("summary", {})
    for key in ("available", "partial", "missing"):
        if key not in summary:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: summary.{key}"
            )

    for row in families:
        if not isinstance(row, dict):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: non-dict family row"
            )
            continue
        for key in (
            "status",
            "required_count",
            "present_required_count",
            "file_count_present",
            "bytes_present",
            "missing_required_paths",
            "claim_dependency",
            "manuscript_blocker",
            "external_to_git",
        ):
            if key not in row:
                missing_tokens.append(
                    f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: "
                    f"{row.get('family_id', '<unknown>')}.{key}"
                )
        if row.get("status") not in {"available", "partial", "missing"}:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: "
                f"{row.get('family_id', '<unknown>')}.status={row.get('status')}"
            )
        if row.get("external_to_git") is not True:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON}: "
                f"{row.get('family_id', '<unknown>')}.external_to_git"
            )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_data_availability_audit_current",
            False,
            "Paper10 real-data availability audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_data_availability_audit_current",
        True,
        "Paper10 real-data availability audit is current and bounded",
    )


def check_paper10_real_data_integrity_smoke_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
        PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON,
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_JSON,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_data_integrity_smoke_current",
            False,
            "missing Paper10 real-data integrity smoke files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_data_integrity_smoke_current",
            False,
            f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    smoke_name = PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if smoke_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {smoke_name}")

    required_tokens = [
        "Paper10 real-data integrity smoke",
        "metadata-only smoke audit",
        "NPZ header smoke",
        "GeoPackage metadata smoke",
        "Directory smoke",
        "JSON schema smoke",
        "raw row values are not exported",
        "D:\\test\\tool2\\transitions.npz",
        "D:\\test\\tool2\\pairwise.npz",
        "D:\\test\\dem_slope_analysis\\output\\DLTB_with_slope.gpkg",
        "D:\\test\\results_real\\blocks",
        "D:\\test\\townships.json",
        "paper10_geojepa_mpc.experiments.real_data_integrity_smoke",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD}: {token}")

    for group in ("npz", "geopackage", "directories", "json"):
        rows = payload.get(group)
        if not isinstance(rows, list):
            missing_tokens.append(f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: {group}")
            continue
        if not rows:
            missing_tokens.append(f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: empty {group}")

    expected_npz = {
        "D:\\test\\tool2\\transitions.npz": {
            "block_features",
            "global_features",
            "actions",
            "rewards",
            "next_block_features",
            "next_global_features",
        },
        "D:\\test\\tool2\\pairwise.npz": {
            "states_bf",
            "states_gf",
            "actions",
            "rewards",
        },
    }
    npz_by_path = {
        row.get("path"): row
        for row in payload.get("npz", [])
        if isinstance(row, dict)
    }
    for path, expected_arrays in expected_npz.items():
        row = npz_by_path.get(path)
        if row is None:
            missing_tokens.append(f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: {path}")
            continue
        if row.get("status") != "readable":
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: {path}.status"
            )
        observed_arrays = set((row.get("arrays") or {}).keys())
        for array_name in sorted(expected_arrays - observed_arrays):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: {path}.{array_name}"
            )

    gpkg_rows = payload.get("geopackage", [])
    if gpkg_rows:
        gpkg = gpkg_rows[0]
        if gpkg.get("status") != "readable":
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: geopackage status"
            )
        contents = gpkg.get("contents", [])
        if not any(row.get("table_name") == "DLTB" for row in contents):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: DLTB contents"
            )
        geometry = gpkg.get("geometry_columns", [])
        if not any(row.get("geometry_type_name") == "MULTIPOLYGON" for row in geometry):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: MULTIPOLYGON geometry"
            )

    summary = payload.get("summary", {})
    if int(summary.get("readable", 0)) < 4:
        missing_tokens.append(
            f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_JSON}: summary.readable"
        )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_data_integrity_smoke_current",
            False,
            "Paper10 real-data integrity smoke gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_data_integrity_smoke_current",
        True,
        "Paper10 real-data integrity smoke is current and metadata-only",
    )


def check_paper10_real_env_smoke_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_ENV_SMOKE_MD,
        PAPER10_REAL_ENV_SMOKE_JSON,
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
        PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_env_smoke_current",
            False,
            "missing Paper10 real-environment smoke files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_ENV_SMOKE_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_REAL_ENV_SMOKE_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_env_smoke_current",
            False,
            f"{PAPER10_REAL_ENV_SMOKE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    smoke_name = PAPER10_REAL_ENV_SMOKE_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if smoke_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {smoke_name}")

    required_tokens = [
        "Paper10 real-environment rollout smoke",
        "not a planning-quality result",
        "not evidence for a new planning-quality or scale-up claim",
        "CountyLevelEnv.step",
        "reviewer_outputs\\paper10_real_env_smoke_5step_h3_k20_seed0.json",
        "paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke",
        "| total reward | 7.6466 |",
        "| min executable-valid actions | 2313 |",
        "| positive reward steps | 5 |",
        "| negative reward steps | 0 |",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(f"{PAPER10_REAL_ENV_SMOKE_MD}: {token}")

    expected_values = {
        ("date",): "2026-06-18",
        ("configuration", "prepared_dir"): "D:\\test",
        ("configuration", "mask_mode"): "executable",
        ("configuration", "env_source"): "paper9",
        ("configuration", "horizon"): 3,
        ("configuration", "top_k"): 20,
        ("configuration", "rollout_steps"): 5,
        ("configuration", "selector"): "paper9",
        ("outcome", "steps_run"): 5,
        ("outcome", "min_base_valid"): 2381,
        ("outcome", "min_executable_valid"): 2313,
        ("outcome", "positive_reward_steps"): 5,
        ("outcome", "negative_reward_steps"): 0,
        ("outcome", "terminated"): False,
        ("outcome", "truncated"): False,
        ("raw_output",): "reviewer_outputs\\paper10_real_env_smoke_5step_h3_k20_seed0.json",
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_SMOKE_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    outcome = payload.get("outcome", {})
    total_reward = outcome.get("total_reward")
    if not isinstance(total_reward, (int, float)) or abs(
        float(total_reward) - 7.646638186195446
    ) > 1e-9:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_SMOKE_JSON}: outcome.total_reward={total_reward}"
        )

    final_metrics = payload.get("final_metrics", {})
    expected_final_metrics = {
        "slope_change_pct": -0.07470047209533646,
        "cont_change": 0.0016273806799396162,
        "baimu_area_change_ha": -7.826418488866091,
    }
    for key, expected in expected_final_metrics.items():
        value = final_metrics.get(key)
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-12:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_JSON}: final_metrics.{key}={value}"
            )

    steps = payload.get("steps")
    if not isinstance(steps, list):
        missing_tokens.append(f"{PAPER10_REAL_ENV_SMOKE_JSON}: steps")
        steps = []
    if len(steps) != 5:
        missing_tokens.append(f"{PAPER10_REAL_ENV_SMOKE_JSON}: len(steps)={len(steps)}")
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_JSON}: step {index} non-dict"
            )
            continue
        if step.get("step") != index:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_JSON}: step {index} index"
            )
        for key in (
            "action",
            "reward",
            "n_base_valid",
            "n_executable_valid",
            "n_candidates",
            "completed_swaps",
            "select_time_sec",
            "slope_change_pct",
            "cont_change",
            "baimu_area_change_ha",
        ):
            if key not in step:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_SMOKE_JSON}: step {index}.{key}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_env_smoke_current",
            False,
            "Paper10 real-environment smoke gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_env_smoke_current",
        True,
        "Paper10 real-environment smoke is current, executable, and claim-bounded",
    )


def check_paper10_real_env_value_filter_smoke_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
        PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON,
        PAPER10_REAL_ENV_SMOKE_MD,
        PAPER10_REAL_DATA_AVAILABILITY_AUDIT_MD,
        PAPER10_REAL_DATA_INTEGRITY_SMOKE_MD,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_env_value_filter_smoke_current",
            False,
            "missing Paper10 real-environment value-filter smoke files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_env_value_filter_smoke_current",
            False,
            f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    smoke_name = PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if smoke_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {smoke_name}")

    required_tokens = [
        "Paper10 real-environment rollout smoke",
        "not a planning-quality result",
        "not evidence for a new planning-quality or scale-up claim",
        "not short-horizon performance evidence",
        "negative reward step",
        "CountyLevelEnv.step",
        "reviewer_outputs\\paper10_real_env_value_filter_smoke_5step_h5_k50_seed0.json",
        "paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke",
        "| selector | `value_filter` |",
        "| candidate_score_mode | `blend` |",
        "| candidate_value_weight | `0.1` |",
        "| total reward | 2.4254 |",
        "| min executable-valid actions | 2312 |",
        "| positive reward steps | 4 |",
        "| negative reward steps | 1 |",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("configuration", "prepared_dir"): "D:\\test",
        ("configuration", "mask_mode"): "executable",
        ("configuration", "env_source"): "paper9",
        ("configuration", "horizon"): 5,
        ("configuration", "top_k"): 50,
        ("configuration", "n_rollouts"): 1,
        ("configuration", "rollout_steps"): 5,
        ("configuration", "selector"): "value_filter",
        ("configuration", "candidate_score_mode"): "blend",
        ("configuration", "candidate_value_weight"): 0.1,
        ("configuration", "random_continuation_mode"): "independent",
        ("configuration", "stable_candidate_order"): False,
        ("outcome", "steps_run"): 5,
        ("outcome", "min_base_valid"): 2381,
        ("outcome", "min_executable_valid"): 2312,
        ("outcome", "positive_reward_steps"): 4,
        ("outcome", "negative_reward_steps"): 1,
        ("outcome", "terminated"): False,
        ("outcome", "truncated"): False,
        ("raw_output",): "reviewer_outputs\\paper10_real_env_value_filter_smoke_5step_h5_k50_seed0.json",
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    outcome = payload.get("outcome", {})
    total_reward = outcome.get("total_reward")
    if not isinstance(total_reward, (int, float)) or abs(
        float(total_reward) - 2.4253884392585983
    ) > 1e-9:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: "
            f"outcome.total_reward={total_reward}"
        )

    final_metrics = payload.get("final_metrics", {})
    expected_final_metrics = {
        "slope_change_pct": -0.10330620803581785,
        "cont_change": 0.0007628346937216257,
        "baimu_area_change_ha": -24.969707818043233,
    }
    for key, expected in expected_final_metrics.items():
        value = final_metrics.get(key)
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-12:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: "
                f"final_metrics.{key}={value}"
            )

    steps = payload.get("steps")
    if not isinstance(steps, list):
        missing_tokens.append(f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: steps")
        steps = []
    if len(steps) != 5:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: len(steps)={len(steps)}"
        )
    if steps:
        rewards = [
            step.get("reward")
            for step in steps
            if isinstance(step, dict) and isinstance(step.get("reward"), (int, float))
        ]
        if not any(float(reward) < 0.0 for reward in rewards):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: negative step reward"
            )
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: step {index} non-dict"
            )
            continue
        if step.get("step") != index:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: step {index} index"
            )
        for key in (
            "action",
            "reward",
            "n_base_valid",
            "n_executable_valid",
            "n_candidates",
            "completed_swaps",
            "select_time_sec",
            "slope_change_pct",
            "cont_change",
            "baimu_area_change_ha",
        ):
            if key not in step:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON}: step {index}.{key}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_env_value_filter_smoke_current",
            False,
            "Paper10 real-environment value-filter smoke gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_env_value_filter_smoke_current",
        True,
        "Paper10 real-environment value-filter smoke is current and claim-bounded",
    )


def check_paper10_real_env_smoke_boundary_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD,
        PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON,
        PAPER10_REAL_ENV_SMOKE_MD,
        PAPER10_REAL_ENV_SMOKE_JSON,
        PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_MD,
        PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_env_smoke_boundary_audit_current",
            False,
            "missing Paper10 real-environment smoke boundary audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_env_smoke_boundary_audit_current",
            False,
            f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 real-environment smoke boundary audit",
        "not a planning-quality result",
        "not a short-horizon performance comparison",
        "different checkpoint, selector, horizon, and top_k settings",
        "value-filter run includes one negative reward step",
        "| paper9_selector | `paper9` | 3 | 20 | 5 | 7.6466 | 5 | 0 | 2313 |",
        "| value_filter_selector | `value_filter` | 5 | 50 | 5 | 2.4254 | 4 | 1 | 2312 |",
        PAPER10_REAL_ENV_SMOKE_JSON.name,
        PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON.name,
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "execution-chain boundary audit",
        ("comparability", "performance_comparison_valid"): False,
        ("comparability", "planning_quality_result"): False,
        ("comparability", "short_horizon_performance_comparison"): False,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    comparability = payload.get("comparability", {})
    different_fields = comparability.get("different_fields", [])
    for field in (
        "checkpoint",
        "selector",
        "horizon",
        "top_k",
        "candidate_score_mode",
        "candidate_value_weight",
    ):
        if field not in different_fields:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                f"comparability.different_fields missing {field}"
            )

    reasons = comparability.get("reasons", [])
    for reason in (
        "different checkpoint, selector, horizon, and top_k settings",
        "single seed and five executed steps",
        "value-filter run includes one negative reward step",
    ):
        if reason not in reasons:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                f"comparability.reasons missing {reason}"
            )

    smokes = payload.get("smokes")
    if not isinstance(smokes, list) or len(smokes) != 2:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
            f"len(smokes)={len(smokes) if isinstance(smokes, list) else 'non-list'}"
        )
        smokes = []
    by_name = {
        smoke.get("name"): smoke
        for smoke in smokes
        if isinstance(smoke, dict) and smoke.get("name")
    }
    expected_smokes = {
        "paper9_selector": {
            "selector": "paper9",
            "horizon": 3,
            "top_k": 20,
            "steps_run": 5,
            "positive_reward_steps": 5,
            "negative_reward_steps": 0,
            "min_executable_valid": 2313,
            "total_reward": 7.646638186195446,
            "source_report": str(PAPER10_REAL_ENV_SMOKE_JSON),
        },
        "value_filter_selector": {
            "selector": "value_filter",
            "horizon": 5,
            "top_k": 50,
            "steps_run": 5,
            "positive_reward_steps": 4,
            "negative_reward_steps": 1,
            "min_executable_valid": 2312,
            "total_reward": 2.4253884392585983,
            "source_report": str(PAPER10_REAL_ENV_VALUE_FILTER_SMOKE_JSON),
        },
    }
    for name, expectations in expected_smokes.items():
        smoke = by_name.get(name)
        if smoke is None:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: smokes.{name}"
            )
            continue
        for key, expected in expectations.items():
            value = smoke.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(
                    float(value) - expected
                ) > 1e-9:
                    missing_tokens.append(
                        f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                        f"smokes.{name}.{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_JSON}: "
                    f"smokes.{name}.{key}={value}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_SMOKE_BOUNDARY_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_env_smoke_boundary_audit_current",
            False,
            "Paper10 real-environment smoke boundary audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_env_smoke_boundary_audit_current",
        True,
        "Paper10 real-environment smoke boundary audit is current and claim-bounded",
    )



def check_paper10_real_env_longhorizon_pilot_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_REALDATA_LONGHORIZON_PROTOCOL,
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_env_longhorizon_pilot_audit_current",
            False,
            "missing Paper10 real-environment long-horizon pilot audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_env_longhorizon_pilot_audit_current",
            False,
            f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("REPRODUCIBILITY.md"),
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 real-data long-horizon seed0 pilot audit",
        "not final planning-quality evidence",
        "value-filter superiority is not supported",
        "matched seeds `0-4`",
        "| total reward | 70.9543 | 67.7135 | -3.2408 |",
        "| first action divergence step | 9 |",
        "No inferential statistics or significance claims are introduced.",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-27",
        ("status",): "locked seed0 long-horizon pilot audit",
        ("source_boundary", "reran_rollouts"): False,
        ("evidence_boundary", "planning_quality_result"): False,
        ("evidence_boundary", "final_performance_evidence"): False,
        ("evidence_boundary", "single_seed_pilot_only"): True,
        ("evidence_boundary", "post_hoc_tuning_allowed"): False,
        ("evidence_boundary", "value_filter_superiority_supported"): False,
        ("evidence_boundary", "confirmatory_next_step"): "matched seeds 0-4",
        ("comparison", "candidate_reward_greater"): False,
        ("comparison", "first_action_divergence_step"): 9,
        ("comparison", "shared_prefix_steps"): 8,
        ("comparison", "position_action_overlap_count"): 9,
        ("comparison", "unique_action_overlap_count"): 74,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    comparison = payload.get("comparison", {})
    float_expectations = {
        "total_reward_delta_candidate_minus_baseline": -3.240847761581,
    }
    for key, expected in float_expectations.items():
        value = comparison.get(key)
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-9:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                f"comparison.{key}={value}"
            )

    metric_expectations = {
        "slope_change_pct": 0.007503881996,
        "cont_change": 0.003559895237,
        "baimu_area_change_ha": 29.600013869751,
    }
    final_metric_deltas = comparison.get("final_metric_deltas", {})
    for key, expected in metric_expectations.items():
        value = final_metric_deltas.get(key)
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-9:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                f"comparison.final_metric_deltas.{key}={value}"
            )

    runs = payload.get("runs")
    if not isinstance(runs, list) or len(runs) != 2:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
            f"len(runs)={len(runs) if isinstance(runs, list) else 'non-list'}"
        )
        runs = []
    by_name = {
        run.get("name"): run
        for run in runs
        if isinstance(run, dict) and run.get("name")
    }
    expected_runs = {
        "matched_paper9": {
            "selector": "paper9",
            "steps_run": 100,
            "total_reward": 70.95434469700466,
            "negative_reward_steps": 13,
            "terminated": True,
            "truncated": False,
        },
        "matched_value_filter": {
            "selector": "value_filter",
            "steps_run": 100,
            "total_reward": 67.7134969354234,
            "negative_reward_steps": 6,
            "terminated": True,
            "truncated": False,
        },
    }
    for name, expectations in expected_runs.items():
        run = by_name.get(name)
        if run is None:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: runs.{name}"
            )
            continue
        for key, expected in expectations.items():
            value = run.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-9:
                    missing_tokens.append(
                        f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                        f"runs.{name}.{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON}: "
                    f"runs.{name}.{key}={value}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_env_longhorizon_pilot_audit_current",
            False,
            "Paper10 real-environment long-horizon pilot audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_env_longhorizon_pilot_audit_current",
        True,
        "Paper10 real-environment long-horizon pilot audit is current and claim-bounded",
    )
def check_paper10_real_env_longhorizon_confirmatory_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD,
        PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON,
        PAPER10_REAL_ENV_LONGHORIZON_PILOT_AUDIT_JSON,
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_real_env_longhorizon_confirmatory_audit_current",
            False,
            "missing Paper10 real-environment long-horizon confirmatory audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_real_env_longhorizon_confirmatory_audit_current",
            False,
            f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("REPRODUCIBILITY.md"),
        PAPER10_CEUS_REVIEW_OPTIMIZATION_REGISTER,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 real-data long-horizon matched 5-seed audit",
        "descriptive matched 5-seed result",
        "| total reward mean | 67.5437 | 69.4705 | 1.9269 |",
        "| total reward sample std | 7.2246 | 1.0004 | -6.2242 |",
        "| candidate win count | 0 | 3 | 3 |",
        "| 0 | 70.9543 | 67.7135 | -3.2408 | 9 |",
        "| 4 | 78.0925 | 69.8677 | -8.2248 | 2 |",
        "Matches pilot audit: `True`",
        "inferential superiority is not supported",
        "post-hoc tuning",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-27",
        ("status",): "locked matched 5-seed real-data audit",
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "protocol_locked"): True,
        ("source_boundary", "post_hoc_tuning_allowed"): False,
        ("evidence_boundary", "descriptive_matched_5seed_result"): True,
        ("evidence_boundary", "descriptive_matched_5seed_mean_reward_higher"): True,
        ("evidence_boundary", "variance_lower_in_matched_5seed"): True,
        ("evidence_boundary", "inferential_superiority_supported"): False,
        ("evidence_boundary", "direct_50_state_scaleup_success_supported"): False,
        ("evidence_boundary", "post_hoc_tuning_allowed"): False,
        ("seed0_pilot_linkage", "matches_pilot_audit"): True,
        ("seed0_pilot_linkage", "baseline_action_trace_match"): True,
        ("seed0_pilot_linkage", "candidate_action_trace_match"): True,
        ("paired_comparison", "matched_seeds"): [0, 1, 2, 3, 4],
        ("paired_comparison", "candidate_win_count"): 3,
        ("paired_comparison", "candidate_loss_count"): 2,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    float_expectations = {
        ("policies", "baseline", "aggregate", "total_reward_mean"): 67.5436698503176,
        ("policies", "baseline", "aggregate", "total_reward_std_sample"): 7.22455439874099,
        ("policies", "candidate", "aggregate", "total_reward_mean"): 69.47054604253474,
        ("policies", "candidate", "aggregate", "total_reward_std_sample"): 1.0003610285842477,
        ("paired_comparison", "total_reward_delta_mean"): 1.9268761922171436,
        ("paired_comparison", "total_reward_delta_std_sample"): 7.512208608270984,
    }
    for path_keys, expected in float_expectations.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-9:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    per_seed = payload.get("paired_comparison", {}).get("per_seed")
    expected_seed_deltas = [
        (0, -3.2408477615812643, 9),
        (1, 3.613740374883278, 1),
        (2, 8.424238053365706, 1),
        (3, 9.062029496163603, 2),
        (4, -8.224779201745605, 2),
    ]
    if not isinstance(per_seed, list) or len(per_seed) != 5:
        missing_tokens.append(
            f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
            f"len(paired_comparison.per_seed)={len(per_seed) if isinstance(per_seed, list) else 'non-list'}"
        )
        per_seed = []
    for index, (seed, expected_delta, expected_divergence) in enumerate(expected_seed_deltas):
        if index >= len(per_seed):
            continue
        row = per_seed[index]
        if row.get("seed") != seed:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                f"paired_comparison.per_seed[{index}].seed={row.get('seed')}"
            )
        value = row.get("total_reward_delta_candidate_minus_baseline")
        if not isinstance(value, (int, float)) or abs(float(value) - expected_delta) > 1e-9:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                f"paired_comparison.per_seed[{index}].delta={value}"
            )
        if row.get("first_action_divergence_step") != expected_divergence:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_JSON}: "
                f"paired_comparison.per_seed[{index}].first_action_divergence_step="
                f"{row.get('first_action_divergence_step')}"
            )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_REAL_ENV_LONGHORIZON_CONFIRMATORY_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_real_env_longhorizon_confirmatory_audit_current",
            False,
            "Paper10 real-environment long-horizon confirmatory audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_real_env_longhorizon_confirmatory_audit_current",
        True,
        "Paper10 real-environment long-horizon confirmatory audit is current and claim-bounded",
    )


def check_paper10_ceus_baseline_inference_hardening_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_BASELINE_HARDENING_MD,
        PAPER10_CEUS_BASELINE_HARDENING_JSON,
        PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            "missing Paper10 CEUS baseline hardening files: "
            + ", ".join(missing),
        )

    audit_text = read_text(root / PAPER10_CEUS_BASELINE_HARDENING_MD)
    patch_text = read_text(root / PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH)
    try:
        payload = json.loads(read_text(root / PAPER10_CEUS_BASELINE_HARDENING_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        doc_text = read_text(root / doc)
        if PAPER10_CEUS_BASELINE_HARDENING_MD.name not in doc_text:
            missing_tokens.append(f"{doc}: {PAPER10_CEUS_BASELINE_HARDENING_MD.name}")

    required_audit_tokens = [
        "Paper10 CEUS baseline and inference hardening audit",
        "diagnostic_only",
        "mixed seed-wise outcome",
        "uniform superiority is not supported",
        "inferential superiority is not supported",
        "executable-mask necessity",
        "monitor gate as evidence control",
    ]
    for token in required_audit_tokens:
        if token not in audit_text:
            missing_tokens.append(f"{PAPER10_CEUS_BASELINE_HARDENING_MD}: {token}")

    required_patch_tokens = [
        "Paper10 CEUS baseline-hardened manuscript patch",
        "descriptive matched 5-seed reward anchor",
        "mixed seed-wise outcome",
        "diagnostic-only two-sided sign test gives p=1.0000",
        "executable-mask necessity",
        "monitor gate as evidence control",
        "Stage 3 boundary evidence",
        "Dongxing/Neijiang calibration evidence",
    ]
    for token in required_patch_tokens:
        if token not in patch_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH}: {token}"
            )

    expected_values = {
        ("status",): "source-derived CEUS baseline and inference hardening audit",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "post_hoc_tuning_allowed"): False,
        ("paired_reward_summary", "n_seeds"): 5,
        ("paired_reward_summary", "candidate_win_count"): 3,
        ("paired_reward_summary", "candidate_loss_count"): 2,
        ("paired_reward_summary", "uniform_superiority_supported"): False,
        ("paired_reward_summary", "inferential_superiority_supported"): False,
        ("paired_reward_summary", "descriptive_mean_reward_anchor_supported"): True,
        ("paired_reward_summary", "sign_test", "classification"): "diagnostic_only",
        ("claim_gates", "descriptive_mean_reward_anchor_supported"): True,
        ("claim_gates", "uniform_superiority_supported"): False,
        ("claim_gates", "inferential_superiority_supported"): False,
        ("claim_gates", "stage3_50state_scaleup_supported"): False,
        ("claim_gates", "robust_transfer_superiority_supported"): False,
        ("claim_gates", "irregular_cadastral_deployment_supported"): False,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    p_value = (
        payload.get("paired_reward_summary", {})
        .get("sign_test", {})
        .get("p_value")
    )
    if not isinstance(p_value, (float, int)) or abs(float(p_value) - 1.0) > 1e-8:
        missing_tokens.append(
            f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: sign_test.p_value={p_value}"
        )

    for rel_path, text in (
        (PAPER10_CEUS_BASELINE_HARDENING_MD, audit_text),
        (PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH, patch_text),
    ):
        for line_no, line in enumerate(text.splitlines(), start=1):
            if is_ceus_baseline_positive_overclaim(line):
                missing_tokens.append(
                    f"{rel_path}:{line_no}: forbidden CEUS baseline hardening wording: {line.strip()}"
                )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            "Paper10 CEUS baseline hardening gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_baseline_inference_hardening_current",
        True,
        "Paper10 CEUS baseline hardening audit and manuscript patch are current",
    )




def check_paper10_guard_information_set_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_GUARD_INFORMATION_SET_AUDIT_MD,
        PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON,
        README,
        MANIFEST,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_guard_information_set_audit_current",
            False,
            "missing Paper10 guard information-set audit files: " + ", ".join(missing),
        )

    audit_text = read_text(root / PAPER10_GUARD_INFORMATION_SET_AUDIT_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_guard_information_set_audit_current",
            False,
            f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    package_name = PAPER10_GUARD_INFORMATION_SET_AUDIT_MD.name
    for doc in (README, MANIFEST, DATA_AVAILABILITY):
        if package_name not in read_text(root / doc):
            missing_tokens.append(f"{doc}: {package_name}")

    required_text_tokens = [
        "Paper10 guard information-set and baseline stress audit",
        "Status: guard_information_set_and_baseline_stress_audit",
        "oracle/action-audit guard",
        "not a standalone deployable no-oracle planner",
        "model_reward_top1_proxy",
        "candidate_score_top1_proxy",
        "executable_random_20seed_rollout",
        "Do not claim proxy-guard rollout superiority.",
        "Do not claim the dynamic baseline suite is complete.",
    ]
    for token in required_text_tokens:
        if token not in audit_text:
            missing_tokens.append(f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_MD}: {token}")

    expected_values = {
        ("status",): "guard_information_set_and_baseline_stress_audit",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "new_dynamic_rollout_baselines"): False,
        ("source_boundary", "statewise_reanalysis_only"): True,
        ("information_set_boundary", "allowed_primary_role"): "oracle/action-audit guard",
        ("information_set_boundary", "deployable_without_reward_oracle"): False,
        ("information_set_boundary", "primary_guard_information_set"): "privileged_immediate_true_reward_action_audit",
        ("statewise_audit_summary", "audited_states"): 2000,
        ("statewise_audit_summary", "switches"): 172,
        ("claim_gates", "true_reward_guard_deployable_without_oracle"): False,
        ("claim_gates", "proxy_guard_rollout_superiority_supported"): False,
        ("claim_gates", "dynamic_baseline_suite_complete"): False,
        ("claim_gates", "manuscript_should_call_guard_oracle_action_audit"): True,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    missing_baselines = set(payload.get("missing_dynamic_baselines", []))
    for baseline in [
        "executable_random_20seed_rollout",
        "greedy_immediate_true_reward_20seed_rollout",
        "rank_only_or_no_value_20seed_rollout",
        "model_reward_proxy_guard_20seed_rollout",
        "candidate_score_proxy_guard_20seed_rollout",
        "full_valid_action_oracle_upper_bound_20seed_rollout",
    ]:
        if baseline not in missing_baselines:
            missing_tokens.append(
                f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: missing baseline {baseline}"
            )

    one_step = payload.get("one_step_policy_diagnostics", {})
    selected = one_step.get("selected_value_filter", {})
    model_proxy = one_step.get("model_reward_top1_proxy", {})
    candidate_proxy = one_step.get("candidate_score_top1_proxy", {})
    if float(model_proxy.get("mean_delta_vs_selected", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: model proxy one-step delta"
        )
    if float(candidate_proxy.get("mean_delta_vs_selected", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: candidate proxy one-step delta"
        )
    if selected.get("diagnostic_scope") != "statewise immediate action audit, not dynamic rollout":
        missing_tokens.append(
            f"{PAPER10_GUARD_INFORMATION_SET_AUDIT_JSON}: selected diagnostic scope"
        )

    if missing_tokens:
        return CheckResult(
            "paper10_guard_information_set_audit_current",
            False,
            "Paper10 guard information-set audit gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_guard_information_set_audit_current",
        True,
        "Paper10 guard information-set audit is current and oracle-bounded",
    )

def check_paper10_proxy_guard_dynamic_baseline_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_MD,
        PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON,
        README,
        MANIFEST,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_proxy_guard_dynamic_baseline_audit_current",
            False,
            "missing Paper10 proxy guard dynamic baseline audit files: "
            + ", ".join(missing),
        )

    audit_text = read_text(root / PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_proxy_guard_dynamic_baseline_audit_current",
            False,
            f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    package_name = PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_MD.name
    for doc in (README, MANIFEST, DATA_AVAILABILITY):
        if package_name not in read_text(root / doc):
            missing_tokens.append(f"{doc}: {package_name}")

    required_text_tokens = [
        "Paper10 proxy guard dynamic baseline stress audit",
        "Status: proxy_guard_dynamic_baseline_stress_audit",
        "value_filter_5seed_anchor",
        "model_reward_proxy_guard_m010",
        "candidate_score_proxy_guard_m010",
        "65.2734",
        "63.4116",
        "Do not claim proxy-guard rollout superiority.",
        "Do not present the true-reward guard as a deployable no-oracle policy.",
    ]
    for token in required_text_tokens:
        if token not in audit_text:
            missing_tokens.append(
                f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("status",): "proxy_guard_dynamic_baseline_stress_audit",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): True,
        ("source_boundary", "new_dynamic_rollout_baselines"): True,
        ("source_boundary", "scope"): "5-seed no-oracle proxy guard stress test, not 20-seed confirmation",
        ("claim_gates", "model_reward_proxy_beats_value_filter_5seed_mean"): False,
        ("claim_gates", "candidate_score_proxy_beats_value_filter_5seed_mean"): False,
        ("claim_gates", "no_oracle_proxy_guard_superiority_supported"): False,
        ("claim_gates", "proxy_guard_20seed_confirmation_complete"): False,
        ("claim_gates", "true_reward_guard_remains_oracle_action_audit"): True,
        ("claim_gates", "manuscript_should_not_promote_proxy_guard"): True,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    anchor = payload.get("value_filter_anchor", {})
    if abs(float(anchor.get("total_reward_mean", 0.0)) - 69.47054604253474) > 1e-8:
        missing_tokens.append(
            f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: value-filter mean"
        )

    proxy_rows = {
        row.get("policy_label"): row
        for row in payload.get("proxy_guard_rollouts", [])
        if isinstance(row, dict)
    }
    expected_proxy_rows = {
        "model_reward_proxy_guard_m010": {
            "total_reward_mean": 65.2734437835953,
            "delta_vs_value_filter_5seed_mean": -4.197102258939438,
            "switches": 99,
            "switch_rate": 0.198,
            "beats_value_filter_5seed_mean": False,
        },
        "candidate_score_proxy_guard_m010": {
            "total_reward_mean": 63.41162026645615,
            "delta_vs_value_filter_5seed_mean": -6.058925776078588,
            "switches": 98,
            "switch_rate": 0.196,
            "beats_value_filter_5seed_mean": False,
        },
    }
    for label, expected_row in expected_proxy_rows.items():
        row = proxy_rows.get(label)
        if not isinstance(row, dict):
            missing_tokens.append(
                f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: {label}"
            )
            continue
        for key, expected in expected_row.items():
            value = row.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-8:
                    missing_tokens.append(
                        f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: "
                        f"{label}.{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_PROXY_GUARD_DYNAMIC_BASELINE_AUDIT_JSON}: "
                    f"{label}.{key}={value}"
                )

    if missing_tokens:
        return CheckResult(
            "paper10_proxy_guard_dynamic_baseline_audit_current",
            False,
            "Paper10 proxy guard dynamic baseline audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_proxy_guard_dynamic_baseline_audit_current",
        True,
        "Paper10 proxy guard dynamic baseline audit is current and negative-bounded",
    )
def check_paper10_ceus_review_response_experiment_package_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD,
        PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        PAPER10_CEUS_BASELINE_HARDENING_JSON,
        PAPER10_CEUS_MECHANISM_CLAIM_AUDIT_JSON,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_review_response_experiment_package_current",
            False,
            "missing Paper10 CEUS review-response experiment package files: "
            + ", ".join(missing),
        )

    package_text = read_text(root / PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_ceus_review_response_experiment_package_current",
            False,
            f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    package_name = PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD.name
    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        doc_text = read_text(root / doc)
        if package_name not in doc_text:
            missing_tokens.append(f"{doc}: {package_name}")

    required_text_tokens = [
        "Paper10 CEUS review-response algorithm experiment package",
        "Status: ceus_review_response_algorithm_experiment_package",
        "`rewardtop7 margin=1.50`",
        "true-reward margin guard",
        "20 / 20",
        "72.1918",
        "65.8876",
        "6.3041",
        "4.1401",
        "8.5056",
        "historical descriptive anchor, not the primary claim",
        "diagnostic sign-test p=1.0000",
        "reward_primary_secondary_mixed",
        "monitor gate as evidence control",
        "Primary Oracle Action-Audit Reward Evidence",
        "submission_story_should_use_guard_as_oracle_action_audit_evidence",
        "Do not claim uniform secondary-metric improvement.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
    ]
    for token in required_text_tokens:
        if token not in package_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD}: {token}"
            )

    expected_values = {
        ("status",): "ceus_review_response_algorithm_experiment_package",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "algorithm_reselection_from_tracked_evidence"): True,
        ("source_boundary", "reviewer_driven_claim_reclassification"): True,
        ("primary_algorithm_evidence", "algorithm"): "true_reward_margin_guard",
        ("primary_algorithm_evidence", "setting"): "bishan_20x16_top5",
        ("primary_algorithm_evidence", "audit_set"): "rewardtop7",
        ("primary_algorithm_evidence", "switch_margin"): 1.5,
        ("primary_algorithm_evidence", "n_seeds"): 20,
        ("primary_algorithm_evidence", "seed_wins"): 20,
        ("primary_algorithm_evidence", "seed_losses"): 0,
        ("legacy_value_filter_anchor", "role"): "historical_descriptive_anchor_not_primary",
        ("legacy_value_filter_anchor", "n_seeds"): 5,
        ("legacy_value_filter_anchor", "candidate_win_count"): 3,
        ("legacy_value_filter_anchor", "candidate_loss_count"): 2,
        ("legacy_value_filter_anchor", "primary_claim_allowed"): False,
        ("secondary_metric_assessment", "classification"): "reward_primary_secondary_mixed",
        ("mechanism_boundary", "monitor_gate_direct_reward_gain_supported"): False,
        ("mechanism_boundary", "monitor_gate_evidence_control_supported"): True,
        ("mechanism_boundary", "executable_mask_necessity_supported"): True,
        ("claim_gates", "primary_guard_confirmatory_20seed_supported"): True,
        ("claim_gates", "old_5seed_value_filter_primary_claim_blocked"): True,
        ("claim_gates", "secondary_metrics_uniformly_aligned"): False,
        ("claim_gates", "monitor_gate_online_reward_gain_supported"): False,
        ("claim_gates", "direct_50state_scaleup_supported"): False,
        ("claim_gates", "robust_transfer_superiority_supported"): False,
        ("claim_gates", "submission_story_should_use_guard_as_primary"): False,
        ("claim_gates", "submission_story_should_use_guard_as_oracle_action_audit_evidence"): True,
        ("claim_gates", "primary_guard_promoted_to_main_algorithm_candidate"): False,
        ("claim_gates", "primary_guard_recorded_as_oracle_action_audit_reward_evidence"): True,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    legacy = payload.get("legacy_value_filter_anchor", {})
    if legacy.get("primary_claim_allowed") is not False:
        missing_tokens.append(
            f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON}: "
            "old_5seed_value_filter_primary_claim_blocked failed"
        )

    primary = payload.get("primary_algorithm_evidence", {})
    ci = primary.get("bootstrap_95ci_delta", [0.0, 0.0])
    numeric_checks = [
        ("primary mean delta", primary.get("mean_delta_vs_baseline", 0.0) > 0.0),
        ("primary min seed delta", primary.get("min_seed_delta_vs_baseline", 0.0) > 0.0),
        ("primary bootstrap CI lower", len(ci) == 2 and ci[0] > 0.0),
        (
            "primary guard mean reward",
            abs(float(primary.get("guard_mean_reward", 0.0)) - 72.19178534319884) < 1e-8,
        ),
        (
            "primary baseline mean reward",
            abs(float(primary.get("baseline_mean_reward", 0.0)) - 65.8876435268697) < 1e-8,
        ),
    ]
    for label, ok in numeric_checks:
        if not ok:
            missing_tokens.append(
                f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_JSON}: {label} failed"
            )

    for line_no, line in enumerate(package_text.splitlines(), start=1):
        if is_true_reward_guard_positive_overclaim(line):
            missing_tokens.append(
                f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD}:{line_no}: "
                f"forbidden true-reward guard wording: {line.strip()}"
            )
        if is_ceus_baseline_positive_overclaim(line):
            missing_tokens.append(
                f"{PAPER10_CEUS_REVIEW_RESPONSE_EXPERIMENT_PACKAGE_MD}:{line_no}: "
                f"forbidden baseline overclaim: {line.strip()}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_review_response_experiment_package_current",
            False,
            "Paper10 CEUS review-response experiment package gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_review_response_experiment_package_current",
        True,
        "Paper10 CEUS review-response experiment package is current and claim-bounded",
    )


def check_paper10_post_guard_experiment_closure_refresh_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
        RESULTS / "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        RESULTS / "e0_paper10_experiment_closure_register_2026-06-27.md",
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "missing Paper10 post-guard experiment-closure refresh files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    required_tokens = [
        "Paper10 post-guard experiment-closure refresh",
        "Status: post_guard_experiment_closure_refresh",
        "source-derived; no rollout or training rerun",
        "rewardtop7 margin=1.50",
        "72.1918",
        "65.8876",
        "6.3041",
        "20 / 20",
        "4.1401",
        "7.7605",
        "8.1905",
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON.name,
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD.name,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON.name,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD.name,
        "e0_paper10_experiment_freeze_audit_2026-06-27.md",
        "e0_paper10_experiment_closure_register_2026-06-27.md",
        PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        "closure update, not a new experiment",
        "not final submission readiness",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-07-08",
        ("status",): "post_guard_experiment_closure_refresh",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("primary_guard", "audit_set"): "rewardtop7",
        ("primary_guard", "switch_margin"): 1.5,
        ("primary_guard", "n_seeds"): 20,
        ("primary_guard", "guard_mean_reward"): 72.19178534319884,
        ("primary_guard", "baseline_mean_reward"): 65.8876435268697,
        ("primary_guard", "mean_delta_vs_baseline"): 6.304141816329158,
        ("primary_guard", "seed_wins"): 20,
        ("primary_guard", "bootstrap_95ci_delta_lower"): 4.140109129548553,
        ("primary_guard", "mean_audit_action_count"): 7.7605,
        ("primary_guard", "dual7x7_mean_audit_action_count"): 8.1905,
        ("closure_decision", "default_next_phase"): "bounded_manuscript_assembly",
        ("closure_decision", "resume_broad_algorithm_redesign"): False,
        ("closure_decision", "historical_june_records_mutated"): False,
        ("submission_boundary", "status"): "not_submission_ready",
        ("claim_locks", "direct_50state_scaleup_supported"): False,
        ("claim_locks", "robust_transfer_superiority_supported"): False,
        ("claim_locks", "deployment_ready_supported"): False,
        ("claim_locks", "universal_fixed_margin_supported"): False,
        ("claim_locks", "final_submission_readiness_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    blockers = nested_value(payload, ("submission_boundary", "open_blockers"))
    if not isinstance(blockers, list):
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
            "submission_boundary.open_blockers"
        )
        blockers = []
    for blocker in (
        "repository DOI or anonymous reviewer link",
        "code licence",
        "generated-data rights and checkpoint or model-weight rights",
        "full Bishan Tool2 data access route",
        "GPKG-root geospatial input access route",
        "Dongxing/Neijiang prepared-data access route",
        "citation policy for local-only sources, preprints, and final reference style",
        "statistical reporting policy for descriptive results versus hypothesis tests",
        "Main Figure 1 final schematic artwork and journal-specific figure/table export rules",
    ):
        if blocker not in blockers:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON}: "
                f"submission_boundary.open_blockers.{blocker}"
            )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_closure_refresh_positive_overclaim(line):
            hits.append(
                f"{PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD}:{line_no}: "
                f"{line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "forbidden post-guard closure refresh wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_post_guard_experiment_closure_refresh_current",
            False,
            "Paper10 post-guard experiment-closure refresh gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_post_guard_experiment_closure_refresh_current",
        True,
        "Paper10 post-guard experiment-closure refresh is current and bounded",
    )



def check_paper10_author_decision_closeout_form_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD,
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON,
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        AUTHOR_DECISION_MATRIX,
        DATA_ACCESS_RIGHTS_REGISTER,
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_author_decision_closeout_form_current",
            False,
            "missing Paper10 author-decision closeout form files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_author_decision_closeout_form_current",
            False,
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    required_tokens = [
        "Paper10 author-decision closeout form",
        "Status: author_input_partially_provided",
        "source-derived; no rollout or training rerun; no submission approval",
        "Formal submission remains blocked",
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
        "available upon request",
        "code can be public",
        "non-DLTB artifacts can be public",
        "original Bishan DLTB data must not be public",
        "original Dongxing DLTB data must not be public",
        "Do not use this form as submission approval.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not claim a universal fixed switch margin.",
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON.name,
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        AUTHOR_DECISION_MATRIX.name,
        DATA_ACCESS_RIGHTS_REGISTER.name,
        PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-07-08",
        ("artifact_type",): "paper10_author_decision_closeout_form",
        ("status",): "author_input_partially_provided",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("source_boundary", "author_decisions_invented"): False,
        ("submission_state", "formal_submission_blocked"): True,
        ("submission_state", "status_reason"): (
            "author provided repository reviewer link and data/code publication boundary; "
            "formal submission remains blocked by named licence terms, restricted DLTB "
            "controlled-access routing, reviewer-link browser test, and final backfill"
        ),
        ("submission_state", "repository_reviewer_link_provided"): True,
        ("submission_state", "repository_reviewer_link_verified_for_browser_review"): False,
        ("submission_state", "preflight_pass_does_not_mean_submission_ready"): True,
        ("closeout_policy", "do_not_invent_author_decisions"): True,
        ("closeout_policy", "all_fields_block_submission_until_closed"): True,
        ("closeout_policy", "use_durable_repository_or_controlled_access_route"): True,
        ("closeout_policy", "available_upon_request_alone_is_not_acceptable"): True,
        ("closeout_policy", "do_not_relicense_restricted_geospatial_inputs"): True,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("claim_locks", "direct_50state_scaleup_supported"): False,
        ("claim_locks", "robust_transfer_superiority_supported"): False,
        ("claim_locks", "deployment_ready_supported"): False,
        ("claim_locks", "universal_fixed_margin_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    expected_source_files = {
        "post_guard_submission_readiness_refresh_json": PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON.name,
        "post_guard_submission_readiness_refresh_md": PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD.name,
        "submission_blocker_packet": SUBMISSION_BLOCKER_DECISION_PACKET.name,
        "author_decision_matrix": AUTHOR_DECISION_MATRIX.name,
        "data_access_rights_register": DATA_ACCESS_RIGHTS_REGISTER.name,
        "submission_boundary_md": PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        "final_export_package": PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
    }
    source_files = payload.get("source_files")
    if not isinstance(source_files, dict):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: source_files"
        )
        source_files = {}
    for key, filename in expected_source_files.items():
        value = source_files.get(key)
        if not isinstance(value, str) or not value.endswith(filename):
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                f"source_files.{key}={value}"
            )

    link_check = payload.get("link_access_check")
    if not isinstance(link_check, dict):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: link_access_check"
        )
        link_check = {}
    if link_check.get("anonymous_reviewer_link") != (
        "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/"
    ):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
            f"link_access_check.anonymous_reviewer_link={link_check.get('anonymous_reviewer_link')}"
        )
    for key in ("check_method", "observed_result", "interpretation"):
        if not link_check.get(key):
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                f"link_access_check.{key}"
            )

    expected_author_boundary = {
        "code_can_be_public": True,
        "original_bishan_dltb_can_be_public": False,
        "original_dongxing_dltb_can_be_public": False,
        "non_dltb_artifacts_can_be_public": True,
    }
    author_input_recorded = payload.get("author_input_recorded")
    if not isinstance(author_input_recorded, dict):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: author_input_recorded"
        )
        author_input_recorded = {}
    author_boundary = author_input_recorded.get("data_and_code_publication_boundary")
    if not isinstance(author_boundary, dict):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
            "author_input_recorded.data_and_code_publication_boundary"
        )
        author_boundary = {}
    for key, expected in expected_author_boundary.items():
        observed = author_boundary.get(key)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                f"author_input_recorded.data_and_code_publication_boundary.{key}={observed}"
            )
    if (
        author_boundary.get("original_bishan_dltb_can_be_public") is True
        or author_boundary.get("original_dongxing_dltb_can_be_public") is True
    ):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
            "original DLTB public release is not allowed"
        )
    expected_fields = [
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
    fields = payload.get("author_decision_closeout_fields")
    if not isinstance(fields, list):
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
            "author_decision_closeout_fields"
        )
        fields = []
    observed_fields = [
        field.get("field") for field in fields if isinstance(field, dict)
    ]
    if observed_fields != expected_fields:
        missing_tokens.append(
            f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
            f"author_decision_closeout_fields={observed_fields}"
        )
    expected_field_statuses = {
        "repository_doi_or_anonymous_reviewer_link": (
            "provided_pending_external_browser_test_and_backfill",
            False,
        ),
        "code_licence": (
            "public_code_allowed_pending_named_software_licence",
            True,
        ),
        "generated_data_and_checkpoint_model_weight_rights": (
            "public_release_allowed_except_sensitive_original_dltb_pending_named_rights_terms",
            True,
        ),
        "full_bishan_tool2_access_route": (
            "derived_tool2_public_release_allowed_pending_dltb_leakage_check_and_deposit",
            False,
        ),
        "gpkg_root_geospatial_input_access_route": (
            "restricted_sensitive_original_bishan_dltb_controlled_access_required",
            True,
        ),
        "dongxing_neijiang_prepared_data_access_route": (
            "split_route_original_dongxing_dltb_restricted_derived_non_dltb_public_pending_leakage_check_and_controlled_route",
            True,
        ),
        "reviewer_data_access": (
            "partially_closed_public_code_and_derived_artifacts_pending_restricted_dltb_reviewer_route_and_browser_test",
            True,
        ),
        "citation_policy": ("unresolved", True),
        "statistical_reporting_policy": ("unresolved", True),
        "main_figure_1_and_journal_export_rules": ("unresolved", True),
    }
    for field in fields:
        if not isinstance(field, dict):
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                "non-dict author_decision_closeout_fields row"
            )
            continue
        name = field.get("field")
        expected_status, expected_author_input_required = expected_field_statuses.get(
            name,
            ("unresolved", True),
        )
        status = str(field.get("status", ""))
        if name in {
            "gpkg_root_geospatial_input_access_route",
            "dongxing_neijiang_prepared_data_access_route",
        } and "public_original_dltb" in status.lower():
            missing_tokens.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                "original DLTB public release is not allowed"
            )
        for key, expected in (
            ("status", expected_status),
            ("author_input_required", expected_author_input_required),
            ("blocking_before_formal_submission", True),
        ):
            if field.get(key) != expected:
                missing_tokens.append(
                    f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                    f"author_decision_closeout_fields.{name}.{key}={field.get(key)}"
                )
        if name == "repository_doi_or_anonymous_reviewer_link":
            provided = field.get("provided_input")
            if not isinstance(provided, dict):
                missing_tokens.append(
                    f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                    "author_decision_closeout_fields.repository.provided_input"
                )
                provided = {}
            if provided.get("anonymous_reviewer_link") != (
                "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/"
            ):
                missing_tokens.append(
                    f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                    "author_decision_closeout_fields.repository.anonymous_reviewer_link"
                )
            for key, expected in (
                ("external_browser_test_required", True),
                ("final_backfill_required", True),
            ):
                if field.get(key) != expected:
                    missing_tokens.append(
                        f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                        f"author_decision_closeout_fields.repository.{key}={field.get(key)}"
                    )
            remaining = field.get("remaining_closeout")
            if not isinstance(remaining, list) or not remaining:
                missing_tokens.append(
                    f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                    "author_decision_closeout_fields.repository.remaining_closeout"
                )
        for key in (
            "recommended_default",
            "acceptable_closeout",
            "not_acceptable",
            "must_record",
            "files_to_update_after_closeout",
        ):
            value = field.get(key)
            if not value:
                missing_tokens.append(
                    f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON}: "
                    f"author_decision_closeout_fields.{name}.{key}"
                )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD}:{line_no}: "
                f"{line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_author_decision_closeout_form_current",
            False,
            "forbidden author-decision closeout wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_author_decision_closeout_form_current",
            False,
            "Paper10 author-decision closeout form gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_author_decision_closeout_form_current",
        True,
        "Paper10 author-decision closeout form is current and no-go guarded",
    )


def check_paper10_public_release_rights_gate_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON,
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_MD,
        PAPER10_AUTHOR_DECISION_CLOSEOUT_FORM_JSON,
        DATA_AVAILABILITY,
        DATA_CODE_AVAILABILITY,
        DATA_ACCESS_RIGHTS_REGISTER,
        ARCHIVE_METADATA_TEMPLATES,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_public_release_rights_gate_current",
            False,
            "missing Paper10 public-release rights gate files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_public_release_rights_gate_current",
            False,
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    normalized_text = " ".join(text.split())
    required_tokens = [
        "Paper10 public-release rights gate",
        "Status: public_release_rights_closed_restricted_data_no_go",
        "author-updated; no rollout or training rerun; no submission approval",
        "Formal submission remains blocked",
        "code uses Apache-2.0",
        "code licence is Apache-2.0",
        "released under CC0-1.0",
        "Original Bishan and Dongxing DLTB inputs are confidential_no_external_access",
        "cannot be provided externally",
        "DLTB-leakage check",
        "4open README.md direct reviewer link",
        "author-confirmed available",
        "curl.exe -L --max-time 30",
        "302 Found",
        "401 Unauthorized",
        "{\"error\":\"not_connected\"}",
        "does not invalidate the README.md direct link",
        "no exact snapshot identifier",
        "submission-preparation commit anchor",
        "confidential_no_external_access",
        "Do not use this gate as submission approval.",
        "Do not apply Apache-2.0 or CC0-1.0 to original Bishan or Dongxing DLTB inputs.",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD}: {token}")

    expected_values = {
        ("date",): "2026-07-09",
        ("artifact_type",): "paper10_public_release_rights_gate",
        ("status",): "public_release_rights_closed_restricted_data_no_go",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("source_boundary", "author_decisions_invented"): False,
        ("submission_blockers", "formal_submission_blocked"): True,
        ("submission_blockers", "preflight_pass_does_not_mean_submission_ready"): True,
        ("licence_state", "code_can_be_public"): True,
        ("licence_state", "named_software_licence_selected"): True,
        ("licence_state", "code_licence_name"): "Apache-2.0",
        ("licence_state", "repository_licence_file_present"): True,
        ("licence_state", "scope_limited_to_licensable_code_and_scripts"): True,
        ("rights_state", "non_dltb_artifacts_can_be_public"): True,
        ("rights_state", "named_generated_output_rights_selected"): True,
        ("rights_state", "generated_output_rights_terms"): "CC0-1.0",
        ("rights_state", "checkpoint_model_weight_rights_selected"): True,
        ("rights_state", "checkpoint_model_weight_rights_terms"): "CC0-1.0",
        ("rights_state", "must_not_relicense_restricted_dltb"): True,
        ("data_boundary", "original_bishan_dltb_public_release_allowed"): False,
        ("data_boundary", "original_dongxing_dltb_public_release_allowed"): False,
        ("data_boundary", "original_bishan_dltb_access_route"): "confidential_no_external_access",
        ("data_boundary", "original_dongxing_dltb_access_route"): "confidential_no_external_access",
        ("data_boundary", "restricted_dltb_external_access_available"): False,
        ("data_boundary", "derived_non_dltb_public_release_allowed_after_leakage_check"): True,
        ("data_boundary", "derived_tool2_leakage_check_completed"): False,
        ("data_boundary", "dongxing_derived_leakage_check_completed"): False,
        ("data_boundary", "restricted_dltb_controlled_access_route_selected"): False,
        ("repository_snapshot", "anonymous_reviewer_link"): "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/",
        ("repository_snapshot", "anonymous_readme_direct_link"): "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md",
        ("repository_snapshot", "archive_platform"): "anonymous.4open.science",
        ("repository_snapshot", "author_confirmed_readme_direct_link_available"): True,
        ("repository_snapshot", "author_confirmation_date"): "2026-07-09",
        ("repository_snapshot", "command_line_access_check", "date"): "2026-07-09",
        ("repository_snapshot", "command_line_access_check", "scope"): "root URL and redirected API path only, not the README.md direct reviewer link",
        ("repository_snapshot", "command_line_access_check", "observed_redirect_status"): "302 Found",
        ("repository_snapshot", "command_line_access_check", "observed_followup_status"): "401 Unauthorized",
        ("repository_snapshot", "command_line_access_check", "observed_get_body"): "{\"error\":\"not_connected\"}",
        ("repository_snapshot", "command_line_access_check", "readme_direct_link_invalidated"): False,
        ("repository_snapshot", "command_line_access_check", "reviewer_browser_verification_closed"): False,
        ("repository_snapshot", "non_author_browser_test_completed"): False,
        ("repository_snapshot", "exact_submission_commit_backfilled"): False,
        ("repository_snapshot", "author_checked_4open_snapshot_identifier"): True,
        ("repository_snapshot", "author_visible_4open_snapshot_identifier"): False,
        ("repository_snapshot", "snapshot_identifier_visibility_date"): "2026-07-09",
        ("repository_snapshot", "exact_4open_snapshot_identifier_available"): False,
        ("repository_snapshot", "submission_preparation_commit_anchor"): "ea7e11a5f5f041d96a611014dd14cb5e44848524",
        ("repository_snapshot", "submission_preparation_commit_anchor_is_exact_4open_snapshot"): False,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("claim_locks", "original_dltb_public_release_supported"): False,
        ("claim_locks", "all_licence_and_rights_blockers_closed"): False,
        ("claim_locks", "licence_and_generated_rights_blockers_closed"): True,
        ("claim_locks", "reviewer_readme_direct_link_author_confirmed"): True,
        ("claim_locks", "reviewer_link_blocker_closed_by_author_confirmation"): True,
        ("claim_locks", "reviewer_browser_link_verified"): False,
        ("claim_locks", "exact_4open_snapshot_identifier_backfilled"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    status = payload.get("status")
    if status == "submission_ready":
        missing_tokens.append(
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: status=submission_ready"
        )
    if nested_value(payload, ("submission_blockers", "formal_submission_blocked")) is False:
        missing_tokens.append(
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: formal_submission_blocked=False"
        )
    if (
        nested_value(payload, ("data_boundary", "original_bishan_dltb_public_release_allowed")) is True
        or nested_value(payload, ("data_boundary", "original_dongxing_dltb_public_release_allowed")) is True
    ):
        missing_tokens.append(
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: original DLTB public release is not allowed"
        )

    licence_path = root / "LICENSE"
    if not licence_path.exists():
        missing_tokens.append(
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: "
            "missing repository Apache-2.0 LICENSE file"
        )
    else:
        licence_text = read_text(licence_path)
        for token in (
            "Apache License",
            "Version 2.0, January 2004",
            "http://www.apache.org/licenses/",
        ):
            if token not in licence_text:
                missing_tokens.append(
                    f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: "
                    f"LICENSE missing {token}"
                )

    for key in ("licence_state", "rights_state", "data_boundary", "repository_snapshot"):
        if not isinstance(payload.get(key), dict):
            missing_tokens.append(f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: {key}")
    required_before = payload.get("required_before_formal_submission")
    if not isinstance(required_before, list) or len(required_before) < 6:
        missing_tokens.append(
            f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON}: required_before_formal_submission"
        )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD}:{line_no}: {line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_public_release_rights_gate_current",
            False,
            "forbidden public-release rights gate wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_public_release_rights_gate_current",
            False,
            "Paper10 public-release rights gate gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_public_release_rights_gate_current",
        True,
        "Paper10 public-release rights gate is current and no-go guarded",
    )

def check_paper10_dltb_leakage_evidence_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD,
        PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON,
        PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_dltb_leakage_evidence_audit_current",
            False,
            "missing Paper10 DLTB leakage evidence audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_dltb_leakage_evidence_audit_current",
            False,
            f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    normalized_text = " ".join(text.split())
    required_tokens = [
        "Paper10 DLTB leakage evidence audit",
        "Status: tracked_public_package_leakage_evidence_recorded_final_archive_pending",
        "Computers, Environment and Urban Systems",
        "Elsevier",
        "Option B",
        "Apache-2.0",
        "CC0-1.0",
        "confidential_no_external_access",
        "tracked public package contains no original Bishan or Dongxing DLTB payload",
        "contains no GPKG/GDB/SHP/DBF/PRJ/CPG geospatial source payloads",
        "small reviewer smoke Tool2 files",
        "exact 4open submission snapshot",
        "DLTB-leakage content review",
        "Original DLTB public release is not allowed",
        "Formal submission remains blocked",
        "not final submission approval",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD}: {token}")

    expected_values = {
        ("artifact_type",): "paper10_dltb_leakage_evidence_audit",
        ("date",): "2026-07-09",
        ("status",): "tracked_public_package_leakage_evidence_recorded_final_archive_pending",
        ("target_journal",): "Computers, Environment and Urban Systems",
        ("journal_data_policy", "publisher"): "Elsevier",
        ("journal_data_policy", "research_data_policy_label"): "Option B",
        ("journal_data_policy", "checked_date"): "2026-07-09",
        ("source_boundary", "git_commit_scanned"): "81eee5a729d994559cd4f81ee76f856747fe0dea",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("source_boundary", "author_decisions_invented"): False,
        ("rights_terms", "code"): "Apache-2.0",
        ("rights_terms", "generated_non_dltb_artifacts"): "CC0-1.0",
        ("rights_terms", "checkpoint_model_weights"): "CC0-1.0",
        ("rights_terms", "must_not_relicense_original_dltb"): True,
        ("raw_dltb_boundary", "original_bishan_dltb_external_access"): "confidential_no_external_access",
        ("raw_dltb_boundary", "original_dongxing_dltb_external_access"): "confidential_no_external_access",
        ("raw_dltb_boundary", "original_bishan_dltb_public_release_allowed"): False,
        ("raw_dltb_boundary", "original_dongxing_dltb_public_release_allowed"): False,
        ("raw_dltb_boundary", "original_dltb_reviewer_access_available"): False,
        ("public_package_evidence", "reviewer_readme_direct_link"): "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md",
        ("public_package_evidence", "tracked_public_package_contains_original_dltb"): False,
        ("public_package_evidence", "tracked_public_package_contains_geospatial_source_payloads"): False,
        ("public_package_evidence", "small_reviewer_smoke_tool2_files_are_not_full_bishan_tool2"): True,
        ("public_package_evidence", "full_bishan_tool2_public_deposit_leakage_check_completed"): False,
        ("public_package_evidence", "dongxing_derived_public_deposit_leakage_check_completed"): False,
        ("public_package_evidence", "final_4open_snapshot_backfill_required"): True,
        ("public_package_evidence", "final_archive_checksum_backfill_required"): True,
        ("submission_gate", "formal_submission_blocked"): True,
        ("submission_gate", "preflight_pass_does_not_mean_submission_ready"): True,
        ("claim_locks", "tracked_public_package_leakage_evidence_recorded"): True,
        ("claim_locks", "final_archive_leakage_evidence_recorded"): False,
        ("claim_locks", "original_dltb_public_release_supported"): False,
        ("claim_locks", "derived_public_deposit_supported_without_leakage_review"): False,
        ("claim_locks", "final_submission_readiness_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    for keys in (
        ("public_package_evidence", "tracked_original_dltb_path_matches"),
        ("public_package_evidence", "tracked_geospatial_source_payload_matches"),
    ):
        observed = nested_value(payload, keys)
        if observed != []:
            missing_tokens.append(
                f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    if payload.get("status") == "submission_ready":
        missing_tokens.append(
            f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: status=submission_ready"
        )
    if nested_value(payload, ("submission_gate", "formal_submission_blocked")) is False:
        missing_tokens.append(
            f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: formal_submission_blocked=False"
        )
    if (
        nested_value(payload, ("raw_dltb_boundary", "original_bishan_dltb_public_release_allowed")) is True
        or nested_value(payload, ("raw_dltb_boundary", "original_dongxing_dltb_public_release_allowed")) is True
        or nested_value(payload, ("public_package_evidence", "tracked_public_package_contains_original_dltb")) is True
        or nested_value(payload, ("raw_dltb_boundary", "original_bishan_dltb_external_access")) != "confidential_no_external_access"
        or nested_value(payload, ("raw_dltb_boundary", "original_dongxing_dltb_external_access")) != "confidential_no_external_access"
    ):
        missing_tokens.append(
            f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: original DLTB public release is not allowed"
        )

    required_before = payload.get("required_before_formal_submission")
    if not isinstance(required_before, list) or len(required_before) < 5:
        missing_tokens.append(
            f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: required_before_formal_submission"
        )
    else:
        for token in (
            "exact 4open submission snapshot",
            "DLTB-leakage content review",
            "target-journal acceptance",
        ):
            if not any(token in item for item in required_before):
                missing_tokens.append(
                    f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON}: required_before_formal_submission missing {token}"
                )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD}:{line_no}: {line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_dltb_leakage_evidence_audit_current",
            False,
            "forbidden DLTB leakage audit wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_dltb_leakage_evidence_audit_current",
            False,
            "Paper10 DLTB leakage evidence audit gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_dltb_leakage_evidence_audit_current",
        True,
        "Paper10 DLTB leakage evidence audit is current and no-go guarded",
    )


def check_paper10_ceus_confidential_dltb_acceptance_packet_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD,
        PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON,
        PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_MD,
        PAPER10_DLTB_LEAKAGE_EVIDENCE_AUDIT_JSON,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_MD,
        PAPER10_PUBLIC_RELEASE_RIGHTS_GATE_JSON,
        PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_confidential_dltb_acceptance_packet_current",
            False,
            "missing Paper10 CEUS confidential-DLTB acceptance packet files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_ceus_confidential_dltb_acceptance_packet_current",
            False,
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    normalized_text = " ".join(text.split())
    required_tokens = [
        "Paper10 CEUS confidential-DLTB acceptance packet",
        "Status: ceus_confidential_dltb_acceptance_packet_prepared_not_editor_accepted",
        "Computers, Environment and Urban Systems",
        "Elsevier research data policy Option B",
        "confidential_no_external_access",
        "cannot be provided externally",
        "no request-based route for raw DLTB",
        "Apache-2.0",
        "CC0-1.0",
        "public code, a small reviewer smoke dataset",
        "target-journal acceptance is not recorded",
        "Formal submission remains blocked",
        "not final submission approval",
    ]
    for token in required_tokens:
        if token not in normalized_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD}: {token}"
            )

    expected_values = {
        ("artifact_type",): "paper10_ceus_confidential_dltb_acceptance_packet",
        ("date",): "2026-07-09",
        ("status",): "ceus_confidential_dltb_acceptance_packet_prepared_not_editor_accepted",
        ("target_journal",): "Computers, Environment and Urban Systems",
        ("journal_data_policy", "publisher"): "Elsevier",
        ("journal_data_policy", "research_data_policy_label"): "Option B",
        ("journal_data_policy", "checked_date"): "2026-07-09",
        ("source_boundary", "git_commit_scanned"): "dfc9a2334ecd896aa21e9a2b89720cc6bf740fb9",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("source_boundary", "author_decisions_invented"): False,
        ("raw_dltb_boundary", "original_bishan_dltb_external_access"): "confidential_no_external_access",
        ("raw_dltb_boundary", "original_dongxing_dltb_external_access"): "confidential_no_external_access",
        ("raw_dltb_boundary", "original_bishan_dltb_public_release_allowed"): False,
        ("raw_dltb_boundary", "original_dongxing_dltb_public_release_allowed"): False,
        ("raw_dltb_boundary", "original_dltb_reviewer_access_available"): False,
        ("raw_dltb_boundary", "request_based_access_route_available"): False,
        ("public_compensation_package", "reviewer_readme_direct_link"): "https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md",
        ("public_compensation_package", "code_licence"): "Apache-2.0",
        ("public_compensation_package", "generated_non_dltb_artifact_terms"): "CC0-1.0",
        ("public_compensation_package", "does_not_replace_raw_dltb_access"): True,
        ("submission_text", "contains_request_based_raw_dltb_route"): False,
        ("editor_acceptance", "target_journal_editor_acceptance_received"): False,
        ("editor_acceptance", "communication_with_editor_completed"): False,
        ("editor_acceptance", "author_must_disclose_in_submission_system"): True,
        ("editor_acceptance", "editor_must_decide_whether_limitation_is_acceptable"): True,
        ("submission_gate", "formal_submission_blocked"): True,
        ("submission_gate", "preflight_pass_does_not_mean_submission_ready"): True,
        ("claim_locks", "ceus_disclosure_text_prepared"): True,
        ("claim_locks", "target_journal_acceptance_recorded"): False,
        ("claim_locks", "original_dltb_external_access_supported"): False,
        ("claim_locks", "final_submission_readiness_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    for keys in (
        ("submission_text", "data_statement"),
        ("submission_text", "cover_letter_disclosure"),
        ("submission_text", "submission_system_research_data_response"),
    ):
        observed = nested_value(payload, keys)
        if not isinstance(observed, str) or "cannot be provided externally" not in observed:
            missing_tokens.append(
                f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: "
                f"{'.'.join(keys)} missing external-access restriction"
            )
        if isinstance(observed, str) and "available upon request" in observed.lower():
            missing_tokens.append(
                f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: "
                f"{'.'.join(keys)} uses vague request wording"
            )

    required_before = payload.get("required_before_formal_submission")
    if not isinstance(required_before, list) or len(required_before) < 5:
        missing_tokens.append(
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: required_before_formal_submission"
        )
    else:
        for token in (
            "target-journal/editor acceptance",
            "final 4open archive snapshot",
            "keep raw Bishan and Dongxing DLTB outside",
        ):
            if not any(token in item for item in required_before):
                missing_tokens.append(
                    f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: required_before_formal_submission missing {token}"
                )

    if payload.get("status") != "ceus_confidential_dltb_acceptance_packet_prepared_not_editor_accepted":
        missing_tokens.append(
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: target-journal acceptance is not recorded"
        )
    if nested_value(payload, ("editor_acceptance", "target_journal_editor_acceptance_received")) is not False:
        missing_tokens.append(
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: target-journal acceptance is not recorded"
        )
    if nested_value(payload, ("submission_gate", "formal_submission_blocked")) is not True:
        missing_tokens.append(
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: formal_submission_blocked=False"
        )
    if (
        nested_value(payload, ("raw_dltb_boundary", "original_bishan_dltb_external_access")) != "confidential_no_external_access"
        or nested_value(payload, ("raw_dltb_boundary", "original_dongxing_dltb_external_access")) != "confidential_no_external_access"
        or nested_value(payload, ("raw_dltb_boundary", "request_based_access_route_available")) is not False
    ):
        missing_tokens.append(
            f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_JSON}: original DLTB external access is not allowed"
        )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_CEUS_CONFIDENTIAL_DLTB_ACCEPTANCE_PACKET_MD}:{line_no}: {line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_ceus_confidential_dltb_acceptance_packet_current",
            False,
            "forbidden CEUS confidential-DLTB acceptance wording: " + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_confidential_dltb_acceptance_packet_current",
            False,
            "Paper10 CEUS confidential-DLTB acceptance packet gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_confidential_dltb_acceptance_packet_current",
        True,
        "Paper10 CEUS confidential-DLTB acceptance packet is current and no-go guarded",
    )


def check_paper10_post_guard_submission_readiness_refresh_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD,
        PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON,
        SUBMISSION_BLOCKER_DECISION_PACKET,
        DATA_ACCESS_RIGHTS_REGISTER,
        PAPER10_SUBMISSION_READINESS_BOUNDARY,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "missing Paper10 post-guard submission-readiness refresh files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    required_tokens = [
        "Paper10 post-guard submission-readiness refresh",
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
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_JSON.name,
        PAPER10_POST_GUARD_EXPERIMENT_CLOSURE_REFRESH_MD.name,
        SUBMISSION_BLOCKER_DECISION_PACKET.name,
        DATA_ACCESS_RIGHTS_REGISTER.name,
        PAPER10_SUBMISSION_READINESS_BOUNDARY.name,
        PAPER10_FINAL_FIGURE_TABLE_EXPORT_PACKAGE.name,
        "not final submission readiness",
        "Do not treat this refresh as final submission readiness.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "Do not claim robust Bishan-to-Dongxing transfer superiority.",
        "Do not claim deployment-ready cadastral planning.",
        "Do not claim a universal fixed switch margin.",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-07-08",
        ("refresh_type",): "post_guard_submission_readiness_refresh",
        ("status",): "not_submission_ready",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "submission_approval"): False,
        ("algorithm_state", "post_guard_bounded_algorithm_closure_current"): True,
        ("algorithm_state", "resume_broad_algorithm_redesign"): False,
        ("algorithm_state", "primary_guard", "audit_set"): "rewardtop7",
        ("algorithm_state", "primary_guard", "switch_margin"): 1.5,
        ("algorithm_state", "primary_guard", "n_seeds"): 20,
        ("algorithm_state", "primary_guard", "mean_delta_vs_baseline"): 6.304141816329158,
        ("submission_state", "final_submission_blocked"): True,
        ("submission_state", "status_reason"): "author decisions unresolved",
        ("submission_state", "preflight_pass_does_not_mean_submission_ready"): True,
        ("claim_locks", "final_submission_readiness_supported"): False,
        ("claim_locks", "direct_50state_scaleup_supported"): False,
        ("claim_locks", "robust_transfer_superiority_supported"): False,
        ("claim_locks", "deployment_ready_supported"): False,
        ("claim_locks", "universal_fixed_margin_supported"): False,
    }
    for keys, expected in expected_values.items():
        observed = nested_value(payload, keys)
        if observed != expected:
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                f"{'.'.join(keys)}={observed}"
            )

    expected_fields = [
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
    fields = payload.get("author_decision_fields")
    if not isinstance(fields, list):
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
            "author_decision_fields"
        )
        fields = []
    observed_fields = [
        field.get("field") for field in fields if isinstance(field, dict)
    ]
    if observed_fields != expected_fields:
        missing_tokens.append(
            f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
            f"author_decision_fields={observed_fields}"
        )
    for field in fields:
        if not isinstance(field, dict):
            missing_tokens.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                "non-dict author_decision_fields row"
            )
            continue
        name = field.get("field")
        for key, expected in (
            ("status", "unresolved"),
            ("must_be_author_supplied", True),
            ("closeout_required_before_submission", True),
        ):
            if field.get(key) != expected:
                missing_tokens.append(
                    f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_JSON}: "
                    f"author_decision_fields.{name}.{key}={field.get(key)}"
                )

    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if is_post_guard_submission_readiness_positive_overclaim(line):
            hits.append(
                f"{PAPER10_POST_GUARD_SUBMISSION_READINESS_REFRESH_MD}:{line_no}: "
                f"{line.strip()}"
            )
    if hits:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "forbidden post-guard submission-readiness wording: "
            + " | ".join(hits),
        )

    if missing_tokens:
        return CheckResult(
            "paper10_post_guard_submission_readiness_refresh_current",
            False,
            "Paper10 post-guard submission-readiness refresh gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_post_guard_submission_readiness_refresh_current",
        True,
        "Paper10 post-guard submission-readiness refresh is current and no-go guarded",
    )


def check_paper10_true_reward_guard_readiness_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_TRUE_REWARD_GUARD_READINESS_MD,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_true_reward_guard_readiness_current",
            False,
            "missing Paper10 true-reward guard readiness files: "
            + ", ".join(missing),
        )

    audit_text = read_text(root / PAPER10_TRUE_REWARD_GUARD_READINESS_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_TRUE_REWARD_GUARD_READINESS_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_true_reward_guard_readiness_current",
            False,
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        doc_text = read_text(root / doc)
        if PAPER10_TRUE_REWARD_GUARD_READINESS_MD.name not in doc_text:
            missing_tokens.append(f"{doc}: {PAPER10_TRUE_REWARD_GUARD_READINESS_MD.name}")

    required_audit_tokens = [
        "Paper10 true-reward guard readiness audit",
        "source-derived true-reward guard readiness audit",
        "`rewardtop7 margin=1.50`",
        "`rewardtop7 margin=1.60`",
        "not final submission readiness",
        "Do not claim a universal fixed switch margin.",
        "Do not claim direct 50-state Bishan scale-up success.",
        "20 / 20",
        "18 / 20",
        "2 / 20",
        "## Primary Paired Statistics",
        "bootstrap 95% CI lower",
        "switch rate",
        "simplified robust default",
        "mean audited actions",
    ]
    for token in required_audit_tokens:
        if token not in audit_text:
            missing_tokens.append(f"{PAPER10_TRUE_REWARD_GUARD_READINESS_MD}: {token}")

    expected_values = {
        ("status",): "source-derived true-reward guard readiness audit",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "algorithm_redesign_performed"): False,
        ("primary_guard", "setting"): "bishan_20x16_top5",
        ("primary_guard", "audit_set"): "rewardtop7",
        ("primary_guard", "switch_margin"): 1.5,
        ("primary_guard", "n_seeds"): 20,
        ("primary_guard", "seed_wins"): 20,
        ("primary_paired_stats", "n"): 20,
        ("primary_paired_stats", "wins"): 20,
        ("primary_paired_stats", "losses"): 0,
        ("primary_paired_stats", "ties"): 0,
        ("small_scale_guard", "setting"): "bishan_10x12_top4",
        ("small_scale_guard", "audit_set"): "rewardtop7",
        ("small_scale_guard", "switch_margin"): 1.6,
        ("small_scale_guard", "n_seeds"): 20,
        ("small_scale_guard", "seed_wins"): 18,
        ("small_scale_guard", "seed_losses"): 2,
        ("claim_gates", "primary_algorithm_candidate_supported"): True,
        ("claim_gates", "primary_paired_statistics_supported"): True,
        ("claim_gates", "small_scale_consistency_supported"): True,
        ("claim_gates", "setting_specific_margin_required"): True,
        ("claim_gates", "universal_fixed_margin_supported"): False,
        ("claim_gates", "direct_50state_scaleup_supported"): False,
        ("claim_gates", "robust_transfer_superiority_supported"): False,
        ("claim_gates", "deployment_ready_cadastral_planning_supported"): False,
        ("claim_gates", "final_submission_readiness_supported"): False,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    primary = payload.get("primary_guard", {})
    if float(primary.get("mean_delta_vs_baseline", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: primary mean delta is not positive"
        )
    if float(primary.get("min_seed_delta_vs_baseline", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: primary min seed delta is not positive"
        )

    primary_stats = payload.get("primary_paired_stats", {})
    primary_ci = primary_stats.get("bootstrap_95ci_delta", [0.0, 0.0])
    if float(primary_stats.get("mean_delta", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: primary paired mean delta is not positive"
        )
    if float(primary_stats.get("min_delta", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: primary paired min delta is not positive"
        )
    if len(primary_ci) != 2 or float(primary_ci[0]) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: primary paired bootstrap CI lower is not positive"
        )

    small = payload.get("small_scale_guard", {})
    if float(small.get("mean_delta_vs_baseline", 0.0)) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: small-scale mean delta is not positive"
        )
    small_ci = small.get("bootstrap_95ci_delta", [0.0, 0.0])
    if len(small_ci) != 2 or float(small_ci[0]) <= 0.0:
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: small-scale bootstrap CI lower is not positive"
        )
    if int(small.get("seed_wins", 0)) <= int(small.get("seed_losses", 0)):
        missing_tokens.append(
            f"{PAPER10_TRUE_REWARD_GUARD_READINESS_JSON}: small-scale wins do not exceed losses"
        )

    for line_no, line in enumerate(audit_text.splitlines(), start=1):
        if is_true_reward_guard_positive_overclaim(line):
            missing_tokens.append(
                f"{PAPER10_TRUE_REWARD_GUARD_READINESS_MD}:{line_no}: "
                f"forbidden true-reward guard wording: {line.strip()}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_true_reward_guard_readiness_current",
            False,
            "Paper10 true-reward guard readiness gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_true_reward_guard_readiness_current",
        True,
        "Paper10 true-reward guard readiness audit is current and claim-bounded",
    )

CEUS_CLEAN_MANUSCRIPT_INTERNAL_SECTIONS = (
    "## Source controls used for this draft",
    "## Terminology Ledger",
    "## Claim-Evidence and Unresolved Blockers",
    "## Author Handoff Notes",
)

CEUS_CLEAN_MANUSCRIPT_DATA_AVAILABILITY_TOKENS = (
    "4open README.md direct link",
    "b5457460e747cc320e2246dbfcd30e082851c01a",
    "Apache-2.0",
    "CC0-1.0",
    "full Bishan Tool2",
    "prepared GPKG-root geospatial inputs",
    "Dongxing/Neijiang prepared data",
    "DLTB-leakage check evidence",
    "confidential_no_external_access",
    "CEUS/Elsevier Research Data Policy Option B",
    "e0_paper10_ceus_submission_policy_verification_2026-07-09",
    "cannot be provided externally",
    "no request-based route for raw DLTB",
)

CEUS_CLEAN_MANUSCRIPT_PENDING_AUTHOR_SECTIONS = (
    "## Declaration of generative AI and AI-assisted technologies",
    "## CRediT authorship contribution statement",
    "## Declaration of competing interest",
    "## Acknowledgements",
    "## Funding",
)

CEUS_CLEAN_MANUSCRIPT_REQUIRED_CAPTIONS = (
    "Figure 1. Monitor-gated GeoJEPA-MPC workflow for farmland layout planning",
    "Figure 2. Bishan 20x16/top5 oracle action-audit guard result",
    "Figure 3. Bishan Stage 3 boundary rows and candidate-score sweep",
    "Figure 4. Dongxing/Neijiang return-label scaling",
    "Supplementary Figure S1. Dongxing/Neijiang low-label transfer stress test",
    "Table 1. Bishan monitor-selected value-label gates",
    "Table 2. Bishan 20-seed oracle action-audit guard and legacy value-filter anchor",
    "Table 3. Dongxing/Neijiang return-label scaling summary",
    "Supplementary Table S1. Stage 3 seed-level rollout rewards",
    "Supplementary Table S2. Dongxing/Neijiang low-label transfer stress-test summary",
    "Supplementary Table S3. Mechanism ablation and control comparison",
)


CEUS_CLEAN_MANUSCRIPT_REQUIRED_SECTION_ORDER = (
    "## Title page",
    "## Highlights",
    "## Abstract",
    "## Keywords",
    "## 1. Introduction",
    "## 2. Materials and methods",
    "## 3. Results",
    "## 4. Discussion",
    "## 5. Conclusion",
    "## Data and Code Availability",
    "## Declaration of generative AI and AI-assisted technologies",
    "## CRediT authorship contribution statement",
    "## Declaration of competing interest",
    "## Acknowledgements",
    "## Funding",
    "## References",
    "## Figure captions",
    "## Table captions",
    "## Clean-draft boundary",
)


def markdown_bullets(section_text: str) -> list[str]:
    return [
        line.strip()[2:].strip()
        for line in section_text.splitlines()
        if line.strip().startswith("- ")
    ]


def check_paper10_ceus_clean_main_manuscript_draft_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT,
        PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_ASSEMBLY_DRAFT,
        PAPER10_CEUS_HIGHLIGHTS,
        README,
        MANIFEST,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_clean_main_manuscript_draft_current",
            False,
            "missing Paper10 CEUS clean main manuscript draft files: "
            + ", ".join(missing),
        )

    draft_text = read_text(root / PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT)
    highlights_text = read_text(root / PAPER10_CEUS_HIGHLIGHTS)
    missing_tokens = []

    source_assembly_name = (
        PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_ASSEMBLY_DRAFT.name
    )
    for doc in (README, MANIFEST, DATA_AVAILABILITY):
        doc_text = read_text(root / doc)
        if PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT.name not in doc_text:
            missing_tokens.append(
                f"{doc}: {PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT.name}"
            )
        if source_assembly_name not in doc_text:
            missing_tokens.append(
                f"{doc}: missing clean-draft source assembly index link: "
                f"{source_assembly_name}"
            )

    required_tokens = [
        "Status: clean CEUS main-manuscript draft, updated by the 2026-07-09 CEUS policy verification, guard information-set audit and proxy guard dynamic baseline stress audit for bounded formal submission",
        "Source assembly: `e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`",
        "## Title page",
        "## Highlights",
        "## Abstract",
        "## Keywords",
        "## Data and Code Availability",
        "## Declaration of generative AI and AI-assisted technologies",
        "## CRediT authorship contribution statement",
        "## Declaration of competing interest",
        "## Funding",
        "## References",
        "references/paper10_verified_references_2026-06-09.bib",
        "references/paper10_local_sources_2026-06-09.bib",
        "journal-formatted reference list",
        "## Clean-draft boundary",
        "suitable for formal CEUS submission as a bounded manuscript package",
        "4open README.md direct link",
        "b5457460e747cc320e2246dbfcd30e082851c01a",
        "Apache-2.0",
        "CC0-1.0",
        "DLTB-leakage check evidence",
        "does not require pre-submission editor acceptance",
        "e0_paper10_ceus_submission_policy_verification_2026-07-09",
        "no request-based route for raw DLTB",
        "Pending author decision",
        "diagnostic-only two-sided sign-test readout was 1.0000",
        "e0_paper10_ceus_review_response_experiment_package_2026-07-09",
        "e0_paper10_guard_information_set_audit_2026-07-09",
        "e0_paper10_proxy_guard_dynamic_baseline_audit_2026-07-09",
        "20-seed rewardtop7 true-reward margin guard",
        "oracle/action-audit reward evidence",
        "not as a standalone no-oracle planner",
        "true-reward margin guard reached 72.1918 mean reward",
        "model-reward and candidate-score proxy guards reached 65.2734 and 63.4116 mean reward",
        "bootstrap 95% CI 4.1401 to 8.5056",
        "does not support a claim that the value filter improved every seed or established inferential superiority",
        "not broad scale-up, transfer superiority or operational cadastral deployment",
    ]
    for token in required_tokens:
        if token not in draft_text:
            missing_tokens.append(f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: {token}")

    data_availability = markdown_section_outside_code_fences(
        draft_text, "## Data and Code Availability"
    )
    for token in CEUS_CLEAN_MANUSCRIPT_DATA_AVAILABILITY_TOKENS:
        if token not in data_availability:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"Data and Code Availability missing route: {token}"
            )

    for section in CEUS_CLEAN_MANUSCRIPT_PENDING_AUTHOR_SECTIONS:
        section_text = markdown_section_outside_code_fences(draft_text, section)
        normalized_section = section_text.lower()
        if (
            "pending author decision" not in normalized_section
            and "author decision pending" not in normalized_section
        ):
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"pending author decision missing in section: {section}"
            )

    for caption in CEUS_CLEAN_MANUSCRIPT_REQUIRED_CAPTIONS:
        if caption not in draft_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"missing required figure/table caption: {caption}"
            )

    section_positions = markdown_heading_positions_outside_code_fences(
        draft_text, CEUS_CLEAN_MANUSCRIPT_REQUIRED_SECTION_ORDER
    )
    for heading in CEUS_CLEAN_MANUSCRIPT_REQUIRED_SECTION_ORDER:
        if heading not in section_positions:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"CEUS clean manuscript section order missing: {heading}"
            )
    for before, after in zip(
        CEUS_CLEAN_MANUSCRIPT_REQUIRED_SECTION_ORDER,
        CEUS_CLEAN_MANUSCRIPT_REQUIRED_SECTION_ORDER[1:],
    ):
        if before not in section_positions or after not in section_positions:
            continue
        if section_positions[before] >= section_positions[after]:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                "CEUS clean manuscript section order violation: "
                f"{before} -> {after} "
                f"(lines {section_positions[before]}, {section_positions[after]})"
            )

    boundary_line = section_positions.get("## Clean-draft boundary")
    if boundary_line is not None:
        in_fence = False
        for line_no, line in enumerate(draft_text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence or line_no <= boundary_line:
                continue
            if stripped.startswith("## "):
                missing_tokens.append(
                    f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                    "unexpected section after clean-draft boundary: "
                    f"{stripped}"
                )

    abstract = markdown_section_outside_code_fences(draft_text, "## Abstract")
    if not abstract:
        missing_tokens.append(f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: ## Abstract")
    else:
        word_count = markdown_word_count(abstract)
        if word_count > 250:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"abstract word count exceeds 250 ({word_count})"
            )

    highlights_section = markdown_section_outside_code_fences(draft_text, "## Highlights")
    draft_highlights = markdown_bullets(highlights_section)
    separate_highlights = [
        line.strip()[2:].strip() if line.strip().startswith("- ") else line.strip()
        for line in highlights_text.splitlines()
        if line.strip()
    ]
    if len(draft_highlights) < 3 or len(draft_highlights) > 5:
        missing_tokens.append(
            f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
            f"highlights count={len(draft_highlights)}"
        )
    for index, highlight in enumerate(draft_highlights, start=1):
        if len(highlight) > 85:
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"highlight exceeds 85 characters at item {index}: {len(highlight)}"
            )
    if separate_highlights != draft_highlights:
        missing_tokens.append(
            f"{PAPER10_CEUS_HIGHLIGHTS}: separate highlights do not match clean draft"
        )

    for section in CEUS_CLEAN_MANUSCRIPT_INTERNAL_SECTIONS:
        if has_markdown_heading_outside_code_fences(draft_text, section):
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}: "
                f"internal-only manuscript section: {section.lstrip('#').strip()}"
            )

    for line_no, line in enumerate(draft_text.splitlines(), start=1):
        for match in PUBLIC_PLACEHOLDER_PATTERN.finditer(line):
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}:{line_no}: "
                f"unresolved bracket placeholder {match.group(0)}"
            )
        if is_submission_readiness_positive_claim(line):
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}:{line_no}: "
                f"forbidden submission-readiness wording: {line.strip()}"
            )
        if is_ceus_baseline_positive_overclaim(line):
            missing_tokens.append(
                f"{PAPER10_CEUS_CLEAN_MAIN_MANUSCRIPT_DRAFT}:{line_no}: "
                f"forbidden CEUS clean manuscript overclaim: {line.strip()}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_clean_main_manuscript_draft_current",
            False,
            "Paper10 CEUS clean main manuscript draft gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_clean_main_manuscript_draft_current",
        True,
        "Paper10 CEUS clean main manuscript draft is current and claim-bounded",
    )

def check_paper10_anchor_raw_rollout_consistency_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD,
        PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_MD,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_anchor_raw_rollout_consistency_audit_current",
            False,
            "missing Paper10 anchor raw-rollout consistency audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_anchor_raw_rollout_consistency_audit_current",
            False,
            f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 anchor raw-rollout consistency audit",
        "source-derived consistency audit",
        "does not add a new experimental claim",
        "No rollout was rerun",
        "Summary match: PASS",
        "Stage 3 frozen-anchor match: PASS",
        "| total_reward_mean | 69.4705 |",
        "| total_reward_std_sample | 1.0004 |",
        "| 0 | 100 | 67.7135 | 67.7135 | 0.0000 |",
        "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json",
        "e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json",
        "e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json",
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        "paper10_geojepa_mpc.experiments.anchor_raw_rollout_consistency_audit",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "source-derived consistency audit",
        ("overall_consistency_pass",): True,
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("summary_consistency", "matches_raw"): True,
        ("stage3_consistency", "matches_raw"): True,
        ("stage3_consistency", "anchor_role"): "frozen_anchor",
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    raw_seed_summaries = payload.get("raw_seed_summaries")
    if not isinstance(raw_seed_summaries, list) or len(raw_seed_summaries) != 5:
        missing_tokens.append(
            f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
            f"len(raw_seed_summaries)="
            f"{len(raw_seed_summaries) if isinstance(raw_seed_summaries, list) else 'non-list'}"
        )
        raw_seed_summaries = []
    expected_rewards = [
        67.7134969354234,
        70.2252087804031,
        69.7218379673849,
        69.82450306303002,
        69.86768346643231,
    ]
    if [row.get("seed") for row in raw_seed_summaries] != [0, 1, 2, 3, 4]:
        missing_tokens.append(
            f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: raw seed order"
        )
    for index, expected_reward in enumerate(expected_rewards):
        if index >= len(raw_seed_summaries):
            continue
        row = raw_seed_summaries[index]
        if row.get("steps_run") != 100 or row.get("reported_steps_run") != 100:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                f"seed {index} steps"
            )
        for key in ("total_reward_from_steps", "reported_total_reward"):
            value = row.get(key)
            if not isinstance(value, (int, float)) or abs(
                float(value) - expected_reward
            ) > 1e-8:
                missing_tokens.append(
                    f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                    f"seed {index} {key}={value}"
                )
        delta = row.get("abs_reported_minus_steps")
        if not isinstance(delta, (int, float)) or float(delta) > 1e-8:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                f"seed {index} abs_reported_minus_steps={delta}"
            )

    expected_aggregate = {
        "n_episodes": 5,
        "total_reward_mean": 69.47054604253474,
        "total_reward_std_sample": 1.0003610285842477,
        "total_reward_min": 67.7134969354234,
        "total_reward_max": 70.2252087804031,
        "slope_change_pct_mean": -1.2507267926554344,
        "cont_change_mean": 0.019233605411040598,
        "baimu_area_change_ha_mean": -207.263937322613,
        "elapsed_sec_mean": 279.6767912999843,
        "zero_swap_steps_sum": 0,
        "negative_zero_swap_steps_sum": 0,
    }
    raw_aggregate = payload.get("raw_aggregate", {})
    for key, expected in expected_aggregate.items():
        value = raw_aggregate.get(key)
        if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-8:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                f"raw_aggregate.{key}={value}"
            )

    for section_name in ("summary_consistency", "stage3_consistency"):
        section = payload.get(section_name, {})
        seed_rewards = section.get("seed_rewards")
        if not isinstance(seed_rewards, list) or len(seed_rewards) != 5:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                f"{section_name}.seed_rewards"
            )
            continue
        for index, expected_reward in enumerate(expected_rewards):
            value = seed_rewards[index]
            if not isinstance(value, (int, float)) or abs(float(value) - expected_reward) > 1e-8:
                missing_tokens.append(
                    f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                    f"{section_name}.seed_rewards[{index}]={value}"
                )
        aggregate_deltas = section.get("aggregate_deltas", {})
        for key in expected_aggregate:
            value = aggregate_deltas.get(key)
            if not isinstance(value, (int, float)) or abs(float(value)) > 1e-8:
                missing_tokens.append(
                    f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON}: "
                    f"{section_name}.aggregate_deltas.{key}={value}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_anchor_raw_rollout_consistency_audit_current",
            False,
            "Paper10 anchor raw-rollout consistency audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_anchor_raw_rollout_consistency_audit_current",
        True,
        "Paper10 anchor raw-rollout consistency audit is current and claim-bounded",
    )


def check_paper10_manuscript_result_tables_freeze_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON,
        PAPER10_CLAIM_SOURCE_AUDIT_JSON,
        PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_manuscript_result_tables_freeze_current",
            False,
            "missing Paper10 manuscript result tables freeze files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD)
    try:
        payload = json.loads(read_text(root / PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_manuscript_result_tables_freeze_current",
            False,
            f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    freeze_name = PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if freeze_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {freeze_name}")

    required_tokens = [
        "Paper10 manuscript result tables freeze",
        "source-derived table freeze",
        "does not add a new experimental claim",
        "No rollout was rerun",
        "raw-rollout consistency: PASS",
        "Table 1. Bishan anchor versus matched baseline",
        "Table 2. Stage 3 boundary rows",
        "Table 3. Claim status for manuscript conversion",
        "Algorithm-readiness addendum: current true-reward guard",
        ORIGINAL_VISION_STAGE3_CONFIRMATORY_ROLLOUTS_JSON.name,
        PAPER10_CLAIM_SOURCE_AUDIT_JSON.name,
        PAPER10_ANCHOR_RAW_ROLLOUT_CONSISTENCY_AUDIT_JSON.name,
        PAPER10_TRUE_REWARD_GUARD_READINESS_JSON.name,
        "matched_paper9_rank_seed2028_baseline | 67.5437 | 7.2246",
        "bishan_20x16_top5_frozen_anchor | 69.4705 | 1.0004 | 1.9269 | PASS",
        "frontier_random050_50x16_h5_seed48_f050 | confirmatory_pass | 50 | 16 | 6 | 64.2960",
        "frontier_random050_50x24_h5_seed47_f075 | confirmatory_pass | 50 | 24 | 12 | 66.2544",
        "frontier_random050_50x24_h5_seed48_f075 | diagnostic_near_pass | 50 | 24 | 12 | 67.4913",
        "boundary evidence; below matched baseline",
        "diagnostic near-pass only; must not be pooled",
        "Bishan 20x16/top5 reward and stability anchor | supported",
        "Stage 3 confirmatory 50-state rows beat the matched baseline | not supported",
        "Dongxing/Neijiang return-label scaling | supported descriptively",
        "robust transfer superiority | not supported",
        "true_reward_margin_guard_m150_rewardtop7_20seed | 65.8876 | 72.1918 | 6.3041 | 20 / 20 | 4.1401 | 7.7605 | 0.0860 | current primary algorithm-readiness candidate; setting-specific guard only",
        "--true-reward-guard-json",
        "paper10_geojepa_mpc.experiments.manuscript_result_tables_freeze",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "source-derived table freeze",
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("raw_rollout_consistency", "overall_consistency_pass"): True,
        ("raw_rollout_consistency", "summary_matches_raw"): True,
        ("raw_rollout_consistency", "stage3_anchor_matches_raw"): True,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    tables = payload.get("tables", {})
    anchor_table = tables.get("table_bishan_anchor_vs_matched_baseline")
    if not isinstance(anchor_table, list) or len(anchor_table) != 2:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
            "table_bishan_anchor_vs_matched_baseline"
        )
        anchor_table = []
    expected_anchor_rows = [
        {
            "row_id": "matched_paper9_rank_seed2028_baseline",
            "mean_reward": 67.5436698503176,
            "std_sample": 7.22455439874099,
            "delta_vs_baseline": 0.0,
        },
        {
            "row_id": "bishan_20x16_top5_frozen_anchor",
            "mean_reward": 69.47054604253474,
            "std_sample": 1.0003610285842477,
            "delta_vs_baseline": 1.9268761922171365,
            "raw_rollout_consistency_pass": True,
        },
    ]
    for index, expected_row in enumerate(expected_anchor_rows):
        if index >= len(anchor_table):
            continue
        row = anchor_table[index]
        for key, expected in expected_row.items():
            value = row.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-8:
                    missing_tokens.append(
                        f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                        f"anchor[{index}].{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                    f"anchor[{index}].{key}={value}"
                )

    stage3_table = tables.get("table_stage3_boundary")
    if not isinstance(stage3_table, list) or len(stage3_table) != 3:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: table_stage3_boundary"
        )
        stage3_table = []
    expected_stage3_rows = [
        {
            "run_name": "frontier_random050_50x16_h5_seed48_f050",
            "role": "confirmatory_pass",
            "states": 50,
            "candidates": 16,
            "selected_top_k": 6,
            "mean_reward": 64.29600411367917,
            "delta_vs_baseline": -3.2476657366384245,
            "interpretation": "boundary evidence; below matched baseline",
        },
        {
            "run_name": "frontier_random050_50x24_h5_seed47_f075",
            "role": "confirmatory_pass",
            "states": 50,
            "candidates": 24,
            "selected_top_k": 12,
            "mean_reward": 66.25436421527586,
            "delta_vs_baseline": -1.2893056350417424,
            "interpretation": "boundary evidence; below matched baseline",
        },
        {
            "run_name": "frontier_random050_50x24_h5_seed48_f075",
            "role": "diagnostic_near_pass",
            "states": 50,
            "candidates": 24,
            "selected_top_k": 12,
            "mean_reward": 67.49131359932167,
            "delta_vs_baseline": -0.05235625099592767,
            "interpretation": "diagnostic near-pass only; must not be pooled",
        },
    ]
    for index, expected_row in enumerate(expected_stage3_rows):
        if index >= len(stage3_table):
            continue
        row = stage3_table[index]
        for key, expected in expected_row.items():
            value = row.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-8:
                    missing_tokens.append(
                        f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                        f"stage3[{index}].{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                    f"stage3[{index}].{key}={value}"
                )

    claim_table = tables.get("table_claim_status")
    if not isinstance(claim_table, list) or len(claim_table) != 5:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: table_claim_status"
        )
        claim_table = []
    claim_status = {
        row.get("claim_id"): row.get("status")
        for row in claim_table
        if isinstance(row, dict)
    }
    expected_claim_status = {
        "bishan_anchor": "supported",
        "stage3_confirmatory_50state": "not supported",
        "diagnostic_near_pass": "not pooled",
        "dongxing_return_label_scaling": "supported descriptively",
        "robust_transfer_superiority": "not supported",
    }
    for claim_id, expected in expected_claim_status.items():
        if claim_status.get(claim_id) != expected:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                f"{claim_id}={claim_status.get(claim_id)}"
            )

    guard_table = tables.get("table_true_reward_guard_readiness")
    if not isinstance(guard_table, list) or len(guard_table) != 1:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
            "table_true_reward_guard_readiness"
        )
        guard_table = []
    expected_guard_row = {
        "row_id": "true_reward_margin_guard_m150_rewardtop7_20seed",
        "setting": "bishan_20x16_top5",
        "audit_set": "rewardtop7",
        "switch_margin": 1.5,
        "baseline_mean_reward": 65.8876435268697,
        "guard_mean_reward": 72.19178534319884,
        "mean_delta_vs_baseline": 6.304141816329158,
        "seed_wins": 20,
        "n_seeds": 20,
        "bootstrap_95ci_delta_lower": 4.140109129548553,
        "switch_rate": 0.086,
        "mean_audit_action_count": 7.7605,
        "dual7x7_mean_audit_action_count": 8.1905,
        "interpretation": "current primary algorithm-readiness candidate; setting-specific guard only",
    }
    if guard_table:
        row = guard_table[0]
        for key, expected in expected_guard_row.items():
            value = row.get(key)
            if isinstance(expected, float):
                if not isinstance(value, (int, float)) or abs(float(value) - expected) > 1e-8:
                    missing_tokens.append(
                        f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                        f"guard.{key}={value}"
                    )
            elif value != expected:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON}: "
                    f"guard.{key}={value}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_manuscript_result_tables_freeze_current",
            False,
            "Paper10 manuscript result tables freeze gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_manuscript_result_tables_freeze_current",
        True,
        "Paper10 manuscript result tables freeze is current and claim-bounded",
    )


def check_paper10_manuscript_text_table_consistency_audit_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD,
        PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON,
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON,
        CEUS_STAGE3_MANUSCRIPT_DRAFT,
        CEUS_STAGE3_MANUSCRIPT_REFRAME,
        PROJECT_PROPOSAL_REPORT,
        AUTHOR_DECISION_MATRIX,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        DATA_AVAILABILITY,
        REPRODUCIBILITY,
        MANIFEST,
        Path("README.md"),
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_manuscript_text_table_consistency_audit_current",
            False,
            "missing Paper10 manuscript text/table consistency audit files: "
            + ", ".join(missing),
        )

    text = read_text(root / PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD)
    try:
        payload = json.loads(
            read_text(root / PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON)
        )
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_manuscript_text_table_consistency_audit_current",
            False,
            f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    audit_name = PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD.name
    linked_docs = [
        Path("README.md"),
        Path("MANIFEST.md"),
        Path("DATA_AVAILABILITY.md"),
        Path("REPRODUCIBILITY.md"),
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT,
        AUTHOR_DECISION_MATRIX,
    ]
    for rel_path in linked_docs:
        path = root / rel_path
        if not path.exists():
            missing_tokens.append(f"{rel_path}: missing file")
            continue
        if audit_name not in read_text(path):
            missing_tokens.append(f"{rel_path}: {audit_name}")

    required_tokens = [
        "Paper10 manuscript text/table consistency audit",
        "source-derived manuscript text/table consistency audit",
        "does not add a new experimental claim",
        "No rollout was rerun",
        "overall consistency: PASS",
        PAPER10_MANUSCRIPT_RESULT_TABLES_FREEZE_JSON.name,
        CEUS_STAGE3_MANUSCRIPT_DRAFT.name,
        CEUS_STAGE3_MANUSCRIPT_REFRAME.name,
        PROJECT_PROPOSAL_REPORT.name,
        AUTHOR_DECISION_MATRIX.name,
        FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT.name,
        "69.4705",
        "67.5437",
        "1.0004",
        "7.2246",
        "64.2960, 66.2544",
        "67.4913",

        "must not be pooled",
        "direct 50-state Bishan scale-up success",
        "robust Bishan-to-Dongxing transfer superiority",
        "PASS does not mean the formal manuscript is ready for submission",
        "paper10_geojepa_mpc.experiments.manuscript_text_table_consistency_audit",
    ]
    for token in required_tokens:
        if token not in text:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD}: {token}"
            )

    expected_values = {
        ("date",): "2026-06-19",
        ("status",): "source-derived manuscript text/table consistency audit",
        ("overall_consistency_pass",): True,
        ("source_boundary", "new_experimental_claim"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("expected_tokens", "anchor_mean"): "69.4705",
        ("expected_tokens", "baseline_mean"): "67.5437",
        ("expected_tokens", "anchor_std"): "1.0004",
        ("expected_tokens", "baseline_std"): "7.2246",
        ("expected_tokens", "diagnostic_near_pass_mean"): "67.4913",
        ("expected_tokens", "algorithm_readiness_addendum", "guard_mean_reward"): "72.1918",
        ("expected_tokens", "algorithm_readiness_addendum", "baseline_mean_reward"): "65.8876",
        ("expected_tokens", "algorithm_readiness_addendum", "mean_delta_vs_baseline"): "6.3041",
        ("expected_tokens", "algorithm_readiness_addendum", "seed_wins"): "20 / 20",
        ("expected_tokens", "algorithm_readiness_addendum", "bootstrap_95ci_delta_lower"): "4.1401",
        ("expected_tokens", "algorithm_readiness_addendum", "mean_audit_action_count"): "7.7605",
        ("expected_tokens", "algorithm_readiness_addendum", "legacy_text_required"): False,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
                    f"{'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    expected_confirmatory = ["64.2960", "66.2544"]
    confirmatory = (
        payload.get("expected_tokens", {}).get("stage3_confirmatory_means")
    )
    if confirmatory != expected_confirmatory:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
            f"expected_tokens.stage3_confirmatory_means={confirmatory}"
        )

    expected_documents = [
        str(CEUS_STAGE3_MANUSCRIPT_DRAFT),
        str(CEUS_STAGE3_MANUSCRIPT_REFRAME),
        str(PROJECT_PROPOSAL_REPORT),
        str(AUTHOR_DECISION_MATRIX),
        str(FORMAL_MANUSCRIPT_ASSEMBLY_BLUEPRINT),
    ]
    documents = payload.get("documents")
    if not isinstance(documents, list) or len(documents) != len(expected_documents):
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: documents"
        )
        documents = []
    observed_documents = [row.get("document") for row in documents if isinstance(row, dict)]
    if observed_documents != expected_documents:
        missing_tokens.append(
            f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
            f"documents={observed_documents}"
        )

    for row in documents:
        if not isinstance(row, dict):
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: non-dict document row"
            )
            continue
        document = row.get("document")
        if row.get("consistent_with_table_freeze") is not True:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
                f"{document}.consistent_with_table_freeze={row.get('consistent_with_table_freeze')}"
            )
        for key in (
            "missing_required_tokens",
            "missing_boundary_tokens",
            "forbidden_positive_claim_hits",
            "unsupported_inferential_hits",
        ):
            value = row.get(key)
            if value != []:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
                    f"{document}.{key}={value}"
                )
        matched_boundary_tokens = set(row.get("matched_boundary_tokens", []))
        for token in (
            "must not be pooled",
            "direct 50-state Bishan scale-up success",
            "robust Bishan-to-Dongxing transfer superiority",
        ):
            if token not in matched_boundary_tokens:
                missing_tokens.append(
                    f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_JSON}: "
                    f"{document}.matched_boundary_tokens.{token}"
                )

    forbidden_50_state = re.compile("|".join(FORBIDDEN_50_STATE_PATTERNS), re.IGNORECASE)
    for line_no, line in enumerate(text.splitlines(), start=1):
        if forbidden_50_state.search(line):
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD}:{line_no}: "
                "positive 50-state wording"
            )
        match = UNSUPPORTED_INFERENTIAL_STATS_PATTERN.search(line)
        if match:
            missing_tokens.append(
                f"{PAPER10_MANUSCRIPT_TEXT_TABLE_CONSISTENCY_AUDIT_MD}:{line_no}: "
                f"unsupported inferential wording {match.group(0)}"
            )

    if missing_tokens:
        return CheckResult(
            "paper10_manuscript_text_table_consistency_audit_current",
            False,
            "Paper10 manuscript text/table consistency audit gaps: "
            + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_manuscript_text_table_consistency_audit_current",
        True,
        "Paper10 manuscript text/table consistency audit is current and claim-bounded",
    )


POST_GUARD_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not"
    r"|not final|false|no-go|not_submission_ready|blocked|unresolved"
    r")\b",
    re.IGNORECASE,
)
POST_GUARD_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
POST_GUARD_FORBIDDEN_TARGETS = (
    re.compile(r"\buniversal fixed switch margin\b", re.IGNORECASE),
    re.compile(r"\bdirect 50[- ]state Bishan scale[- ]up success\b", re.IGNORECASE),
    re.compile(
        r"\brobust Bishan[- ]to[- ]Dongxing transfer superiority\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdeployment-ready cadastral planning\b", re.IGNORECASE),
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\bready to submit\b", re.IGNORECASE),
)


def is_post_guard_closure_refresh_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in POST_GUARD_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if POST_GUARD_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in POST_GUARD_FORBIDDEN_TARGETS):
            return True
    return False

POST_GUARD_SUBMISSION_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not"
    r"|not final|false|no-go|not_submission_ready|blocked|unresolved"
    r"|remains blocked|does not mean"
    r")\b",
    re.IGNORECASE,
)
POST_GUARD_SUBMISSION_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
POST_GUARD_SUBMISSION_FORBIDDEN_TARGETS = (
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\bready to submit\b", re.IGNORECASE),
    re.compile(r"\ball blockers closed\b", re.IGNORECASE),
    re.compile(r"\bsubmission_ready\b", re.IGNORECASE),
)


def is_post_guard_submission_readiness_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in POST_GUARD_SUBMISSION_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if POST_GUARD_SUBMISSION_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(
            target.search(clause)
            for target in POST_GUARD_SUBMISSION_FORBIDDEN_TARGETS
        ):
            return True
    return False


TRUE_REWARD_GUARD_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not"
    r"|not final|false|no "
    r")\b",
    re.IGNORECASE,
)
TRUE_REWARD_GUARD_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
TRUE_REWARD_GUARD_FORBIDDEN_TARGETS = (
    re.compile(r"\buniversal fixed switch margin\b", re.IGNORECASE),
    re.compile(r"\bdirect 50[- ]state Bishan scale[- ]up success\b", re.IGNORECASE),
    re.compile(
        r"\brobust Bishan[- ]to[- ]Dongxing transfer superiority\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdeployment-ready cadastral planning\b", re.IGNORECASE),
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
)


def is_true_reward_guard_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in TRUE_REWARD_GUARD_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if TRUE_REWARD_GUARD_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in TRUE_REWARD_GUARD_FORBIDDEN_TARGETS):
            return True
    return False

CEUS_BASELINE_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|insufficient|cannot|must not|should not|no "
    r"|without|rather than"
    r")\b",
    re.IGNORECASE,
)
CEUS_BASELINE_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
CEUS_BASELINE_FORBIDDEN_TARGETS = (
    re.compile(r"\bstatistically significant\b", re.IGNORECASE),
    re.compile(r"\brobustly superior\b", re.IGNORECASE),
    re.compile(r"\buniformly superior\b", re.IGNORECASE),
    re.compile(r"\bdirect 50[- ]state Bishan scale[- ]up success\b", re.IGNORECASE),
    re.compile(
        r"\brobust Bishan[- ]to[- ]Dongxing transfer superiority\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdeployment-ready\b", re.IGNORECASE),
)


def is_ceus_baseline_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in CEUS_BASELINE_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if CEUS_BASELINE_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in CEUS_BASELINE_FORBIDDEN_TARGETS):
            return True
    return False

SUBMISSION_READINESS_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"does not mean|do not|must not|cannot|can't|may not|should not"
    r")\b",
    re.IGNORECASE,
)
SUBMISSION_READINESS_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
SUBMISSION_READINESS_FORBIDDEN_TARGETS = (
    re.compile(r"\bStatus:\s*submission_ready\b", re.IGNORECASE),
    re.compile(r"\bfinal submission-ready\b", re.IGNORECASE),
    re.compile(r"\bready for final submission\b", re.IGNORECASE),
    re.compile(r"\bready to submit\b", re.IGNORECASE),
    re.compile(r"\ball blockers closed\b", re.IGNORECASE),
    re.compile(
        r"\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bscale[- ]?up\b.{0,80}\bsuccess\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\brobust\b.{0,80}\bbishan[- ]to[- ]dongxing\b.{0,80}\btransfer\b.{0,80}\bsuperiority\b",
        re.IGNORECASE,
    ),
)


def is_submission_readiness_positive_claim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in SUBMISSION_READINESS_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if SUBMISSION_READINESS_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in SUBMISSION_READINESS_FORBIDDEN_TARGETS):
            return True
    return False

ORIGINAL_VISION_POSITIVE_CLAIM_CUE = re.compile(
    r"\b("
    r"claim(?:s|ed|ing)?"
    r"|prove(?:s|d|n|ing)?"
    r"|support(?:s|ed|ing)?"
    r"|show(?:s|ed|ing)?"
    r"|demonstrate(?:s|d|ing)?"
    r"|validate(?:s|d|ing)?"
    r"|establish(?:es|ed|ing)?"
    r"|confirm(?:s|ed|ing)?"
    r")\b",
    re.IGNORECASE,
)
ORIGINAL_VISION_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not"
    r"|don't"
    r"|must not"
    r"|should not"
    r"|may not"
    r"|cannot"
    r"|can't"
    r"|not sufficient"
    r"|insufficient"
    r"|does not"
    r"|do not support"
    r"|not supported"
    r"|unsupported"
    r"|no new conclusion"
    r")\b",
    re.IGNORECASE,
)
ORIGINAL_VISION_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
ORIGINAL_VISION_PROHIBITED_CLAIM_TARGETS = (
    re.compile(
        r"\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bsuccess\b"
        r"|\b50[- ]state\b.{0,80}\bbishan\b.{0,80}\bsuccess\b"
        r"|\bdirect\b.{0,80}\b50[- ]state\b.{0,80}\bsuccess\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b50[- ]state\b.{0,80}\bscale[- ]?up\b"
        r"|\bscale[- ]?up\b.{0,80}\b50[- ]state\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bbishan[- ]to[- ]dongxing\b.{0,120}\btransfer\b.{0,80}\bsuperiority\b"
        r"|\bbishan[- ]to[- ]dongxing\b.{0,120}\bsuperiority\b"
        r"|\btransfer\b.{0,80}\bsuperiority\b.{0,120}\bbishan[- ]to[- ]dongxing\b",
        re.IGNORECASE,
    ),
)


def is_original_vision_positive_claim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in ORIGINAL_VISION_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if ORIGINAL_VISION_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if not ORIGINAL_VISION_POSITIVE_CLAIM_CUE.search(clause):
            continue
        if any(
            target.search(clause)
            for target in ORIGINAL_VISION_PROHIBITED_CLAIM_TARGETS
        ):
            return True
    return False


def check_original_vision_validation_registry_current(root: Path) -> CheckResult:
    paths = [
        root / ORIGINAL_VISION_DESIGN,
        root / ORIGINAL_VISION_REGISTRY,
    ]
    missing = [path for path in paths if not path.exists()]
    if missing:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing: " + ", ".join(str(path.relative_to(root)) for path in missing),
        )

    hits = []
    for path in paths:
        rel_path = path.relative_to(root)
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            if is_original_vision_positive_claim(line):
                hits.append(f"{rel_path}:{line_no}: {line.strip()}")
    if hits:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "forbidden validation wording: " + " | ".join(hits),
        )

    registry_text = read_text(root / ORIGINAL_VISION_REGISTRY)
    required_reference = ORIGINAL_VISION_DESIGN.as_posix()
    design_spec = markdown_section_outside_code_fences(registry_text, "## Design Spec")
    if required_reference not in design_spec:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing registry ## Design Spec reference: " + required_reference,
        )
    if not has_markdown_heading_outside_code_fences(registry_text, "## Claim Lock"):
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing registry section: ## Claim Lock",
        )

    return CheckResult(
        "original_vision_validation_registry_current",
        True,
        "original-vision validation design and registry are current and guarded",
    )


CHECKS: tuple[Callable[[Path], CheckResult], ...] = (
    check_required_paths_exist,
    check_archive_manifest_required_fields,
    check_archive_manifest_included_paths_resolve,
    check_excluded_paths_not_tracked,
    check_public_submission_placeholders_absent,
    check_public_data_route_wording_specific,
    check_forbidden_50_state_claims,
    check_self_contained_manuscript_no_paper9_placeholder,
    check_citation_keys_resolve,
    check_reviewer_smoke_protocol_links,
    check_integrated_dongxing_source_data_links,
    check_dongxing_data_availability_routes,
    check_integrated_figure_table_numbering_frozen,
    check_submission_blocker_decision_packet_current,
    check_integrated_target_venue_conversion_checklist_current,
    check_integrated_citation_statistics_policy_current,
    check_ceus_reviewer_improvement_packet_current,
    check_ceus_research_article_manuscript_draft_current,
    check_ceus_stage3_manuscript_reframe_current,
    check_ceus_stage3_manuscript_draft_current,
    check_paper10_project_proposal_report_current,
    check_paper10_author_decision_matrix_current,
    check_paper10_formal_manuscript_blueprint_current,
    check_paper10_formal_manuscript_draft_current,
    check_paper10_bounded_manuscript_assembly_current,
    check_paper10_mechanism_ablation_packet_current,
    check_paper10_claim_source_audit_current,
    check_paper10_figure_table_source_coverage_audit_current,
    check_paper10_figure_table_caption_claim_packet_current,
    check_paper10_final_figure_table_export_package_current,
    check_paper10_archive_source_data_closeout_current,
    check_paper10_main_figure1_final_artwork_closeout_current,
    check_paper10_ceus_submission_policy_verification_current,
    check_paper10_submission_readiness_boundary_current,
    check_paper10_manuscript_result_tables_freeze_current,
    check_paper10_manuscript_text_table_consistency_audit_current,
    check_paper10_real_data_availability_audit_current,
    check_paper10_real_data_integrity_smoke_current,
    check_paper10_real_env_smoke_current,
    check_paper10_real_env_value_filter_smoke_current,
    check_paper10_real_env_smoke_boundary_audit_current,
    check_paper10_real_env_longhorizon_pilot_audit_current,
    check_paper10_real_env_longhorizon_confirmatory_audit_current,
    check_paper10_ceus_baseline_inference_hardening_current,
    check_paper10_ceus_review_response_experiment_package_current,
    check_paper10_guard_information_set_audit_current,
    check_paper10_proxy_guard_dynamic_baseline_audit_current,
    check_paper10_true_reward_guard_readiness_current,
    check_paper10_post_guard_experiment_closure_refresh_current,
    check_paper10_author_decision_closeout_form_current,
    check_paper10_data_publication_boundary_backfill_current,
    check_paper10_public_release_rights_gate_current,
    check_paper10_dltb_leakage_evidence_audit_current,
    check_paper10_ceus_confidential_dltb_acceptance_packet_current,
    check_paper10_post_guard_submission_readiness_refresh_current,
    check_paper10_ceus_clean_main_manuscript_draft_current,
    check_paper10_anchor_raw_rollout_consistency_audit_current,
    check_original_vision_validation_registry_current,
)


def run_checks(root: Path) -> list[CheckResult]:
    return [check(root) for check in CHECKS]


def to_payload(results: list[CheckResult]) -> dict:
    failed = [result.name for result in results if not result.ok]
    passed = [result.name for result in results if result.ok]
    return {
        "ok": not failed,
        "total_checks": len(results),
        "passed_checks": passed,
        "failed_checks": failed,
        "checks": [
            {"name": result.name, "ok": result.ok, "details": result.details}
            for result in results
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Paper10 submission preflight checks."
    )
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[2],
        type=Path,
        help="Repository root to check.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a text summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    payload = to_payload(run_checks(root))

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        status = "PASS" if payload["ok"] else "FAIL"
        print(f"Paper10 preflight: {status}")
        for item in payload["checks"]:
            prefix = "ok" if item["ok"] else "fail"
            print(f"[{prefix}] {item['name']}: {item['details']}")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
