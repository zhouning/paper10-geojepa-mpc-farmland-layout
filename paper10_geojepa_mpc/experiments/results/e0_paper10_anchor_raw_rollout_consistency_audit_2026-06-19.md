# Paper10 anchor raw-rollout consistency audit

Date: 2026-06-19

Status: source-derived consistency audit for the Bishan 20x16/top5 frozen anchor.

This audit recomputes the tracked anchor from raw rollout step records. It does not add a new experimental claim. No rollout was rerun.

## Consistency status

- Summary match: PASS
- Stage 3 frozen-anchor match: PASS
- Tolerance: `1e-08`

## Raw aggregate recomputed from steps

| metric | value |
|---|---:|
| n_episodes | 5 |
| total_reward_mean | 69.4705 |
| total_reward_std_sample | 1.0004 |
| total_reward_min | 67.7135 |
| total_reward_max | 70.2252 |
| slope_change_pct_mean | -1.2507 |
| cont_change_mean | 0.0192 |
| baimu_area_change_ha_mean | -207.2639 |

## Seed-level step recomputation

| seed | steps | total reward from steps | reported total reward | abs delta |
|---:|---:|---:|---:|---:|
| 0 | 100 | 67.7135 | 67.7135 | 0.0000 |
| 1 | 100 | 70.2252 | 70.2252 | 0.0000 |
| 2 | 100 | 69.7218 | 69.7218 | 0.0000 |
| 3 | 100 | 69.8245 | 69.8245 | 0.0000 |
| 4 | 100 | 69.8677 | 69.8677 | 0.0000 |

## Source files

- raw rollout: `paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json`
- raw rollout: `paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json`
- rollout summary: `paper10_geojepa_mpc\experiments\results\e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`
- Stage 3 summary: `paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json`

## Interpretation boundary

This audit recomputes the Bishan 20x16/top5 anchor from tracked raw rollout step records and checks consistency with the packaged rollout summary and Stage 3 frozen-anchor row.
The audit supports evidence-chain consistency only; manuscript wording should continue to distinguish this anchor from Stage 3 50-state boundary evidence and from Dongxing transfer calibration evidence.

## Regeneration command

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.anchor_raw_rollout_consistency_audit --raw-rollout paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json --raw-rollout paper10_geojepa_mpc\experiments\results\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json --summary-json paper10_geojepa_mpc\experiments\results\e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json --stage3-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md
```
