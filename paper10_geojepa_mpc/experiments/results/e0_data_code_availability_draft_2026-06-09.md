# Paper10 E0 Data and Code Availability draft

Date: 2026-06-20

This document prepares a manuscript-ready Data and Code Availability statement
for the current Paper10 formal manuscript package. It is a draft for journal
submission and must be updated with repository DOIs, anonymous reviewer links,
licences, and any institutional access route selected before submission. The
current evidence boundary is the validated Bishan 20x16/top5 anchor plus the
2026-06-20 Stage 3 50x24 candidate-score sweep, which did not change the data-
access requirements.

Target journal: not fixed. This draft follows a generic Nature-style structure
without assuming final journal-specific wording.

Route planning note:
`paper10_geojepa_mpc/experiments/results/e0_submission_route_and_archive_plan_2026-06-09.md`
tracks the generic, Nature-family, and methods/reproducibility submission
routes and the archive records that must be assigned before this statement is
finalized. Fill-in archive metadata and controlled-access wording templates
are tracked in
`paper10_geojepa_mpc/experiments/results/e0_archive_metadata_templates_2026-06-09.md`.
The machine-readable archive manifest is tracked in
`paper10_geojepa_mpc/experiments/results/e0_archive_manifest_2026-06-09.csv`.
The current figure, table, and claim-to-source-data mapping is tracked in
`paper10_geojepa_mpc/experiments/results/e0_source_data_map_2026-06-09.md`.
The integrated Dongxing/Neijiang figure and source-data mapping is tracked in
`paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md`.
The data-access and rights decision register is tracked in
`paper10_geojepa_mpc/experiments/results/e0_data_access_and_rights_decision_register_2026-06-09.md`.
The archive release and DOI or reviewer-link backfill checklist is tracked in
`paper10_geojepa_mpc/experiments/results/e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`.
The current no-go submission blocker decision packet is tracked in
`paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md`.

## Dataset inventory and access routes

| dataset or artifact family | supports | current location | access route | submission status |
|---|---|---|---|---|
| Small reviewer smoke Tool2 data (`transitions.npz`, `pairwise.npz`, sample log and summary) | Tests and smoke-scale verification | `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/` | public code repository after archive/release | included in Git; needs repository DOI or release URL before submission |
| Optional GeoFM asset | Optional fusion-code paths and tests | `paper7/data/block_geofm_embeddings.npy`; `paper7/data/geofm_metadata.json` | public code repository after archive/release | included in Git; licence/metadata should be checked before submission |
| Paper10 E0 generated value labels | Monitor gates, value-head training, figure/table source evidence | `paper10_geojepa_mpc/experiments/results/*.npz`; JSON/Markdown monitor outputs | public code/data repository after archive/release | included in Git; record should describe each file family |
| Paper10 E0 checkpoints | Reproducing packaged value-head rollouts | `paper10_geojepa_mpc/experiments/checkpoints/` | public code/data repository after archive/release | included in Git; record should include model/checkpoint metadata |
| Paper10 E0 rollout summaries and manuscript source data | Reported 20x16/top5 anchor metrics, 50-state boundary diagnostics, and figure source data | `paper10_geojepa_mpc/experiments/results/`; figure-ready CSV files | public code/data repository after archive/release | included in Git; source-data mapping is already documented in figure/table drafts |
| Dongxing/Neijiang generated summaries and figure source data | Cross-region calibration tables, Figure 4 return-label scaling, and Figure 5 low-label transfer stress test | `paper10_geojepa_mpc/experiments/results/e0_dongxing_*_2026-06-10.*`; `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv` | public code/data repository after archive/release | included in Git as derived source data; needs repository DOI or release URL before submission |
| Generated figure previews | Draft visual checks | ignored `reviewer_outputs/` | not part of submitted source data unless selected | generated locally; do not cite unless exported and deposited |
| Full Bishan Tool2 data (`tool2/transitions.npz`, `tool2/pairwise.npz`) | Full-scale training and rollout reproduction | external to Git; placement documented in `DATA_AVAILABILITY.md` and `REPRODUCIBILITY.md` | public repository or controlled/justified request, depending on authors' rights | not yet deposited; needs DOI/access route before submission |
| Full prepared Bishan geospatial inputs, including GPKG root | Real-environment rollouts and reproducible 20x16 label generation | external to Git; expected files documented in `DATA_AVAILABILITY.md`; GPKG root required for packaged 20x16 reproduction | likely restricted or controlled/justified request if raw cadastral data cannot be redistributed | access condition must be decided before submission |
| Dongxing/Neijiang prepared environment, transitions, pairwise labels, and geospatial inputs | External-region real-environment rollouts, 3711-block action-space adaptation, return-label scaling, and low-label stress tests | external to Git; audited in `e0_dongxing_local_data_cross_region_audit_2026-06-10.md`; includes prepared block products, `trajectories_6k_neijiang.npz`, `pairwise_data_neijiang.npz`, and slope-enriched geospatial inputs | public deposit if redistribution rights exist; otherwise controlled-access record with public metadata and reviewer route | not yet deposited; needs Dongxing/Neijiang data DOI or controlled-access route before submission |
| Paper9 local manuscript source | Task/reward provenance during internal drafting | local `D:/test/paper9_v6.tex`; status note in `references/paper10_paper9_local_source_status_2026-06-09.md` | not a dataset; local-only manuscript source | replace or formalize before submission |

