# Paper10 GeoJEPA-MPC Farmland Layout

Reproducibility package for Paper10:

`JEPA-Regularized Geospatial World Models for Constrained Farmland Layout Planning`

The repository packages the Paper10 code, tests, experiment outputs, saved
checkpoints, compatibility code borrowed from the Paper9 environment, and the
small smoke Tool2 dataset needed for reviewer-side verification. The full
Bishan Tool2 dataset is larger than a normal source repository and is documented
as an external data dependency in `DATA_AVAILABILITY.md`.

The current paper-facing boundary is the validated Bishan 20x16/top5 positive
anchor plus the 2026-06-20 Stage 3 50x24 candidate-score sweep, which kept the
50-state line below the matched Paper9 baseline.

## Latest Packaged Experiment

This package now includes the 2026-06-08 `frontier_random050` value-head
20x16/h5 scale-up:

- value labels: `paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`
- trained checkpoint: `paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt`
- scale-up report: `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_20x16_h5_seed44_top5_report_2026-06-08.md`
- five-seed rollout summary: `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`

The scale-up uses `selector=value_filter`, executable masks, `H=5`, `K=50`,
candidate blend weight `0.1`, and the diagnostics-selected top-5 value-head
gate. The recorded 100-step seeds 0-4 mean total reward is `69.4705` with sample
standard deviation `1.0004`.

The latest boundary update is the 2026-06-20 Stage 3 50x24 candidate-score
sweep on the same `frontier_random050` line. `blend0.10` remained the best
candidate-filter variant, but it still stayed below the matched Paper9
baseline, so the manuscript claim boundary did not change.
A 2026-06-27 locked full-Bishan 100-step seed0 pilot tests the matched
Paper9 and Paper10 value-filter policies under the same H=5/K=50/executable-mask
settings. The two traces diverged at step 9, and the value-filter candidate
scored `67.7135` versus `70.9543` for matched Paper9. This remains tracked as
pilot evidence in `paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.md`.

The matched seeds `0-4` follow-up is now source-audited in
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md`.
It links the tracked raw rollout files back to the seed0 pilot audit and reports
matched Paper9 mean reward `67.5437` (sample std `7.2246`) versus value-filter
mean reward `69.4705` (sample std `1.0004`). The value-filter run wins 3/5
seeds and loses on seeds 0 and 4, so this supports only a bounded descriptive
Bishan 5-seed statement, not an inferential, multi-region, or 50-state scale-up
claim.

Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
as the current CEUS baseline and inference hardening audit. It fixes matched
Paper9 versus value-filter wording, keeps the 5-seed result descriptive and
mixed seed-wise, and prevents uniform or inferential superiority claims.

Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md`
as the current algorithm-readiness boundary for the 2026-07-07 true-reward
margin guard evidence. It promotes Bishan 20x16/top5 `audit7x7 margin=1.50`
as the current primary guard candidate and 10x12/top4 `rewardtop7 margin=1.60`
as setting-specific consistency support, while blocking universal-margin,
50-state scale-up, transfer-superiority, deployment-ready, and final-submission
claims.

The previous 10x12/h5 top-4 pilot remains packaged as the direct baseline. Its
recorded 100-step seeds 0-4 mean total reward is `65.2566` with sample standard
deviation `5.0037`.

The tested 50-state `frontier_random050` label sets are negative diagnostics,
not training inputs. The macOS `50x24/h5 seed45` run and the Windows seed46
ablation grid failed the monitor gates, so the current paper-facing claim stays
anchored on the reproducible 20x16/top5 result.

Paper-facing writing assets are tracked under
`paper10_geojepa_mpc/experiments/results/`:

