# Paper10 CEUS Baseline and Inference Hardening Design

Date: 2026-07-06

Status: design approved for implementation planning

Branch: `main`

Current saved commit before this design:
`802bcff5b9350f7aa3de3c3573adfa668d76505a`
(`test: lock post-5seed readiness boundary`)

## 1. Purpose

Paper10 is currently a bounded CEUS-route manuscript package. The strongest
positive evidence is the Bishan 20x16/top5 value-filter anchor, but the latest
matched 5-seed audit is mixed: the value-filter policy has higher mean reward
and lower sample standard deviation than the matched Paper9 baseline, while
winning only 3 of 5 seeds and losing seeds 0 and 4. Stage 3 50-state rows,
Dongxing/Neijiang transfer tests, and the ungated-top4 mechanism control further
prevent a broad scale-up or robust transfer claim.

This design adds a focused hardening pass for CEUS review risk. The goal is not
to tune the method until the result becomes positive. The goal is to make the
baseline policy, paired evidence, secondary-metric tradeoffs, and allowed
statistical language explicit, source-derived, and machine-checkable before the
next manuscript rewrite.

## 2. One-Sentence Argument

In constrained farmland layout planning, Paper10 may claim a monitor-gated
GeoJEPA-MPC decision-support workflow with a descriptive Bishan 20x16/top5
reward anchor, supported by executable-mask evidence and matched baseline
audits, while explicitly bounding inferential superiority, 50-state scaling,
cross-region transfer, and irregular cadastral deployment claims.

## 3. Current Evidence Boundary

The hardening pass starts from the current locked files:

- `e0_paper10_bounded_manuscript_assembly_draft_2026-06-27.md`
- `e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.md`
- `e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.md`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.json`
- `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md`
- `e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`
- `e0_dongxing_return_label_family_summary_2026-06-10.csv`
- `e0_dongxing_low_label_budget_family_summary_2026-06-10.csv`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`

The current route remains CEUS-first. The current package is still
`not_submission_ready` because repository DOI/reviewer link, licence, generated
data rights, full-data access routes, citation policy, statistical policy, and
final figure/export decisions are unresolved.

## 4. Goals

This pass should produce one source-derived audit package and one manuscript
patch layer.

The audit package should:

- freeze the comparator taxonomy for the CEUS route;
- recompute paired matched Paper9 versus value-filter seed-level deltas from
  tracked source artifacts;
- report exact win/loss counts, paired mean delta, median delta, minimum and
  maximum delta, and whether every seed improves;
- report secondary-metric tradeoffs where source data are available;
- compute a small-sample inference-readiness readout without converting it into
  a significance claim;
- classify each manuscript-facing claim as `supported_descriptive`,
  `not_supported`, `diagnostic_only`, or `submission_blocked`;
- emit both Markdown and JSON outputs for manuscript and preflight use;
- be covered by focused tests so later edits cannot silently overclaim.

The manuscript patch layer should:

- revise the Results and Discussion claim hierarchy around the hardened audit;
- state that the 5-seed reward result is descriptive and mixed seed-wise;
- distinguish executable-mask necessity from value-filter superiority;
- keep the ungated-top4 result as a boundary on monitor-gate performance
  wording;
- keep Stage 3 and Dongxing/Neijiang as boundary and calibration evidence;
- preserve the no-go submission blockers.

## 5. Non-Goals

This pass must not:

- redesign GeoJEPA, the value head, or candidate scoring;
- tune top-k, horizon, monitor thresholds, blend weights, or candidate-value
  weight after seeing seed outcomes;
- rerun open-ended 50-state training;
- claim direct 50-state Bishan scale-up success;
- claim robust Bishan-to-Dongxing transfer superiority;
- claim solved irregular cadastral deployment;
- claim a full Constrained MDP, CPO, or RCPO solver;
- introduce p-values or confidence intervals as positive evidence unless a
  predefined statistical policy classifies the result as inferentially
  supported;
