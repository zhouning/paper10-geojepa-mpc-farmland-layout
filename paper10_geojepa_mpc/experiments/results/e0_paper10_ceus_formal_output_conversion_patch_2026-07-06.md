# Paper10 CEUS formal-output conversion patch

Date: 2026-07-06

Status: formal-output conversion patch, not a final submission package.

Purpose: convert the CEUS baseline-hardened manuscript assembly into a cleaner journal-facing manuscript while preserving the current no-go submission boundary.

## One-sentence argument

In constrained farmland layout planning, GeoJEPA-MPC provides an evidence-controlled planning-support workflow by combining monitor-gated value labels with executable rollout masks; the evidence supports a descriptive Bishan 20x16/top5 matched 5-seed reward anchor and identifies Stage 3, Dongxing/Neijiang and cadastral-deployment boundaries.

## Preferred title

Monitor-gated value labels for evidence-controlled GeoJEPA-MPC farmland layout planning

## Alternate titles

1. Evidence-controlled value filtering for GeoJEPA-MPC farmland layout planning
2. Monitor-gated value labels and executable masks for farmland layout planning
3. Bounded GeoJEPA-MPC planning support for constrained farmland layout

## CEUS highlights file

Use `e0_paper10_ceus_highlights_2026-07-06.txt` as the separate editable highlights file.

| chars | highlight |
|---:|---|
| 68 | Monitor gates control value-label escalation for farmland layout planning. |
| 70 | Bishan 20x16/top5 gives a descriptive matched 5-seed reward anchor. |
| 67 | Value filtering wins 3/5 seeds, so superiority remains descriptive. |
| 58 | Executable masks prevent invalid zero-swap rollout behavior. |
| 66 | Stage 3 and Dongxing tests define scale and calibration boundaries. |

## Abstract for formal conversion

Constrained farmland layout planning requires sequential spatial decisions for which local feasibility and finite-horizon value can diverge. We present a monitor-gated GeoJEPA-MPC workflow that generates finite-horizon value labels, screens label quality before value-head training and enforces executable actions during rollout. In Bishan, the 20x16/top5 value filter was evaluated against the matched Paper9 `rank_seed2028` comparator under the same H=5, K=50 and executable-mask protocol. Across seeds 0-4, mean 100-step reward was 69.4705 for the value-filter policy and 67.5437 for the comparator, with sample standard deviation 1.0004 versus 7.2246. The seed-wise outcome was mixed: value filtering won 3/5 seeds and lost seeds 0 and 4, so the result is reported descriptively. Removing the executable mask reduced mean reward to 40.3515 and produced 100 zero-swap steps and 98 negative zero-swap steps, identifying executable masking as necessary for valid rollout behavior under the current protocol. An ungated top-4 control did not separate from the gated anchor, so the monitor gate is framed as label-quality evidence control rather than a separately proven online reward-gain mechanism. Stage 3 50-state rows, a 50x24 candidate-score sweep and Dongxing/Neijiang stress tests further bound the claim to calibrated planning support, not broad scale-up, transfer superiority or operational cadastral deployment.

## Cover-style significance summary

This manuscript addresses a practical bottleneck in learned agricultural planning: a candidate swap can be executable locally but still poor over a finite planning horizon, while learned value labels can become misleading if they are generated without quality control. Paper10 contributes a monitor-gated value-label workflow and an executable-mask rollout protocol for GeoJEPA-MPC farmland layout planning. The evidence is deliberately bounded: Bishan provides a descriptive matched 5-seed reward anchor, executable-mask ablation identifies a necessary validity control, and Stage 3 plus Dongxing/Neijiang experiments show where larger label sets and transfer claims remain unsupported. This framing should be presented as planning-support and reproducibility evidence for CEUS readers.

## Main-manuscript cleanup map

| current assembly item | formal manuscript destination |
|---|---|
| Source controls used for this draft | move to supplementary provenance note or archive README |
| One-Sentence Argument | remove from manuscript body; retain as author checklist |
| Terminology Ledger | move to supplementary methods note if needed |
| Title | keep on title page |
| Highlights | submit as separate editable highlights file |
| Abstract and Keywords | keep in main manuscript |
| Introduction, Methods, Results, Discussion, Conclusion | keep in main manuscript after final copyedit |
| Data and Code Availability | keep, but backfill DOI, licence and access routes before submission |
| Figure and Table List | convert into final figure/table files, captions and source-data metadata |
| Claim-Evidence and Unresolved Blockers | move to supplementary review-risk checklist; do not keep in main article body |
| Author Handoff Notes | remove from submission manuscript |

## Section-level edit instructions

### Front matter

- Use the preferred title unless the author team chooses a shorter version.
- Keep keywords to 1-7 English terms.
- Submit the five highlights as a separate editable file.
- Add title-page metadata: author names, affiliations, corresponding author, present addresses if needed, funding, acknowledgements, competing interests, CRediT roles and AI-use disclosure if applicable.

