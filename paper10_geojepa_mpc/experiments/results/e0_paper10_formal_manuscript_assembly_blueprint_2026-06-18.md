# Paper10 formal manuscript assembly blueprint

Date: 2026-06-18

Status: formal-manuscript assembly blueprint. This file converts the current
Paper10 CEUS Stage 3 manuscript draft into an author-facing assembly plan for a
formal manuscript package. It is not a final manuscript, not a journal-specific
submission file, and not evidence that the paper is ready for submission.

Source basis:

- `e0_ceus_stage3_manuscript_draft_2026-06-18.md`
- `e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- `e0_paper10_author_decision_matrix_2026-06-18.md`
- `e0_paper10_project_proposal_opening_report_2026-06-18.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`

## one-sentence argument

In constrained farmland layout planning, Paper10 supports a bounded claim that
monitor-gated value labels can improve and stabilize GeoJEPA-MPC rollouts at the
validated Bishan 20x16/top5 anchor, supported by five-seed matched-baseline
evidence, while Stage 3 50-state rollouts and Dongxing/Neijiang results define
the scale, transfer and deployment boundaries that must remain explicit in the
formal manuscript.

## Terminology ledger

| canonical term | first-use definition | manuscript rule |
|---|---|---|
| GeoJEPA-MPC | Geospatial JEPA and model-predictive planning workflow for constrained farmland layout planning. | Use as the method name; do not rebrand it in later sections. |
| monitor-gated value labels | Finite-horizon return labels accepted only after monitor checks. | Use as the central contribution; state that gates control escalation before value-head training. |
| value filter | Scalar value head used to filter candidate actions before rollout scoring. | Report label scale, top-k, horizon, rollout seeds and comparator when making a performance claim. |
| matched Paper9 `rank_seed2028` | Current Stage 3 comparator used under the same horizon, top-k, mask and seed protocol. | Use only under the self-contained Paper10 Methods route unless the author freezes a separate public Paper9 route. |
| diagnostic near-pass | Stage 1 near-pass row rolled out for diagnostic context. | The `67.4913` row must not be pooled with confirmatory rows. |
| Dongxing/Neijiang prepared data | External-region package with 3711 blocks and 76,376 parcel assignments. | Use as calibration and stress-test evidence, not as transfer-superiority proof. |
| block-level planning-unit abstraction | Implemented action abstraction in which actions select blocks rather than arbitrary parcel geometries. | State as a deployment boundary in Methods and Discussion. |
| soft training and hard inference | Reward and count penalties guide labels, while executable masks enforce rollout feasibility. | Do not describe the current implementation as a Constrained MDP/CPO/RCPO solver. |

## Section assembly plan

The formal manuscript should be assembled evidence-first. The current CEUS Stage
3 draft already contains all major sections, but final conversion should reorder
editing effort around the Results evidence rather than polishing the opening
first.

1. Results: lock Bishan, Stage 3 and Dongxing claims to exact source artifacts.
2. Methods: make the self-contained Paper10 Methods route reproducible without
   a public Paper9 citation.
3. Discussion: interpret why the workflow is useful despite failed 50-state
   confirmatory rows.
4. Data and Code Availability: backfill repository DOI or reviewer link,
   licence, full Bishan Tool2, GPKG-root and Dongxing/Neijiang prepared data
   routes.
5. Title and abstract: compress only after the claim boundary and data routes
   are frozen.

## Evidence-first drafting order

The next manuscript editing pass should use this order:

1. Convert the Results section into claim-first subsections with one evidence
   table or figure reference per claim.
2. Convert Methods into a reproducibility route that names inputs, outputs,
   masks, seeds, top-k, horizons, candidate-value weights and blocked
   dependencies.
3. Rebuild Discussion around the central interpretation: monitor gates are an
   evidence-control mechanism, not a broad scale-up guarantee.
4. Backfill Data and Code Availability only after author decisions close.
5. Finalize title, abstract, highlights and keywords last.

## Title and abstract

Current defensible title route:

`Monitor-gated value labels bound GeoJEPA-MPC farmland layout planning`

The abstract should keep the same movement as the CEUS Stage 3 draft:

1. constrained farmland layout planning creates long-horizon value uncertainty;
2. monitor-gated value labels provide a quality-control step;
3. Bishan 20x16/top5 provides the positive anchor;
4. Stage 3 50-state rows bound the scale claim;
5. Dongxing/Neijiang supports calibration and stress testing;
6. submission implications are reproducibility and claim control, not broad
   operational deployment.

Numbers allowed in the abstract are `69.4705`, `67.5437`, `64.2960`,
`66.2544` and `67.4913`. The abstract may also report sample standard
deviation `1.0004` versus `7.2246` if the target journal accepts the added
detail.

## Introduction

The Introduction should use an application-first funnel:

1. farmland layout planning requires sequential geospatial decisions under
   slope, contiguity, area and administrative constraints;
2. immediate swap rewards do not fully determine long-horizon planning value;
3. MPC and predictive representation learning motivate candidate rollout and
   value estimation, but they do not by themselves solve evidence quality;
4. Paper10 introduces monitor-gated value labels as the quality-control step
   before value-filter training;
5. the evidence ladder is intentionally bounded: Bishan positive anchor, Stage
   3 boundary evidence, Dongxing/Neijiang calibration and stress test.

Do not open the Introduction with a broad promise about national-scale land-use
optimization. The paper is strongest when it names the concrete planning
workflow and the evidence-control gap early.

## Methods

Methods should remain self-contained until Paper9 has a public route. The
section must explain the task formulation, planning units, executable mask,
reward, value-label generation, monitor gates, value-filter training, rollout
protocol and external-region protocol without citing a local-only placeholder.

Required method locks:

- use the self-contained Paper10 Methods route;
- name the matched Paper9 `rank_seed2028` comparator as the current comparator;
- state that pairwise-only baseline policy remains unresolved;
- state that full Bishan Tool2, GPKG-root and Dongxing/Neijiang prepared data
  routes are still author-decision blockers;
- define the block-level planning-unit abstraction;
- state that irregular cadastral deployment needs area-tolerance matching,
  shared-perimeter-weighted contiguity and parcel geometry constraints;
- state that the implementation is soft training and hard inference, not a
  Constrained MDP/CPO/RCPO solver.

## Results

Results should be written as a ladder of four claims.

| result claim | evidence source | manuscript wording |
|---|---|---|
| Monitor gates selected the Bishan value-label anchor. | Monitor JSON/Markdown files and Stage 3 draft section 3.1. | Monitor checks authorized the 20x16/top5 label setting for manuscript-facing value-filter testing. |
| Bishan 20x16/top5 improved reward and stability. | Mean reward `69.4705` versus matched baseline `67.5437`; sample standard deviation `1.0004` versus `7.2246`. | The validated Bishan 20x16/top5 value filter improved reward and seed-level stability under the tested protocol. |
| Stage 3 50-state rows did not support broad scale-up. | Confirmatory rows `64.2960` and `66.2544`; diagnostic near-pass `67.4913`. | Stage 3 completed rollouts but did not support direct positive 50-state scale-up under the matched comparator; the near-pass row must not be pooled. |
| Dongxing/Neijiang supports calibration and stress testing. | Return-label family and low-label budget summaries. | Dongxing/Neijiang shows real-environment calibration value, while scratch strength prevents a robust transfer-superiority claim. |

Do not claim direct 50-state Bishan scale-up success. Do not claim robust Bishan-to-Dongxing transfer superiority.

## Discussion

Discussion should interpret the Stage 3 outcome as a useful boundary, not as a
failed paper. The central point is that monitor gates make it possible to reject
weak value-label settings before they become inflated manuscript claims.

The Discussion should address three rival explanations:

1. the Bishan anchor may reflect a condition-specific value-filter setting
   rather than a general scale-up rule;
2. the matched Paper9 comparator may remain acceptable for the current CEUS
   route, but the pairwise-only baseline policy is still unresolved;
3. Dongxing/Neijiang improvements may reflect local return-label calibration
   rather than reusable Bishan initialization.

The deployment boundary should be concrete. Current evidence uses blocks and
queen contiguity. Operational irregular-parcel deployment needs area-tolerance
matching, shared-perimeter-weighted contiguity, parcel geometry constraints and
a closed data-access route.

## Conclusion

The conclusion should be one paragraph, not a figure-by-figure recap. It should
state that Paper10 contributes a reproducible monitor-gated value-filtering
workflow for constrained geospatial planning. It should then name the strongest
evidence, the Stage 3 boundary, and the Dongxing/Neijiang calibration result.
The final sentence should keep the implication bounded to planning-support and
evidence-control use until comparator, data-access, licence and export
decisions are closed.

## Data and Code Availability

The formal manuscript cannot finalize Data and Code Availability until author
decisions close the repository DOI or reviewer link, code licence,
generated-output rights, full Bishan Tool2 route, GPKG-root route and
Dongxing/Neijiang prepared data route.

Current safe wording route:

- code and tracked derived evidence can be described through the repository
  commit and archive manifest;
- full Bishan Tool2 and GPKG-root reruns require controlled or public data
  access records;
- Dongxing/Neijiang full reruns require access to prepared blocks, parcel
  assignments, transitions, pairwise labels, environment wrappers and
  slope-enriched inputs;
- derived summary CSVs can support figure/source-data review but cannot be
  described as sufficient for full external-region reruns.

## Figure and table assembly map

| item | manuscript job | source-control dependency |
|---|---|---|
| Main Figure 1 | Explain monitor-gated value filtering workflow. | Workflow source map and Methods section. |
| Main Figure 2 | Show Bishan 20x16/top5 reward and stability. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`; rollout summaries. |
| Main Figure 3 | Show Stage 3 50-state boundary. | `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`; `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`. |
| Main Figure 4 | Show Dongxing return-label scaling. | `e0_dongxing_return_label_family_summary_2026-06-10.csv`; `e0_source_data_map_with_dongxing_2026-06-11.md`. |
| Supplementary Figure S1 | Show Dongxing low-label stress test. | `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`; `e0_source_data_map_with_dongxing_2026-06-11.md`. |
| Main Table 1 | Summarize monitor-selected Bishan gates. | Monitor JSON/Markdown files and table package. |
| Main Table 2 | Summarize matched-baseline rollout comparison. | Stage 3 rollout Markdown/JSON. |
| Main Table 3 | Summarize Dongxing return-label scaling. | Dongxing family summary CSV and integrated table package. |

