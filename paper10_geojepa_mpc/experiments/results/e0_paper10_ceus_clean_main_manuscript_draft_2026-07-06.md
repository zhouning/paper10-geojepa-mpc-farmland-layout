# Paper10 CEUS clean main manuscript draft

Date: 2026-07-06

Status: clean CEUS main-manuscript draft, updated by the 2026-07-09 CEUS policy verification for bounded formal submission. This file removes author handoff notes, source-control lists, terminology ledgers, claim-lock tables and unresolved-blocker tables from the manuscript body. It does not add a new experiment, and it keeps the bounded claim boundary while treating remaining author names, affiliations, CRediT roles, declarations, funding and upload steps as submission-system fields rather than algorithm, experiment, archive or artwork blockers.

Source assembly: `e0_paper10_ceus_baseline_hardened_manuscript_assembly_draft_2026-07-06.md`.

## Title page

Title: Monitor-gated value labels for evidence-controlled GeoJEPA-MPC farmland layout planning

Article type: Research Article candidate for Computers, Environment and Urban Systems.

Authors, affiliations and corresponding author: pending author decision.

Short title: Monitor-gated GeoJEPA-MPC for farmland planning

## Highlights

Submit `e0_paper10_ceus_highlights_2026-07-06.txt` as the separate editable highlights file.

- Monitor gates control value-label escalation for farmland layout planning.
- Bishan 20x16/top5 gives a descriptive matched 5-seed reward anchor.
- Value filtering wins 3/5 seeds, so superiority remains descriptive.
- Executable masks prevent invalid zero-swap rollout behavior.
- Stage 3 and Dongxing tests define scale and calibration boundaries.

## Abstract

Constrained farmland layout planning requires sequential spatial decisions for which local feasibility and finite-horizon value can diverge. We present a monitor-gated GeoJEPA-MPC workflow that generates finite-horizon value labels, screens label quality before value-head training and enforces executable actions during rollout. In Bishan, the 20x16/top5 value filter was evaluated against the matched `rank_seed2028` comparator under the same H=5, K=50 and executable-mask protocol. Across seeds 0-4, mean 100-step reward was 69.4705 for the value-filter policy and 67.5437 for the comparator, with sample standard deviation 1.0004 versus 7.2246. The seed-wise outcome was mixed: value filtering won 3/5 seeds and lost seeds 0 and 4, so the result is reported descriptively. Removing the executable mask reduced mean reward to 40.3515 and produced 100 zero-swap steps and 98 negative zero-swap steps, identifying executable masking as necessary for valid rollout behavior under the current protocol. An ungated top-4 control did not separate from the gated anchor, so the monitor gate is framed as label-quality evidence control rather than a separately proven online reward-gain mechanism. Stage 3 50-state rows, a 50x24 candidate-score sweep and Dongxing/Neijiang stress tests further bound the claim to calibrated planning support, not broad scale-up, transfer superiority or operational cadastral deployment.

## Keywords

Farmland layout planning; land-use optimization; GeoJEPA-MPC; value labels; model-predictive planning; geospatial decision support; monitor gates.

## 1. Introduction

Farmland layout planning is a spatial optimization problem in which local land-use changes must be evaluated against slope, contiguity, parcel shape, area and administrative constraints. GIS-based land-use allocation and land consolidation systems have long treated land management as a multi-criteria planning task rather than as a purely local classification problem [@aerts2003linear_integer_land_use_allocation; @stewart2014multiobjective_gis_land_use; @demetriou2012ipdss_land_consolidation; @yao2018spatial_optimization_land_use]. Parcel exchange and parcel-shape studies further show why the geometry of planning units matters for practical land-consolidation decisions [@demetriou2013parcel_shape_index; @teijeiro2020parcel_exchange].

The difficulty for learned planning is that the value of a local swap is not fully determined by its immediate reward. A block exchange can alter later connectivity, slope reduction opportunities and area aggregation. A planner must therefore evaluate finite-horizon candidate futures while respecting executable constraints. Model-predictive control provides a natural template for rolling finite-horizon decision making [@mayne2014mpc_future_promise; @rawlings2017model_predictive_control], while learned world models show how latent dynamics can support candidate rollout and search [@ha2018recurrent_world_models; @hafner2019planet].

