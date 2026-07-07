# Bishan 20x16/top5 reward-only top7 margin-boundary triage

This triage tests whether the simplified robust default
`reward-only top7, margin=1.50` can use a lower switch margin. The lower-margin
candidate keeps the same learned filter and audit set but changes
`true_reward_switch_margin` from `1.50` to `1.25`.

## 5-seed 100-step gate

| policy | margin | mean reward | delta vs baseline | wins vs baseline | delta vs m1.50 | mean audited actions | mean true-audit sec/step | switches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rewardtop7 | 1.50 | 71.8258 | 2.3553 | 5 / 5 | 0.0000 | 7.7580 | 0.4539 | 49 |
| rewardtop7 | 1.25 | 72.2180 | 2.7475 | 4 / 5 | 0.3922 | 7.7840 | 0.4652 | 47 |

## Seed-level reward deltas

| seed | m1.50 vs baseline | m1.25 vs baseline | m1.25 vs m1.50 |
|---:|---:|---:|---:|
| 0 | 0.5825 | 1.7297 | 1.1472 |
| 1 | 6.0147 | -0.6291 | -6.6438 |
| 2 | 3.1866 | 5.1756 | 1.9891 |
| 3 | 0.2330 | 1.9353 | 1.7023 |
| 4 | 1.7597 | 5.5258 | 3.7661 |

## Interpretation

Lowering the margin from `1.50` to `1.25` slightly improves the five-seed mean
reward (`+0.3922` vs m1.50), but it fails the robustness gate because seed 1
falls below the baseline (`-0.6291`) and drops `6.6438` relative to m1.50. The
audit set is unchanged, so the lower margin does not reduce true-reward audit
cost.

The result supports keeping `margin=1.50` as the current robust default. The
lower margin remains a reward-seeking ablation, not a confirmatory candidate.

## Decision

Do not expand reward-only top7 `margin=1.25` to the 20-seed confirmatory tier.
Keep `reward-only top7, margin=1.50` as the simplified robust default for the
Bishan 20x16/top5 setting.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_m125_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m125_rewardtop7_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m125_rewardtop7_vs_m150_rewardtop7_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
