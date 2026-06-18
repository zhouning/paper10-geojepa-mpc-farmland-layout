# Paper10 real-data availability audit

Date: 2026-06-18
Audited root: `D:\test`

Status: external-dependency audit for manuscript and rerun planning. This is not a data-rights approval, not a redistribution record, and not evidence that restricted datasets may be deposited.

The audit records path existence, file counts, and byte totals only; raw geospatial data are not copied into Git.

## Summary

| status | data families |
|---|---:|
| available | 5 |
| partial | 0 |
| missing | 1 |

## Data Families

| family | status | required paths present | files | bytes | manuscript blocker | claim dependency |
|---|---|---:|---:|---:|---|---|
| Full Bishan Tool2 arrays | available | 2/2 | 2 | 1.54 GB | Full Bishan Tool2 access route | Bishan full-data training and rollout reruns |
| Bishan slope-enriched geospatial root | available | 1/1 | 1 | 153.10 MB | GPKG-root geospatial input route | Executable-mask real-environment rollouts |
| Bishan prepared block and township inputs | available | 2/2 | 63 | 18.39 MB | GPKG-root geospatial input route | Full Bishan rollout reproduction |
| Dongxing/Neijiang primary prepared-results directory | available | 1/1 | 6 | 9.06 MB | Dongxing/Neijiang prepared-data route | External-region full reruns and timing audit |
| Dongxing/Neijiang alternate prepared-results directory | available | 1/1 | 9 | 5.45 MB | Dongxing/Neijiang prepared-data route | External-region path fallback |
| Dongxing/Neijiang local prepared-results directory | missing | 0/1 | 0 | 0 B | Dongxing/Neijiang prepared-data route | External-region local rerun fallback |

## Missing Required Paths

### Dongxing/Neijiang local prepared-results directory

- `D:\test\dongxing`

## Optional Paths Present

No optional paths were present during this audit.

## Interpretation Boundary

This report is a readiness map for reruns and Data Availability backfill. It does not change any performance claim. Missing or partial rows identify access or placement blockers that must be closed before full reruns or final manuscript submission wording.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.real_data_availability_audit --root D:\test --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_real_data_availability_audit_2026-06-18.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_real_data_availability_audit_2026-06-18.md
```
