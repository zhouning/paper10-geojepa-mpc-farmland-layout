# Paper10 50-state redesign handoff

Date: 2026-06-09

## Current decision

Do not train any currently tested 50-state `frontier_random050` value-label
set. The macOS `50x24/h5 seed45 f0.5` run and the Windows seed46 ablation grid
all failed the monitor gate. The current Paper10 E0 result remains:

- `frontier_random050 20x16/h5 seed44 top5`
- five-seed mean total reward: `69.4705`
- sample standard deviation: `1.0004`
- improvement over 10x12/top4: `+4.2139` reward, `+6.46%`

## Superseded assets

These assets are still useful for reproduction or for editing into a new
diagnostic run, but they are no longer the next training route:

- `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`
- `docs/macos_frontier_random050_50x24_h5.md`
- `scripts/macos/run_frontier_random050_50x24_h5.sh`
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`
- `scripts/windows/frontier_random050_ablation.env.example.ps1`

The Colab/macOS 50x24 seed45 path is superseded because that label set failed
the default and post-hoc monitor checks. The Windows seed46 grid is superseded
as a completed negative diagnostic; reuse the runner only after changing the
grid deliberately.

## Evidence to carry forward

- 20x16/top5 passed because candidate regret was `0.1877`, candidate overlap
  was `0.6300`, and one-step regret was `2.4626`.
- macOS GPKG reproduction matched the packaged 20x16 labels exactly or within
  floating-point tolerance. Use a GPKG root for reproducibility.
- 50x16 and 50x20 Windows rows became too close to one-step reward at larger
  top-k values.
- 50x24 Windows rows retained excessive candidate regret or weak overlap until
  top-k became too broad.

## Next experiment rule

Only train a value head when a label set returns `decision=continue` for one
of the pre-declared monitor gates. Do not relax thresholds after seeing a
failed label set unless the paper explicitly frames that as a new ablation.

Default monitor thresholds are:

| threshold | value |
|---|---:|
| candidate top-k regret max | 0.25 |
| candidate top-k overlap min | 0.50 |
| one-step top-k regret min | 0.25 |

## Recommended next route

1. Keep the manuscript anchored on 20x16/top5.
2. Treat all existing 50-state rows as boundary diagnostics.
3. Before another 50-state run, decide whether the goal is:
   - a seed-sensitivity check of the existing `frontier_random050` proposal; or
   - a changed candidate proposal / changed monitor design.
4. If staying within current code, run label-only probes first. Good candidates
   are additional seeds for the least-bad row family, such as `50x16/h5 f0.5`
   with seeds 47 and 48.
5. If those still fail, stop running larger `frontier_random050` grids and
   modify candidate proposal logic before spending more compute.

## Windows continuation notes

The Windows runner's local env file can override `$Grid`. For a seed-sensitivity
probe, copy:

```powershell
Copy-Item scripts\windows\frontier_random050_ablation.env.example.ps1 `
  scripts\windows\frontier_random050_ablation.env.ps1
```

Then edit only the local ignored env file and set a narrow grid, for example:

```powershell
$Grid = @(
    @{
        Name = "frontier_random050_50x16_h5_seed47_f050"
        NStates = 50
        CandidateActions = 16
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 47
        TrainingSeed = 3047
    },
    @{
        Name = "frontier_random050_50x16_h5_seed48_f050"
        NStates = 50
        CandidateActions = 16
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 48
        TrainingSeed = 3048
    }
)
```

Leave `$TrainOnPass = 0` for the first pass. Train only after a monitor gate
passes and after committing the label-only findings.

## Paper-writing route

The paper can move forward without a passing 50-state value head. The strongest
current claim is bounded but defensible: monitor-gated frontier-random labels
improve GeoJEPA-MPC at the reproducible 20x16/top5 scale, while the tested
50-state rows identify a candidate-proposal boundary.
