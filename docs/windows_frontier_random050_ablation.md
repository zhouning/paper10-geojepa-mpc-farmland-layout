# Windows continuation guide: frontier_random050 ablation grid

Use this guide when Colab quota is unavailable and the next Paper10
`frontier_random050` diagnosis should run on the Windows workstation. The
Windows route is not blocked by training support: CUDA is not required, and the
verified local path uses CPU execution through:

`D:\adk\.venv\Scripts\python.exe`

The default workflow is label-first. It generates value labels, runs diagnostics
and the monitor gate, and writes a compact summary. It does not train a value
head unless a gate passes and `TrainOnPass = 1` is explicitly enabled.

## Current conclusion

Do not continue the macOS `50x24/h5 seed45` label set into value-head training.
That run failed the top-3, top-4, and top-5 monitor gates. The Windows runner is
for the next ablation grid, not for forcing that failed label set through
training.

## 1. Pull the repository

```powershell
git pull
```

## 2. Use the verified Windows Python environment

The current Windows probe used:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

CPU is the supported baseline on this machine. CUDA is not required for the
runner. Longer label generation can still take time on CPU.

## 3. Confirm the full Bishan data root

Use `D:\test` as the Windows data root. It must contain:

```text
tool2/transitions.npz
tool2/pairwise.npz
dem_slope_analysis/output/DLTB_with_slope.gpkg
results_real/blocks
townships.json
```

The Windows runner requires `DLTB_with_slope.gpkg` directly. This avoids the
`.shp` versus `.gpkg` ambiguity that affected the earlier macOS audit.

## 4. Configure local overrides

Copy the template:

```powershell
Copy-Item scripts\windows\frontier_random050_ablation.env.example.ps1 `
  scripts\windows\frontier_random050_ablation.env.ps1
```

Tracked template path: `scripts/windows/frontier_random050_ablation.env.example.ps1`.

The default local settings are:

```powershell
$DataRoot = "D:\test"
$RunRoot = "D:\test\paper10_runs"
$PythonBin = "D:\adk\.venv\Scripts\python.exe"
$Device = "cpu"
$TrainOnPass = 0
$RunPytest = 1
```

Leave `TrainOnPass = 0` for the first ablation pass. Set `TrainOnPass = 1` only
after you are ready to train value heads for rows whose monitor gate returns
`continue`.

## 5. Run the ablation grid

```powershell
powershell -ExecutionPolicy Bypass -File scripts\windows\run_frontier_random050_ablation_grid.ps1
```

Tracked runner path: `scripts/windows/run_frontier_random050_ablation_grid.ps1`.

Default grid:

| states | candidates | horizon | frontier fraction | label seed |
|---:|---:|---:|---:|---:|
| 50 | 16 | 5 | 0.5 | 46 |
| 50 | 20 | 5 | 0.5 | 46 |
| 50 | 24 | 5 | 0.75 | 46 |
| 50 | 24 | 5 | 1.0 | 46 |

Each row runs:

- `paper10_geojepa_mpc.experiments.value_label_generation`
- `paper10_geojepa_mpc.experiments.value_label_diagnostics`
- `paper10_geojepa_mpc.experiments.value_label_monitor`

The gate top-k values are `3`, `4`, and `5`. Training is skipped unless
`TrainOnPass = 1` and at least one of those top-k gates returns `continue`.

## Outputs

Outputs stay outside the Git checkout under:

```text
D:\test\paper10_runs
```

Important files:

```text
frontier_random050_ablation_summary.json
frontier_random050_ablation_summary.md
<run-name>/logs/
<run-name>/reports/
<run-name>/value_label_monitor_top3.json
<run-name>/value_label_monitor_top4.json
<run-name>/value_label_monitor_top5.json
```

Use `frontier_random050_ablation_summary.md` to decide the next action:

- If no row passes, keep Paper10 anchored on the reproducible `20x16/h5 seed44
  top5` result and report the 50-state boundary as a diagnostic limitation.
- If one or more rows pass, rerun with `TrainOnPass = 1` or narrow the grid to
  the passing rows and then train value heads.

Do not commit generated `.npz`, checkpoints, or run directories unless a
specific publication artifact is selected.
