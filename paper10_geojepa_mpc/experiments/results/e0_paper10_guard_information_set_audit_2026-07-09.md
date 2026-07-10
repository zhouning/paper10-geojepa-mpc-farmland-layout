# Paper10 guard information-set and baseline stress audit

Date: 2026-07-09

Status: guard_information_set_and_baseline_stress_audit

This audit reduces CEUS review risk by separating the current oracle/action-audit guard from no-oracle deployable proxy guards.
It reanalyzes tracked action-audit rollout rows and does not rerun training or dynamic rollouts.

## Information-Set Boundary

- Primary guard role: oracle/action-audit guard.
- Primary guard information set: `privileged_immediate_true_reward_action_audit`.
- Deployable without reward oracle: False.
- Not allowed role: not a standalone deployable no-oracle planner.
- Review risk: CEUS reviewers may treat the current guard as privileged simulator/reward access unless a learned or operational proxy guard is evaluated under the same rollout protocol.

## Statewise Audit Summary

| metric | value |
|---|---:|
| audited states | 2000 |
| switches | 172 |
| switch rate | 0.0860 |
| mean audited actions | 7.7605 |
| mean valid actions | 2285.4405 |
| selected true-reward regret mean | 0.8904 |
| selected is audit true best rate | 0.0610 |

## One-Step Policy Diagnostics

These rows are statewise immediate diagnostics, not dynamic rollout baselines.

| policy | mean true reward | delta vs selected | improves selected rate | true-best match rate |
|---|---:|---:|---:|---:|
| selected_value_filter | 0.4098 | 0.0000 | 0.0000 | 0.0000 |
| model_reward_top1_proxy | 0.6184 | 0.2085 | 0.6170 | 0.1585 |
| candidate_score_top1_proxy | 0.6367 | 0.2269 | 0.6360 | 0.1760 |
| audit_true_best_upper_bound | 1.3003 | 0.8904 | 0.9390 | 1.0000 |
| margin_true_reward_guard_executed | 0.7219 | 0.3121 | 0.0860 | 0.0000 |

## Dynamic Baseline Suite Boundary

Completed dynamic baselines:

- value_filter_20seed_rollout
- true_reward_margin_guard_20seed_rollout
- dual7x7_true_reward_guard_diagnostic

Missing dynamic baselines:

- executable_random_20seed_rollout
- greedy_immediate_true_reward_20seed_rollout
- rank_only_or_no_value_20seed_rollout
- model_reward_proxy_guard_20seed_rollout
- candidate_score_proxy_guard_20seed_rollout
- full_valid_action_oracle_upper_bound_20seed_rollout

## Claim Gates

| gate | status |
|---|---|
| statewise_proxy_screening_supported | True |
| oracle_upper_bound_statewise_supported | True |
| true_reward_guard_deployable_without_oracle | False |
| proxy_guard_rollout_superiority_supported | False |
| dynamic_baseline_suite_complete | False |
| manuscript_should_call_guard_oracle_action_audit | True |

## Claim Locks

Do not call the true-reward guard a standalone deployable no-oracle planner.
Do not claim proxy-guard rollout superiority.
Do not claim the dynamic baseline suite is complete.
Do not claim learned planner superiority from the oracle/action-audit guard alone.
