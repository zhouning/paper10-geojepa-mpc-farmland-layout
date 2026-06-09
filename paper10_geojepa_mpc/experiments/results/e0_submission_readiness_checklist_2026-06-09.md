# E0 submission readiness checklist

Date: 2026-06-09

This checklist converts the current Paper10 E0 manuscript, citation, figure,
data, and reproducibility assets into a submission-readiness tracker. It does
not add new experimental evidence. Its purpose is to keep the next Paper10
steps ordered by reviewer risk and to prevent unsupported claims from entering
the manuscript.

## One-sentence argument

In constrained Bishan farmland swap planning, Paper10 shows that
monitor-gated `frontier_random050` value labels improve GeoJEPA-MPC rollout
reward and seed stability at the reproducible 20x16/top5 scale, supported by
five-seed rollout summaries, monitor diagnostics, and a GPKG-root reproduction
audit, with the boundary that tested 50-state labels failed the monitor gate and
should be treated as negative diagnostics rather than successful scale-up.

## Terminology ledger

| canonical term | first-use definition | decision |
|---|---|---|
| Paper10 | The current GeoJEPA-MPC farmland layout planning manuscript and reproducibility package. | Use as the manuscript/package name. |
| GeoJEPA-MPC | The packaged rank-checkpoint planner and finite-horizon candidate-selection workflow. | Do not claim a newly trained transition model in E0. |
| `frontier_random050` | Candidate-label strategy mixing model-scored frontier actions with random exploratory actions at frontier fraction 0.5. | Use exact code token for experiment identifiers. |
| monitor gate | Candidate-quality rule using candidate regret, candidate overlap, one-step regret, and minimum state count before value-head training. | Failed label sets are diagnostics, not training inputs. |
| 10x12/top4 | Pilot label scale with 10 states, 12 candidates, and top-4 training gate. | Use as the direct pilot baseline. |
| 20x16/top5 | Main positive E0 label scale with 20 states, 16 candidates, and top-5 training gate. | Use as the current paper-facing result. |
| 50-state diagnostics | macOS seed45 and Windows seed46 `frontier_random050` 50-state rows. | Use only as negative boundary evidence. |
| GPKG root | Full-data root resolving `DLTB_with_slope.gpkg` for reproducible 20x16 label generation. | Treat as part of the experimental condition. |
| `zhou2026paper9_local` | Local-only unpublished Paper9 placeholder for Bishan task/reward provenance. | Replace or formalize before submission. |

## Completed submission assets