## Draft Data Availability

The data supporting the packaged E0 analyses are provided in the archived
Paper10 repository and associated data record [REPOSITORY/DOI TO BE ADDED].
The record contains the small reviewer smoke dataset, generated E0 value-label
files, monitor outputs, rollout summaries, figure-ready CSV source data,
manuscript table source notes, saved checkpoints, and metadata needed to
inspect the reported Bishan 20x16/top5 anchor and the 2026-06-20 Stage 3
50x24 candidate-score sweep. The figure source data used for the current E0
draft figures are the tracked CSV files
`paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv`
and
`paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv`.
For the integrated Dongxing/Neijiang figures, the tracked source-data files are
`paper10_geojepa_mpc/experiments/results/e0_dongxing_return_label_family_summary_2026-06-10.csv`
and
`paper10_geojepa_mpc/experiments/results/e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`.
These files summarize derived model-evaluation outputs and do not by
themselves provide the prepared Dongxing/Neijiang data needed for full reruns.

The full Bishan Tool2 transition and pairwise datasets are not stored directly
in the Git repository because the binary files are approximately 1.65 GB in
total. These files are required to rerun full-scale training and real
environment rollouts from scratch. Before submission, the authors should
either deposit the full `tool2/` directory in a durable research-data
repository with a DOI [FULL TOOL2 DOI TO BE ADDED], or provide a controlled
institutional access route if redistribution is restricted.

Full real-environment rollouts and label generation also require prepared
Bishan geospatial inputs, including the parcel/block data and a data root that
resolves `dem_slope_analysis/output/DLTB_with_slope.gpkg`. The packaged 20x16
label set reproduced on the GPKG data root, whereas a root resolving shapefile
inputs first generated materially different labels. The GPKG root convention is
therefore part of the reproducibility condition for the reported 20x16/top5
result. The 2026-06-20 50x24 candidate-score sweep does not change this route.
If raw cadastral or prepared geospatial files cannot be redistributed because
of governance, licensing, or third-party restrictions, the final statement
should name the responsible data owner or institutional access route, the
eligibility conditions for qualified researchers, and any data-use agreement
required for access [RESTRICTED-DATA ACCESS ROUTE TO BE ADDED].

The Dongxing/Neijiang external-region evidence depends on prepared
cross-region data and environment files outside the Git repository, including
3711-block prepared features, 76,376 parcel assignments, transition
trajectories, pairwise candidate labels, block products, and slope-enriched
geospatial inputs. The tracked repository contains derived Dongxing summaries,
tables, and figure source data, but full Dongxing/Neijiang training and
rollout reproduction requires a separate data record. Before submission, the
authors should either deposit the prepared Dongxing/Neijiang data in a durable
repository with a DOI [DONGXING/NEIJIANG DATA DOI TO BE ADDED], or provide a
controlled-access metadata record that names the responsible data owner,
request route, eligibility criteria, review process, reviewer access route,
and data-use or no-redistribution terms [DONGXING/NEIJIANG CONTROLLED-ACCESS RECORD TO BE ADDED].

The repository also includes a small smoke dataset under
`arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`. This smoke data is
sufficient for automated tests and smoke-scale verification, but it is not a
substitute for the full Bishan data needed to rerun the full E0 rollouts. The
optional GeoFM embedding asset used by optional fusion tests is included under
`paper7/data/`.

## Draft Code Availability

All custom code used for the packaged Paper10 E0 analyses is included in the
Paper10 repository [REPOSITORY/DOI TO BE ADDED]. The repository contains the
GeoJEPA-MPC model code, Paper9 compatibility adapter, environment-mask logic,
value-label generation scripts, monitor-gate scripts, value-head training
entry points, rollout evaluation scripts, plotting scripts for draft E0
figures, tests, saved checkpoints, and reproducibility documentation. The main
verification command is:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

The full command recipes for smoke verification, packaged 20x16/top5 reruns,
Windows 50-state diagnostic ablations, the 2026-06-20 50x24 candidate-score
sweep, and macOS 50x24/h5 diagnostic reproduction are documented in
`REPRODUCIBILITY.md`. Generated preview figures and rerun outputs are written
under ignored `reviewer_outputs/` by default.

## Repository and citation actions

- Archive the GitHub repository as a versioned release in Zenodo, Figshare,
  OSF, an institutional repository, or another durable repository that provides
  a DOI.
- Use the route matrix in
  `e0_submission_route_and_archive_plan_2026-06-09.md` to decide whether the
  submission needs a public DOI before initial submission, an anonymous
  reviewer link, or a controlled-access data record.
- If journal policy requires full data access during review, deposit the full
  `tool2/` directory, prepared GPKG-root geospatial inputs, and
  Dongxing/Neijiang prepared data before submission, or provide an anonymous
  controlled-access reviewer route.
- Add a dataset README or repository landing-page description that maps each
  file family to the manuscript results it supports.