The numbering must stay aligned with
`e0_integrated_figure_table_numbering_freeze_2026-06-11.md` unless the target
journal imposes a different limit and the source-data map is updated in the
same commit.

## Claim-evidence map

| claim | status | evidence or blocker |
|---|---|---|
| Monitor-gated value labels are useful at the validated Bishan anchor. | Supported. | Bishan 20x16/top5 mean reward `69.4705` versus `67.5437`; sample standard deviation `1.0004` versus `7.2246`. |
| Stage 3 supports direct positive 50-state scale-up. | Not supported. | Confirmatory rows `64.2960` and `66.2544` are below the matched baseline; diagnostic `67.4913` must not be pooled. |
| Dongxing/Neijiang proves transfer superiority. | Not supported. | Return-label scaling helps both transfer and scratch families; scratch remains stronger in key settings. |
| Irregular cadastral deployment is solved. | Not supported. | Current evidence is block-level and queen-contiguity based; deployment needs added parcel geometry constraints. |
| The paper is ready for final submission. | Not supported. | Author decisions remain open for comparator, repository DOI or reviewer link, licence, data access, citations, statistics and final exports. |

## Author-decision blockers

The following blockers must be closed before the formal manuscript can replace
this blueprint:

- target venue and article type;
- comparator and pairwise-only baseline policy;
- repository DOI or reviewer link;
- code licence and generated-output rights;
- full Bishan Tool2 data route;
- GPKG-root geospatial input route;
- Dongxing/Neijiang prepared data route;
- citation policy and Paper9 public-route handling;
- statistical reporting policy;
- final figure/table export package.

## Next manuscript-editing sequence

1. Freeze target venue and article type.
2. Decide whether matched Paper9 `rank_seed2028` remains the comparator or a
   separately named pairwise-only baseline must be added.
3. Backfill repository DOI or reviewer link, licence and data-access route.
4. Convert Results into final figure/table references.
5. Convert Methods into final reproducibility wording.
6. Revise Discussion and Conclusion for the final claim boundary.
7. Finalize title, abstract, highlights and keywords.
8. Run `D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py`.

Passing preflight with this blueprint means the manuscript assembly route is
explicit and claim-bounded. It does not mean the paper is ready for final
submission.
