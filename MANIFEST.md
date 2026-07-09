# Manifest

This repository is a Paper10 reproducibility package. It intentionally includes
source code, tests, result evidence, checkpoints, compatibility code, and small
data needed for smoke verification.

## Included

- `LICENSE`: Apache-2.0 licence for licensable code and scripts.
- `paper10_geojepa_mpc/`: 409 tracked non-cache files in the active
  Paper10 workspace, including 96 Python files, 131 JSON files, 134 Markdown
  files, 11 CSV files, 9 NPZ files, 11 PyTorch checkpoint files, 16 log files,
  and 1 TXT highlights file.
- `arcgis_toolbox_paper9/private_source/`: 10 Paper9 compatibility source files
  used by Paper10's real-environment rollout and value-label workflows.
- `county_env.py`: Paper9 county-level environment implementation used by
  `private_source.blocks_env`.
- `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`: 4 small smoke
  Tool2 files used by tests and smoke commands.
- `paper7/data/`: GeoFM embedding array and metadata used by optional fusion
  paths.
- `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`: Google Colab
  notebook retained for 50x24/h5 diagnostic reproduction or re-parameterized
  future runs.
- `docs/macos_frontier_random050_50x24_h5.md`: macOS continuation guide for the
  superseded `frontier_random050` 50x24/h5 diagnostic run.
- `scripts/macos/run_frontier_random050_50x24_h5.sh`: resumable macOS local
  runner for the same experiment.
- `scripts/macos/frontier_random050_50x24_h5.env.example`: local path and device
  configuration template for the macOS runner.