- `e0_frontier_random050_results_synthesis_2026-06-09.md`
- `e0_frontier_random050_manuscript_section_draft_2026-06-09.md`
- `e0_frontier_random050_manuscript_tables_2026-06-09.md`
- `e0_frontier_random050_manuscript_scaffold_2026-06-09.md`
- `e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md`
- `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`
- `e0_frontier_random050_introduction_cited_draft_2026-06-09.md`
- `e0_frontier_random050_methods_draft_2026-06-09.md`
- `e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_submission_route_and_archive_plan_2026-06-09.md`
- `e0_archive_metadata_templates_2026-06-09.md`
- `e0_archive_manifest_2026-06-09.csv`
- `e0_source_data_map_2026-06-09.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_reviewer_smoke_replication_protocol_2026-06-09.md`
- `e0_reviewer_smoke_verification_log_2026-06-10.md`
- `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`
- `e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md`
- `e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md`
- `e0_submission_readiness_checklist_2026-06-09.md`
- `e0_bishan_task_environment_self_contained_methods_2026-06-09.md`
- `e0_reward_and_rollout_metric_definitions_2026-06-09.md`
- `e0_citation_and_claim_checklist_2026-06-09.md`
- `e0_frontier_random050_figure_plan_2026-06-09.md`
- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_post_dongxing_submission_gap_audit_2026-06-10.md`
- `e0_integrated_dongxing_figure_plan_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_ceus_reviewer_improvement_packet_2026-06-12.md`
- `e0_ceus_research_article_manuscript_draft_2026-06-12.md`
- `e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- `e0_ceus_stage3_manuscript_draft_2026-06-18.md`
- `e0_paper10_formal_manuscript_draft_2026-06-20.md`
- `e0_paper10_bounded_manuscript_assembly_draft_2026-06-27.md`
- `e0_paper10_main_figure1_artwork_preview_2026-06-27.md`
- `e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md`
- `ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.svg`
- `ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.pdf`
- `ceus_submission_assets/main_figure1_workflow/figure_1_monitor_gated_geojepa_mpc_workflow.png`
- `e0_paper10_target_journal_fit_assessment_2026-06-27.md`
- `e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.md`
- `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md`
- `e0_paper10_ceus_review_optimization_register_2026-06-27.md`
- `e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
- `e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`
- `e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`
- `e0_paper10_formal_output_readiness_audit_2026-07-06.md`
- `e0_paper10_ceus_formal_output_conversion_patch_2026-07-06.md`
- `e0_paper10_ceus_clean_main_manuscript_draft_2026-07-06.md`
- `e0_paper10_ceus_highlights_2026-07-06.txt`
- `e0_paper10_experiment_freeze_audit_2026-06-27.md`
- `e0_paper10_experiment_closure_register_2026-06-27.md`
- `e0_paper10_project_proposal_opening_report_2026-06-18.md`
- `e0_paper10_author_decision_matrix_2026-06-18.md`
- `e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.json`
- `e0_paper10_claim_source_consistency_audit_2026-06-18.md`
- `e0_paper10_real_data_availability_audit_2026-06-18.md`
- `e0_paper10_real_data_integrity_smoke_2026-06-18.md`
- `e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.md`
- `e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.md`
- `e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md`
- `e0_paper10_real_env_matched_paper9_smoke_5step_h5_k50_seed0_2026-06-27.md`
- `e0_paper10_real_env_matched_value_filter_smoke_5step_h5_k50_seed0_2026-06-27.md`
- `e0_paper10_real_env_matched_smoke_boundary_audit_2026-06-27.md`
- `e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`
- `e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md`
- `e0_paper10_figure_table_source_coverage_audit_2026-06-19.md`
- `e0_paper10_figure_table_caption_claim_packet_2026-06-19.md`
- `e0_data_code_availability_draft_2026-06-09.md` now includes the
  Dongxing/Neijiang prepared-data access route that must be closed before
  submission.

Verified citation assets are tracked under `references/`:

- `paper10_verified_references_2026-06-09.bib`
- `paper10_local_sources_2026-06-09.bib`
- `paper10_citation_map_2026-06-09.md`
- `paper10_paper9_local_source_status_2026-06-09.md`

## Repository Layout

- `paper10_geojepa_mpc/`: Paper10 models, planning utilities, training helpers,
  experiments, tests, checkpoints, and recorded result artifacts.
- `arcgis_toolbox_paper9/private_source/`: Paper9 compatibility code used by
  Paper10 real-environment rollouts.
- `county_env.py`: Paper9 `CountyLevelEnv` environment required by the bundled
  compatibility layer.
- `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`: small smoke
  Tool2 dataset included in Git.
- `paper7/data/`: small GeoFM embedding asset used by optional fusion tests and
  ablations.
- `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`: Google Colab
  notebook retained for 50x24/h5 diagnostic reproduction or re-parameterized
  future runs.
- `docs/windows_frontier_random050_ablation.md`: Windows CPU guide for
  reproducing or editing the `frontier_random050` 50-state label-only ablation
  grid.
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`: resumable Windows
  PowerShell runner for that ablation grid.
