# Paper10 manuscript text/table consistency audit

Date: 2026-06-19

Status: source-derived manuscript text/table consistency audit.

This audit checks current manuscript-facing text against the frozen result tables and does not add a new experimental claim. No rollout was rerun.

overall consistency: PASS

## Source files

- table freeze JSON: `paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`
- document: `paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_draft_2026-06-18.md`
- document: `paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_reframe_2026-06-18.md`
- document: `paper10_geojepa_mpc\experiments\results\e0_paper10_project_proposal_opening_report_2026-06-18.md`
- document: `paper10_geojepa_mpc\experiments\results\e0_paper10_author_decision_matrix_2026-06-18.md`
- document: `paper10_geojepa_mpc\experiments\results\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md`

## Frozen tokens checked

| item | token |
|---|---|
| Bishan anchor mean | 69.4705 |
| matched baseline mean | 67.5437 |
| Bishan anchor sample std | 1.0004 |
| matched baseline sample std | 7.2246 |
| Stage 3 confirmatory means | 64.2960, 66.2544 |
| diagnostic near-pass mean | 67.4913 |
| boundary guardrails | must not be pooled, direct 50-state Bishan scale-up success, robust Bishan-to-Dongxing transfer superiority |

## Document audit

| document | status | missing numeric tokens | missing boundary tokens | forbidden positive hits | unsupported inferential hits |
|---|---|---|---|---:|---:|
| paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_draft_2026-06-18.md | PASS | none | none | 0 | 0 |
| paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_reframe_2026-06-18.md | PASS | none | none | 0 | 0 |
| paper10_geojepa_mpc\experiments\results\e0_paper10_project_proposal_opening_report_2026-06-18.md | PASS | none | none | 0 | 0 |
| paper10_geojepa_mpc\experiments\results\e0_paper10_author_decision_matrix_2026-06-18.md | PASS | none | none | 0 | 0 |
| paper10_geojepa_mpc\experiments\results\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md | PASS | none | none | 0 | 0 |

## Interpretation boundary

- PASS means the checked manuscript-facing text contains the frozen table numbers and required boundary guardrails.
- PASS does not mean the formal manuscript is ready for submission.
- Any future text edit that changes these numbers or turns a boundary into a positive claim should update the freeze or fail preflight.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.manuscript_text_table_consistency_audit --table-freeze-json paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --document paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_draft_2026-06-18.md --document paper10_geojepa_mpc\experiments\results\e0_ceus_stage3_manuscript_reframe_2026-06-18.md --document paper10_geojepa_mpc\experiments\results\e0_paper10_project_proposal_opening_report_2026-06-18.md --document paper10_geojepa_mpc\experiments\results\e0_paper10_author_decision_matrix_2026-06-18.md --document paper10_geojepa_mpc\experiments\results\e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_text_table_consistency_audit_2026-06-19.md
```
