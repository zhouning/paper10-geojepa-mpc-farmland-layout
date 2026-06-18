# Paper10 author decision and formal-submission conversion matrix

Date: 2026-06-18

Status: author-decision control document. This file translates the current
Paper10 proposal report and CEUS Stage 3 manuscript draft into concrete
author decisions that must be closed before a formal journal submission
package can be declared ready. It is not a final manuscript, not a data
availability statement, and not a substitute for institutional data-rights
approval.

Source basis:

- `e0_paper10_project_proposal_opening_report_2026-06-18.md`
- `e0_ceus_stage3_manuscript_draft_2026-06-18.md`
- `e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_paper10_real_data_availability_audit_2026-06-18.md`

## One-sentence conversion argument

Paper10 can move from a temporary project-proposal/opening-report package to a
formal submission package only after the author team freezes the comparator,
repository, licence, data-access, citation, statistical-reporting, and figure
export decisions while preserving the current claim boundary: Bishan
20x16/top5 is the positive anchor, Stage 3 50-state rows are scale-boundary
evidence, and Dongxing/Neijiang is calibration and stress-test evidence rather
than robust transfer-superiority evidence.

## Decision matrix

| decision | recommended default | acceptable alternatives | must not choose | files to update after decision | close-out evidence |
|---|---|---|---|---|---|
| Target venue and article type | Use a computational geography, land-use planning, or environmental modelling research-article route; CEUS remains the current working target. | Methods/reproducibility route if the authors want to emphasize workflow, source-data mapping, and failure-mode transparency. | Broad Nature-family route without stronger data-access, source-data, and generality support. | Final manuscript; `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`; README submission notes. | Journal name, article type, abstract format, word limit, figure/table limit, reference style, anonymity policy, and source-data rule recorded. |
| Comparator and pairwise-only baseline policy | Accept matched Paper9 `rank_seed2028` as the current comparator for the Stage 3 CEUS route, with self-contained Paper10 Methods wording because Paper9 is not public. | Run and report a separately named pairwise-only baseline before final manuscript conversion. | Mix matched Paper9 and pairwise-only labels without naming the comparator or rollout protocol. | CEUS manuscript Methods/Results; proposal report if updated; `e0_submission_blocker_decision_packet_2026-06-11.md`; source-data map. | Comparator name, checkpoint, rollout settings, seed count, and rationale recorded in Methods and table notes. |
| Repository DOI or reviewer link | Archive the exact submission commit and create an anonymous reviewer link if the target journal supports anonymous review. | Public DOI before submission; private journal-approved review link. | Vague personal cloud or drive-link route. | `DATA_AVAILABILITY.md`; `e0_data_code_availability_draft_2026-06-09.md`; archive manifest; final manuscript. | Persistent DOI or reviewer URL, commit hash, version date, access window, and anonymity status recorded. |
| Code licence | Use a standard named software licence after confirming all included code can be licensed by the authors. | Institution-approved restricted code-use statement. | Imply open-source reuse before rights are confirmed. | Repository licence file if added; `MANIFEST.md`; rights register; archive metadata. | Licence text or restriction statement committed and cited in Data and Code Availability. |
| Generated-output and checkpoint rights | Assign rights terms for generated Markdown, JSON, CSV, NPZ labels, figure source data, checkpoints, and model weights separately from raw geospatial data. | Restrict checkpoints while releasing scripts and derived source-data tables. | Re-license restricted raw data through generated-output wording. | Data/code availability draft; archive metadata templates; rights register. | Rights terms list each artifact family and explicitly separate generated outputs from external raw data. |
| Full Bishan Tool2 access route | Use controlled-access metadata if redistribution rights are uncertain. | Public DOI if rights allow; institutional request route with named access body. | Vague request-only wording without eligibility, review, response expectation, and use terms. | `DATA_AVAILABILITY.md`; data availability draft; rights register; final manuscript. | Access owner, eligibility, review criteria, reviewer route, response expectation, and data-use terms recorded. |
| GPKG-root geospatial input route | Assign the prepared `DLTB_with_slope.gpkg`, block products, and township inputs to the same controlled/public route family as full Bishan where possible. | Separate controlled route for GPKG-root prepared inputs. | State that full reruns are reproducible from Git alone. | `REPRODUCIBILITY.md`; Data Availability; data availability draft; final manuscript. | Exact file family, route, reviewer access, and rerun dependency note recorded. |
| Dongxing/Neijiang prepared-data route | Use controlled-access metadata unless the authors can publish the 3711-block products and 76,376 parcel assignments. | Public DOI if rights allow. | Treat derived summary CSVs as sufficient for full external-region reruns. | Data availability draft; source-data map with Dongxing; rights register; final manuscript. | Route covers prepared blocks, parcel assignments, transitions, pairwise labels, environment wrappers, and slope-enriched inputs. |
| Citation policy | Keep public manuscript citations to verified public sources and use the self-contained Paper10 Methods route while Paper9 is not public. | Formalize Paper9 if it becomes submitted/public before final conversion. | Cite the local-only placeholder key `zhou2026paper9_local` in public manuscript text. | Citation/statistics policy; citation map; BibTeX files; Methods; final manuscript. | Public manuscript contains no unresolved local-only placeholder and all citation keys resolve. |
| Statistical reporting policy | Keep descriptive means, sample standard deviations, minima, maxima, seed/checkpoint counts, and condition-specific comparisons. | Add formal tests only with a predefined analysis plan and source-data mapping. | Use inferential-statistics wording without a plan. | Citation/statistics policy; Results; captions; tables; final manuscript. | Statistical policy is recorded and all inferential terms are either absent or backed by a committed analysis plan. |
| Final figure/table export package | Preserve the current figure/table numbering freeze, then adapt only after target-venue limits are known. | Move panels between main and supplementary files if journal limits require it. | Change figure/table numbering without updating the freeze, source-data map, and captions together. | Figure exports; source-data maps; figure/table freeze; table package; final manuscript. | Export dimensions, format, source-data names, captions, and supplementary placement are recorded. |
| Claim boundary | Use monitor-gated value filtering as the contribution; Bishan 20x16/top5 as the positive anchor; Stage 3 50-state rows as boundary evidence; Dongxing as calibration/stress test. | Narrow further to a methods/reproducibility claim if target venue requires stronger caution. | Claim direct 50-state Bishan scale-up success, robust Bishan-to-Dongxing transfer superiority, solved irregular parcel deployment, or a full Constrained MDP/CPO/RCPO solver. | Title, abstract, Results, Discussion, conclusion, proposal report, captions, reviewer response materials. | Final public text contains the guardrail wording and no prohibited positive claim. |

