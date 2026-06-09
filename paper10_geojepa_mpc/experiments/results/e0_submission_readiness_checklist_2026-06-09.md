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
| Results synthesis | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_synthesis_2026-06-09.md` | Source-grounded E0 result summary and boundary framing. |
| Cited Introduction draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_introduction_cited_draft_2026-06-09.md` | Literature-framed opening with verified citation keys. |
| Methods draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_methods_draft_2026-06-09.md` | Reproducible method wording for label generation, monitor gates, training, and rollouts. |
| Cited Results/Discussion draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md` | Paper-facing result interpretation without moving external references into local evidence claims. |
| Tables draft | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` | Manuscript table contracts and quantitative source mapping. |
| Figure plan | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_figure_plan_2026-06-09.md` | Figure contracts, caption drafts, source data, and figure-specific risk notes. |
| Data and Code Availability draft | `paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md` | Manuscript availability wording and archive/data DOI action list. |
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
| Paper9 provenance is local-only. | Reviewers cannot verify the task/reward source, and the bibliography would cite an unpublished local file. | Replace `zhou2026paper9_local` with a public Paper9 preprint/article, or merge the self-contained Bishan task/environment note plus reward-definition note into Paper10 Methods/supplement. |
| Target journal is not selected. | Citation style, word limits, abstract structure, figure limits, and data-policy wording remain unsettled. | Choose the target journal and convert the integrated draft to its format. |
| LeWorldModel citation policy is unresolved. | A 2026 arXiv preprint could be over-weighted as established prior art. | Decide whether the journal permits LeWM as a cited design comparison; otherwise cite peer-reviewed JEPA/world-model sources and keep LeWM as an internal related-work note. |
| Repository and data archive identifiers are missing. | Data and Code Availability cannot be finalized. | Archive the exact submission commit and assign repository/data DOI or reviewer-access links. |
| Full Bishan data route is undecided. | Full reruns may be impossible for reviewers even though smoke verification works. | Decide public deposit versus controlled access for full `tool2/` and GPKG-root geospatial inputs, including licence or restriction terms. |
| Figure/table numbering is not final. | Cross-references and source-data mapping may drift during formatting. | Select final figures/tables, freeze numbering, then update captions and the integrated draft. |
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
| Paper9 citation risk. | `zhou2026paper9_local` is local-only and unpublished; a code-derived self-contained replacement note now exists but has not been merged into final Methods. | high | Resolve before submission by choosing public Paper9 citation or self-contained Paper10 Methods; do not leave the local placeholder in the final bibliography. |
| Reference-policy risk. | Verified references exist, but target-journal style and LeWM policy are unresolved. | medium | Freeze target journal, reference style, and preprint policy before final manuscript conversion. |

## Action order for the next session

1. Resolve the Paper9 provenance path: public citation, supplementary methods,
   or self-contained Paper10 Methods using
   `e0_bishan_task_environment_self_contained_methods_2026-06-09.md` plus
   `e0_reward_and_rollout_metric_definitions_2026-06-09.md`.
2. Select the target journal and format constraints.
3. Decide repository/data archiving route and full Bishan data access route.
4. Freeze the final figure/table set and update numbering across the integrated
   manuscript, table draft, figure plan, and source-data notes.
5. Convert the integrated manuscript draft into the target journal format.
6. Run a final claim sweep for prohibited 50-state scale-up language and
   unresolved citation placeholders.
7. Run tests and repository verification from a clean checkout or reviewer-like
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

- Public citation or self-contained Paper10 Methods replacement for
  `zhou2026paper9_local` is in place.
- Target journal, article format, word limits, and reference style are selected.
- Repository DOI or anonymous reviewer link is recorded.
- Full Bishan `tool2/` and GPKG-root geospatial data route is documented with
  licence or restriction terms.
- Figure/table numbering and source-data mapping are frozen.
- All manuscript citation keys resolve in the final bibliography.
- A final prohibited-claim sweep finds no 50-state success or unverified Paper9
  public-citation claims.
- Reviewer smoke tests pass on the archived submission commit.
