#!/usr/bin/env bash
set -euo pipefail

# macOS local runner for the Paper10 frontier_random050 50x24/h5 experiment.
# Run from the repository root after editing scripts/macos/frontier_random050_50x24_h5.env.
# Default target preview: N_STATES=50 CANDIDATE_ACTIONS=24 LABEL_HORIZON=5
# LABEL_SEED=45 TRAINING_SEED=3045.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$SCRIPT_DIR/frontier_random050_50x24_h5.env}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

DATA_ROOT="${DATA_ROOT:-$REPO_ROOT}"
RUN_ROOT="${RUN_ROOT:-$HOME/paper10_runs}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
DEVICE="${DEVICE:-cpu}"
RUN_OPTIONAL_SEEDS="${RUN_OPTIONAL_SEEDS:-0}"

N_STATES="${N_STATES:-50}"
CANDIDATE_ACTIONS="${CANDIDATE_ACTIONS:-24}"
LABEL_HORIZON="${LABEL_HORIZON:-5}"
LABEL_SEED="${LABEL_SEED:-45}"
TRAINING_SEED="${TRAINING_SEED:-3045}"
GAMMA="${GAMMA:-0.99}"
FRONTIER_FRACTION="${FRONTIER_FRACTION:-0.5}"
TRAINING_EPOCHS="${TRAINING_EPOCHS:-3}"
TRAINING_BATCH_SIZE="${TRAINING_BATCH_SIZE:-16}"
TRANSITION_SAMPLES="${TRANSITION_SAMPLES:-6000}"
PAIRWISE_STATES="${PAIRWISE_STATES:-50}"
PAIRWISE_SUBSAMPLE="${PAIRWISE_SUBSAMPLE:-24}"
N_PAIRS="${N_PAIRS:-8}"
ROLLOUT_HORIZON="${ROLLOUT_HORIZON:-5}"
ROLLOUT_TOP_K="${ROLLOUT_TOP_K:-50}"
GATE_ROLLOUT_STEPS="${GATE_ROLLOUT_STEPS:-20}"
FINAL_ROLLOUT_STEPS="${FINAL_ROLLOUT_STEPS:-100}"

RUN_NAME="${RUN_NAME:-frontier_random050_50x24_h5_seed45}"
RUN_DIR="$RUN_ROOT/$RUN_NAME"
LOG_DIR="$RUN_DIR/logs"
REPORT_DIR="$RUN_DIR/reports"
CHECKPOINT_DIR="$RUN_DIR/checkpoints"
PACKAGE_DIR="$RUN_DIR/packages"

mkdir -p "$LOG_DIR" "$REPORT_DIR" "$CHECKPOINT_DIR" "$PACKAGE_DIR"

require_path() {
  local path="$1"
  if [[ ! -e "$path" ]]; then
    echo "Missing required path: $path" >&2
    exit 1
  fi
}

require_any_path() {
  local label="$1"
  shift
  local path
  for path in "$@"; do
    if [[ -e "$path" ]]; then
      return 0
    fi
  done
  echo "Missing required path, expected one of: $label" >&2
  for path in "$@"; do
    echo "  $path" >&2
  done
  exit 1
}

require_dltb_layer() {
  local gpkg="$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.gpkg"
  local shp="$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.shp"
  if [[ -e "$gpkg" ]]; then
    return 0
  fi
  require_path "$shp"
  require_path "$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.dbf"
  require_path "$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.shx"
  require_path "$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.prj"
}

run_cmd() {
  local log_name="$1"
  shift
  local log_path="$LOG_DIR/$log_name"
  echo "$ $*"
  {
    echo "$ $*"
    "$@"
  } 2>&1 | tee "$log_path"
}

run_if_missing() {
  local output_path="$1"
  local log_name="$2"
  shift 2
  if [[ -e "$output_path" ]]; then
    echo "Skipping because final artifact already exists: $output_path"
    return 0
  fi
  run_cmd "$log_name" "$@"
  require_path "$output_path"
}

json_value() {
  local path="$1"
  local expression="$2"
  "$PYTHON_BIN" - "$path" "$expression" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
value = data
for part in sys.argv[2].split("."):
    value = value[part]
print(value)
PY
}

cd "$REPO_ROOT"

echo "Repository: $REPO_ROOT"
echo "DATA_ROOT: $DATA_ROOT"
echo "RUN_DIR: $RUN_DIR"
echo "PYTHON_BIN: $PYTHON_BIN"
echo "DEVICE: $DEVICE"

