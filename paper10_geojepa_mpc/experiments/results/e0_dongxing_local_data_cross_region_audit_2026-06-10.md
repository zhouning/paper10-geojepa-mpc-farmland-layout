# Dongxing Local Data and Cross-Region Audit

Date: 2026-06-10

This note records the local audit of the Neijiang Dongxing data after the
Windows Bishan 20x16/top5 reproduction was completed. The key correction is
that Dongxing is not limited to the raw `dongxing.shp` file on this machine.
There are also older cross-region prepared products under
`D:\test\neijiang_cross_region`, but they are not a drop-in replacement for the
current Paper10 Bishan 2,600-block pipeline.

## Local Dongxing Inventory

Raw DLTB:

- `D:\test\dongxing.shp`
  - Features: 134,369
  - CRS: `EPSG:2359`
  - Geometry: `Polygon`
  - Has `DLBM` and `QSDWDM`
  - Does not have `slope_mean`
  - Does not have `category`

Slope-enriched DLTB:

- `D:\adk\01数据样例\内江东兴区\dem_slope_analysis\output\DLTB_with_slope.gpkg`
  - Layer: `DLTB`
  - Features: 134,369
  - CRS: `EPSG:4326`
  - Geometry: `Polygon`
  - Has `DLBM`, `QSDWDM`, `category`, `slope_mean`, `slope_max`, and
    `slope_pixel_count`

Older cross-region prepared directory:

- `D:\test\neijiang_cross_region`
  - `blocks\`: township block products
  - `trajectories_6k_neijiang.npz`: transition trajectories
  - `pairwise_data_neijiang.npz`: pairwise candidate labels
  - `ensembles\baseline\`: Paper9-style baseline ensembles
  - `ensembles\partial\`: Paper9-style partial-transfer ensembles
  - `5seed_multiobj_results_baseline.json`
  - `5seed_multiobj_results_partial.json`

Published/repro artifacts were also found under:

- `D:\test\_publish\arcgis-farmland-mpc\paper\repro_artifacts\macos_2026-05-29\dongxing_5seed.json`
- `D:\test\_publish\arcgis-farmland-mpc\paper\repro_artifacts\macos_2026-05-29\dongxing_5seed_RESEARCH_ensembles.json`

## Prepared Product Shapes

`D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz`:

| array | shape | dtype |
|---|---:|---|
| `block_features` | `(6000, 3711, 17)` | `float32` |
| `global_features` | `(6000, 12)` | `float32` |
| `actions` | `(6000,)` | `int64` |
| `rewards` | `(6000,)` | `float32` |
| `next_block_features` | `(6000, 3711, 17)` | `float32` |
| `next_global_features` | `(6000, 12)` | `float32` |

`D:\test\neijiang_cross_region\pairwise_data_neijiang.npz`:

| array | shape | dtype |
|---|---:|---|
| `states_bf` | `(1000, 3711, 17)` | `float32` |
| `states_gf` | `(1000, 12)` | `float32` |
| `actions` | `(1000, 50)` | `int64` |
| `rewards` | `(1000, 50)` | `float32` |

The block dimension is 3,711, not Bishan's 2,600.

## Block Directory

`D:\test\neijiang_cross_region\blocks` contains 29 township directories with
the expected block files:

- `block_features.json`
- `block_compositions.json`
- `parcel_block_mapping.csv`

The `blocks\neijiang_summary.json` file reports 29 township entries. Across the
loaded environment, the county-level environment reports:

- 76,376 swappable parcels
- 76,376 parcels assigned to townships
- 3,711 total blocks
- 70,806 / 76,376 parcels assigned to blocks
- 1,025 cross-township block edges

## Environment Smoke

Command:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 D:\test\neijiang_cross_region\county_env_neijiang.py
```

Result:

- Loaded the Dongxing slope-enriched GPKG and prepared blocks.
- Built the county environment successfully.
- Observation dimension: 63,099.
- Action dimension: 3,711.
- Initial average farmland slope: 10.5476.
- Initial contiguity: 2.6314.
- Initial baimu fang: 384 patches, 74,341.9 ha total.
- Ran 3 random environment steps successfully.

This confirms that the older Dongxing cross-region environment still runs on
the Windows machine.

## Existing Dongxing Cross-Region Results

The existing results are Paper9-style contrastive ensemble experiments, not the
current Paper10 `GeoJEPATransitionModel` value-head pipeline.

Baseline result:

`D:\test\neijiang_cross_region\5seed_multiobj_results_baseline.json`

| metric | value |
|---|---:|
| region | `Neijiang Dongxing` |
| mode | `baseline` |
| seeds | 5 |
| eval episodes per seed | 5 |
| slope pct mean | -0.5013045984534781 |
| slope pct std | 0.024189537243931174 |
| cont pct mean | 1.2808615254122429 |
| reward mean | 64.97475452510453 |
| reward std | 11.147493498662863 |
| baimu area delta ha mean | 267.09130524496607 |

