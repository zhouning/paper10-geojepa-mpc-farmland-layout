# Paper10 author-decision closeout form

Date: 2026-07-08

Status: author_input_partially_provided

Status note: source-derived; no rollout or training rerun; no submission approval.

This closeout form converts the post-guard submission blocker state into an author-facing intake sheet. It does not make unprovided author decisions, does not create repository identifiers, and does not replace institutional data-rights approval.

## Source basis

- `e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json`
- `e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_paper10_author_decision_matrix_2026-06-18.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`

## Submission state

Formal submission remains blocked. The repository anonymous reviewer link has been provided, and the author has clarified the data/code publication boundary: code can be public, non-DLTB artifacts can be public, original Bishan DLTB data must not be public, and original Dongxing DLTB data must not be public. The remaining blockers are the named licence/rights terms, DLTB controlled-access route, non-author browser-session test for the 4open link, leakage checks before any derived-data deposit, and final manuscript/archive backfill. Passing repository preflight means the blocker surface is tracked and guarded; it does not mean the paper has approval for formal submission.

## Use rule

Author-provided closeout must fill the fields below before final manuscript backfill. Do not use temporary cloud folders, personal drive links, local paths, or "available upon request" wording as durable access routes. Do not apply open data terms to restricted geospatial inputs unless the authors hold those rights. Original Bishan and Dongxing DLTB inputs are restricted and must not be publicly redistributed.

## Author input recorded

- repository DOI or anonymous reviewer link: provided_pending_external_browser_test_and_backfill
- anonymous reviewer link: https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/
- code can be public: yes, pending named software licence and repository metadata scope.
- non-DLTB artifacts can be public: yes, pending named generated-data/model-weight rights terms and DLTB-leakage checks where relevant.
- original Bishan DLTB data must not be public: confirmed restricted/sensitive.
- original Dongxing DLTB data must not be public: confirmed restricted/sensitive.
- command-line access check: `curl.exe -L --max-time 20 -I` reached the 4open route, observed a redirect to `/api/repo/geojepa-mpc-farmland-layout-8552/file/`, and then received `401 Unauthorized` from the unauthenticated API follow-up.
- interpretation: the 4open route exists, but reviewer-facing browser access still requires an independent non-author browser-session test before formal submission.
- remaining closeout: record the exact submission commit represented by the 4open snapshot; select named code/data/model rights terms; define controlled access for restricted DLTB inputs if journal review requires it; backfill Data and Code Availability, `MANIFEST.md`, the archive manifest, and final manuscript wording.

## Author-decision closeout table

