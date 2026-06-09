# E0 Bishan task and environment self-contained Methods note

Date: 2026-06-09

This note drafts a self-contained manuscript Methods description of the Bishan
farmland layout task used by the current Paper10 E0 `frontier_random050`
evidence package. It is intended to reduce dependence on the local-only
`zhou2026paper9_local` placeholder by making the task, state, action, reward,
and reproducibility boundary traceable to packaged code. It is not a new
experiment and does not replace the need to decide the final Paper9 citation
policy before submission.

## One-sentence argument

In the packaged Bishan environment, Paper10 evaluates a block-level sequential
farmland swap task in which each action selects one spatial block, the
environment executes up to five connectivity-aware paired farmland/forest
swaps, and the reward combines stepwise changes in slope, contiguity, and
connected baimu-fang area, with all definitions traceable to `county_env.py`,
`blocks_env.py`, and the E0 reward-definition note.

## Terminology ledger

| canonical term | first-use definition | decision |
|---|---|---|
| Bishan environment | County-level farmland layout planning environment implemented by `CountyLevelEnv`. | Use as the task/environment name. |
| parcel | Swappable land unit loaded from `DLTB_with_slope.gpkg` or `.shp`. | Use for cadastral units. |
| block | Planning unit containing one or more swappable parcels. | Use as the action target. |
| township | Administrative grouping used to load and report blocks. | Use for data organization, not as the action. |
| farmland | Parcel type with `DLBM` prefix `011`, `012`, or `013`. | Code-defined class `FARMLAND=1`. |
| forest | Parcel type with `DLBM` prefix `031`, `032`, or `033`. | Code-defined class `FOREST=2`. |
| baimu-fang patch | Connected farmland component with area at least `66700.0` square meters. | Keep pinyin term and define once. |
| executable action | Block action whose best greedy paired swap has higher farmland slope than forest slope. | Use for E0 `mask_mode=executable`. |

## Source-code basis

| definition | packaged source |
|---|---|
| Built-in Bishan constants and `CountyLevelEnv` implementation | `county_env.py` |
| Region-agnostic prepared-data factory | `arcgis_toolbox_paper9/private_source/blocks_env.py` |
| Executable action mask used by E0 | `paper10_geojepa_mpc/planning/env_masks.py` |
| Reward formula and rollout metrics | `paper10_geojepa_mpc/experiments/results/e0_reward_and_rollout_metric_definitions_2026-06-09.md` |
| E0 label generation and rollout scripts | `paper10_geojepa_mpc/experiments/value_label_generation.py`; `paper10_geojepa_mpc/experiments/run_e0_env_rollout_smoke.py` |

## Draft Methods prose

### Bishan farmland swap task

We define the Bishan planning problem as a finite-horizon sequential land-use
swap task over spatial blocks. The environment loads swappable parcels from a
prepared `DLTB_with_slope` layer and retains parcels whose land-use code
belongs to either farmland or forest. Farmland parcels are identified by `DLBM`
prefixes `011`, `012`, and `013`; forest parcels are identified by prefixes
`031`, `032`, and `033`. Parcel areas are computed after projection to
`EPSG:32648`, and parcel slopes are read from the prepared `slope_mean` field.
The environment builds parcel adjacency with queen contiguity and uses the
resulting graph to compute farmland-neighbor counts, contiguity, and connected
baimu-fang patches.

The planning units are blocks rather than individual parcels. For each township
listed in `townships.json`, the environment loads
`block_compositions.json` to map block identifiers to parcel indices and
`block_features.json` to recover static block compactness. A block action
therefore chooses where to invest the next local swap operation, while the
environment deterministically chooses the specific paired parcel conversion
inside that block. This action-space design keeps the planner at a block
resolution while retaining parcel-level slope, adjacency, and area effects in
the transition dynamics.

### State and observations

The observation is the concatenation of a per-block feature matrix and a
county-level global feature vector. Each block has 17 features, including
normalized farmland and forest slope summaries, best local slope gain,
available farmland and forest areas, remaining swap potential, prior swaps in
the block, compactness, block area, neighboring-block investment status,
neighboring farmland area, current farmland area, and whether the block has
already received investment. The global vector has 12 features, including
remaining budget fraction, normalized global farmland slope, normalized
contiguity, step fraction, slope improvement, contiguity improvement,
baimu-fang count and area summaries, invested-block fraction, investment
entropy across townships, a placeholder cross-township baimu feature, and the
maximum single-township investment fraction.

These features are code-defined descriptors used by the packaged planner and
value-label pipeline. They should not be described as externally observed
policy variables unless the final manuscript separately justifies that
interpretation. For the current E0 evidence, they define the state interface
between the Bishan environment and GeoJEPA-MPC.

### Action semantics and executable masks

The base action space is `Discrete(n_blocks)`: one action selects one block.
The base environment marks a block valid when the block still contains at least
one unswapped farmland parcel and one unswapped forest parcel. In the E0
paper-facing experiments, this base mask is intersected with an executable
mask before label generation and rollout evaluation. The executable mask
replicates the environment's greedy paired-swap rule and keeps only blocks for
which the best available farmland parcel has a higher slope than the best
available forest parcel.

