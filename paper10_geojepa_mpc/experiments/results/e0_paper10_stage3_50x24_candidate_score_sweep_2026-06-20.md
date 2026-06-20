# Paper10 Stage 3 50x24 Candidate-Score Sweep

Date: 2026-06-20

This note checks whether the current `frontier_random050 50x24/h5 seed48 f075`
value head can be rescued by changing only the candidate filtering score inside
`selector=value_filter`. The rollout protocol is unchanged. Candidate scoring
only changes which top-k candidates are passed into the reward rollout; the
final action is still chosen by the horizon-5 reward rollout among those
candidates.

## Source Data

- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\baseline_paper9_rank_seed2028_h5_k50_seeds0-4_100step.json`
- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_filter_blend010_h5_k50_seeds0-4_100step.json`
- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_filter_blend005_h5_k50_seeds0-4_100step.json`
- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_filter_value_h5_k50_seeds0-4_100step.json`
- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_filter_blend015_h5_k50_seeds0-4_100step.json`
- `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_filter_blend025_h5_k50_seeds0-4_100step.json`

## Common Settings

| setting | value |
|---|---|
| environment source | `paper9` |
| prepared dir | `D:\test` |
| rollout seeds | `0-4` |
| rollout steps | `100` |
| horizon | `5` |
| top-k | `50` |
| mask mode | `executable` |
| selector | `value_filter` |
| checkpoint | `D:\test\paper10_original_vision_validation\stage3_colab_handoff\frontier_random050_50x24_h5_seed48_f075\value_head_top12_seed3048.pt` |

## Sweep Results

| run | selector | candidate score mode | value weight | mean total reward | sd | min | max | delta vs paper9 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| paper9 baseline | `paper9` | n/a | n/a | 67.543670 | 7.224554 | 60.762474 | 78.092463 | 0.000000 |
| existing blend010 | `value_filter` | `blend` | 0.10 | 67.491314 | 4.571073 | 61.621435 | 72.773186 | -0.052356 |
| blend025 | `value_filter` | `blend` | 0.25 | 65.897065 | 5.512595 | 60.462442 | 73.638443 | -1.646605 |
| blend005 | `value_filter` | `blend` | 0.05 | 63.645012 | 7.441492 | 52.355880 | 71.870398 | -3.898658 |
| value | `value_filter` | `value` | 0.50 | 63.184904 | 8.338900 | 48.927801 | 69.466534 | -4.358766 |
| blend015 | `value_filter` | `blend` | 0.15 | 62.739750 | 3.821549 | 59.713334 | 67.656624 | -4.803920 |

## Interpretation

- `blend0.10` remains the best of the candidate-filter variants, but it still
  does not beat the paper9 baseline.
- Pure `value` filtering is materially worse on this checkpoint.
- Candidate-score tuning can reduce variance, but it does not recover a
  positive mean-reward result on the current 50x24/f075 line.
- This 50-state line remains boundary evidence; no new positive claim is
  justified.

