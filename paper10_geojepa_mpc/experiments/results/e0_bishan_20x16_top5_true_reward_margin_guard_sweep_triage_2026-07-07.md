# Bishan 20x16/top5 true-reward margin guard sweep

This bounded sweep tests a conservative hybrid guard over the learned top set. The rollout-selected action is kept unless the audited true one-step best action exceeds it by at least the configured true-reward margin.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Baseline: `blend_w0p10_value_filter_10step`
- Candidate score mode: `blend`, value weight `0.10`
- Top-k capacity: 50
- Guard audit pool: selected action, model-reward top10, blend top10
- Random audit sample: 0
- Matched seeds: 0-4
- Steps per seed: 10

## Sweep result

| policy | margin | mean reward | delta vs baseline | seed wins | switches / states |
|---|---:|---:|---:|---:|---:|
| baseline | - | 14.1054 | 0.0000 | - | - |
| pure_guard_m000 | 0.00 | 13.9578 | -0.1476 | 1/5 | 46/50 |
| margin_m075 | 0.75 | 14.7605 | 0.6551 | 3/5 | 37/50 |
| margin_m100 | 1.00 | 19.4160 | 5.3106 | 5/5 | 28/50 |
| margin_m125 | 1.25 | 17.3828 | 3.2774 | 4/5 | 24/50 |
| margin_m150 | 1.50 | 17.4087 | 3.3033 | 3/5 | 24/50 |
| margin_m200 | 2.00 | 15.0754 | 0.9701 | 4/5 | 15/50 |

## Interpretation

Pure one-step true-reward replacement is too aggressive and remains slightly below the baseline. A margin guard changes the behavior materially: `margin=1.0` wins all five matched seeds and raises mean reward by `+5.3106` over the current short-gate baseline. Lower margin `0.75` is still too close to greedy replacement, while higher margins are increasingly conservative and lose part of the gain.

## Decision

Promote `margin_true_reward_guard` with `true_reward_switch_margin=1.0` to the next long-horizon gate. Do not promote `audit_true_best` or the more conservative `2.0` setting. Keep the existing learned filter settings (`blend`, value weight `0.10`, `top_k=50`, independent continuation) unchanged around this guard.

## Evidence files

- `e0_bishan_20x16_top5_true_reward_margin_guard_sweep_5seed_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_vs_blend010_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_vs_blend010_5seed_10step_comparison_2026-07-07.md`
