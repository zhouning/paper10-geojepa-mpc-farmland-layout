# Paper10 Current Handoff

Date: 2026-06-18

Branch: `paper10-original-vision-validation`

Remote tracking branch: `origin/paper10-original-vision-validation`

Current save point before this handoff update:
`d10fff40889b7c37ff24e683cab952514282e335`
(`docs: add paper10 project proposal report`)

## Current Workspace

Worktree:

```text
D:\test\paper10-geojepa-mpc-farmland-layout\.worktrees\paper10-original-vision-validation
```

GitHub repository:

```text
https://github.com/zhouning/paper10-geojepa-mpc-farmland-layout
```

Branch PR page:

```text
https://github.com/zhouning/paper10-geojepa-mpc-farmland-layout/pull/new/paper10-original-vision-validation
```

## Current Paper10 Position

Paper10 should now be framed as a bounded, reproducible
`monitor-gated value labels` / `value filtering` workflow for GeoJEPA-MPC
farmland layout planning.

Do not frame Paper10 as:

- direct 50-state Bishan scale-up success;
- robust Bishan-to-Dongxing transfer superiority;
- solved irregular cadastral parcel deployment;
- a full Constrained MDP, CPO, or RCPO solver.

The positive anchor remains Bishan `20x16/top5`:

- mean reward: `69.4705`;
- matched Paper9 baseline: `67.5437`;
- reward delta: `+1.9269`;
- sample standard deviation: `1.0004` versus baseline `7.2246`.

Stage 3 confirmatory 50-state rows completed rollout but did not beat the
matched baseline:

- `frontier_random050_50x16_h5_seed48_f050`, top-k 6, mean reward `64.2960`,
  delta `-3.2477`;
- `frontier_random050_50x24_h5_seed47_f075`, top-k 12, mean reward `66.2544`,
  delta `-1.2893`.

Diagnostic near-pass:

- `frontier_random050_50x24_h5_seed48_f075`, top-k 12, mean reward `67.4913`,
  delta `-0.0524`;
- must not be pooled with confirmatory rows.

Dongxing/Neijiang supports calibration and stress-test evidence, not robust
transfer superiority.

## Current User-Facing Outputs

Temporary project-proposal/opening-report substitute:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_project_proposal_opening_report_2026-06-18.md
```

Current CEUS Stage 3 manuscript draft:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_draft_2026-06-18.md
```

Current Stage 3 manuscript reframe/control layer:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_reframe_2026-06-18.md
```

Stage 3 rollout summary:

```text
paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md
paper10_geojepa_mpc/experiments/results/e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json
```

## Work Completed Since Original Stage 3 Plan

- Stage 3 confirmatory rollout summary was added and pushed.
- Stage 3 manuscript reframe was added and pushed.
- Full CEUS Stage 3 manuscript draft was added and pushed.
- Chinese Paper10 project-proposal/opening-report substitute was added and
  pushed for temporary topic approval before the formal paper is ready.
- `README.md` and `MANIFEST.md` now index the project-proposal report.
- Preflight now guards the CEUS Stage 3 manuscript draft.

## Remaining Blockers Before Formal Submission

- Pairwise-only baseline policy remains unresolved unless the author accepts
  matched Paper9 `rank_seed2028` as the comparator.
- Repository DOI or anonymous reviewer link is still needed.
- Software licence, generated-output rights, and model/checkpoint rights terms
  are still needed.
- Full Bishan Tool2, GPKG-root geospatial inputs, and Dongxing/Neijiang
  prepared data need public or controlled-access routes.
- Citation policy remains bounded by the fact that Paper9 has not been formally
  submitted.
- Formal inferential statistical language requires a predefined statistical
  plan; current evidence is descriptive.
- Final figure exports and source-data package remain to be closed.

## Last Verification

Run from:

```text
D:\test\paper10-geojepa-mpc-farmland-layout\.worktrees\paper10-original-vision-validation
```

Commands passed:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py paper10_geojepa_mpc\tests\test_original_vision_monitor_matrix.py paper10_geojepa_mpc\tests\test_original_vision_decision_packet.py paper10_geojepa_mpc\tests\test_dongxing_transfer_audit.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Observed results:

- `42 passed`
- `Paper10 preflight: PASS`

## Resume Instructions

1. Open the worktree above.
2. Run `git status --short --branch`.
3. Confirm the branch is `paper10-original-vision-validation`.
4. Start from the proposal report if the user asks for立项/开题材料.
5. Start from the CEUS Stage 3 manuscript draft if the user asks for paper
   drafting.
6. Preserve the claim boundaries above unless new verified evidence changes
   them.
