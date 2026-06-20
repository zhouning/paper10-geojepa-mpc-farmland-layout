# Paper10 mechanism ablation evidence packet

Status: mechanism experiment evidence packet, not a manuscript claim.

## Claim Boundary

- GeoJEPA itself is prior art and is not claimed as the Paper10 invention.
- Paper10's tested mechanism is monitor-gated value labels plus executable masks plus value-filtered MPC.
- The 50-state evidence remains boundary evidence unless matched rollouts beat the predefined comparator.

## Monitor Gates

| gate | top-k | decision | class | candidate regret | candidate overlap | one-step regret | failed metrics |
|---|---:|---|---|---:|---:|---:|---|
| gated_top5 | 5 | continue | pass | 0.1877 | 0.6300 | 2.4626 | none |
| ungated_top4 | 4 | stop | stop | 0.4680 | 0.4875 | 2.4626 | candidate_topk_regret,candidate_topk_overlap |

## Matched Bishan Mechanism Conditions

| condition | mean reward | std sample | reward delta vs full | std delta vs full | slope pct | cont | baimu ha | zero swaps | negative zero swaps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_gated_masked | 69.4705 | 1.0004 | 0.0000 | 0.0000 | -1.2507 | 0.0192 | -207.2639 | 0.0000 | 0.0000 |
| heuristic_paper9_masked | 67.5437 | 7.2246 | -1.9269 | 6.2242 | -1.2645 | 0.0195 | -211.8544 | 0.0000 | 0.0000 |
| no_mask | 40.3515 | 10.4853 | -29.1191 | 9.4849 | -1.0967 | 0.0142 | -195.3967 | 100.0000 | 98.0000 |
| ungated_top4 | 69.4705 | 1.0004 | 0.0000 | 0.0000 | -1.2507 | 0.0192 | -207.2639 | 0.0000 | 0.0000 |

## Stage 3 Boundary Link

The Stage 3 50-state sweep is included only to keep the mechanism result bounded. It must not be written as positive 50-state scale-up evidence unless a matched 50-state condition beats the predefined comparator.

## Interpretation

A useful mechanism claim requires the full gated and masked condition to outperform one or more matched ablations without relying on forbidden broad GeoJEPA, direct 50-state, or robust transfer claims.
