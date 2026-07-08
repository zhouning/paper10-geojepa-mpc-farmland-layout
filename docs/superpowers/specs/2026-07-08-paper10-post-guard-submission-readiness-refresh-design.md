# Paper10 Post-Guard Submission-Readiness Refresh Design

## Purpose

Add a source-derived submission-readiness refresh after the July 8 post-guard
experiment-closure update. The refresh must separate algorithm/experiment
closure from final submission readiness, so the project can continue toward
publication without overstating that the manuscript is formally ready to
submit.

## Current Context

The current primary algorithm guard is the July 8 `rewardtop7 margin=1.50`
guard recorded in:

- `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.json`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_true_reward_guard_readiness_2026-07-08.md`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.json`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_experiment_closure_refresh_2026-07-08.md`

The current submission boundary remains `not_submission_ready`, with blockers
tracked in:

- `paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md`
- `paper10_geojepa_mpc/experiments/results/e0_data_access_and_rights_decision_register_2026-06-09.md`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_submission_readiness_boundary_2026-06-26.md`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_final_figure_table_export_package_2026-06-20.md`

## Required Artifact

Create a deterministic source-derived builder that writes:

- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.json`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_post_guard_submission_readiness_refresh_2026-07-08.md`

The artifact must record:

- date: `2026-07-08`;
- status: `not_submission_ready`;
- source boundary: no new experimental claim, no rollout rerun, no training
  rerun, no submission approval;
- algorithm state: post-guard bounded algorithm closure is current;
- submission state: final submission remains blocked;
- open author-decision fields:
  repository DOI or anonymous reviewer link, code licence, generated-data and
  checkpoint/model-weight rights, full Bishan Tool2 route, GPKG-root geospatial
  route, Dongxing/Neijiang prepared-data route, reviewer data access, citation
  policy, statistical reporting policy, and Main Figure 1 / journal export
  rules;
- claim locks: no final submission readiness, no direct 50-state success, no
  robust Bishan-to-Dongxing transfer superiority, no deployment-ready cadastral
  planning, and no universal fixed margin.

## Data Availability Discipline

The refresh must not invent repository identifiers, DOIs, licences, embargoes,
reviewer links, data owners, access committees, eligibility rules, review
criteria, response times, data-use agreements, or redistribution rights.

If a field is unresolved, it must remain explicitly unresolved. The artifact
may ask for author input, but it must not silently close a blocker.

## Preflight Gate

Extend `scripts/paper10/preflight_submission_checks.py` with a new check named:

`paper10_post_guard_submission_readiness_refresh_current`

The check must require the new JSON and Markdown artifact, verify the source
links and expected status values, require all unresolved author-decision fields,
and reject positive final-submission wording such as:

- `final submission-ready`
- `ready for final submission`
- `ready to submit`
- `all blockers closed`
- `submission_ready`

Negative guardrail wording such as `not_submission_ready`, `not final
submission readiness`, and `Do not treat this refresh as final submission
readiness` must be allowed.

## Tests

Use test-driven implementation.

Add builder tests that first fail because the new module does not exist, then
pass after the deterministic builder is implemented. The tests must verify JSON
values, Markdown tokens, source boundaries, author-decision fields, and claim
locks.

Add preflight tests that first fail because the new preflight names are absent,
then pass after the check is implemented. The tests must cover missing refresh
files, malformed or changed status values, positive final-submission overclaim
wording, and allowed negative guardrails.

## Out of Scope

Do not edit training, rollout, label-generation, plotting, or guard algorithm
code. Do not rewrite June historical records. Do not create a final submission
manuscript. Do not add a repository DOI, licence, data access route, or journal
export decision unless the author provides it explicitly.

## Success Criteria

- The new refresh artifacts are generated deterministically from tracked source
  files.
- Paper10 preflight passes with the new check registered.
- Full pytest passes.
- The repository remains on a bounded no-go submission boundary.
- `2503.05774v1.pdf` remains untracked and uncommitted.