require_path "$DATA_ROOT/tool2/transitions.npz"
require_path "$DATA_ROOT/tool2/pairwise.npz"
require_path "$DATA_ROOT/results_real/blocks"
require_path "$DATA_ROOT/townships.json"
require_any_path \
  "dem_slope_analysis/output/DLTB_with_slope.gpkg or dem_slope_analysis/output/DLTB_with_slope.shp" \
  "$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.gpkg" \
  "$DATA_ROOT/dem_slope_analysis/output/DLTB_with_slope.shp"
require_dltb_layer

run_cmd "pytest.log" "$PYTHON_BIN" -m pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider

BASE_CHECKPOINT="$REPO_ROOT/paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt"
RESULT_PREFIX="e0_value_labels_frontier_random050_rank_seed2028_${N_STATES}x${CANDIDATE_ACTIONS}_h${LABEL_HORIZON}_seed${LABEL_SEED}"
VALUE_HEAD_RUN="e0_frontier_random050_value_head_${N_STATES}x${CANDIDATE_ACTIONS}_h${LABEL_HORIZON}_seed${LABEL_SEED}"

LABEL_PATH="$RUN_DIR/${RESULT_PREFIX}.npz"
LABEL_PARTIAL_PATH="$RUN_DIR/${RESULT_PREFIX}.partial.npz"
VALUE_HEAD_CHECKPOINT="$CHECKPOINT_DIR/${VALUE_HEAD_RUN}/value_head_seed${TRAINING_SEED}.pt"
VALUE_HEAD_METRICS="$RUN_DIR/${VALUE_HEAD_RUN}_metrics.json"
mkdir -p "$(dirname "$VALUE_HEAD_CHECKPOINT")"

# Command preview:
# value_label_generation --n-states 50 --candidate-actions 24 --label-horizon 5 --candidate-mode frontier_random --frontier-fraction 0.5 --partial-output
run_if_missing "$LABEL_PATH" "value_label_generation.log" \
  "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation \
  --checkpoint "$BASE_CHECKPOINT" \
  --prepared-dir "$DATA_ROOT" \
  --n-states "$N_STATES" \
  --candidate-actions "$CANDIDATE_ACTIONS" \
  --label-horizon "$LABEL_HORIZON" \
  --gamma "$GAMMA" \
  --seed "$LABEL_SEED" \
  --mask-mode executable \
  --candidate-mode frontier_random \
  --frontier-fraction "$FRONTIER_FRACTION" \
  --advance-policy random \
  --continuation-policy random \
  --score-batch-size 512 \
  --device "$DEVICE" \
  --partial-output "$LABEL_PARTIAL_PATH" \
  --progress-every 1 \
  --output "$LABEL_PATH"

# Command preview:
# value_label_diagnostics --top-k 3
# value_label_monitor --top-k 3
# value_label_diagnostics --top-k 4
# value_label_monitor --top-k 4
# value_label_diagnostics --top-k 5
# value_label_monitor --top-k 5
for top_k in 3 4 5; do
  diag_json="$RUN_DIR/value_label_diagnostics_top${top_k}.json"
  diag_md="$REPORT_DIR/value_label_diagnostics_top${top_k}.md"
  monitor_json="$RUN_DIR/value_label_monitor_top${top_k}.json"
  monitor_md="$REPORT_DIR/value_label_monitor_top${top_k}.md"
  run_if_missing "$diag_json" "value_label_diagnostics_top${top_k}.log" \
    "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.value_label_diagnostics \
    --input "$LABEL_PATH" \
    --top-k "$top_k" \
    --output-json "$diag_json" \
    --output-md "$diag_md"
  run_if_missing "$monitor_json" "value_label_monitor_top${top_k}.log" \
    "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.value_label_monitor \
    --input "$LABEL_PATH" \
    --top-k "$top_k" \
    --output-json "$monitor_json" \
    --output-md "$monitor_md"
done

selected_top_k="$("$PYTHON_BIN" - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
passing = []
decisions = {}
for top_k in (3, 4, 5):
    path = run_dir / f"value_label_monitor_top{top_k}.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    decisions[str(top_k)] = result.get("decision")
    if result.get("decision") == "continue":
        passing.append(top_k)
if not passing:
    raise SystemExit(f"No monitor gate passed: {decisions}")
selected = max(passing)
(run_dir / "selected_top_k.json").write_text(
    json.dumps(
        {
            "selected_top_k": selected,
            "passing_topks": passing,
            "monitor_decisions": decisions,
        },
        indent=2,
        sort_keys=True,
    ),
    encoding="utf-8",
)
print(selected)
PY
)"
echo "selected_top_k=$selected_top_k"

