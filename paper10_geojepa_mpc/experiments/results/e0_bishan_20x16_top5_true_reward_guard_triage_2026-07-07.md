# Bishan 20x16/top5 true-reward guard triage

This experiment tests the most direct consequence of the true-reward action
audit: after the current value-filter selector proposes an action, build a small
learned top-set audit pool and execute the action with the highest actual
environment one-step reward inside that pool.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Baseline selector: `value_filter`
- Candidate score mode: `blend`
- Candidate value weight: `0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Random continuation mode: `independent`
- Stable candidate order: `False`
- Guard execution policy: `audit_true_best`
- Guard audit pool: selected action, model-reward top10, blend top10
- Guard random audit sample: 0
- Matched seeds: 0-4
- Steps per seed: 10

## Aggregate result

| metric | value |
|---|---:|
| baseline mean total reward | 14.1054 |
| true-reward guard mean total reward | 13.9578 |
| delta vs baseline | -0.1476 |
| guard seed wins | 1 / 5 |
| guard selected-action regret mean | 1.2823 |
| audit true best in model-reward top10 | 0.9800 |
| audit true best in blend top10 | 0.9800 |

The guard won seed 0 by `+4.3255`, but lost seeds 1-4. The mean penalty is
small, but the matched 5-seed gate is negative and does not justify promoting a
pure one-step true-reward policy.

## Interpretation

The positive audit result was not sufficient to make a greedy one-step true
reward guard better than the current learned rollout selector. This implies that
the one-step environment reward is useful evidence, but using it as a hard
replacement for rollout selection can break later trajectory value.

The next algorithmic candidate should therefore be a hybrid reranker/guard:
preserve the learned rollout proposal and use true one-step reward as an
additional local term or conservative veto over a small top set. This directly
targets the diagnosed selection gap without replacing rollout reasoning.

## Decision

Do not promote `audit_true_best` as the default execution policy.

Keep the stable reference as:

- `candidate_score_mode=blend`
- `candidate_value_weight=0.10`
- `top_k=50`
- `candidate_reward_reserve=0`
- `random_continuation_mode=independent`
- `stable_candidate_order=False`

Proceed to a bounded hybrid true-reward reranking experiment and require it to
beat the current `blend_w0p10` baseline on the matched 5-seed short gate before
any long-horizon escalation.

## Evidence files

- `true_reward_action_audit.py`
- `test_true_reward_action_audit.py`
- `e0_bishan_20x16_top5_true_reward_guard_blend010_seeds0-4_10step_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_guard_vs_blend010_5seed_10step_comparison_2026-07-07.json`
- `e0_bishan_20x16_top5_true_reward_guard_vs_blend010_5seed_10step_comparison_2026-07-07.md`
