# E0 Bishan 5-Epoch 3-Seed Candidate-Metric Summary

Date: 2026-06-07

Dataset: full Bishan Paper9 Tool2 data

- transition samples: 6000
- pairwise states: 1000
- candidate actions per state: 50
- epochs: 5
- seeds: 2026, 2027, 2028
- evaluation seed: 12345
- top-K metric: K = 5

## Aggregate Metrics

| config | ranking_acc mean | ranking_acc std | top1 hit mean | top1 regret mean | top5 hit mean | top5 regret mean |
|---|---:|---:|---:|---:|---:|---:|
| mse_only | 0.612648 | 0.018113 | 0.103333 | 1.242889 | 0.366000 | 0.771249 |
| rank | 0.857708 | 0.007905 | 0.337000 | 0.856138 | 0.696000 | 0.559640 |
| rank_sigreg | 0.869565 | 0.000000 | 0.323667 | 0.872620 | 0.687000 | 0.584058 |

## Aggregate Standard Deviations

| config | top1 hit std | top1 regret std | top5 hit std | top5 regret std |
|---|---:|---:|---:|---:|
| mse_only | 0.017243 | 0.023672 | 0.008718 | 0.060241 |
| rank | 0.023259 | 0.081614 | 0.018358 | 0.026197 |
| rank_sigreg | 0.049003 | 0.110306 | 0.013748 | 0.062731 |

## Interpretation

The 3-seed candidate-action results separate representation/ranking diagnostics
from planning-facing candidate selection quality:

1. `rank` and `rank_sigreg` both strongly outperform `mse_only` on all
   candidate metrics.
2. `rank_sigreg` has the highest sampled pairwise ranking accuracy, but `rank`
   has better average top-1 hit, top-1 regret, top-5 hit, and top-5 regret.
3. The next E0 decision should use `rank` as the primary MPC-facing model and
   keep `rank_sigreg` as a secondary ablation or tune `lambda_sig` before using
   it in planning.

This supports the Paper10 framing: latent regularization is not a substitute for
planning-facing validation. Candidate regret is closer to MPC action choice than
pairwise ranking accuracy alone.
