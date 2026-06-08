# E0 value-head rollout comparison with value-filter

| run | selector | H | model score | candidate score | total reward | slope % | cont | baimu ha |
|---|---:|---:|---|---|---:|---:|---:|---:|
| original_h5_reward | paper9 | 5 | reward |  | 70.9543 | -1.2933 | 0.01846 | -234.37 |
| original_h1_reward | paper9 | 1 | reward | None | 56.6428 | -1.2387 | 0.01836 | -195.64 |
| frontier_reward_head_h5_reward | paper9 | 5 | reward | None | 59.1869 | -1.2169 | 0.01841 | -203.27 |
| frontier_reward_head_h1_reward | paper9 | 1 | reward | None | 60.7865 | -1.2476 | 0.01805 | -203.57 |
| independent_value_h1_value_as_reward | paper9 | 1 | value | None | 68.0870 | -1.2369 | 0.01963 | -162.14 |
| independent_value_h5_value_as_reward | paper9 | 5 | value | None | 67.9265 | -1.2172 | 0.02070 | -158.56 |
| independent_value_h5_blend025_as_reward | paper9 | 5 | blend | None | 61.5477 | -1.2710 | 0.02243 | -221.38 |
| independent_value_h5_blend010_as_reward | paper9 | 5 | blend | None | 66.7825 | -1.2861 | 0.01938 | -222.04 |
| independent_value_h5_value_filter_reward_rollout | value_filter | 5 | reward | value | 71.6428 | -1.2258 | 0.01734 | -187.89 |
| independent_value_h5_value_filter_candidate_blend010_reward_rollout | value_filter | 5 | reward | blend | 72.0001 | -1.3113 | 0.01922 | -220.48 |
