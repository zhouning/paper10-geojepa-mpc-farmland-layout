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
| Full-data smoke conditions were previously mismatched. | Ran matched full-Bishan 5-step smoke runs for matched Paper9 and value-filter with seed 0, H=5, K=50, and executable masks. | `e0_paper10_real_env_matched_smoke_boundary_audit_2026-06-27.md` | The two traces have identical actions and rewards; this supports execution-chain reachability and condition alignment only, not value-filter superiority. |
| Short matched smokes do not test long-horizon divergence. | Added a locked 100-step seed0 protocol and audit for matched Paper9 versus value-filter under the same H=5/K=50/executable-mask settings. | `e0_paper10_ceus_realdata_longhorizon_protocol_2026-06-27.md`; `e0_paper10_real_env_longhorizon_seed0_pilot_audit_2026-06-27.md` | The value-filter candidate did not beat matched Paper9 on seed0 (`67.7135` versus `70.9543`), so value-filter superiority remains unsupported and matched seeds `0-4` are the next confirmatory step if stronger evidence is still desired. |

## Current technical interpretation

- The strongest retained performance anchor is still Bishan 20x16/top5.
- The current algorithmic story should be written as a monitor-gated
  geospatial decision-support workflow with executable-mask enforcement.
- The code-level audits now block the main overclaims identified by the CEUS
  review: arbitrary threshold selection, ambiguous comparator use, no-mask
  overinterpretation, monitor-gate reward overclaiming, mixed secondary-metric
  treatment, long-horizon value-filter superiority from seed0, and positive
  50-state scale-up language.

## Not solved by this pass

| open item | why it remains open | required next evidence |
|---|---|---|
| New real-data planning-quality evaluation. | The new files now include a matched five-step full-Bishan smoke pair and a locked 100-step seed0 pilot; the seed0 pilot is negative for value-filter superiority and remains single-seed evidence. | The same predefined full-data rollout protocol on matched seeds `0-4`, with locked metrics and no post-hoc threshold or weight tuning. |
| Multi-region robustness. | Dongxing/Neijiang remain calibration or stress-test evidence under current files. | Matched multi-region rollouts with the same baseline policy and monitor gates. |
| Strong value-filter superiority. | Current ungated_top4 reward matches full_gated_masked in the mechanism packet. | A matched ablation where full value-filtered MPC beats ungated and heuristic comparators under the same rollout settings. |
| Inferential statistical claims. | Existing policy is descriptive statistics only. | A predefined inferential analysis plan before adding p-values or confidence-interval claims. |
| Final CEUS manuscript conversion. | The algorithm and experiment boundary still needs author confirmation before final writing. | Manuscript rewrite that imports these audits as wording constraints, not as new performance experiments. |

## Recommended next action

Proceed to a bounded CEUS manuscript rewrite only if the target claim remains:
evidence-controlled decision-support workflow, not broad agricultural-AI
scale-up success. If a stronger value-filter claim is desired, first run the
locked matched seeds `0-4` real-data protocol and any multi-region experiments
before writing the final paper.
