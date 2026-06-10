# Dongxing Results Synthesis for Paper10

Date: 2026-06-10

This synthesis consolidates the Dongxing/Neijiang real-data experiments run for
Paper10. It is intended to guide the paper narrative and prevent overclaiming.

## Evidence Ladder

1. Local Dongxing/Neijiang data are usable.

   The local environment loads 3711 blocks from 76376 parcels, with 70806
   parcels assigned to blocks. The initial environment has average farmland
   slope `10.5476`, contiguity `2.6314`, and 384 baimu-fang patches totaling
   `74341.9 ha`.

2. Paper10 can adapt to Dongxing's action space.

   The Bishan checkpoint can initialize a 3711-action Dongxing model by copying
   same-shaped tensors and reinitializing `action_emb.weight`. This makes
   cross-region model reuse technically feasible.

3. Pairwise-only training is not enough.

   At 1000 pairwise states, scratch is slightly better than transfer on
   pairwise regret, and rollout confirms that pairwise-only transfer is not a
   robust advantage.

4. Planner calibration matters.

   Reusing Bishan's `candidate-value-weight=0.1` is suboptimal for Dongxing.
   Pure value candidate filtering (`candidate-value-weight=1.0`) improves both
   transfer and scratch rollouts.

5. Real-environment return labels matter more.

   Moving from pairwise-only labels to Dongxing real-environment return labels
   improves rollout reward for both transfer and scratch families. The 50x16
   return-label checkpoints are the strongest Dongxing results so far.

## Main Rollout Table

All rows use the tuned Dongxing rollout setting:

- `--env-source neijiang`
- `--rollout-steps 100`
- `--horizon 5`
- `--top-k 50`
- `--seeds 0-4`
- `--mask-mode executable`
- `--selector value_filter`
- `--candidate-score-mode blend`
- `--candidate-value-weight 1.0`

| label type | family | episodes | mean reward | reward sd | mean slope change pct | mean contiguity change | mean baimu area change ha | checkpoint-mean reward sd |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| pairwise_1000s | transfer | 15 | 37.8893925916614 | 14.1352633600858 | -0.3424219820891 | 0.0172300695325141 | 5.30178919647058 | 12.9953628799359 |
| pairwise_1000s | scratch | 15 | 40.2110803350696 | 13.6594641971396 | -0.30525395814417 | 0.026323231439775 | 262.059208475224 | 9.41814422770678 |
| return_20x16_h5 | transfer | 15 | 41.7733004189559 | 10.7533323718661 | -0.302996119903207 | 0.021988017667381 | 157.21199984949 | 8.72222561932945 |
| return_20x16_h5 | scratch | 15 | 43.0396799073507 | 15.2827215930085 | -0.240349301350516 | 0.0303669042725326 | 460.306420471522 | 11.6114935515193 |
| return_50x16_h5 | transfer | 15 | 51.6182891684444 | 18.0526685790304 | -0.29047987873686 | 0.020492412647046 | 107.369615389442 | 19.2355264471805 |
| return_50x16_h5 | scratch | 15 | 55.7324381574268 | 19.9277864758067 | -0.262322189731164 | 0.0235623387414179 | 262.319346048888 | 21.7058940005209 |

## What We Can Claim

Supported claims:

- Paper10's code path now runs on a second real region, Dongxing/Neijiang.
- The model can be adapted from Bishan's 2600-block action space to Dongxing's
  3711-block action space.
- Dongxing performance is sensitive to planner candidate filtering.
- `candidate-value-weight=1.0` is better than the Bishan default `0.1` for this
  Dongxing setup.
- Real-environment return labels improve Dongxing rollout reward over
  pairwise-only labels.
- Scaling return labels from 20x16 to 50x16 improves mean reward for both
  transfer and scratch families.
- The strongest Dongxing row so far is scratch with 50x16 return labels:
  mean reward `55.7324`.

Unsupported claims:

- Do not claim Bishan-initialized transfer beats Dongxing scratch.
- Do not claim pairwise ranking metrics predict final rollout reward reliably.
- Do not claim the current Dongxing result proves general cross-region transfer
  superiority.
- Do not frame Dongxing as a clean positive transfer result.

## Scientific Interpretation

The Dongxing experiments are valuable because they show where Paper10 actually
generalizes and where it does not.

The method-level generalization is positive:

- the data pipeline can move to a second county-level environment;
- the action-space adaptation works;
- value-head candidate filtering works in the real environment;
- return-label scaling improves rollout reward.

The initialization-level transfer result is negative or neutral:

- transfer is technically feasible;
- transfer sometimes has stronger slope reduction;
- scratch remains better on family mean reward at both 20x16 and 50x16 return
  label scales.

The paper should therefore treat Dongxing as an external-region stress test and
label-target calibration study, not as a positive transfer benchmark.

## Paper10 Value

Paper10's value is not "Bishan weights transfer and beat local training." The
current evidence does not support that.

The stronger value proposition is:

> Paper10 introduces a GeoJEPA-MPC workflow for constrained farmland layout
> optimization, shows that value-head candidate filtering and real-environment
> return labels can be calibrated on real geospatial environments, and
> demonstrates on a second region that return-label scaling substantially
> improves rollout reward even when naive cross-region initialization does not
> outperform local scratch adaptation.

## Innovation

The current innovations that remain defensible are:

- A real-environment GeoJEPA-MPC pipeline for block-level farmland layout
  optimization.
- Executable action masking for real swap feasibility.
- Value-head candidate filtering that separates candidate selection from final
  MPC rollout scoring.
- Monitorable real-environment return-label generation.
- Cross-region action-space adaptation with compatible checkpoint loading.
- A negative-transfer stress test showing that planner calibration and label
  target selection dominate naive initialization reuse.

## Recommended Manuscript Framing

Use this structure:

1. Bishan main experiment: show the core GeoJEPA-MPC/value-label result.
2. Dongxing external-region stress test: show that the same pipeline runs on a
   second real county-level environment.
3. Planner calibration: show that Dongxing requires `candidate-value-weight=1.0`.
4. Label scaling: show pairwise -> 20x16 return -> 50x16 return improves
   rollout reward.
5. Transfer limitation: state that scratch remains stronger than current
   Bishan-initialized transfer on Dongxing primary reward.

## Low-Label-Budget Update

The low-label-budget transfer test has now been run with the existing 50x16
label file. See
`e0_dongxing_low_label_budget_family_2026-06-10.md`.

The family-level result is mixed rather than a clean transfer win:

- scratch is higher at 5 labels;
- scratch is higher at 10 labels;
- transfer is higher at 20 labels;
- transfer consistently gives stronger slope reduction;
- scratch consistently gives stronger contiguity and baimu-area gains.

This reinforces the main synthesis: Dongxing is a useful external-region stress
test and calibration study, but the current evidence still rules out a broad
"transfer wins" claim.
