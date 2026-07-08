# Paper10 figure/table caption-claim packet

Date: 2026-06-19

Status: source-derived figure/table caption-claim packet.

This packet provides journal-neutral draft captions and bounded claim wording for source-covered figure/table items. It does not add a new experimental claim. No rollout was rerun.

caption-claim packet: PASS
submission-ready figure/table package: NO

## Source files

- source_coverage_audit_json: `paper10_geojepa_mpc/experiments/results/e0_paper10_figure_table_source_coverage_audit_2026-06-19.json`
- result_tables_freeze_json: `paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.json`

## Journal-neutral draft captions and claim boundaries

| item | placement | final artwork | draft caption | allowed claims | forbidden claims | unresolved manuscript fields |
|---|---|---|---|---|---|---|
| Main Figure 1 | main | pending | Journal-neutral draft caption: monitor-gated value labels pass through label generation, monitor checks, value-filter training, candidate filtering, and masked MPC rollout before manuscript claims are accepted. | workflow schematic only; no new quantitative result<br>monitor gates control escalation before value-filter training | Do not describe the workflow schematic as experimental evidence.<br>Do not claim irregular cadastral deployment is solved. | final schematic artwork<br>journal figure dimensions<br>target-journal caption length |
| Main Figure 2 | main | preview_available | Journal-neutral draft caption: Bishan 20x16/top5 is the positive anchor under the tested matched rollout protocol, with mean reward 69.4705 versus 67.5437 for the matched comparator and sample standard deviation 1.0004 versus 7.2246. | Bishan 20x16/top5 is the positive anchor only under the tested rollout protocol<br>Use as the positive Bishan anchor only. | Do not generalize this panel to direct 50-state Bishan scale-up success.<br>Do not describe the difference with inferential testing language. | final figure number<br>inset decision<br>target-journal caption length |
| Main Figure 3 | main_or_supplement_pending_journal_limit | preview_available | Journal-neutral draft caption: Stage 3 completed 50-state boundary rows but did not support a direct positive scale-up claim under the matched comparator (frontier_random050_50x16_h5_seed48_f050 mean 64.2960 delta -3.2477; frontier_random050_50x24_h5_seed47_f075 mean 66.2544 delta -1.2893; frontier_random050_50x24_h5_seed48_f075 mean 67.4913 delta -0.0524). The diagnostic near-pass must not be pooled with confirmatory rows. | Use as Stage 3 boundary evidence.<br>Report separately; must not be pooled.<br>diagnostic near-pass must not be pooled | direct 50-state Bishan scale-up success<br>Do not pool the diagnostic near-pass with confirmatory rows. | final main-versus-supplementary placement<br>target-journal caption length |
| Main Figure 4 | main | preview_available | Journal-neutral draft caption: Dongxing/Neijiang return-label scaling provides calibration and stress-test evidence; the 50x16 transfer-minus-scratch value is -4.1141, so this panel must not be written as robust transfer superiority. | Use as calibration or stress-test evidence.<br>Dongxing/Neijiang supports calibration and stress-test value | robust Bishan-to-Dongxing transfer superiority<br>Do not use as a positive transfer claim. | final figure number<br>metric panel placement<br>target-journal caption length |
| Supplementary Figure S1 | supplementary_pending_journal_limit | preview_available | Journal-neutral draft caption: Dongxing low-label stress-test results show mixed transfer behavior and should be used as boundary context rather than a robust superiority claim. | low-label transfer behavior is mixed<br>use as supplementary stress-test context unless journal limits require another placement | Do not claim low-label transfer superiority is robust.<br>Do not convert this supplementary stress test into a main positive result without updating the source map. | final main-versus-supplementary placement<br>target-journal caption length |
| Main Table 1 | main | preview_available | Journal-neutral draft caption: monitor-selected Bishan gates summarize which label settings were allowed to advance to manuscript-facing value-filter testing. | monitor gates authorize escalation; they do not prove general scale-up<br>use gate status as evidence-control context | Do not claim monitor acceptance proves deployment readiness.<br>Do not treat gate selection as an independent performance experiment. | final table number<br>target-journal caption length |
| Main Table 2 | main | preview_available | Journal-neutral draft caption: frozen matched-baseline table reports the positive Bishan anchor and Stage 3 boundary rows using tracked Stage 3 and raw-rollout consistency evidence. Algorithm-readiness addendum records the current true-reward guard evidence: mean reward 72.1918 versus 65.8876, delta 6.3041, seed wins 20 / 20, and bootstrap 95% CI lower 4.1401, with mean audited actions 7.7605. | Table 1 is the only positive Bishan performance anchor<br>Stage 3 rows are boundary evidence<br>diagnostic near-pass must not be pooled<br>Algorithm-readiness addendum is current true-reward guard evidence<br>setting-specific guard only | Do not rewrite Stage 3 boundary rows as direct 50-state Bishan scale-up success.<br>Do not add unsupported comparison-testing wording to the frozen table.<br>Do not treat the guard addendum as final submission readiness.<br>Do not claim a universal fixed switch margin. | rounding<br>main-text placement<br>target-journal caption length |
| Main Table 3 | main_or_supplement_pending_journal_limit | preview_available | Journal-neutral draft caption: Dongxing return-label scaling summarizes descriptive calibration evidence and keeps robust transfer superiority unsupported. | return-label scaling is descriptive calibration evidence<br>Use as calibration or stress-test evidence. | robust Bishan-to-Dongxing transfer superiority<br>Do not treat descriptive Dongxing scaling as a confirmatory transfer test. | whether full metric table is main text<br>target-journal caption length |

## Submission blockers

- target-journal caption length
- final figure/table export package
- final schematic artwork for Main Figure 1
- final main-versus-supplementary placement

## Interpretation boundary

- PASS means every source-covered figure/table item has a draft caption, allowed claims, forbidden claims, and unresolved manuscript fields.
- PASS does not mean the formal manuscript is ready for submission.
- Do not claim direct 50-state Bishan scale-up success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
- The diagnostic near-pass must not be pooled with confirmatory rows.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.figure_table_caption_claim_packet --source-coverage-audit-json paper10_geojepa_mpc\experiments\results\e0_paper10_figure_table_source_coverage_audit_2026-06-19.json --result-tables-freeze-json paper10_geojepa_mpc\experiments\results\e0_paper10_manuscript_result_tables_freeze_2026-06-19.json --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_figure_table_caption_claim_packet_2026-06-19.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_figure_table_caption_claim_packet_2026-06-19.md
```
