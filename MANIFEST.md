# Manifest

This repository is a Paper10 reproducibility package. It intentionally includes
source code, tests, result evidence, checkpoints, compatibility code, and small
data needed for smoke verification.

## Included

- `paper10_geojepa_mpc/`: 288 non-cache files copied from the active Paper10
  workspace, including 57 Python files, 101 JSON files, 85 Markdown files,
  10 CSV files,
  9 NPZ files, 10 PyTorch checkpoint files, and 16 log files.
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
- `scripts/paper10/plot_integrated_dongxing_figures.py`:
  offline plotting script for integrated Dongxing Figure 4 and Figure 5
  previews from tracked CSV source data.
- `scripts/paper10/preflight_submission_checks.py`:
  submission preflight checker for archive manifest required fields,
  included-path resolution, excluded/local Git-tracking guardrails,
  public-facing placeholder leakage, vague data-route wording, prohibited
  50-state wording, public-manuscript Paper9 placeholder leakage,
  citation-key resolution, reviewer smoke protocol/log cross-links, integrated
  Dongxing figure/source-data, Data Availability route, figure/table
  numbering-freeze, blocker-decision-packet, integrated target-venue
  conversion-checklist, citation/statistical-reporting policy, CEUS
  reviewer-improvement packet cross-links, CEUS manuscript draft constraints,
  and the Stage 3 manuscript reframe claim boundary.
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
