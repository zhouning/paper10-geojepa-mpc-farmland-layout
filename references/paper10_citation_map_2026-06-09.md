# Paper10 verified citation map

Date: 2026-06-09

This note turns the E0 citation checklist into manuscript-ready reference
targets. It uses only sources that were located through public DOI, publisher,
arXiv, or conference pages for the verified bibliography. It also records a
separate local-only Paper9 source for internal drafting; this source is not a
publicly verified bibliography entry and must be replaced or formalized before
submission.

BibTeX file:

- `references/paper10_verified_references_2026-06-09.bib`
- `references/paper10_local_sources_2026-06-09.bib` for local-only Paper9
  manuscript provenance

## Citation policy for Paper10

- Cite a source only for the specific claim it supports.
- Do not cite LeWorldModel (LeWM) as established prior art without noting that it
  is a 2026 arXiv preprint; it is suitable as a direct design comparison or
  motivation source for JEPA world models.
- Do not cite any source as evidence that Paper10 scales to 50 states. The local
  E0 evidence says the opposite for tested `frontier_random050` 50-state labels.
- Use `zhou2026paper9_local` only as an internal-draft placeholder for the
  local Paper9 manuscript. Before submission, replace it with a public preprint,
  accepted article, final supplementary-methods citation, or a self-contained
  Paper10 Methods section.

## Claim-to-citation map

| manuscript placeholder | verified citation keys | supported wording |
|---|---|---|
| `[CITATION: farmland layout / land consolidation as constrained spatial planning]` | `yao2018spatial_optimization_land_use`; `demetriou2012ipdss_land_consolidation`; `demetriou2014ipdss_land_consolidation_book` | Land-use allocation and land-consolidation planning are spatially explicit planning problems that combine GIS, optimization, and multiple criteria. |
| `[CITATION: parcel-level or block-level land-use optimization]` | `aerts2003linear_integer_land_use_allocation`; `stewart2014multiobjective_gis_land_use`; `teijeiro2020parcel_exchange`; `demetriou2013parcel_shape_index` | Parcel/site allocation, parcel exchange, compactness, contiguity, and parcel shape have been modeled as spatial optimization or decision-support problems. |
| `[CITATION: model-predictive control for long-horizon planning]` | `mayne2014mpc_future_promise`; `rawlings2017model_predictive_control` | Model-predictive control repeatedly evaluates finite-horizon predictions to choose actions under constraints. |
| `[CITATION: learned world models for planning]` | `ha2018recurrent_world_models`; `hafner2019planet`; `maes2026leworldmodel` | Learned latent dynamics/world models can support planning by rolling out candidate futures in a learned representation. |
| `[CITATION: JEPA or self-supervised predictive representation learning]` | `assran2023ijepa`; `maes2026leworldmodel` | JEPA-style self-supervised learning predicts target embeddings from context embeddings rather than reconstructing pixels directly. |
| `[CITATION: value functions or learned reranking for candidate action selection]` | `sutton2018reinforcement_learning`; `mnih2015dqn`; `silver2016alphago` | Value functions/action-value functions can score candidate states or actions; policy/value networks can be combined with search. |
| `[CITATION: prior Paper9 environment or farmland reward definition]` | `zhou2026paper9_local` (local-only) | Internal drafts may cite the local Paper9 v6 manuscript for Bishan CountyLevelEnv task/reward provenance; replace or formalize before submission. |

## Suggested manuscript usage

### Introduction

Use `yao2018spatial_optimization_land_use`, `stewart2014multiobjective_gis_land_use`,
and `demetriou2012ipdss_land_consolidation` in the opening field paragraph to
establish that land-use and land-consolidation planning are spatially explicit,
multi-criteria optimization problems. Avoid overstating that these papers solve
Paper10's exact farmland swap setting.

Use `mayne2014mpc_future_promise`, `ha2018recurrent_world_models`, and
`hafner2019planet` in the bottleneck/prior-work paragraph to connect long-horizon
candidate evaluation with MPC and learned latent world-model planning.

