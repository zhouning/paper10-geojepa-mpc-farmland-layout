# Paper10 CEUS review-driven optimization register

Status: CEUS review-driven technical optimization register.

This register records what was changed after the strict CEUS-style review. It
separates source-derived technical audits from future experiments that would be
needed for stronger claims.

## Completed in this pass

| reviewer concern | technical response | evidence file | claim effect |
|---|---|---|---|
| Monitor thresholds may be arbitrary. | Added strict/default/lenient monitor-threshold sensitivity audit and preserved recorded-threshold provenance. | `e0_paper10_ceus_monitor_threshold_sensitivity_2026-06-27.md` | Bishan 20x16/top5 is robust under the tested threshold sets; 10x12/top4 is preserved as a historical-threshold pilot, not a current CEUS default pass. |
| Baseline policy is unclear. | Added CEUS mechanism-claim audit with matched Paper9 masked baseline as default comparator and pairwise-only evidence as diagnostic/model-initialization evidence. | `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md` | Paper10 claims must compare against matched Paper9 unless explicitly labelled as diagnostic. |
| No-mask ablation may be overinterpreted. | Mechanism audit separates executable-mask necessity from value-filter superiority. | `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md` | No-mask failures support mask necessity only; they do not prove full value-filter superiority. |
| Monitor gate may be overclaimed as direct online reward gain. | Mechanism audit detects equal reward between full_gated_masked and ungated_top4. | `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md` | Monitor gate is framed as evidence control, not a demonstrated online reward-gain mechanism. |
| Secondary metrics may conflict with reward. | Mechanism audit reports secondary metric tradeoffs against matched Paper9. | `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md` | The result is mixed: slope and baimu-area deltas align, contiguity delta is a tradeoff. |
| 50-state evidence may be overstated. | Mechanism audit keeps Stage 3 50-state delta versus Paper9 as a boundary check. | `e0_paper10_ceus_mechanism_claim_audit_2026-06-27.md` | Positive 50-state scale-up remains unsupported because best value-filter delta versus Paper9 is negative. |

## Current technical interpretation

- The strongest retained performance anchor is still Bishan 20x16/top5.
- The current algorithmic story should be written as a monitor-gated
  geospatial decision-support workflow with executable-mask enforcement.
- The code-level audits now block the main overclaims identified by the CEUS
  review: arbitrary threshold selection, ambiguous comparator use, no-mask
  overinterpretation, monitor-gate reward overclaiming, mixed secondary-metric
  treatment, and positive 50-state scale-up language.

## Not solved by this pass

| open item | why it remains open | required next evidence |
|---|---|---|
| New real-data planning-quality evaluation. | The new files are source-derived audits; they do not run new long-horizon real-data rollouts. | A predefined full-data rollout protocol with matched comparator, seeds, and locked metrics. |
| Multi-region robustness. | Dongxing/Neijiang remain calibration or stress-test evidence under current files. | Matched multi-region rollouts with the same baseline policy and monitor gates. |
| Strong value-filter superiority. | Current ungated_top4 reward matches full_gated_masked in the mechanism packet. | A matched ablation where full value-filtered MPC beats ungated and heuristic comparators under the same rollout settings. |
| Inferential statistical claims. | Existing policy is descriptive statistics only. | A predefined inferential analysis plan before adding p-values or confidence-interval claims. |
| Final CEUS manuscript conversion. | The algorithm and experiment boundary still needs author confirmation before final writing. | Manuscript rewrite that imports these audits as wording constraints, not as new performance experiments. |

## Recommended next action

Proceed to a bounded CEUS manuscript rewrite only if the target claim remains:
evidence-controlled decision-support workflow, not broad agricultural-AI
scale-up success. If a stronger claim is desired, run the open real-data and
multi-region experiments before writing the final paper.