- `docs/windows_frontier_random050_ablation.md`: Windows CPU continuation guide
  for reproducing or editing the `frontier_random050` 50-state ablation grid.
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`: resumable Windows
  PowerShell runner for label generation, diagnostics, monitor gates, and
  optional value-head training after a passing gate.
- `scripts/windows/frontier_random050_ablation.env.example.ps1`: local path,
  device, and ablation-grid configuration template for the Windows runner.
- `docs/superpowers/specs/2026-06-07-paper10-geojepa-mpc-design.md`: design
  specification.
- `docs/superpowers/plans/2026-06-07-paper10-geojepa-mpc.md`: implementation
  plan.
- `docs/superpowers/plans/2026-06-07-paper10-e0-smoke-training.md`: smoke
  training plan.
- `docs/superpowers/notes/2026-06-09-paper10-50state-redesign-handoff.md`:
  current continuation decision for Paper10 after the failed 50-state
  `frontier_random050` diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_10x12_h5_seed43_pilot_report_2026-06-08.md`:
  `frontier_random050` value-head 10x12/h5 pilot report.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`:
  five-seed 100-step rollout summary for the 10x12/h5 pilot.
- `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt`:
  checkpoint used by the 10x12/h5 pilot rollouts.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_20x16_h5_seed44_top5_report_2026-06-08.md`:
  latest `frontier_random050` value-head 20x16/h5 scale-up report.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_draft_2026-06-20.md`:
  current formal manuscript draft with the 2026-06-20 candidate-score sweep
  boundary.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`:
  current no-go submission-readiness boundary for the CEUS route, preserving
  unresolved DOI, licence, data-access, citation, statistical-reporting, and
  final figure/export blockers without declaring final submission readiness.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_experiment_freeze_audit_2026-06-27.md`:
  current algorithm-freeze decision boundary for choosing experiment closure
  and claim-controlled manuscript assembly by default, while reserving
  algorithm redesign for deliberate stronger-claim tracks.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_experiment_closure_register_2026-06-27.md`:
  current experiment-closure register that freezes default comparator,
  descriptive-statistics, figure/export, data-route, and algorithm-work
  decisions for the next bounded manuscript assembly pass.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_bounded_manuscript_assembly_draft_2026-06-27.md`:
  current bounded manuscript assembly draft carrying the 2026-06-20
  formal draft into the 2026-06-27 freeze and closure boundary.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_main_figure1_artwork_preview_2026-06-27.md`:
  Main Figure 1 workflow-artwork preview record, documenting the reproducible
  schematic script and ignored local PNG/SVG/PDF preview outputs.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md`:
  current Main Figure 1 final artwork candidate closeout, recording tracked
  SVG/PDF/PNG exports and preserving the no-go submission gate.
- `paper10_geojepa_mpc/experiments/results/ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.svg`:
  tracked editable SVG final artwork candidate for Main Figure 1.
- `paper10_geojepa_mpc/experiments/results/ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.pdf`:
  tracked PDF final artwork candidate for Main Figure 1.
- `paper10_geojepa_mpc/experiments/results/ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.png`:
  tracked high-resolution PNG preview for the Main Figure 1 final artwork
  candidate.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_target_journal_fit_assessment_2026-06-27.md`:
  current target-journal route assessment, recommending CEUS first under the
  frozen claim boundary and documenting conditional EMS, CEA, SAT, AI in
  Agriculture, JAG, and Scientific Reports alternatives.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.md`:
  current CEUS monitor-threshold sensitivity audit, including strict/default/
  lenient gates and recorded-threshold provenance for historical monitor rows.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.json`:
  machine-readable output for the monitor-threshold sensitivity audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md`:
  current CEUS mechanism/baseline claim audit separating matched Paper9,
  pairwise-only, no-mask, ungated-top4, secondary-metric, and 50-state claim
  boundaries.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_mechanism_claim_audit_2026-06-27.json`:
  machine-readable output for the mechanism/baseline claim audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_review_optimization_register_2026-06-27.md`:
  CEUS review-driven optimization register separating addressed technical
  audit items from unresolved real-data, multi-region, and stronger-claim
  experiment needs.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`:
  source-derived CEUS baseline and inference hardening audit that locks mixed
  seed-wise wording, diagnostic-only sign-test interpretation, secondary-metric
  tradeoffs and no-overclaim gates for the next CEUS manuscript pass.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md`:
  source-derived algorithm-readiness audit for the 2026-07-07 true-reward
  margin guard evidence, promoting 20x16/top5 `rewardtop7 margin=1.50` as
  the current primary guard candidate and 10x12/top4 `rewardtop7 margin=1.60`
  as setting-specific consistency support while preserving no-overclaim gates.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.json`:
  machine-readable source for the true-reward guard readiness preflight check.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_review_response_experiment_package_2026-07-09.md`:
  CEUS review-response algorithm experiment package promoting the 20-seed
  `rewardtop7 margin=1.50` true-reward guard as the primary Bishan algorithm
  evidence and demoting the old 5-seed value-filter result to descriptive
  background.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_review_response_experiment_package_2026-07-09.json`:
  machine-readable source for the CEUS review-response experiment preflight check.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_public_release_rights_gate_2026-07-09.md`:
  current public-release rights gate recording Apache-2.0 for code, CC0-1.0
  for generated non-DLTB data/model artifacts, confidential_no_external_access
  for original Bishan and Dongxing DLTB inputs, the author-confirmed 4open
  README.md direct reviewer link, and remaining leakage-check,
  journal-acceptance and final-backfill blockers.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_public_release_rights_gate_2026-07-09.json`:
  machine-readable source for the public-release rights gate preflight check.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`:
  bounded manuscript patch for the next CEUS assembly pass.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`:
  current CEUS baseline-hardened manuscript assembly draft that integrates the
  2026-07-06 baseline/inference hardening audit with the bounded manuscript,
  mechanism ablation, Stage 3 boundary and Dongxing/Neijiang calibration
  evidence.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_formal_output_readiness_audit_2026-07-06.md`:
  formal-output readiness audit recording that Paper10 is convertible into a
  bounded CEUS manuscript draft but still has open repository, licence,
  data-access, declaration and figure/export blockers before formal submission.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_formal_output_conversion_patch_2026-07-06.md`:
  CEUS formal-output conversion patch with title options, five compliant
  highlights, abstract replacement text, cleanup map, data/code backfill
  template and figure/table export checklist.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_clean_main_manuscript_draft_2026-07-06.md`:
  clean CEUS main-manuscript draft for bounded formal submission, with internal
  handoff tables removed and the 2026-07-09 CEUS policy verification applied.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_submission_policy_verification_2026-07-09.md`:
  current CEUS submission-policy closeout verifying Elsevier Research Data
  Policy Option B, confidential raw-DLTB disclosure route, Figure 1 upload
  readiness, highlights compliance, and remaining submission-system fields.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_submission_policy_verification_2026-07-09.json`:
  machine-readable source for the CEUS submission-policy verification preflight
  check.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_highlights_2026-07-06.txt`:
  separate editable CEUS highlights file with five bullet points, each no more
  than 85 characters including spaces.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`:
  latest 50x24/f075 candidate-score sweep showing the boundary remains below
  the matched Paper9 baseline.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.json`:
  machine-readable output for the latest 50x24/f075 candidate-score sweep.
