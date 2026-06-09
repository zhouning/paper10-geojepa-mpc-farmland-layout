# Paper10 E0 self-contained manuscript submission gap audit

Date: 2026-06-09

This audit reviews the self-contained integrated manuscript route before a
target-journal submission file is created. It is a reviewer-risk ledger, not a
new manuscript draft. It does not select a journal, add experiments, assign
repository identifiers, resolve licences, change the positive E0 claim, or
claim a passing 50-state result.

## Source basis

- `e0_frontier_random050_integrated_manuscript_self_contained_methods_draft_2026-06-09.md`
- `e0_target_venue_and_manuscript_conversion_checklist_2026-06-09.md`
- `e0_submission_readiness_checklist_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `e0_source_data_map_2026-06-09.md`
- `e0_archive_release_and_doi_backfill_checklist_2026-06-09.md`

## One-sentence argument under audit

In constrained Bishan farmland swap planning, Paper10 shows that
monitor-gated `frontier_random050` value labels improve GeoJEPA-MPC rollout
reward and seed stability at the reproducible 20x16/top5 scale, supported by
five-seed rollout summaries, monitor diagnostics, and a GPKG-root reproduction
audit, with the boundary that tested 50-state labels failed the monitor gate
and remain negative diagnostics.

## Blocking gaps before journal submission

| blocker | why it blocks submission | required close-out |
|---|---|---|
| Target journal and article type are not selected. | The manuscript cannot be formatted, sectioned, shortened, or referenced correctly without venue rules. | Fill target journal, article type, abstract format, word limits, reference style, figure/table limits, anonymity policy, and required supplementary elements. |
| Final manuscript file has not been created from the self-contained route. | The current file is a working integrated draft, not a journal-formatted submission file. | Create `[FINAL MANUSCRIPT FILE TO BE CREATED]` only after venue, archive, data-access, and figure/table decisions are fixed. |
| Repository DOI or reviewer link is missing. | Data and Code Availability still contains `[REPOSITORY/DOI TO BE ADDED]`; reviewers cannot cite or inspect a stable archive record. | Release the exact submission commit or create a repository-supported reviewer link, then backfill all repository fields. |
| Full Bishan `tool2/` route is undecided. | Full training and rollout reruns need `tool2/transitions.npz` and `tool2/pairwise.npz`, which are external to Git. | Choose public DOI or controlled-access record, including owner, access route, eligibility, review criteria, and data-use terms. |
| GPKG-root geospatial access route is undecided. | The positive 20x16/top5 reproduction depends on the GPKG-root convention, but the prepared geospatial inputs are external. | Decide public deposit or controlled-access metadata for `DLTB_with_slope.gpkg`, `results_real/blocks/`, and `townships.json`. |
| Code and data licences are not fixed. | Archive metadata and Data Availability cannot be finalized without rights terms. | Select code licence and generated-data rights; confirm whether optional GeoFM files may remain in the public archive. |
| Figure and table numbering are not frozen. | Source-data mapping, captions, and final manuscript cross-references may drift. | Select final main and supplementary figures/tables, then update the figure plan, table draft, source-data map, and manuscript text. |
| Reference policy is unresolved. | The public manuscript must not cite local-only Paper9 material, and the LeWorldModel preprint policy depends on the venue. | Keep the self-contained Paper10 task route; decide whether the target journal permits the 2026 arXiv LeWorldModel citation. |

## Reviewer risks that can be handled by framing

| risk | current status | recommended framing |
|---|---|---|
| Contribution may look narrow. | Positive evidence is bounded to 20x16/top5 rather than a broad benchmark suite. | Frame the contribution as monitor-gated value-label selection plus a transparent failure boundary, not as broad planner superiority. |
| Evaluation breadth may be challenged. | Main comparison is 20x16/top5 versus 10x12/top4 over five rollout seeds, with failed 50-state diagnostics. | State the E0 scope explicitly; use 50-state rows as stress-test diagnostics and avoid broad claims. |
| Baseline completeness may be challenged. | The direct comparator is the prior 10x12/top4 pilot, with a matched `frontier_independent` branch mentioned as context. | Keep baseline language local and bounded; do not claim superiority over external geospatial optimizers. |
| Methods may read long for some venues. | The self-contained draft includes task, environment, reward, data root, labels, monitor gates, training, and rollout details. | Move venue-excess detail to supplementary Methods only after ensuring reproducibility details remain accessible. |
| Abstract may over-emphasize negative diagnostics. | The draft includes both the positive result and the 50-state boundary. | Lead with the 20x16/top5 gain and stability improvement; keep 50-state rows as a concise boundary sentence. |
| GPKG/shapefile issue may look like fragility. | The macOS audit identified GPKG-root resolution as part of the reproducible condition. | Present this as a documented data-root condition and source-data audit, not as an incidental file-format problem. |

## Current strengths to preserve

| strength | evidence | preservation rule |
|---|---|---|
| Public route avoids a local-only Paper9 citation. | The self-contained manuscript body intentionally does not cite `zhou2026paper9_local`. | Keep task, reward, and environment details inside Paper10 Methods unless a public Paper9 source becomes available. |
| Main quantitative claim is source-backed. | 20x16/top5 mean `69.4705`, sample std `1.0004`, improvement `4.2139` or `6.46%`. | Keep these values tied to rollout summaries and table sources. |
| Reproducibility condition is explicit. | GPKG-root audit reproduced packaged 20x16 labels exactly or within floating-point tolerance. | Keep GPKG root in Methods, Data Availability, and source-data mapping. |
| Failed 50-state rows are not hidden. | macOS seed45 and Windows seed46 rows are documented as monitor failures. | Use them as boundary evidence only; do not imply training or positive 50-state validation. |
| Archive scaffolding exists. | Metadata templates, manifest, source-data map, release checklist, and conversion checklist are tracked. | Use these files as the single source of truth during final backfill. |

## Section-level close-out checklist

| section | must be closed before final manuscript | owner file |
|---|---|---|
| Title | Select venue-appropriate title without broad scale language. | Final manuscript file. |
| Abstract | Rewrite after figure/table and Data Availability decisions are fixed. | Final manuscript file. |
| Introduction | Decide whether target venue needs China-specific farmland policy context. | Final manuscript file and verified references. |
| Methods | Decide main versus supplementary placement for long environment and reward details. | Self-contained Methods note and final manuscript file. |
| Results | Freeze final table/figure numbering and rounding policy. | Tables draft, figure plan, source-data map. |
| Discussion | Keep one-step-reward rival explanation and failed 50-state boundary visible. | Final manuscript file. |
| Data and Code Availability | Replace all DOI, reviewer-link, licence, and data-access placeholders. | Data availability draft and archive metadata templates. |
| References | Convert citations to target style and remove any local-only public citation path. | Verified BibTeX, citation map, final manuscript file. |

## Recommended next action order

1. Select the target venue family and article type.
2. Decide whether the current E0 scope is best framed as computational
   planning, methods/reproducibility, or a Nature-family route.
3. Freeze the intended main figures and tables.
4. Choose archive platform, code licence, generated-data rights, and full-data
   access route.
5. Backfill repository DOI or reviewer link and controlled-access fields.
6. Create the final journal-specific manuscript file from the self-contained
   route.
7. Run final citation, claim, source-data, archive, and smoke-test checks from
   the exact submission commit.
