# Bishan 20x16/top5 reward-only top7 guard simplification triage

This experiment tests whether the robust `audit7x7 margin=1.50` guard needs both model-reward top7 and blend top7 audit paths. The simplified candidate keeps the same learned filter and margin rule but audits only the selected action plus model-reward top7 actions (`audit_top_reward=7`, `audit_top_candidate=0`).

## 20-seed result

| metric | value |
|---|---:|
| baseline mean reward | 65.8876 |
| dual7x7 mean reward | 72.1773 |
| reward-only top7 mean reward | 72.1918 |
| reward-only delta vs baseline | 6.3041 |
| reward-only wins vs baseline | 20 / 20 |
| reward-only delta vs dual7x7 | 0.0144 |
| reward-only wins/losses/ties vs dual7x7 | 1 / 1 / 18 |
| bootstrap 95% CI vs baseline | [4.1401, 8.5056] |

## Audit cost proxy

| guard | mean audited actions | mean true-audit sec/step | switches |
|---|---:|---:|---:|
| reward-only top7 | 7.7605 | 0.4452 | 172 |
| dual7x7 | 8.1905 | 0.4790 | 171 |

## Seed-level deltas

| seed | reward-only delta vs baseline | reward-only delta vs dual7x7 |
|---:|---:|---:|
| 0 | 0.5825 | 0.0000 |
| 1 | 6.0147 | 0.0000 |
| 2 | 3.1866 | 0.0000 |
| 3 | 0.2330 | -0.4828 |
| 4 | 1.7597 | 0.0000 |
| 5 | 0.0029 | 0.0000 |
| 6 | 0.8565 | 0.0000 |
| 7 | 14.4199 | 0.7718 |
| 8 | 10.8797 | 0.0000 |
| 9 | 4.9877 | 0.0000 |
| 10 | 15.4454 | 0.0000 |
| 11 | 12.8594 | 0.0000 |
| 12 | 10.2059 | 0.0000 |
| 13 | 6.1038 | 0.0000 |
| 14 | 8.5784 | 0.0000 |
| 15 | 1.6209 | 0.0000 |
| 16 | 12.2019 | 0.0000 |
| 17 | 10.1792 | 0.0000 |
| 18 | 1.3899 | 0.0000 |
| 19 | 4.5750 | 0.0000 |

## Interpretation

The reward-only top7 simplification preserves the 20-seed robustness result: it wins `20/20` seeds against the value-filter baseline and has a strictly positive bootstrap CI for the mean delta. It is also effectively tied with the dual-path `audit7x7` guard, with a small positive mean difference (`+0.0144`) and fewer audited actions on average (`7.7605` vs `8.1905`).

This means the extra blend-top7 audit path is not needed for the current Bishan 20x16/top5 robust default. The simplification improves algorithm clarity: candidate filtering still uses `blend_w0p10`, but the true-reward guard audits only the model-reward top7 alternatives plus the rollout-selected action.

## Decision

Promote `reward-only top7, margin=1.50` as the current simplified robust default for Paper10 Bishan 20x16/top5. Keep dual7x7 as a bounded ablation and avoid runtime superiority claims because wall-clock timing remains environment-state dependent.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop7_blend010_seeds0-19_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_vs_blend010_20seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_vs_dual7x7_20seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_rewardtop7_20seed_paired_stats_2026-07-07.json`
