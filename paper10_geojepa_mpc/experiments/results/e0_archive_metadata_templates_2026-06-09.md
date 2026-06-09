# Paper10 E0 archive metadata templates

Date: 2026-06-09

This document provides fill-in templates for the repository and data archive
records needed before a Paper10 E0 submission. It does not assign identifiers,
licences, creators, access committees, data owners, embargoes, or journal
decisions. Replace every bracketed field before submission.

## Template use

Use these templates after selecting the submission route in
`e0_submission_route_and_archive_plan_2026-06-09.md`. Keep one archive record
for the public code and packaged E0 evidence, and decide separately whether the
full Bishan `tool2/` data and prepared GPKG-root geospatial inputs can be
public or must be controlled.

Do not use a temporary cloud folder or a personal web link as the final data
identifier. Use a repository DOI, accession, Handle, ARK, or another stable
record identifier.

## Record 1: code and packaged E0 evidence archive

Recommended status: public archive, unless anonymous review requires a private
reviewer link before acceptance.

```text
Title:
[Paper10 GeoJEPA-MPC Farmland Layout E0 Reproducibility Package]

Creators:
[creator 1: family name, given name, affiliation, ORCID if available]
[creator 2: family name, given name, affiliation, ORCID if available]

Resource type:
Software / Dataset

Repository / publisher:
[Zenodo, Figshare, OSF, institutional repository, or other selected archive]

Identifier:
[DOI OR STABLE IDENTIFIER TO BE ASSIGNED]

Version:
[release version, e.g. v0.1.0-submission or journal-specific archive version]

Exact Git commit:
[SUBMISSION COMMIT HASH]

Description:
This archive contains the Paper10 GeoJEPA-MPC E0 reproducibility package for
monitor-gated `frontier_random050` value-label generation and value-head rollout
evaluation in constrained Bishan farmland layout planning. It includes source
code, tests, small reviewer smoke data, generated E0 value-label files,
monitor outputs, rollout summaries, saved checkpoints, figure-ready CSV source
data, manuscript source notes, and reproducibility documentation. The current
paper-facing positive result is the 20x16/h5 top-5 value-head package with
five-seed mean total reward `69.4705` and sample standard deviation `1.0004`.
Tested 50-state `frontier_random050` runs are included only as failed
diagnostics and should not be interpreted as successful scale-up evidence.

Keywords:
GeoJEPA-MPC; farmland layout planning; model predictive control; value labels;
geospatial optimization; reproducibility package; Bishan

Licence / rights:
[CODE LICENCE TO BE SELECTED]
[DATA LICENCE OR DATA RIGHTS TERMS TO BE SELECTED]

Related identifiers:
[MANUSCRIPT PREPRINT OR ARTICLE DOI, IF AVAILABLE]
[FULL TOOL2 DATA DOI OR ACCESS RECORD, IF AVAILABLE]
[GPKG-ROOT GEOSPATIAL DATA DOI OR ACCESS RECORD, IF AVAILABLE]

Access:
Public archive after release, or anonymous reviewer link during peer review:
[PUBLIC DOI OR REVIEWER LINK TO BE ADDED]
```

### Included file families for Record 1

| file family | archive handling | notes |
|---|---|---|
| `paper10_geojepa_mpc/` source code and tests | include | Main Paper10 implementation and test suite. |
| `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/` | include | Small smoke data for reviewer-side tests; not a substitute for full Bishan data. |
| `paper10_geojepa_mpc/experiments/results/*.json`, `*.md`, `*.csv`, `*.npz` | include | Generated E0 evidence, value labels, monitor outputs, rollout summaries, and manuscript source data. |
| `paper10_geojepa_mpc/experiments/checkpoints/` | include | Saved model checkpoints used by packaged rollouts. |
| `scripts/`, `notebooks/`, `docs/`, root reproducibility docs | include | Reproduction commands, continuation guides, and manuscript planning notes. |
| ignored `reviewer_outputs/` | exclude unless final figures are selected | Generated local previews are not source data until intentionally exported and documented. |

## Record 2: full Bishan Tool2 data

Recommended status: public data record if redistribution rights exist;
otherwise controlled-access record with public metadata.

```text
Title:
[Full Bishan Tool2 transition and pairwise data for Paper10 GeoJEPA-MPC]

Creators / data owners:
[creator or data owner fields to be confirmed]

Resource type:
Dataset

Repository / access body:
[DATA REPOSITORY OR INSTITUTIONAL ACCESS BODY]

Identifier:
[DOI, ACCESSION, OR CONTROLLED-ACCESS RECORD TO BE ASSIGNED]

Files:
tool2/transitions.npz
tool2/pairwise.npz

Approximate size:
1.65 GB total

Description:
Full prepared transition and pairwise training data used by the Paper10
GeoJEPA-MPC full Bishan training and rollout workflows. These files are
external to the Git repository and are required to rerun full-scale training
and real-environment rollouts from scratch.

Access and rights:
[PUBLIC LICENCE IF REDISTRIBUTABLE, OR RESTRICTION REASON AND ACCESS PROCESS]

Reviewer access:
[ANONYMOUS REVIEWER LINK OR CONTROLLED-ACCESS REVIEW PROCESS]

Preferred citation:
[Creator(s)] ([Year]) [Dataset title]. [Repository]. [Identifier].
```

