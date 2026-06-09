# Paper10 E0 submission route and archive plan

Date: 2026-06-09

This note converts the current Paper10 E0 manuscript and reproducibility
package into a route-specific submission and archiving plan. It does not add
new experimental evidence, repository identifiers, licences, access committees,
or journal decisions. It defines what must be decided before submission and
which archive record each decision should produce.

Fill-in archive metadata templates are provided in
`e0_archive_metadata_templates_2026-06-09.md`.
The release and identifier backfill sequence is tracked in
`e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`.

## Current defensible submission route

The public manuscript route should use
`paper10_geojepa_mpc/experiments/results/e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`
as the working draft unless a public Paper9 citation becomes available. This
route keeps Bishan task, reward, environment, and data-root details inside the
Paper10 Methods package rather than depending on the local-only
`zhou2026paper9_local` placeholder.

The paper-facing claim remains bounded to the monitor-gated
`frontier_random050` 20x16/h5 top-5 value-head result:

- five-seed mean total reward: `69.4705`
- sample standard deviation: `1.0004`
- direct 10x12/top4 baseline mean total reward: `65.2566`
- mean-reward improvement: `4.2139`, or `6.46%`

The tested 50-state `frontier_random050` runs are negative diagnostics only.
They must not be described as successful scale-up evidence.

## Route matrix

| route | likely use | required manuscript changes | required archive/access actions | unresolved decisions |
|---|---|---|---|---|
| Generic computational or urban/planning journal | Fastest route for the current E0 evidence package. | Convert the self-contained integrated draft to the journal structure; keep E0 framing explicit; include Data and Code Availability. | Archive the exact GitHub submission commit; provide full `tool2/` and GPKG-root data DOI or controlled-access route; include source-data mapping. | Target journal, reference style, repository choice, licences, full-data owner/access route. |
| Nature-family or Springer Nature route | Higher data-policy and source-data burden. | Use Nature-style abstract/Methods structure; add source-data mapping for each figure panel; ensure Data and Code Availability has stable identifiers before submission. | Provide DOI or anonymous reviewer links for code, generated E0 artifacts, and any public data; define restricted-data access body and eligibility if geospatial data cannot be public. | Whether current E0 scope is strong enough; whether full data can be deposited or must be controlled; final code/data licences. |
| Methods or reproducibility-focused venue | Best fit if contribution is framed as a guarded workflow and evidence package. | Emphasize monitor-gated value-label generation, negative 50-state diagnostics, and reviewer-runnable package. | Archive code/checkpoints/results as the primary record; provide smoke data in Git; provide a separate full-data route for reruns beyond smoke verification. | Venue expectations for benchmark breadth, full-data access, and software licence. |

## Archive record plan

| record | contents | identifier needed | access route | notes |
|---|---|---|---|---|
| Code and packaged E0 evidence archive | GitHub release at the exact submission commit, source code, tests, small smoke data, generated E0 labels, checkpoints, JSON/Markdown summaries, figure CSV source data, and reproducibility docs. | Repository DOI or durable release identifier. | Public repository archive unless journal anonymity requires a private reviewer link first. | Preferred first archive record because most paper-facing E0 evidence is already in Git. |
| Full Bishan Tool2 data record | `tool2/transitions.npz` and `tool2/pairwise.npz`. | Dataset DOI or controlled-access record identifier. | Public data repository if redistribution rights exist; otherwise controlled institutional route. | Needed for full training and rollout reproduction; not needed for smoke tests. |
| Prepared GPKG-root geospatial data record | Prepared parcel/block inputs, `DLTB_with_slope.gpkg` root convention, `results_real/blocks/`, and `townships.json` as permitted. | Dataset DOI, accession, or controlled-access record. | Public only if rights allow; otherwise restricted access with public metadata. | Required because the GPKG root reproduced packaged 20x16 labels while shapefile-first resolution did not. |
| Figure source-data mapping | Final figure CSVs, panel-to-file mapping, table source notes, and captions. | Same identifier as code/evidence archive or a separate source-data record. | Public if derived outputs are shareable. | Update after final figure/table numbering is frozen. |
| Restricted-data metadata record | Public metadata for any cadastral/geospatial data that cannot be redistributed. | Repository landing page or institutional access page. | Controlled or justified request route with named owner/process. | Do not use a vague "available upon request" statement. |

## Access decision table

| item | can be public now? | submission handling |
|---|---:|---|
| Paper10 source code, tests, scripts, smoke Tool2 data, generated E0 outputs, checkpoints, and manuscript source notes | likely yes, subject to licence choice | Archive as the submission commit and cite the release/DOI. |
| Optional GeoFM asset under `paper7/data/` | needs rights/licence confirmation | Keep in the code archive only if redistribution terms are confirmed; otherwise document replacement or removal. |
| Full Bishan `tool2/` binary data | unknown | Decide public deposit versus controlled access before submission. |
| Prepared cadastral/geospatial GPKG-root inputs | unknown and potentially restricted | If not public, name the responsible data owner, request procedure, eligibility, and data-use agreement. |
| Generated figure CSVs and E0 JSON/Markdown summaries | likely yes | Include as source data in the code/evidence archive. |
| Paper9 local manuscript source | no | Do not cite as a public source; keep only in internal source-status notes unless formalized. |

## Minimum repository metadata

Before submission, the code/evidence archive should include:

- title matching the final manuscript title or a close package title;
- creators and affiliations;
- repository/version date and exact Git commit;
- short description of the E0 `frontier_random050` evidence package;
- file-family manifest matching `MANIFEST.md`;
- licence for code and separate licence or access terms for data;
- related identifiers for any full-data record, preprint, or final article;
- source-data mapping for final figures and tables;
- tested verification command and expected test result;
- note that 50-state rows are failed diagnostics, not scale-up evidence.

## Action order

1. Select the target journal or venue family.
2. Decide whether to archive through GitHub release plus Zenodo, Figshare, OSF,
   an institutional repository, or another durable record.
3. Select code licence and data licence or restriction terms.
4. Decide whether full Bishan `tool2/` data and prepared GPKG-root geospatial
   inputs can be public.
5. If any full data are restricted, name the owner, access body, eligibility
   rules, request route, response expectation, and data-use agreement.
6. Freeze final figure/table numbering and source-data mapping.
7. Fill the selected archive metadata fields in
   `e0_archive_metadata_templates_2026-06-09.md`.
8. Use `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md` to
   release the exact submission commit, capture identifiers, and backfill
   manuscript availability fields.
9. Archive the exact submission commit and record the DOI or reviewer link in
   `e0_data_code_availability_draft_2026-06-09.md`.
10. Re-run the citation, claim, and test verification checks from a clean
   checkout before final submission.

## Submission warning

Do not write only "data are available upon reasonable request" for the full
Bishan Tool2 or GPKG-root geospatial inputs. If the data are not public, the
final statement must state the restriction reason, data owner, request route,
eligibility conditions, review process, and data-use conditions.
