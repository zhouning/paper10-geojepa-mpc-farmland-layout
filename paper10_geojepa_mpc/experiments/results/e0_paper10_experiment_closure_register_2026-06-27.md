# Paper10 experiment-closure register

Date: 2026-06-27

Status: closure_register

This register turns the 2026-06-27 experiment-freeze audit into concrete
closure decisions for the bounded Paper10 manuscript route. It does not rerun
experiments, does not add a new experimental claim, and does not replace the
author-decision matrix or data-rights register.

## Source basis

- `e0_paper10_experiment_freeze_audit_2026-06-27.md`
- `e0_paper10_author_decision_matrix_2026-06-18.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`

## Default closure decisions

| topic | default decision for the next writing pass | status | algorithm work needed |
|---|---|---|---|
| Manuscript route | Keep CEUS Research Article as the working route unless the author selects a different venue. | carry_forward | no |
| Central comparator | Use matched Paper9 `rank_seed2028` as the named comparator with rollout settings stated in Methods and table notes. | default_frozen | no |
| Pairwise-only baseline | Do not add a new pairwise-only baseline unless the author deliberately changes the comparator policy. | deferred | no |
| Statistical reporting | Use descriptive reporting only: mean, sample standard deviation, min, max, seed count, checkpoint and rollout settings. | default_frozen | no |
| Inferential tests | Do not add p-values, confidence intervals, superiority, non-inferiority, or equivalence wording without a new predefined plan. | blocked_without_plan | optional only |
| Bishan positive anchor | Keep Bishan 20x16/top5 as the sole positive performance anchor. | frozen | no |
| Stage 3 50-state rows | Keep the tested 50-state rows as boundary evidence below the matched comparator. | frozen | no |
| Dongxing/Neijiang | Use as calibration and stress-test evidence only. | frozen | no |
| Executable mask mechanism | Keep executable masks as the strongest mechanism evidence. | frozen | no |
| Monitor gates | Describe monitor gates as value-label quality control rather than as an isolated reward-improvement mechanism. | frozen | no |
| Real-data warnings | Document libpysal connectivity and guarded divide warnings unless a later cleanup task is explicitly opened. | carry_forward | optional |
| Figure/table export | Keep the current export contract: Figures 2-4, S1, and Tables 1-3 are export-ready; Main Figure 1 artwork remains pending. | partially_closed | no algorithm work |
| Data and rights | Keep repository DOI, licence, full Bishan, GPKG-root, Dongxing/Neijiang, and generated-output rights as author or institutional decisions. | open_blocker | no algorithm work |

## Experiment work policy

| possible next action | do now? | reason |
|---|---|---|
| Re-run full Bishan 20x16/top5 anchor | no by default | Windows real-data reproduction already matched canonical labels, checkpoint, and rollout aggregate. |
| Add more rollout seeds for descriptive robustness | optional | Useful only if the author wants stronger descriptive stability before manuscript conversion. |
| Add formal statistical tests | no by default | Requires a predefined analysis plan and source-data mapping. |
| Tune 50x24 candidate-score weights again | no | The 2026-06-20 sweep did not recover the matched comparator. |
| Redesign candidate generation or value-label training | no by default | Needed only for a stronger 50-state track. |
| Build Dongxing/Neijiang full rerun pipeline | no by default | Needed only for a stronger transfer track or if the target venue requires full external-region reruns. |
| Add irregular cadastral parcel constraints | no by default | Needed only for an operational deployment claim. |
| Produce Main Figure 1 artwork | yes before final manuscript packaging | This is a figure task, not an algorithm task. |
| Fill data-access and rights fields | yes before final manuscript packaging | This is an author or institutional route task, not an algorithm task. |

## Manuscript-entry gate

| gate | current reading | action |
|---|---|---|
| Algorithm boundary | Freeze candidate for the bounded route. | Do not modify broad algorithm behavior. |
| Experiment boundary | Sufficient for a bounded planning-support workflow manuscript draft. | Write inside the frozen claim boundary. |
| Submission boundary | No-go boundary remains active. | Keep DOI, licence, data routes, statistics policy, and figure export blockers visible. |
| Stronger-claim boundary | Not sufficient for broad scale, transfer, or deployment claims. | Re-enter algorithm development only if the author chooses that track. |

## Immediate manuscript assembly order

1. Update the Methods text around comparator, mask enforcement, monitor-gated
   value labels, and descriptive reporting.
2. Update the Results text from the frozen tables: Bishan anchor, mechanism
   ablation, Stage 3 boundary, and Dongxing calibration.
3. Update Discussion and limitations to state why 50-state, transfer, and
   deployment claims remain bounded.
4. Prepare Main Figure 1 artwork and reuse the frozen source maps for the
   remaining figures and tables.
5. Backfill data/code availability fields only after the repository, licence,
   and restricted-data routes are selected.
6. Run preflight, full tests, and `git diff --check` after manuscript edits.

## Current answer to the author question

Paper10 should not continue broad algorithm improvement by default. It should
continue with experiment closure and bounded manuscript assembly. More
computational experiments are optional only for stronger descriptive support,
and required only if the author chooses a stronger 50-state, transfer, or
operational-deployment claim track.