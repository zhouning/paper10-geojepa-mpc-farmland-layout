# Paper10 caption-claim handoff

Date: 2026-06-19

## Current save point

- Branch: `paper10-original-vision-validation`
- Upstream: `origin/paper10-original-vision-validation`
- Remote: `https://github.com/zhouning/paper10-geojepa-mpc-farmland-layout.git`
- Latest pushed commit before this handoff note:
  `a3ea6a4757485aef59721446cbc196cebe0d0f5f`
- Commit subject:
  `test: add figure table caption claim packet`
- Worktree:
  `D:/test/paper10-geojepa-mpc-farmland-layout/.worktrees/paper10-original-vision-validation`

## What was completed

The current session added a source-derived figure/table caption-claim packet for
the formal Paper10 manuscript route. It converts the source-covered figure/table
assembly map into journal-neutral draft captions, allowed claims, forbidden
claims, and unresolved manuscript fields.

Primary new artifacts:

- `paper10_geojepa_mpc/experiments/figure_table_caption_claim_packet.py`
- `paper10_geojepa_mpc/tests/test_figure_table_caption_claim_packet.py`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_caption_claim_packet_2026-06-19.json`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_caption_claim_packet_2026-06-19.md`

Preflight integration:

- `scripts/paper10/preflight_submission_checks.py`
  now includes `paper10_figure_table_caption_claim_packet_current`.
- `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  now requires the caption-claim packet in the current repository and minimal
  fixture.

Cross-linked public/reproducibility docs:

- `README.md`
- `REPRODUCIBILITY.md`
- `DATA_AVAILABILITY.md`
- `MANIFEST.md`
- `paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`

## Evidence and boundaries

No rollout was rerun. No new experimental claim was added.

The caption-claim packet is derived from:

- `e0_paper10_figure_table_source_coverage_audit_2026-06-19.json`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`

The packet covers these items in order:

1. Main Figure 1
2. Main Figure 2
3. Main Figure 3
4. Main Figure 4
5. Supplementary Figure S1
6. Main Table 1
7. Main Table 2
8. Main Table 3

Current rigorous claim boundaries:

- Bishan 20x16/top5 is the positive anchor under the tested matched rollout
  protocol.
- Stage 3 50-state rows are boundary evidence, not direct scale-up success.
- The diagnostic near-pass must not be pooled with confirmatory rows.
- Dongxing/Neijiang supports calibration and stress-test value, not robust
  Bishan-to-Dongxing transfer superiority.
- Real-environment smoke reports are execution-chain evidence, not
  short-horizon planning-quality evidence.
- The manuscript is still not submission-ready.

## Last verification

Fresh verification performed before this handoff:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_figure_table_caption_claim_packet.py paper10_geojepa_mpc\tests\test_submission_preflight.py paper10_geojepa_mpc\tests\test_manuscript_text_table_consistency_audit.py -q -p no:cacheprovider
```

Result: `40 passed`.

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Result: `220 passed`.

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Result: `Paper10 preflight: PASS`, 35 checks.

## Recommended next task

The next rigorous step should move from caption-ready evidence control toward a
real manuscript file, but only after preserving claim boundaries. Recommended
options:

1. Create a journal-neutral formal manuscript draft assembled from the blueprint,
   result-table freeze, text/table consistency audit, source coverage audit, and
   caption-claim packet.
2. Alternatively, close one remaining blocker first: target journal/article
   type, final figure export rules, or Main Figure 1 final schematic artwork.
3. If running new experiments, prioritize a predeclared comparator or real-data
   rerun plan rather than adding ad hoc positive claims.

Do not claim submission readiness until target venue, article type, repository
identifier/reviewer route, licences, full data-access routes, final figures,
caption lengths, and table placement are closed and preflight is updated.
