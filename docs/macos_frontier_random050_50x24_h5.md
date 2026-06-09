# macOS continuation guide: frontier_random050 50x24/h5

Use this guide to reproduce, audit, or deliberately re-parameterize the Paper10
`frontier_random050` 50x24/h5 macOS diagnostic. The workflow keeps full data
and generated outputs outside Git, so the macOS machine can `git pull` the
repository and then run from local disk.

## Current status

As of 2026-06-09, the `50x24/h5 seed45` macOS run has failed the default and
post-hoc monitor gates. Do not continue that label set into value-head
training. This guide is retained for reproduction, audit, or deliberate
re-parameterization of the diagnostic workflow.

## 1. Pull the repository

```bash
git clone https://github.com/zhouning/paper10-geojepa-mpc-farmland-layout.git
cd paper10-geojepa-mpc-farmland-layout
git pull
```

If the repository already exists on the macOS machine, run only `git pull` from
the checkout.

## 2. Create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider
```

The runner defaults to `DEVICE=cpu`, which is the most conservative macOS
choice. Apple Silicon users can try `DEVICE=mps` after the smoke tests pass, but
CPU is the baseline for reproducibility.

## 3. Place the full Bishan data

Create or mount one `DATA_ROOT` directory containing:

```text
tool2/transitions.npz
tool2/pairwise.npz
dem_slope_analysis/output/DLTB_with_slope.gpkg
dem_slope_analysis/output/DLTB_with_slope.shp
results_real/blocks/
townships.json
```

Only one DLTB layer is required: either `DLTB_with_slope.gpkg` or the shapefile
set headed by `DLTB_with_slope.shp`. The full `tool2/` files and prepared
geospatial inputs remain external to Git.

## 4. Configure local paths

Copy the template and edit it:

```bash
cp scripts/macos/frontier_random050_50x24_h5.env.example \
  scripts/macos/frontier_random050_50x24_h5.env
nano scripts/macos/frontier_random050_50x24_h5.env
```

At minimum set:

```bash
DATA_ROOT=/Volumes/paper10_data/full_bishan
RUN_ROOT=$HOME/paper10_runs
PYTHON_BIN=.venv/bin/python
DEVICE=cpu
RUN_OPTIONAL_SEEDS=0
```

Set `RUN_OPTIONAL_SEEDS=1` only after the seed-0 100-step rollout has completed
and you want the optional seeds 1-4 extension.

## 5. Run the experiment

```bash
bash scripts/macos/run_frontier_random050_50x24_h5.sh
```

The script validates data layout, runs the test suite, generates the 50x24/h5
value labels, and runs top-3/top-4/top-5 diagnostics and monitors. Downstream
training is justified only if the monitor selects a passing top-k gate.

## Resume behavior

Every long step uses a final-artifact gate. If the final artifact already exists
under `RUN_ROOT`, that step is skipped on the next run. Value-label generation
writes a `.partial.npz` for monitoring during long execution, but the underlying
generator does not resume from that partial file; restart skips only when the
final `.npz` exists.

Outputs are written under:

```text
$RUN_ROOT/frontier_random050_50x24_h5_seed45/
```

Useful files after a run:

```text
logs/
reports/
selected_top_k.json
selected_blend_gate.json
frontier_random050_50x24_h5_macos_summary.json
packages/frontier_random050_50x24_h5_seed45_macos_outputs.zip
```

## Manual command mapping

The runner corresponds to the same experiment encoded in the Colab notebook,
but with macOS paths:

- `value_label_generation`: `--n-states 50 --candidate-actions 24 --label-horizon 5 --candidate-mode frontier_random --frontier-fraction 0.5`
- `value_label_diagnostics` and `value_label_monitor`: `--top-k 3`, `--top-k 4`, `--top-k 5`
- `run_e0_value_head_train`: `--candidate-top-k <selected_top_k> --seed 3045`
- `run_e0_env_rollout_smoke`: `--selector value_filter --candidate-score-mode blend --candidate-value-weight 0.05/0.10`

Keep generated outputs outside the Git checkout unless a specific artifact is
chosen for publication.