- `docs/superpowers/`: Paper10 design and implementation planning notes.
- `DATA_AVAILABILITY.md`: full-data layout and large-file policy.
- `REPRODUCIBILITY.md`: commands for tests, smoke runs, and full-data runs.
- `MANIFEST.md`: inventory of included and intentionally externalized assets.

## Quick Start

Create and activate an environment, then install the Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the reviewer smoke verification:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

For the ordered reviewer-side smoke replication protocol, including expected
array shapes and the boundary between clone-only smoke checks and full Bishan
reruns, see
`paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_replication_protocol_2026-06-09.md`.
The latest local execution log for that protocol is
`paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_verification_log_2026-06-10.md`.

Run the included smoke data summary:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

Run the submission preflight checks before archive release or manuscript
backfill:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/preflight_submission_checks.py
```

Use `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md` as the current no-go
submission-readiness boundary. It records that preflight passing does not mean
final submission readiness.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_experiment_freeze_audit_2026-06-27.md`
as the current algorithm-freeze decision boundary before deciding whether to
continue algorithm development or move into bounded manuscript assembly. It
keeps the default path on experiment closure and claim-controlled writing,
while reserving algorithm redesign for a deliberate stronger-claim track.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_experiment_closure_register_2026-06-27.md`
as the current experiment-closure register for default comparator,
statistics, figure/export, data-route, and algorithm-work decisions before
the next bounded manuscript assembly pass.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_bounded_manuscript_assembly_draft_2026-06-27.md`
as the current bounded manuscript assembly draft before journal-specific
formatting, figure export, DOI/licence backfill, or data-access wording.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`
as the current CEUS baseline-hardened assembly draft for the next manuscript
writing pass. It incorporates the 2026-07-06 baseline and inference hardening
audit, keeps the Bishan 20x16/top5 result descriptive, and preserves Stage 3,
Dongxing/Neijiang and data-access boundaries.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_formal_output_readiness_audit_2026-07-06.md`
as the current formal-output readiness audit. It records that Paper10 can be
converted into a bounded CEUS manuscript draft but still has open DOI, licence,
full-data access, declaration and figure-export blockers before formal
submission.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_formal_output_conversion_patch_2026-07-06.md`
and
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_highlights_2026-07-06.txt`
for the next CEUS formal-output conversion pass.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_clean_main_manuscript_draft_2026-07-06.md`
as the current clean main-manuscript draft for author review and journal-format
conversion. It removes internal handoff and claim-lock material from the main
body while preserving the no-go submission boundary.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_main_figure1_artwork_preview_2026-06-27.md`
as the Main Figure 1 workflow-artwork preview record. Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md`
as the current Main Figure 1 final artwork candidate closeout. It records the
tracked SVG/PDF/PNG assets and keeps final journal file-format confirmation,
archive identifier backfill, declarations, and confidential-DLTB acceptance open
before formal submission.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_target_journal_fit_assessment_2026-06-27.md`
as the current target-journal route assessment. It recommends a CEUS-first
route by default, with EMS, CEA, SAT, AI in Agriculture, JAG, and Scientific
Reports treated as conditional alternatives.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.md`
as the current monitor-threshold sensitivity audit before defending monitor
threshold choices or the 10x12/top4 historical pilot boundary.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md`
as the current mechanism/baseline claim audit before interpreting matched
Paper9, pairwise-only, no-mask, ungated-top4, secondary-metric, or 50-state
results.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_review_optimization_register_2026-06-27.md`
as the current CEUS review-driven optimization register. It records which
review concerns were addressed by source-derived technical audits and which
still need new real-data or multi-region experiments.

Generate the Main Figure 1 workflow preview:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/plot_main_figure1_workflow.py
```

