# Paper10 CEUS review-response algorithm experiment package

Date: 2026-07-09

Status: ceus_review_response_algorithm_experiment_package

This package responds to CEUS-style review risk by reclassifying the tracked 20-seed true-reward margin guard as oracle/action-audit Bishan reward evidence.

## Source Boundary

No training or rollout was rerun for this package.
The package is not text-only: it changes the manuscript-facing evidence hierarchy using tracked confirmatory guard artifacts and explicit information-set boundaries.

## Primary Oracle Action-Audit Reward Evidence

Primary algorithm candidate: `rewardtop7 margin=1.50` true-reward margin guard for Bishan 20x16/top5.

| metric | value |
|---|---:|
| baseline mean reward | 65.8876 |
| guard mean reward | 72.1918 |
| mean delta vs baseline | 6.3041 |
| seed wins / seeds | 20 / 20 |
| seed losses / seeds | 0 / 20 |
| paired seeds | 20 |
| min seed delta | 0.0029 |
| bootstrap 95% CI lower | 4.1401 |
| bootstrap 95% CI upper | 8.5056 |
| switch rate | 0.0860 |
| switches / audited states | 172 / 2000 |
| mean audited actions | 7.7605 |
| dual7x7 mean audited actions | 8.1905 |

## Legacy Value-Filter Anchor

The 5-seed value-filter result is retained as a historical descriptive anchor, not the primary claim.

| metric | value |
|---|---:|
| baseline mean reward | 67.5437 |
| value-filter mean reward | 69.4705 |
| paired mean delta | 1.9269 |
| wins / seeds | 3 / 5 |
| losses / seeds | 2 / 5 |
| diagnostic sign-test p=1.0000 | 1.0000 |

## Secondary Metrics

Classification: `reward_primary_secondary_mixed`.

| metric | delta vs value-filter baseline | direction |
|---|---:|---|
| baimu_area_change_ha_mean | -6.6666 | tradeoff |
| cont_change_mean | 0.0007 | aligned |
| slope_change_pct_mean | -0.0063 | tradeoff |

## Mechanism Boundary

The monitor gate remains framed as monitor gate as evidence control, not as a separately proven online reward-gain mechanism.

| gate | value |
|---|---|
| monitor gate direct reward gain supported | False |
| monitor gate evidence control supported | True |
| executable mask necessity supported | True |
| no-mask negative zero-swap steps | 98.0000 |

## Guard Information-Set Boundary

Primary guard role: oracle/action-audit guard.
The current true-reward guard is not a standalone deployable no-oracle planner.

| diagnostic | value |
|---|---:|
| deployable without reward oracle | False |
| audited states | 2000 |
| selected true-reward regret mean | 0.8904 |
| model_reward_top1_proxy delta vs selected | 0.2085 |
| candidate_score_top1_proxy delta vs selected | 0.2269 |

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
| primary_guard_promoted_to_main_algorithm_candidate | False |
| primary_guard_recorded_as_oracle_action_audit_reward_evidence | True |
| primary_guard_confirmatory_20seed_supported | True |
| old_5seed_value_filter_primary_claim_blocked | True |
| bootstrap_ci_lower_positive | True |
| all_primary_seeds_improve | True |
| secondary_metrics_uniformly_aligned | False |
| monitor_gate_online_reward_gain_supported | False |
| monitor_gate_evidence_control_supported | True |
| executable_mask_necessity_supported | True |
| direct_50state_scaleup_supported | False |
| robust_transfer_superiority_supported | False |
| deployment_ready_cadastral_planning_supported | False |
| submission_story_should_use_guard_as_primary | False |
| submission_story_should_use_guard_as_oracle_action_audit_evidence | True |
| true_reward_guard_deployable_without_oracle | False |
| proxy_guard_rollout_superiority_supported | False |
| dynamic_baseline_suite_complete | False |
| manuscript_should_call_guard_oracle_action_audit | True |

## Manuscript Sync Actions

- Present the 20-seed rewardtop7 true-reward margin guard as oracle/action-audit Bishan reward evidence, not as a deployable no-oracle algorithm.
- Move the 5-seed value-filter result to historical descriptive anchor and comparator context.
- Report secondary planning metrics as mixed rather than uniformly improved.
- Frame the monitor gate as evidence control, not direct online reward gain.
- Frame the true-reward guard as an oracle/action-audit guard, not a standalone deployable no-oracle planner.
- Treat proxy-guard and stronger dynamic baselines as unresolved experiment risks.

## Claim Locks

Do not claim uniform secondary-metric improvement.
Do not claim direct monitor-gate online reward gain.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not call the true-reward guard a standalone deployable no-oracle planner.
Do not claim proxy-guard rollout superiority.
Do not claim a complete dynamic baseline suite.