Partial-transfer result:

`D:\test\neijiang_cross_region\5seed_multiobj_results_partial.json`

| metric | value |
|---|---:|
| region | `Neijiang Dongxing` |
| mode | `partial` |
| seeds | 5 |
| eval episodes per seed | 5 |
| slope pct mean | -0.4925240000000001 |
| slope pct std | 0.017182267137953615 |
| cont pct mean | 0.9044000000000001 |
| reward mean | 53.624 |
| reward std | 13.106966452997431 |
| baimu area delta ha mean | 61.504 |

Important interpretation:

- These older results are useful local evidence that Dongxing can be processed
  and evaluated.
- They should not be promoted as the current Paper10 positive result.
- In the stored summaries, the older partial-transfer result is not stronger
  than the older baseline on reward or contiguity, so it is at best diagnostic
  cross-region evidence.

## Paper10 Compatibility Check

A direct compatibility test was run by scoring Dongxing pairwise data with the
current Bishan Paper10 checkpoint:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_score_checkpoint --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --pairwise D:\test\neijiang_cross_region\pairwise_data_neijiang.npz --top-k 5 --batch-states 1 --max-states 2 --device cpu --output reviewer_outputs\dongxing_incompatible_bishan_checkpoint_score.json
```

Result:

```text
IndexError: index out of range in self
```

The failure occurs in `model.action_emb(flat_actions)`. This is expected:

- Bishan Paper10 checkpoint: `n_blocks=2600`
- Dongxing pairwise data: `n_blocks=3711`
- Dongxing action IDs can exceed the Bishan action embedding size.

Conclusion: Dongxing data are available, but the current Paper10 Bishan
checkpoint is not dimension-compatible with Dongxing.

## Existing Scripts That Can Be Reused

Older cross-region scripts under `D:\test\neijiang_cross_region`:

- `build_blocks.py`
  - Reuses older block-definition code and points it at Dongxing
    `DLTB_with_slope.gpkg`.
  - Overrides land-use classification from `DLBM`.
- `county_env_neijiang.py`
  - Monkey-patches the older `D:\test\county_env.py` constants to instantiate a
    Dongxing environment.
- `collect_transitions_neijiang.py`
  - Generated the 6,000 Dongxing transition trajectory file.
- `generate_pairwise_neijiang.py`
  - Generated the 1,000-state, 50-candidate pairwise file.
- `train_5seed_neijiang.py`
  - Trains older Paper9-style ensembles from scratch or by partial transfer
    from Bishan ensembles, while reinitializing `action_emb` because
    `2600 != 3711`.
- `eval_mpc_neijiang.py`
  - Evaluates the older ensembles on Dongxing with MPC.

These scripts are valuable references, but they live outside the current
Paper10 package and use older model classes:

- `data_agent.transition_model.TransitionModel`
- `paper9_contrastive` training utilities

They are not the same as the current Paper10
`GeoJEPATransitionModel` / value-label / value-head stack.

## What Dongxing Needs for Paper10

To turn Dongxing into a valid Paper10 experiment, the next engineering task is
not data discovery. The next task is a 3,711-block Paper10 adapter:

1. Add or document a Paper10 Dongxing prepared root convention:
   - slope GPKG path;
   - block directory;
   - township code map;
   - transition/pairwise `.npz` paths.
2. Add a Paper10 environment adapter rather than monkey-patching the older
   top-level `D:\test\county_env.py`.
3. Add a Paper10 training entry point for `n_blocks=3711`.
   - From-scratch training needs `trainable_scope=all` or an equivalent setting.
   - A Bishan-transfer route must copy dimension-independent weights and
     reinitialize `action_emb`, matching the older Neijiang script's logic.
4. Run a small 3,711-block Paper10 smoke:
   - load Dongxing pairwise arrays;
   - instantiate a `GeoJEPATransitionModel(n_blocks=3711)`;
   - train/evaluate on a small subset;
   - run a short Dongxing environment rollout.
5. Only after the smoke is stable, run a larger cross-region experiment and
   decide whether it becomes manuscript evidence or remains diagnostic.

## Bottom Line

Dongxing data are locally available and usable, but not as a direct plug-in to
the existing Bishan 2,600-block Paper10 checkpoint. The correct status is:

- Bishan: fully reproducible in current Paper10 on Windows.
- Dongxing raw and prepared data: available locally.
- Dongxing old Paper9-style cross-region experiments: available and runnable.
- Dongxing current Paper10 experiment: not yet implemented; needs a
  dimension-compatible 3,711-block adapter/training path.