## Recommended decision order

1. Freeze target venue and article type.
2. Freeze comparator and pairwise-only baseline policy.
3. Freeze repository DOI or reviewer-link route.
4. Freeze code licence and generated-output/checkpoint rights.
5. Freeze full Bishan, GPKG-root, and Dongxing/Neijiang data-access routes.
6. Freeze citation policy and Paper9 public-route handling.
7. Freeze statistical reporting policy.
8. Freeze final figure/table export package.
9. Run the final claim-boundary sweep and preflight.

This order prevents circular editing. For example, target venue determines
anonymity and figure limits; data-access route determines Data Availability;
statistics policy determines Results wording; comparator policy determines
the central Bishan and Stage 3 tables.

## Default manuscript route if no new author decision arrives

If the author team cannot close new decisions immediately, the safest next
writing route is:

- keep the CEUS Research Article candidate route as working target;
- keep matched Paper9 `rank_seed2028` as the explicitly named comparator;
- keep reporting descriptive means and sample standard deviations only;
- keep Paper9 out of public manuscript citations and use the self-contained Paper10 Methods route;
- keep full Bishan, GPKG-root, and Dongxing/Neijiang data access as unresolved
  blockers rather than implying they are already deposited; use
  `e0_paper10_real_data_availability_audit_2026-06-18.md` to separate local
  path availability from rights and repository-access decisions;
- keep the proposal report as temporary立项/开题 material, not a submission file.

This route supports continued drafting but does not authorize final
submission. Final submission remains blocked until repository, licence,
data-access, citation, statistical, and export decisions are closed.

## Claim-evidence locks for conversion

| claim | current evidence | allowed wording | blocked wording |
|---|---|---|---|
| Bishan positive anchor | 20x16/top5 mean reward `69.4705`; matched Paper9 baseline `67.5437`; sample standard deviation `1.0004` versus `7.2246`. | The validated Bishan 20x16/top5 value filter improved reward and seed-level stability under the tested rollout protocol. | Do not claim universal planner superiority or all-indicator improvement. |
| Stage 3 50-state boundary | `64.2960` and `66.2544` mean rewards for the two confirmatory rows, both below baseline. | Stage 3 completed 50-state rollouts but did not support direct positive scale-up under the matched comparator. | Do not claim direct 50-state Bishan scale-up success. |
| Diagnostic near-pass | `67.4913` mean reward, `-0.0524` below baseline. | The near-pass row is useful diagnostic context and must not be pooled with confirmatory rows. | Do not use the near-pass row to strengthen the confirmatory 50-state claim. |
| Dongxing/Neijiang calibration | Return-label scaling improves both transfer and scratch families; scratch remains stronger at 50x16 and at 5/10 low-label budgets. | Dongxing/Neijiang supports calibration and stress-test value. | Do not claim robust Bishan-to-Dongxing transfer superiority. |
| Deployment boundary | Current evidence uses block-level planning-unit abstraction and queen contiguity. | Irregular cadastral deployment requires area-tolerance matching, shared-perimeter-weighted contiguity, and parcel geometry constraints. | Do not claim solved irregular cadastral parcel deployment. |

## Completion checklist

- [ ] Target venue and article type are named.
- [ ] Comparator and pairwise-only baseline policy are frozen.
- [ ] Repository DOI or reviewer link is recorded.
- [ ] Code licence is selected or restriction statement is written.
- [ ] Generated-output and checkpoint rights are recorded.
- [ ] Full Bishan Tool2 data route is recorded.
- [ ] GPKG-root geospatial input route is recorded.
- [ ] Dongxing/Neijiang prepared-data route is recorded.
- [ ] Citation policy is frozen and public text has no local-only placeholder.
- [ ] Statistical reporting policy is frozen.
- [ ] Final figure/table export package is frozen.
- [ ] Claim-boundary sweep passes.
- [ ] `D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider` passes.
- [ ] `D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py` passes.
- [ ] `git diff --check` passes.

## Handoff note

Passing repository preflight with this decision matrix means the decision
surface is explicit and claim-bounded. It does not mean the author has made the
decisions, and it does not mean the paper is ready for final submission.