| asset | path | readiness use |
|---|---|---|
| Integrated manuscript draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_integrated_manuscript_draft_2026-06-09.md` | Current single-entry working manuscript with abstract, Introduction, Methods, Results, Discussion, conclusion, claim-evidence map, and blockers. |
| Self-contained integrated manuscript variant | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md` | Public-submission-oriented manuscript route that does not cite `zhou2026paper9_local` in the manuscript body. |
| Results synthesis | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_synthesis_2026-06-09.md` | Source-grounded E0 result summary and boundary framing. |
| Cited Introduction draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_introduction_cited_draft_2026-06-09.md` | Literature-framed opening with verified citation keys. |
| Methods draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_methods_draft_2026-06-09.md` | Reproducible method wording for label generation, monitor gates, training, and rollouts. |
| Cited Results/Discussion draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md` | Paper-facing result interpretation without moving external references into local evidence claims. |
| Tables draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` | Manuscript table contracts and quantitative source mapping. |
| Figure plan | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_figure_plan_2026-06-09.md` | Figure contracts, caption drafts, source data, and figure-specific risk notes. |
| Data and Code Availability draft | `paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md` | Manuscript availability wording and archive/data DOI action list. |
| Submission route and archive plan | `paper10_geojepa_mpc/experiments/results/e0_submission_route_and_archive_plan_2026-06-09.md` | Route matrix for generic, Nature-family, and methods/reproducibility venues plus archive record and restricted-data decisions. |
| Archive metadata templates | `paper10_geojepa_mpc/experiments/results/e0_archive_metadata_templates_2026-06-09.md` | Fill-in repository metadata, controlled-access wording, source-data mapping, and dataset README templates for final archive records. |
| Machine-readable archive manifest | `paper10_geojepa_mpc/experiments/results/e0_archive_manifest_2026-06-09.csv` | CSV file-family checklist separating public archive contents, external full-data records, and excluded local/generated artifacts. |
| Source-data map | `paper10_geojepa_mpc/experiments/results/e0_source_data_map_2026-06-09.md` | Figure, table, and claim-to-source mapping for archive source-data metadata. |
| Data access and rights decision register | `paper10_geojepa_mpc/experiments/results/e0_data_access_and_rights_decision_register_2026-06-09.md` | Central register for code licence, generated-output rights, optional GeoFM rights, full Tool2 access, GPKG-root geospatial access, reviewer routes, and availability backfill fields. |
| Archive release and DOI backfill checklist | `paper10_geojepa_mpc/experiments/results/e0_archive_release_and_doi_backfill_checklist_2026-06-09.md` | Ordered release, DOI/reviewer-link capture, full-data route, backfill, and final verification checklist. |
| Target-venue and manuscript-conversion checklist | `paper10_geojepa_mpc/experiments/results/e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md` | Section-by-section conversion plan for turning the self-contained integrated draft into a journal-specific submission package after venue, reference, figure, DOI, and data-access decisions are fixed. |
| Self-contained manuscript gap audit | `paper10_geojepa_mpc/experiments/results/e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md` | Reviewer-risk ledger separating blocking submission gaps from risks that can be handled by bounded framing and final conversion. |
| Self-contained Bishan task/environment Methods note | `paper10_geojepa_mpc/experiments/results/e0_bishan_task_environment_self_contained_methods_2026-06-09.md` | Code-derived task, state, action, reward, episode, and data-root wording that can be merged into Paper10 Methods if public Paper9 citation is unavailable. |
| Reward and metric definitions | `paper10_geojepa_mpc/experiments/results/e0_reward_and_rollout_metric_definitions_2026-06-09.md` | Source-grounded reward, executable-mask, label-return, and rollout metric definitions. |
| Citation and claim checklist | `paper10_geojepa_mpc/experiments/results/e0_citation_and_claim_checklist_2026-06-09.md` | Claim-to-evidence and citation-needs tracker. |
| Verified bibliography | `references/paper10_verified_references_2026-06-09.bib` | Publicly verified first-pass bibliography. |
| Local-source bibliography | `references/paper10_local_sources_2026-06-09.bib` | Internal-only Paper9 placeholder bibliography; not submission-ready as a public source. |
| Citation map | `references/paper10_citation_map_2026-06-09.md` | Claim-to-citation policy and verification status. |
| Paper9 local-source note | `references/paper10_paper9_local_source_status_2026-06-09.md` | Documents why `zhou2026paper9_local` remains a blocker. |

## Submission blockers

