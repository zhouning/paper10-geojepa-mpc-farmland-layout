# Paper10 integrated target venue and manuscript conversion checklist with Dongxing

Date: 2026-06-12

File:
`e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`

This checklist controls the next with-Dongxing manuscript-conversion pass. It
extends the Bishan-only checklist
`e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md` without
deleting it. It is not a final manuscript, does not select a target journal,
does not assign repository identifiers, and does not resolve licence or data
access decisions.

Use this file after the author team has reviewed
`e0_submission_blocker_decision_packet_2026-06-11.md` and before creating a
journal-specific manuscript file from the integrated scaffold.
For the current CEUS Research Article candidate route and reviewer-facing
revision controls, use
`e0_ceus_reviewer_improvement_packet_2026-06-12.md` together with this
checklist.

## Source basis

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_post_dongxing_submission_gap_audit_2026-06-10.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_ceus_reviewer_improvement_packet_2026-06-12.md`
- `references/paper10_citation_map_2026-06-09.md`

## One-sentence argument

In constrained farmland layout planning, Paper10 shows that monitor-gated
GeoJEPA-MPC value filtering improves Bishan real-environment planning at the
20x16/top5 label scale and can be calibrated in a Dongxing/Neijiang external
region, supported by Bishan five-seed rollout rewards, monitor diagnostics,
Dongxing return-label scaling, and low-label stress tests, with the boundary
that direct 50-state Bishan scale-up and robust Bishan-to-Dongxing transfer
superiority are not supported by the current evidence.

## Terminology ledger

| canonical term | first-use definition | manuscript conversion rule |
|---|---|---|
| GeoJEPA-MPC | The Paper10 geospatial JEPA and model-predictive planning workflow used for constrained farmland layout planning. | Use consistently as the method name; do not rename it during journal conversion. |
| monitor gate | A candidate-label quality check used before value-head training or manuscript-facing claim escalation. | Present it as a guardrail for value filtering, not as an after-the-fact explanation. |
| value labels | Finite-horizon return labels generated from candidate action sets for value-head training and evaluation. | Keep label scale, horizon, candidate count, and top-k gate explicit. |
| value filter | The rollout selector that uses the trained value head to filter candidate swaps. | Link claims to the 20x16/top5 Bishan evidence unless a later experiment changes the boundary. |
| Bishan E0 | The primary Paper10 Bishan evidence package with 10x12/top4 baseline, 20x16/top5 positive result, and failed 50-state diagnostics. | Treat as the primary positive result and the main reproducibility route. |
| Dongxing/Neijiang | The external-region real-environment package with 3711 blocks, 76,376 parcels, return-label scaling, and low-label stress tests. | Use as calibration and stress-test evidence, not as proof of robust transfer superiority. |
| return-label scaling | Dongxing experiments that compare pairwise-only, 20x16 return-label, and 50x16 return-label settings. | Use for Main Figure 4 and Main Table 3. |
| low-label stress test | Dongxing experiments comparing transfer and scratch families at 5, 10, and 20 value-label budgets. | Use for Supplementary Figure S1 and Supplementary Table S2 unless the target journal requires a different layout. |

## Venue decision grid

| venue route | fit with current evidence | conversion emphasis | unresolved blocker |
|---|---|---|---|
| Computational geography, urban analytics, or land-use planning journal | Strongest generic fit because the paper has real-environment planning evidence and a transparent data boundary. | Lead with constrained farmland planning, monitor-gated value filtering, Bishan 20x16/top5, and Dongxing calibration. | Target journal and article type; reference style; figure/table limits; repository DOI or reviewer link. |
| Methods or reproducibility-focused venue | Fits if the paper is framed as a guarded value-label workflow with reproducible smoke tests and explicit failure boundaries. | Emphasize workflow, monitor gates, source-data maps, reviewer smoke protocol, and failure-mode transparency. | Code licence; generated-data rights; full Bishan, GPKG-root, and Dongxing/Neijiang prepared data access route. |
| Nature-family or broad interdisciplinary route | Possible only after the authors accept a higher source-data, repository, and broad-audience framing burden. | Use broader problem framing, tighter section architecture, explicit source-data mapping, and stronger availability wording. | Whether current scope is strong enough; source-data package finalization; journal-specific policy checks. |

Do not create the journal-formatted manuscript until the author team has
selected the venue route and closed the blockers in the no-go packet.

## With-Dongxing manuscript conversion workflow

| manuscript element | source basis | conversion action | risk check |
|---|---|---|---|
| Title | Integrated scaffold; claim locks in the blocker packet. | Name monitor-gated value filtering, GeoJEPA-MPC, and constrained farmland layout planning. | Avoid "first", "general", "transfer succeeds", or scale-up success wording. |
| Abstract | Integrated scaffold, tables, source-data map, and figure/table freeze. | Draft last using context, bottleneck, approach, Bishan 20x16/top5 result, Dongxing calibration, and boundary. | Include the Dongxing boundary without implying robust transfer superiority. |
| Introduction | Integrated scaffold and verified citation map. | Use a field-scale to bottleneck funnel: farmland planning, sequential swap planning, value filtering, monitoring, and external-region calibration. | Do not overstate policy scope or claim broad geospatial generality without citations. |
| Methods | Self-contained Bishan notes, Dongxing section draft, reproducibility guide, and data-access register. | Separate task formulation, Bishan environment, Dongxing/Neijiang environment, label generation, monitor gate, value-head training, rollouts, and reproducibility scope. | No hidden Paper9 dependency in the public route; no vague "standard preprocessing" language. |
| Results | Integrated tables, Main Figure 1 through Main Figure 4, Supplementary Figure S1, and source-data maps. | Use the evidence ladder: workflow validation, Bishan main result, 50-state boundary, Dongxing return-label scaling, and low-label stress test. | Observation must stay separate from interpretation; scratch advantages must remain visible. |
| Discussion | Post-Dongxing gap audit and blocker packet. | Interpret why guarded value filtering helps, why transfer superiority remains mixed, and which data/access limits remain before reuse. | Do not convert limitations into generic future-work language. |
| Conclusion | Integrated scaffold and claim-evidence guardrails. | State the bounded contribution, decisive Bishan evidence, Dongxing calibration value, and current boundary in one compact paragraph. | No new data, no universal planner claim, and no positive 50-state scale-up wording. |
| Data and Code Availability | Availability draft, rights register, archive checklist, and source-data map. | Backfill identifiers, licences, and dataset-to-route mapping after decisions are made. | Do not use vague request-only wording; name the chosen public or controlled route. |
| References | Verified BibTeX, local-source bibliography, citation map, and `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`. | Apply the target journal style only after the citation policy is fixed. | Public manuscript must not rely on unresolved local-only placeholders. |
| Figures and tables | `e0_integrated_figure_table_numbering_freeze_2026-06-11.md` and `e0_source_data_map_with_dongxing_2026-06-11.md`. | Preserve Main Figure 4, Supplementary Figure S1, Main Table 3, and source-data links unless the target journal forces a documented change. | Every quantitative figure/table must map to tracked source data or a named external data route. |

CEUS-specific conversion addendum from
`e0_ceus_reviewer_improvement_packet_2026-06-12.md`:

| CEUS reviewer risk | required conversion action | no-go wording |
|---|---|---|
| Grid or block abstraction may look unrealistic for irregular cadastral parcels. | State the block-level planning-unit abstraction and name area-tolerance matching as the irregular-parcel extension. | Do not claim arbitrary cadastral parcel exchange is solved. |
| Queen contiguity may not capture engineering adjacency. | Add shared-perimeter-weighted contiguity and shape compactness as future deployment requirements. | Do not claim shared-perimeter-weighted contiguity was evaluated. |
| Soft training and hard inference may look theoretically inconsistent. | Explain reward/count penalties as ranking guidance and executable masks plus paired inference as hard rollout enforcement. | Do not claim a Constrained MDP, CPO, or RCPO implementation. |
| Sensitivity may look like reward-engineering fragility. | Use Dongxing `candidate-value-weight=1.0` as evidence of planner calibration and local deployment tuning. | Do not present one candidate-value weight as universal. |

## Figure and table conversion locks

Use `e0_integrated_figure_table_numbering_freeze_2026-06-11.md` as the current
generic freeze:

- Main Figure 1: monitor-gated value filtering workflow.
- Main Figure 2: Bishan 20x16/top5 reward and stability.
- Main Figure 3: Bishan 50-state monitor boundary.
- Main Figure 4: Dongxing return-label scaling.
- Supplementary Figure S1: Dongxing low-label transfer stress test.
- Main Table 1: Bishan monitor gates.
- Main Table 2: Bishan rollout improvement and stability.
- Main Table 3: Dongxing return-label scaling.
- Supplementary Table S1: Bishan 50-state details.
- Supplementary Table S2: Dongxing low-label stress test.

If target-journal limits require moving items between main text and
Supplementary Information, update the freeze, source-data map, scaffold, table
package, and final manuscript in the same conversion pass.

## Claim-evidence guardrails

| claim direction | allowed conversion wording | prohibited wording or implication |
|---|---|---|
| Bishan primary result | The monitor-gated 20x16/top5 value filter improved five-seed mean reward from `65.2566` to `69.4705` and reduced sample standard deviation from `5.0037` to `1.0004`. | Do not claim superiority over all planners, all regions, or all geospatial planning tasks. |
| Monitor gate | Monitor diagnostics identify when value labels are suitable for value-head training and manuscript-facing claims. | Do not claim the monitor guarantees all future label scales. |
| Dongxing return labels | Dongxing return-label scaling improves both transfer and scratch families relative to pairwise-only labels. | Do not claim robust Bishan-to-Dongxing transfer superiority. |
| Dongxing low-label budgets | Scratch is stronger at 5 and 10 labels, while transfer is stronger at 20 labels in the recorded stress test. | Do not hide the mixed result or recast it as a pure transfer win. |
| 50-state Bishan diagnostics | Tested 50-state Bishan labels failed monitor gates and define the current scale-up boundary. | Do not claim direct 50-state Bishan scale-up success. |
| Data and code reuse | Smoke data, generated source data, checkpoints, scripts, and external full-data routes are mapped separately. | Do not imply that all full Bishan or Dongxing/Neijiang prepared data are already deposited. |

## Required backfill fields before final manuscript

| field | required before journal-specific formatting | source or decision owner |
|---|---|---|
| Target journal and article type | Journal name, article type, audience breadth, abstract format, word limit, reference style, anonymity policy, and figure/table limits. | Author team plus target journal instructions. |
| Repository DOI or reviewer link | Persistent repository DOI, anonymous reviewer link, or journal-approved private route for the exact submission commit. | Archive release checklist. |
| Code licence | Named licence or institution-approved restriction for repository code and scripts. | Author/institution decision. |
| Generated-data rights | Rights terms for generated Markdown, CSV, JSON, NPZ, checkpoints, and model weights that do not relicense restricted raw data. | Author/institution decision. |
| Full Bishan Tool2 data access route | Public DOI, controlled-access record, or institution-approved access process for full `tool2/` files. | Data owner/institution decision. |
| GPKG-root geospatial inputs access route | Public or controlled route for `DLTB_with_slope.gpkg`, block products, and township inputs. | Data owner/institution decision. |
| Dongxing/Neijiang prepared data access route | Public DOI or controlled-access metadata route for prepared 3711-block products, parcel assignments, transition/pairwise files, environment wrappers, and geospatial inputs. | Data owner/institution decision. |
| Citation policy | Whether local-only sources can be formalized, whether preprints are acceptable, and which references are required in each section. | Author team plus target journal instructions; current control file is `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`. |
| Statistical reporting policy | Descriptive-only reporting or predefined statistical tests, comparison groups, correction policy, and reporting precision. | Author team and target journal expectations; current control file is `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`. |
| Final export package | Final figure dimensions, resolution, source-data naming, table files, supplementary package, and manuscript file format. | Target journal instructions. |

## Final preflight and test sequence

Run this sequence after the checklist is updated and before any final
journal-specific manuscript file is declared ready:

1. Confirm the blocker packet no longer has unresolved no-go decisions or marks
   any remaining item as a target-journal-approved limitation.
2. Confirm the final title, abstract, Results, Discussion, conclusion,
   captions, and availability statement all use the same claim boundary.
3. Confirm Main Figure 4, Supplementary Figure S1, Main Table 3, and all Bishan
   figures/tables still map to source data.
4. Confirm DOI/reviewer-link, licence, full Bishan route, GPKG-root route, and
   Dongxing/Neijiang route are backfilled in availability and archive metadata.
5. Confirm citation keys resolve and local-only placeholders are removed or
   formalized.
6. Run `D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider`.
7. Run `D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py`.
8. Run `git diff --check`.

Passing these checks means the repository guardrails are internally consistent.
It does not mean a target journal has accepted the data route, citation policy,
statistical policy, or figure export package.
