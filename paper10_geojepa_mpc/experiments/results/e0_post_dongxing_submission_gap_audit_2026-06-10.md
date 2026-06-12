# Paper10 Post-Dongxing Submission Gap Audit

Date: 2026-06-10

This audit updates the Paper10 submission-readiness view after the
Dongxing/Neijiang real-environment experiments. It is a reviewer-risk and
close-out ledger. It does not select a journal, create a final submission file,
assign repository identifiers, resolve data rights, or add new experiments.

The current no-go decision packet for turning this audit into author decisions
is `e0_submission_blocker_decision_packet_2026-06-11.md`.
The current with-Dongxing target-venue and manuscript-conversion checklist is
`e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`.
The current citation and statistical-reporting policy is
`e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`.

## Source Basis

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_dongxing_manuscript_section_draft_2026-06-10.md`
- `e0_dongxing_results_synthesis_2026-06-10.md`
- `e0_dongxing_return_label_50x16_family_2026-06-10.md`
- `e0_dongxing_low_label_budget_family_2026-06-10.md`
- `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`

## Updated One-Sentence Argument Under Audit

In constrained farmland layout planning, Paper10 shows that monitor-gated
GeoJEPA-MPC value filtering can improve real-environment rollouts and can be
calibrated in a second county-level environment, supported by the Bishan
20x16/top5 value-label result, Dongxing return-label scaling, and low-label
transfer stress tests, with the boundary that direct 50-state Bishan scale-up
and naive Bishan-to-Dongxing transfer are not robustly supported.

## What Changed After Dongxing

| item | before Dongxing | after Dongxing | manuscript effect |
|---|---|---|---|
| Evidence breadth | Bishan E0 only, with 20x16/top5 positive result and 50-state monitor failures. | Adds a second real county-level environment with 3711 blocks and 76376 parcels. | The paper can now claim cross-region execution and calibration, not only single-region validation. |
| Transfer claim | Not tested beyond Bishan. | Pairwise-only, return-label, and low-label Dongxing tests show mixed or negative transfer superiority. | The paper must avoid robust transfer-superiority language. |
| Value-label utility | Positive at Bishan 20x16/top5. | Dongxing return-label scaling improves both transfer and scratch families up to 50x16. | The value-label workflow has stronger method evidence. |
| Boundary evidence | Bishan 50-state labels failed monitor gates. | Dongxing scratch remains stronger at 50x16 and at 5/10 low-label budgets. | The limitation section becomes more credible and more specific. |
| Figure/table package | Bishan tables and CSVs only. | Adds Dongxing summary CSVs and integrated table package. | Main or supplementary figures can now show external-region calibration. |

## Blocking Gaps Before Journal Submission

| blocker | why it blocks submission | required close-out |
|---|---|---|
| Target journal and article type remain unset. | The manuscript cannot be formatted, shortened, or referenced correctly without venue rules. | Select target journal, article type, abstract format, word limits, reference style, figure/table limits, anonymity policy, and source-data requirements. |
| Final manuscript file does not exist. | The current assets are scaffolds, section drafts, and table packages, not a journal-formatted submission manuscript. | Create a final manuscript file after venue, figure/table, data-access, and archive decisions are fixed. |
| Figure assets are not final. | The integrated scaffold names Figures 1-5, but Dongxing figures are not yet plotted and Figure 1 is not drawn. | Generate or draw the final figure set, freeze numbering, and create panel-level source-data mapping. |
| Repository DOI or reviewer link is missing. | Data and Code Availability still lacks a stable archive identifier. | Archive the exact submission commit or create a reviewer link, then backfill all DOI/reviewer-link placeholders. |
| Full Bishan data route is undecided. | Full training and rollout reproduction depends on external `tool2/` files. | Decide public DOI or controlled-access route for full Bishan Tool2 data. |
| Dongxing/Neijiang data route is undecided. | The external-region evidence depends on `D:\test\neijiang_cross_region` data and environment wrapper files outside the Git-tracked package. | Decide whether Dongxing prepared data can be public; otherwise define a controlled-access route and metadata record. |
| GPKG-root geospatial access route is undecided. | Bishan label reproduction depends on the GPKG-root convention, and the prepared geospatial inputs may be restricted. | Define public deposit or controlled-access metadata for GPKG-root inputs. |
| Code and generated-data licences are not fixed. | Archive metadata and Data Availability cannot be final without rights terms. | Select code licence and generated-output rights; confirm optional external assets. |
| Citation policy is unresolved. | The final manuscript still needs journal-appropriate citations and must avoid local-only public citations. | Use `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`, finalize verified references, decide whether 2026 arXiv sources are acceptable, and remove or formalize local-only placeholders. |
| Statistical reporting policy is not fixed. | Current results report descriptive means and standard deviations, not hypothesis tests. | Use `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md` and decide whether descriptive reporting is sufficient for the target venue or whether pre-declared statistical tests are required. |

## Reviewer Risks After Dongxing

| risk | current status | recommended framing |
|---|---|---|
| Reviewers may expect positive transfer after seeing a second region. | Dongxing does not support robust Bishan-to-Dongxing transfer superiority. | Frame Dongxing as external-region stress testing and calibration, not as a positive transfer benchmark. |
| Reviewers may ask why scratch beats transfer. | Scratch is stronger at Dongxing 50x16 and at 5/10 low-label budgets; transfer is stronger only at 20 labels and slope reduction. | State the objective tradeoff: transfer helps slope-oriented outcomes, scratch is stronger for contiguity and baimu-area outcomes. |
| Contribution may still look narrow. | Evidence is stronger than before, but still two-region and descriptive. | Emphasize the workflow: monitor gate, executable masks, return labels, planner calibration, and transparent failure boundaries. |
| Evaluation may be seen as internally benchmarked. | There is no external optimizer benchmark suite. | Avoid claims against all planners; claim reproducible workflow calibration under real-environment rollouts. |
| Data availability may be challenged. | Full Bishan and Dongxing prepared data are not yet assigned public or controlled routes. | Resolve access routes before submission; do not use vague "available upon request" wording. |
| Figure burden has increased. | Integrated story now needs Bishan and Dongxing panels. | Use a small main figure set and move detailed seed/checkpoint tables to supplementary material. |

## Current Strengths to Preserve

| strength | evidence | preservation rule |
|---|---|---|
| Bishan main positive result is bounded and numeric. | 20x16/top5 mean reward `69.4705`, sample std `1.0004`, improvement over 10x12/top4. | Keep this as the primary positive result. |
| Bishan 50-state failures are explicit. | macOS and Windows 50-state labels failed monitor gates. | Keep them as scale-up boundary evidence. |
| Dongxing adds real external-region evidence. | 3711-block Dongxing/Neijiang environment, return-label training, and real rollouts completed. | Use Dongxing to support method portability and calibration, not transfer superiority. |
| Dongxing return labels improve both families. | Transfer improves `37.8894` to `51.6183`; scratch improves `40.2111` to `55.7324`. | Claim return-label utility, not initialization superiority. |
| Low-label budget result is honestly mixed. | Scratch higher at 5/10 labels; transfer higher at 20 labels. | Use as stress-test evidence and limitation. |
| Figure-ready CSVs now exist for Dongxing. | `e0_dongxing_return_label_family_summary_2026-06-10.csv` and `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`. | Use these as source data for Dongxing plots. |

## Section-Level Close-Out Checklist

| section | must be closed before final manuscript | owner file |
|---|---|---|
| Title | Select title that names monitor-gated value filtering without overclaiming transfer. | Integrated scaffold and final manuscript. |
| Abstract | Use Bishan 20x16/top5 as primary positive result and Dongxing as calibration evidence. | Integrated scaffold and final manuscript. |
| Introduction | Add final citations and decide policy/context breadth. | Verified references and final manuscript. |
| Methods | Integrate Bishan and Dongxing protocols without making Methods unreadably long. | Self-contained Methods note plus Dongxing section draft. |
| Results | Freeze figure/table order and decide whether Dongxing low-label budget is main or supplementary. | Integrated table package and final manuscript. |
| Discussion | Preserve boundary language: no robust transfer superiority. | Integrated scaffold and final manuscript. |
| Data and Code Availability | Add repository DOI/reviewer link, full Bishan route, Dongxing route, and GPKG-root route. | Data availability draft and access-rights register. |
| References | Resolve citation style and local-only source policy. | Verified BibTeX and final manuscript. |
| Source data | Map every final figure/table to tracked CSV/JSON/Markdown source. | Source-data map update needed. |

## Recommended Next Action Order

1. Freeze the final main and supplementary figure/table set under the
   with-Dongxing scaffold.
2. Generate figure assets for Bishan reward/stability, Bishan 50-state monitor
   failures, Dongxing return-label scaling, and Dongxing low-label budget.
3. Update the source-data map with the final panel-to-file mapping.
4. Select target venue and article type.
5. Update Data and Code Availability for Dongxing/Neijiang data access.
6. Decide repository DOI or reviewer-link route and archive platform.
7. Create the final journal-specific manuscript file from the integrated
   scaffold using
   `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`.
8. Run final claim, citation, source-data, data-availability, and smoke-test
   checks from the exact submission commit.

## Stop Conditions

Do not create the final submission manuscript until these are resolved:

- target journal and article type;
- final figure/table set;
- repository DOI or reviewer link;
- code and data licence decisions;
- full Bishan and Dongxing data access routes;
- GPKG-root access route;
- citation policy for local-only and preprint sources.

Do not strengthen the manuscript claim to "cross-region transfer succeeds" or
"Bishan initialization beats local training." The current evidence does not
support those statements.