- `paper10_geojepa_mpc/experiments/results/e0_windows_frontier_random050_ablation_findings_2026-06-09.md`:
  Windows CPU 50-state ablation findings for the completed negative
  `frontier_random050` candidate-grid diagnosis.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_synthesis_2026-06-09.md`:
  paper-facing synthesis of the E0 `frontier_random050` pilot, scale-up,
  reproduction audit, and 50-state boundary diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_section_draft_2026-06-09.md`:
  manuscript-style Results and Discussion draft for the E0 `frontier_random050`
  evidence package.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md`:
  manuscript-ready E0 `frontier_random050` tables, captions, and placement
  recommendations.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_scaffold_2026-06-09.md`:
  full-paper scaffold with title candidates, abstract draft, section plan,
  figure/table placement, and claim-evidence map for the E0 evidence package.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md`:
  single-entry generic manuscript draft assembling the cited Introduction,
  Methods, Results, Discussion, abstract, conclusion, claim-evidence map, and
  submission blockers.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`:
  public-submission-oriented integrated manuscript variant whose Methods section
  uses the packaged Paper10 task/environment and reward notes instead of the
  local-only Paper9 citation placeholder.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_introduction_cited_draft_2026-06-09.md`:
  citation-inserted Introduction draft using the verified Paper10 BibTeX keys
  while preserving the unresolved Paper9 citation boundary.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_methods_draft_2026-06-09.md`:
  paper-facing Methods draft covering task formulation, `frontier_random050`
  value-label generation, monitor-gated selection, value-head-only training,
  rollout evaluation, reproducibility conditions, and 50-state boundary
  diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md`:
  citation-aware Results and Discussion draft that keeps quantitative E0 claims
  tied to local evidence while using external references only for general
  value-function, MPC, and world-model framing.
- `paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md`:
  manuscript-ready Data and Code Availability draft mapping included smoke
  data, generated E0 artifacts, checkpoints, external full Bishan data,
  Dongxing/Neijiang prepared data, GPKG reproducibility inputs, repository DOI
  needs, and restricted-data access blockers.
- `paper10_geojepa_mpc/experiments/results/e0_submission_route_and_archive_plan_2026-06-09.md`:
  route-specific submission and archiving plan covering generic, Nature-family,
  and methods/reproducibility venue routes; code/data archive records; full
  Bishan data access decisions; licences; source-data mapping; and restricted
  data warnings.
- `paper10_geojepa_mpc/experiments/results/e0_archive_metadata_templates_2026-06-09.md`:
  fill-in archive metadata templates for the code/evidence record, full Bishan
  Tool2 data record, prepared GPKG-root geospatial inputs record, restricted
  access wording, source-data mapping, and dataset README skeleton.
- `paper10_geojepa_mpc/experiments/results/e0_archive_manifest_2026-06-09.csv`:
  machine-readable archive manifest that groups included, externalized, and
  excluded file families by archive record, access route, archive action,
  external-dependency status, and submission status.
- `paper10_geojepa_mpc/experiments/results/e0_source_data_map_2026-06-09.md`:
  figure, table, and claim-to-source mapping for the current E0 manuscript
  package, including CSV, JSON, Markdown, NPZ, checkpoint, plotting-script, and
  external full-data-route references for archive source-data metadata.
- `paper10_geojepa_mpc/experiments/results/e0_data_access_and_rights_decision_register_2026-06-09.md`:
  data-access and rights decision register for code licence, generated-output
  rights, optional GeoFM redistribution, full Tool2 access, GPKG-root
  geospatial access, Dongxing/Neijiang prepared-data access, reviewer routes,
  and final availability backfill fields.
- `paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_replication_protocol_2026-06-09.md`:
  reviewer-oriented clone-only smoke replication protocol with command order,
  expected smoke outputs, failure interpretation, and explicit separation from
  full Bishan reruns and failed 50-state diagnostics.
- `paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_verification_log_2026-06-10.md`:
  local execution log for the reviewer smoke protocol at commit
  `534e0f8115a55d5c080bf21bb888657ccd9dd585`, including pytest, smoke data
  header, smoke-scale training, and optional value-head smoke results.
- `paper10_geojepa_mpc/experiments/results/e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`:
  release checklist for the code/evidence archive, full-data route decisions,
  DOI or reviewer-link backfill, final verification, and no-go submission
  warnings.
- `paper10_geojepa_mpc/experiments/results/e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md`:
  target-venue and manuscript-conversion checklist for turning the
  self-contained integrated draft into a journal-specific submission package
  after format, citation, figure, DOI, and data-access decisions are fixed.
- `paper10_geojepa_mpc/experiments/results/e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md`:
  reviewer-risk audit for the self-contained integrated manuscript route,
  separating blocking submission gaps from risks that can be handled by
  bounded framing and final manuscript conversion.
- `paper10_geojepa_mpc/experiments/results/e0_submission_readiness_checklist_2026-06-09.md`:
  submission-readiness tracker covering completed manuscript assets,
  unresolved blockers, reviewer-risk matrix, next-session action order, and
  claim-evidence guardrails for the E0 evidence package.
- `paper10_geojepa_mpc/experiments/results/e0_bishan_task_environment_self_contained_methods_2026-06-09.md`:
  code-derived self-contained Methods note for the Bishan task, state, action,
  reward, episode, data-root, and Paper9-provenance replacement route.
- `paper10_geojepa_mpc/experiments/results/e0_reward_and_rollout_metric_definitions_2026-06-09.md`:
  source-grounded reward-function, executable-mask, value-label return, and
  rollout-metric definitions extracted from the packaged environment and E0
  rollout scripts.
- `paper10_geojepa_mpc/experiments/results/e0_citation_and_claim_checklist_2026-06-09.md`:
  manuscript citation-needs and claim-evidence checklist separating local E0
  evidence from external literature still requiring verification.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_figure_plan_2026-06-09.md`:
  manuscript figure contracts, panel maps, source-data links, caption drafts,
  and review-risk notes for E0 Figures 1-3.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`:
  integrated Paper10 manuscript spine that adds Dongxing/Neijiang evidence
  while preserving the bounded transfer claim.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`:
  manuscript-ready Bishan and Dongxing table package for the integrated
  scaffold.