Regenerate the tracked Main Figure 1 final artwork candidate:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/plot_main_figure1_workflow.py --variant final --formats svg pdf png
```

Generate draft integrated Dongxing Figure 4 and Figure 5 previews from tracked
CSV source data:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/plot_integrated_dongxing_figures.py
```

Before manuscript conversion, use
`paper10_geojepa_mpc/experiments/results/e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
as the current generic figure/table numbering freeze.
Use
`paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md`
as the current no-go decision packet before creating a journal-specific
submission manuscript.
Use
`paper10_geojepa_mpc/experiments/results/e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
as the current with-Dongxing target-venue and manuscript-conversion checklist.
Use
`paper10_geojepa_mpc/experiments/results/e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
as the current citation and statistical-reporting boundary before final
manuscript conversion.
Use
`paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md`
as the current CEUS reviewer-improvement packet before converting Methods,
Discussion, Data Availability, or reviewer-response text.
Use
`paper10_geojepa_mpc/experiments/results/e0_ceus_research_article_manuscript_draft_2026-06-12.md`
as the current CEUS Research Article candidate manuscript draft. It remains
blocked for final submission until repository identifiers, licences, full-data
routes, citation policy, statistical policy, and final figure exports are
closed.
Use
`paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
as the current Stage 3 claim-boundary layer before editing the CEUS draft. The
Stage 3 confirmatory 50-state rows did not beat the matched Paper9 baseline,
so final manuscript conversion must use the 2026-06-18 replacement title,
abstract, Results, Discussion, and Conclusion.
Use
`paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_draft_2026-06-18.md`
as the current CEUS Stage 3 manuscript draft. It applies the Stage 3 reframe to
the earlier CEUS candidate draft and remains blocked for final submission until
repository identifiers, licences, full-data routes, baseline policy, citation
policy, statistical policy, and final figure exports are closed.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_project_proposal_opening_report_2026-06-18.md`
as the current Chinese project-proposal/opening-report substitute for temporary
topic approval before the formal Paper10 manuscript is ready.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_author_decision_matrix_2026-06-18.md`
as the current author-decision matrix before formal manuscript conversion.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`
as the current formal-manuscript assembly blueprint before replacing the Stage
3 draft with a journal-specific manuscript.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_claim_source_consistency_audit_2026-06-18.md`
as the current source-derived consistency audit for Bishan, Stage 3, and
Dongxing/Neijiang claim boundaries.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_availability_audit_2026-06-18.md`
as the current real-data availability audit for full Bishan, GPKG-root, block
input, and Dongxing/Neijiang external-dependency routing before final Data and
Code Availability wording.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_integrity_smoke_2026-06-18.md`
as the current metadata-only integrity smoke for readable full Tool2 NPZ,
GeoPackage, block-directory, township JSON, and Dongxing/Neijiang directory
structures.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.md`
as the current five-step full-Bishan real-environment execution-chain smoke
for the Paper10 checkpoint, Paper9 adapter, MPC selector, executable mask, and
`CountyLevelEnv.step`. It is not a planning-quality result and does not change
manuscript performance claims.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.md`
as the current five-step full-Bishan value-filter execution-chain smoke for
the 20x16/top5 checkpoint. It includes one negative reward step and is not
short-horizon performance evidence for the selector.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md`
as the current boundary audit for the two real-environment smoke reports. It
records that they use different checkpoint, selector, horizon, and top_k
settings and must not be treated as a short-horizon performance comparison.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_matched_smoke_boundary_audit_2026-06-27.md`
as the current matched full-Bishan smoke boundary audit. It records that the
matched Paper9 and value-filter five-step H=5/K=50 traces are identical and
therefore support execution-chain reachability only, not short-horizon
value-filter superiority.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md`
as the current source-derived raw-rollout consistency audit for the Bishan
20x16/top5 frozen anchor. It recomputes the five seed rewards from tracked raw
step records and checks them against the packaged rollout summary and Stage 3
frozen-anchor row without rerunning rollouts or adding a new experimental claim.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`
as the current manuscript result-table freeze before editing Results, captions,
or claim-evidence maps. It derives the Bishan anchor, Stage 3 boundary rows,
and claim-status table from tracked Stage 3, claim-source, and raw-rollout
audit JSON files without adding a new experimental claim.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md`
as the current manuscript text/table consistency audit before treating the
Stage 3 manuscript draft, proposal report, author matrix, or assembly blueprint
as synchronized with the frozen result tables.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_source_coverage_audit_2026-06-19.md`
as the current figure/table source coverage audit before treating the formal
manuscript figure and table assembly map as source-covered. It records source
coverage only. Main Figure 1 final artwork is superseded by the
2026-07-09 final-artwork closeout; final journal dimensions, placement,
captions and export-system confirmation remain submission blockers.
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_caption_claim_packet_2026-06-19.md`
as the current figure/table caption-claim packet before drafting figure/table
captions or claim-evidence text. It provides journal-neutral draft captions,
allowed claims, forbidden claims, and unresolved manuscript fields without
rerunning rollouts or adding a new experimental claim.
- Original-vision validation design and registry:
  `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
  and
  `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`.

