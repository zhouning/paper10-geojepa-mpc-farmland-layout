# Paper10 integrated citation and statistical reporting policy

Date: 2026-06-12

File: `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`

This policy controls citation and statistical-reporting wording for the current
with-Dongxing Paper10 submission package. It is not a final reference style,
not a target-journal statistical-analysis plan, and not a substitute for author
decisions. It records the current safe route until the target journal, citation
policy, and statistical reporting policy are closed in
`e0_submission_blocker_decision_packet_2026-06-11.md`.

## Source basis

- `references/paper10_citation_map_2026-06-09.md`
- `references/paper10_verified_references_2026-06-09.bib`
- `references/paper10_local_sources_2026-06-09.bib`
- `references/paper10_paper9_local_source_status_2026-06-09.md`
- `e0_citation_and_claim_checklist_2026-06-09.md`
- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`

## One-sentence policy

Paper10 should cite only verified public sources for external intellectual
debt, keep `zhou2026paper9_local` as an internal local-only placeholder unless
the authors formalize or replace it, and report current Bishan and
Dongxing/Neijiang results as descriptive evidence without formal hypothesis
tests unless a target-journal-approved statistical plan is added.

## Citation policy

| topic | current route | manuscript rule |
|---|---|---|
| Verified external literature | Use `references/paper10_verified_references_2026-06-09.bib` and the claim-specific map in `references/paper10_citation_map_2026-06-09.md`. | Cite a source only for the claim it directly supports. |
| Local Paper9 provenance | `zhou2026paper9_local` remains in `references/paper10_local_sources_2026-06-09.bib` and is documented in `references/paper10_paper9_local_source_status_2026-06-09.md`. | Do not cite `zhou2026paper9_local` in a public manuscript body unless the target venue permits unpublished author-verified sources. |
| Self-contained Paper10 Methods route | Use the Bishan task/environment note and reward-definition note if no public Paper9 source is available. | Prefer a self-contained Paper10 Methods route for task, reward, and environment provenance. |
| LeWorldModel / LeWM | `maes2026leworldmodel` is verified as a 2026 arXiv preprint. | Cite it only as a recent preprint design comparison or motivation source; do not write it as settled prior art. |
| Result claims | Use local CSV, JSON, Markdown, NPZ, checkpoint, and source-data-map artifacts. | Do not use external literature as evidence for Paper10's measured Bishan or Dongxing performance. |
| Final reference style | Still blocked by Target journal and article type. | Apply numbered, author-year, BibTeX, EndNote, or journal-specific style only after the target venue is selected. |

## Public-manuscript citation locks

- Public manuscript text must not rely on unresolved local-only placeholders.
- If `zhou2026paper9_local` remains in the bibliography for internal drafting,
  the public manuscript route must instead describe the Bishan task and reward
  within Paper10 Methods, Supplementary Methods, or a citable code/data
  supplement.
- If the target journal disallows arXiv preprints, remove
  `maes2026leworldmodel` from the final public manuscript or move it to an
  internal related-work note.
- New citations must be added first to the verified BibTeX or local-source
  inventory, then mapped to a specific claim in the citation map.

## Statistical reporting policy

| result family | current reporting status | safe wording |
|---|---|---|
| Bishan 10x12/top4 versus 20x16/top5 | Five rollout seeds per row; reported with mean, sample standard deviation, minimum, maximum, and percent change. | Describe as a five-seed descriptive rollout comparison. |
| Bishan monitor gates | Monitor outputs report candidate regret, candidate overlap, one-step regret, and stop/continue decisions. | Describe as a pre-training quality gate and scale-boundary diagnostic. |
| Bishan 50-state diagnostics | Tested label sets failed monitor gates and were not trained as positive scale-up rows. | Describe as failed monitor-gate diagnostics and current scale boundary. |
| Dongxing return-label scaling | Three initialization checkpoints and five rollout seeds per checkpoint are aggregated by family. | Describe as descriptive return-label scaling and planner calibration evidence. |
| Dongxing low-label stress test | Transfer and scratch families are mixed across 5, 10, and 20 label budgets. | Describe as a low-label transfer stress test, not as robust transfer superiority. |

No formal hypothesis tests have been run for the current integrated package.
Do not use `statistically significant`, p-values, confidence intervals, formal
superiority, non-inferiority, or equivalence wording unless a statistical plan,
analysis script, and source-data mapping are added.

## If formal tests are later added

Before adding inferential wording, the author team must define:

1. The primary hypothesis and outcome metric.
2. The unit of replication: seed, checkpoint, region, block, or rollout.
3. The comparison groups and whether the test is paired or unpaired.
4. The multiple-comparison policy for Bishan, Dongxing, return-label scaling,
   and low-label-budget families.
5. The exact analysis script and source-data files.
6. Reporting precision, effect sizes, confidence intervals, and target-journal
   table or caption requirements.

Until those fields exist, tables and captions should report descriptive means,
sample standard deviations, seed/checkpoint counts, and exact experimental
conditions.

## Claim wording guardrails

| claim area | allowed wording | prohibited direction |
|---|---|---|
| Bishan improvement | "The 20x16/top5 row had a higher five-seed mean reward than the 10x12/top4 row." | Do not call this a statistically significant improvement. |
| Dongxing calibration | "Return-label scaling increased mean reward in both transfer and scratch families." | Do not claim robust Bishan-to-Dongxing transfer superiority. |
| Low-label stress test | "Scratch was higher at 5 and 10 labels, while transfer was higher at 20 labels." | Do not hide the mixed result or convert it into a pure transfer win. |
| 50-state Bishan | "The tested 50-state label sets failed monitor gates." | Do not claim direct 50-state Bishan scale-up success. |
| Literature framing | "JEPA, MPC, world-model, and value-function references motivate the method family." | Do not cite external papers as evidence for Paper10's local results. |

## Files to update after author decisions

| decision | required file updates |
|---|---|
| Target journal and article type | Final manuscript, this policy, target-venue checklist, blocker packet, and README submission notes. |
| Final citation policy | `references/paper10_citation_map_2026-06-09.md`, BibTeX files, final manuscript, and bibliography export. |
| Public Paper9 route | Local-source status note, Methods text, final bibliography, and Data/Code Availability if supplementary methods or code/data supplement is used. |
| Preprint policy | Citation map, verified BibTeX, Introduction, Discussion, and final bibliography. |
| Statistical reporting policy | Integrated tables, Results text, figure captions, source-data map, and final manuscript. |
| Formal statistical tests | Analysis script, source-data map, reproducibility guide, table captions, and final manuscript. |

## Preflight interpretation

Passing preflight with this policy means the repository has an explicit current
rule for citation and statistical-reporting boundaries. It does not mean the
final target-journal reference style or inferential statistical plan has been
selected.
