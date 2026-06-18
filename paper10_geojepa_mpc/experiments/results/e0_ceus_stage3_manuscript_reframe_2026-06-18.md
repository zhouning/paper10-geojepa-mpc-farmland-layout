# Paper10 CEUS Stage 3 manuscript reframe

Date: 2026-06-18

Status: CEUS Stage 3 manuscript reframe. This file updates the
manuscript-facing claim boundary after the original-vision Stage 3
confirmatory rollouts. It is not a final submission manuscript and does not
close the repository DOI, licence, full-data access, citation-policy,
statistical-policy, or figure-export blockers.

Source controls used for this reframe:

- `e0_ceus_research_article_manuscript_draft_2026-06-12.md`
- `e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.md`
- `e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`

## Paper10 now solves

Paper10 now solves a bounded evidence-control problem: when can
monitor-gated value labels be trusted enough to train a GeoJEPA-MPC value
filter for constrained farmland layout planning, and where does that evidence
stop? The current answer is positive at the Bishan 20x16/top5 anchor and
negative for broad 50-state scale-up under the matched Paper9 baseline used in
Stage 3.

## One-sentence argument

In constrained farmland layout planning, we show that monitor-gated value
labels can improve and stabilize GeoJEPA-MPC rollouts at the validated Bishan
20x16/top5 scale, supported by five-seed reward and matched-baseline checks,
while Stage 3 confirmatory rollouts show that the tested 50-state value-label
rows did not beat the matched Paper9 baseline and therefore bound the method
as a calibrated planning-support workflow rather than a broad scale-up result.

## Terminology ledger

| canonical term | first-use definition | manuscript rule |
|---|---|---|
| GeoJEPA-MPC | A geospatial JEPA and model-predictive planning workflow for constrained farmland layout planning. | Use as the method name; avoid renaming it as a generic RL solver. |
| monitor-gated value labels | Finite-horizon return labels accepted only after candidate-regret, overlap and one-step-regret checks. | Present as the quality-control mechanism that decides whether value-head training is manuscript-facing. |
| value filter | The scalar value head used to filter candidate actions during rollout. | Report label scale, top-k, horizon, baseline and rollout seeds with each performance claim. |
| matched Paper9 baseline | The `paper9 rank_seed2028` checkpoint rolled out under the same Stage 3 horizon, top-k, mask and seed protocol. | Use as the Stage 3 comparator unless the author explicitly freezes a separate pairwise-only baseline. |
| confirmatory 50-state rows | Stage 1 pass rows advanced to Stage 3 value-filter rollouts. | Report as confirmatory evidence that did not exceed the matched Paper9 baseline. |
| diagnostic_near_pass | A Stage 1 near-pass row rolled out for diagnostic context. | It must not be pooled with confirmatory rows or used to strengthen the 50-state claim. |

## Title replacement

Monitor-gated value labels bound GeoJEPA-MPC farmland layout planning

Alternative conservative title:

Monitor-gated value filtering for calibrated farmland layout planning

## Abstract replacement

Constrained farmland layout planning requires sequential spatial decisions
whose long-horizon value can diverge from immediate reward. We present a
monitor-gated GeoJEPA-MPC workflow that generates finite-horizon value labels,
checks label quality before value-head training, and applies executable masks
during rollout. In Bishan, the validated 20x16/top5 value filter reached
69.4705 mean reward across five 100-step seeds, compared with 67.5437 for the
matched Paper9 baseline and 65.2566 for the earlier 10x12/top4 pilot. Stage 3
confirmatory tests then evaluated the two passing 50-state rows under matched
rollout settings. The 50x16/top6 row reached 64.2960 mean reward and the
50x24/top12 row reached 66.2544, both below the matched Paper9 baseline; a
diagnostic near-pass row reached 67.4913 and must not be pooled with
confirmatory rows. Dongxing/Neijiang evidence remains useful as a calibration
and stress-test package, but it does not support robust Bishan-to-Dongxing
transfer superiority. These results support monitor-gated value filtering as
a reproducible evidence-control workflow for constrained geospatial planning,
while bounding claims about broad 50-state scaling, arbitrary cadastral parcel
deployment and cross-region transfer superiority.

## Results replacement

### Monitor-gated value labels improved the validated Bishan anchor

The validated Bishan 20x16/top5 value-filter anchor remains the primary
positive result. Across five 100-step rollout seeds, the 20x16/top5 value
filter reached 69.4705 mean reward with sample standard deviation 1.0004. In
the Stage 3 matched comparison, the Paper9 `rank_seed2028` baseline reached
67.5437 mean reward with sample standard deviation 7.2246. The anchor
therefore exceeded the matched Paper9 baseline by 1.9269 reward units and
showed lower seed-level variation under the tested rollout protocol.

### Stage 3 did not support broad 50-state scale-up

