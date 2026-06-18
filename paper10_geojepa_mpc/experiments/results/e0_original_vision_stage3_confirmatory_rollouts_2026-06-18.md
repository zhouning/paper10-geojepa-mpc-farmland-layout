# Paper10 Original-Vision Stage 3 Confirmatory Rollouts

Date: 2026-06-18

Status: value-filter rollouts complete for authorized Bishan rows; matched Paper9 baseline complete; pairwise-only baseline remains pending unless treated as the Paper9 rank-checkpoint baseline by explicit author decision.

## Settings

- code commit: `6c3535755a20d3ba1dcd2d59d566bb76b3feecdd`
- rollout seeds: `0,1,2,3,4`
- rollout steps: `100`
- horizon: `5`
- global top-k: `50`
- mask mode: `executable`
- value-filter scoring: `candidate_score_mode=blend`, `candidate_value_weight=0.1`
- raw local output root: `D:/test/paper10_original_vision_validation/stage3_colab_handoff`

## Matched Paper9 Baseline

| family | mean reward | sample std | min | max | slope mean % | cont mean | baimu ha mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| paper9 rank_seed2028 | 67.5437 | 7.2246 | 60.7625 | 78.0925 | -1.2645 | 0.0195 | -211.8544 |

## Authorized Row Results

| role | run | selected top-k | mean reward | sample std | value minus Paper9 | slope mean % | cont mean | baimu ha mean | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| frozen_anchor | `frontier_random050_20x16_h5_seed44_f050` | 5 | 69.4705 | 1.0004 | 1.9269 | -1.2507 | 0.0192 | -207.2639 | anchor_reproduction_from_tracked_evidence |
| confirmatory_pass | `frontier_random050_50x16_h5_seed48_f050` | 6 | 64.2960 | 4.2503 | -3.2477 | -1.2660 | 0.0201 | -215.8683 | stage3_value_filter_complete |
| confirmatory_pass | `frontier_random050_50x24_h5_seed47_f075` | 12 | 66.2544 | 4.8565 | -1.2893 | -1.2538 | 0.0200 | -213.9300 | stage3_value_filter_complete |
| diagnostic_near_pass | `frontier_random050_50x24_h5_seed48_f075` | 12 | 67.4913 | 4.5711 | -0.0524 | -1.2665 | 0.0207 | -211.0930 | diagnostic_value_filter_complete |

## Seed-Level Rewards

| run | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---:|---:|---:|---:|---:|
| `paper9_rank_seed2028` | 70.9543 | 66.6115 | 61.2976 | 60.7625 | 78.0925 |
| `frontier_random050_20x16_h5_seed44_f050` | 67.7135 | 70.2252 | 69.7218 | 69.8245 | 69.8677 |
| `frontier_random050_50x16_h5_seed48_f050` | 61.3389 | 60.8596 | 71.0890 | 62.4408 | 65.7518 |
| `frontier_random050_50x24_h5_seed47_f075` | 65.3712 | 62.3169 | 61.0486 | 70.6791 | 71.8560 |
| `frontier_random050_50x24_h5_seed48_f075` | 61.6214 | 66.8520 | 72.7732 | 64.9377 | 71.2723 |

## Interpretation Lock

- The two Stage 1 pass rows completed Stage 3 value-filter rollout, but neither exceeded the matched Paper9 rank-checkpoint baseline on five-seed mean reward.
- The diagnostic near-pass row is reported only as diagnostic evidence and must not be pooled with confirmatory pass rows.
- These results do not authorize a broad 50-state deployment or scale claim.
- Pairwise-only baseline wording remains unresolved unless the Paper9 rank-checkpoint baseline is explicitly accepted as that comparator.
- Do not change the manuscript claim until the baseline policy and final summary are reviewed.
