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

## Conclusion

Do not train value heads for these four 50-state rows. The least-bad row in this
grid is `50x16/h5 seed46 f0.5` at top-5, but it still exceeds the candidate
top-k regret threshold (`0.3840 > 0.2500`). Increasing candidate count or
frontier fraction worsened the candidate gate under seed 46.

The current validated Paper10 scale-up evidence remains the reproducible
`frontier_random050 20x16/h5 seed44 top5` route. Future 50-state work should
change the candidate proposal strategy or acceptance thresholds deliberately,
rather than continuing these failed rows into value-head training.
