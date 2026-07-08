# Paper10 true-reward guard readiness audit

Date: 2026-07-08

Status: source-derived true-reward guard readiness audit.

No training, rollout, algorithm redesign, or post-hoc experiment rerun was performed.
This is an algorithm-readiness evidence boundary, not final submission readiness.

## Source Provenance

- Primary 20x16/top5 comparison: `paper10_geojepa_mpc/experiments/results/e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-07.json`
- Primary 20x16/top5 paired statistics: `paper10_geojepa_mpc/experiments/results/e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_20seed_paired_stats_2026-07-07.json`
- Small-scale 10x12/top4 statistics: `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_5seed_paired_stats_2026-07-07.json`

## Primary Guard Candidate

The current Paper10 primary algorithm candidate is `rewardtop7 margin=1.50` for Bishan 20x16/top5.

| metric | value |
|---|---:|
| baseline mean reward | 65.8876 |
| guard mean reward | 72.1918 |
| mean delta vs baseline | 6.3041 |
| seed wins | 20 / 20 |
| min seed delta | 0.0029 |
| max seed delta | 15.4454 |

## Primary Paired Statistics

| metric | value |
|---|---:|
| paired seeds | 20 |
| wins / losses / ties | 20 / 0 / 0 |
| mean delta | 6.3041 |
| median delta | 5.5012 |
| bootstrap 95% CI lower | 4.1401 |
| bootstrap 95% CI upper | 8.5056 |
| switch rate | 0.0860 |
| selected true-reward regret mean | 0.8904 |

## Rewardtop7 Simplification Boundary

The primary guard is the simplified robust default: it audits the rollout-selected action plus model-reward top7 actions, not the extra blend-top7 path.

| metric | value |
|---|---:|
| mean audited actions | 7.7605 |
| dual7x7 mean audited actions | 8.1905 |
| mean delta vs dual7x7 | 0.0144 |
| wins / losses / ties vs dual7x7 | 1 / 1 / 18 |

## Small-Scale Consistency Guard

The supporting small-scale guard is `rewardtop7 margin=1.60` for Bishan 10x12/top4.

| metric | value |
|---|---:|
| baseline mean reward | 65.2566 |
| guard mean reward | 72.2820 |
| mean delta vs baseline | 7.0253 |
| seed wins | 5 / 5 |
| min seed delta | 2.1341 |
| bootstrap 95% CI lower | 2.6990 |

## Claim Gates

| gate | status |
|---|---|
| primary algorithm candidate supported | True |
| primary paired statistics supported | True |
| small-scale consistency supported | True |
| setting-specific margin required | True |
| universal fixed margin supported | False |
| direct 50-state scale-up supported | False |
| robust transfer superiority supported | False |
| deployment-ready cadastral planning supported | False |

## Interpretation Boundary

Use this audit to treat the 2026-07-07 reward-only top7 true-reward margin guard as the current simplified robust default for Paper10 Bishan experiments.
The evidence supports a setting-specific guard, not a universal margin or a general scale-up result.

Do not claim a universal fixed switch margin.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not treat this as final submission readiness.
