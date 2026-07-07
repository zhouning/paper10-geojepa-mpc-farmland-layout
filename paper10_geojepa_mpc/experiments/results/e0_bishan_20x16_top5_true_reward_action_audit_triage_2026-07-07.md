# Bishan 20x16/top5 true-reward action audit triage

This diagnostic follows the current value-filter policy and audits sampled candidate
actions with the actual environment one-step reward. It is designed to distinguish
three possible failure modes:

1. the candidate pool misses high-reward actions,
2. the learned reward/blend scores misrank true one-step environment reward,
3. the rollout selection chooses actions that are not strong under true one-step
   environment reward even though they are present in the learned top set.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Selector: `value_filter`
- Candidate score mode: `blend`
- Candidate value weight: `0.10`
- Top-k capacity: 50
- Reward reserve: 0
- Random continuation mode: `independent`
- Stable candidate order: `False`
- Audit seeds: 0-4
- Audit steps per seed: 3
- Audit action set per state: selected action, top model-reward actions, top blend
  actions, and a fixed random sample
- Total audited states: 15

## Aggregate result

| metric | value |
|---|---:|
| audited states | 15 |
| selected action is audit true-reward best | 0.0000 |
| selected true-reward regret mean | 1.9360 |
| selected true-reward regret max | 2.5022 |
| audit true-reward best in model-reward top10 | 1.0000 |
| audit true-reward best in blend top10 | 1.0000 |
| true reward vs model-reward Pearson mean | 0.7701 |
| true reward vs blend Pearson mean | 0.7680 |
| true reward vs model-reward Spearman mean | 0.9264 |
| true reward vs blend Spearman mean | 0.9269 |

Per-seed selected-action true-reward regret means were `1.8800`, `1.7538`,
`2.0051`, `1.7262`, and `2.3150`. The selected action was never the best true
one-step reward action inside the audited action set.

## Interpretation

The high-level candidate pool is not the bottleneck. The true one-step best action in
the audited set was always present in both the model-reward top10 and blend top10.
The learned scores are also strongly rank-correlated with sampled true one-step
environment reward.

The failure is downstream of candidate inclusion: the MPC rollout selector frequently
chooses an action that is not the best under true one-step environment reward among
nearby high-scoring alternatives. This is consistent with the earlier long-horizon
negative results for `common`, `stable_candidate_order`, reward reserve, and scalar
weight changes: those knobs do not address the immediate true-reward selection gap.

## Decision

Stop treating the problem as a candidate-filter capacity or scalar-score calibration
issue. The next algorithmic candidate should add a true-reward-aware guard or
reranking stage over a small learned top set, then test whether that improves the
matched rollout reward without relying on an oracle over all valid actions.

A bounded next experiment is:

- form a small audit/rerank set from the selected action, model-reward top actions,
  and blend top actions;
- evaluate actual environment one-step reward for only that small set;
- select either the true one-step best action or a conservative blend of learned
  rollout score and true one-step reward;
- compare against the current `blend_w0p10` baseline on the same short 5-seed gate
  before any 100-step escalation.

## Evidence files

- `true_reward_action_audit.py`
- `test_true_reward_action_audit.py`
- `e0_bishan_20x16_top5_true_reward_action_audit_blend010_seeds0-4_3step_2026-07-07.json`