Value functions can improve candidate selection, but value labels create a quality-control problem in geospatial planning. A larger label set is useful only if generated returns preserve meaningful candidate rankings. The resulting value filter must also remain compatible with hard feasibility masks during rollout. JEPA-style predictive representations motivate learning in an embedding space rather than reconstructing raw inputs [@assran2023ijepa]. The manuscript-facing claim in this paper is narrower: value labels for farmland planning need explicit monitoring before they are used to train a planner-facing value head.

We evaluate a monitor-gated GeoJEPA-MPC workflow for constrained farmland layout planning. The workflow generates finite-horizon return labels for candidate block actions, applies monitor gates to check candidate regret, candidate overlap and one-step reward alignment, trains a value filter only for accepted label sets, and enforces feasibility with executable masks and paired inference during rollout. This is a soft training and hard inference design. Reward and count penalties shape rankings during training, while hard masks and deterministic paired swaps enforce executable actions.

The evidence ladder is deliberately bounded. Bishan provides the primary positive result: a monitor-selected 20x16/top5 value-label setting improved descriptive mean reward and reduced seed-level reward variation under a matched protocol. Stage 3 then tested whether authorized 50-state value-label rows could support a stronger scale claim. They completed value-filter rollouts but remained below the matched comparator. Dongxing/Neijiang provides second-region calibration and stress-test evidence, but mixed transfer-versus-scratch outcomes prevent a transfer-superiority claim.

## 2. Materials and methods

### 2.1 Task formulation and planning units

We model farmland layout planning as a finite-horizon sequential swap task over spatial blocks. At each environment step, the planner selects one block. The environment then executes up to five paired farmland-forest swaps inside that block. The execution rule converts a higher-slope unswapped farmland parcel to forest and a lower-slope unswapped forest parcel to farmland when the slope condition is satisfied. The default episode budget is 500 paired swaps, giving a maximum of 100 planning steps at five swaps per action.

The implemented action is block-level rather than arbitrary parcel-level. A block action identifies where a local swap should be attempted. The environment then chooses the specific parcel pair through the deterministic greedy execution rule. This block-level planning-unit abstraction is a current evidence boundary. Deployment on irregular cadastral parcels would require area-tolerance matching between candidate exchange units, parcel geometry features and explicit shape constraints.

The environment represents topology with queen contiguity. This abstraction supports reproducible block and parcel adjacency in the current code path. It is not a final engineering definition for irregular parcel deployment. Shared-perimeter-weighted contiguity and compactness features should be added before operational parcel-exchange use is claimed.

### 2.2 State, action masks and reward

The observation concatenates a per-block feature matrix with a county-level global feature vector. Block features include normalized farmland and forest slope summaries, available farmland and forest areas, remaining swap potential, compactness, current farmland area and investment status. Global features include remaining budget fraction, global farmland slope, contiguity, step fraction, slope and contiguity changes, baimu-fang count and area summaries, investment entropy across townships and the maximum single-township investment fraction.

The base action mask keeps blocks with at least one unswapped farmland parcel and one unswapped forest parcel. Value-label generation and rollout evaluation intersect this base mask with an executable mask. For each block, the executable mask checks whether the best available farmland parcel has higher slope than the best available forest parcel under the same connectivity-adjusted scoring rule used by the environment. This prevents the planner from selecting blocks that satisfy the coarse availability mask but execute no useful paired swap.

The per-step reward combines normalized stepwise reduction in area-weighted farmland slope, normalized stepwise contiguity change, normalized stepwise change in connected baimu-fang area, a bonus for newly counted baimu-fang patches, an asymmetric penalty when baimu-fang area decreases and a penalty for zero-swap actions. Rollout total reward is the undiscounted sum of per-step rewards over the 100-step episode. Final slope change, contiguity change and baimu-area change are final-step episode metrics averaged across rollout seeds when aggregated.

### 2.3 GeoJEPA-MPC and value filtering

GeoJEPA-MPC combines a geospatial predictive representation, candidate action generation, finite-horizon rollout scoring and a learned scalar value filter. The planner samples candidate block actions under the executable mask, scores candidate futures, blends model-predictive rollout scores with value-head outputs, and selects actions for environment execution. In Bishan rollouts, the value-filter setting used `selector=value_filter`, horizon 5, global top-k 50, blend candidate scoring and candidate-value-weight 0.1. In Dongxing calibration experiments, the planner required candidate-value-weight 1.0.