- close DOI, licence, rights, citation, data-access, or final export blockers.

## 6. Comparator Taxonomy

The CEUS route should use the following comparator names consistently.

| comparator | role | allowed use |
|---|---|---|
| `matched_paper9_rank_seed2028` | Default matched CEUS baseline under the same H=5, K=50, executable-mask, and 100-step rollout settings. | Main Bishan paired comparison. |
| `value_filter_20x16_top5` | Paper10 value-filter candidate trained from the validated Bishan 20x16/top5 labels. | Main positive anchor, descriptive only. |
| `ungated_top4_control` | Mechanism boundary control that matched the full gated masked reward. | Shows monitor gate is evidence control, not demonstrated online reward gain. |
| `no_mask_control` | Executable-mask ablation. | Supports mask necessity only. |
| `stage3_50state_rows` | Authorized 50-state confirmatory rows and candidate-score sweep. | Boundary evidence, not scale-up success. |
| `dongxing_transfer_scratch_families` | External-region calibration and low-label stress tests. | Calibration evidence, not robust transfer superiority. |

If a separately identified pairwise-only baseline is added later, it must be a
new named comparator with its own source files and cannot be conflated with the
matched Paper9 baseline.

## 7. New Audit Artifact

Create:

```text
paper10_geojepa_mpc/experiments/results/
  e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md
  e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json
```

The Markdown file is the author-facing audit. The JSON file is the
machine-readable source for tests, preflight checks, and future table assembly.

## 8. Audit Computation

Implement a source-derived runner:

```text
paper10_geojepa_mpc/experiments/ceus_baseline_inference_hardening.py
```

The runner should not rerun training or rollout. It should read the current
tracked audit JSON/CSV files and produce a deterministic report.

The runner should compute:

- `n_seeds`
- seed-level baseline reward, candidate reward, reward delta, and win/loss/tie
  label
- paired mean reward delta
- paired median reward delta
- sample standard deviation of paired deltas
- minimum and maximum paired delta
- candidate win count, loss count, and tie count
- exact two-sided sign-test p-value for the observed win/loss count, labelled
  `diagnostic_only` because n=5 is underpowered and no inferential claim was
  predefined before the original rollouts
- a claim gate:
  - `uniform_superiority_supported = false` unless all seeds improve;
  - `inferential_superiority_supported = false` unless a future predefined
    statistical policy and adequate sample size support it;
  - `descriptive_mean_reward_anchor_supported = true` only when candidate mean
    reward exceeds baseline mean reward and all source routes are present.
- secondary metrics from the mechanism packet:
  - reward, slope percent, contiguity, baimu area, zero swaps, and negative
    zero swaps for full gated masked, matched Paper9, no mask, and ungated top4
    conditions;
  - a tradeoff classification that states reward improved descriptively while
    secondary metrics are mixed.
- source-file provenance for every number included.

The exact sign-test implementation can be a small standard-library function:

```python
from math import comb

def two_sided_sign_test_pvalue(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)
```

For the current 3-win/2-loss result, the expected p-value is `1.0`. The
manuscript should not present this as evidence against the method; it should
use it to justify descriptive-only language.

## 9. Manuscript Patch Layer

Create:

```text
paper10_geojepa_mpc/experiments/results/
  e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md
```

This file should not replace the full manuscript draft. It should provide
drop-in replacements for these sections:

- Abstract result sentences;
- Results subsection for the Bishan 20x16/top5 matched comparison;
- Results subsection for mechanism ablation;
- Discussion paragraphs on baseline fairness, inference limits, and CEUS
  planning-support relevance;
- Claim-evidence table rows affected by the new audit.

The patch should use the hardened terminology:

- `descriptive matched 5-seed reward anchor`
- `mixed seed-wise outcome`
- `executable-mask necessity`
- `monitor gate as evidence control`
- `Stage 3 boundary evidence`
- `Dongxing/Neijiang calibration evidence`

The patch should avoid:

- `statistically significant`
- `robustly superior`
- `consistent improvement across seeds`
- `direct scale-up`
- `transfer superiority`
- `deployment-ready cadastral planning`

## 10. Preflight Guard

Extend:

```text
scripts/paper10/preflight_submission_checks.py
```

Add a check named:

```text
paper10_ceus_baseline_inference_hardening_current
```

The check should pass only if:

- both hardening audit outputs exist;
- the manuscript patch exists;
- the JSON contains `uniform_superiority_supported: false`;
- the JSON contains `inferential_superiority_supported: false`;
- the JSON contains `descriptive_mean_reward_anchor_supported: true`;
- the Markdown audit includes the exact phrase `diagnostic_only` for the
  sign-test readout;
- the manuscript patch includes the phrase `mixed seed-wise outcome`;
- README, MANIFEST, DATA_AVAILABILITY, and REPRODUCIBILITY reference the new
  hardening audit or explicitly defer to it for CEUS baseline and inference
  wording.

The check should fail if the patch or audit contains unqualified overclaims:

- `statistically significant`
- `robustly superior`
- `uniformly superior`
- `direct 50-state Bishan scale-up success`
- `robust Bishan-to-Dongxing transfer superiority`
- `deployment-ready`

Negative guardrails are allowed when they are clearly prohibitive, such as
`Do not claim robust Bishan-to-Dongxing transfer superiority`.

## 11. Tests

Use test-driven development for the implementation.

Add focused tests to:

```text
paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py
paper10_geojepa_mpc/tests/test_submission_preflight.py
```

Required behavior tests:

- `two_sided_sign_test_pvalue(3, 2)` returns `1.0`;
- paired reward summary from a minimal fixture returns 3 wins, 2 losses, mean
  delta above zero, and `uniform_superiority_supported == False`;
- secondary metric classification marks reward as descriptively improved but
  secondary metrics as mixed when slope or contiguity do not all improve;
- JSON output includes source provenance for the matched 5-seed audit and
  mechanism packet;
- preflight registers
  `paper10_ceus_baseline_inference_hardening_current`;
- preflight fails when the audit JSON is missing;
- preflight fails when `uniform_superiority_supported` is true for the current
  mixed seed result;
- preflight fails when manuscript patch text contains unqualified
  `statistically significant`;
- preflight allows negative guardrail wording.

## 12. Verification

Run focused verification:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected results:

- focused tests pass;
- preflight prints `Paper10 preflight: PASS`;
- preflight output includes `[ok] paper10_ceus_baseline_inference_hardening_current`.

Before claiming the branch is complete, run the full suite:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

## 13. Expected Manuscript Effect

After implementation, Paper10 should be easier to defend to CEUS reviewers
because the paper will no longer depend on soft wording around a mixed result.
The revised evidence chain should be:

1. The workflow is relevant to constrained geospatial decision support.
2. The Bishan 20x16/top5 value-filter anchor improves mean reward
   descriptively under a matched protocol.
3. The seed-wise result is mixed, so inferential and uniform superiority are
   not claimed.
4. Executable masks are necessary for valid rollout behavior.
5. Monitor gates are justified as label-quality and evidence-control
   machinery, not as a separately proven online reward mechanism.
6. Failed 50-state and mixed Dongxing/Neijiang results define applicability
   boundaries.
7. The package remains not submission-ready until data, licence, citation,
   statistical, and figure/export blockers are closed.

## 14. Commit Plan

Use at least three commits:

1. `docs: design paper10 ceus baseline hardening`
2. `test: cover paper10 ceus baseline hardening audit`
3. `feat: add paper10 ceus baseline hardening audit`
4. `docs: add paper10 ceus baseline hardened manuscript patch`
5. `test: guard paper10 ceus baseline hardening preflight`

If implementation reveals that source files do not contain enough secondary
metric detail for a planned table, keep the audit conservative and mark that
field `not_assessable_from_tracked_sources` rather than inventing data or
rerunning unplanned experiments.