- `paper10_geojepa_mpc/experiments/results/e0_post_dongxing_submission_gap_audit_2026-06-10.md`:
  post-Dongxing submission blocker and reviewer-risk ledger.
- `paper10_geojepa_mpc/experiments/results/e0_integrated_dongxing_figure_plan_2026-06-11.md`:
  figure contract and caption-risk plan for integrated Figures 1-5.
- `paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md`:
  source-data map binding Dongxing Figure 4 and Figure 5 to tracked CSVs,
  tables, and the with-Dongxing scaffold.
- `paper10_geojepa_mpc/experiments/results/e0_integrated_figure_table_numbering_freeze_2026-06-11.md`:
  current generic manuscript-conversion freeze for main/supplementary figure
  and table numbering with Dongxing evidence.
- `paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md`:
  current no-go decision packet collecting target venue, DOI/reviewer-link,
  licence, data-access, citation, statistics, and final export blockers before
  journal-specific manuscript conversion.
- `paper10_geojepa_mpc/experiments/results/e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`:
  current with-Dongxing target-venue and manuscript-conversion checklist for
  turning the integrated scaffold, tables, figure/table freeze, source-data
  map, and blocker packet into a journal-specific manuscript after author
  decisions are closed.
- `paper10_geojepa_mpc/experiments/results/e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`:
  current with-Dongxing citation and statistical-reporting policy that keeps
  local-only sources, preprints, descriptive results, and any future
  inferential claims under explicit manuscript-conversion control.
