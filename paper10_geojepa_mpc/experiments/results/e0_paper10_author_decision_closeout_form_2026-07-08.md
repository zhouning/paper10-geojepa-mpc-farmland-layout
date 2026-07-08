# Paper10 author-decision closeout form

Date: 2026-07-08

Status: author_input_partially_provided

Status note: source-derived; no rollout or training rerun; no submission approval.

This closeout form converts the post-guard submission blocker state into an author-facing intake sheet. It does not make author decisions, does not create repository identifiers, and does not replace institutional data-rights approval.

## Source basis

- `e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json`
- `e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_paper10_author_decision_matrix_2026-06-18.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`

## Submission state

Formal submission remains blocked. The repository anonymous reviewer link has been provided, but it still requires a non-author browser-session test and final manuscript/archive backfill. Passing repository preflight means the blocker surface is tracked and guarded; it does not mean the paper has approval for formal submission.

## Use rule

Author-provided closeout must fill the fields below before final manuscript backfill. Do not use temporary cloud folders, personal drive links, local paths, or "available upon request" wording as durable access routes. Do not apply open data terms to restricted geospatial inputs unless the authors hold those rights.

## Author input recorded

- repository DOI or anonymous reviewer link: provided_pending_external_browser_test_and_backfill
- anonymous reviewer link: https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/
- command-line access check: `curl.exe -L --max-time 20 -I` reached the 4open route, observed a redirect to `/api/repo/geojepa-mpc-farmland-layout-8552/file/`, and then received `401 Unauthorized` from the unauthenticated API follow-up.
- interpretation: the 4open route exists, but reviewer-facing browser access still requires an independent non-author browser-session test before formal submission.
- remaining closeout: record the exact submission commit represented by the 4open snapshot and backfill Data and Code Availability, `MANIFEST.md`, the archive manifest, and final manuscript wording.

## Author-decision closeout table

| field | status | recommended default | author must provide | not acceptable | files to update after closeout |
|---|---|---|---|---|---|
| repository DOI or anonymous reviewer link | provided_pending_external_browser_test_and_backfill | Anonymous 4open reviewer link provided: `https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/`. | Non-author browser-session test; exact submission commit represented by the 4open snapshot; version date; access window; final Data/Code Availability and archive-manifest backfill. | Treating command-line `401 Unauthorized` API follow-up as reviewer-browser verification; marking this field fully closed before backfill. | `DATA_AVAILABILITY.md`; `MANIFEST.md`; `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_manifest_2026-06-09.csv`; final manuscript. |
| code licence | unresolved | Select a named software licence only after confirming all included code can be licensed by the authors. | Licence name or restriction statement; scope limited to licensable code and scripts; repository metadata location. | Implicit open-source wording; licence that also claims restricted third-party data. | `LICENCE` or `LICENSE` file if selected; `MANIFEST.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; archive metadata. |
| generated-data and checkpoint/model-weight rights | unresolved | Assign rights terms by artifact family and keep generated outputs separate from restricted raw geospatial inputs. | Rights for JSON, Markdown, CSV, NPZ outputs, source-data tables, checkpoints, model weights, and raw-geospatial restriction boundary. | Single broad data licence that relicenses raw geospatial inputs; missing checkpoint or model-weight terms. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_metadata_templates_2026-06-09.md`; archive metadata. |
| full Bishan Tool2 route | unresolved | Use controlled-access metadata if redistribution rights are uncertain. | Data owner or access body; restriction reason; eligible requesters; review criteria; reviewer route; data-use or no-redistribution terms. | Local path only; informal request-only wording without eligibility or review process. | `DATA_AVAILABILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; final manuscript. |
| GPKG-root geospatial route | unresolved | Use the same route family as full Bishan where possible, while naming the exact GPKG-root file families. | `DLTB_with_slope.gpkg` route; block products route; township inputs route; reviewer access route; rerun dependency note. | Claiming full reruns are reproducible from Git alone; omitting GPKG-root dependencies from Data Availability. | `DATA_AVAILABILITY.md`; `REPRODUCIBILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; final manuscript. |
| Dongxing/Neijiang prepared-data route | unresolved | Use controlled-access metadata unless the prepared external-region products can be redistributed. | Prepared block products route; parcel assignment route; transition and pairwise file route; environment wrapper route; slope-enriched input route; reviewer access route. | Derived summary CSVs as a substitute for full rerun inputs; local paths only. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; `e0_source_data_map_with_dongxing_2026-06-11.md`; final manuscript. |
| reviewer data access | unresolved | Give reviewers a tested repository-supported private link or controlled-access route for every non-public dataset required beyond smoke verification. | Which datasets reviewers can access; route for each restricted dataset; credential or request procedure; test outside author account. | Author-only local paths; untested private links; post-acceptance-only deposit promise. | `DATA_AVAILABILITY.md`; `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`; reviewer instructions; final manuscript. |
| citation policy | unresolved | Use verified public sources in manuscript text and keep local-only Paper9 material out unless it becomes public and citable. | Acceptable source types; preprint policy; local-only source replacement route; final reference style. | Local-only citation key in public manuscript; unverified reference placeholders. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; `references/paper10_citation_map_2026-06-09.md`; bibliography files; final manuscript. |
| statistical reporting policy | unresolved | Keep descriptive reporting unless the authors define tests, comparison groups, multiplicity handling, and precision before editing inferential claims. | Comparison groups; seed/checkpoint counts; test choice if any; multiplicity handling if any; precision policy. | Inferential superiority wording without committed analysis plan; post-hoc test language added only in prose. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; Results section; table captions; final manuscript. |
| Main Figure 1 / journal export rules | unresolved | Preserve the current figure/table numbering freeze and adapt exports only after target journal rules are known. | Main Figure 1 final artwork status; figure and table limits; PDF/SVG/raster requirements; source-data file names; supplementary placement rules. | Changing numbering without source-data and caption updates; submitting local preview files as final source data without mapping. | `e0_paper10_final_figure_table_export_package_2026-06-20.md`; figure exports; source-data maps; captions; final manuscript. |

## Minimal author reply format

Use this structure when sending author decisions back into the repository:

```text
repository DOI or anonymous reviewer link: provided_pending_external_browser_test_and_backfill / https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/
code licence: unresolved / value and scope
generated-data and checkpoint/model-weight rights: unresolved / value by artifact family
full Bishan Tool2 route: unresolved / public DOI or controlled-access route
GPKG-root geospatial route: unresolved / public DOI or controlled-access route
Dongxing/Neijiang prepared-data route: unresolved / public DOI or controlled-access route
reviewer data access: unresolved / route per restricted dataset
citation policy: unresolved / public-source, preprint, and Paper9 route
statistical reporting policy: unresolved / descriptive-only or predefined tests
Main Figure 1 / journal export rules: unresolved / final artwork and export rules
```

## Claim locks

Do not use this form as submission approval.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not claim a universal fixed switch margin.