run_if_missing "$VALUE_HEAD_METRICS" "value_head_train.log" \
  "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train \
  --transition-path "$DATA_ROOT/tool2/transitions.npz" \
  --pairwise-path "$LABEL_PATH" \
  --init-checkpoint "$BASE_CHECKPOINT" \
  --checkpoint-path "$VALUE_HEAD_CHECKPOINT" \
  --output "$VALUE_HEAD_METRICS" \
  --epochs "$TRAINING_EPOCHS" \
  --batch-size "$TRAINING_BATCH_SIZE" \
  --transition-samples "$TRANSITION_SAMPLES" \
  --pairwise-states "$PAIRWISE_STATES" \
  --pairwise-subsample "$PAIRWISE_SUBSAMPLE" \
  --n-pairs "$N_PAIRS" \
  --candidate-top-k "$selected_top_k" \
  --candidate-batch-states 1 \
  --candidate-max-states "$PAIRWISE_STATES" \
  --checkpoint-metric auto \
  --checkpoint-mode min \
  --seed "$TRAINING_SEED" \
  --device "$DEVICE"
require_path "$VALUE_HEAD_CHECKPOINT"

for blend in 0.05 0.10; do
  blend_tag="$(printf 'blend%03d' "$(awk "BEGIN { printf \"%d\", $blend * 100 }")")"
  gate_output="$RUN_DIR/${VALUE_HEAD_RUN}_top${selected_top_k}_${blend_tag}_h${ROLLOUT_HORIZON}_k${ROLLOUT_TOP_K}_seed0_${GATE_ROLLOUT_STEPS}step.json"
  # Command preview:
  # run_e0_env_rollout_smoke --rollout-steps 20 --seed 0 --candidate-value-weight 0.05
  # run_e0_env_rollout_smoke --rollout-steps 20 --seed 0 --candidate-value-weight 0.10
  run_if_missing "$gate_output" "rollout_gate_${blend_tag}.log" \
    "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke \
    --checkpoint "$VALUE_HEAD_CHECKPOINT" \
    --prepared-dir "$DATA_ROOT" \
    --rollout-steps "$GATE_ROLLOUT_STEPS" \
    --horizon "$ROLLOUT_HORIZON" \
    --top-k "$ROLLOUT_TOP_K" \
    --seed 0 \
    --device "$DEVICE" \
    --mask-mode executable \
    --selector value_filter \
    --candidate-score-mode blend \
    --candidate-value-weight "$blend" \
    --output "$gate_output"
done

selected_blend="$("$PYTHON_BIN" - "$RUN_DIR" "$VALUE_HEAD_RUN" "$selected_top_k" "$ROLLOUT_HORIZON" "$ROLLOUT_TOP_K" "$GATE_ROLLOUT_STEPS" <<'PY'
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
run_name = sys.argv[2]
top_k = sys.argv[3]
horizon = sys.argv[4]
rollout_top_k = sys.argv[5]
steps = sys.argv[6]
choices = []
for blend in ("0.05", "0.10"):
    tag = f"blend{int(round(float(blend) * 100)):03d}"
    path = run_dir / f"{run_name}_top{top_k}_{tag}_h{horizon}_k{rollout_top_k}_seed0_{steps}step.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    choices.append((float(result.get("total_reward", 0.0)), float(blend), path.name))
choices.sort()
selected = choices[-1][1]
(run_dir / "selected_blend_gate.json").write_text(
    json.dumps(
        {
            "selected_blend_weight": selected,
            "gate_rewards": {str(blend): reward for reward, blend, _ in choices},
            "gate_files": [name for _, _, name in choices],
        },
        indent=2,
        sort_keys=True,
    ),
    encoding="utf-8",
)
print(f"{selected:.2f}")
PY
)"
selected_blend_tag="$(printf 'blend%03d' "$(awk "BEGIN { printf \"%d\", $selected_blend * 100 }")")"
echo "selected_blend=$selected_blend"

ROLLOUT_SEED0="$RUN_DIR/${VALUE_HEAD_RUN}_top${selected_top_k}_${selected_blend_tag}_h${ROLLOUT_HORIZON}_k${ROLLOUT_TOP_K}_seed0_${FINAL_ROLLOUT_STEPS}step.json"
ROLLOUT_SEED0_SUMMARY="$RUN_DIR/${VALUE_HEAD_RUN}_top${selected_top_k}_${selected_blend_tag}_h${ROLLOUT_HORIZON}_k${ROLLOUT_TOP_K}_seed0_${FINAL_ROLLOUT_STEPS}step_summary.json"

