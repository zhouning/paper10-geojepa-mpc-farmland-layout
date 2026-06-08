# E0 value-label strategy diagnostics

Date: 2026-06-08

## Purpose

This note records the current evidence for Paper10 value-head training. The question is whether the value labels add useful long-horizon ranking information, and whether the current candidate generation policy is suitable for scaling.

## Compared label sets

| label set | states | candidates | top-k | candidate mode | continuation | diagnostic file |
|---|---:|---:|---:|---|---|---|
| random 20x20 | 20 | 20 | 5 | random | random | `e0_value_label_diagnostics_20x20_h3_seed1_top5.json` |
| frontier 20x50 | 20 | 50 | 5 | reward-head frontier | random | `e0_value_label_diagnostics_frontier_rank_seed2028_20x50_h3_seed2_top5.json` |
| frontier_random 5x8 | 5 | 8 | 3 | 50% frontier + random | random | `e0_value_label_diagnostics_frontier_random050_rank_seed2028_5x8_h3_seed31_top3.json` |
| frontier_random 8x12 partial | 8 | 12 | 5 | 50% frontier + random | random | `e0_value_label_diagnostics_frontier_random050_rank_seed2028_8x12_h3_seed37partial_top5.json` |

## Key metrics

| label set | residual/return std ratio | one-step top1 disagreement | one-step top-k overlap | one-step top-k regret | candidate-score pearson | candidate top1 disagreement | candidate top-k overlap | candidate top-k regret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| random 20x20 | 0.9353 | 0.8000 | 0.5600 | 0.4706 | n/a | n/a | n/a | n/a |
| frontier 20x50 | 0.8657 | 0.7000 | 0.4400 | 1.6319 | 0.0556 | 0.9000 | 0.1900 | 0.9834 |
| frontier_random 5x8 | 0.6372 | 0.6000 | 0.7333 | 0.0000 | 0.5496 | 0.8000 | 0.5333 | 1.2916 |
| frontier_random 8x12 partial | 0.7203 | 0.5000 | 0.7750 | 0.0000 | 0.4135 | 1.0000 | 0.7250 | 0.0000 |

## Interpretation

The existing labels are not just immediate reward labels. Both 20-state datasets show substantial residual variation: `returns - one_step_rewards` has a per-state standard deviation comparable to the return labels themselves. Immediate reward also disagrees with multi-step return on the top action in 70% to 80% of states. This supports keeping a separate long-horizon value objective.

The weak branch is the old frontier label set. The candidate scores used to build the frontier candidates have almost no flat correlation with realized return (`pearson_flat = 0.0556`) and only 19% top-5 overlap with the true return top-5. This explains why the independent value head did not improve 5-seed rollout performance: the label set contains useful return variation, but the candidate distribution is biased by a score that does not reliably identify long-horizon winners.

The `frontier_random` candidate mode improved top-k coverage in small samples. In the 8x12 partial run, candidate-score top-5 already covers the realized return optimum with zero top-k regret, and candidate-score/return correlation is much higher than the old frontier set. However, candidate top1 remains unreliable. This means the value signal should be used for top-k filtering or reranking, not as a greedy top1 replacement.

## Compute implication

Local Windows can run smoke experiments, tests, diagnostics, and small label sets. It is not efficient for larger value-label generation: `frontier_random` 5x8 took about 200.6 seconds, and a 10x12 run reached only 8 states before the 480 second timeout. The bottleneck is mostly environment state restore and rollout simulation, not only neural network scoring, so a GPU alone will not fully solve it.

Colab Pro+ is still useful for model training and batched scoring once label files exist. For label generation, it is only worth using if the full Paper9 environment and prepared data can run correctly there. The new partial-output path reduces risk: interrupted runs now leave a usable `.partial.npz`.

## Next design decision

Do not scale the old independent value-head training yet. The next experiment should use a larger `frontier_random` label set with partial output, then train the independent value head on top-k ranking quality rather than optimizing for top1 behavior.

## Monitor check

The new `value_label_monitor` script was run on the 8x12 `frontier_random` partial file:

| monitor | decision | candidate top-k regret | candidate top-k overlap | one-step top-k regret | interpretation |
|---|---|---:|---:|---:|---|
| top-3 | `continue` | 0.5866 | 0.4167 | 1.4871 | top-3 is still hard enough that multi-step labels add useful filtering signal |
| top-5 | `stop` | 0.0000 | 0.7250 | 0.0000 | top-5 is too permissive for this partial file because one-step reward already covers the best return action |

Use top-3 as the primary continuation rule for the next 24-candidate label run. Top-5 remains useful as a sanity check, but it is not strict enough to decide whether value-head training will add value.

## Value-head training smoke

The new `run_e0_value_head_train` entry point was smoke-tested on the 5x8 `frontier_random` label set with `trainable_scope=value_head`, `rank_score_mode=value`, and checkpoint selection by `candidate_top3_regret`.

Output: `e0_frontier_random050_value_head_smoke_5x8_h3_seed31.json`

| metric | value |
|---|---:|
| epochs | 1 |
| pairwise states | 5 |
| transition samples | 256 |
| ranking accuracy | 0.7000 |
| train ranking accuracy | 0.8333 |
| candidate top1 hit rate | 0.6000 |
| candidate top1 regret | 1.1943 |
| candidate top3 hit rate | 0.8000 |
| candidate top3 regret | 0.0441 |
| elapsed seconds | 107.5560 |

This validates the training entry point and checkpoint wiring. It is not a performance claim because the label set is intentionally tiny.

Recommended next controlled experiment:

1. Generate `frontier_random` labels with `n_states=50`, `candidate_actions=24`, `label_horizon=5`, `frontier_fraction=0.5`, `progress_every=2`.
2. Diagnose the partial file every 10 states. Continue only if candidate-score top-5 regret remains near zero and one-step top-k regret remains materially above zero.
3. Train an independent value head on the resulting labels, with validation focused on `candidate_top5_regret`, not only ranking accuracy.
4. Test planner integration as candidate filtering with blend weights `0.02`, `0.05`, and `0.10`; do not use value-head top1 scoring as the main policy.

Stop rule before 5-seed rollout: a single seed 100-step rollout must beat both the original seed0 baseline and the previous unstable value-filter seed0 run.
