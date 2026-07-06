# Paper10 CEUS baseline-hardened manuscript patch

Date: 2026-07-06

Status: bounded manuscript patch. This file does not replace the full manuscript
draft and does not add a new experiment. It provides drop-in wording for the
next CEUS manuscript assembly pass using
`e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md` as the current
baseline and inference boundary.

## Abstract Result Sentences

In Bishan, the validated 20x16/top5 value filter produced a descriptive matched
5-seed reward anchor: mean 100-step reward was 69.4705 for the value-filter
policy and 67.5437 for the matched Paper9 baseline under the same H=5, K=50,
executable-mask protocol. The outcome was mixed seed-wise, with the value filter
winning 3 of 5 seeds and losing seeds 0 and 4; therefore the current evidence
does not support uniform superiority or inferential superiority.

## Results: Bishan Matched Baseline Comparison

The Bishan 20x16/top5 policy remained the only positive performance anchor after
baseline hardening. Across the locked seeds 0-4, value-filter mean reward was
69.4705 compared with 67.5437 for the matched Paper9 `rank_seed2028` baseline,
and sample standard deviation was lower for the value-filter policy (1.0004
versus 7.2246). The paired reward deltas were -3.2408, 3.6137, 8.4242, 9.0620
and -8.2248. This establishes a descriptive matched 5-seed reward anchor, but
not a uniform seed-wise improvement. A diagnostic-only two-sided sign test gives p=1.0000 for the 3-win/2-loss split, so the result should remain descriptive unless a future predefined inference plan is added before new rollouts.

## Results: Mechanism and Secondary Metrics

The mechanism evidence separates executable-mask necessity from value-filter
superiority. Removing the executable mask reduced mean reward from 69.4705 to
40.3515 and produced 100 zero-swap steps and 98 negative zero-swap steps,
supporting executable-mask necessity for valid rollouts. By contrast, the
ungated top-4 control matched the full gated masked reward, so the monitor gate
should be described as evidence control for label escalation rather than as a
separately demonstrated online reward-gain mechanism. Secondary metrics were
mixed relative to matched Paper9: reward and reward variation favored the
value-filter anchor, while not every final slope, contiguity and baimu-area
indicator moved in the same favorable direction.

## Discussion: Baseline Fairness and Inference Limits

The baseline-hardened interpretation is narrower but more defensible for CEUS.
Paper10 does not show that value filtering is robustly superior across every
seed, region or label scale. It shows that a monitor-gated value-filter
configuration can produce a higher descriptive mean reward than a matched
Paper9 baseline in the Bishan 20x16/top5 setting, while the mixed seed-wise
outcome requires conservative reporting. This framing keeps the contribution in
decision-support terms: the workflow records when a value-label configuration
is usable, when it fails to scale, and when comparator evidence remains only
diagnostic.

## Discussion: Applicability Boundary

The Stage 3 50-state rows remain Stage 3 boundary evidence, and the later
candidate-score sweep did not overturn that boundary. Dongxing/Neijiang remains
Dongxing/Neijiang calibration evidence, not proof of robust transfer
superiority. The current block-level planning-unit abstraction and queen
contiguity are still insufficient to claim deployment-ready irregular cadastral
planning. These boundaries should stay visible because they define the regime in
which the current GeoJEPA-MPC evidence is credible.

## Claim-Evidence Table Updates

| claim | hardened status | manuscript wording |
|---|---|---|
| Bishan 20x16/top5 improves mean reward versus matched Paper9. | supported_descriptive | descriptive matched 5-seed reward anchor |
| Value filter improves every seed. | not_supported | mixed seed-wise outcome; wins 3/5 seeds |
| Value filter is inferentially superior. | not_supported | diagnostic_only sign-test readout; no predefined inference plan |
| Executable mask is necessary for valid rollouts. | supported_descriptive | executable-mask necessity |
| Monitor gate directly improves online reward. | not_supported | monitor gate as evidence control |
| Stage 3 50-state rows show scale-up success. | not_supported | Stage 3 boundary evidence |
| Dongxing proves robust transfer superiority. | not_supported | Dongxing/Neijiang calibration evidence |
| Irregular cadastral deployment is solved. | not_supported | deployment boundary remains open |