For a selected block, the greedy execution rule attempts at most
`swaps_per_step=5` paired swaps. At each paired swap, the environment scores
candidate farmland parcels by slope minus `delta_conn` times the current
farmland-neighbor count, and scores candidate forest parcels by slope minus
`gamma_conn` times the current farmland-neighbor count. The highest-scored
farmland parcel is converted to forest, and the lowest-scored forest parcel is
converted to farmland, only if the farmland parcel has higher slope than the
forest parcel. Converted parcels are marked as swapped and cannot be used again
in the same episode. If no qualifying pair remains, block execution stops
before the five-swap maximum.

### Reward and episode termination

The default episode budget is 500 paired swaps, with at most five paired swaps
per environment action, giving a maximum of 100 planning steps. After each
block action, the reward combines normalized stepwise reduction in
area-weighted farmland slope, normalized stepwise change in contiguity,
normalized stepwise change in connected baimu-fang area, and a bonus for newly
counted baimu-fang patches. The environment adds an asymmetric penalty when
baimu-fang area decreases and a `-1.0` penalty when the selected block executes
zero swaps. The exact formula and reporting metrics are recorded in
`e0_reward_and_rollout_metric_definitions_2026-06-09.md`.

The environment terminates when the step count reaches `max_steps`, or earlier
if no base-valid block remains. Under E0 `mask_mode=executable`, the planner
also restricts its candidate set to executable blocks. Rollout total reward is
reported as the undiscounted sum of per-step environment rewards over the
100-step episode. Value-label returns use the same environment reward but apply
the label horizon and discount factor configured in the value-label generator.

### Data-root and reproducibility boundary

The region-agnostic factory `make_env` builds the environment from a prepared
data root containing a `DLTB_with_slope` layer, block composition files, block
feature files, and `townships.json`. The built-in Bishan layout uses the
repository root as the prepared-data root. The current paper-facing E0
reproduction route is the root that resolves
`dem_slope_analysis/output/DLTB_with_slope.gpkg`, because the macOS audit
matched the packaged 20x16/h5 seed44 label arrays under the GPKG root and
showed that shapefile-first resolution can generate different labels. The
GPKG-root convention should therefore be stated as part of the experimental
condition when reporting the 20x16/top5 result.

Full reruns still require the external full Bishan Tool2 data and prepared
geospatial inputs described in `DATA_AVAILABILITY.md` and `REPRODUCIBILITY.md`.
The Git repository includes smoke data, generated E0 labels, monitor outputs,
checkpoints, rollout summaries, tests, and figure source data, but it does not
currently contain the full `tool2/` directory or all prepared full-data
geospatial inputs.

## How this reduces the Paper9 blocker

This note provides a public, code-derived Methods route for the Bishan task and
environment definitions. If the final manuscript cannot cite a public Paper9
source, the authors can merge this note with
`e0_reward_and_rollout_metric_definitions_2026-06-09.md` and cite the packaged
Paper10 code/supplement instead of citing `zhou2026paper9_local` for task and
reward provenance. The final submission must still choose one path explicitly:

1. Replace `zhou2026paper9_local` with a public Paper9 preprint or article.
2. Move this self-contained description into Paper10 main or supplementary
   Methods and remove the local Paper9 citation from public claims.
3. Keep Paper9 as an unpublished source only if the target journal permits it
   and the authors are willing to expose it to reviewers.

## Claim-evidence map

| claim | evidence | status |
|---|---|---|
| The environment action selects a block, not an individual parcel. | `CountyLevelEnv.action_space = spaces.Discrete(self.n_blocks)`; `step(action)` casts the action to `block_id`. | supported |
| The environment executes up to five paired swaps after one block action. | `swaps_per_step=5`; `_execute_greedy_in_block(block_id, self.swaps_per_step)`. | supported |
| Farmland and forest classes are code-defined from `DLBM` prefixes. | `_classify_type` maps `011/012/013` to farmland and `031/032/033` to forest. | supported |
| Baimu-fang patches are connected farmland components above `66700.0` square meters. | `BAIMU_THRESHOLD_M2 = 66700.0`; `_count_baimu_fang`. | supported |
| E0 uses an executable mask stricter than the base mask. | `executable_swap_mask`; E0 reward-definition note; label and rollout scripts. | supported |
| The GPKG root is part of the current 20x16 reproduction condition. | `e0_macos_gpkg_reproduction_findings_2026-06-09.md`; Data Availability draft. | supported |
| This note replaces a public Paper9 citation. | It is a code-derived draft, not a peer-reviewed or public Paper9 source. | not supported; use only as self-contained Paper10 Methods material |

## Assumptions or missing inputs

- The target journal has not been selected, so the final location of this
  material is unresolved: main Methods, supplementary Methods, or a repository
  methods note.
- The note describes the packaged environment implementation. It does not
  validate the policy meaning of each reward weight or claim that the reward is
  externally standardized.
- If the authors publish or archive Paper9 before Paper10 submission, the final
  manuscript should reconcile this code-derived wording with the formal Paper9
  notation.
