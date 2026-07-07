# Bishan 20x16/top5 reward-only audit cost-boundary triage

This triage tests whether the simplified robust default
`reward-only top7, margin=1.50` can be reduced further to reward-only top6 or
top5 while preserving the long-horizon reward improvement.

All candidates keep the same learned filter and guard:

- `candidate_score_mode=blend`
- `candidate_value_weight=0.10`
- `top_k=50`
- `audit_random_sample=0`
- `audit_top_candidate=0`
- `execution_policy=margin_true_reward_guard`
- `true_reward_switch_margin=1.50`
- `random_continuation_mode=independent`

Only `audit_top_reward` changes.

## 5-seed 100-step gate

| guard | mean reward | delta vs baseline | delta vs rewardtop7 | wins vs baseline | mean audited actions | mean true-audit sec/step | switches |
|---|---:|---:|---:|---:|---:|---:|---:|
| rewardtop7 | 71.8258 | 2.3553 | 0.0000 | 5 / 5 | 7.7580 | 0.4539 | 49 |
| rewardtop6 | 69.8147 | 0.3442 | -2.0111 | 3 / 5 | 6.7780 | 0.3913 | 43 |
| rewardtop5 | 67.4133 | -2.0573 | -4.4125 | 2 / 5 | 5.8040 | 0.3525 | 40 |

## Seed-level reward deltas vs baseline

| seed | rewardtop7 | rewardtop6 | rewardtop5 |
|---:|---:|---:|---:|
| 0 | 0.5825 | -1.9391 | 2.6879 |
| 1 | 6.0147 | 6.1988 | -3.6843 |
| 2 | 3.1866 | 5.9282 | 6.2453 |
| 3 | 0.2330 | -10.2268 | -10.2268 |
| 4 | 1.7597 | 1.7597 | -5.3084 |

## Interpretation

Reducing the audit set below reward-only top7 saves roughly one or two true
reward evaluations per step, but the reward loss is too large and not
seed-stable. Rewardtop6 loses two of five seeds against the baseline and has a
mean reward `2.0111` below rewardtop7. Rewardtop5 is worse: it loses three of
five seeds against the baseline and has negative mean delta vs the baseline.

The result supports reward-only top7 as the current cost-stability boundary for
the Bishan 20x16/top5 setting. Top6 and top5 should be retained as negative
cost-boundary evidence rather than promoted to confirmatory 20-seed candidates.

## Decision

Keep `reward-only top7, margin=1.50` as the simplified robust default. Do not
expand rewardtop6 or rewardtop5 to the 20-seed confirmatory tier unless a future
algorithmic change alters the ranking or guard rule.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop6_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop5_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop6_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop5_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop6_vs_rewardtop7_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop5_vs_rewardtop7_5seed_100step_comparison_2026-07-07.json`
