# Paper10 public-release rights gate

Date: 2026-07-09

Status: public_release_rights_closed_restricted_data_no_go

Status note: author-updated; no rollout or training rerun; no submission approval.

This gate records the public-release rights boundary after the author confirmed
that code uses Apache-2.0, generated non-DLTB data and model/checkpoint
artifacts are completely open under CC0-1.0, and original Bishan and Dongxing
DLTB inputs are confidential and cannot be shared externally. It does not
create repository identifiers and does not authorize redistribution of
restricted geospatial inputs.

## Source basis

- author update on 2026-07-09: code licence Apache-2.0; generated data/model completely open; restricted data confidential and unavailable externally
- `LICENSE`
- `e0_paper10_author_decision_closeout_form_2026-07-08.md`
- `e0_paper10_author_decision_closeout_form_2026-07-08.json`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `DATA_AVAILABILITY.md`
- `MANIFEST.md`

## Gate outcome

Formal submission remains blocked. The code licence is Apache-2.0 and the
repository `LICENSE` file is present. Generated non-DLTB JSON, Markdown, CSV,
NPZ outputs, source-data tables, checkpoints, and model-weight artifacts are
released under CC0-1.0. These open terms do not apply to original Bishan or
Dongxing DLTB inputs.

Original Bishan and Dongxing DLTB inputs are confidential_no_external_access:
they are restricted, cannot be publicly redistributed, and cannot be provided
externally through public download, private reviewer link, controlled-access
credentials, or informal request. Any final Data and Code Availability wording
must state this limitation directly. Derived Tool2 artifacts and
Dongxing/Neijiang derived non-DLTB artifacts remain public-deposit candidates
under CC0-1.0 only after DLTB-leakage check evidence, checksums, and archive
metadata are recorded.

The 4open README.md direct reviewer link is recorded for code and derived
non-DLTB artifacts and was author-confirmed available on 2026-07-09:
`https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md`.
A 2026-07-09 command-line check of the root URL using `curl.exe -L --max-time
30 -I` observed `302 Found` followed by `401 Unauthorized` from the redirected
API path, and `curl.exe -L --max-time 30` returned
`{"error":"not_connected"}`. This root-link API result does not invalidate the
README.md direct link. The author checked the 4open page on 2026-07-09
and reported that no exact snapshot identifier, version identifier, or
commit hash was visible. The GitHub submission-preparation commit anchor is
`ea7e11a5f5f041d96a611014dd14cb5e44848524`, but this is not proof of the exact 4open snapshot.

## Current gates

| gate | status | submission consequence |
|---|---|---|
| code public release | Apache-2.0 | `LICENSE` is present; backfill archive metadata and final manuscript wording. |
| generated outputs and checkpoints | CC0-1.0 | Applies only to generated non-DLTB outputs, source-data tables, checkpoints, and model weights. |
| original Bishan DLTB | confidential_no_external_access | Do not place in public archives or reviewer links; disclose that no external raw-data access is available. |
| original Dongxing DLTB | confidential_no_external_access | Do not place in public archives or reviewer links; disclose that no external raw-data access is available. |
| derived Tool2 artifacts | CC0-1.0 public candidate after leakage check | Deposit only after DLTB-leakage check, checksums, and rights metadata. |
| 4open reviewer link | README.md direct link author-confirmed available; no visible snapshot identifier | Root-link command-line API follow-up returned 401, but the author-confirmed README.md direct link is the reviewer-facing route; the author checked the page on 2026-07-09 and no exact snapshot identifier was visible, so retain the GitHub submission-preparation commit anchor without treating it as exact 4open snapshot proof. |

## Required before formal submission

1. Backfill Apache-2.0 code licence and CC0-1.0 generated-artifact terms into
   Data and Code Availability, archive metadata, source-data records, and the
   final manuscript.
2. Record that original Bishan and Dongxing DLTB inputs are confidential and no
   external raw-data access route is available.
3. Record DLTB-leakage check evidence before any new public deposit of derived
   Tool2 or Dongxing/Neijiang non-DLTB artifacts.
4. Record the author-confirmed 4open README.md direct reviewer link in final
   materials and backfill the exact snapshot represented by that link if the
   platform exposes it; otherwise keep the visible-snapshot limitation disclosed.
5. Decide whether the target journal will accept the confidential raw-DLTB
   limitation with public code, smoke data, generated artifacts, and metadata.
6. Backfill final Data and Code Availability, `MANIFEST.md`, archive metadata,
   and manuscript wording after these checks are closed.

## Claim locks

Do not use this gate as submission approval.
Do not apply Apache-2.0 or CC0-1.0 to original Bishan or Dongxing DLTB inputs.
Do not claim original DLTB data are available to reviewers externally.
Do not treat the root-link command-line API 401 as invalidating the
author-confirmed README.md direct reviewer link.
Do not claim the GitHub submission-preparation commit anchor is exact 4open snapshot proof.
Do not claim all submission blockers are closed.
