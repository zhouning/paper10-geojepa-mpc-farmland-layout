# Paper10 Design Spec: GeoJEPA-MPC for Farmland Layout Optimization

**Date:** 2026-06-07  
**Working title:** JEPA-Regularized Geospatial World Models for Constrained Farmland Layout Planning  
**Status:** design draft for review  
**Primary predecessor:** Paper9 contrastive world-model MPC  
**Secondary predecessors:** Paper8 GeoFM latent world model, Paper7 learned environment with GeoFM ablation

## 1. One-Sentence Argument

In county-scale farmland consolidation, we test whether a JEPA-regularized geospatial latent world model can augment the Paper9 ranking-aware MPC planner with remote-sensing or GeoFM-derived representations, supported by action-ranking diagnostics, MPC planning outcomes, ablations, and cross-region stress tests, while keeping cadastral feasibility and cultivated-land balance as symbolic hard constraints.

The claim is deliberately bounded. Paper10 should not claim that LeWM directly solves farmland layout optimization. The paper should claim that stable latent world-model training can be made useful for constrained cadastral planning only when it is coupled to action-ranking supervision and a hard-constrained MPC loop.

## 2. Positioning Against Existing Papers

| Paper | Core contribution | Boundary | Paper10 relationship |
|---|---|---|---|
| Paper8 | Frozen GeoFM embedding dynamics for LULC prediction; downstream feature-dropout RL probe | Planning result is auxiliary and still feature-dominated | Reuses GeoFM latent-state idea and the caution that embeddings alone are insufficient |
| Paper9 | Contrastive reward-head training fixes action-ranking failure; MPC solves county-scale farmland planning | Uses engineered block features, not learned visual/geospatial state encoders | Supplies the planning engine, pairwise ranking protocol, baselines, and operational verification |
| Paper7 | Learned environment for policy training; causal reward calibration; GeoFM improves validation loss but hurts policy quality | Optimizes policies in learned env, not test-time MPC | Supplies the negative control: better one-step prediction does not imply better planning |
| Paper10 | JEPA/SIGReg-style geospatial latent model plus Paper9 ranking-aware MPC | Tests utility under planning metrics, not just prediction metrics | New paper, not a merge |

## 3. Research Questions

1. Can SIGReg or JEPA-style latent regularization stabilize a county-scale transition model without damaging within-state action ranking?
2. Do GeoFM or raster-derived latents add planning value beyond Paper9's 17 engineered block features?
3. Under what data regimes are geospatial latents useful: full cadastral features, partial features, feature-scarce transfer, or synthetic landscapes?
4. Does action-ranking supervision remain necessary when the state encoder becomes richer?
5. Can a latent-enhanced planner preserve Paper9's operational checks: action masks, paired swaps, cadastral output, and independent GIS recomputation?

## 4. Recommended Design

Use a staged, low-risk extension of Paper9 rather than a full raw-pixel replacement.

### Stage A: Feature-Latent Control

Start with Paper9's existing state:

- per-block features: 17 dimensions
- global features: 12 dimensions or current Paper9 variant
- action: selected block id
- pairwise data: states x sampled valid actions x true rewards

Replace the direct transition context with a latent bottleneck:

```text
block/global state -> encoder -> z_t
(z_t, action embedding) -> predictor -> z_{t+1}, reward, optional decoded deltas
loss = transition/reward MSE + lambda_rank * pairwise_rank + lambda_sig * SIGReg(z_t)
```

This stage asks whether SIGReg is compatible with Paper9's strongest insight: planning depends on action ranking, not aggregate prediction fidelity.

### Stage B: GeoFM-Augmented Latent

Add block-level GeoFM features as an optional channel:

```text
block input = [17 engineered features || 64 AlphaEarth block embedding]
```

Use gated fusion rather than naive concatenation:

```text
h_block = gate * h_engineered + (1 - gate) * h_geofm
```

Also train with feature-channel dropout:

- `p=0.0`: full engineered features
- `p=0.3`: partial feature dropout, aligned with Paper8's moderate-dropout evidence
- `p=1.0`: GeoFM-only stress test

This directly tests the Paper7/Paper8 tension: GeoFM may improve representation or prediction metrics, but may still be insufficient or harmful for planning unless the fusion is constrained.

### Stage C: Raster/Parcel-Aware Latent

Only after Stage A/B pass, add a raster or graph-raster encoder:

- land-use state raster
- DEM/slope raster
- roads/water/construction-land barriers
- township boundary and block id masks
- optional AlphaEarth embedding grid