| blocker | risk if unresolved | required action |
|---|---|---|
| Paper9 provenance is local-only in the older integrated draft. | Reviewers cannot verify a bibliography entry that cites an unpublished local file. | Use the self-contained integrated manuscript variant for public submission unless a public Paper9 citation becomes available. |
| Target journal is not selected. | Citation style, word limits, abstract structure, figure limits, and data-policy wording remain unsettled. | Choose the target journal and convert the integrated draft to its format. |
| Target-journal manuscript conversion is not planned. | Final formatting may drift from the bounded E0 claim, source-data map, or self-contained Paper9 replacement route. | Use `e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md` before creating the final journal-specific manuscript file. |
| Self-contained manuscript gap audit is not closed. | A final manuscript could carry unresolved archive, data-access, figure-numbering, or reference-policy blockers into submission. | Use `e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md` as the final blocker ledger before creating the journal-specific manuscript file. |
| LeWorldModel citation policy is unresolved. | A 2026 arXiv preprint could be over-weighted as established prior art. | Decide whether the journal permits LeWM as a cited design comparison; otherwise cite peer-reviewed JEPA/world-model sources and keep LeWM as an internal related-work note. |
| Repository and data archive identifiers are missing. | Data and Code Availability cannot be finalized. | Archive the exact submission commit and assign repository/data DOI or reviewer-access links. |
| Submission and archive route is not selected. | Archive metadata, anonymity, DOI timing, and source-data requirements may drift by venue. | Use `e0_submission_route_and_archive_plan_2026-06-09.md` to choose the generic, Nature-family, or methods/reproducibility route before final formatting. |
| Archive metadata fields are not finalized. | Repository records may be inconsistent with the manuscript statement or missing required DataCite fields. | Fill `e0_archive_metadata_templates_2026-06-09.md` after selecting the repository, licence, creators, identifiers, and access route. |
| DOI and reviewer-link backfill has not been executed. | Manuscript, archive metadata, and repository records may cite different identifiers or omit the exact submission commit. | Use `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md` after archive release and before final submission. |
| Machine-readable archive manifest is not frozen. | Repository uploads may omit required file families or accidentally include external/restricted data. | Freeze `e0_archive_manifest_2026-06-09.csv` after route, licence, and data-access decisions. |
| Full Bishan data route is undecided. | Full reruns may be impossible for reviewers even though smoke verification works. | Decide public deposit versus controlled access for full `tool2/` and GPKG-root geospatial inputs, including licence or restriction terms. |
| Data-access and rights decisions are not centralized. | Final Data Availability, archive metadata, source-data mapping, and reviewer-route wording may diverge. | Use `e0_data_access_and_rights_decision_register_2026-06-09.md` as the single decision register before DOI and licence backfill. |
| Figure/table numbering is not final. | Cross-references and source-data mapping may drift during formatting. | Select final figures/tables, freeze numbering, then update captions and the integrated draft. |
| Source-data map is not frozen to final numbering. | Archive metadata may drift from final figure/table labels. | Update `e0_source_data_map_2026-06-09.md` after final figure/table numbering and before archive release. |
| China-specific farmland policy literature has not been separately checked. | The Introduction may miss region-specific motivation if the target journal expects policy context. | Run a focused literature pass only if the target venue or framing needs it. |

## Reviewer-risk matrix

| risk | current evidence status | severity | mitigation before submission |
|---|---|---:|---|
| Contribution may look incremental. | The current positive claim is bounded to monitor-gated label selection improving GeoJEPA-MPC at 20x16/top5. | high | Make the contribution explicit as a label-quality-gated value-filtering workflow plus negative 50-state boundary diagnostics; avoid broad scale-up language. |
| Evaluation may look too small. | Main evidence uses five rollout seeds and a 20-state/16-candidate label set; 50-state rows are negative diagnostics. | high | Present the limitation openly; add new experiments only after a pre-declared 50-state gate passes. |
| Baseline completeness may be questioned. | Direct comparison is 10x12/top4 pilot and prior matched `frontier_independent` branch, not a broad external planner benchmark. | medium | Label current results as E0 evidence and avoid claiming superiority over all planning methods. |
| 50-state overclaim risk. | All tested 50-state label sets failed gates before training. | high | Keep all 50-state wording as boundary diagnostics; do not say the method scales to 50 states. |
| GPKG/shapefile reproducibility risk. | macOS audit showed the GPKG root reproduces packaged 20x16 labels, while shapefile-first resolution does not. | medium | State the GPKG root as an experimental condition in Methods and Data Availability. |
| Data/code availability risk. | Smoke data, outputs, and checkpoints are included; full data and DOI route remain external. | high | Add repository/data DOI or controlled-access route before submission. |
| Paper9 citation risk. | The self-contained integrated manuscript variant now removes `zhou2026paper9_local` from the manuscript body, but final submission formatting and bibliography cleanup are still pending. | medium | Use the self-contained variant as the public draft path; keep the local placeholder only in internal source-status documents unless a public Paper9 citation becomes available. |
| Reference-policy risk. | Verified references exist, but target-journal style and LeWM policy are unresolved. | medium | Freeze target journal, reference style, and preprint policy before final manuscript conversion. |

