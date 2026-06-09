# E0 citation and claim checklist

Date: 2026-06-09

This checklist prepares the next Paper10 writing step: adding citations without
weakening the current E0 evidence boundary. It does not invent references,
DOIs, or bibliography entries. It separates local evidence already packaged in
the repository from external literature that still needs to be searched and
verified.

## One-sentence argument

Paper10 can currently make a bounded E0 claim: monitor-gated
`frontier_random050` value labels improve GeoJEPA-MPC rollout stability at the
reproducible 20x16/top5 scale, while all tested 50-state label sets remain
negative diagnostics that require candidate-proposal redesign before training.

## Current reference basis

The tracked reference inventory is intentionally small:

| item | local source | current use |
|---|---|---|
| LE-WM project | `references/README.md` | Motivation and comparison point for world-model planning. |
| Local source paper candidate | `D:\test\2603.19312v3.pdf` listed in `references/README.md` | Not committed; retrieve/verify before citing. |
| Verified Paper10 citation map | `references/paper10_citation_map_2026-06-09.md` | Maps citation placeholders to verified source keys and supported wording. |
| Verified Paper10 BibTeX | `references/paper10_verified_references_2026-06-09.bib` | First tracked bibliography file for Introduction and Methods citation insertion. |
| Paper9-compatible environment | `county_env.py`, `arcgis_toolbox_paper9/private_source/` | Local method provenance; cite prior Paper9 manuscript if available. |
| Paper10 E0 experiments | `paper10_geojepa_mpc/experiments/results/` | Primary evidence for all reported results. |

Do not add a citation to the manuscript until the source has been read and the
specific claim it supports has been checked against the source.

## Introduction citation needs

| paragraph job | claim to support | citation status | needed source type |
|---|---|---|---|
| Field stake | Farmland layout planning is a constrained spatial/sequential optimization problem involving land-use, slope, continuity, and area-related objectives. | needs external citation | Land consolidation, farmland planning, spatial optimization, or geospatial land-use planning literature. |
| Field stake | Local parcel or block swaps can affect landscape-scale contiguity and suitability metrics. | needs external citation | Spatial land-use optimization or parcel-level land consolidation work. |
| Bottleneck | One-step scoring can be insufficient when long-horizon planning quality depends on future returns. | needs external citation | Model-predictive control, reinforcement learning planning, value function, or world-model planning literature. |
| Prior attempts | Learned world models can support candidate action evaluation in planning. | needs external citation | World-model planning papers; LE-WM source if verified. |
| Prior attempts | JEPA-style/self-supervised predictive representations are relevant to learned world models. | needs external citation | JEPA or self-supervised representation learning source; cite only after verifying relevance to this method. |
| Present study | This paper tests monitor-gated frontier-random labels for GeoJEPA-MPC rather than claiming general 50-state scale-up. | local evidence | Manuscript scaffold, results synthesis, monitor outputs, 50-state diagnostics. |

Recommended Introduction structure remains:

```text
field stake -> bottleneck -> prior attempts -> unresolved gap -> present study
```

The Introduction should not include the exact E0 numbers; those belong in the
abstract and Results.

## Methods citation and evidence needs

| Methods claim | local evidence | external citation need |
|---|---|---|
| The environment optimizes a constrained farmland swap task with executable block actions. | `county_env.py`; `e0_reward_and_rollout_metric_definitions_2026-06-09.md` | Prior Paper9 environment/manuscript if this environment has been previously described. |
| The reward combines slope, contiguity, baimu-fang area, baimu-fang count, and penalties. | `e0_reward_and_rollout_metric_definitions_2026-06-09.md`; `county_env.py` | Prior Paper9 or land-planning metric sources for slope/contiguity/area motivation. |
| `mask_mode=executable` restricts actions to blocks that can execute a positive greedy paired swap. | `paper10_geojepa_mpc/planning/env_masks.py`; reward/metric note | No external citation required; code-defined implementation detail. |
| `frontier_random050` combines model-scored frontier actions with random exploratory actions. | `value_label_generation.py`; Methods draft | No external citation required unless framed as exploration/reranking methodology. |
| The monitor gate uses candidate regret, candidate overlap, and one-step regret before training. | `value_label_monitor.py`; monitor JSON/Markdown outputs | No external citation required for the implemented gate; external citations useful only if positioning as validation/gating practice. |
| Value-head-only training disables transition MSE when `lambda_sig=0`. | Training metrics with `transition_loss_enabled=false`; `run_e0_value_head_train.py` | No external citation required. |
| Rollout evaluation uses 100-step seeds 0-4, executable masks, horizon 5, top-k 50, blend mode, and candidate value weight 0.1. | 10x12 and 20x16 rollout summaries; Methods draft | No external citation required. |
| GPKG root is the reproducible route for the packaged 20x16 labels. | `e0_macos_gpkg_reproduction_findings_2026-06-09.md` | No external citation required unless discussing general GIS file-format reproducibility. |

