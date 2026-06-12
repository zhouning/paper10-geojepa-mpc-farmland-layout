# Paper10 CEUS Reviewer Handoff

Date: 2026-06-12

This note records the current Paper10 CEUS-reviewer improvement state before
shutdown. It is a handoff note only. It does not replace the manuscript control
files under `paper10_geojepa_mpc/experiments/results/`.

## Current Objective

Prepare Paper10 for a CEUS Research Article candidate route while preserving a
self-contained Paper10 Methods route because Paper9 has not been formally
submitted.

## Work Completed In This Session

- Added `paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md`.
- Updated the integrated manuscript scaffold to include CEUS-facing hooks for:
  - block-level planning-unit abstraction;
  - irregular cadastral parcel boundary;
  - area-tolerance matching;
  - shared-perimeter-weighted contiguity;
  - soft training and hard inference;
  - no Constrained MDP, CPO, or RCPO implementation claim;
  - Dongxing `candidate-value-weight=1.0` as planner calibration evidence.
- Cross-linked the CEUS packet from README, MANIFEST, DATA_AVAILABILITY,
  REPRODUCIBILITY, the submission blocker packet, and the with-Dongxing
  target-venue checklist.
- Added preflight guard `ceus_reviewer_improvement_packet_current` in
  `scripts/paper10/preflight_submission_checks.py`.
- Extended `paper10_geojepa_mpc/tests/test_submission_preflight.py` so the new
  preflight guard must pass.

## Data Found Under D:\test

Do not copy these large or restricted data files into Git. Use them only for
local reruns or for archive planning after rights are confirmed.

| data family | local path | role |
|---|---|---|
| Full Bishan transitions | `D:\test\tool2\transitions.npz` | Full Bishan value-head training and rollout reruns. |
| Full Bishan pairwise data | `D:\test\tool2\pairwise.npz` | Full checkpoint scoring and value-head metadata. |
| Bishan GPKG root | `D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg` | GPKG-root real-environment reproduction. |
| Bishan block products | `D:\test\results_real\blocks` | Full Bishan real-environment rollout inputs. |
| Bishan township file | `D:\test\townships.json` | Full prepared data route input. |
| Bishan shapefile | `D:\test\bishan.shp` | Optional future parcel-geometry audit after rights check. |
| Dongxing shapefile | `D:\test\dongxing.shp` | Optional future parcel-geometry audit after rights check. |
| Neijiang wrapper/data | `D:\test\neijiang_cross_region` | External-region Dongxing/Neijiang experiments. |

## Claim Locks

- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim direct 50-state Bishan scale-up success.
- Do not claim shared-perimeter-weighted contiguity has been evaluated.
- Do not claim a Constrained MDP, CPO, or RCPO implementation.
- Do not cite Paper9 publicly until it has a public preprint, article, or
  supplement.
- Keep statistics descriptive unless a formal statistical-analysis plan is
  added.

## Latest Verification

Fresh commands run from `D:\test\paper10-geojepa-mpc-farmland-layout`:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
git diff --check
```

Results:

- `133 passed in 66.27s`
- `Paper10 preflight: PASS`, 17 checks including
  `ceus_reviewer_improvement_packet_current`
- `git diff --check` exit code 0; only LF/CRLF warnings were reported

## Current Git State

There are many modified and untracked files from the broader Paper10 submission
work. Do not revert them. The key new file from this session is:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md
```

Previously created untracked integrated Dongxing/control files are still
untracked and required by current preflight checks.

## Suggested Next Step

When resuming, start by running:

```powershell
git status --short
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Then continue with the next manuscript-level task: convert the integrated
scaffold into a CEUS-facing final manuscript draft, using
`e0_ceus_reviewer_improvement_packet_2026-06-12.md`,
`e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`,
and `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`.
