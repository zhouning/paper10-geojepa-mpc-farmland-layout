# Paper10 formal-output readiness audit

Date: 2026-07-06

Status: not_ready_for_formal_submission

Verdict: Paper10 should not be exported as a final CEUS submission package yet. It can be exported as a bounded CEUS manuscript-conversion draft, with the external data, rights, licence, figure-export and declaration decisions still open.

## Scope

This audit reviews the latest Paper10 CEUS baseline-hardened manuscript assembly:

- `e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`
- current repository HEAD at the time of audit: `e5b6a23940aedf8b78cec4e91d61a412288cbdc4`
- current no-go boundary: `e0_paper10_submission_readiness_boundary_2026-06-26.md`
- current data boundary: `DATA_AVAILABILITY.md`

The CEUS author guide was checked on 2026-07-06: `https://www.sciencedirect.com/journal/computers-and-electronics-in-agriculture/publish/guide-for-authors`. The relevant conversion constraints are editable source files, an abstract not exceeding 250 words, 1-7 keywords, a separate editable highlights file with 3-5 bullet points of at most 85 characters each, separate figure files, editable tables, research-data deposit and citation or a stated reason why data cannot be shared, and a data availability statement at submission.

## Reviewer-style readout

### Reviewer 1: technical readiness

The technical story is now defensible as a bounded algorithmic paper. The strongest supported contribution is not broad superiority; it is a reproducible evidence-control workflow in which monitor gates select value-label targets, executable masks prevent invalid rollout behavior, and the manuscript reports where larger label sets and cross-region transfer stop helping.

The case is still not complete for formal submission because the package does not yet provide the full external data access route needed to inspect or rerun the reported full Bishan and Dongxing/Neijiang workflows. Repository DOI, software licence, generated-data rights and checkpoint rights also remain unresolved. These are not cosmetic issues; they affect reviewer trust and publisher compliance.

### Reviewer 2: novelty and claim strength

The paper has a credible CEUS-facing novelty angle if it is framed around monitor-gated value labels for geospatial planning support. The authors should avoid framing the result as a general 50-state improvement, robust Bishan-to-Dongxing transfer advantage, or deployment-ready cadastral planner. The current evidence does not support those claims.

The Bishan 20x16/top5 result is useful but descriptive. Mean reward is 69.4705 for the value-filter policy versus 67.5437 for the matched Paper9 comparator, with sample standard deviation 1.0004 versus 7.2246. The seed-wise result is mixed: paired deltas are -3.2408, 3.6137, 8.4242, 9.0620 and -8.2248, so the value filter wins 3/5 seeds and loses seeds 0 and 4. Stage 3 rows remain below the matched comparator, and Dongxing/Neijiang supports calibration rather than transfer superiority.

### Reviewer 3: readability and package readiness

The latest manuscript assembly is readable enough for internal conversion, but it still contains author-handoff material, claim-evidence tables and blocker tables that should not remain in the main journal manuscript body. Those items belong in supplementary materials, an internal submission checklist, or an archive README.

The draft also needed CEUS-format cleanup. The in-manuscript highlights have now been reduced to five bullets, and a separate highlights text file has been added. The remaining package-level work is figure and table export, editable source manuscript assembly, declarations, data/code availability backfill and reference-style finalization.

## Cross-review synthesis

Consensus: Paper10 is scientifically usable as a bounded manuscript draft, but not yet as a formal submission package. The internal evidence boundaries are now mostly honest and coherent. The remaining blockers are external submission requirements and manuscript packaging decisions, plus the need to keep the claim strength aligned with descriptive evidence.

The current safe output is:

- CEUS baseline-hardened manuscript assembly draft.
- CEUS formal-output conversion patch.
- Separate CEUS highlights text file.
- Source-mapped figures, tables and evidence registers.

The current unsafe output is a final journal submission package that implies closed data access, closed code/data rights, finished figure exports, resolved references or inferential superiority.

## No-go blockers

| blocker | status | required close-out evidence |
|---|---|---|
| Repository DOI or anonymous reviewer link | open | durable archive DOI or journal-approved reviewer link, exact commit hash and access window |
| Code licence | open | licence file and matching manuscript wording |
| Generated-data and checkpoint rights | open | rights terms for value labels, rollout outputs, checkpoints and optional model assets |
| Full Bishan Tool2 data route | open | public repository record or controlled-access metadata record with owner, eligibility, review process and reviewer access |
| GPKG-root geospatial input route | open | public or controlled-access route for slope-enriched geospatial inputs, blocks and township inputs |
| Dongxing/Neijiang prepared-data route | open | public or controlled-access route for prepared block, parcel, trajectory and environment-wrapper files |
| Citation and reference style | open | verified public references, preprint markings if used, and final CEUS reference formatting |
| Statistical reporting policy | open | keep descriptive wording unless a predefined inference plan is added before new tests |
| Main Figure 1 and figure/table exports | open | final editable schematic, separate figure files, captions, table placement and source-data links |
| Declarations | open | funding, competing interests, CRediT, AI-use disclosure if applicable, acknowledgements and permissions |

## What is already close to formal output

- Title and one-sentence argument are aligned with the evidence boundary.
- Abstract is under the CEUS 250-word limit.
- Keywords are within the 1-7 CEUS limit.
- Highlights are now reduced to 5 CEUS-length bullets.
- Bishan primary result is reported with matched comparator, seeds, mean, sample standard deviation, paired deltas and mixed seed-wise boundary.
- Mechanism evidence separates executable-mask necessity from monitor-gate evidence control.
- Stage 3 and Dongxing/Neijiang are framed as boundary and calibration evidence.
- The Data and Code Availability draft correctly preserves pending DOI, licence and controlled-access backfill rather than pretending those decisions are closed.

## Required close-out order

1. Freeze the target route as CEUS Original Research and confirm author list, affiliations, corresponding author and declarations.
2. Create the repository archive and record DOI or anonymous reviewer link.
3. Add the software licence and generated-output/checkpoint rights wording.
4. Publish or register controlled-access records for full Bishan Tool2, GPKG-root and Dongxing/Neijiang prepared data.
5. Generate final editable manuscript source and move author-handoff/checklist tables out of the main body.
6. Export figures and tables as separate journal files, including final Main Figure 1 artwork.
7. Backfill Data and Code Availability, data references, web-reference access dates, declarations and source-data file names.
8. Rerun the submission preflight and targeted tests.

## Claim locks for the formal manuscript

- Report Bishan 20x16/top5 as a descriptive matched 5-seed reward anchor.
- State that the value-filter policy wins 3/5 seeds and loses seeds 0 and 4.
- Keep the diagnostic-only sign-test readout as a non-inferential diagnostic.
- Treat executable masks as necessary for valid rollouts under the current protocol.
- Treat the monitor gate as evidence control for label escalation.
- Treat Stage 3 rows and the 50x24 sweep as boundary evidence.
- Treat Dongxing/Neijiang as calibration and stress-test evidence.
- Do not claim direct 50-state Bishan scale-up success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim solved irregular cadastral parcel deployment.
- Do not claim a full Constrained MDP, CPO or RCPO solver.
- Do not claim Paper10 invented GeoJEPA.

## Formal-output decision

Decision: continue conversion work, but do not produce a final submission package until the no-go blockers are closed. The latest manuscript is strong enough to serve as the source of a formal CEUS draft, not strong enough to be treated as the submitted article package itself.