## Record 3: prepared GPKG-root geospatial inputs

Recommended status: public only if data rights allow; otherwise controlled
access with public metadata and a concrete request route.

```text
Title:
[Prepared Bishan GPKG-root geospatial inputs for Paper10 GeoJEPA-MPC]

Creators / data owners:
[creator or data owner fields to be confirmed]

Resource type:
Dataset

Repository / access body:
[DATA REPOSITORY OR INSTITUTIONAL ACCESS BODY]

Identifier:
[DOI, ACCESSION, OR CONTROLLED-ACCESS RECORD TO BE ASSIGNED]

Required placement:
dem_slope_analysis/output/DLTB_with_slope.gpkg
results_real/blocks/
townships.json

Description:
Prepared Bishan parcel, block, and township geospatial inputs used by the
Paper10 real-environment rollout and value-label workflows. The GPKG root is
part of the reproducibility condition for the packaged 20x16/top5 result,
because the GPKG root reproduced the packaged labels whereas shapefile-first
resolution generated materially different labels in the macOS audit.

Access and rights:
[PUBLIC LICENCE IF REDISTRIBUTABLE, OR RESTRICTION REASON AND ACCESS PROCESS]

Reviewer access:
[ANONYMOUS REVIEWER LINK OR CONTROLLED-ACCESS REVIEW PROCESS]

Preferred citation:
[Creator(s)] ([Year]) [Dataset title]. [Repository]. [Identifier].
```

## Controlled-access wording fields

Use these fields if full Tool2 or geospatial inputs cannot be openly
redistributed:

```text
Restriction reason:
[legal, governance, licence, third-party, cadastral, or institutional reason]

Responsible owner or access body:
[named data owner, institution, repository, or access committee]

Eligible requesters:
[qualified researchers, reviewers, institutional users, or other eligibility]

Request route:
[email, repository request form, institutional data access portal, or URL]

Review criteria:
[scientific purpose, non-commercial use, ethics/permission status, affiliation,
data-use agreement, or other criteria]

Expected response time:
[time frame if known, otherwise leave unresolved]

Data-use agreement:
[terms, citation requirement, no redistribution clause, or unresolved]

Reviewer route:
[anonymous reviewer link, editor-mediated route, or repository review access]
```

## Source-data mapping template

Update this table after final figure and table numbering is frozen.

| manuscript item | source files | archive record | notes |
|---|---|---|---|
| Figure 1, workflow schematic | `[FINAL SOURCE OR ARTWORK FILE]` | Record 1 | Add only after final figure is selected. |
| Figure 2, seed-wise reward comparison | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_seedwise_rewards_2026-06-09.csv` | Record 1 | Supports 10x12/top4 vs 20x16/top5 reward comparison. |
| Figure 3, failed 50-state diagnostics | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_topk_diagnostics_2026-06-09.csv` | Record 1 | Boundary diagnostic only; not successful scale-up evidence. |
| Main results table | `paper10_geojepa_mpc/experiments/results/e0_frontier_random050_manuscript_tables_2026-06-09.md` and rollout summaries | Record 1 | Confirm final table number before submission. |
| Full rerun commands | `REPRODUCIBILITY.md` | Record 1 plus Records 2 and 3 if full reruns are required | Smoke verification runs from Record 1 alone. |

## Dataset README skeleton

Use this skeleton for any separate data record.

```text
# [Dataset title]

## Summary
[What the dataset contains and which Paper10 results it supports.]

## Files
- [filename]: [contents, format, approximate size, related figure/table/result]

## Variables and units
[field name] | [definition] | [unit] | [allowed values or missing-value code]

## Methods and provenance
[How the files were generated, prepared, filtered, or transformed.]

## Software and environment
[software, package versions, scripts, operating system, or upstream pipeline]

## Access and licence
[licence, access restriction, embargo, data-use agreement, or controlled route]

## Citation
[preferred DataCite-style citation]
```

## Unresolved fields before submission

- Target journal or venue family.
- Archive platform and identifier strategy.
- Code licence.
- Data licence or restriction terms for shareable generated outputs.
- Redistribution rights for optional GeoFM asset.
- Public deposit versus controlled access for full `tool2/`.
- Public deposit versus controlled access for GPKG-root geospatial inputs.
- Data owner or institutional access route for restricted geospatial data.
- Final figure/table numbering and source-data mapping.
