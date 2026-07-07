# Bishan 20x16/top5 ranking-failure overlap triage

This diagnostic checks whether the current `blend_w0p10` value-filter policy is failing
because the candidate filter misses the model-reward top actions. The test compares
model one-step reward scores against the `blend` candidate scores over reward-top1
rollout states.

## Locked setting

- Environment/data anchor: Bishan E0, prepared under `D:\test`
- Grid and checkpoint: 20x16, horizon 5, top5-trained value head
- Candidate score mode: `blend`
- Candidate value weight: `0.10`
- Top-k capacity: 50
- Mask: executable actions
- Seeds: 0-4
- States per seed: 20
- Total diagnostic states: 100

## Aggregate diagnostic result

| metric | value |
|---|---:|
| states | 100 |
| mean top50 overlap fraction, reward vs blend | 0.9700 |
| reward-top1 in blend top50 rate | 1.0000 |
| blend-top1 in reward top50 rate | 1.0000 |
| blend-top1 reward regret mean | 0.0023 |
| blend-top50 best reward regret mean | 0.0000 |
| score Pearson mean | 0.99998 |
| score Spearman mean | 0.99982 |

Per-seed summaries were identical in the main coverage metrics: each seed ran 20
states, had mean reward/blend top50 overlap `0.9700`, had reward-top1 in blend top50
rate `1.0000`, and had blend-top50 best reward regret `0.0000`.

## Interpretation

The immediate candidate-filter stage is not the current bottleneck under the model
reward score. The blend top50 candidate pool consistently contains the model-reward
top action, and the best model-reward action inside the blend top50 has zero regret
relative to the model-reward top action across these 100 diagnostic states.

This explains why local scalar-weight tuning around `blend_w0p10` has not improved
the long-horizon result: `blend_w0p10` is already almost collinear with the model
one-step reward score on this anchor. The remaining failure mode is therefore more
likely downstream:

- the model one-step reward can be misaligned with realized long-horizon environment
reward,
- the rollout continuation can amplify early local choices,
- the learned value head may not provide enough independent long-horizon information
inside this real Bishan state distribution.

## Decision

Do not continue blind tuning of top-k, scalar blend weight, candidate reserve, common
continuation, or stable candidate ordering for this anchor. Those knobs have now been
bounded by matched experiments or diagnostics.

The next algorithm work should target long-horizon value/rollout alignment directly.
Useful next candidates are:

- a diagnostic that compares selected actions against sampled true one-step environment
  rewards on the actual value-filter trajectory,
- value-head retraining or calibration against longer-horizon labels for the real
  Bishan 20x16/top5 state distribution,
- a conservative long-horizon guard that rejects actions with poor realized one-step
  environment reward when the learned rollout score is high.

## Evidence files

- `e0_bishan_20x16_top5_value_filter_candidate_overlap_blend010_seed0_20step_2026-07-07.json`
- `e0_bishan_20x16_top5_value_filter_candidate_overlap_blend010_seed1_20step_2026-07-07.json`
- `e0_bishan_20x16_top5_value_filter_candidate_overlap_blend010_seed2_20step_2026-07-07.json`
- `e0_bishan_20x16_top5_value_filter_candidate_overlap_blend010_seed3_20step_2026-07-07.json`
- `e0_bishan_20x16_top5_value_filter_candidate_overlap_blend010_seed4_20step_2026-07-07.json`
