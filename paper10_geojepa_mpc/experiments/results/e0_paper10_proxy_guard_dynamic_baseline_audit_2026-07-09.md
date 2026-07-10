# Paper10 proxy guard dynamic baseline stress audit

Date: 2026-07-09

Status: proxy_guard_dynamic_baseline_stress_audit

This audit records new 5-seed dynamic rollouts for no-oracle score-margin proxy guards.
It is a stress test, not a 20-seed confirmation.

## Baseline

| policy | n | mean reward | sample std |
|---|---:|---:|---:|
| value_filter_5seed_anchor | 5 | 69.4705 | 1.0004 |

## Proxy Dynamic Rollouts

| policy | n | mean reward | delta vs value filter | switch rate | better switches | worse switches |
|---|---:|---:|---:|---:|---:|---:|
| model_reward_proxy_guard_m010 | 5 | 65.2734 | -4.1971 | 0.1980 | 79 | 20 |
| candidate_score_proxy_guard_m010 | 5 | 63.4116 | -6.0589 | 0.1960 | 77 | 21 |

## Claim Gates

| gate | status |
|---|---|
| model_reward_proxy_beats_value_filter_5seed_mean | False |
| candidate_score_proxy_beats_value_filter_5seed_mean | False |
| no_oracle_proxy_guard_superiority_supported | False |
| proxy_guard_20seed_confirmation_complete | False |
| true_reward_guard_remains_oracle_action_audit | True |
| manuscript_should_not_promote_proxy_guard | True |

## Interpretation

The tested no-oracle score-margin proxy guards did not beat the 5-seed value-filter anchor, so statewise proxy gains should not be converted into a dynamic rollout superiority claim.

Do not claim proxy-guard rollout superiority.
Do not present the true-reward guard as a deployable no-oracle policy.
