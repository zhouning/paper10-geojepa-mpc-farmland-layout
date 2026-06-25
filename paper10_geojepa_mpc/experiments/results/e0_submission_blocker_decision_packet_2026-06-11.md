# Paper10 submission blocker decision packet

Date: 2026-06-11

This packet is a submission-control document for the current with-Dongxing
Paper10 package. It is not a final manuscript, not a journal-specific checklist,
and not a substitute for author decisions. It consolidates the remaining
blocking decisions that must be closed before a final submission manuscript can
be created.

## Source basis

- `e0_post_dongxing_submission_gap_audit_2026-06-10.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`
- `e0_paper10_formal_manuscript_draft_2026-06-20.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_ceus_reviewer_improvement_packet_2026-06-12.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`

## Current no-go status

Do not submit until the author team has closed the decisions below:

The current target route for the next manuscript-conversion pass is frozen as
the CEUS Research Article candidate route recorded in
`e0_ceus_reviewer_improvement_packet_2026-06-12.md`. That closes the venue
choice for this conversion pass and leaves the repository DOI, code licence,
generated-data rights, full-data access, citation, statistical-reporting, and
final export blockers below.

1. Repository DOI or reviewer link.
2. Code licence.
3. Generated-data rights and checkpoint/model-weight rights.
4. Full Bishan Tool2 data access route.
5. GPKG-root geospatial inputs access route.
6. Dongxing/Neijiang prepared data access route.
7. Citation policy for local-only sources, preprints, and final reference style.
8. Statistical reporting policy for descriptive results versus hypothesis tests.
9. Final journal-specific figure/table count, source-data naming, and export
   formats.

## Decision table

| decision | current status | minimum close-out before manuscript conversion | files to update after decision |
|---|---|---|---|
| Target journal and article type | Current status: frozen as CEUS Research Article candidate route. | Apply CEUS journal instructions in the current conversion pass; exact journal-format details will be finalized when the submission file is created. | Final manuscript; `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`; README submission notes. |
| Repository DOI or reviewer link | Current status: unresolved. | Archive the exact submission commit or create a reviewer link; record persistent identifier, version, access timing, and whether the link is anonymous. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_manifest_2026-06-09.csv`; `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`; final manuscript. |
| Code licence | Current status: unresolved. | Select a named software licence and confirm it covers only code and scripts that the authors can license. | Repository licence file if added; `MANIFEST.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; archive metadata. |
| Generated-data rights | Current status: unresolved. | Select rights terms for generated JSON, Markdown, CSV, NPZ labels, checkpoints, model weights, and shareable source-data files without relicensing restricted raw geospatial data. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_metadata_templates_2026-06-09.md`; archive metadata. |
| Full Bishan Tool2 data access route | Current status: unresolved. | Choose public DOI, controlled-access repository, or institutional request route; name owner/access body, eligibility, review criteria, reviewer route, response expectation, and data-use terms. | `DATA_AVAILABILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; final manuscript. |
| GPKG-root geospatial inputs access route | Current status: unresolved. | Choose public DOI or controlled-access metadata route for `DLTB_with_slope.gpkg`, block products, and township inputs used by reproducible label generation and rollouts. | `DATA_AVAILABILITY.md`; `REPRODUCIBILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; final manuscript. |
| Dongxing/Neijiang prepared data access route | Current status: unresolved. | Choose public DOI or controlled-access metadata route for prepared 3711-block products, 76,376 parcel assignments, transition/pairwise files, environment wrappers, and slope-enriched geospatial inputs. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; `e0_source_data_map_with_dongxing_2026-06-11.md`; final manuscript. |
| Citation policy | Current status: unresolved. | Decide whether local-only sources can be formalized, whether preprints are acceptable for the target venue, and which verified references are required in Introduction, Methods, Results, and Discussion. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; `references/paper10_citation_map_2026-06-09.md`; final manuscript; bibliography files. |
| Statistical reporting policy | Current status: unresolved. | Decide whether descriptive means and standard deviations are sufficient, or define pre-declared statistical tests, comparison groups, multiple-comparison handling, and reporting precision. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; Results section; table captions; `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`; final manuscript. |
| Final figure/table export package | Current status: frozen export contract for the current CEUS route; Main Figure 1 artwork remains pending. | Use `e0_paper10_final_figure_table_export_package_2026-06-20.md` with `e0_integrated_figure_table_numbering_freeze_2026-06-11.md` as the current export contract, then finalize PDF/SVG and raster previews only as required. | Figure exports; source-data maps; final manuscript; supplementary files; `e0_paper10_final_figure_table_export_package_2026-06-20.md`. |

## Claim locks

- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim direct 50-state Bishan scale-up success.
- Keep Bishan 20x16/top5 as the primary positive result.
- Treat the 2026-06-20 50x24 candidate-score sweep as boundary evidence only.
- Use Dongxing/Neijiang as external-region calibration and transfer stress-test
  evidence.
- Keep Dongxing scratch advantages at 50x16 and at 5/10 low-label budgets
  visible in the Results, figures, tables, or Supplementary Information.

## Required author answers

The next manuscript-conversion pass needs these concrete answers:

| field | required answer |
|---|---|
| Target journal | CEUS Research Article candidate route, frozen for the current conversion pass. |
| Submission archive route | Public DOI before submission, anonymous reviewer link, or private review route. |
| Code licence | Named licence or institutional restriction. |
| Data rights terms | Named data licence for shareable derived data, or restriction statement. |
| Full Bishan route | Public DOI or controlled-access record. |
| GPKG-root route | Public DOI or controlled-access record. |
| Dongxing/Neijiang route | Public DOI or controlled-access record. |
| Reviewer data access | Whether reviewers receive public download, private link, or controlled-access credentials. |
| Citation policy | Acceptable source types and local-only source replacement route. |
| Statistics policy | Descriptive-only reporting or defined statistical tests. |

## Preflight interpretation

Passing preflight with this packet means the blockers are explicitly tracked and
cross-linked. It does not mean the blockers are solved. Final submission remains
blocked until the author team fills the unresolved fields and updates the Data
and Code Availability statement, archive metadata, final manuscript, and source
data maps.