- Fill the archive record and dataset README fields in
  `e0_archive_metadata_templates_2026-06-09.md` after selecting the repository
  and access route.
- Use `e0_archive_manifest_2026-06-09.csv` to verify which file families belong
  in the public code/evidence archive, which require external records, and
  which stay excluded.
- Use `e0_source_data_map_2026-06-09.md` as the current source-data map for
  Bishan-focused archive metadata and
  `e0_source_data_map_with_dongxing_2026-06-11.md` for integrated
  Dongxing/Neijiang source-data mapping, then update them after final
  figure/table numbering is frozen.
- Use `e0_data_access_and_rights_decision_register_2026-06-09.md` to close
  code licence, generated-data rights, optional GeoFM rights, full Tool2 access,
  and GPKG-root access decisions before final wording.
- Use `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md` after
  archive release to backfill the repository DOI, reviewer link, submission
  commit hash, licences, and full-data access route consistently.
- Use `e0_submission_blocker_decision_packet_2026-06-11.md` before manuscript
  conversion to confirm the target venue, DOI/reviewer-link route, licences,
  data access routes, citation policy, and statistics policy are still
  unresolved or have been explicitly closed.
- Add licence metadata for the code and for any shareable data. Do not apply an
  open licence to third-party or restricted cadastral/geospatial data unless
  the authors have redistribution rights.
- Add dataset citations in the final reference list when repository DOIs are
  assigned.

## FAIR and metadata audit

| item | current status | action before submission |
|---|---|---|
| Persistent identifier | GitHub remote exists, but no archive DOI is recorded in the manuscript assets. | Create a versioned repository/data archive and record the DOI. |
| Route selection | A route matrix now exists, but no target journal or archive route has been selected. | Choose the generic, Nature-family, or methods/reproducibility route and align archive timing with that route. |
| Archive metadata | Fill-in metadata templates exist, but creator, licence, identifier, related-identifier, and controlled-access fields are not finalized. | Complete `e0_archive_metadata_templates_2026-06-09.md` after venue and repository choices. |
| Machine-readable archive manifest | A file-family archive manifest is tracked, but final repository identifiers and licences are not assigned. | Update `e0_archive_manifest_2026-06-09.csv` if archive membership changes after venue or licence decisions. |
| File manifest | `MANIFEST.md`, `DATA_AVAILABILITY.md`, and `REPRODUCIBILITY.md` describe included and external assets. | Align final archive file list with these documents. |
| Figure source data | Figure-ready CSV files are tracked for seed-wise rewards and top-k diagnostics. | Confirm final figure numbers and include source-data mapping in the archive metadata. |
| Dongxing/Neijiang source data | Derived Dongxing summary CSVs are tracked for return-label scaling and low-label transfer stress-test figures. | Deposit or control-access the prepared Dongxing/Neijiang data needed for full reruns; include the derived CSVs in the code/evidence archive. |
| Source-data map | Claim, figure, and table source-data maps are tracked for Bishan and integrated Dongxing routes, but final journal numbering is not frozen. | Update `e0_source_data_map_2026-06-09.md` and `e0_source_data_map_with_dongxing_2026-06-11.md` after final figure/table selection. |
| Full raw/processed data route | Full Tool2 and prepared geospatial data are external to Git. | Decide public deposit versus controlled/justified access. |
| Restricted-data rationale | Raw cadastral/geospatial restriction is inferred from Paper9 local-source notes and repository policy, but the responsible access body is not named. | Add the data owner, responsible institution, request route, eligibility, and data-use conditions. |
| Licence | Repository/data licence is not fixed in this statement. | Add code licence and data licence or restriction terms. |
| Versioning | Current manuscript-facing assets are dated 2026-06-20 and tied to commit history, while older 2026-06-09 result files remain as historical records. | Archive the exact submission commit and cite that version. |

## Missing information / risk flags

- No repository DOI, dataset DOI, or anonymous reviewer link is recorded yet.
- Target journal and archive route are not selected yet; availability wording
  may need adjustment after venue choice.
- Full Bishan Tool2 files and prepared GPKG-root geospatial inputs are external
  to Git; the final access route must be selected before submission.
- Dongxing/Neijiang prepared data are external to Git; the final public deposit
  or controlled-access route must be selected before submission.
- If the prepared cadastral/geospatial data are restricted, the final statement
  must name the responsible owner or institutional access route rather than
  saying only "available on request."
- The final licence terms for code, generated data, checkpoints, and any
  shareable geospatial derivatives are not fixed.
- The Paper9 local manuscript source is not a data repository or public
  reference and must not be used as the final availability route.

## Chinese author notes

- 这份文件是投稿用 Data and Code Availability 草稿，不是最终声明。
- 投稿前必须补 GitHub/Zenodo 等归档 DOI，或者至少提供审稿人可访问的私有链接。
- full Bishan `tool2/` 和 GPKG-root geospatial inputs 现在还不在 Git 里；如果不能公开分发，需要写清楚数据所有方、申请路径、审核条件和 data-use agreement。
- 不要只写 "available upon reasonable request"；必须说明限制原因和可执行的访问流程。
