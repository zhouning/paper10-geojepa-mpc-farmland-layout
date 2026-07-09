# Paper10 archive source-data closeout

Date: 2026-07-09

Status: archive_source_data_closeout_prepared_not_submission_ready

Scope: source-derived closeout for Record 1 archive metadata, FAIR/DataCite fields and figure/table source-data mapping for the CEUS route. This packet does not rerun training, rerun rollouts, add new experimental claims or grant submission approval.

## Source basis

- `e0_archive_manifest_2026-06-09.csv`
- `e0_archive_metadata_templates_2026-06-09.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`
- `e0_paper10_figure_table_source_coverage_audit_2026-06-19.md`
- `e0_paper10_figure_table_caption_claim_packet_2026-06-19.md`
- `e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md`
- `e0_paper10_public_release_rights_gate_2026-07-09.md`
- `e0_paper10_dltb_leakage_evidence_audit_2026-07-09.md`
- `e0_paper10_ceus_confidential_dltb_acceptance_packet_2026-07-09.md`

Git commit scanned: `3df9429fb8785539020aa7c7dbce1c925ca18d9b`.

## Record 1 public package

Record 1 contains the public code/evidence package: code, tests, scripts, smoke data, generated non-DLTB JSON/Markdown/CSV/NPZ outputs, source-data tables, checkpoints, model-weight artifacts, metadata, reproducibility documentation, and the tracked Main Figure 1 final artwork candidate. Code and scripts are Apache-2.0. Generated non-DLTB artifacts are CC0-1.0.

Record 1 excludes original Bishan DLTB and original Dongxing DLTB. Original raw DLTB remains confidential_no_external_access and cannot be provided externally.

## FAIR and DataCite closeout

- Findable: Record 1 has public metadata fields prepared and the 4open README.md direct reviewer link recorded.
- Accessible: access conditions are explicit; raw DLTB is restricted with no external access route, while public package metadata can remain public.
- Interoperable: source-data files use tracked CSV, JSON, Markdown, SVG, PDF, PNG and NPZ package formats, with figure/table mappings recorded.
- Reusable: Apache-2.0 and CC0-1.0 rights terms are recorded for licensable code and generated non-DLTB artifacts; original DLTB is not relicensed.
- DataCite fields prepared: title, creator placeholders, publisher/repository, publication year, resource type, version, rights, related identifiers and description are available in the archive metadata template.

## Figure and table source-data alignment

| asset | closeout status |
|---|---|
| Main Figure 1 | final artwork candidate exported; SVG/PDF/PNG tracked; journal file-format confirmation remains open |
| Main Figure 2 | export_ready; source coverage recorded |
| Main Figure 3 | export_ready; source coverage recorded |
| Main Figure 4 | export_ready; Dongxing return-label source CSV recorded |
| Supplementary Figure S1 | export_ready; Dongxing low-label source CSV recorded |
| Main Tables 1-3 | export_ready under tracked source tables |

The final export package and source-coverage audit remain the controlling files for figure/table rendering. `e0_paper10_main_figure1_final_artwork_closeout_2026-07-09.md` supersedes the earlier pending_artwork row for Main Figure 1 only; it does not change quantitative figure/table evidence or manuscript claims.

## Resolved submission fields

- Main Figure 1 final artwork: exported_final_candidate.

## Unresolved submission fields

- Target-journal/editor acceptance of confidential raw-DLTB non-availability: not_recorded.
- Exact 4open snapshot identifier: not_visible_on_platform.
- Final public archive identifier: anonymous README.md direct reviewer link only.
- Final journal dimensions and file formats: not_finalized.
- Final declarations: pending_author_decision.

## Submission gate

Formal submission remains blocked. This packet is not final submission approval. A preflight pass means that Record 1 archive metadata and figure/table source-data mapping are internally aligned; it does not make the paper final-submission-ready.
