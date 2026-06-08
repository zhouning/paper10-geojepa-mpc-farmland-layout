# E0 Bishan 5-Epoch 3-Seed Summary

Date: 2026-06-07

Dataset: full Bishan Paper9 Tool2 data

- transitions: 6000 samples, 2600 blocks, 17 block features
- pairwise states: 1000 states, 50 candidate actions per state
- training device: CPU
- epochs: 5
- batch size: 16
- pairwise subsample per update: 16 states
- sampled action pairs per pairwise state: 4
- evaluation seed: 12345
- seeds: 2026, 2027, 2028

## Aggregate Metrics

| config | n | ranking_acc mean | ranking_acc std | final_mse mean | elapsed mean sec |
|---|---:|---:|---:|---:|---:|
| mse_only | 3 | 0.612648 | 0.018113 | 0.115239 | 68.80 |
| rank | 3 | 0.857708 | 0.007905 | 0.013462 | 349.23 |
| rank_sigreg | 3 | 0.869565 | 0.000000 | 0.013264 | 349.56 |

## Per-Seed Ranking Accuracy

| seed | mse_only | rank | rank_sigreg |
|---:|---:|---:|---:|
| 2026 | 0.596838 | 0.849802 | 0.869565 |
| 2027 | 0.632411 | 0.865613 | 0.869565 |
| 2028 | 0.608696 | 0.857708 | 0.869565 |

## Interpretation

This is a short E0 diagnostic, not a manuscript-grade final result. It supports
two early decisions:

1. Action-ranking supervision is necessary: `rank` substantially improves
   ranking accuracy over `mse_only`.
2. SIGReg is safe to keep in the next ablation: `rank_sigreg` did not degrade
   ranking accuracy in this 3-seed, 5-epoch probe and showed a small aggregate
   improvement over `rank`.

The next E0 run should increase epochs and report planning-facing metrics such
as top-K regret before any claim is made about SIGReg improving MPC outcomes.
