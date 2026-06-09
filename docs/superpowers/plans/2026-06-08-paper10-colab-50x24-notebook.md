# Paper10 Colab 50x24 Notebook Implementation Plan

Status update, 2026-06-09: this plan is superseded as the next training route.
The 50x24/h5 seed45 line was run on macOS with the GPKG root and failed the
default and post-hoc monitor gates. Keep the notebook as a diagnostic template,
but do not continue the seed45 label set into value-head training.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Original goal, now superseded:** Create a complete Google Colab notebook for
the Paper10 `frontier_random050` 50x24/h5 experiment.

**Architecture:** The notebook is a resumable experiment pipeline. It mounts Google Drive, clones the reviewer repository, validates full Bishan data placement, writes long-running outputs to Drive, and skips steps whose final artifacts already exist.

**Tech Stack:** Google Colab, Python 3, PyTorch, GeoPandas, libpysal, Paper10 experiment modules, Google Drive storage.

---

### Task 1: Notebook Skeleton

**Files:**
- Create: `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`

- [ ] Add notebook metadata for Python 3 Colab execution.
- [ ] Add an opening Markdown cell explaining objective, required data, and expected runtime.
- [ ] Add a parameters cell with repository URL, branch, Drive paths, target scale, seeds, and rollout settings.

### Task 2: Colab Setup And Data Validation

**Files:**
- Create: `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`

- [ ] Add Drive mount, repository clone/update, and dependency installation cells.
- [ ] Add full-data layout checks for `tool2/transitions.npz`, `tool2/pairwise.npz`, `dem_slope_analysis/output/DLTB_with_slope.gpkg` or shapefile, `results_real/blocks/`, and `townships.json`.
- [ ] Add a smoke test cell using `pytest`.

### Task 3: 50x24/h5 Experiment Pipeline

**Files:**
- Create: `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`

- [ ] Add value-label generation with `--n-states 50`, `--candidate-actions 24`, `--label-horizon 5`, `--candidate-mode frontier_random`, `--frontier-fraction 0.5`, and `.partial.npz` output.
- [ ] Add top-3/top-4/top-5 diagnostics and monitor cells.
- [ ] Add automatic top-k selection from monitor decisions.
- [ ] Add value-head training using CUDA when available.

### Task 4: Rollout, Summary, And Packaging

**Files:**
- Create: `notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb`

- [ ] Add 20-step blend0.05 and blend0.10 gates.
- [ ] Add 100-step seed0 rollout and optional seeds1-4 rollout.
- [ ] Add summary JSON and Markdown report generation.
- [ ] Add ZIP packaging to Google Drive for download.

### Task 5: Verification And Repository Update

**Files:**
- Modify: `README.md`
- Modify: `MANIFEST.md`

- [ ] Validate the notebook is parseable JSON.
- [ ] Confirm all referenced commands use Colab paths rather than local Windows paths.
- [ ] Update repository docs to mention the Colab notebook.
- [ ] Run the Paper10 test suite from the release repository.
- [ ] Commit and push the notebook and docs.
