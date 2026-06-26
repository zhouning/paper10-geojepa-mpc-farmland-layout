# Paper10 Submission Readiness Boundary Design

Date: 2026-06-26

Status: design approved for implementation

Branch: `paper10-original-vision-validation`

Current saved commit before this design:
`257cdaf5a42729ea83744148b42ad8e3d86ded19`
(`test: guard paper10 mechanism ablation packet preflight`)

## 1. Purpose

Paper10 now has a claim-bounded CEUS manuscript route, a formal manuscript
draft, a final figure/table export contract, Stage 3 boundary evidence, and a
mechanism ablation packet. The repository preflight passes, but passing
preflight means the current evidence package is internally guarded; it does not
mean the manuscript is ready for final journal submission.

This design adds an explicit current submission-readiness boundary. The
boundary must make the current no-go status machine-checkable so future edits
cannot silently turn a draft-ready package into a claimed submission-ready
package.

## 2. Current Position

The allowed current route is:

- continue the CEUS Research Article conversion pass;
- keep the formal manuscript draft as the active paper-facing output;
- prepare figure/table exports under the frozen export contract;
- preserve the current claim boundary around the Bishan 20x16/top5 positive
  anchor, Stage 3 50-state boundary rows, Dongxing/Neijiang calibration and
  stress-test evidence, and the mechanism ablation packet.

The current package is not final-submission ready because the author team has
not closed all submission decisions.

## 3. Goals

The implementation should create a small, explicit no-go boundary artifact and
guard it through preflight.

The boundary should:

- state `not_submission_ready`;
- list the exact blockers that must remain visible before final submission;
- link the current source-basis files that justify the no-go boundary;
- identify allowed next actions that do not require changing the scientific
  claim;
- identify prohibited actions and overclaims;
- be included in the preflight check list as
  `paper10_submission_readiness_boundary_current`.

## 4. Non-Goals

This change must not:

- declare the manuscript ready for submission;
- create a new experimental result;
- rerun rollout or training code;
- change the formal manuscript scientific claim;
- solve DOI, licence, data-access, citation, or statistical-reporting decisions;
- finalize Main Figure 1 artwork or journal-specific figure dimensions;
- replace the existing submission blocker packet.

## 5. New Artifact

Create:

```text
paper10_geojepa_mpc/experiments/results/
  e0_paper10_submission_readiness_boundary_2026-06-26.md
```

The artifact should be Markdown because it is an author-facing boundary record.
No JSON companion is required for the first implementation. The preflight check
can validate fixed text sections directly, matching existing Markdown-only
checks such as the final figure/table export package.

## 6. Required Artifact Content

The Markdown boundary must include the following sections.

### Status

The status section must include the exact token:

```text
Status: not_submission_ready
```

It should also state that repository preflight passing does not mean final
submission readiness.

### Source Basis

The source basis must link these current files:

- `e0_paper10_formal_manuscript_draft_2026-06-20.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_paper10_final_figure_table_export_package_2026-06-20.md`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`

### Allowed Next Actions

The allowed action list should include:

- continue CEUS manuscript conversion;
- edit the formal manuscript draft within the current claim boundary;
- prepare figure/table exports under the frozen export contract;
- close author decisions for DOI, licence, data access, citation policy,
  statistical reporting, and journal-specific export rules.

### Submission Blockers

The blocker list must preserve these unresolved fields:

1. repository DOI or anonymous reviewer link;
2. code licence;
3. generated-data rights and checkpoint or model-weight rights;
4. full Bishan Tool2 data access route;
5. GPKG-root geospatial input access route;
6. Dongxing/Neijiang prepared-data access route;
7. citation policy for local-only sources, preprints, and final reference style;
8. statistical reporting policy for descriptive results versus hypothesis
   tests;
9. Main Figure 1 final schematic artwork and journal-specific figure/table
   export rules.

### Claim Locks

The claim-lock section must keep these forbidden conclusions out of the current
submission route:

- direct 50-state Bishan scale-up success;
- robust Bishan-to-Dongxing transfer superiority;
- solved irregular cadastral parcel deployment;
- full Constrained MDP, CPO, or RCPO solver;
- invented GeoJEPA.

### Preflight Meaning

The artifact must state that preflight passing means the boundary is tracked and
cross-linked, not that the paper is ready to submit.

## 7. Preflight Check

Add a check named:

```text
paper10_submission_readiness_boundary_current
```

The check should pass only if:

- the boundary artifact exists;
- the artifact includes `Status: not_submission_ready`;
- all required source-basis filenames are present;
- all nine submission blockers are present;
- the current final export package is referenced;
- the artifact includes the preflight-meaning distinction;
- public docs reference the boundary artifact from README, MANIFEST,
  REPRODUCIBILITY, and DATA_AVAILABILITY;
- the artifact does not contain positive submission-ready wording.

The check should fail if the artifact contains unqualified phrases such as:

- `Status: submission_ready`;
- `final submission-ready`;
- `ready for final submission`;
- `all blockers closed`;
- `direct 50-state Bishan scale-up success`;
- `robust Bishan-to-Dongxing transfer superiority`.

Negative guardrail phrasing is allowed when it is clearly prohibitive, for
example `Do not claim direct 50-state Bishan scale-up success`.

## 8. Documentation Updates

Add short cross-links to:

- `README.md`
- `MANIFEST.md`
- `REPRODUCIBILITY.md`
- `DATA_AVAILABILITY.md`

Each link should state that the boundary is the current no-go submission
readiness record and that it does not declare final submission readiness.

## 9. Testing Strategy

Use TDD for implementation.

First add failing tests in `paper10_geojepa_mpc/tests/test_submission_preflight.py`:

- current repository preflight includes
  `paper10_submission_readiness_boundary_current`;
- minimal fixture fails when the boundary artifact is missing;
- boundary check fails when `Status: not_submission_ready` is missing;
- boundary check fails when a required blocker is missing;
- boundary check rejects unqualified submission-ready wording;
- boundary check allows negative guardrail wording.

Then implement the artifact, constants, check function, check-list registration,
minimal fixture inclusion, and public-document cross-links.

## 10. Verification

Run focused verification:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected results:

- pytest passes;
- preflight prints `Paper10 preflight: PASS`;
- output includes `[ok] paper10_submission_readiness_boundary_current`.

## 11. Commit Plan

Use two commits:

1. `docs: add paper10 submission readiness boundary design`
2. `docs: guard paper10 submission readiness boundary`

The implementation commit should include only the boundary artifact, preflight
code, tests, and public-document cross-links.