The value filter is trained from generated value labels rather than from an uncontrolled collection of all candidate returns. For a selected state and candidate action set, the label generator applies each candidate action, rolls out a configured continuation policy for a finite horizon and stores both the one-step reward and the discounted multi-step return. The packaged Bishan positive labels use horizon 5 and discount factor 0.99.

### 2.4 Monitor-gated value-label selection

The monitor gate checks whether a generated label set is suitable for value-head training and manuscript-facing escalation. For each candidate top-k, the monitor reports candidate regret, candidate overlap and one-step regret. Candidate regret measures the return gap under the candidate-score top-k set. Candidate overlap measures agreement with the return-ranked top-k set. One-step regret checks whether multi-step returns retain information beyond immediate reward.

Training proceeds only for label sets that pass the monitor gate. This design treats failed labels as diagnostic evidence rather than silently converting them into model checkpoints. The Stage 3 protocol applied this rule to authorized 50-state rows and then compared the resulting rollouts with a matched comparator under the same rollout settings.

### 2.5 Bishan and Stage 3 protocol

Bishan is the primary validation environment for the current draft. The paper-facing route uses the GPKG-root prepared-data convention that resolves `dem_slope_analysis/output/DLTB_with_slope.gpkg`, because the local reproduction audit matched the packaged 20x16/horizon-5 seed44 label arrays under that root. Full reruns require the external full Bishan Tool2 transition and pairwise data plus prepared geospatial inputs. The Git repository includes smoke data, generated value labels, monitor outputs, checkpoints, rollout summaries and figure-ready source data.

The original Bishan evidence compared a 10-state, 12-candidate, horizon-5 pilot with a 20-state, 16-candidate, horizon-5 scale-up. Stage 3 then trained and rolled out only the two Stage 1 pass rows: `frontier_random050_50x16_h5_seed48_f050` with top-k 6 and `frontier_random050_50x24_h5_seed47_f075` with top-k 12. A near-pass 50x24/top12 seed48 row was reported only as `diagnostic_near_pass`. All Stage 3 rollouts used five seeds, 100 steps, horizon 5, global top-k 50, executable masks, blend candidate scoring and candidate-value-weight 0.1. The later 2026-06-20 candidate-score sweep on `frontier_random050_50x24_h5_seed48_f075` tested blend weights 0.05, 0.10, 0.15, 0.25 and pure `value` filtering.

### 2.6 Dongxing/Neijiang protocol

Dongxing/Neijiang is used as an external-region calibration and transfer stress test. The environment loaded 3711 blocks from 76,376 parcel assignments. Bishan checkpoints could initialize compatible Dongxing model tensors while reinitializing action-space-specific embeddings. The experiments compared pairwise-only training with real-environment return-label scaling at 20x16 and 50x16. They also tested low-label budgets of 5, 10 and 20 states.

The Dongxing design is not a pure transfer-superiority benchmark. It is a stress test of whether the workflow can run in a second real environment, whether local return labels improve planning, and whether Bishan initialization is useful under constrained label budgets. The current evidence shows that return-label scaling helps both transfer and scratch families, while low-label and 50x16 comparisons remain mixed between transfer and scratch.

### 2.7 Evaluation and reporting policy

The primary reported outcome is 100-step rollout total reward. Secondary reported outcomes are final slope change, final contiguity change and final baimu-area change. Bishan rows are reported over five rollout seeds. Dongxing family rows aggregate three initialization checkpoints and five rollout seeds per checkpoint. All current results are descriptive: means, sample standard deviations, minima, maxima and condition-specific comparisons are reported without hypothesis-test wording.

## 3. Results

### 3.1 Monitor gates selected the Bishan value-label targets

The monitor gate selected trainable Bishan value-label targets before value-head training. The 10x12/horizon-5 seed43 pilot selected top-4, with candidate regret 0.4923, candidate overlap 0.5000 and one-step regret 1.2916. The 20x16/horizon-5 seed44 row selected top-5, with candidate regret 0.1877, candidate overlap 0.6300 and one-step regret 2.4626. These diagnostics supported using the 20x16/top5 labels for the primary Bishan value-filter test.

### 3.2 Bishan 20x16/top5 produced a descriptive matched 5-seed reward anchor

The baseline-hardened Bishan 20x16/top5 comparison is the strongest performance evidence. Across locked seeds 0-4, value-filter mean reward was 69.4705 compared with 67.5437 for the matched `rank_seed2028` comparator. Sample standard deviation was lower for the value-filter policy, 1.0004 versus 7.2246. The paired mean delta was 1.9269 reward units.