## Results claim-evidence map

| result claim | exact local evidence | manuscript status |
|---|---|---|
| 10x12/top4 is the pilot baseline. | `e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json`; `e0_frontier_random050_manuscript_tables_2026-06-09.md` | supported |
| 20x16/top5 is the main E0 result. | `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; `e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json` | supported |
| 20x16/top5 improves mean reward over 10x12/top4 by `4.2139` (`6.46%`). | `e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json`; tables doc | supported |
| 20x16/top5 reduces seed sensitivity. | Sample std `5.0037` to `1.0004`; minimum reward `57.9750` to `67.7135`; tables doc | supported |
| 20x16 labels reproduce under the GPKG data root. | `e0_macos_gpkg_reproduction_findings_2026-06-09.md` | supported |
| Tested 50-state label sets should not be trained. | macOS seed45 finding; Windows seed46 ablation finding; post-hoc top-k CSV/tables | supported |
| GeoJEPA-MPC has demonstrated 50-state value-head scale-up. | No passing 50-state gate exists. | not supported; do not claim |

## Figure and table citation hooks

| item | what it supports | citation / evidence hook |
|---|---|---|
| Figure 1 workflow schematic | Monitor-gated value-label pipeline. | Code paths in figure plan; no external citation needed except method context. |
| Figure 2 reward distribution | 10x12/top4 vs 20x16/top5 rollout stability. | Seed-wise CSV and rollout summaries. |
| Figure 3 50-state diagnostics | Failed 50-state top-k checks. | Top-k diagnostics CSV, Windows ablation findings, macOS findings. |
| Table E0-1 | Monitor-selected training gates. | Monitor JSON outputs and tables doc. |
| Table E0-2 | Five-seed rollout comparison. | Rollout summary JSON files and tables doc. |
| Table E0-S1 | GPKG reproduction audit. | macOS GPKG reproduction findings. |

## Suggested citation placeholders

Use explicit placeholders in the manuscript draft until sources are verified:

```text
[CITATION: farmland layout / land consolidation as constrained spatial planning]
[CITATION: parcel-level or block-level land-use optimization]
[CITATION: model-predictive control for long-horizon planning]
[CITATION: learned world models for planning]
[CITATION: JEPA or self-supervised predictive representation learning]
[CITATION: value functions or learned reranking for candidate action selection]
[CITATION: prior Paper9 environment or farmland reward definition]
```

Avoid vague placeholder text such as `[add refs]`; each placeholder should name
the exact claim it must support.

## Literature-search targets

The next literature pass should search for source papers in this order:

1. Prior Paper9 manuscript or internal write-up defining the Bishan environment,
   reward terms, and Paper9 baseline.
2. Land consolidation or farmland layout optimization papers that justify
   slope, contiguity, and connected-area objectives.
3. Model-predictive control and learned world-model planning papers relevant to
   candidate action evaluation.
4. JEPA/self-supervised predictive representation sources relevant to the
   GeoJEPA naming and model design.
5. Value-function or reranking literature that helps frame the value-head
   filtering contribution.

## Claims to avoid

Do not write these claims unless future evidence changes:

| prohibited claim | reason |
|---|---|
| The method scales to 50 states. | Every tested 50-state `frontier_random050` label set failed the monitor gate. |
| Failed 50-state rows were trained and performed poorly. | They were not trained because the gate failed. |
| The GPKG/shapefile discrepancy is a model effect. | The evidence identifies a data-root resolution boundary. |
| Top-k is fixed across all label sets. | The usable gate shifted from top-4 in 10x12 to top-5 in 20x16. |
| The gain is explained only by one-step reward. | The 20x16/top5 monitor retained one-step regret `2.4626`; failed post-hoc rows show the opposite case. |

## Next writing actions

1. Locate the prior Paper9 environment manuscript or method note.
2. Decide whether the target journal permits citation to the 2026 LeWM arXiv
   preprint; if not, use only the peer-reviewed JEPA/world-model sources.
3. Insert citations from `references/paper10_citation_map_2026-06-09.md` into
   the Introduction and Methods draft after each claim is
   matched to a verified source.
4. Run a separate China-specific farmland or land-consolidation literature pass
   if the Introduction needs region-specific policy context.

## Chinese author notes

- 这份清单不是参考文献表，而是“哪些句子需要找文献、哪些结果已经有本地证据”的
  对照表。
- 目前可以安全写 20x16/top5 的 paper-facing 结论；不能写 50-state 成功扩展。
- 已经新增第一版 BibTeX 和 claim-to-citation map；下一步是把这些引用插入
  Introduction/Methods，并补齐 Paper9 的正式可引用来源。
