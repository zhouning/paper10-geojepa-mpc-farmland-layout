# Paper10 E0 target venue and manuscript conversion checklist

Date: 2026-06-09

This checklist converts the current self-contained Paper10 E0 manuscript draft
into a target-journal submission package. It does not select a journal, assign
DOIs, add experimental evidence, change the positive claim, or resolve data
rights. It defines the decisions and manuscript edits that must happen after a
venue is selected.

Use `e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md` as the
reviewer-risk blocker ledger before creating the final journal-specific
manuscript file.

## One-sentence argument

In constrained Bishan farmland swap planning, Paper10 shows that monitor-gated
`frontier_random050` value labels improve GeoJEPA-MPC rollout reward and seed
stability at the reproducible 20x16/top5 scale, supported by five-seed rollout
summaries, monitor diagnostics, and a GPKG-root reproduction audit, with the
boundary that tested 50-state labels failed the monitor gate and remain
negative diagnostics.

## Canonical terminology

| term | first-use definition | conversion rule |
|---|---|---|
| Paper10 | The current GeoJEPA-MPC farmland layout planning manuscript and reproducibility package. | Use as internal package name; replace with final title in journal files if needed. |
| GeoJEPA-MPC | The packaged rank-checkpoint planner and finite-horizon candidate-selection workflow. | Do not describe E0 as training a new transition model. |
| `frontier_random050` | Candidate-label strategy mixing model-scored frontier actions with random exploratory actions at frontier fraction 0.5. | Keep exact code token in Methods; use a readable expansion on first use. |
| monitor gate | Candidate-quality rule applied before value-head training. | Use as the central workflow control, not as an after-the-fact filter. |
| 20x16/top5 | Main positive E0 label scale with 20 states, 16 candidates, and top-5 gate. | Use as the current paper-facing result. |
| 10x12/top4 | Direct pilot baseline with 10 states, 12 candidates, and top-4 gate. | Use as the bounded comparator. |
| 50-state diagnostics | macOS seed45 and Windows seed46 50-state `frontier_random050` rows. | Use only as failed diagnostic evidence. |
| GPKG root | Full-data root resolving `DLTB_with_slope.gpkg` for reproducible 20x16 label generation. | Treat as part of the experimental protocol. |

## Venue decision grid

| venue route | strongest fit | manuscript conversion emphasis | pre-submission blocker |
|---|---|---|---|
| Generic computational planning / urban analytics journal | Current E0 evidence package with applied geospatial planning framing. | Keep the abstract and Introduction accessible; preserve full Methods detail; present 50-state rows as boundary diagnostics. | Target journal format, reference style, repository DOI or reviewer link, and full-data access route. |
| Methods or reproducibility-focused venue | Monitor-gated value-label workflow plus reviewer-runnable package. | Emphasize workflow, monitor gates, reproducibility assets, source-data map, and failure-mode transparency. | Software licence, archive metadata, and full-data route for reruns beyond smoke tests. |
| Nature-family or Springer Nature route | Possible only if the authors want a higher data-policy and source-data burden. | Use broader opening, tighter claims, explicit source-data mapping, and stronger Data and Code Availability. | Whether E0 scope is strong enough, whether full data can be deposited or controlled-access metadata can satisfy policy, and whether figure source data are final. |

Do not create a final formatted manuscript until `[TARGET JOURNAL TO BE
SELECTED]`, `[ARTICLE TYPE TO BE SELECTED]`, and `[REFERENCE STYLE TO BE
SELECTED]` are filled.

## Manuscript conversion workflow

| section | current source | conversion action | risk check |
|---|---|---|---|
| Title | `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md` | Choose a concrete title that names value filtering, GeoJEPA-MPC, and farmland layout planning. | Avoid "first", "general", or broad scalability claims. |
| Abstract | Same self-contained draft plus tables and source-data map. | Rewrite after final Results and Discussion are frozen: context, bottleneck, approach, 20x16/top5 result, implication, boundary. | Include the quantitative improvement and the 50-state boundary without making the abstract read like a failure report. |
| Introduction | Self-contained draft; cited Introduction draft; verified bibliography. | Use a field-scale-to-bottleneck funnel: land-use planning, sequential swap planning, MPC/value functions, JEPA/world-model motivation, present monitor-gated workflow. | Decide whether China-specific farmland policy citations are needed for the chosen audience. |
| Methods | Self-contained Methods note; reward definitions; reproducibility docs. | Keep task formulation, data root, action/reward, candidate labels, monitor gate, value-head training, rollout evaluation, and reproducibility conditions. | No vague phrases such as "standard preprocessing"; no hidden Paper9 dependency in the public route. |
| Results | Results synthesis, tables draft, rollout summaries, monitor JSON files, figure CSVs. | Use evidence ladder: monitor validation, main 20x16/top5 result, GPKG reproduction, failed 50-state diagnostics. | Keep observation separate from interpretation; do not imply 50-state training occurred. |
| Discussion | Self-contained draft and submission readiness checklist. | Interpret why monitor gating matters, address one-step-reward rival explanation, explain GPKG-root reproducibility, and state 50-state bottleneck. | Limitations must be specific: five seeds, 20-state label scale, full-data access, candidate-proposal design. |
| Conclusion | Self-contained draft. | Restate contribution, decisive evidence, implication, and boundary in one compact paragraph. | No new data and no future-work promise stronger than the evidence. |
| Data and Code Availability | `e0_data_code_availability_draft_2026-06-09.md`; archive release checklist. | Backfill DOI, reviewer link, licences, full Tool2 route, and GPKG-root access route. | Do not write only "available upon request" for restricted data. |
| Figures and tables | Figure plan, manuscript tables, source-data map, plotting script. | Freeze final numbering and decide main versus supplementary placement. | Every quantitative figure/table must map to tracked source data. |
| References | Verified BibTeX, local-source status note, citation map. | Convert to the target journal style after citation policy is fixed. | Public manuscript body must not cite `zhou2026paper9_local`. |