The raster encoder should not own feasibility. It supplies latent context; the existing CountyLevelEnv still owns legal actions, paired swaps, and metric computation.

## 5. System Architecture

Paper10 should introduce `GeoJEPA-MPC` as four modules.

### Module 1: Representation Builder

Inputs:

- prepared Paper9 block features
- optional AlphaEarth/GeoFM block embeddings
- optional raster tensors generated from DLTB, DEM, and barriers

Outputs:

- `state_features.npz`: Paper9-compatible engineered features
- `geofm_block_features.npz`: optional `(n_blocks, 64)` block embeddings
- `raster_context.npz`: optional spatial tensors for Stage C
- metadata with projection, year, embedding source, block alignment checks

### Module 2: JEPA-Regularized Transition Model

Minimum architecture:

```text
Block encoder: shared MLP over block features
GeoFM encoder: shared MLP or frozen projection over 64-d embeddings
Global encoder: MLP over global features
State aggregator: mean/attention pooling into z_t
Action embedding: selected block id + selected block representation
Predictor: action-conditioned MLP/Transformer over z_t
Heads: next global delta, selected-block delta, reward, optional decoder
```

Loss:

```text
L = L_state_mse
  + 0.1 * L_reward_mse
  + lambda_rank * L_pairwise_rank
  + lambda_sig * SIGReg(z_t)
  + optional L_probe for metric-aligned latent channels
```

Important: the ranking term stays on the model side, following Paper9. SIGReg is an anti-collapse regularizer, not a substitute for ranking supervision.

### Module 3: Masked Categorical MPC

Reuse Paper9 Tool 4 semantics:

1. enumerate or sample valid blocks from `env.action_masks()`
2. score every valid one-step candidate with the learned model
3. keep top-K candidates
4. roll out horizon `H=5` in model space
5. execute only the selected first action in the real CountyLevelEnv
6. update true state and replan

Do not use LeWM's continuous CEM unchanged. Farmland planning is a masked high-branching categorical problem, not continuous robot control.

### Module 4: GIS Verification

Keep Paper9's independent verification requirement:

- output optimized DLTB/shapefile
- recompute slope, contiguity, and baimu-fang from geometry
- verify farm-to-forest and forest-to-farm swap counts match
- report any constraint violations as failures, not warnings

## 6. Experiment Plan

### Experiment 0: Compatibility Smoke Test

Purpose: ensure the new model can read existing Paper9 Tool 2 data and drive Tool 4 without GeoFM.

Configs:

- Paper9 transition model baseline
- latent bottleneck, no SIGReg, no ranking
- latent bottleneck + ranking
- latent bottleneck + ranking + SIGReg

Primary metrics:

- pairwise ranking accuracy
- top-K regret
- Spearman or Kendall over sampled actions
- MPC slope/contiguity/baimu outcomes on Bishan smoke subset
- runtime and memory

Gate to continue: the best latent model must not catastrophically degrade action ranking or MPC outcome relative to Paper9 baseline. It does not need to beat Paper9 yet.

### Experiment 1: GeoFM Fusion

Purpose: test whether static GeoFM embeddings help planning after gated fusion and ranking supervision.

Configs:

- engineered only
- GeoFM only
- engineered + GeoFM concat
- engineered + GeoFM gated fusion
- gated fusion + feature dropout

Primary comparison:

- Does GeoFM improve ranking accuracy?
- Does it improve MPC outcome?
- Does it improve transfer or feature-scarce robustness?
- Does it repeat Paper7's failure mode: lower validation loss but worse planning?

### Experiment 2: Ranking Necessity

Purpose: test whether richer latents remove the Paper9 ranking bottleneck.

Configs:

- MSE only
- MSE + SIGReg
- MSE + ranking
- MSE + ranking + SIGReg
- MSE + ranking + SIGReg + GeoFM

Expected safe claim:

If ranking remains necessary, Paper10 strengthens Paper9: representation quality is not enough. If SIGReg/GeoFM reduces the ranking gap, the paper gets a stronger positive mechanism.

### Experiment 3: Cross-Region and Synthetic Generalization

Datasets:

- Bishan real county
- Neijiang Dongxing real county
- Paper9 seven synthetic landscape presets
- optional public restoration case only as a negative cross-domain comparator

Protocols:

- train from scratch per region
- Bishan to Neijiang partial transfer
- limited-pairwise fine-tune: 10%, 25%, 50%, 100% pairwise data
- feature-scarce transfer: engineered dropout at evaluation

Primary question:

Does geospatial latent information reduce the amount of local pairwise data needed, or does it only add prediction noise?

### Experiment 4: Raster/Parcel-Aware Extension

Run only if Stage A/B justify it.

Configs:

- block-feature model
- block + GeoFM model
- raster context + block features
- raster context + GeoFM + block features

Primary question:

Does spatial texture or neighborhood context improve candidate ranking beyond engineered adjacency/compactness features?

## 7. Success Criteria

Paper10 can be successful in three different ways.

### Strong Positive Result

GeoJEPA-MPC improves Paper9 on transfer, feature-scarce deployment, or cross-region sample efficiency while matching the main Bishan planning result.

### Mechanistic Result

SIGReg improves latent stability or calibration, but ranking supervision remains the decisive ingredient. This is still publishable if diagnostics are clear.

### Negative-but-Useful Result

GeoFM or raster latents improve prediction metrics but not planning. This is publishable if framed as an evidence-based warning: geospatial foundation representations need action-ranking alignment before they can support constrained land-use optimization.

The paper should not require beating Paper9's headline Bishan number to be worthwhile.

## 8. Figure and Table Plan

Figures:

1. Concept map: LeWM idea + Paper8 GeoFM latent + Paper9 ranking-aware MPC -> Paper10 GeoJEPA-MPC.
2. Architecture: representation builder, latent model, rank loss, masked MPC, GIS verification.
3. Ranking diagnostics: pairwise accuracy, top-K regret, rank correlation across configs.
4. Planning outcomes: slope, contiguity, baimu count/area for Paper9 vs latent variants.
5. GeoFM paradox: prediction loss vs planning quality, explicitly testing Paper7's warning.
6. Transfer/data-scarcity: local pairwise data fraction vs performance.

Tables:

1. Method comparison table.
2. Ablation table for SIGReg, ranking, GeoFM, gated fusion.
3. Cross-region transfer table.
4. Runtime and memory table.
5. Constraint-verification table.

## 9. Manuscript Structure

1. Introduction
   - County-scale farmland planning needs constrained action ranking, not just prediction.
   - Paper9 showed ranking-aware MPC works with engineered features.
   - JEPA/GeoFM world models raise the question of whether learned geospatial latents can reduce feature dependence.

2. Related Work
   - JEPA and latent world models
   - GeoFM and geospatial representation learning
   - Model-based RL/MPC for planning
   - Land-use and farmland consolidation optimization

3. Problem Setting
   - same county-scale MDP as Paper9
   - action masks, paired swaps, metrics, hard constraints

4. GeoJEPA-MPC Method
   - representation builder
   - latent transition model
   - SIGReg and ranking loss
   - masked categorical MPC
   - GIS verification

5. Experiments
   - compatibility and ablation
   - GeoFM fusion
   - ranking necessity
   - cross-region and synthetic tests
   - optional raster extension

6. Discussion
   - when latent geospatial representations help
   - why prediction accuracy may decouple from planning utility
   - why constraints must remain symbolic
   - deployment and data-governance boundaries

7. Conclusion
   - bounded claim about representation-aware, ranking-aligned world models for constrained spatial planning

## 10. Implementation Strategy

Keep changes isolated from production Paper9.

Recommended new branch/directory:

```text
paper10_geojepa_mpc/
  README.md
  models/
    geojepa_transition_model.py
    sigreg.py
    fusion.py
  training/
    train_geojepa_ensemble.py
    eval_ranking.py
  data/
    build_geofm_block_features.py
    build_raster_context.py
  planning/
    geojepa_ensemble_runner.py
    mpc_plan_geojepa.py
  experiments/
    configs/
    run_e0_smoke.py
    run_e1_geofm_fusion.py
    run_e2_ranking_ablation.py
    run_e3_transfer.py
  manuscript/
    paper10_geojepa_mpc.tex
```

Reuse from Paper9:

- Tool 1 prepared data schema
- Tool 2 transition and pairwise sampling
- Tool 4 MPC loop semantics
- verification scripts
- synthetic benchmark

New code should be additive. Do not modify Paper9 production toolbox until Paper10 evidence justifies backporting.

## 11. Needed User Cooperation

Experiments that may require your help:

1. AlphaEarth or other GeoFM block embeddings for Bishan and Neijiang, if not already cached.
2. Confirmation of which county datasets can be used for Paper10 beyond Bishan and Neijiang.
3. Long-running CPU/GPU runs after the smoke tests pass.
4. Decision on target journal after the first ablation results: methods-oriented vs application-oriented framing.

