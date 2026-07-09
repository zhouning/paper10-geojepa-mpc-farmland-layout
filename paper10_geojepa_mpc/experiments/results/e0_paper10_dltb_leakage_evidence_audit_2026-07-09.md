# Paper10 DLTB leakage evidence audit

Date: 2026-07-09

Status: tracked_public_package_leakage_evidence_recorded_final_archive_pending

Scope: source-derived public-release evidence audit for Computers, Environment and Urban Systems (CEUS). This audit records a tracked-package leakage screen at Git commit `81eee5a729d994559cd4f81ee76f856747fe0dea` and the author-confirmed 4open README.md direct reviewer link: `https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md`. It does not rerun training, rerun rollouts, add a new experimental claim, or grant submission approval.

## CEUS data-policy hook

CEUS is an Elsevier journal and its Guide for Authors lists research data policy Option B. The submission package should deposit, cite and link shareable research data where possible, and should include a data statement explaining why data cannot be shared when restrictions apply. Paper10 must therefore disclose that original Bishan and Dongxing DLTB inputs are confidential_no_external_access and cannot be provided externally.

Source checked on 2026-07-09: https://www.elsevier.com/journals/computers-environment-and-urban-systems/0198-9715/guide-for-authors

## Rights and restricted-data boundary

- Code and scripts are Apache-2.0.
- Generated non-DLTB JSON, Markdown, CSV, NPZ outputs, source-data tables, checkpoints and model-weight artifacts are CC0-1.0.
- Apache-2.0 and CC0-1.0 must not be applied to original Bishan or Dongxing DLTB inputs.
- Original Bishan DLTB external access: confidential_no_external_access.
- Original Dongxing DLTB external access: confidential_no_external_access.
- Original DLTB public release is not allowed, and original DLTB reviewer access is not available through public download, reviewer credentials, controlled access or informal requests.

## Tracked public-package leakage evidence

The tracked path scan used this command:

```powershell
git ls-files | rg -n -i "(^|/)(dltb|.*dltb.*|.*\.gpkg|.*\.gdb|.*\.shp|.*\.dbf|.*\.prj|.*\.cpg)$|dongxing|neijiang|tool2|transitions\.npz|pairwise\.npz"
```

Result interpretation:

- The tracked public package contains no original Bishan or Dongxing DLTB payload.
- The tracked public package contains no GPKG/GDB/SHP/DBF/PRJ/CPG geospatial source payloads.
- Positive path hits are expected non-DLTB artifacts: reviewer smoke Tool2 files, Dongxing derived CSV/JSON/Markdown summaries, code, tests, checkpoints, value-label outputs, source-data tables and manuscript audits.
- The small reviewer smoke Tool2 files under `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/` are not the full Bishan Tool2 transition and pairwise datasets.
- Full Bishan Tool2, prepared GPKG-root geospatial inputs and full Dongxing/Neijiang prepared data are external to Git and are not cleared for public release by this tracked-package scan.

## Remaining leakage checks before formal submission

- Backfill the exact 4open submission snapshot commit represented by the reviewer link.
- Run and record an independent DLTB-leakage content review on the final public archive snapshot.
- Record checksums for any public derived Tool2, Dongxing or Neijiang artifacts deposited outside Git.
- Confirm CEUS or the target journal accepts confidential raw-DLTB non-availability with public code, smoke data, generated outputs and metadata.
- Align the final Data and Code Availability statement with the accepted archive snapshot.

## Submission gate

Formal submission remains blocked. This audit is not final submission approval. A preflight pass only means the current tracked-package leakage evidence and confidentiality boundary are recorded; it does not prove that a future or external archive snapshot is free of DLTB leakage.