- `paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md`:
  current CEUS Research Article candidate-route improvement packet, including
  reviewer concern mapping, `D:\test` local data discovery, experiment
  feasibility decisions, and no-overclaim locks for irregular parcels,
  contiguity topology, soft-training/hard-inference wording, and transfer
  claims.
- `paper10_geojepa_mpc/experiments/results/e0_ceus_research_article_manuscript_draft_2026-06-12.md`:
  CEUS Research Article candidate manuscript draft converted from the
  integrated scaffold, tables, figure/table freeze, source-data map, citation
  and statistics policy, and CEUS reviewer-improvement packet.
- `paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_reframe_2026-06-18.md`:
  current Stage 3 manuscript-facing reframe for the CEUS route, including the
  replacement title, abstract, Results, Discussion, Conclusion, and
  claim-evidence map after confirmatory 50-state rows failed to beat the
  matched Paper9 baseline.
- `paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_draft_2026-06-18.md`:
  current CEUS Stage 3 manuscript draft applying the Stage 3 reframe to the
  earlier CEUS Research Article candidate draft, with bounded Bishan, Stage 3,
  and Dongxing claims plus unresolved submission blockers.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_project_proposal_opening_report_2026-06-18.md`:
  Chinese project-proposal/opening-report substitute for temporary topic
  approval before the formal Paper10 manuscript is ready, derived from the
  claim-bounded Stage 3 manuscript draft.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_author_decision_matrix_2026-06-18.md`:
  author-decision and formal-submission conversion matrix that turns the
  proposal/manuscript blockers into close-out choices, affected files, and
  completion evidence.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`:
  formal-manuscript assembly blueprint that maps the Stage 3 draft into
  section-level editing order, evidence locks, figure/table assembly and
  author-decision blockers before a journal-specific manuscript is produced.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_claim_source_consistency_audit_2026-06-18.md`:
  source-derived consistency audit that recomputes the current Bishan, Stage 3
  and Dongxing/Neijiang claim statuses from tracked JSON/CSV evidence.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_claim_source_consistency_audit_2026-06-18.json`:
  machine-readable output for the claim-source consistency audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_availability_audit_2026-06-18.md`:
  real-data availability audit that records local full Bishan, GPKG-root,
  block/township, and Dongxing/Neijiang external-dependency path status without
  copying raw data into Git.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_availability_audit_2026-06-18.json`:
  machine-readable output for the real-data availability audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_integrity_smoke_2026-06-18.md`:
  metadata-only real-data integrity smoke that records NPZ array headers,
  GeoPackage metadata, directory summaries, and JSON top-level keys without
  exporting raw rows or geometries.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_integrity_smoke_2026-06-18.json`:
  machine-readable output for the real-data integrity smoke.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.md`:
  five-step full-Bishan real-environment execution-chain smoke for the Paper10
  checkpoint, Paper9 adapter, MPC selector, executable mask, and
  `CountyLevelEnv.step`; it is not a planning-quality result.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.json`:
  machine-readable output for the real-environment execution-chain smoke.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.md`:
  five-step full-Bishan value-filter execution-chain smoke for the 20x16/top5
  checkpoint; it records one negative reward step and is not short-horizon
  performance evidence.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.json`:
  machine-readable output for the value-filter execution-chain smoke.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md`:
  boundary audit across the two tracked real-environment smoke reports,
  recording that different checkpoint, selector, horizon, and top-k settings
  prevent short-horizon performance-comparison use.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_boundary_audit_2026-06-19.json`:
  machine-readable output for the real-environment smoke boundary audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_paper9_smoke_5step_h5_k50_seed0_2026-06-27.md`:
  matched full-Bishan five-step H=5/K=50 Paper9 smoke report.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_paper9_smoke_5step_h5_k50_seed0_2026-06-27.json`:
  machine-readable output for the matched Paper9 smoke report.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_value_filter_smoke_5step_h5_k50_seed0_2026-06-27.md`:
  matched full-Bishan five-step H=5/K=50 value-filter smoke report.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_value_filter_smoke_5step_h5_k50_seed0_2026-06-27.json`:
  machine-readable output for the matched value-filter smoke report.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_smoke_boundary_audit_2026-06-27.md`:
  boundary audit for the matched full-Bishan smoke pair, recording identical
  action/reward traces and the no-performance-claim boundary.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_smoke_boundary_audit_2026-06-27.json`:
  machine-readable output for the matched smoke boundary audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_realdata_longhorizon_protocol_2026-06-27.md`:
  locked 100-step full-Bishan seed0 matched rollout pilot protocol for the
  CEUS real-data follow-up.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.md`:
  seed0 100-step matched Paper9/value-filter pilot audit recording the step-9
  trace divergence, reward delta, secondary-metric deltas, and no-superiority
  boundary.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.json`:
  machine-readable output for the long-horizon seed0 pilot audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md`:
  source-derived matched seeds 0-4 Paper9/value-filter audit; it links the
  tracked raw rollout files to the seed0 pilot audit and keeps the result as a
  descriptive Bishan-only evidence boundary.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json`:
  machine-readable output for the matched 5-seed long-horizon confirmatory
  audit.
