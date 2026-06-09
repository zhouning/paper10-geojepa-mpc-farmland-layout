# Paper10 E0 reviewer smoke replication protocol

Date: 2026-06-09

This protocol gives reviewers a clone-only verification route for the Paper10
E0 reproducibility package. It is not a full Bishan rerun protocol. Full
training and real-environment rollouts require the external full Bishan
`tool2/` data and prepared GPKG-root geospatial inputs documented in
`DATA_AVAILABILITY.md`.

## What this protocol verifies

The reviewer smoke route verifies that:

- the packaged Python modules import and the test suite runs from the archive;
- the included small Tool2 smoke data has the expected array families and
  shapes;
- smoke-scale training can execute on CPU from the included smoke data;
- packaged value-label and checkpoint artifacts are readable by the same code
  paths used in the paper-facing E0 workflow;
- local rerun outputs stay under ignored `reviewer_outputs/` unless explicitly
  selected for archiving.

The smoke route does not verify:

- full Bishan value-label regeneration from the GPKG root;
- full `tool2/transitions.npz` or `tool2/pairwise.npz` training;
- five-seed 100-step real-environment rollout reproduction;
- any passing 50-state result claim.

The paper-facing positive claim remains bounded to the monitor-gated
`frontier_random050` 20x16/h5 top-5 value-head result. The tested 50-state rows
remain failed diagnostics.

## Required files included in Git

The smoke protocol uses only files included in Record 1 of the archive plan:

```text
README.md
REPRODUCIBILITY.md
requirements.txt
paper10_geojepa_mpc/
arcgis_toolbox_paper9/private_source/
county_env.py
arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/
paper10_geojepa_mpc/experiments/results/
paper10_geojepa_mpc/experiments/checkpoints/
```

The smoke Tool2 directory must contain:

```text
transitions.npz
pairwise.npz
sample_transitions.log
sample_transitions_summary.json
```

## Reviewer command sequence

From a fresh clone, create an environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the required test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Run the smoke data header check:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

Run smoke-scale training:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_smoke.py
```

Optionally run the packaged value-head training smoke against the included
10x12 value-label data. This writes only ignored local outputs:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\value_head_smoke\value_head.pt --output reviewer_outputs\value_head_smoke\metrics.json --epochs 1 --batch-size 16 --transition-samples 500 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
```

On macOS or Linux, use the active environment's `python` executable and forward
slashes in paths. The module names and arguments are otherwise the same.

## Expected smoke outputs

The test suite should report all packaged tests passing. On the current
Windows verification environment, the expected count is:

```text
108 passed
```

The smoke data header check should report these array shapes:

```text
transitions:
  actions: [500]
  block_features: [500, 30, 17]
  global_features: [500, 12]
  next_block_features: [500, 30, 17]
  next_global_features: [500, 12]
  rewards: [500]

pairwise:
  actions: [100, 10]
  rewards: [100, 10]
  states_bf: [100, 30, 17]
  states_gf: [100, 12]
```

The smoke-scale training command should emit three entries named `mse_only`,
`rank`, and `rank_sigreg`. The current CPU run reports `n_transition_samples`
`500`, `n_pairwise_states` `100`, and ranking accuracies `0.59375`, `0.71875`,
and `0.71875`, respectively. Small floating-point differences in loss values
are acceptable across Python, PyTorch, and BLAS builds.

The optional value-head smoke should produce
`reviewer_outputs/value_head_smoke/metrics.json` with
`transition_loss_enabled=false`, `trainable_scope=value_head`, and candidate
top-4 metrics over the packaged 10x12 label file.

## How to interpret failures

| failure | likely cause | reviewer action |
|---|---|---|
| Import or pytest failure | Missing dependency, wrong Python environment, or incomplete archive clone. | Reinstall `requirements.txt`; confirm the clone contains `paper10_geojepa_mpc/`, `arcgis_toolbox_paper9/private_source/`, and `county_env.py`. |
| Smoke data file missing | The archive omitted the small Tool2 smoke directory. | Check `arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/`; this is a Record 1 archive issue, not a full-data access issue. |
| Full-data command fails with missing `tool2/` or GPKG files | The reviewer is running a full Bishan command without external data. | Use the smoke protocol first; request or mount the full-data route described in `DATA_AVAILABILITY.md` for full reruns. |
| Output appears under `reviewer_outputs/` | Expected local rerun behavior. | Do not archive this directory unless final generated artifacts are deliberately selected and documented. |

## Submission backfill use

Before final archive release, record the exact submission commit, archive DOI or
anonymous reviewer link, and final smoke-test result in:

```text
paper10_geojepa_mpc/experiments/results/e0_archive_release_and_doi_backfill_checklist_2026-06-09.md
paper10_geojepa_mpc/experiments/results/e0_data_code_availability_draft_2026-06-09.md
```

If a journal requires one-click full-data review, this smoke protocol is still
useful but insufficient by itself. Add the full Tool2 and GPKG-root public or
controlled-access records before submission.
