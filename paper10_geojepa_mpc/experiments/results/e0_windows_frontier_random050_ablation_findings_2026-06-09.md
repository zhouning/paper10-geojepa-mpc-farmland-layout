# E0 Windows frontier_random050 ablation findings

Date: 2026-06-09

This note records the Windows CPU ablation run for the next Paper10
`frontier_random050` value-label scale-up. The run used the Windows continuation
runner added in:

- `scripts/windows/run_frontier_random050_ablation_grid.ps1`
- `docs/windows_frontier_random050_ablation.md`

## Runtime setup

- Repository: `D:\test\paper10-geojepa-mpc-farmland-layout`
- Data root: `D:\test`
- Python: `D:\adk\.venv\Scripts\python.exe`
- Device: `cpu`
- Train-on-pass: `0`
- Gate top-k values: `3`, `4`, `5`

The runner first executed the repository test suite:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider
```

Result: `105 passed`.

## Local output location

Generated labels, logs, and monitor reports were written outside Git:

```text
D:\test\paper10_runs
```

The compact local summaries are:

```text
D:\test\paper10_runs\frontier_random050_ablation_summary.json
D:\test\paper10_runs\frontier_random050_ablation_summary.md
D:\test\paper10_runs\frontier_random050_ablation_posthoc_topk_summary.json
D:\test\paper10_runs\frontier_random050_ablation_posthoc_topk_summary.md
```

The generated `.npz` files and run directories are intentionally not committed.

## Monitor results

All four candidate rows failed the monitor gate. No value-head training was
started.

| run | top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---|---:|---:|---:|
| `50x16/h5 seed46 f0.5` | 3 | `stop` | 0.7914 | 0.3133 | 2.3184 |
| `50x16/h5 seed46 f0.5` | 4 | `stop` | 0.4639 | 0.4650 | 2.0969 |
| `50x16/h5 seed46 f0.5` | 5 | `stop` | 0.3840 | 0.5760 | 1.7764 |
| `50x20/h5 seed46 f0.5` | 3 | `stop` | 0.7654 | 0.3533 | 2.8514 |
| `50x20/h5 seed46 f0.5` | 4 | `stop` | 0.6163 | 0.4100 | 2.7718 |
| `50x20/h5 seed46 f0.5` | 5 | `stop` | 0.5841 | 0.5320 | 2.6927 |
| `50x24/h5 seed46 f0.75` | 3 | `stop` | 1.4308 | 0.2400 | 2.9821 |
| `50x24/h5 seed46 f0.75` | 4 | `stop` | 1.1872 | 0.2600 | 2.8166 |
| `50x24/h5 seed46 f0.75` | 5 | `stop` | 1.1009 | 0.2960 | 2.5471 |
| `50x24/h5 seed46 f1.0` | 3 | `stop` | 1.6735 | 0.2533 | 3.1501 |
| `50x24/h5 seed46 f1.0` | 4 | `stop` | 1.3982 | 0.2600 | 2.9863 |
| `50x24/h5 seed46 f1.0` | 5 | `stop` | 1.3346 | 0.3240 | 2.8339 |

## Post-hoc larger top-k checks

After the default gate failed, post-hoc monitors were run for top-6, top-8,
top-10, and top-12. These checks do not change the training decision; they are
only diagnostic.

All post-hoc checks also returned `stop`.

| run | top-k | decision | candidate regret | candidate overlap | one-step regret |
|---|---:|---|---:|---:|---:|
| `50x16/h5 seed46 f0.5` | 6 | `stop` | 0.3010 | 0.6533 | 1.4748 |
| `50x16/h5 seed46 f0.5` | 8 | `stop` | 0.1324 | 0.7350 | 0.1056 |
| `50x16/h5 seed46 f0.5` | 10 | `stop` | 0.1324 | 0.7560 | 0.0811 |
| `50x16/h5 seed46 f0.5` | 12 | `stop` | 0.1238 | 0.8067 | 0.0725 |
| `50x20/h5 seed46 f0.5` | 6 | `stop` | 0.5164 | 0.5467 | 1.3441 |
| `50x20/h5 seed46 f0.5` | 8 | `stop` | 0.4685 | 0.6175 | 0.1588 |
| `50x20/h5 seed46 f0.5` | 10 | `stop` | 0.0780 | 0.7280 | 0.0739 |
| `50x20/h5 seed46 f0.5` | 12 | `stop` | 0.0739 | 0.7550 | 0.0000 |
| `50x24/h5 seed46 f0.75` | 6 | `stop` | 0.9522 | 0.3467 | 2.4113 |
| `50x24/h5 seed46 f0.75` | 8 | `stop` | 0.9118 | 0.4250 | 2.0970 |
| `50x24/h5 seed46 f0.75` | 10 | `stop` | 0.6931 | 0.4960 | 0.3802 |
| `50x24/h5 seed46 f0.75` | 12 | `stop` | 0.2912 | 0.6167 | 0.3419 |
| `50x24/h5 seed46 f1.0` | 6 | `stop` | 1.2449 | 0.3967 | 2.8339 |
| `50x24/h5 seed46 f1.0` | 8 | `stop` | 1.2432 | 0.4675 | 2.7080 |
| `50x24/h5 seed46 f1.0` | 10 | `stop` | 0.5200 | 0.5780 | 0.6433 |
| `50x24/h5 seed46 f1.0` | 12 | `stop` | 0.2691 | 0.6400 | 0.6011 |

The larger top-k checks fail for two different reasons. For `50x16` and
`50x20`, regret becomes small at larger top-k, but one-step regret also becomes
too small, meaning the label can be mostly solved by immediate reward and adds
little multi-step filtering signal. For both `50x24` rows, candidate regret
remains too high or overlap too low until the top-k is broad enough to weaken
the value-filtering task.

## Conclusion

Do not train value heads for these four 50-state rows. The least-bad default
gate row is `50x16/h5 seed46 f0.5` at top-5, but it still exceeds the candidate
top-k regret threshold (`0.3840 > 0.2500`). Larger top-k values do not rescue
the decision: they either retain too much candidate regret or become mostly
solvable by one-step reward. Increasing candidate count or frontier fraction
worsened the candidate gate under seed 46.

The current validated Paper10 scale-up evidence remains the reproducible
`frontier_random050 20x16/h5 seed44 top5` route. Future 50-state work should
change the candidate proposal strategy or acceptance thresholds deliberately,
rather than continuing these failed rows into value-head training.