- paper10_geojepa_mpc/experiments/results/e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md:
  source-derived raw-rollout consistency audit for the Bishan 20x16/top5
  frozen anchor; it recomputes five seed rewards from tracked raw step records
  and checks the packaged rollout summary and Stage 3 frozen-anchor row.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json`:
  machine-readable output for the anchor raw-rollout consistency audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`:
  source-derived manuscript result-table freeze for the Bishan anchor, Stage 3
  boundary rows, and claim-status table, derived from tracked audit JSON
  evidence without adding a new experimental claim.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`:
  machine-readable output for the manuscript result-table freeze.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md`:
  source-derived manuscript text/table consistency audit that checks the
  current manuscript-facing text against the frozen result tables without
  rerunning rollouts.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.json`:
  machine-readable output for the manuscript text/table consistency audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_source_coverage_audit_2026-06-19.md`:
  source-derived figure/table source coverage audit that checks the formal
  manuscript figure/table assembly map against tracked source files, scripts,
  unresolved export fields, and claim boundaries without rerunning rollouts.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_source_coverage_audit_2026-06-19.json`:
  machine-readable output for the figure/table source coverage audit.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_caption_claim_packet_2026-06-19.md`:
  source-derived figure/table caption-claim packet that provides
  journal-neutral draft captions, allowed claims, forbidden claims, and
  unresolved manuscript fields without rerunning rollouts.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_caption_claim_packet_2026-06-19.json`:
  machine-readable output for the figure/table caption-claim packet.
- Original-vision validation design and registry:
  `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
  and
  `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`:
  figure-ready seed-wise reward comparison for 10x12/top4 vs 20x16/top5.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`:
  figure-ready post-hoc top-k diagnostics for failed Windows 50-state labels.
- `paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_family_summary_2026-06-10.csv`:
  Figure 4 source data for Dongxing pairwise-only, 20x16, and 50x16
  return-label scaling.
- `paper10_geojepa_mpc/experiments/results/e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`:
  Figure 5 source data for Dongxing low-label transfer stress testing.
- `scripts/paper10/plot_frontier_random050_figures.py`:
  offline plotting script for the seed-wise reward and top-k diagnostic figures;
  writes generated figure files under ignored `reviewer_outputs/` by default.
- `scripts/paper10/plot_main_figure1_workflow.py`:
  offline plotting script for the Main Figure 1 monitor-gated workflow
  schematic. The default preview writes PNG/SVG/PDF files under ignored
  `reviewer_outputs/`; `--variant final --formats svg pdf png` regenerates
  the tracked CEUS final artwork candidate assets.
- `scripts/paper10/plot_integrated_dongxing_figures.py`:
  offline plotting script for integrated Dongxing Figure 4 and Figure 5
  previews from tracked CSV source data.
- `paper10_geojepa_mpc/experiments/monitor_threshold_sensitivity.py`:
  source-derived CEUS monitor-threshold sensitivity audit runner.
- `paper10_geojepa_mpc/experiments/ceus_mechanism_claim_audit.py`:
  source-derived CEUS mechanism/baseline claim audit runner.
- `paper10_geojepa_mpc/experiments/real_env_longhorizon_confirmatory_audit.py`:
  source-derived matched 5-seed real-environment Paper9/value-filter audit runner.
- scripts/paper10/preflight_submission_checks.py:
  submission preflight checker for archive manifest required fields,
  included-path resolution, excluded/local Git-tracking guardrails,
  public-facing placeholder leakage, vague data-route wording, prohibited
  50-state wording, public-manuscript Paper9 placeholder leakage,
  citation-key resolution, reviewer smoke protocol/log cross-links, integrated
  Dongxing figure/source-data, Data Availability route, figure/table
  numbering-freeze, blocker-decision-packet, integrated target-venue
  conversion-checklist, citation/statistical-reporting policy, CEUS
  reviewer-improvement packet cross-links, CEUS manuscript draft constraints,
  the Stage 3 manuscript reframe claim boundary, and the CEUS Stage 3
  manuscript draft claim boundary, formal-manuscript blueprint and
  source-derived claim audit, real-data availability audit, real-data integrity
  smoke, five-step real-environment execution-chain smokes, their boundary
  audit, manuscript result-table freeze, manuscript text/table consistency
  audit, figure/table source coverage audit, and figure/table caption-claim
  packet.
- `references/paper10_verified_references_2026-06-09.bib`:
  verified BibTeX entries for the first Paper10 manuscript citation pass.
- `references/paper10_local_sources_2026-06-09.bib`:
  local-only unpublished-source placeholders for internal manuscript drafting,
  including Paper9 task/reward provenance.
- `references/paper10_citation_map_2026-06-09.md`:
  claim-to-citation mapping for the E0 manuscript draft, including local-only
  Paper9 and 50-state boundary notes.
- `references/paper10_paper9_local_source_status_2026-06-09.md`:
  status note documenting the local Paper9 v6 manuscript source and the
  requirement to replace or formalize it before submission.
- `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`:
  five-seed 100-step rollout summary for the 20x16/h5 scale-up.
- `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt`:
  checkpoint used by the 20x16/h5 scale-up rollouts.
- Root reproducibility documents:
  - `README.md`
  - `REPRODUCIBILITY.md`
  - `DATA_AVAILABILITY.md`
  - `requirements.txt`
  - `.gitignore`
  - `references/README.md`

## Excluded Intentionally

- Python caches: `__pycache__/`, `.pytest_cache/`, `*.pyc`.
- Local virtual environments.
- Full Bishan Tool2 data under `tool2/`, because it is approximately 1.65 GB.
- Full prepared geospatial inputs under `dem_slope_analysis/` and
  `results_real/`, because they should be supplied through the project data
  archive or generated by the upstream preparation pipeline.
- Third-party paper PDFs. The LE-WM paper and upstream GitHub project are listed
  in `references/README.md` instead.

## Large File Check

At packaging time, no included file was larger than 100 MB.

