# Paper10 true-reward guard readiness audit

Date: 2026-07-08

Status: source-derived true-reward guard readiness audit.

No training, rollout, algorithm redesign, or post-hoc experiment rerun was performed.
This is an algorithm-readiness evidence boundary, not final submission readiness.

## Source Provenance

- Primary 20x16/top5 comparison: `paper10_geojepa_mpc/experiments/results/e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_vs_blend010_10seed_100step_comparison_2026-07-07.json`
- Small-scale 10x12/top4 statistics: `paper10_geojepa_mpc/experiments/results/e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_5seed_paired_stats_2026-07-07.json`

## Primary Guard Candidate

The current Paper10 primary algorithm candidate is `audit7x7 margin=1.50` for Bishan 20x16/top5.

| metric | value |
|---|---:|
| baseline mean reward | 68.8015 |
| guard mean reward | 73.0649 |
| mean delta vs baseline | 4.2634 |
| seed wins | 10 / 10 |
| min seed delta | 0.0029 |
| max seed delta | 13.6481 |

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
| small-scale consistency supported | True |
| setting-specific margin required | True |
| universal fixed margin supported | False |
| direct 50-state scale-up supported | False |
| robust transfer superiority supported | False |
| deployment-ready cadastral planning supported | False |

## Interpretation Boundary

Use this audit to treat the 2026-07-07 true-reward margin guard as the current algorithm-readiness candidate for Paper10 Bishan experiments.
The evidence supports a setting-specific guard, not a universal margin or a general scale-up result.

Do not claim a universal fixed switch margin.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not treat this as final submission readiness.
