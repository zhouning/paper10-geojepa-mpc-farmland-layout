# Bishan 20x16/top5 true-reward margin guard long-horizon triage

This long-horizon gate tests the short-gate winner from the true-reward margin sweep: keep the learned value-filter rollout action unless the audited true one-step best action is at least `1.0` reward unit better than the selected action. The guard audits only the selected action, model-reward top10, and blend top10; it does not search all valid actions.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Baseline: `blend_w0p10_value_filter_100step`
- Candidate: `blend_w0p10_margin_true_reward_guard_m100_100step`
- Candidate score mode: `blend`, value weight `0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Random continuation mode: `independent`
- Stable candidate order: `False`
- Guard audit pool: selected action, model-reward top10, blend top10
- Guard random audit sample: 0
- True-reward switch margin: `1.0`
- Matched seeds: 0-4
- Steps per seed: 100

## Long-horizon result

| metric | baseline | margin guard | delta |
|---|---:|---:|---:|
| mean total reward | 69.4705 | 71.8745 | +2.4040 |
| seed wins | - | 4 / 5 | - |
| mean slope change pct | -1.2507 | -1.2888 | -0.0381 |
| mean contiguity change | 0.0192 | 0.0200 | +0.0007 |
| mean baimu area change ha | -207.2639 | -206.4647 | +0.7993 |

| seed | baseline reward | margin guard reward | delta |
|---:|---:|---:|---:|
| 0 | 67.7135 | 69.6535 | +1.9400 |
| 1 | 70.2252 | 66.3351 | -3.8901 |
| 2 | 69.7218 | 78.9865 | +9.2646 |
| 3 | 69.8245 | 72.2619 | +2.4374 |
| 4 | 69.8677 | 72.1358 | +2.2681 |

## Guard behavior

| metric | value |
|---|---:|
| audited states | 500 |
| guard switches | 63 / 500 |
| selected action is audit true-best | 0.0640 |
| selected true-reward regret mean | 0.7656 |
| mean audited action count | 11.3040 |
| mean true-reward audit time per step | 0.6321 sec |

Timing fields in the generic rollout comparison should not be read as speed improvements, because the new script stores the true-reward audit cost separately from `select_time_sec`. The algorithmic conclusion is about reward behavior, not runtime.

## Interpretation

The margin guard survives the long-horizon reversal test that rejected earlier short-positive variants (`common` continuation and stable candidate order). It improves mean 100-step reward by `+2.4040` over the current `blend_w0p10` long-horizon reference and wins 4/5 matched seeds. The remaining seed1 loss means the result should still be reported as descriptive matched-seed evidence, not every-seed dominance.

The improvement is mechanistically consistent with the diagnostic chain: the learned top set contains high true one-step reward actions, pure one-step greedy replacement is too aggressive, and a margin guard preserves rollout selection except when the one-step evidence is large enough.

## Decision

Promote `margin_true_reward_guard` with `true_reward_switch_margin=1.0` as the current best Paper10 algorithmic variant for Bishan 20x16/top5 experiments. Keep `blend_w0p10`, `top_k=50`, reward reserve 0, independent continuation, and `stable_candidate_order=False` unchanged around it.

Do not claim every-seed superiority or runtime improvement. The next algorithmic work should reduce the guard cost and test whether the same margin rule remains positive when the audit set is smaller or the true one-step reward is approximated without full environment snapshot/restore.

## Evidence files

- `true_reward_action_audit.py`
- `test_true_reward_action_audit.py`
- `e0_bishan_20x16_top5_true_reward_margin_guard_sweep_5seed_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_sweep_triage_2026-07-07.md`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_blend010_seeds0-4_100step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_vs_blend010_5seed_100step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_margin_guard_m100_vs_blend010_5seed_100step_comparison_2026-07-07.md`
