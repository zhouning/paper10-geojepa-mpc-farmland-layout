# Paper10 Paper9 local-source status

Date: 2026-06-09

This note resolves the current Paper10 Paper9 citation gap as far as the local
workspace allows. It does not claim that Paper9 is publicly published or
externally verified. It records a local-only source that can support internal
drafting until the authors provide a public preprint, accepted article, or final
supplementary-material citation.

## Local source selected

| item | status | reason |
|---|---|---|
| `D:\test\paper9_v6.tex` | selected local source | Complete local manuscript with task formulation, Bishan CountyLevelEnv setting, reward formulation, action-space encapsulation, and data availability notes. |
| `D:\test\paper9_v7_draft.tex` | newer draft, not selected as citation source | Nature Sustainability skeleton; useful narrative update, but comments describe Methods/Data/Code/Bibliography as stubs lifted from v6. |
| `D:\test\paper9_dual_dreamer.tex` | older related draft | Contains CountyLevelEnv and reward text, but v6 is more complete and better aligned with reward/method details. |

Local-only BibTeX:

- `references/paper10_local_sources_2026-06-09.bib`
- Key: `zhou2026paper9_local`

## What the local Paper9 source supports

| Paper10 claim | local Paper9 support | use in Paper10 |
|---|---|---|
| Bishan farmland planning is a county-level sequential block-selection task. | `paper9_v6.tex` Methods describes Bishan District, 13 townships, 2,600 spatial blocks, 52,515 cadastral parcels, 100-step episodes, and a 500 paired-swap budget. | Methods task formulation. |
| The environment action chooses a block, while paired farmland-forest swaps are executed internally. | `paper9_v6.tex` Methods action-space section describes block-level categorical actions and deterministic paired-swap execution. | Methods action semantics. |
| Reward combines slope reduction, contiguity, baimu-fang count/area, and bonuses/penalties. | `paper9_v6.tex` Methods reward section defines the reward formula, weights, slope metric, contiguity metric, and baimu-fang reporting. | Methods reward provenance and Paper10 reward definitions. |
| Raw cadastral data are restricted, but derived features/logs can support reproducibility. | `paper9_v6.tex` Data availability section records governance restrictions and planned release of derived features, pairwise data, seeds, hyperparameters, and logs. | Data/reproducibility boundary. |

## Manuscript policy

- Internal Paper10 drafts may use `[@zhou2026paper9_local]` only as a
  local-source placeholder.
- Do not merge `zhou2026paper9_local` into
  `paper10_verified_references_2026-06-09.bib`, because that file is reserved
  for public DOI, publisher, arXiv, or conference sources.
- Before journal submission, replace `[@zhou2026paper9_local]` with one of:
  a public Paper9 preprint, an accepted/published Paper9 article, a final
  supplementary-methods citation bundled with Paper10, or a self-contained
  Paper10 Methods section that no longer cites Paper9 for task/reward
  provenance.
- If the target venue permits citation of unpublished manuscripts, keep the
  local-only entry clearly marked as unpublished and author-verified.

## Self-contained Paper10 replacement route

The repository now includes a code-derived task/environment Methods note:

- `paper10_geojepa_mpc/experiments/results/e0_bishan_task_environment_self_contained_methods_2026-06-09.md`

This note describes the Bishan task, data-root convention, parcel/block/township
hierarchy, state features, block-action semantics, greedy paired-swap execution,
episode termination, and the route for merging the reward-definition note into
Paper10 Methods. It is not a public Paper9 citation. It is a replacement route
only if the final manuscript moves the relevant task and reward details into
Paper10 main Methods, supplementary Methods, or a citable code/data supplement.

## Remaining action

Author decision needed: choose whether Paper9 will be cited as a separate
public work, moved into Paper10 supplementary methods using the self-contained
Methods note plus reward-definition note, or treated as local code provenance
only.
