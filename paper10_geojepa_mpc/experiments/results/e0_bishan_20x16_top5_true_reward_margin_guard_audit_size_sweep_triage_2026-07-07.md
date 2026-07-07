# Bishan 20x16/top5 true-reward guard audit-size sweep

This experiment reduces the true-reward margin guard audit set while keeping the learned filter and margin rule fixed. The tested policy is `margin_true_reward_guard` with `true_reward_switch_margin=1.0`, `candidate_score_mode=blend`, value weight `0.10`, `top_k=50`, reward reserve 0, independent continuation, and no random audit sample.

## 10-step gate

| audit set | mean reward | delta vs baseline | seed rewards | switches | mean audited actions | mean true-audit sec/step |
|---|---:|---:|---|---:|---:|---:|
| baseline | 14.1054 | 0.0000 | `9.7064, 16.3140, 14.7417, 15.5221, 14.2427` | 0 | - | - |
| audit3x3 | 16.1640 | 2.0586 | `20.8977, 16.4465, 16.5101, 15.7667, 11.1990` | 17 | 4.020 | 0.2551 |
| audit5x5 | 18.1828 | 4.0774 | `20.8977, 21.3708, 16.5101, 15.7667, 16.3685` | 19 | 6.220 | 0.3819 |
| audit7x7 | 19.1802 | 5.0749 | `20.8977, 21.3708, 21.4975, 15.7667, 16.3685` | 20 | 8.420 | 0.5032 |
| audit10x10 | 19.4160 | 5.3106 | `21.9446, 20.8555, 21.4975, 16.7746, 16.0078` | 28 | 11.080 | 0.6380 |

## 100-step gate

| audit set | mean reward | delta vs baseline | seed wins | seed rewards | switches | mean audited actions | mean true-audit sec/step |
|---|---:|---:|---:|---|---:|---:|---:|
| baseline | 69.4705 | 0.0000 | - | `67.7135, 70.2252, 69.7218, 69.8245, 69.8677` | 0 | - | - |
| audit5x5 | 72.9160 | 3.4455 | 4/5 | `72.6920, 76.4548, 79.8384, 63.0764, 72.5185` | 52 | 6.202 | 0.3700 |
| audit7x7 | 74.1137 | 4.6431 | 4/5 | `67.6308, 76.5019, 76.3512, 72.5604, 77.5239` | 56 | 8.318 | 0.6436 |
| audit10x10 | 71.8745 | 2.4040 | 4/5 | `69.6535, 66.3351, 78.9865, 72.2619, 72.1358` | 63 | 11.304 | 0.6321 |

## Interpretation

The guard does not need the full 10x10 learned audit pool. The 3x3 short gate remains positive but loses too much reward and is not escalated. The 5x5 guard is the lower-cost positive variant: in the 100-step gate it reaches mean reward `72.9160`, `+3.4455` over baseline, with `4/5` seed wins and mean audited actions reduced from `11.304` in full 10x10 to `6.202`.

The 7x7 guard is the reward-leading variant: in the 100-step gate it reaches mean reward `74.1137`, `+4.6431` over baseline, with `4/5` seed wins. It also beats the 10x10 full guard mean (`71.8745`) and the 5x5 mean (`72.9160`), although timing should remain a secondary claim because trajectory-dependent environment state changes make per-step wall time noisy.

## Decision

Promote `audit7x7` as the current reward-leading Paper10 Bishan 20x16/top5 algorithmic variant. Keep `audit5x5` as the cost-ablation positive variant. Do not shrink to `audit3x3` for the main long-horizon claim. Continue to avoid claims of every-seed superiority: both 5x5 and 7x7 win `4/5` seeds against the current baseline.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit3x3_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit5x5_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit7x7_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit5x5_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit7x7_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit5x5_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit7x7_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_audit7x7_vs_audit5x5_5seed_100step_comparison_2026-07-07.json`
