# Paper10 E0 data access and rights decision register

Date: 2026-06-20

This register lists the data, code, model, and derived-output rights decisions
that must be made before the Paper10 E0 manuscript can be submitted. It does
not assign licences, data owners, access committees, repository identifiers,
embargoes, reviewer links, or publication decisions. Its purpose is to keep
the manuscript Data and Code Availability statement, archive metadata, source
data map, and final submission files aligned.

The current no-go blocker packet for coordinating these decisions before
manuscript conversion is
`e0_submission_blocker_decision_packet_2026-06-11.md`.

## Scope

Use this register before filling:

- `[CODE LICENCE TO BE SELECTED]`
- `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]`
- `[REPOSITORY/DOI TO BE ADDED]`
- `[FULL TOOL2 DOI TO BE ADDED]`
- `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]`
- `[DONGXING/NEIJIANG DATA DOI TO BE ADDED]`
- `[DONGXING/NEIJIANG CONTROLLED-ACCESS RECORD TO BE ADDED]`
- `[PUBLIC DOI OR REVIEWER LINK TO BE ADDED]`
- `e0_submission_blocker_decision_packet_2026-06-11.md`

The current positive E0 claim remains limited to the Bishan 20x16/top5 result.
The 2026-06-20 Stage 3 50x24 candidate-score sweep did not change any
data-access route. The tested 50-state rows remain failed diagnostics and do
not change any data-access route.

## Author closeout update (2026-07-08)

The current author-provided boundary is recorded in
`e0_paper10_author_decision_closeout_form_2026-07-08.md` and should override
older ambiguous route options in this register:

- `public_code_allowed_pending_named_software_licence`: code can be public, but
  the named software licence and repository metadata scope remain pending.
- non-DLTB artifacts can be public, but generated-output/model-weight rights
  terms and any needed DLTB-leakage check remain pending.
- Original Bishan and Dongxing DLTB inputs are restricted and must not be
  publicly redistributed.
- `restricted_sensitive_original_bishan_dltb_controlled_access_required`: the
  GPKG-root route for original Bishan DLTB inputs requires controlled access or
  an institution/data-owner route if reviewer inspection is required.
- `split_route_original_dongxing_dltb_restricted_derived_non_dltb_public_pending_leakage_check_and_controlled_route`:
  Dongxing/Neijiang derived non-DLTB artifacts may be public after leakage
  checks, while original Dongxing DLTB inputs remain restricted.

## Author rights update (2026-07-09)

This update supersedes the pending licence fields above for code and generated
non-DLTB artifacts:

- Code licence: Apache-2.0, recorded in `LICENSE`, scoped only to licensable
  code and scripts.
- Generated-output and checkpoint/model-weight rights: CC0-1.0 for generated
  non-DLTB JSON, Markdown, CSV, NPZ outputs, source-data tables, checkpoints,
  and model-weight artifacts.
- Original Bishan and Dongxing DLTB inputs: confidential_no_external_access;
  they cannot be publicly redistributed and cannot be shared externally through
  public download, private reviewer link, controlled-access credentials, or
  informal request.
- DLTB-leakage check evidence remains required before any new public deposit of
  derived Tool2 or Dongxing/Neijiang non-DLTB artifacts.

## Decision register

