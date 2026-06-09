# Data Availability

For manuscript submission wording and the current repository/data DOI action
list, see:

```text
paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md
```

## Included in This Repository

Small reviewer smoke data is included at:

```text
arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/
```

Files:

- `transitions.npz`
- `pairwise.npz`
- `sample_transitions.log`
- `sample_transitions_summary.json`

The optional GeoFM asset is also included:

```text
paper7/data/block_geofm_embeddings.npy
paper7/data/geofm_metadata.json
```

These files are small enough for normal Git and are required for smoke tests or
optional GeoFM code paths.

## External Full Dataset

The full Bishan Tool2 dataset is not committed to Git:

- `tool2/transitions.npz`: approximately 1.52 GB
- `tool2/pairwise.npz`: approximately 127 MB
- total: approximately 1.65 GB

After obtaining the dataset, place it under the repository root:

```text
tool2/transitions.npz
tool2/pairwise.npz
```

Full real-environment rollouts also require the prepared parcel and block data:

```text
dem_slope_analysis/output/DLTB_with_slope.shp
dem_slope_analysis/output/DLTB_with_slope.dbf
dem_slope_analysis/output/DLTB_with_slope.shx
dem_slope_analysis/output/DLTB_with_slope.prj
results_real/blocks/
townships.json
```

`dem_slope_analysis/output/DLTB_with_slope.gpkg` may be used instead of the
shapefile set.

## Why Large Data Is External

The full Tool2 files are binary scientific data larger than ordinary GitHub
source-control limits and would make reviewer cloning slow and fragile. This
repository therefore includes:

- the complete code path for loading and using the full data;
- the small smoke dataset needed for automated verification;
- all saved Paper10 checkpoints and recorded result artifacts currently under
  `paper10_geojepa_mpc/experiments/`;
- explicit placement instructions for external full data.

If a journal or reviewer requires one-click full-data retrieval, publish the
full `tool2/` directory and prepared geospatial inputs through an archival data
repository, then add the DOI or download URL here.
