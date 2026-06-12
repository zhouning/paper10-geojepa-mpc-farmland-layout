# Data Availability

For manuscript submission wording and the current repository/data DOI action
list, see:

```text
paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md
```

For the route-specific archive plan, including generic, Nature-family, and
methods/reproducibility submission paths, see:

```text
paper10_geojepa_mpc/experiments/results/e0_submission_route_and_archive_plan_2026-06-09.md
```

For fill-in archive metadata, controlled-access wording, and dataset README
templates, see:

```text
paper10_geojepa_mpc/experiments/results/e0_archive_metadata_templates_2026-06-09.md
```

For a machine-readable archive manifest that separates included, externalized,
and excluded file families, see:

```text
paper10_geojepa_mpc/experiments/results/e0_archive_manifest_2026-06-09.csv
```

For the current figure, table, and claim-to-source-data mapping, see:

```text
paper10_geojepa_mpc/experiments/results/e0_source_data_map_2026-06-09.md
paper10_geojepa_mpc/experiments/results/e0_source_data_map_with_dongxing_2026-06-11.md
```

For the current generic manuscript-conversion figure/table numbering freeze,
including main and supplementary placement for Dongxing evidence, see:

```text
paper10_geojepa_mpc/experiments/results/e0_integrated_figure_table_numbering_freeze_2026-06-11.md
```

For the current no-go decision packet that consolidates unresolved target
journal, DOI/reviewer-link, licence, data-access, citation, statistics, and
export-format blockers, see:

```text
paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md
```

For the current with-Dongxing target-venue and manuscript-conversion checklist,
including section-by-section conversion actions and Data and Code Availability
backfill fields, see:

```text
paper10_geojepa_mpc/experiments/results/e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md
```

For the current CEUS reviewer-improvement packet, including `D:\test` local
data discovery, full Bishan and Dongxing/Neijiang rerun feasibility, and the
no-copy/no-redistribution boundary for full geospatial payloads, see:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md
```

For the data-access and rights decision register, including full Tool2,
GPKG-root geospatial inputs, optional GeoFM rights, code licence, generated-data
rights, Dongxing/Neijiang prepared-data access, and reviewer routes, see:

```text
paper10_geojepa_mpc/experiments/results/e0_data_access_and_rights_decision_register_2026-06-09.md
```

For the release sequence and DOI or reviewer-link backfill checklist, see:

```text
paper10_geojepa_mpc/experiments/results/e0_archive_release_and_doi_backfill_checklist_2026-06-09.md
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