| item | current package status | supports | candidate access route | required author decision | unresolved fields |
|---|---|---|---|---|---|
| Paper10 source code, tests, scripts, and notebooks | Included in Git. | Reviewer smoke verification, value-label generation, rollout evaluation, plotting, and manuscript reproducibility. | Public code/evidence archive with DOI or private reviewer link during review. | Apache-2.0 selected for licensable code and scripts; still select archive platform, release tag, and exact submission commit. | `LICENSE`; `[REPOSITORY/DOI TO BE ADDED]`; `[PUBLIC DOI OR REVIEWER LINK TO BE ADDED]`; `[SUBMISSION COMMIT HASH]` |
| Small reviewer smoke Tool2 data | Included in Git under `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`. | Automated tests and smoke-scale verification. | Included with Record 1 if rights allow. | Confirm the smoke data can be redistributed with the repository archive and state any data rights terms. | `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]` |
| Generated E0 JSON, Markdown, CSV, and NPZ outputs | Included in Git under `paper10_geojepa_mpc/experiments/results/`. | Main Bishan 20x16/top5 result, Stage 3 boundary evidence, source-data mapping, and failed 50-state diagnostics. | Public code/evidence archive with Record 1. | CC0-1.0 selected for generated non-DLTB outputs; still confirm no restricted raw geospatial data are embedded beyond permitted derived outputs. | `CC0-1.0`; `[REPOSITORY/DOI TO BE ADDED]` |
| E0 checkpoints | Included in Git under `paper10_geojepa_mpc/experiments/checkpoints/`. | Reproducing packaged rollouts and value-filter evaluation. | Public code/evidence archive with Record 1. | CC0-1.0 selected for checkpoint/model-weight artifacts; Apache-2.0 remains scoped to code and scripts only. | `CC0-1.0`; `LICENSE` |
| Optional GeoFM asset | Included in Git under `paper7/data/`. | Optional fusion tests and ablations. | Include only if redistribution terms are confirmed; otherwise remove, replace, or document as external. | Confirm source, owner, licence, and whether it can remain in a public archive. | Optional GeoFM rights field in archive manifest; `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]` |
| Full Bishan Tool2 data | External to Git; expected as `tool2/transitions.npz` and `tool2/pairwise.npz`. | Full-scale training and real-environment rollout reruns. | Public dataset DOI if redistribution rights exist; otherwise controlled-access repository or institutional access route. | Identify owner, repository or access body, public-versus-controlled route, reviewer access, eligibility, review criteria, and data-use terms. | `[FULL TOOL2 DOI TO BE ADDED]`; `[FULL TOOL2 CONTROLLED-ACCESS RECORD TO BE ADDED]`; `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` |
| Prepared GPKG-root geospatial inputs | External to Git; expected as `dem_slope_analysis/output/DLTB_with_slope.gpkg`, `results_real/blocks/`, and `townships.json`. | Reproducible 20x16 label generation and full real-environment rollouts. | confidential_no_external_access for original Bishan DLTB inputs. | Disclose that original Bishan DLTB cannot be provided externally; do not create public or reviewer raw-DLTB links. | confidential raw-data limitation; `[GPKG-ROOT DOI TO BE ADDED]` only for permitted non-DLTB derived artifacts if deposited |
| Dongxing/Neijiang derived summaries and source-data CSVs | Included in Git under `paper10_geojepa_mpc/experiments/results/` as Markdown and CSV result summaries, including `e0_dongxing_return_label_family_summary_2026-06-10.csv`, `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`, and `e0_source_data_map_with_dongxing_2026-06-11.md`. | Integrated manuscript tables, Figure 4 return-label scaling, Figure 5 low-label transfer stress test, and reviewer claim audit. | Public code/evidence archive with Record 1. | Select generated-output rights terms and confirm no restricted raw geospatial data are embedded beyond permitted aggregate or derived outputs. | `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]`; `[REPOSITORY/DOI TO BE ADDED]` |
| Dongxing/Neijiang prepared data and environment files | External to Git; audited in `e0_dongxing_local_data_cross_region_audit_2026-06-10.md`; includes prepared 3711-block products, 76,376 parcel assignments, `trajectories_6k_neijiang.npz`, `pairwise_data_neijiang.npz`, slope-enriched geospatial inputs, and environment wrapper files. | Full external-region training and rollout reruns, action-space adaptation, return-label scaling, and low-label transfer stress testing. | Public dataset DOI if redistribution rights exist; otherwise controlled-access repository or institutional access route with public metadata. | Identify Dongxing/Neijiang data owner, restriction reason, repository or access body, reviewer access route, eligible requesters, review criteria, response expectation, and data-use or no-redistribution terms. | `[DONGXING/NEIJIANG DATA DOI TO BE ADDED]`; `[DONGXING/NEIJIANG CONTROLLED-ACCESS RECORD TO BE ADDED]`; `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` |
| Generated figure previews and rerun outputs | Ignored under `reviewer_outputs/` unless intentionally exported. | Local visual checks and rerun previews. | Excluded by default; include only selected final exports with source-data mapping. | Decide final figure exports and whether any generated files become submitted source data. | Final figure/table numbering and source-data map fields |
| Paper9 local manuscript source | Not a public data record; local-only status note exists. | Internal task/reward provenance during drafting only. | Do not use as public data, code, or citation route. | Replace with self-contained Paper10 Methods route unless a public Paper9 source is created and verified. | Public Paper9 citation decision |

## Required access wording fields for restricted data

If full Tool2, GPKG-root geospatial data, or Dongxing/Neijiang prepared data
are not public, the final manuscript must name:

- restriction reason;
- responsible owner or access body;
- request route;
- eligible requesters;
- review criteria;
- data-use agreement or no-redistribution terms;
- reviewer access route;
- expected response time if known.

Do not use only "available upon request" or "available upon reasonable request"
without these details.

## Minimum archive rights decisions

| decision | acceptable close-out | not acceptable |
|---|---|---|
| Code licence | A named software licence recorded in the repository and archive metadata. | Leaving `[CODE LICENCE TO BE SELECTED]` in manuscript or archive files. |
| Generated-output rights | A named data licence or rights statement for E0 outputs, smoke data, CSV source data, NPZ labels, and checkpoints if applicable. | Applying an open licence to third-party or restricted geospatial data without rights. |
| Full Tool2 route | Public DOI or controlled-access record with public metadata and reviewer route. | Temporary cloud folder or informal private transfer as the final route. |
| GPKG-root route | Public DOI or controlled-access metadata record with concrete request process. | Omitting the GPKG-root condition from Data Availability. |
| Dongxing/Neijiang route | Public DOI or controlled-access metadata record with concrete request process and reviewer route. | Citing only local paths or derived CSVs as if they allow full external-region reruns. |
| Optional GeoFM asset | Confirmed redistribution terms or removal/replacement before final archive. | Assuming it can be redistributed because it is small. |

## Backfill order

1. Decide code licence and generated-data rights terms.
2. Confirm optional GeoFM redistribution status.
3. Select Record 1 archive platform and create DOI or reviewer link.
4. Decide full Tool2 public deposit versus controlled access.
5. Decide GPKG-root geospatial public deposit versus controlled access.
6. Decide Dongxing/Neijiang prepared-data public deposit versus controlled
   access.
7. Fill Record 2, Record 3, and Dongxing/Neijiang metadata templates or
   restricted-access fields.
8. Backfill Data and Code Availability, archive metadata, source-data map, and
   final manuscript files.
9. Re-run archive manifest, citation, prohibited-claim, and smoke-test checks
   from the exact submission commit.
