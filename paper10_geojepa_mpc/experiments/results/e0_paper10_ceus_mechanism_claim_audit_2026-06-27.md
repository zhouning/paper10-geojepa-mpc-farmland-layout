# CEUS mechanism-claim audit

Status: source-derived CEUS mechanism-claim audit.

Source-derived claim audit only; not a new rollout, training run, or inferential statistics test.

## Baseline Policy

- Default performance comparator: matched Paper9 masked baseline.
- pairwise-only evidence is retained as diagnostic/model-initialization evidence, not as the default performance comparator.

## Claim Decisions

| claim | status | key delta/count | interpretation |
|---|---|---:|---|
| matched_paper9_reward_stability | descriptive_support | 1.9269 | reward/stability comparison is descriptive only |
| executable_mask_necessity | supported | 98.0000 | no-mask failures support mask necessity, not full value-filter superiority |
| value_filter_superiority_vs_ungated | not_supported_equal_reward | 0.0000 | equal reward blocks a standalone value-filter superiority claim |
| direct_monitor_gate_reward_gain | not_supported_equal_reward | 0.0000 | monitor gate should be framed as evidence control, not direct online reward gain |
| stage3_50state_positive_scaleup | not_supported_boundary | -0.0524 | 50-state rows remain boundary evidence |

## Secondary Metric Tradeoffs

Classification: `mixed`

| metric | delta vs matched Paper9 | direction |
|---|---:|---|
| slope_change_pct_mean | 0.0138 | aligned |
| cont_change_mean | -0.0003 | tradeoff |
| baimu_area_change_ha_mean | 4.5905 | aligned |

## Interpretation Boundary

- Use this audit to police CEUS wording before manuscript conversion.
- It does not replace new multi-region validation, real-data rollout experiments, or a predefined inferential analysis plan.
- It blocks claims that the current ablation evidence does not support.