## Full Experiments

Full Bishan training and real-environment rollout commands require the external
prepared data under the repository root:

- `tool2/transitions.npz`
- `tool2/pairwise.npz`
- `dem_slope_analysis/output/DLTB_with_slope.shp` or `.gpkg`
- `results_real/blocks/`
- `townships.json`

See `DATA_AVAILABILITY.md` for exact placement and `REPRODUCIBILITY.md` for
the command sequence.

## Colab 50x24/h5 Diagnostic

The repository includes
`notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`. Its original
50x24/h5 seed45 target has since failed the monitor gate on macOS, so the
notebook should be treated as a diagnostic/reproduction template unless its
parameters are deliberately changed.

## macOS 50x24/h5 Diagnostic

When Colab compute quota is unavailable, the same diagnostic can be reproduced
locally from `docs/macos_frontier_random050_50x24_h5.md`. The tracked runner
`scripts/macos/run_frontier_random050_50x24_h5.sh` validates local full-data
placement, writes outputs outside the Git checkout, and skips steps whose final
artifacts already exist.

## Windows 50-State Ablation

The Windows workstation can run Paper10 on CPU with the full data rooted at
`D:\test`. Use `docs/windows_frontier_random050_ablation.md` and
`scripts/windows/run_frontier_random050_ablation_grid.ps1` for reproducing or
editing the `frontier_random050` 50-state label-only ablation grid. The packaged
seed46 grid failed all default and post-hoc checks; reuse the runner only for
reproduction or after editing the local ignored grid. The runner defaults to
monitor-only mode and trains only when a gate passes and local config explicitly
sets `TrainOnPass = 1`.

For the current continuation decision, see
`docs/superpowers/notes/2026-06-09-paper10-50state-redesign-handoff.md`.

## Verification Status

The source package was copied from the active Paper10 workspace on 2026-06-08.
Before packaging, the Paper10 test suite was run with:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `88 passed in 49.97s`.

After packaging, the same test suite was run from this repository directory:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result: `88 passed in 43.25s`.

After adding the Windows ablation package on 2026-06-09, the suite was rerun
from this repository directory with the same Python executable.