## Action order for the next session

1. Use the self-contained integrated manuscript variant as the working public
   submission draft, unless a public Paper9 citation becomes available.
2. Select the target journal or venue family.
3. Choose the submission/archive route in
   `e0_submission_route_and_archive_plan_2026-06-09.md`.
4. Decide repository/data archiving route and full Bishan data access route.
5. Use `e0_data_access_and_rights_decision_register_2026-06-09.md` to centralize
   code licence, generated-output rights, optional GeoFM rights, full Tool2
   access, GPKG-root access, and reviewer-route decisions.
6. Fill the selected metadata fields in
   `e0_archive_metadata_templates_2026-06-09.md`.
7. Use `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md` to define
   release tag, submission commit, DOI/reviewer-link, and backfill fields.
8. Freeze the machine-readable archive manifest.
9. Freeze the final figure/table set and update numbering across the integrated
   manuscript, table draft, figure plan, and source-data map.
10. Use `e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md` to
   convert the integrated manuscript draft into the target journal format.
11. Use `e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md` to
    close the remaining blocker ledger before final manuscript creation.
12. Run a final claim sweep for prohibited 50-state scale-up language and
   unresolved citation placeholders.
13. Run tests and repository verification from a clean checkout or reviewer-like
   environment before archive release.

## Claim-evidence guardrails

| manuscript claim | status |
|---|---|
| 20x16/top5 mean total reward is `69.4705` and sample standard deviation is `1.0004`. | Supported by packaged rollout summaries. |
| 20x16/top5 improves over 10x12/top4 by `4.2139` or `6.46%`. | Supported by packaged rollout summaries and tables draft. |
| GPKG root reproduces the packaged 20x16 labels. | Supported by macOS GPKG reproduction findings. |
| Tested 50-state `frontier_random050` labels failed monitor gates. | Supported by macOS and Windows diagnostic findings. |
| Tested 50-state labels support value-head training. | Not supported; do not claim. |
| Paper10 generally scales to 50 states. | Not supported; do not claim. |
| Paper9 task/reward provenance is publicly citable. | Not yet supported; resolve `zhou2026paper9_local`. |

## Ready-to-submit gate

Paper10 E0 is not ready for journal submission until all items below are true:

- Public draft path uses the self-contained integrated manuscript variant and
  does not cite `zhou2026paper9_local` in the manuscript body.
- Target journal, article format, word limits, and reference style are selected.
- Target-venue manuscript conversion has been completed from the self-contained
  integrated draft without changing the E0 claim boundary.
- Self-contained manuscript gap audit blockers are either closed or explicitly
  carried as venue-approved limitations.
- Submission/archive route is selected and documented.
- Archive metadata fields are completed for the selected route.
- Repository DOI or anonymous reviewer link is recorded.
- Repository DOI or anonymous reviewer link is backfilled consistently across
  Data Availability, archive metadata, and release notes.
- Full Bishan `tool2/` and GPKG-root geospatial data route is documented with
  licence or restriction terms.
- Code licence, generated-output rights, optional GeoFM rights, full-data
  access routes, and reviewer routes are centralized in the data-access and
  rights decision register.
- Figure/table numbering and source-data mapping are frozen.
- All manuscript citation keys resolve in the final bibliography.
- A final prohibited-claim sweep finds no 50-state success or unverified Paper9
  public-citation claims.
- Reviewer smoke tests pass on the archived submission commit.