## 12. Review Risks and Mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| "This is just Paper9 with more features" | Novelty risk | Make the claim about representation-learning plus ranking alignment, not simple feature concatenation |
| GeoFM hurts planning again | Likely given Paper7 | Treat as a central test, not an embarrassment; use gated fusion/dropout and report negative evidence honestly |
| SIGReg improves latent distribution but not planning | Possible | Report ranking and MPC metrics as primary; keep latent diagnostics secondary |
| Hard constraints are not learned | Reviewers may ask why not end-to-end | State that cadastral legality and cultivated-land balance are symbolic constraints by design |
| Full raster model is expensive | Scope creep | Stage C is optional and gated by Stage A/B results |
| Raw cadastral data cannot be shared | Reproducibility risk | Use Paper9 synthetic benchmark and aggregate/pairwise derivatives |

## 13. Immediate Next Step

Before coding, run a local asset audit:

1. locate existing Tool 2 transition and pairwise `.npz` files
2. locate any cached GeoFM/AlphaEarth block embeddings
3. confirm Paper9 baseline scripts can run on a small smoke subset
4. define Experiment 0 configs and expected outputs

After that audit, create an implementation plan with exact files, commands, smoke tests, and experiment checkpoints.

## 14. Asset Audit Completed on 2026-06-07

Local reusable assets found:

### 14.1 Smoke-Scale Paper9 Dataset

Path: `D:\test\arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared`

- `tool2\transitions.npz`
  - `block_features`: `(500, 30, 17)`, float32
  - `global_features`: `(500, 12)`, float32
  - `actions`: `(500,)`, int64
  - `rewards`: `(500,)`, float32
  - `next_block_features`: `(500, 30, 17)`, float32
  - `next_global_features`: `(500, 12)`, float32
- `tool2\pairwise.npz`
  - `states_bf`: `(100, 30, 17)`, float32
  - `states_gf`: `(100, 12)`, float32
  - `actions`: `(100, 10)`, int64
  - `rewards`: `(100, 10)`, float32
- `tool3\train_summary.json`
  - 3 ONNX members already trained
  - final ranking accuracy: `1.0`, `0.8095`, `0.9474`
  - training time: about 1.7 s per member

Use this for Experiment 0 code-path validation only. It is too small for manuscript-level claims.

### 14.2 Full Bishan Paper9 Dataset

Path: `D:\test\tool2`

- `transitions.npz`
  - `block_features`: `(6000, 2600, 17)`, float32
  - `global_features`: `(6000, 12)`, float32
  - `actions`: `(6000,)`, int64
  - `rewards`: `(6000,)`, float32
  - `next_block_features`: `(6000, 2600, 17)`, float32
  - `next_global_features`: `(6000, 12)`, float32
- `pairwise.npz`
  - `states_bf`: `(1000, 2600, 17)`, float32
  - `states_gf`: `(1000, 12)`, float32
  - `actions`: `(1000, 50)`, int64
  - `rewards`: `(1000, 50)`, float32
- `sample_transitions_summary.json`
  - 6,000 transitions
  - 1,000 pairwise states x 50 actions
  - median pairwise reward std: `0.6855`
- `D:\test\tool3\train_summary.json`
  - Paper9 baseline ensemble already trained
  - final ranking accuracy: `0.8986`, `0.9308`, `0.8826`
  - training time: about 1,940-1,980 s per member

Use this as the main Experiment 0 full-scale benchmark and as the first manuscript-grade baseline.

### 14.3 Existing GeoFM Embeddings

Path: `D:\test\paper7\data`

- `block_geofm_embeddings.npy`: `(2600, 64)`, float32
- `geofm_metadata.json`
  - `n_blocks`: 2600
  - `embedding_dim`: 64
  - `year`: 2020
  - source: AlphaEarth `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`
  - method: centroid point sampling

These embeddings align with full Bishan scale, not the 30-block smoke subset. Experiment 1 should therefore start from full Bishan or create a smoke-subset embedding slice with explicit block-id alignment.

### 14.4 Paper7 GeoFM Negative Control

Path: `D:\test\CEUS_submission_paper7\08_supplementary_optional\result_summaries\e4_geofm_results.json`

- no GeoFM: transition validation loss `0.085084`; policy slope results `-0.818`, `-1.107`
- with GeoFM: validation loss `0.050763`; slope results about `-0.692`, `-0.714`

Use this as a pre-registered risk: lower transition loss is not enough. Paper10 metrics must prioritize ranking and MPC outcomes.