Use `assran2023ijepa` and, if the manuscript explicitly discusses LeWM,
`maes2026leworldmodel` to justify the JEPA naming and the design connection to
predictive latent representations.

### Methods

Use external citations sparingly in Methods. The implementation details of
`frontier_random050`, executable masks, monitor gates, value-head-only training,
and rollout evaluation are code-defined and should cite local source artifacts
instead of external papers.

If the Methods motivate the reward terms, cite land-use and land-consolidation
sources only for broad objective rationale. The exact reward formula must remain
anchored to `county_env.py` and
`paper10_geojepa_mpc/experiments/results/e0_reward_and_rollout_metric_definitions_2026-06-09.md`.
For internal drafts, `zhou2026paper9_local` can mark the local Paper9
task/reward provenance, but it is not a public-source substitute.

### Results and Discussion

Do not add external citations to the E0 result claims unless they are used for
interpretation. The quantitative claims should point to the local JSON, CSV, and
Markdown result artifacts. The discussion can cite `silver2016alphago` or
`mnih2015dqn` only when explaining the general idea of learned value scoring, not
as evidence for Paper10 performance.

The draft
`paper10_geojepa_mpc/experiments/results/e0_frontier_random050_results_discussion_cited_draft_2026-06-09.md`
applies this policy: E0 numbers remain tied to local result artifacts, while
external references frame value functions, MPC, and learned world models.

## Verification notes

| key | public verification route | status |
|---|---|---|
| `aerts2003linear_integer_land_use_allocation` | Wiley DOI page, `10.1111/j.1538-4632.2003.tb01106.x` | verified |
| `stewart2014multiobjective_gis_land_use` | University of Manchester publication page and DOI, `10.1016/j.compenvurbsys.2014.04.002` | verified |
| `yao2018spatial_optimization_land_use` | SAGE DOI page, `10.1177/0160017617728551` | verified |
| `demetriou2012ipdss_land_consolidation` | SAGE DOI page, `10.1068/b37075` | verified |
| `demetriou2014ipdss_land_consolidation_book` | Springer book page, `10.1007/978-3-319-02347-2` | verified |
| `demetriou2013parcel_shape_index` | Wiley/CiNii metadata, `10.1111/j.1467-9671.2012.01371.x` | verified |
| `teijeiro2020parcel_exchange` | ScienceDirect DOI page, `10.1016/j.compenvurbsys.2019.101422` | verified |
| `mayne2014mpc_future_promise` | ScienceDirect DOI page, `10.1016/j.automatica.2014.10.128` | verified |
| `rawlings2017model_predictive_control` | Google Books / publisher metadata | verified metadata, no DOI |
| `ha2018recurrent_world_models` | Official project page with BibTeX and NeurIPS paper link | verified |
| `hafner2019planet` | PMLR proceedings page | verified |
| `assran2023ijepa` | CVPR open-access page and OpenAIRE DOI metadata | verified |
| `maes2026leworldmodel` | arXiv page, arXiv DOI, and local `2603.19312v3.pdf` metadata | verified as preprint |
| `mnih2015dqn` | Nature DOI page, `10.1038/nature14236` | verified |
| `silver2016alphago` | Nature DOI page, `10.1038/nature16961` | verified |
| `sutton2018reinforcement_learning` | MIT Press book page | verified metadata, no DOI |
| `zhou2026paper9_local` | local `D:\test\paper9_v6.tex`; see `paper10_paper9_local_source_status_2026-06-09.md` | local-only, unpublished; not public verified |

## Remaining citation gaps

1. Replace or formalize the local Paper9 source before submission.
2. Decide whether the final journal allows citation to the 2026 LeWM arXiv
   preprint. If not, cite `assran2023ijepa` for JEPA and keep LeWM as an
   unsubmitted related-work note.
3. If the Introduction needs China-specific farmland consolidation sources,
   run a separate Chinese-language literature pass; this file only records
   globally indexed English-language sources verified today.
