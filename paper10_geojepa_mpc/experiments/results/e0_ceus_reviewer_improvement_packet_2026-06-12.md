# Paper10 CEUS Reviewer Improvement Packet

Date: 2026-06-12

This packet records the CEUS-facing revision route for Paper10 after the
pre-submission reviewer audit. It is not a final response letter, not a final
manuscript, and not a data-rights decision. It is a control file for converting
the current integrated scaffold into a CEUS Research Article candidate while
keeping the evidence boundary explicit.

Current source controls:

- `e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md`
- `e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md`
- `e0_integrated_figure_table_numbering_freeze_2026-06-11.md`
- `e0_source_data_map_with_dongxing_2026-06-11.md`
- `e0_submission_blocker_decision_packet_2026-06-11.md`
- `e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md`
- `e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md`
- `DATA_AVAILABILITY.md`
- `REPRODUCIBILITY.md`

## Scope Decision

Target route for the next conversion pass: CEUS Research Article candidate.

Paper9 has not been formally submitted. Public Paper10 manuscript text must
therefore use the self-contained Paper10 Methods route instead of relying on
`zhou2026paper9_local` as a public source. Paper9 can remain an internal
provenance note until it has a public preprint, article, or supplement.

## One-Sentence Argument

In constrained farmland layout planning, Paper10 shows that monitor-gated
GeoJEPA-MPC value filtering improves the Bishan 20x16/top5 real-environment
rollout and can be calibrated in a Dongxing/Neijiang external-region stress
test, supported by tracked source data and local full-data routes, with the
boundary that direct 50-state Bishan scale-up and robust Bishan-to-Dongxing
transfer superiority are not supported.

## D:\test Data Discovery

The current Git checkout intentionally includes smoke data and generated result
artifacts, not the full raw/prepared geospatial payloads. A targeted scan of
`D:\test` found the following local-only assets that can support reruns or
archive planning. These paths are local evidence locations, not public
submission links and not permission to redistribute the files.

| data family | found local path | size or count | role in Paper10 |
|---|---|---:|---|
| Full Bishan transitions | `D:\test\tool2\transitions.npz` | 1,522,832,889 bytes | Full Bishan value-head training and rollout reruns beyond smoke verification. |
| Full Bishan pairwise data | `D:\test\tool2\pairwise.npz` | 127,198,041 bytes | Full checkpoint scoring and value-head training metadata. |
| Bishan GPKG root | `D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg` | 160,534,528 bytes | GPKG-root real-environment reproduction route. |
| Bishan township file | `D:\test\townships.json` | 407 bytes | Prepared full-data route input. |
| Bishan shapefile root | `D:\test\bishan.shp` | 109,517,752 bytes | Alternative upstream geospatial source; rights route unresolved. |
| Dongxing shapefile root | `D:\test\dongxing.shp` | 128,938,056 bytes | External-region upstream source; rights route unresolved. |
| Bishan block products | `D:\test\results_real\blocks` | 62 files recursively | Prepared block inputs for full real-environment rollouts. |
| Neijiang environment wrapper | `D:\test\neijiang_cross_region\county_env_neijiang.py` | 3,032 bytes | External-region environment route used by Dongxing/Neijiang experiments. |
| Neijiang trajectories | `D:\test\neijiang_cross_region\trajectories_6k_neijiang.npz` | 2,207,721,783 bytes | External-region training/label evidence; too large for Git. |
| Neijiang pairwise data | `D:\test\neijiang_cross_region\pairwise_data_neijiang.npz` | 184,237,773 bytes | External-region pairwise training evidence. |
| Neijiang block products | `D:\test\neijiang_cross_region\blocks` | 88 files recursively | External-region prepared block inputs. |
| Dongxing reviewer outputs | `reviewer_outputs\dongxing_value_labels` | 37 JSON, 28 log, 13 PT, 5 NPZ files | Ignored local outputs underlying tracked Dongxing summaries and figures. |

The repository still lacks full root-level `tool2/`, full
`dem_slope_analysis/output/DLTB_with_slope.gpkg`, and full `results_real/blocks`
payloads by design. The checkout contains only `results_real/blocks/README.md`
and the small smoke Tool2 route. Do not copy the full files into Git; use them
for local reruns or deposit them through the chosen public or controlled data
route after rights are confirmed.

## CEUS Reviewer Concern Matrix

