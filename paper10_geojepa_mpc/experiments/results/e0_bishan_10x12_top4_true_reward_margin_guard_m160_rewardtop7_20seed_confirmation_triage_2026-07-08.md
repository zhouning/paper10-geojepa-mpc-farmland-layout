# Bishan 10x12/top4 rewardtop7 20-seed confirmation

Date: 2026-07-08

Status: descriptive_confirmation

This packet extends the small-scale `rewardtop7 margin=1.60` guard from 5 to 20 matched seeds.
It is not final submission readiness.

## Protocol

- setting: `10x12/top4`
- baseline: `blend_w0p10`, horizon 5, top-k 50, 100-step rollouts
- guard: `rewardtop7 margin=1.60`
- audit set: selected action plus model-reward top7 actions
- seeds: 20 matched seeds
- post-hoc margin tuning in this task: false

## Result

| metric | value |
|---|---:|
| baseline mean reward | 66.2495 |
| guard mean reward | 72.2849 |
| mean delta vs baseline | 6.0354 |
| median delta vs baseline | 3.3491 |
| seed wins | 18 / 20 |
| seed losses | 2 / 20 |
| min seed delta | -0.7662 |
| max seed delta | 17.6598 |
| bootstrap 95% CI lower | 3.6258 |
| bootstrap 95% CI upper | 8.6207 |

## Interpretation

Use this as a 10x12/top4 setting-specific guard confirmation only.
It supports the transferable rewardtop7 guard mechanism only within the tested small-scale setting and calibrated margin.
It does not make `1.60` a universal fixed switch margin.

## Claim locks

Do not claim a universal fixed switch margin.
Do not claim direct 50-state Bishan scale-up success.
Do not claim robust Bishan-to-Dongxing transfer superiority.
Do not claim deployment-ready cadastral planning.
Do not treat this as final submission readiness.