## Section architecture after conversion

| section | paragraph jobs |
|---|---|
| Introduction | field stake; sequential planning bottleneck; prior methods and unresolved gap; present monitor-gated contribution. |
| Methods | task formulation; data and environment; GeoJEPA-MPC planner; value-label generation; monitor gate; value-head training; rollout evaluation; reproducibility boundary. |
| Results | monitor-gate selection; reward and stability improvement; GPKG-root reproduction; failed 50-state diagnostics. |
| Discussion | central advance; rival explanation and one-step-reward check; relation to MPC/value/world-model framing; constraints and next scale-up question. |
| Conclusion | bounded contribution; decisive 20x16/top5 evidence; implication for guarded value filtering; current boundary. |

## Backfill fields for final manuscript package

| field | required before final formatting | source or owner |
|---|---|---|
| `[TARGET JOURNAL TO BE SELECTED]` | Journal name, article type, audience breadth, and section order. | Author decision. |
| `[ABSTRACT FORMAT TO BE SELECTED]` | Structured or unstructured; word limit; required keywords. | Target journal instructions. |
| `[REFERENCE STYLE TO BE SELECTED]` | Numbered, author-year, BibTeX, EndNote, or journal-specific style. | Target journal instructions. |
| `[FIGURE/TABLE LIMITS TO BE SELECTED]` | Main and supplementary limits; source-data rules. | Target journal instructions. |
| `[REPOSITORY/DOI TO BE ADDED]` | Code and packaged E0 evidence archive identifier. | Archive release checklist. |
| `[FULL TOOL2 DOI TO BE ADDED]` | Public DOI or controlled-access record for full Tool2 data. | Data owner and archive route. |
| `[RESTRICTED-DATA ACCESS ROUTE TO BE ADDED]` | Named owner, request route, eligibility, review criteria, and data-use terms. | Data owner or institution. |
| `[CODE LICENCE TO BE SELECTED]` | Final software licence. | Author/institution decision. |
| `[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]` | Terms for generated E0 outputs, smoke data, and any shareable data. | Author/institution decision. |
| `[FINAL MANUSCRIPT FILE TO BE CREATED]` | Journal-formatted manuscript file. | Created after the above fields are fixed. |

## Claim-evidence guardrails during conversion

| claim type | allowed wording | prohibited direction |
|---|---|---|
| Main result | 20x16/top5 improved five-seed mean total reward from `65.2566` to `69.4705` and reduced sample standard deviation from `5.0037` to `1.0004`. | Do not imply superiority over all planners or all geospatial planning tasks. |
| Method contribution | Monitor-gated value labels improved candidate filtering at the validated E0 scale. | Do not claim the monitor proves label quality in all future scales. |
| Reproducibility | GPKG-root label generation reproduced the packaged 20x16 arrays exactly or within floating-point tolerance. | Do not omit the GPKG-root condition. |
| 50-state evidence | Tested 50-state labels failed the monitor gate and identify candidate proposal design as the next bottleneck. | Do not describe the failed rows as a passing 50-state result or positive 50-state evidence. |
| Paper9 provenance | Self-contained public route describes task, environment, and reward from packaged Paper10 code and notes. | Do not cite the local-only Paper9 placeholder in the final manuscript body. |

## Final manuscript checks

Run these checks before submitting or creating the archive record:

1. Confirm the manuscript uses the self-contained route unless a public Paper9
   citation exists.
2. Confirm blockers in
   `e0_self_contained_manuscript_submission_gap_audit_2026-06-09.md` are closed
   or explicitly carried as venue-approved limitations.
3. Confirm every citation key resolves after conversion to the target reference
   style.
4. Confirm the final title, abstract, Results, Discussion, and Conclusion all
   use the same claim boundary.
5. Confirm figure/table numbering matches the source-data map.
6. Confirm Data and Code Availability includes repository identifiers or
   reviewer links, not placeholders.
7. Confirm full Tool2 and GPKG-root data access wording names a concrete public
   or controlled route.
8. Grep for prohibited broad-scale or public-Paper9 claims.
9. Run reviewer smoke tests from the exact submission commit.

## Author action notes

- This checklist converts the existing self-contained manuscript into a real
  submission draft; it does not choose the journal for the authors.
- The positive claim remains limited to 20x16/top5; 50-state rows remain failed
  diagnostics and boundary evidence.
- Do not create the final submission manuscript file until the target journal,
  abstract format, reference style, figure/table limits, DOI, licences, and
  full-data access route are fixed.