| CEUS-style concern | Required manuscript action | Experiment or data action | Current status |
|---|---|---|---|
| Grid or block simplification versus irregular cadastral parcels. | Add a Methods/Discussion boundary: current swaps are block-level/equal-unit abstractions; irregular parcel deployment needs area-tolerance matching and parcel geometry features. | No new full experiment required for this revision pass. The local Bishan and Dongxing shapefile/GPKG roots found above support future parcel-geometry audits if rights allow. | Add to integrated scaffold and final CEUS conversion checklist. |
| Queen-contiguity definition may not reflect engineering adjacency on irregular parcels. | State that queen contiguity is the current computational abstraction; irregular parcel deployment should use shared-perimeter-weighted contiguity and shape compactness. | Optional future experiment: compare queen adjacency versus shared perimeter length on `D:\test\bishan.shp` and `D:\test\dongxing.shp` after defining reproducible geometry rules. | Do not claim a perimeter-weighted implementation exists. |
| Soft training and hard inference may look inconsistent. | Explain the design as soft training and hard inference: reward/count penalties shape rankings, while executable masks and paired inference enforce feasibility at deployment. | No new experiment required; existing monitor gates and executable-mask rollouts support the boundary. | Add Constrained MDP discussion without claiming CPO/RCPO was implemented. |
| Sensitivity and planning-support controllability. | Treat `candidate-value-weight` as a planner calibration parameter and discuss safe post-training controls for a planning support system. | Dongxing planner sweep already supports `candidate-value-weight=1.0` versus the Bishan default `0.1`; use it as calibration evidence. | Supported by tracked Dongxing summaries. |
| External optimizer baseline expectations. | Do not claim superiority over all planners. State that the present evidence tests value filtering and calibration, not a full optimizer benchmark suite. | A fair external optimizer baseline would need a separate predeclared protocol. Existing scripts in `D:\test` are not yet a validated Paper10 baseline. | Keep as a future-review risk, not a current claim. |
| Paper9 source status. | Keep Paper10 public Methods self-contained. | None. | Paper9 has not been formally submitted; no public Paper9 citation route. |
| Bibliography audit. | Verify BibTeX entry types and protected capitalization before CEUS formatting. | Current Paper10 BibTeX search found no `batty2013new` key in the verified/local Paper10 bibliography; keep the audit as a final-formatting check. | No Batty-entry correction needed in the current Paper10 bibliography. |

## Manuscript Insertions To Carry Forward

Add the following CEUS-facing hooks during manuscript conversion:

1. Methods task formulation: define the current planning unit abstraction and
   explicitly distinguish block-level swaps from arbitrary cadastral parcel
   exchange.
2. Methods topology definition: state that current contiguity uses queen
   adjacency and that shared-perimeter-weighted contiguity is the required
   irregular-parcel extension.
3. Methods inference route: state that the implementation uses soft training
   and hard inference rather than a full Constrained MDP, CPO, or RCPO solver.
4. Results/Discussion planning-support route: use the Dongxing
   `candidate-value-weight=1.0` sweep as evidence that deployment requires
   local planner calibration.
5. Discussion limitation: keep the two-region, descriptive-only boundary and
   say that broader transfer claims require additional external regions and a
   predefined comparison protocol.
6. Data Availability: map full Bishan, GPKG-root, and Dongxing/Neijiang data
   to public or controlled routes before submission.

## Experiment Decision

No new full Bishan rerun was run in this pass. The missing full Bishan payloads
were found under `D:\test`, so a rerun is feasible locally, but it is not needed
to answer the current CEUS reviewer concerns. The stronger revision action is
to use the existing Bishan 20x16/top5 result, failed 50-state monitor gates,
and Dongxing/Neijiang return-label scaling as the main evidence ladder.

Do not add an external optimizer baseline inside the current manuscript unless
the author team first approves a separate protocol covering optimizer choices,
equal budgets, seed design, feasibility constraints, and reporting metrics.

## Claim Locks

- Do not claim robust Bishan-to-Dongxing transfer superiority.
- Do not claim direct 50-state Bishan scale-up success.
- Do not claim a shared-perimeter-weighted contiguity implementation has been
  evaluated.
- Do not claim a Constrained MDP, CPO, or RCPO baseline has been implemented.
- Do not use `statistically significant`, p-values, or confidence intervals
  unless a formal statistical-analysis plan and outputs are added.

## Chinese Author Notes

- CEUS 路线可以继续推进，但 public manuscript 必须自包含，不能依赖尚未正式投稿的 Paper9。
- `D:\test` 下已经找到了 full Bishan、GPKG、Neijiang/Dongxing 的关键本地数据；这些只能作为本地复现实验和归档规划证据，不能直接写成公开下载链接。
- 当前不建议临时加入外部优化器 baseline；这会引入新的公平性和计算预算问题，反而拖慢 CEUS 投稿。先把现有证据写稳。
