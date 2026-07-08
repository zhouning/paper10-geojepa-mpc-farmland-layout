# Paper10 10x12 Guard 20-Seed Confirmation Design

## Purpose

Extend the current Bishan 10x12/top4 small-scale true-reward guard evidence from
5 matched rollout seeds to 20 matched rollout seeds. The goal is to test whether
the setting-specific `rewardtop7 margin=1.60` guard remains positive when the
small-scale support set is widened, without changing the current Paper10 primary
20x16/top5 guard or claiming a universal switch margin.

## Current Evidence

The current post-guard readiness audit records:

- primary guard: Bishan 20x16/top5, `rewardtop7 margin=1.50`, 20 seeds, mean
  delta `+6.3041` versus the matched `blend_w0p10` baseline, 20/20 seed wins;
- small-scale guard: Bishan 10x12/top4, `rewardtop7 margin=1.60`, 5 seeds, mean
  delta `+7.0253` versus the matched `blend_w0p10` baseline, 5/5 seed wins;
- boundary: the switch margin is setting-specific, not universal.

The 10x12/top4 evidence is currently weaker than the 20x16/top5 evidence because
it has only five matched seeds. This design widens that support set while keeping
the protocol fixed.

## Protocol

The confirmation uses the existing 10x12/top4 value-head checkpoint:

`paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt`

Baseline configuration:

- script: `paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke`
- selector: `value_filter`
- mask mode: `executable`
- horizon: `5`
- top-k: `50`
- rollout steps: `100`
- candidate score mode: `blend`
- candidate value weight: `0.10`
- random continuation mode: `independent`
- stable candidate order: `false`
- seeds: `0-19`

Guard configuration:

- script: `paper10_geojepa_mpc.experiments.true_reward_action_audit`
- execution policy: `margin_true_reward_guard`
- true reward switch margin: `1.60`
- audit set: selected action plus model-reward top7 actions
- audit random sample: `0`
- audit top candidate count: `0`
- all baseline settings otherwise unchanged
- seeds: `0-19`

The existing seeds `0-4` baseline and guard artifacts remain source inputs. The
new run adds seeds `5-19` and then builds a combined 20-seed evidence packet.

## Outputs

The implementation will create:

- raw baseline seeds `5-19` JSON;
- raw guard seeds `5-19` JSON;
- combined baseline seeds `0-19` JSON;
- combined guard seeds `0-19` JSON;
- 20-seed baseline-versus-guard comparison JSON and Markdown;
- 20-seed paired-statistics JSON;
- 20-seed confirmation triage Markdown.

## Decision Rules

The 10x12/top4 confirmation passes its bounded support check if:

- the combined packet contains exactly seeds `0-19` for both baseline and guard;
- every paired seed has both baseline and guard rewards;
- the mean paired reward delta is positive;
- seed wins are reported explicitly;
- the bootstrap 95% confidence interval is reported as descriptive evidence.

If the guard loses one or more seeds, the result remains valid evidence and must
be reported directly. The output must not tune a new margin after seeing the
20-seed result in this task.

## Claim Boundary

Allowed claim:

- `rewardtop7 margin=1.60` has 20-seed descriptive support as the current
  10x12/top4 setting-specific guard if the observed 20-seed result is positive.

Forbidden claims:

- universal fixed switch margin;
- direct 50-state Bishan scale-up success;
- robust Bishan-to-Dongxing transfer superiority;
- deployment-ready cadastral planning;
- final submission readiness.

This task does not resolve repository DOI, licence, generated-data rights, full
data access, citation policy, statistical-reporting policy, reviewer access, or
journal-specific figure/export rules.
