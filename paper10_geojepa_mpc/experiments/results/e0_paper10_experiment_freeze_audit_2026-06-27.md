# Paper10 experiment-freeze audit

Date: 2026-06-27

Status: algorithm_freeze_candidate

This audit records the current decision boundary for Paper10 after the
2026-06-20 formal manuscript draft and the 2026-06-26 no-go submission
boundary. It is a planning and claim-control document. It does not rerun
experiments, does not add a new experimental claim, and does not close any
repository, licence, data-access, citation, statistics, or figure-export
blocker.

## Source basis

- `e0_paper10_formal_manuscript_draft_2026-06-20.md`
- `e0_paper10_submission_readiness_boundary_2026-06-26.md`
- `e0_paper10_manuscript_result_tables_freeze_2026-06-19.md`
- `e0_paper10_mechanism_ablation_packet_2026-06-20.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_paper10_stage3_50x24_candidate_score_sweep_2026-06-20.md`
- `e0_paper10_claim_source_consistency_audit_2026-06-18.md`
- `e0_windows_realdata_20x16_top5_reproduction_2026-06-10.md`
- `e0_paper10_real_data_availability_audit_2026-06-18.md`
- `e0_paper10_real_data_integrity_smoke_2026-06-18.md`
- `e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md`

## Decision

The default next phase is experiment closure and manuscript assembly within the
current claim boundary, not open-ended algorithm redesign.

Algorithm work should resume only if the author wants a stronger claim than
the current evidence supports, such as direct 50-state Bishan scale-up, robust
Bishan-to-Dongxing transfer superiority, or operational irregular-cadastral
parcel deployment.

## Evidence status

| item | status | basis | freeze implication |
|---|---|---|---|
| Bishan 20x16/top5 anchor | supported | mean reward 69.4705 versus matched Paper9 67.5437; sample std 1.0004 versus 7.2246 | Keep as the only positive Bishan performance anchor. |
| Real-data reproduction | supported | Windows real-data rerun reproduced the canonical labels, monitor decision, checkpoint hash, and five-seed rollout aggregate | Treat Bishan full-data availability as an access-route and rights problem, not as an algorithm-evidence gap. |
| Executable mask mechanism | supported | no-mask reward 40.3515 versus full gated masked 69.4705, with many zero-swap actions | Keep executable masks as a central mechanism claim. |
| Monitor-gated value labels | supported as quality control | gated top5 passed monitor gates; ungated top4 failed monitor gates | Describe gating as evidence control; do not claim gating alone separated rollout reward under the recorded matched ablation. |
| Ungated top4 control | not separated from anchor | ungated_top4 reward equals full_gated_masked in the mechanism packet | Use as a boundary on the gating-performance wording. |
| Stage 3 50-state confirmatory rows | not supported as positive scale-up | 50x16 and 50x24 rows remained below matched Paper9 baseline | Use as boundary evidence only. |
| 50x24 candidate-score rescue | not supported | best blend0.10 row remained below matched Paper9 baseline | Do not continue tuning candidate-score weights unless the goal changes. |
| Dongxing/Neijiang transfer superiority | not supported | transfer-minus-scratch remained mixed or negative in key rows | Use Dongxing/Neijiang as calibration or stress-test evidence only. |
| Irregular cadastral deployment | not supported | current implementation is block-level with deterministic paired swaps | Keep operational deployment claims out of the manuscript. |

## Allowed manuscript claim

Paper10 may claim that monitor-gated value labels, executable masks, and
value-filtered MPC provide a reproducible and bounded planning-support workflow
for constrained Bishan farmland layout planning. The supported positive result
is the 20x16/top5 Bishan anchor under the matched rollout protocol.

## Forbidden claim drift

- Do not claim direct 50-state Bishan scale-up success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim solved irregular cadastral parcel deployment.
- Do not claim a full Constrained MDP, CPO, or RCPO solver.
- Do not claim Paper10 invented GeoJEPA.
- Do not pool the diagnostic near-pass row with confirmatory Stage 3 rows.
- Do not use five-step real-environment smoke runs as planning-quality
  performance evidence.

## Experiment closure checklist

Before replacing the formal draft with a journal-specific manuscript, close or
explicitly carry these items:

| item | required action | algorithm change needed by default |
|---|---|---|
| Baseline policy | Freeze matched Paper9 `rank_seed2028` as the comparator or document a different author decision. | no |
| Statistics policy | Decide descriptive-only reporting versus additional seeds or tests. | no, unless stronger inference is required |
| Data access route | Fill code archive, full Bishan Tool2, GPKG-root, and Dongxing/Neijiang access records. | no |
| Figure export | Produce final journal-specific figure/table exports from the frozen source map. | no |
| Real-data warnings | Decide whether to document or clean libpysal connectivity and guarded divide warnings. | optional |
| 50-state ambition | If the manuscript must claim positive 50-state scale-up, redesign candidate generation or value-label training and rerun confirmatory tests. | yes |
| Transfer ambition | If the manuscript must claim transfer superiority, prepare comparable Dongxing/Neijiang pipelines and rerun transfer-vs-scratch tests. | yes |
| Deployment ambition | If the manuscript must claim cadastral deployment, add area tolerance, parcel geometry, compactness, and operational constraint tests. | yes |

## Recommended next sequence

1. Freeze the current method for a bounded planning-support paper.
2. Run repository preflight and the full Paper10 test suite after this audit is
   added.
3. If verification passes, edit the manuscript only inside the claim boundary
   above.
4. Resolve author decisions for baseline wording, statistics, data access,
   licence, citation policy, and final figure exports.
5. Re-enter algorithm development only for a deliberate stronger-claim track.

## Current go/no-go reading

| question | answer |
|---|---|
| Continue broad algorithm modification now? | No, not by default. |
| Do more experiments before manuscript assembly? | Yes, only closure or policy-driven experiments unless a stronger-claim track is chosen. |
| Is the current evidence sufficient for an unbounded algorithm-success paper? | No. |
| Is the current evidence sufficient for a bounded planning-support workflow manuscript draft? | Yes, with the blockers and claim locks above preserved. |