The seed-level outcome was mixed. Paired reward deltas were -3.2408, 3.6137, 8.4242, 9.0620 and -8.2248 for seeds 0-4. The value filter therefore won 3/5 seeds and lost seeds 0 and 4. The diagnostic-only two-sided sign-test readout was 1.0000. This pattern supports a descriptive mean reward and lower-variation statement under the tested protocol. It does not support a claim that the value filter improved every seed or established inferential superiority.

Secondary metrics were also mixed. Relative to the matched comparator, mean slope-change difference was 0.0138 and mean baimu-area-change difference was 4.5905 ha, while mean contiguity-change difference was -0.0003. The safest interpretation is reward-centered: the value-filter anchor improved mean reward and reduced reward variation under the implemented reward definition, while final planning indicators did not all move in the same favorable direction.

### 3.3 Stage 3 defined the 50-state boundary

Stage 3 trained and rolled out only the authorized Bishan rows from the validation pass. The confirmatory 50-state row `frontier_random050_50x16_h5_seed48_f050` selected top-k 6 and reached 64.2960 mean reward, 3.2477 below the matched comparator. The confirmatory row `frontier_random050_50x24_h5_seed47_f075` selected top-k 12 and reached 66.2544 mean reward, 1.2893 below the matched comparator. These rows completed value-filter rollout but did not improve on the comparator.

A later candidate-score sweep on `frontier_random050_50x24_h5_seed48_f075` varied `candidate-score-mode` across blend weights 0.05, 0.10, 0.15 and 0.25, plus pure `value` filtering. `blend0.10` remained the best candidate-filter variant at 67.4913 mean reward, but it still remained below the matched comparator. Pure `value` filtering was materially worse. Candidate-score tuning therefore reinforced the boundary interpretation rather than changing the claim.

### 3.4 Diagnostic near-pass evidence remained separate

The `diagnostic_near_pass` row `frontier_random050_50x24_h5_seed48_f075` selected top-k 12 and reached 67.4913 mean reward, 0.0524 below the matched comparator. This row is useful because it shows a near-baseline failure mode under the same rollout settings. It must not be pooled with the confirmatory rows or used to imply that Stage 3 established a broader 50-state claim.

### 3.5 Mechanism ablation identified executable masks as rollout-critical

The mechanism packet compared four matched Bishan rollout conditions under the 20x16/top5 protocol. The full gated masked condition reached 69.4705 mean reward with sample standard deviation 1.0004. Removing the executable mask reduced mean reward to 40.3515 and produced 100 zero-swap steps and 98 negative-zero-swap steps. This indicates that the planner repeatedly chose blocks that did not execute useful paired swaps.

The ungated top-4 control recorded the same mean reward and sample standard deviation as the full gated masked anchor. The monitor gate should therefore be framed as upstream label-quality control and escalation filtering. The current ablation does not isolate it as an independent source of online rollout gain. Supplementary Table S3 records this four-condition packet.

### 3.6 Dongxing required planner calibration

The Dongxing/Neijiang package established that the workflow could execute in a second real county-level environment. The action space contained 3711 blocks from 76,376 parcel assignments. This required action-space adaptation when loading Bishan-initialized checkpoints. The planner did not reuse the Bishan candidate-value-weight setting unchanged. Dongxing return-label rollouts used candidate-value-weight 1.0, compared with the Bishan default 0.1, supporting the interpretation that value filtering is a calibratable component in a planning-support workflow.

### 3.7 Dongxing return labels improved transfer and scratch families

In Dongxing, real-environment return-label scaling improved both Bishan-initialized transfer and Dongxing scratch families relative to pairwise-only labels. Pairwise-only transfer reached 37.8894 mean reward, and pairwise-only scratch reached 40.2111. With 50x16 return labels, transfer increased to 51.6183 and scratch increased to 55.7324. The strongest family mean in this comparison was scratch 50x16, not transfer 50x16. The result supports local calibration and return-label scaling rather than robust transfer superiority.

### 3.8 Low-label Dongxing transfer was mixed

The Dongxing low-label stress test further bounds the transfer claim. At 5 labels, scratch had higher mean reward than transfer, 50.3654 versus 41.6380. At 10 labels, scratch again had higher mean reward, 47.7970 versus 44.3382. At 20 labels, transfer had higher mean reward than scratch, 44.7080 versus 40.4596. Transfer showed stronger slope reduction, while scratch showed stronger contiguity and baimu-area outcomes. These mixed outcomes remain visible in the manuscript package.

