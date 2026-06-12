# Paper10 Original-Vision Validation Handoff

Date: 2026-06-12

This note records the current Paper10 state before shutdown. It is a handoff
note for continuing the research-validation task. It does not replace the
manuscript control files under `paper10_geojepa_mpc/experiments/results/`.

## Current User Direction

The user rejected an overly strong claim that the original Paper10 vision could
not fully land. The correct research stance is:

- Current evidence is not sufficient to support the strongest original vision.
- Current evidence also does not disprove the original vision.
- The next task is to validate the original vision rigorously with predefined
experiments, rather than narrowing claims by assumption.

The user approved focusing first on:

1. value-label / monitor-gate validity, especially larger label settings; and
2. cross-region transfer versus local calibration.

Irregular parcel deployment and topology extensions remain important, but are
secondary to the first validation pass.

## Work Completed In This Session

- Created CEUS Research Article candidate manuscript draft:
  `paper10_geojepa_mpc/experiments/results/e0_ceus_research_article_manuscript_draft_2026-06-12.md`.
- Added a new preflight guard:
  `ceus_research_article_manuscript_draft_current`.
- Extended `paper10_geojepa_mpc/tests/test_submission_preflight.py` so the new
  guard must pass.
- Linked the CEUS manuscript draft from `README.md`, `MANIFEST.md`,
  `DATA_AVAILABILITY.md`, and `REPRODUCIBILITY.md`.
- Reframed the scientific stance: the CEUS draft is a conservative, defensible
  manuscript route, not a verdict against the larger original vision.

## Current Hardware Assessment

Windows workstation:

- CPU: Intel Core Ultra 9 185H, 16 cores / 22 logical processors.
- Memory: about 32 GB total; about 15 GB free during the check.
- GPU: Intel Arc Graphics only; no visible NVIDIA GPU.
- PyTorch: `2.9.1+cpu`; `torch.cuda.is_available()` returned `False`.
- Disk: D drive has about 95 GB free; C drive has about 6 GB free.

Interpretation:

- Windows is suitable for CPU diagnostics, label-only monitor matrices, small
  value-head training checks, summaries, and limited rollout reproduction.
- Windows is not ideal as the sole runner for large multi-seed,
  multi-checkpoint, 100-step rollout matrices.
- Google Colab Pro+ should be used for the main batch experiments if a full
  validation matrix is required.
- macOS is useful for independent reproduction of selected key rows and
  platform/path sensitivity checks.

## Evidence and Timing Already Known

Local full data found:

- `D:\test\tool2\transitions.npz`: 1.52 GB.
- `D:\test\tool2\pairwise.npz`: 127 MB.
- `D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg`: 160 MB.
- `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`: 2.21 GB.
- `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`: 184 MB.

Useful prior timings:

- Bishan 20x16/top5 label generation in the packaged summary recorded
  `843.5874` seconds.
- A Windows real-data 20x16/top5 reproduction recorded label generation at
  about `218.4911` seconds.
- Bishan 20x16/top5 100-step rollouts took about `266-290` seconds per seed.
- Dongxing 3x5/h3 smoke label generation recorded about `44.9418` seconds.
- Dongxing smoke value-head training recorded about `1.4430` seconds.

Existing 50-state Windows ablation:

- `D:\test\paper10_runs\frontier_random050_ablation_summary.md`
- `D:\test\paper10_runs\frontier_random050_ablation_summary.json`
- `D:\test\paper10_runs\frontier_random050_ablation_posthoc_topk_summary.md`

The current seed46 50-state rows did not pass the monitor gate, including
post-hoc top-k checks through 12. This should be treated as evidence for the
tested rows only, not as proof that the original scale-up idea cannot work.

## Claim Discipline To Preserve

- Do not say the original vision cannot land unless a predefined validation
  matrix has tested and rejected it.
- Do say that the current CEUS draft cannot claim strong scale-up or robust
  transfer yet.
- Do not claim direct 50-state Bishan success from current evidence.
- Do not claim robust Bishan-to-Dongxing transfer superiority from current
  evidence.
- Do not add external optimizer baselines without a fair protocol covering
  optimizer choice, equal budgets, seeds, constraints, and metrics.

## Next Session Start Here

Run from `D:\test\paper10-geojepa-mpc-farmland-layout`:

```powershell
git status --short --branch
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Then create an original-vision validation design/spec that covers:

1. Hypotheses:
   - H1: larger value-label settings can pass monitor gates under some
     candidate proposal, seed, or top-k settings.
   - H2: value-label scaling improves rollouts beyond pairwise-only or
     no-value-filter baselines under matched rollout budgets.
   - H3: Bishan initialization helps Dongxing only under specific label-budget
     or calibration regimes, rather than robustly dominating scratch.
2. Windows first-pass experiments:
   - label-only monitor matrix for additional 50-state rescue candidates;
   - audit existing Dongxing transfer/scratch result files;
   - limited rollout sanity checks only where needed.
3. Colab Pro+ batch experiments:
   - train and roll out only rows that pass or nearly pass predefined monitor
     thresholds;
   - matched transfer versus scratch matrix;
   - value-filter and candidate-value-weight ablations.
4. macOS reproduction:
   - one positive Bishan row and one negative or near-pass 50-state row;
   - one selected Dongxing row if data transfer is practical.
5. Stop/go criteria:
   - what result is enough to keep the original strong theme;
   - what result forces the conservative CEUS theme;
   - what remains inconclusive.

## Verification At Handoff

Fresh command run before writing this note:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Result:

- `Paper10 preflight: PASS`
- 18 checks passed, including `ceus_research_article_manuscript_draft_current`.

Full test suite was also run earlier in the session after adding the CEUS draft
guard:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Result:

- `133 passed`

## Current Git Intent

This handoff should be committed together with the CEUS manuscript draft,
preflight guard, test assertion, and documentation index updates. If the
commit exists when the next session starts, continue from the validation-design
task above. If not, inspect `git status --short --branch` and preserve the
listed working-tree changes before running new experiments.