Result: `105 passed in 3.74s`.

After adding manuscript tables, figure assets, the 50-state redesign handoff,
the manuscript scaffold, and the figure plan on 2026-06-09, the suite was rerun
again from this repository directory with the same Python executable.

Result: `108 passed in 3.75s`.

After adding the paper-facing Methods draft on 2026-06-09, the suite was rerun
again from this repository directory with the same Python executable.

Result: `108 passed in 4.68s`.

After adding the reward and rollout metric definitions note on 2026-06-09, the
suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After adding the submission-readiness checklist on 2026-06-09, the suite was
rerun again from this repository directory with the same Python executable.

Result: `108 passed`.

After adding the self-contained Bishan task/environment Methods note on
2026-06-09, the suite was rerun again from this repository directory with the
same Python executable.

Result: `108 passed`.

After adding the self-contained integrated manuscript variant on 2026-06-09,
the suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After adding the submission archive route plan and archive metadata templates
on 2026-06-09, the suite was rerun again from this repository directory with
the same Python executable.

Result: `108 passed in 4.11s`.

After adding the E0 source-data map on 2026-06-09, the suite was rerun again
from this repository directory with the same Python executable.

Result: `108 passed`.

After adding the machine-readable E0 archive manifest on 2026-06-09, the suite
was rerun again from this repository directory with the same Python executable.

Result: `108 passed`.

After adding the E0 archive release and DOI backfill checklist on 2026-06-09,
the suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After adding the E0 target-venue and manuscript-conversion checklist on
2026-06-09, the suite was rerun again from this repository directory with the
same Python executable.

Result: `108 passed`.

After adding the E0 self-contained manuscript submission gap audit on
2026-06-09, the suite was rerun again from this repository directory with the
same Python executable.

Result: `108 passed`.

After adding the E0 data access and rights decision register on 2026-06-09, the
suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After adding the E0 reviewer smoke replication protocol on 2026-06-09, the
suite was rerun again from this repository directory with the same Python
executable.

Result: `108 passed`.

After running and logging the reviewer smoke replication protocol on
2026-06-10, the suite was rerun again from this repository directory with the
same Python executable.

Result: `108 passed`.

After adding the submission preflight checker on 2026-06-10, the suite was
rerun again from this repository directory with the same Python executable.

Result: `111 passed`.

After extending the submission preflight checker to validate archive manifest
path resolution and excluded/local Git-tracking guardrails on 2026-06-10, the
suite was rerun again from this repository directory with the same Python
executable.

Result: `114 passed`.

After extending the submission preflight checker to reject unresolved public
bracket placeholders in public-facing docs and integrated manuscript drafts on
2026-06-10, the suite was rerun again from this repository directory with the
same Python executable.

Result: `115 passed`.

After extending the submission preflight checker to reject vague public
data-route wording in public-facing docs and integrated manuscript drafts on
2026-06-10, the suite was rerun again from this repository directory with the
same Python executable.

Result: `116 passed`.

After adding integrated Dongxing Figure 4/5 source-data maps, the offline
Dongxing plotting script, Dongxing/Neijiang Data Availability route checks, and
preflight cross-link checks on 2026-06-11, the suite was rerun again from this
repository directory with the same Python executable.

Result: `133 passed in 8.86s`.

After adding the integrated figure/table numbering freeze and preflight
cross-link check on 2026-06-11, the suite was rerun again from this repository
directory with the same Python executable.

Result: `133 passed in 9.38s`.

After adding the with-Dongxing target-venue and manuscript-conversion checklist
and preflight cross-link check on 2026-06-12, the suite was rerun again from
this repository directory with the same Python executable.

Result: `133 passed in 16.30s`.

After adding the integrated citation and statistical-reporting policy and
preflight cross-link check on 2026-06-12, the suite was rerun again from this
repository directory with the same Python executable.

Result: `133 passed in 10.78s`.

Reviewers should run the relative-path command in `REPRODUCIBILITY.md` after
cloning.
