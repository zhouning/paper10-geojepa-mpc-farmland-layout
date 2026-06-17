# Paper10 Original-Vision Validation Registry

Date: 2026-06-17

This registry starts the preregistered validation pass for the original Paper10
vision. It records what is frozen before new experiments, what thresholds will
be used, and what evidence is required before changing the manuscript claim.

## Design Spec

- `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
- Commit introducing the spec: `da7e793 docs: add original vision validation design`

## Frozen Evidence

### Bishan 20x16/h5 top-5 positive anchor

- candidate family: `frontier_random050`
- label setting: `20x16/h5`
- label seed: `44`
- monitor top-k: `5`
- monitor decision: `continue`
- candidate top-k regret: `0.18767197132110597`
- candidate top-k overlap: `0.6300000000000001`
- one-step top-k regret: `2.462647271156311`
- five-seed mean total reward: `69.47054604253474`
- five-seed sample standard deviation: `1.0003610285842477`
- reproduction note:
  `paper10_geojepa_mpc/experiments/results/e0_windows_realdata_20x16_top5_reproduction_2026-06-10.md`

### 50-state seed46 boundary diagnostics

- existing Windows summary:
  `D:\test\paper10_runs\frontier_random050_ablation_summary.md`
- existing post-hoc top-k summary:
  `D:\test\paper10_runs\frontier_random050_ablation_posthoc_topk_summary.md`
- current interpretation: all tested seed46 50-state rows failed the monitor
  gate and remain row-specific negative diagnostics.

### Dongxing/Neijiang evidence

- synthesis:
  `paper10_geojepa_mpc/experiments/results/e0_dongxing_results_synthesis_2026-06-10.md`
- current interpretation: method portability, planner calibration, and
  return-label scaling are supported; a broad transfer-win claim is not
  supported by the current evidence.

## Confirmatory Monitor Gate

For confirmatory value-label validation, a row passes only if at least one
preregistered monitor top-k satisfies all thresholds:

| metric | pass threshold |
|---|---:|
| candidate top-k regret | `<= 0.25` |
| candidate top-k overlap | `>= 0.50` |
| one-step top-k regret | `>= 0.25` |

For 50-state Stage 1 rows, the preregistered top-k set is `5, 6, 8, 10, 12`.

## Stage 1 Label-Only Matrix

The first Windows label-only matrix uses `TrainOnPass = 0`.

| run family | states | candidates | horizon | frontier fraction | label seeds |
|---|---:|---:|---:|---:|---|
| `50x16_h5_f050` | 50 | 16 | 5 | 0.50 | 47, 48 |
| `50x20_h5_f050` | 50 | 20 | 5 | 0.50 | 47, 48 |
| `50x24_h5_f075` | 50 | 24 | 5 | 0.75 | 47, 48 |

The optional seed49-50 expansion is allowed only if the first matrix contains a
`pass` or `near_pass` decision under the design spec.

## Stage 2 Audit

The Stage 2 audit uses existing Dongxing CSV summaries before adding new
Dongxing compute. It reports matched transfer-minus-scratch effects by family
and label budget.

## Claim Lock

No new conclusion about 50-state scale-up or transfer superiority may be added
until Stage 1 and Stage 2 outputs exist and are compared against the design
spec.