# Command preview:
# run_e0_env_rollout_smoke --rollout-steps 100 --seed 0
run_if_missing "$ROLLOUT_SEED0" "rollout_100step_seed0.log" \
  "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke \
  --checkpoint "$VALUE_HEAD_CHECKPOINT" \
  --prepared-dir "$DATA_ROOT" \
  --rollout-steps "$FINAL_ROLLOUT_STEPS" \
  --horizon "$ROLLOUT_HORIZON" \
  --top-k "$ROLLOUT_TOP_K" \
  --seed 0 \
  --device "$DEVICE" \
  --mask-mode executable \
  --selector value_filter \
  --candidate-score-mode blend \
  --candidate-value-weight "$selected_blend" \
  --output "$ROLLOUT_SEED0"

run_if_missing "$ROLLOUT_SEED0_SUMMARY" "rollout_100step_seed0_summary.log" \
  "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.rollout_summary \
  "$ROLLOUT_SEED0" \
  --output "$ROLLOUT_SEED0_SUMMARY"

ROLLOUT_SEEDS_1_4="$RUN_DIR/${VALUE_HEAD_RUN}_top${selected_top_k}_${selected_blend_tag}_h${ROLLOUT_HORIZON}_k${ROLLOUT_TOP_K}_seeds1-4_${FINAL_ROLLOUT_STEPS}step.json"
if [[ "$RUN_OPTIONAL_SEEDS" == "1" ]]; then
  # Command preview:
  # run_e0_env_rollout_smoke --rollout-steps 100 --seeds 1-4
  run_if_missing "$ROLLOUT_SEEDS_1_4" "rollout_100step_seeds1-4.log" \
    "$PYTHON_BIN" -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke \
    --checkpoint "$VALUE_HEAD_CHECKPOINT" \
    --prepared-dir "$DATA_ROOT" \
    --rollout-steps "$FINAL_ROLLOUT_STEPS" \
    --horizon "$ROLLOUT_HORIZON" \
    --top-k "$ROLLOUT_TOP_K" \
    --seeds 1-4 \
    --device "$DEVICE" \
    --mask-mode executable \
    --selector value_filter \
    --candidate-score-mode blend \
    --candidate-value-weight "$selected_blend" \
    --output "$ROLLOUT_SEEDS_1_4"
else
  echo "Skipping optional seeds 1-4. Set RUN_OPTIONAL_SEEDS=1 to run them."
fi

SUMMARY_JSON="$RUN_DIR/frontier_random050_50x24_h5_macos_summary.json"
SUMMARY_MD="$REPORT_DIR/frontier_random050_50x24_h5_macos_report.md"
"$PYTHON_BIN" - "$SUMMARY_JSON" "$SUMMARY_MD" "$RUN_NAME" "$DATA_ROOT" "$DEVICE" "$selected_top_k" "$selected_blend" "$LABEL_PATH" "$VALUE_HEAD_CHECKPOINT" "$VALUE_HEAD_METRICS" "$ROLLOUT_SEED0" "$ROLLOUT_SEED0_SUMMARY" "$ROLLOUT_SEEDS_1_4" <<'PY'
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
keys = [
    "run_name",
    "data_root",
    "device",
    "selected_top_k",
    "selected_blend_weight",
    "label_path",
    "value_head_checkpoint",
    "value_head_metrics",
    "rollout_seed0",
    "rollout_seed0_summary",
    "rollout_seeds1_4",
]
summary = dict(zip(keys, sys.argv[3:]))
summary["rollout_seeds1_4"] = (
    summary["rollout_seeds1_4"] if Path(summary["rollout_seeds1_4"]).exists() else None
)
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
report_lines = [
    "# Paper10 frontier_random050 50x24/h5 macOS report",
    "",
    f"Run name: `{summary['run_name']}`",
    f"Device: `{summary['device']}`",
    f"Selected top-k: `{summary['selected_top_k']}`",
    f"Selected blend weight: `{summary['selected_blend_weight']}`",
    "",
    "## Artifacts",
    "",
]
for key, value in summary.items():
    report_lines.append(f"- `{key}`: `{value}`")
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
PY

PACKAGE_PATH="$PACKAGE_DIR/${RUN_NAME}_macos_outputs.zip"
(
  cd "$RUN_DIR"
  zip -r "$PACKAGE_PATH" . \
    -x "packages/*" \
    -x "*.partial.npz" \
    -x "*.partial.json"
)
echo "Summary: $SUMMARY_JSON"
echo "Report: $SUMMARY_MD"
echo "Package: $PACKAGE_PATH"
