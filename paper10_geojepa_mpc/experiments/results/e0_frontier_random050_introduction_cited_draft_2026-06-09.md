# E0 frontier_random050 Introduction draft with citations

Date: 2026-06-09

This document converts the Paper10 E0 scaffold and verified citation map into a
citation-inserted Introduction draft. It uses citation keys from
`references/paper10_verified_references_2026-06-09.bib`. The Paper9
environment/reward source is now tracked separately as a local-only manuscript
placeholder in `references/paper10_local_sources_2026-06-09.bib`; this
Introduction draft does not need to cite it directly.

## One-sentence argument

In constrained farmland layout planning, we show that monitor-gated
frontier-random value labels can train a GeoJEPA-MPC value filter that improves
and stabilizes long-horizon rollouts at the validated 20x16/top5 scale, while
the tested 50-state label sets define a negative boundary for the current
candidate proposal.

## Terminology ledger

| canonical term | first-use definition | use decision |
|---|---|---|
| GeoJEPA-MPC | JEPA-regularized geospatial world-model planning with model-predictive candidate selection | Use as the method family name. |
| frontier-random value labels | Multi-step candidate-action return labels generated from `frontier_random050` candidate pools | Use as the readable phrase; keep `frontier_random050` for exact experiment labels. |
| monitor gate | Diagnostic rule that decides whether a label set is suitable for value-head training | Use before any training claim. |
| value filter | Scalar value head used to rerank or filter candidate actions during rollout | Avoid implying transition-model retraining. |
| 50-state boundary | Failed 50-state monitor diagnostics for tested `frontier_random050` labels | Present as limitation and stress test, not scale-up success. |

## Draft Introduction

Spatial land-use allocation and land-consolidation planning are commonly framed
as GIS-supported, multi-criteria optimization problems in which local parcel or
site decisions affect landscape-level objectives
[@yao2018spatial_optimization_land_use; @stewart2014multiobjective_gis_land_use;
@demetriou2012ipdss_land_consolidation]. Prior work has represented these
problems through integer programming, multiobjective land-use allocation,
parcel-exchange optimization, and parcel-shape or consolidation decision-support
systems
[@aerts2003linear_integer_land_use_allocation; @teijeiro2020parcel_exchange;
@demetriou2013parcel_shape_index;
@demetriou2014ipdss_land_consolidation_book]. Paper10 studies a related but
more sequential setting: farmland layout is improved through executable
land-use swaps, and each local swap can change slope, contiguity, connected
area, and future action availability over many planning steps.

This sequential structure creates a planning bottleneck. A candidate action that
looks attractive under an immediate score may not preserve the best
long-horizon return once subsequent swaps are considered. Model-predictive
control addresses this general problem by repeatedly using finite-horizon
predictions to choose actions under constraints
[@mayne2014mpc_future_promise; @rawlings2017model_predictive_control].
Reinforcement-learning value functions provide a complementary way to score
states or actions by expected future return, and learned value estimates have
been used to guide action selection and search in high-dimensional decision
problems [@sutton2018reinforcement_learning; @mnih2015dqn; @silver2016alphago].
For farmland swap planning, the open question is not whether long-horizon
signals are useful in principle, but whether a small and reproducible
value-label workflow can improve candidate filtering without training on
low-quality labels.

Learned world models offer one route to this problem because they can plan in a
latent representation rather than directly in the full observation space
[@ha2018recurrent_world_models; @hafner2019planet]. Joint-embedding predictive
architectures (JEPAs) further motivate predictive representation learning in
which a model predicts target embeddings instead of reconstructing raw inputs
[@assran2023ijepa]. A recent arXiv preprint, LeWorldModel, applies a
JEPA-style world-model approach to pixel-based control and is useful as a
design comparison, but it should be cited as a 2026 preprint rather than as
settled prior art [@maes2026leworldmodel]. These sources motivate the
GeoJEPA-MPC framing, but they do not solve the Paper10-specific problem of
constructing and validating multi-step candidate labels for constrained
geospatial farmland swaps.

Here we test a monitor-gated frontier-random labeling workflow for GeoJEPA-MPC.
The method first generates multi-step return labels from candidate pools that
mix model-scored frontier actions with random exploratory actions, then permits
value-head training only when predeclared candidate-regret, candidate-overlap,
one-step-regret, and state-count gates pass. The present evidence ladder is
bounded: a 10x12/top4 pilot establishes the value-head route, a 20x16/top5 run
provides the main paper-facing result, a GPKG-root audit records the current
reproducible data condition, and tested 50-state `frontier_random050` labels
remain negative diagnostics rather than training inputs. This framing supports
a specific claim - monitor-gated value labels improve GeoJEPA-MPC at the
validated 20x16/top5 scale - while identifying candidate-proposal redesign as
the next step for 50-state scale-up.

## Claim-evidence map

| claim | citation or local evidence | status |
|---|---|---|
| Land-use allocation and land consolidation can be framed as spatial multi-criteria optimization or decision support. | `yao2018spatial_optimization_land_use`; `stewart2014multiobjective_gis_land_use`; `demetriou2012ipdss_land_consolidation`; `demetriou2014ipdss_land_consolidation_book` | supported by external literature |
| Parcel-level allocation, exchange, shape, and compactness are legitimate planning concerns. | `aerts2003linear_integer_land_use_allocation`; `teijeiro2020parcel_exchange`; `demetriou2013parcel_shape_index` | supported by external literature |
| Long-horizon action choice can be framed through MPC and value functions. | `mayne2014mpc_future_promise`; `rawlings2017model_predictive_control`; `sutton2018reinforcement_learning`; `mnih2015dqn`; `silver2016alphago` | supported by external literature |
| Learned world models and JEPA-style representation learning motivate the GeoJEPA-MPC framing. | `ha2018recurrent_world_models`; `hafner2019planet`; `assran2023ijepa`; `maes2026leworldmodel` | supported, with LeWM marked as preprint |
| Paper10 improves GeoJEPA-MPC at 20x16/top5. | E0 monitor outputs, value-head checkpoint metrics, five-seed rollout summaries, and manuscript tables | supported locally |
| A positive 50-state value-head claim can be made from the current E0 evidence. | No passing 50-state monitor gate exists. | not supported; do not claim |

## Assumptions or missing inputs

- The prior Paper9 environment or reward-definition source is represented only
  by local key `zhou2026paper9_local`; replace or formalize it before
  submission.
- The target journal and reference style are not fixed. This draft uses
  Pandoc-style citation keys only as manuscript placeholders.
- China-specific farmland or land-consolidation policy citations may be added
  later if the final Introduction needs regional policy context.

## Why this structure

- Paragraph 1 establishes the spatial-planning field stake without implying that
  prior land-use papers solve the exact Paper10 swap environment.
- Paragraph 2 states the long-horizon candidate-ranking bottleneck before naming
  GeoJEPA-MPC.
- Paragraph 3 positions world models and JEPA as method motivation, not as
  evidence for Paper10 performance.
- Paragraph 4 gives the bounded present-study claim and explicitly keeps
  50-state rows as negative diagnostics.
