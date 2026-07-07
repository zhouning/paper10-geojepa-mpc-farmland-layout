# Bishan 20x16/top5 audit7x7 margin=1.50 20-seed confirmatory triage

This confirmatory holdout freezes the current robust default before extension: `blend_w0p10`, `top_k=50`, `audit7x7`, no random audit sample, and `true_reward_switch_margin=1.50`. Seeds 10-19 were run after the seeds0-9 robustness result and are treated as the confirmatory holdout batch.

## Aggregate result

| metric | value |
|---|---:|
| seeds | 20 |
| baseline mean reward | 65.8876 |
| candidate mean reward | 72.1773 |
| paired mean delta | 6.2897 |
| paired median delta | 5.5012 |
| wins / losses / ties | 20 / 0 / 0 |
| min seed delta | 0.0029 |
| max seed delta | 15.4454 |
| bootstrap 95% CI for mean delta | [4.1643, 8.4501] |
| normal-approx 95% CI for mean delta | [4.0726, 8.5068] |

## Seed-level result

| seed | baseline | candidate | delta |
|---:|---:|---:|---:|
| 0 | 67.7135 | 68.2960 | 0.5825 |
| 1 | 70.2252 | 76.2399 | 6.0147 |
| 2 | 69.7218 | 72.9084 | 3.1866 |
| 3 | 69.8245 | 70.5403 | 0.7158 |
| 4 | 69.8677 | 71.6274 | 1.7597 |
| 5 | 70.9025 | 70.9054 | 0.0029 |
| 6 | 71.3928 | 72.2493 | 0.8565 |
| 7 | 62.6650 | 76.3131 | 13.6481 |
| 8 | 64.8928 | 75.7726 | 10.8797 |
| 9 | 70.8091 | 75.7968 | 4.9877 |
| 10 | 55.9966 | 71.4421 | 15.4454 |
| 11 | 62.3181 | 75.1775 | 12.8594 |
| 12 | 62.4917 | 72.6976 | 10.2059 |
| 13 | 62.4648 | 68.5687 | 6.1038 |
| 14 | 65.1951 | 73.7734 | 8.5784 |
| 15 | 67.8109 | 69.4318 | 1.6209 |
| 16 | 62.9174 | 75.1193 | 12.2019 |
| 17 | 59.7798 | 69.9590 | 10.1792 |
| 18 | 67.4888 | 68.8787 | 1.3899 |
| 19 | 63.2747 | 67.8497 | 4.5750 |

## Guard behavior

| metric | value |
|---|---:|
| audited states | 2000 |
| switches | 171 |
| switch rate | 0.0855 |
| mean audited actions | 8.1905 |
| mean true-audit sec/step | 0.4790 |
| selected is audit true-best rate | 0.0610 |
| selected true-reward regret mean | 0.8885 |

## Interpretation

The frozen robust default survives the 10-seed holdout and the combined 20-seed matched protocol. The candidate wins every seed (`20/20`) and raises mean 100-step reward by `+6.2897`. The bootstrap confidence interval for the paired mean delta remains strictly positive, supporting a stronger descriptive algorithmic claim than the earlier 5-seed and 10-seed packets.

The claim remains bounded: it is a Bishan E0, 20x16/top5, matched 100-step protocol result. The true-reward audit uses additional environment evaluations, so runtime superiority should not be claimed. Auxiliary land metrics are mixed and should not be framed as all-indicator improvement.

## Decision

Promote `audit7x7 margin=1.50` as the current robust Paper10 algorithmic default for Bishan 20x16/top5. This is now supported by a frozen 20-seed confirmatory packet and should replace the earlier 5-seed-only framing in future manuscript updates.

## Evidence files

- `e0_bishan_20x16_top5_value_filter_blend010_selectedaudit_seeds0-19_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_blend010_seeds0-19_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_vs_blend010_20seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_20seed_paired_stats_2026-07-07.json`
