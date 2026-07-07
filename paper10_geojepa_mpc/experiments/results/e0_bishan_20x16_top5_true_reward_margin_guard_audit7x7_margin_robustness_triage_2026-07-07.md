# Bishan 20x16/top5 audit7x7 margin and robustness triage

This packet tunes the switch margin for the true-reward `audit7x7` guard and extends the consistency-leading setting from 5 seeds to 10 matched 100-step seeds. The learned filter remains fixed: `blend`, value weight `0.10`, `top_k=50`, reward reserve 0, independent continuation, and no random audit sample.

## 10-step margin gate

| policy | margin | mean reward | delta vs baseline | seed wins | switches |
|---|---:|---:|---:|---:|---:|
| baseline | - | 14.1054 | 0.0000 | - | 0 |
| m075 | 0.75 | 17.9461 | 3.8407 | 5/5 | 32 |
| m100 | 1.00 | 19.1802 | 5.0749 | 5/5 | 20 |
| m125 | 1.25 | 19.1802 | 5.0749 | 5/5 | 20 |
| m150 | 1.50 | 19.4507 | 5.3453 | 5/5 | 20 |

## 100-step margin gate, seeds 0-4

| policy | margin | mean reward | delta vs baseline | seed wins | seed rewards | switches |
|---|---:|---:|---:|---:|---|---:|
| baseline | - | 69.4705 | 0.0000 | - | `67.7135, 70.2252, 69.7218, 69.8245, 69.8677` | 0 |
| m100 | 1.00 | 74.1137 | 4.6431 | 4/5 | `67.6308, 76.5019, 76.3512, 72.5604, 77.5239` | 56 |
| m125 | 1.25 | 71.9741 | 2.5036 | 4/5 | `69.4432, 69.5961, 74.8974, 70.5403, 75.3935` | 46 |
| m150 | 1.50 | 71.9224 | 2.4518 | 5/5 | `68.2960, 76.2399, 72.9084, 70.5403, 71.6274` | 49 |

## 100-step robustness, seeds 0-9

| policy | mean reward | delta vs baseline | seed wins | seed deltas | switches | mean audited actions | mean true-audit sec/step |
|---|---:|---:|---:|---|---:|---:|---:|
| baseline | 68.8015 | 0.0000 | - | `-` | 0 | 1.000 | 0.0799 |
| m150 | 73.0649 | 4.2634 | 10/10 | `0.5825, 6.0147, 3.1866, 0.7158, 1.7597, 0.0029, 0.8565, 13.6481, 10.8797, 4.9877` | 92 | 8.192 | 0.4894 |

## Interpretation

The initial `margin=1.00` audit7x7 variant remains the 5-seed reward-leading setting, with mean reward `74.1137` and `+4.6431` over the 100-step baseline, but it loses seed 0 slightly. The more conservative `margin=1.50` setting lowers the 5-seed mean to `71.9224`, but wins all five initial seeds and is therefore the consistency-leading setting.

The 10-seed extension supports the consistency interpretation: `audit7x7 margin=1.50` reaches mean reward `73.0649` versus baseline `68.8015`, a `+4.2634` mean delta, and wins `10/10` matched seeds. The smallest seed delta is `+0.0029`, so this remains a descriptive matched-protocol result rather than a universal dominance claim.

## Decision

Promote `audit7x7 margin=1.50` as the current robust default for Paper10 Bishan 20x16/top5 experiments. Keep `audit7x7 margin=1.00` as the reward-leading 5-seed ablation, not as the robustness default. Continue to avoid runtime claims from generic comparison timing because true-reward audit time is recorded separately in audit rows.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_m075_audit7x7_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m125_audit7x7_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m125_audit7x7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_value_filter_blend010_selectedaudit_seeds0-9_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_blend010_seeds0-9_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit7x7_vs_blend010_10seed_100step_comparison_2026-07-07.json`