Stage 3 trained and rolled out only the authorized Bishan rows from the
original-vision validation pass. The confirmatory 50-state row
`frontier_random050_50x16_h5_seed48_f050` selected top-k 6 and reached 64.2960
mean reward, 3.2477 below the matched Paper9 baseline. The confirmatory row
`frontier_random050_50x24_h5_seed47_f075` selected top-k 12 and reached
66.2544 mean reward, 1.2893 below the matched baseline. These confirmatory
rows completed value-filter rollout but did not improve on the comparator.
They should therefore be reported as a scale boundary, not as a positive
50-state result.

### Diagnostic near-pass evidence remains separate

The diagnostic_near_pass row `frontier_random050_50x24_h5_seed48_f075`
selected top-k 12 and reached 67.4913 mean reward, 0.0524 below the matched
Paper9 baseline. This row is useful because it shows a near-baseline failure
mode under the same rollout settings. It must not be pooled with the
confirmatory rows or used to imply that Stage 3 established a broad 50-state
claim.

### Dongxing/Neijiang remains a calibration and stress-test result

The Dongxing/Neijiang evidence should remain in the manuscript as external
calibration and stress-test evidence. Return-label scaling improved both
transfer and scratch families relative to pairwise-only labels, but scratch
remained higher than Bishan-initialized transfer in several matched
comparisons. Do not claim robust Bishan-to-Dongxing transfer superiority.

## Discussion replacement

The Stage 3 evidence changes the manuscript from a scale-up story into a
claim-boundary story. The strongest supported contribution is not that larger
value-label sets automatically improve GeoJEPA-MPC planning. It is that
monitor gates can separate a useful value-label scale from label sets that
remain unsuitable for manuscript-facing escalation.

This interpretation also clarifies why the failed 50-state results strengthen
the paper rather than merely weaken it. The 20x16/top5 anchor beat the matched
Paper9 baseline and stabilized five-seed rollout rewards, while the
confirmatory 50-state rows failed to beat that comparator. The monitor-gated
workflow therefore functions as an evidence-control layer: it tells the user
when value filtering is useful under a particular data, candidate and rollout
configuration, and when additional label scale is not enough.

The Stage 3 results keep several boundaries visible. The matched Paper9
baseline is the comparator used here; a separate pairwise-only baseline remains
unresolved unless the author explicitly accepts the Paper9 rank-checkpoint
baseline as that comparator. Dongxing/Neijiang supports local calibration and
stress testing, not robust transfer superiority. The current implementation
uses a block-level planning-unit abstraction and queen contiguity, so it also
does not solve arbitrary irregular cadastral parcel exchange.

## Conclusion replacement

Paper10 supports monitor-gated value filtering as a calibrated workflow for
constrained farmland layout planning. The validated Bishan 20x16/top5 value
filter improved reward relative to the matched Paper9 baseline, but Stage 3
confirmatory 50-state rows did not. The manuscript should therefore claim a
bounded, reproducible evidence-control workflow for GeoJEPA-MPC planning, not
direct 50-state Bishan scale-up success, solved irregular parcel deployment or
robust Bishan-to-Dongxing transfer superiority.

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| Monitor-gated value labels can improve Bishan GeoJEPA-MPC rollouts at the validated anchor scale. | Bishan 20x16/top5 mean reward 69.4705 versus matched Paper9 baseline 67.5437; sample standard deviation 1.0004 versus 7.2246. | supported |
| Stage 3 confirmatory 50-state rows did not beat the matched Paper9 baseline. | 50x16/top6 mean reward 64.2960 and 50x24/top12 mean reward 66.2544 versus matched Paper9 baseline 67.5437. | supported |
| The diagnostic near-pass row should not strengthen the 50-state claim. | diagnostic_near_pass 50x24/top12 seed48 mean reward 67.4913, still below baseline by 0.0524, and explicitly marked diagnostic. | supported |
| Dongxing/Neijiang supports calibration and stress testing. | Return-label scaling improves both transfer and scratch families, while scratch remains stronger in several matched comparisons. | supported with boundary |
| Broad 50-state deployment is established. | No Stage 3 confirmatory 50-state row exceeded the matched Paper9 baseline. | not supported |
| Robust Bishan-to-Dongxing transfer superiority is established. | Stage 2 and earlier Dongxing comparisons show mixed transfer-minus-scratch effects. | not supported |

## Current blockers before final submission

- The pairwise-only baseline policy remains unresolved unless the author
  explicitly accepts the matched Paper9 `rank_seed2028` baseline as the
  comparator.
- Repository DOI or reviewer link, code licence, generated-data rights and
  full-data access routes remain unresolved in
  `e0_submission_blocker_decision_packet_2026-06-11.md`.
- The final manuscript must update title, abstract, Results, Discussion,
  Conclusion, figure captions and table captions to use this Stage 3 claim
  boundary consistently.
- Do not claim direct 50-state Bishan scale-up success.
- Do not claim robust Bishan-to-Dongxing transfer superiority.