## 4. Discussion

The baseline-hardened evidence narrows the paper, but it makes the manuscript more defensible. The supported contribution is not broad value-filter superiority across seeds, regions or label scales. The supported contribution is an evidence-controlled workflow that records when a value-label setting is usable, when executable constraints are essential and when additional label scale does not improve the matched comparator.

The Bishan 20x16/top5 anchor combines a higher descriptive mean reward with lower seed-level reward variation. It is also bounded because the seed-level evidence is mixed. Seed0 and seed4 losses prevent a uniform seed-wise statement. The diagnostic-only sign-test readout of 1.0000 also prevents inferential wording. This framing lets reviewers see where the evidence starts and stops.

The mechanism ablation clarifies which part of the workflow is indispensable. The executable mask is necessary for valid rollout behavior under the current environment. Without it, the planner produced widespread zero-swap behavior and sharply lower reward. The monitor gate plays a different role. It controls which value labels are allowed to become manuscript-facing training evidence, but the current ablation does not isolate it as an independent online reward mechanism.

The Stage 3 results define a boundary condition. Two authorized 50-state rows completed rollout and remained below the matched comparator. The later candidate-score sweep did not change that conclusion. This shows that more labels or different candidate filtering are not automatically enough under the current state, candidate and rollout configuration.

The Dongxing/Neijiang results add external-environment relevance but not transfer superiority. The workflow executed in a second real county-level setting, and return-label scaling improved both transfer and scratch families. However, scratch remained stronger in the 50x16 family mean and at low-label budgets of 5 and 10. This pattern argues for local calibration and careful environment-specific tuning.

The current spatial abstraction remains a practical limitation for CEUS readers. The experiments operate on a block-level planning-unit abstraction with queen contiguity, not arbitrary irregular cadastral parcel exchange. Operational parcel planning would need area-tolerance matching, shared-perimeter-weighted contiguity, compactness features and explicit parcel-geometry constraints.

The soft training and hard inference design should be stated plainly. Reward and count penalties shape value labels and learned rankings, while executable masks and paired inference enforce rollout feasibility. This is a planning-support workflow using learned scores as a filtered recommendation layer. It is not evidence that the implementation is a full constrained reinforcement-learning solver.

Several limitations remain for interpretation. First, the current evidence is two-region and descriptive. Broader generalization claims require additional external regions and a predefined comparison protocol. Second, the pairwise-only baseline policy remains unresolved unless the author team explicitly accepts the matched `rank_seed2028` comparator as the route comparator. Third, original Bishan and Dongxing DLTB inputs are confidential and cannot be externally provided, so full raw-DLTB reruns remain limited to the author-controlled environment. The 2026-07-09 CEUS policy verification treats this as a required disclosure in the Data and Code Availability statement, not as a pre-submission algorithm or experiment blocker.

## 5. Conclusion

Paper10 supports monitor-gated value labels and executable masks as a bounded GeoJEPA-MPC workflow for constrained farmland layout planning. The validated Bishan 20x16/top5 policy provides a descriptive matched 5-seed reward anchor, and the mechanism packet shows that executable masks are necessary for valid rollouts. The mixed seed-wise outcome, Stage 3 boundary rows, candidate-score sweep and Dongxing/Neijiang stress tests prevent stronger claims about uniform superiority, larger-label improvement, transfer superiority or operational cadastral deployment. The CEUS manuscript should therefore present the work as a reproducible evidence-control and planning-support workflow with explicit boundaries.

## Data and Code Availability

This CEUS-facing statement is updated by `e0_paper10_ceus_submission_policy_verification_2026-07-09.md`. The reviewer-facing repository route is the author-confirmed 4open README.md direct link: `https://anonymous.4open.science/r/geojepa-mpc-farmland-layout-8552/README.md`. The current GitHub submission-preparation commit anchor is `92a10620d8832bacae4fbeda1fdb5708b265d139`. The author checked the 4open page on 2026-07-09 and reported no visible exact snapshot identifier, version identifier or commit hash; this GitHub commit is therefore a submission-preparation anchor, not proof of the exact 4open snapshot. Under the checked CEUS/Elsevier Research Data Policy Option B route, the confidential raw-DLTB limitation is disclosed in this section and does not require pre-submission editor acceptance before the manuscript can be submitted for review.

