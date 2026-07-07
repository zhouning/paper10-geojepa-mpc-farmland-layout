# Bishan 10x12/top4 reward-only top7 margin-calibration triage

This triage tests whether the Paper10 true-reward guard transfers from the
20x16/top5 anchor to the smaller 10x12/top4 pilot checkpoint. The audit rule is
kept fixed as reward-only top7; only the true-reward switch margin is calibrated.

## Protocol

- checkpoint: `e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt`
- baseline: existing 10x12/top4 `blend_w0p10`, `top_k=50`, independent-continuation rollout
- candidate score: `blend`, `candidate_value_weight=0.10`
- audit set: selected action plus model-reward top7
- audit random sample: `0`
- execution policy: `margin_true_reward_guard`
- horizon: `5`
- rollout: matched 100-step seeds `0-4`

## 5-seed 100-step margin gate

| policy | margin | mean reward | delta vs baseline | seed wins | min seed delta | switches | mean audited actions | mean true-audit sec/step |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | - | 65.2566 | 0.0000 | - | - | 0 | - | - |
| rewardtop7 | 1.50 | 69.2652 | 4.0086 | 4 / 5 | -13.7568 | 47 | 7.8040 | 0.4594 |
| rewardtop7 | 1.60 | 72.2820 | 7.0253 | 5 / 5 | 2.1341 | 49 | 7.7960 | 0.4677 |
| rewardtop7 | 1.75 | 70.1005 | 4.8439 | 4 / 5 | -4.0277 | 41 | 7.7800 | 0.4648 |
| rewardtop7 | 2.00 | 72.1585 | 6.9019 | 4 / 5 | -4.0277 | 34 | 7.7660 | 0.4417 |

## Seed-level reward deltas vs baseline

| seed | m1.50 | m1.60 | m1.75 | m2.00 |
|---:|---:|---:|---:|---:|
| 0 | 2.1341 | 2.1341 | -4.0277 | -4.0277 |
| 1 | -13.7568 | 2.7673 | 1.8882 | 6.7129 |
| 2 | 13.9032 | 13.9032 | 14.5352 | 17.0337 |
| 3 | 5.1330 | 3.6924 | 8.6658 | 10.8365 |
| 4 | 12.6297 | 12.6297 | 3.1579 | 3.9540 |

## Paired statistics for m1.60

| metric | value |
|---|---:|
| baseline mean reward | 65.2566 |
| candidate mean reward | 72.2820 |
| paired mean delta | 7.0253 |
| paired median delta | 3.6924 |
| wins/losses | 5 / 0 |
| min seed delta | 2.1341 |
| bootstrap 95% CI for mean delta | [2.6990, 11.4213] |

## Interpretation

Directly transferring the 20x16/top5 margin (`1.50`) is not robust on the
10x12/top4 checkpoint: it raises the mean but loses seed 1 by `13.7568`. Raising
the margin to `1.75` or `2.00` fixes seed 1 but causes seed 0 to fall below the
baseline. The intermediate `margin=1.60` is the only tested margin that wins all
five matched seeds while keeping a positive bootstrap interval for the paired
mean delta.

This is algorithmically useful because it separates the transferable mechanism
from the tunable threshold. The transferable part is the reward-only top7
true-reward guard; the switch margin is setting-specific and must be calibrated
against matched long-horizon seeds.

## Decision

Promote `reward-only top7, margin=1.60` as the current 10x12/top4
setting-specific robust guard. Keep the 20x16/top5 default at
`reward-only top7, margin=1.50`; do not claim a universal fixed margin.

## Evidence files

- `e0_bishan_10x12_top4_blend010_h5_k50_seeds0-4_100step_consolidated_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m150_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m160_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m175_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m200_audit_rewardtop7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_5seed_paired_stats_2026-07-07.json`
- `e0_bishan_10x12_top4_true_reward_margin_guard_m160_rewardtop7_vs_blend010_5seed_100step_comparison_2026-07-07.json`