| field | status | recommended default | author must provide | not acceptable | files to update after closeout |
|---|---|---|---|---|---|
| repository DOI or anonymous reviewer link | provided_pending_external_browser_test_and_backfill | Anonymous 4open reviewer link provided: `https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/`. | Non-author browser-session test; exact submission commit represented by the 4open snapshot; version date; access window; final Data/Code Availability and archive-manifest backfill. | Treating command-line `401 Unauthorized` API follow-up as reviewer-browser verification; marking this field fully closed before backfill. | `DATA_AVAILABILITY.md`; `MANIFEST.md`; `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_manifest_2026-06-09.csv`; final manuscript. |
| code licence | public_code_allowed_pending_named_software_licence | Public code release is allowed; select a named software licence for licensable code and scripts before final archive metadata. | Licence name or institution-approved code-use statement; scope limited to licensable code and scripts; repository metadata location. | Implicit open-source wording; licence that also claims restricted third-party data or original DLTB inputs. | `LICENCE` or `LICENSE` file if selected; `MANIFEST.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; archive metadata. |
| generated-data and checkpoint/model-weight rights | public_release_allowed_except_sensitive_original_dltb_pending_named_rights_terms | Public release is allowed for generated non-DLTB outputs, source tables, checkpoints, and model weights after selecting named rights terms and confirming no restricted original DLTB content is embedded. | Named rights terms for JSON, Markdown, CSV, NPZ outputs, source-data tables, checkpoints, and model weights; DLTB exclusion boundary. | Single broad data licence that relicenses raw geospatial inputs; missing checkpoint or model-weight terms; public release of original DLTB. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_archive_metadata_templates_2026-06-09.md`; archive metadata. |
| full Bishan Tool2 route | derived_tool2_public_release_allowed_pending_dltb_leakage_check_and_deposit | Treat full Bishan Tool2 transition and pairwise files as shareable derived artifacts only after a DLTB-leakage check; keep original Bishan DLTB geospatial inputs restricted. | No further author rights decision for derived Tool2; still record leakage-check evidence, archive identifier, checksums, and reviewer route. | Local path only; informal request-only wording without eligibility or review process; treating Tool2 as permission to publish original Bishan DLTB. | `DATA_AVAILABILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; final manuscript. |
| GPKG-root geospatial route | restricted_sensitive_original_bishan_dltb_controlled_access_required | Do not publicly redistribute original Bishan DLTB/GPKG-root geospatial inputs; use controlled-access or institution/data-owner routing with public metadata if journal review requires access. | Responsible owner or access body; restriction reason; eligible requesters; review criteria; reviewer route if required; data-use/no-redistribution terms. | Claiming full reruns are reproducible from Git alone; omitting GPKG-root dependencies from Data Availability; public release of original Bishan DLTB. | `DATA_AVAILABILITY.md`; `REPRODUCIBILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; final manuscript. |
| Dongxing/Neijiang prepared-data route | split_route_original_dongxing_dltb_restricted_derived_non_dltb_public_pending_leakage_check_and_controlled_route | Publicly release Dongxing/Neijiang derived non-DLTB summaries and source data, but keep original Dongxing DLTB inputs restricted and define controlled access if full rerun inputs are required. | Split public derived artifacts from restricted original-DLTB inputs; leakage-check evidence; controlled-access owner/body and reviewer route if required. | Derived summary CSVs as a substitute for full rerun inputs; local paths only; public release of original Dongxing DLTB. | `e0_data_code_availability_draft_2026-06-09.md`; `e0_data_access_and_rights_decision_register_2026-06-09.md`; `e0_source_data_map_with_dongxing_2026-06-11.md`; final manuscript. |
| reviewer data access | partially_closed_public_code_and_derived_artifacts_pending_restricted_dltb_reviewer_route_and_browser_test | Use the 4open reviewer link for public code and derived non-DLTB artifacts after independent browser testing; route restricted original DLTB access only through an approved controlled process. | Which restricted DLTB datasets reviewers can inspect if required; controlled route or editor-mediated procedure; non-author browser test outside the author account. | Author-only local paths; untested private links; post-acceptance-only deposit promise; public reviewer link containing original DLTB. | `DATA_AVAILABILITY.md`; `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`; reviewer instructions; final manuscript. |
| citation policy | unresolved | Use verified public sources in manuscript text and keep local-only Paper9 material out unless it becomes public and citable. | Acceptable source types; preprint policy; local-only source replacement route; final reference style. | Local-only citation key in public manuscript; unverified reference placeholders. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; `references/paper10_citation_map_2026-06-09.md`; bibliography files; final manuscript. |
| statistical reporting policy | unresolved | Keep descriptive reporting unless the authors define tests, comparison groups, multiplicity handling, and precision before editing inferential claims. | Comparison groups; seed/checkpoint counts; test choice if any; multiplicity handling if any; precision policy. | Inferential superiority wording without committed analysis plan; post-hoc test language added only in prose. | `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`; Results section; table captions; final manuscript. |
| Main Figure 1 / journal export rules | unresolved | Preserve the current figure/table numbering freeze and adapt exports only after target journal rules are known. | Main Figure 1 final artwork status; figure and table limits; PDF/SVG/raster requirements; source-data file names; supplementary placement rules. | Changing numbering without source-data and caption updates; submitting local preview files as final source data without mapping. | `e0_paper10_final_figure_table_export_package_2026-06-20.md`; figure exports; source-data maps; captions; final manuscript. |

## Minimal author reply format

Use this structure when sending author decisions back into the repository:

```text
repository DOI or anonymous reviewer link: provided_pending_external_browser_test_and_backfill / https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/
code licence: public_code_allowed_pending_named_software_licence / named licence still required
generated-data and checkpoint/model-weight rights: public_release_allowed_except_sensitive_original_dltb_pending_named_rights_terms / named rights terms still required
full Bishan Tool2 route: derived_tool2_public_release_allowed_pending_dltb_leakage_check_and_deposit / derived Tool2 public only after leakage check
GPKG-root geospatial route: restricted_sensitive_original_bishan_dltb_controlled_access_required / owner or access body still required if reviewer access is needed
Dongxing/Neijiang prepared-data route: split_route_original_dongxing_dltb_restricted_derived_non_dltb_public_pending_leakage_check_and_controlled_route / derived public, original DLTB restricted
reviewer data access: partially_closed_public_code_and_derived_artifacts_pending_restricted_dltb_reviewer_route_and_browser_test / route per restricted DLTB dataset if required
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
