# Paper10 Colab Notebook Handoff

Date: 2026-06-08

## Current State

The user approved creating a complete Google Colab notebook for the next
Paper10 `frontier_random050` 50x24/h5 experiment.

The design is to build a resumable Colab pipeline that:

- mounts Google Drive;
- clones or updates `zhouning/paper10-geojepa-mpc-farmland-layout`;
- validates the full Bishan data layout;
- generates 50x24/h5 value labels with partial output and logs;
- runs top-3/top-4/top-5 diagnostics and monitor gates;
- selects the passing top-k gate automatically;
- trains the value head with CUDA if available;
- runs 20-step blend gates and 100-step rollout validation;
- writes summary JSON, Markdown report, and a ZIP package to Drive.

## Files Already Saved

- `docs/superpowers/plans/2026-06-08-paper10-colab-50x24-notebook.md`

## Not Yet Done

- Create `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`.
- Update `README.md` and `MANIFEST.md` to mention the notebook.
- Validate the notebook JSON and referenced commands.
- Run tests, then commit and push the completed notebook.

## Important Design Notes

- Default target should be `n_states=50`, `candidate_actions=24`,
  `label_horizon=5`, `seed=45`, and training seed `3045`.
- Outputs should go to Google Drive, not Colab ephemeral storage.
- Existing `value_label_generation.py` writes `.partial.npz` for monitoring,
  but does not resume from that partial file. The notebook should make this
  explicit and skip only when final artifacts already exist.
- Full Bishan data must come from the user's Drive or uploaded data archive.
  The GitHub repository intentionally does not include full `tool2/`,
  geospatial inputs, `results_real/blocks/`, or `townships.json`.
