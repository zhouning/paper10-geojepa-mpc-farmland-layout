# Paper10 E0 archive release and DOI backfill checklist

Date: 2026-06-09

This checklist turns the current Paper10 E0 archive plan, metadata templates,
manifest, and source-data map into a release sequence. It does not assign
DOIs, repository identifiers, licences, data owners, access committees,
embargoes, reviewer links, or journal decisions. Replace each bracketed field
only after the archive or access body has issued it.

## Purpose and scope

Use this file after selecting the target venue and archive route. It covers:

- releasing the code and packaged E0 evidence archive;
- deciding public versus controlled access for the full Bishan `tool2/` data;
- deciding public versus controlled access for the prepared GPKG-root
  geospatial inputs;
- backfilling repository identifiers into the manuscript-facing Data and Code
  Availability statement and archive metadata;
- rerunning final checks from the exact submission commit.

Use `e0_data_access_and_rights_decision_register_2026-06-09.md` before this
release sequence to centralize code licence, generated-output rights, optional
GeoFM rights, full Tool2 access, GPKG-root access, and reviewer-route
decisions.

The current paper-facing positive claim remains bounded to the monitor-gated
`frontier_random050` 20x16/h5 top-5 value-head result. Tested 50-state
`frontier_random050` rows remain failed diagnostics and must not be promoted
to positive scale-up evidence.

## Preconditions before release

| item | required state before release | current action |
|---|---|---|
| Target venue | Journal or venue family selected, including anonymity and data-policy requirements. | Fill `[TARGET VENUE TO BE SELECTED]`. |
| Public manuscript route | Self-contained integrated manuscript variant selected unless a public Paper9 citation becomes available. | Use `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`. |
| Archive route | GitHub release plus Zenodo, Figshare, OSF, institutional repository, or another durable record selected. | Fill `[ARCHIVE PLATFORM TO BE SELECTED]`. |
| Archive manifest | `e0_archive_manifest_2026-06-09.csv` frozen or updated for any venue-driven membership change. | Confirm no unintended restricted files are included. |
| Source-data map | `e0_source_data_map_2026-06-09.md` frozen to final figure/table numbering. | Update after final figure selection. |
| Licences and rights | Code licence, generated-data terms, optional GeoFM rights, and full-data rights decided. | Fill licence and rights placeholders. |
| Full Tool2 route | Public deposit or controlled-access route selected for `tool2/transitions.npz` and `tool2/pairwise.npz`. | Fill `[FULL TOOL2 DOI TO BE ADDED]` or controlled-access record. |
| GPKG-root route | Public deposit or controlled-access route selected for GPKG-root geospatial inputs. | Fill `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` if not public. |

## Record 1 release: code and packaged E0 evidence

1. Confirm the submission commit contains the final manuscript-facing files,
   archive manifest, source-data map, metadata templates, tests, checkpoints,
   figure CSV source data, and reproducibility instructions.
2. Run the reviewer smoke test suite from that commit. The reviewer-facing
   command order, expected smoke outputs, and failure interpretation are in
   `e0_reviewer_smoke_replication_protocol_2026-06-09.md`.
   The latest tracked local execution log is
   `e0_reviewer_smoke_verification_log_2026-06-10.md`.

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

3. Create the repository release tag:

```text
[RELEASE TAG TO BE SELECTED]
```

4. Create the durable archive record for the exact submission commit:

```text
[ARCHIVE PLATFORM TO BE SELECTED]
[PUBLIC DOI OR REVIEWER LINK TO BE ADDED]
[SUBMISSION COMMIT HASH]
```

5. Upload or connect the archive to the GitHub release according to the
   selected repository workflow.
6. Confirm the archive landing page has title, creators, description, version,
   licence or rights terms, file list, related identifiers, and the exact Git
   commit.
7. Test any private reviewer link outside the author account before submission.
8. Do not use a temporary cloud folder, personal website, or unpublished drive
   link as the final identifier.

## Records 2 and 3 release: full data routes

