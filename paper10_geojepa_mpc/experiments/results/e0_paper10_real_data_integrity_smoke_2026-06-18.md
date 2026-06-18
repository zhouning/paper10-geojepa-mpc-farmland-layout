# Paper10 real-data integrity smoke

Date: 2026-06-18
Audited root: `D:\test`

Status: metadata-only smoke audit for real-data readability. NPZ arrays are read for headers, GeoPackage files are read through SQLite metadata tables, directories are summarized by extension and size, and raw row values are not exported.

## Summary

| status | count |
|---|---:|
| missing | 3 |
| readable | 7 |

## NPZ header smoke

| path | status | arrays | bytes |
|---|---|---:|---:|
| `D:\test\tool2\transitions.npz` | readable | 6 | 1.42 GB |
| `D:\test\tool2\pairwise.npz` | readable | 4 | 121.31 MB |

## NPZ arrays

### `D:\test\tool2\transitions.npz`

| array | shape | dtype |
|---|---|---|
| block_features | `[6000, 2600, 17]` | `float32` |
| global_features | `[6000, 12]` | `float32` |
| actions | `[6000]` | `int64` |
| rewards | `[6000]` | `float32` |
| next_block_features | `[6000, 2600, 17]` | `float32` |
| next_global_features | `[6000, 12]` | `float32` |

### `D:\test\tool2\pairwise.npz`

| array | shape | dtype |
|---|---|---|
| states_bf | `[1000, 2600, 17]` | `float32` |
| states_gf | `[1000, 12]` | `float32` |
| actions | `[1000, 50]` | `int64` |
| rewards | `[1000, 50]` | `float32` |

## GeoPackage metadata smoke

| path | status | tables | feature layers | geometry columns | bytes |
|---|---|---:|---:|---:|---:|
| `D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg` | readable | 13 | 1 | 1 | 153.10 MB |

## Directory smoke

| path | status | files | bytes | extensions |
|---|---|---:|---:|---|
| `D:\test\results_real\blocks` | readable | 62 | 18.39 MB | .0:3, .csv:13, .json:32, .png:13, .zip:1 |
| `G:\我的云端硬盘\paper4_results\dongxing` | readable | 6 | 9.06 MB | .json:3, .zip:3 |
| `G:\我的云端硬盘\paper4_results\dongxing1` | readable | 9 | 5.45 MB | .json:6, .zip:3 |

## JSON schema smoke

| path | status | top-level type | top-level keys | bytes |
|---|---|---|---|---:|
| `D:\test\townships.json` | readable | dict | 500227001, 500227002, 500227100, 500227101, 500227102, 500227103, 500227104, 500227105, 500227106, 500227107, 500227108, 500227109, 500227200 | 407 B |
| `G:\我的云端硬盘\paper4_results\dongxing\colab_timing.json` | missing | None | none | 0 B |
| `G:\我的云端硬盘\paper4_results\dongxing\marl_eval_seed0.json` | missing | None | none | 0 B |
| `G:\我的云端硬盘\paper4_results\dongxing\county_eval_seed0.json` | missing | None | none | 0 B |

## Interpretation Boundary

This smoke audit supports data-readiness and rerun planning only. It does not change Paper10 performance claims, does not export restricted rows or geometries, and does not replace data-rights approval.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.real_data_integrity_smoke --root D:\test --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_real_data_integrity_smoke_2026-06-18.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_real_data_integrity_smoke_2026-06-18.md
```
