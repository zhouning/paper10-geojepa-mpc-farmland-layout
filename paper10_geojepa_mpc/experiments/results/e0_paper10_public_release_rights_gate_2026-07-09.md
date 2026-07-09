# Paper10 public-release rights gate

Date: 2026-07-09

Status: public_release_rights_pending_no_go

Status note: source-derived; no rollout or training rerun; no submission approval.

This gate records the public-release rights boundary after the author confirmed
that code can be public, non-DLTB artifacts can be public, and original Bishan
and Dongxing DLTB inputs are restricted. It does not choose a licence, does not
create repository identifiers, and does not authorize redistribution of
restricted geospatial inputs.

## Source basis

- `e0_paper10_author_decision_closeout_form_2026-07-08.md`
- `e0_paper10_author_decision_closeout_form_2026-07-08.json`
- `e0_data_access_and_rights_decision_register_2026-06-09.md`
- `e0_data_code_availability_draft_2026-06-09.md`
- `DATA_AVAILABILITY.md`
- `MANIFEST.md`

## Gate outcome

Formal submission remains blocked. Code can be public, but a named software
licence has not been selected and no repository `LICENSE` or `LICENCE` file is
present. Non-DLTB artifacts can be public, but generated-data and
checkpoint/model-weight rights terms are still pending. Original Bishan and
Dongxing DLTB inputs are restricted and must not be publicly redistributed.

Derived Tool2 artifacts and Dongxing/Neijiang derived non-DLTB artifacts remain
public-deposit candidates only after DLTB-leakage check evidence, checksums,
and archive metadata are recorded. The 4open reviewer link is recorded for code
and derived non-DLTB artifacts, but non-author browser-session testing and exact
snapshot backfill remain pending.

## Current gates

| gate | status | submission consequence |
|---|---|---|
| code public release | allowed_pending_named_software_licence | Add a named code licence or institution-approved code-use statement before final archive metadata. |
| generated outputs and checkpoints | public_release_allowed_pending_named_rights_terms | Select generated-output and model-weight rights terms without relicensing restricted DLTB inputs. |
| original Bishan DLTB | restricted_no_public_redistribution | Use controlled access or institution/data-owner routing if reviewer inspection is required. |
| original Dongxing DLTB | restricted_no_public_redistribution | Split public derived non-DLTB artifacts from restricted original DLTB inputs. |
| derived Tool2 artifacts | public_candidate_after_leakage_check | Deposit only after DLTB-leakage check, checksums, and rights metadata. |
| 4open reviewer link | provided_pending_non_author_browser_test | Verify outside the author account and backfill the exact represented snapshot. |

## Required before formal submission

1. Select a named software licence or institution-approved code-use statement
   for licensable code and scripts.
2. Select named rights terms for generated JSON, Markdown, CSV, NPZ outputs,
   source-data tables, checkpoints, and model weights.
3. Record DLTB-leakage check evidence before public deposit of derived Tool2 or
   derived Dongxing/Neijiang non-DLTB artifacts.
4. Keep original Bishan and Dongxing DLTB inputs out of public archives and
   define a controlled-access or editor-mediated route only if reviewers need
   raw-input inspection.
5. Test the 4open reviewer link from a non-author browser session and backfill
   the exact snapshot represented by that link.
6. Backfill Data and Code Availability, `MANIFEST.md`, archive metadata, and the
   final manuscript after the above choices are closed.

## Claim locks

Do not use this gate as submission approval.
Do not apply an open licence to original Bishan or Dongxing DLTB inputs.
Do not claim the 4open link has been reviewer-browser verified until it is
tested outside the author account.
Do not claim all data and licence blockers are closed.