The repository package contains custom code, tests, scripts, the small reviewer smoke dataset, generated value-label files, monitor outputs, rollout summaries, figure-ready CSV source data, manuscript table source notes, saved checkpoints and metadata needed to inspect the reported Bishan 10x12/top4, Bishan 20x16/top5, Bishan Stage 3 boundary and Dongxing summary results. Code and scripts are licensed under Apache-2.0 in `LICENSE`. Generated non-DLTB JSON, Markdown, CSV, NPZ outputs, source-data tables, checkpoints and model-weight artifacts are released under CC0-1.0.

The full Bishan Tool2 transition and pairwise datasets are external to Git because they are large binary scientific data. They are treated as derived non-DLTB artifacts, but any new public deposit still requires DLTB-leakage check evidence, archive checksums and rights metadata. Full Bishan reruns also require the prepared GPKG-root geospatial inputs, block products and township inputs.

Original Bishan and Dongxing DLTB inputs are confidential and cannot be provided externally or publicly redistributed through public download, reviewer links, controlled-access credentials or informal requests. There is no request-based route for raw DLTB. This limitation is disclosed directly in the submission, while public code, smoke data, generated non-DLTB outputs, source-data tables, checkpoints and metadata support review of the reported bounded claims.

The Dongxing/Neijiang prepared data are also external to Git. The tracked repository contains derived Dongxing summary tables and figure source CSVs, but full external-region reruns require prepared block products, parcel assignments, transition trajectories, pairwise labels, environment wrapper files and slope-enriched geospatial inputs. Derived non-DLTB artifacts may be deposited under CC0-1.0 only after DLTB-leakage checks. Original Dongxing DLTB inputs remain confidential_no_external_access.

## Declaration of generative AI and AI-assisted technologies

Author decision pending. If AI-assisted language editing is disclosed for the submission route, this section should state the tool name, use purpose and author verification responsibility. It must not imply that AI generated data, references, images or unverified scientific claims.

## CRediT authorship contribution statement

Pending author decision.

## Declaration of competing interest

Pending author decision.

## Acknowledgements

Pending author decision.

## Funding

Pending author decision.

## References

Reference list source files for the clean draft are `references/paper10_verified_references_2026-06-09.bib` and `references/paper10_local_sources_2026-06-09.bib`. The journal-formatted reference list must be generated from these verified BibTeX files during final CEUS conversion.

## Figure captions

Figure 1. Monitor-gated GeoJEPA-MPC workflow for farmland layout planning. The schematic should show finite-horizon value-label generation, monitor-gate checks, value-head training, executable-mask rollout and claim-boundary recording.

Figure 2. Bishan 20x16/top5 matched 5-seed reward anchor. The figure should report the value-filter and matched comparator rewards under H=5, K=50, executable-mask and seeds 0-4, and it should show the mixed seed-wise outcome.

Figure 3. Bishan Stage 3 boundary rows and candidate-score sweep. The figure should show that authorized 50-state rows and the later 50x24 sweep remained below the matched comparator under the reported rollout settings.

Figure 4. Dongxing/Neijiang return-label scaling. The figure should compare pairwise-only, 20x16 and 50x16 return-label families for transfer and scratch initialization.

Supplementary Figure S1. Dongxing/Neijiang low-label transfer stress test at 5, 10 and 20 labels.

## Table captions

Table 1. Bishan monitor-selected value-label gates for the 10x12/top4 and 20x16/top5 settings.

Table 2. Bishan matched 5-seed rollout comparison for the 20x16/top5 value-filter policy and the matched comparator.

Table 3. Dongxing/Neijiang return-label scaling summary for transfer and scratch families.

Supplementary Table S1. Stage 3 seed-level rollout rewards.

Supplementary Table S2. Dongxing/Neijiang low-label transfer stress-test summary.

Supplementary Table S3. Mechanism ablation and control comparison for executable masks and monitor-gate evidence control.

## Clean-draft boundary

This clean draft is suitable for formal CEUS submission as a bounded manuscript package after the author fills submission-system metadata: author list, affiliations, corresponding author, CRediT roles, competing-interest declaration, funding/acknowledgements, cover letter and final file uploads. The algorithm, experiment, archive/source-data and Main Figure 1 artwork blockers tracked in the current policy verification are closed for bounded submission.