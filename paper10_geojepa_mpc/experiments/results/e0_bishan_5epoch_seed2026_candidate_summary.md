# E0 Bishan Candidate-Action Metrics

Date: 2026-06-07

Dataset: full Bishan Paper9 Tool2 pairwise data

- transition samples: 6000
- pairwise states: 1000
- candidate actions per state: 50
- epochs: 5
- seed: 2026
- evaluation: all 1000 pairwise states, top-5 candidates

## Metrics

| config | pairwise ranking_acc | top1 hit | top1 regret | top5 hit | top5 regret |
|---|---:|---:|---:|---:|---:|
| mse_only | 0.596838 | 0.100 | 1.255152 | 0.356 | 0.834585 |
| rank | 0.849802 | 0.312 | 0.930026 | 0.709 | 0.568499 |
| rank_sigreg | 0.869565 | 0.275 | 0.979713 | 0.684 | 0.644223 |

## Interpretation

This run strengthens the Paper10 design rationale:

1. Ranking supervision improves planning-facing candidate selection metrics over
   MSE-only. The `rank` model has higher top-1/top-5 hit rates and lower regret.
2. SIGReg is not automatically a planning improvement. In this seed,
   `rank_sigreg` improves pairwise ranking accuracy but performs worse than
   `rank` on top-K candidate selection metrics.
3. Paper10 should treat pairwise ranking accuracy as necessary but not
   sufficient. Top-K regret and eventually MPC outcomes must be primary
   planning-facing metrics.

The next step is to run candidate metrics for seeds 2027 and 2028, then decide
whether SIGReg should stay as a main ablation or only as a diagnostic variant.