### Introduction

- Keep the application-first funnel: farmland layout problem, sequential planning bottleneck, value-label quality-control gap, GeoJEPA-MPC workflow.
- Make the prior-work contrast specific to planning support and value-label control. Do not imply Paper10 invented GeoJEPA.
- End with the bounded evidence ladder rather than a broad superiority claim.

### Methods

- Keep the order: task formulation, state/action/reward, executable masks, GeoJEPA-MPC value filtering, monitor gate, Bishan/Stage 3 protocol, Dongxing/Neijiang protocol and reporting policy.
- State that reward/count penalties guide training labels, while executable masks and paired inference enforce rollout feasibility.
- Avoid naming the implementation as a full Constrained MDP, CPO or RCPO solver.

### Results

- Lead with monitor-gate selection, then Bishan 20x16/top5, Stage 3 boundary, mechanism ablation and Dongxing/Neijiang calibration.
- Report Bishan reward as descriptive: mean 69.4705 versus 67.5437, sample standard deviation 1.0004 versus 7.2246 and paired mean delta 1.9269.
- Include seed deltas -3.2408, 3.6137, 8.4242, 9.0620 and -8.2248 so readers see the mixed seed-wise outcome.
- Keep the diagnostic-only sign-test readout out of superiority language.
- Report secondary metrics as mixed: slope and baimu-area means align, while contiguity has a small tradeoff.

### Discussion and Conclusion

- Interpret the work as evidence-controlled planning support.
- Name the key failure modes: mixed seed outcomes, 50-state boundary rows, monitor gate not isolated as an online reward mechanism, and second-region calibration rather than transfer superiority.
- Keep the cadastral-deployment limitation explicit: the current evidence uses block-level planning units and queen contiguity, not arbitrary irregular parcel exchange with area-tolerance matching and shared-perimeter topology.

## Data and Code Availability backfill template

Use this structure after author decisions are closed:

1. Code/evidence archive: name the repository archive, DOI or anonymous reviewer link, exact commit hash, software licence and access date.
2. Included reviewer evidence: list smoke data, generated value labels, monitor outputs, rollout summaries, figure-source CSV files, checkpoints and metadata included in the archive.
3. External Bishan Tool2 data: give public repository DOI or controlled-access metadata record, access owner, eligibility, review process, reviewer access route and data-use terms.
4. GPKG-root geospatial inputs: give public repository DOI or controlled-access metadata record for slope-enriched geospatial inputs, block products and township inputs.
5. Dongxing/Neijiang prepared data: give public repository DOI or controlled-access metadata record for prepared block, parcel, trajectory and environment-wrapper files.
6. Generated outputs and checkpoints: state redistribution terms and any restrictions on model weights.
7. Source-data map: bind each figure and table to tracked source files.

## Figure and table export package

| item | required formal-output action |
|---|---|
| Main Figure 1 | finalize editable workflow schematic; export separate PDF/EPS and preview PNG |
| Main Figure 2 | export Bishan matched 5-seed reward/stability figure from locked source data |
| Main Figure 3 | export Stage 3 boundary figure or table-linked panel |
| Main Figure 4 | export Dongxing return-label scaling figure from tracked CSV |
| Tables 1-3 | submit as editable text tables with captions and notes |
| Supplementary Figure S1 | export Dongxing low-label stress-test figure |
| Supplementary Tables S1-S3 | submit seed-level, low-label and mechanism-ablation tables as editable text |

## Supplementary-material map

- Supplementary Note 1: source-control and provenance register.
- Supplementary Note 2: monitor-threshold and label-quality diagnostics.
- Supplementary Table S1: Stage 3 seed-level rollout rewards.
- Supplementary Table S2: Dongxing low-label transfer stress test.
- Supplementary Table S3: mechanism ablation and control comparison.
- Supplementary Data: figure-source CSVs and result JSON files that are small enough for archive inclusion.

## Do-not-cross claim boundary

- No inferential superiority from the current 5-seed Bishan result.
- No uniform seed-wise improvement claim.
- No direct 50-state scale-up claim.
- No robust Bishan-to-Dongxing transfer-superiority claim.
- No deployment-ready irregular cadastral parcel claim.
- No full constrained-RL solver claim.

## Immediate manuscript edits already applied

- The assembly draft highlights were reduced from seven bullets to five CEUS-length bullets.
- A separate editable highlights text file was added.
- Markdown heading spacing was repaired before Section 3.3 and before Data and Code Availability.

## Remaining non-authorial work before formal output

- Generate and inspect final figure files.
- Convert the cleaned manuscript into editable Word or LaTeX source.
- Verify reference keys and final CEUS reference style.
- Run spelling, grammar, figure-number and table-number checks.
- Rerun preflight and targeted tests after the DOI, licence, data-route and figure-export backfill.
