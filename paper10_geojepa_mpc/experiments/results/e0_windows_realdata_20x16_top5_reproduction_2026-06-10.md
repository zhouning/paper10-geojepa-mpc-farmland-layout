# Windows Real-Data 20x16/top5 Reproduction

Date: 2026-06-10

This note records a full Windows rerun of the Paper10 E0
`frontier_random050 20x16/h5 seed44 top5` evidence path using the local Bishan
real-data root at `D:\test`. The run was done after confirming that the full
data were available outside the repository root.

The reproduction used:

- Data root: `D:\test`
- Rank checkpoint:
  `paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt`
- Full transition input:
  `D:\test\tool2\transitions.npz`
- Explicit prepared root flag for environment-based commands:
  `--prepared-dir D:\test`

The generated reproduction outputs were kept under `reviewer_outputs\` and are
not tracked by git.

## 1. Value-Label Generation

Command parameters:

- `--n-states 20`
- `--candidate-actions 16`
- `--label-horizon 5`
- `--gamma 0.99`
- `--seed 44`
- `--mask-mode executable`
- `--candidate-mode frontier_random`
- `--frontier-fraction 0.5`
- `--advance-policy random`
- `--continuation-policy random`
- `--prepared-dir D:\test`

Output:

`reviewer_outputs\realdata_repro_e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`

Summary:

| metric | value |
|---|---:|
| elapsed sec | 218.4910674999992 |
| states generated | 20 |
| candidate actions | 16 |
| return mean | 1.4419478178024292 |
| return std | 4.164623260498047 |
| one-step reward mean | 0.985366702079773 |
| one-step reward std | 2.9745426177978516 |
| candidate score mean | 0.42427149415016174 |
| candidate score std | 0.8070693016052246 |

Array-level comparison against the tracked canonical artifact:

`paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`

| array | shape | result |
|---|---:|---|
| `states_bf` | `(20, 2600, 17)` | exact match, max abs diff 0 |
| `states_gf` | `(20, 12)` | exact match, max abs diff 0 |
| `actions` | `(20, 16)` | exact match |
| `returns` | `(20, 16)` | exact match, max abs diff 0 |
| `one_step_rewards` | `(20, 16)` | exact match, max abs diff 0 |
| `state_steps` | `(20,)` | exact match |
| `n_valid_actions` | `(20,)` | exact match |
| `candidate_scores` | `(20, 16)` | exact match, max abs diff 0 |

Conclusion: the Windows real-data rerun reproduces the packaged 20x16/h5 seed44
label dataset byte-for-byte at the array-value level.

## 2. Value-Label Monitor

The reproduced label file was evaluated with `value_label_monitor --top-k 5`.

Result:

| metric | value |
|---|---:|
| decision | `continue` |
| candidate top-k regret | 0.18767197132110597 |
| candidate top-k overlap | 0.6300000000000001 |
| one-step top-k regret | 2.462647271156311 |
| candidate Pearson flat | 0.31701449341690197 |

This matches the tracked top-5 monitor decision used by the current paper-facing
20x16/top5 route.

## 3. Value-Head Training

The value-head training command used the reproduced label file as
`--pairwise-path` and the full local transition file only for transition sample
count/header resolution:

- `--transition-path D:\test\tool2\transitions.npz`
- `--pairwise-path reviewer_outputs\realdata_repro_e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz`
- `--epochs 3`
- `--batch-size 16`
- `--pairwise-states 20`
- `--pairwise-subsample 16`
- `--n-pairs 8`
- `--candidate-top-k 5`
- `--candidate-batch-states 1`
- `--candidate-max-states 20`
- `--seed 3044`
- `--device cpu`

Training summary:

| metric | value |
|---|---:|
| best checkpoint epoch | 2 |
| best checkpoint metric | `candidate_top5_regret` |
| best checkpoint value | 0.18767197132110597 |
| final rank loss | 0.13101713359355927 |
| ranking accuracy | 0.6381579041481018 |
| train ranking accuracy | 0.6428571343421936 |
| candidate top1 hit rate | 0.75 |
| candidate top1 regret | 0.5390448331832886 |
| candidate top5 hit rate | 0.9 |
| candidate top5 regret | 0.18767197132110597 |
| trainable parameters | 8,321 |

The reproduced checkpoint is byte-identical to the tracked canonical
checkpoint:

| checkpoint | SHA256 |
|---|---|
| reproduced `reviewer_outputs\realdata_repro_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt` | `5604D00F53450081AC43934A24D9203D85F4EF25560C3F3D3ECC7D3D533B1849` |
| tracked `paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt` | `5604D00F53450081AC43934A24D9203D85F4EF25560C3F3D3ECC7D3D533B1849` |

## 4. Five-Seed 100-Step Rollout

Rollout configuration:

- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 0.1`
- `--prepared-dir D:\test`
- checkpoint:
  `reviewer_outputs\realdata_repro_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt`

The rollout was run as `seed 0` plus a `seeds 1-4` batch.

Per-seed totals:

| seed | total reward | slope change pct | contiguity change | baimu area change ha |
|---:|---:|---:|---:|---:|
| 0 | 67.7134969354234 | -1.2858170878072237 | 0.022020494825437886 | -204.76889053727984 |
| 1 | 70.2252087804031 | -1.2078240943877006 | 0.01754519795560272 | -195.7612509440005 |
| 2 | 69.7218379673849 | -1.228753579409333 | 0.017596053601851125 | -217.57383621649743 |
| 3 | 69.82450306303002 | -1.2147233880498347 | 0.016833218908129055 | -206.9790116117954 |
| 4 | 69.86768346643231 | -1.31651581362308 | 0.02217306176418221 | -211.23669730349184 |

Aggregate comparison against the tracked canonical rollout summary:

| metric | reproduced | tracked canonical | abs diff |
|---|---:|---:|---:|
| mean total reward | 69.47054604253474 | 69.47054604253474 | 0 |
| sample std total reward | 1.0003610285842477 | 1.0003610285842477 | 0 |
| min total reward | 67.7134969354234 | 67.7134969354234 | 0 |
| max total reward | 70.2252087804031 | 70.2252087804031 | 0 |
| mean slope change pct | -1.2507267926554344 | -1.2507267926554344 | 0 |
| mean contiguity change | 0.019233605411040598 | 0.019233605411040598 | 0 |
| mean baimu area change ha | -207.263937322613 | -207.263937322613 | 0 |

Conclusion: the Windows real-data rerun exactly reproduces the tracked
five-seed 20x16/top5 rollout summary.

## Warnings

The same dataset-topology warnings appeared during the real-data runs:

- `libpysal` reports a non-fully-connected weights matrix with disconnected
  components and islands.
- `county_env.py` emits guarded divide warnings during feature construction.

These warnings did not prevent label generation, training, or rollouts. They
should be documented as real-data topology/feature-construction warnings rather
than treated as data unavailability.

## Conclusion

Windows can run the real Paper10 Bishan experiment path locally. The full
20x16/h5 seed44 sequence with explicit `--prepared-dir D:\test` reproduced:

1. the canonical label arrays exactly;
2. the top-5 monitor `continue` decision;
3. the value-head checkpoint byte-for-byte;
4. the five-seed 100-step rollout aggregate exactly.

The next Paper10 decision should not be whether Bishan real data are available.
They are available and reproducible on this Windows machine. The next technical
work should either:

1. freeze this 20x16/top5 result as the current main Paper10 evidence package;
2. clean up the warning sources for a cleaner release log; or
3. start a separate Dongxing preprocessing task, because Dongxing is currently
   raw DLTB rather than a Paper10 prepared root.
