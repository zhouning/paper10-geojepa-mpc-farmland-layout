# Paper10 CEUS baseline and inference hardening audit

Date: 2026-07-06

Status: source-derived CEUS baseline and inference hardening audit.

No training, rollout, algorithm redesign, or post-hoc tuning was performed.

## Source Provenance

- Matched 5-seed audit: `paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json`
- Mechanism ablation packet: `paper10_geojepa_mpc\experiments\results\e0_paper10_mechanism_ablation_packet_2026-06-20.json`

## Paired Reward Boundary

| metric | value |
|---|---:|
| matched seeds | 5 |
| baseline mean reward | 67.5437 |
| value-filter mean reward | 69.4705 |
| paired mean delta | 1.9269 |
| paired median delta | 3.6137 |
| paired min delta | -8.2248 |
| paired max delta | 9.0620 |
| candidate wins | 3 |
| candidate losses | 2 |
| ties | 0 |
| diagnostic sign-test p | 1.0000 |

Sign-test classification: `diagnostic_only`.

This is a mixed seed-wise outcome. The descriptive mean reward anchor is supported for Bishan 20x16/top5, but uniform superiority is not supported and inferential superiority is not supported.

## Seed-Level Rows

| seed | baseline reward | value-filter reward | delta | outcome |
|---:|---:|---:|---:|---|
| 0 | 70.9543 | 67.7135 | -3.2408 | loss |
| 1 | 66.6115 | 70.2252 | 3.6137 | win |
| 2 | 61.2976 | 69.7218 | 8.4242 | win |
| 3 | 60.7625 | 69.8245 | 9.0620 | win |
| 4 | 78.0925 | 69.8677 | -8.2248 | loss |

## Secondary Metric Tradeoffs

Classification: `reward_descriptive_secondary_mixed`.

| metric | delta vs matched Paper9 | direction |
|---|---:|---|
| slope_change_pct_mean | 0.0138 | aligned |
| cont_change_mean | -0.0003 | tradeoff |
| baimu_area_change_ha_mean | 4.5905 | aligned |

## Claim Gates

| claim gate | status | manuscript wording |
|---|---|---|
| descriptive mean reward anchor | True | descriptive matched 5-seed reward anchor |
| mixed seed-wise outcome | True | mixed seed-wise outcome |
| uniform superiority | False | uniform superiority is not supported |
| inferential superiority | False | inferential superiority is not supported |
| executable-mask necessity | True | executable-mask necessity |
| monitor gate reward gain | False | monitor gate as evidence control |
| Stage 3 50-state scale-up | False | Stage 3 boundary evidence |
| transfer superiority | False | Dongxing/Neijiang calibration evidence |

## Interpretation Boundary

Use this audit to harden CEUS manuscript language. It supports a bounded descriptive Bishan 20x16/top5 mean-reward statement, documents executable-mask necessity, and treats the monitor gate as evidence control rather than as a separately proven online reward-gain mechanism.

The current evidence does not support broad scale-up, transfer superiority, or cadastral deployment claims.