| record | files or data family | route decision | identifier field | minimum metadata |
|---|---|---|---|---|
| Record 2 | Full Bishan `tool2/transitions.npz` and `tool2/pairwise.npz` | Public data repository if rights allow; otherwise controlled-access record. | `[FULL TOOL2 DOI TO BE ADDED]` or `[FULL TOOL2 CONTROLLED-ACCESS RECORD TO BE ADDED]` | title, creators or data owners, file list, size, provenance, licence or restriction reason, reviewer route, preferred citation |
| Record 3 | Prepared GPKG-root geospatial inputs, `results_real/blocks/`, and `townships.json` | Public only if redistribution rights allow; otherwise controlled access with public metadata. | `[GPKG-ROOT DOI TO BE ADDED]` or `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` | title, owners, GPKG-root placement, provenance, legal/governance restriction reason, request route, eligibility, data-use agreement |

If a data family cannot be openly redistributed, the final statement must name
the responsible owner or access body, request route, eligibility conditions,
review process, expected response terms if known, and data-use agreement. Do
not write only "available upon request" or "available upon reasonable request".

## Backfill matrix

| placeholder or field | update location | required value |
|---|---|---|
| `[REPOSITORY/DOI TO BE ADDED]` | `e0_data_code_availability_draft_2026-06-09.md`; final manuscript Data and Code Availability | Record 1 DOI or stable repository identifier. |
| `[PUBLIC DOI OR REVIEWER LINK TO BE ADDED]` | `e0_archive_metadata_templates_2026-06-09.md`; final submission cover/materials if needed | Public DOI or repository-supported anonymous reviewer link. |
| `[SUBMISSION COMMIT HASH]` | `e0_archive_metadata_templates_2026-06-09.md`; release notes; archive landing page | Exact Git commit used for submission. |
| `[CODE LICENCE TO BE SELECTED]` | Archive landing page; `e0_archive_metadata_templates_2026-06-09.md`; root repository metadata if added | Final software licence. |
| `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]` | Archive landing page; Data Availability; metadata templates | Rights terms for generated E0 outputs and included smoke data. |
| `[FULL TOOL2 DOI TO BE ADDED]` | Data Availability; archive templates; source-data or supplementary metadata if full reruns are promised | Public DOI for full `tool2/` data, or replace with controlled-access wording. |
| `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` | Data Availability; Record 3 metadata; final manuscript if GPKG-root data are restricted | Named access body, request URL/email/form, eligibility, review criteria, and data-use terms. |
| Optional GeoFM rights field | `e0_archive_manifest_2026-06-09.csv`; archive metadata | Confirm redistribution terms or remove/replace the asset before release. |
| Final figure/table numbering | `e0_source_data_map_2026-06-09.md`; figure plan; table draft; integrated manuscript | Frozen figure/table numbers and source-data mapping. |

## Final verification sequence

Run these checks after all backfilled identifiers and metadata fields are
committed locally, and before creating or updating the public archive:

1. `git diff --check`
2. Run the bundled preflight checker:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/preflight_submission_checks.py
```

3. Parse `e0_archive_manifest_2026-06-09.csv` with a CSV parser and confirm all
   rows have `record_id`, `path_or_pattern`, `access_route`, `archive_action`,
   and `status`.
4. Confirm Record 1 include/include-after-rights-check paths resolve inside the
   repository, while excluded/local full-data and cache patterns are not tracked
   by Git except for documented route README placeholders.
5. Confirm every citation key used by the public manuscript, citation map, and
   citation checklist exists in the verified or local BibTeX files.
6. Confirm the public self-contained manuscript body does not cite
   `@zhou2026paper9_local`.
7. Grep for prohibited passing-50-state wording and keep only guardrail or
   failed-diagnostic uses.
8. Run the full Paper10 test suite:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

8. If possible, clone the archive candidate into a clean directory and rerun
   `e0_reviewer_smoke_replication_protocol_2026-06-09.md` from the archived
   release or reviewer link.
   Record the exact result in a new verification log if the archived candidate
   commit differs from `534e0f8115a55d5c080bf21bb888657ccd9dd585`.
9. Record the final submission commit, test result, DOI or reviewer link, and
   any remaining restricted-data route in the submission files.

## No-go warnings

- Do not claim a full data deposit until the full Tool2 and GPKG-root records
  or controlled-access routes exist.
- Do not use temporary cloud links as final data identifiers.
- Do not use "available upon request" without a restriction reason and a
  concrete access process.
- Do not cite Paper9 as public unless a public Paper9 source exists.
- Do not describe the failed 50-state diagnostics as a passing 50-state result,
  positive scale-up evidence, or general 50-state scalability.
- Do not change archive membership after DOI assignment without creating a new
  version or documenting the repository version policy.
