# Paper10 Original Vision Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and run the first preregistered Paper10 original-vision validation pass without making a scientific conclusion before Stage 1 and Stage 2 evidence exists.

**Architecture:** Keep the validation additive. Add small tested Python helpers for monitor-matrix classification and Dongxing transfer audit, use the existing value-label generation and monitor scripts for the expensive runs, and write Markdown/JSON/CSV evidence files under `paper10_geojepa_mpc/experiments/results/`.

**Tech Stack:** Python standard library, pytest, existing Paper10 experiment modules, PowerShell Windows runner, Git-tracked Markdown/JSON/CSV evidence files.

---

## File Structure

Create:

- `paper10_geojepa_mpc/experiments/original_vision_monitor_matrix.py`
  Summarizes Stage 1 monitor JSON outputs into row-level `pass`, `near_pass`, or `fail` decisions using the preregistered thresholds.
- `paper10_geojepa_mpc/experiments/dongxing_transfer_audit.py`
  Normalizes existing Dongxing CSV summaries and computes transfer-minus-scratch effects for matched families and label budgets.
- `paper10_geojepa_mpc/experiments/original_vision_decision_packet.py`
  Generates the Stage 1-2 stop/go packet from Stage 1 monitor counts and Stage 2 Dongxing comparisons.
- `paper10_geojepa_mpc/tests/test_original_vision_monitor_matrix.py`
  Unit tests for monitor row classification and report writing.
- `paper10_geojepa_mpc/tests/test_dongxing_transfer_audit.py`
  Unit tests for Dongxing CSV normalization and matched effect calculations.
- `paper10_geojepa_mpc/tests/test_original_vision_decision_packet.py`
  Unit tests for stop/go decision selection and packet rendering.
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`
  Stage 0 registry that records the frozen evidence, preregistered thresholds, and command entry points.
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv`
  Generated Stage 2 audit table.
- `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`
  Generated Stage 2 audit narrative.
- `D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation.env.ps1`
  Local ignored PowerShell override for Stage 1 label-only runs. This file is outside git.

Modify:

- `scripts/paper10/preflight_submission_checks.py`
  Add a guarded check that the validation registry and design spec exist and do not contain prohibited positive 50-state or robust-transfer wording.
- `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  Assert the new preflight check is present.
- `README.md`, `MANIFEST.md`, `REPRODUCIBILITY.md`
  Link the validation design and registry after the registry exists.

Do not modify:

- `paper10_geojepa_mpc/experiments/value_label_generation.py`
- `paper10_geojepa_mpc/experiments/value_label_monitor.py`
- `paper10_geojepa_mpc/experiments/value_label_diagnostics.py`
- `scripts/windows/run_frontier_random050_ablation_grid.ps1`

Those existing scripts already support the Stage 1 label-only matrix.

---

### Task 1: Add Stage 0 Validation Registry

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`

- [ ] **Step 1: Create the registry file**

Use `apply_patch` to create this exact file content:

```markdown
# Paper10 Original-Vision Validation Registry

Date: 2026-06-17

This registry starts the preregistered validation pass for the original Paper10
vision. It records what is frozen before new experiments, what thresholds will
be used, and what evidence is required before changing the manuscript claim.

## Design Spec

- `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
- Commit introducing the spec: `da7e793 docs: add original vision validation design`

## Frozen Evidence

### Bishan 20x16/h5 top-5 positive anchor

- candidate family: `frontier_random050`
- label setting: `20x16/h5`
- label seed: `44`
- monitor top-k: `5`
- monitor decision: `continue`
- candidate top-k regret: `0.18767197132110597`
- candidate top-k overlap: `0.6300000000000001`
- one-step top-k regret: `2.462647271156311`
- five-seed mean total reward: `69.47054604253474`
- five-seed sample standard deviation: `1.0003610285842477`
- reproduction note:
  `paper10_geojepa_mpc/experiments/results/e0_windows_realdata_20x16_top5_reproduction_2026-06-10.md`

### 50-state seed46 boundary diagnostics

- existing Windows summary:
  `D:\test\paper10_runs\frontier_random050_ablation_summary.md`
- existing post-hoc top-k summary:
  `D:\test\paper10_runs\frontier_random050_ablation_posthoc_topk_summary.md`
- current interpretation: all tested seed46 50-state rows failed the monitor
  gate and remain row-specific negative diagnostics.

### Dongxing/Neijiang evidence

- synthesis:
  `paper10_geojepa_mpc/experiments/results/e0_dongxing_results_synthesis_2026-06-10.md`
- current interpretation: method portability, planner calibration, and
  return-label scaling are supported; robust transfer superiority is not
  supported by the current evidence.

## Confirmatory Monitor Gate

For confirmatory value-label validation, a row passes only if at least one
preregistered monitor top-k satisfies all thresholds:

| metric | pass threshold |
|---|---:|
| candidate top-k regret | `<= 0.25` |
| candidate top-k overlap | `>= 0.50` |
| one-step top-k regret | `>= 0.25` |

For 50-state Stage 1 rows, the preregistered top-k set is `5, 6, 8, 10, 12`.

## Stage 1 Label-Only Matrix

The first Windows label-only matrix uses `TrainOnPass = 0`.

| run family | states | candidates | horizon | frontier fraction | label seeds |
|---|---:|---:|---:|---:|---|
| `50x16_h5_f050` | 50 | 16 | 5 | 0.50 | 47, 48 |
| `50x20_h5_f050` | 50 | 20 | 5 | 0.50 | 47, 48 |
| `50x24_h5_f075` | 50 | 24 | 5 | 0.75 | 47, 48 |

The optional seed49-50 expansion is allowed only if the first matrix contains a
`pass` or `near_pass` decision under the design spec.

## Stage 2 Audit

The Stage 2 audit uses existing Dongxing CSV summaries before adding new
Dongxing compute. It reports matched transfer-minus-scratch effects by family
and label budget.

## Claim Lock

No new conclusion about 50-state scale-up or transfer superiority may be added
until Stage 1 and Stage 2 outputs exist and are compared against the design
spec.
```

- [ ] **Step 2: Run a focused grep check**

Run:

```powershell
rg -n "direct 50-state success|robust transfer superiority|proves scale-up" paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md
```

Expected: no output and exit code `1`.

- [ ] **Step 3: Stage and commit the registry**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md
git diff --cached --check
git commit -m "docs: add original vision validation registry"
```

Expected: commit succeeds.

---

### Task 2: Add Monitor Matrix Classification Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_original_vision_monitor_matrix.py`
- Create: `paper10_geojepa_mpc/experiments/original_vision_monitor_matrix.py`

- [ ] **Step 1: Write failing tests**

Use `apply_patch` to create `paper10_geojepa_mpc/tests/test_original_vision_monitor_matrix.py` with this exact content:

```python
import json

from paper10_geojepa_mpc.experiments.original_vision_monitor_matrix import (
    classify_monitor,
    classify_run,
    markdown_report,
    summarize_ablation,
)


def _monitor(top_k, decision, regret, overlap, one_step):
    return {
        "top_k": top_k,
        "decision": decision,
        "metrics": {
            "candidate_topk_regret": regret,
            "candidate_topk_overlap": overlap,
            "one_step_topk_regret": one_step,
        },
    }


def test_classify_monitor_passes_only_continue_rows():
    result = classify_monitor(_monitor(5, "continue", 0.24, 0.51, 0.26))

    assert result["decision_class"] == "pass"
    assert result["failed_metrics"] == []


def test_classify_monitor_marks_single_close_miss_as_near_pass():
    result = classify_monitor(_monitor(8, "stop", 0.29, 0.60, 0.40))

    assert result["decision_class"] == "near_pass"
    assert result["failed_metrics"] == ["candidate_topk_regret"]


def test_classify_monitor_rejects_multiple_misses():
    result = classify_monitor(_monitor(10, "stop", 0.40, 0.30, 0.10))

    assert result["decision_class"] == "fail"
    assert result["failed_metrics"] == [
        "candidate_topk_regret",
        "candidate_topk_overlap",
        "one_step_topk_regret",
    ]


def test_classify_run_prefers_pass_over_near_pass():
    run = {
        "run_name": "frontier_random050_50x16_h5_seed47_f050",
        "n_states": 50,
        "candidate_actions": 16,
        "label_horizon": 5,
        "frontier_fraction": 0.5,
        "label_seed": 47,
        "monitors": [
            _monitor(5, "stop", 0.29, 0.60, 0.40),
            _monitor(6, "continue", 0.20, 0.55, 0.30),
        ],
    }

    result = classify_run(run)

    assert result["row_decision"] == "pass"
    assert result["selected_top_k"] == 6
    assert result["near_pass_top_ks"] == [5]


def test_summarize_ablation_writes_json_and_markdown(tmp_path):
    summary_path = tmp_path / "summary.json"
    output_json = tmp_path / "matrix.json"
    output_md = tmp_path / "matrix.md"
    summary_path.write_text(
        json.dumps(
            {
                "run_root": str(tmp_path),
                "gate_topks": [5, 6],
                "runs": [
                    {
                        "run_name": "frontier_random050_50x16_h5_seed47_f050",
                        "n_states": 50,
                        "candidate_actions": 16,
                        "label_horizon": 5,
                        "frontier_fraction": 0.5,
                        "label_seed": 47,
                        "monitors": [
                            _monitor(5, "stop", 0.29, 0.60, 0.40),
                            _monitor(6, "continue", 0.20, 0.55, 0.30),
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload = summarize_ablation(summary_path, output_json, output_md)

    assert payload["decision_counts"] == {"pass": 1, "near_pass": 0, "fail": 0}
    assert output_json.exists()
    assert output_md.exists()
    assert "| frontier_random050_50x16_h5_seed47_f050 | pass | 6 | 5 |" in output_md.read_text(
        encoding="utf-8"
    )


def test_markdown_report_includes_no_positive_scale_claim():
    text = markdown_report(
        {
            "source_summary": "summary.json",
            "decision_counts": {"pass": 0, "near_pass": 1, "fail": 1},
            "runs": [
                {
                    "run_name": "frontier_random050_50x16_h5_seed47_f050",
                    "row_decision": "near_pass",
                    "selected_top_k": None,
                    "near_pass_top_ks": [8],
                    "best_candidate_topk_regret": 0.29,
                    "best_candidate_topk_overlap": 0.60,
                    "best_one_step_topk_regret": 0.40,
                }
            ],
        }
    )

    assert "positive 50-state" not in text.lower()
    assert "robust transfer" not in text.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_monitor_matrix.py -q -p no:cacheprovider
```

Expected: fail with `ModuleNotFoundError` for `original_vision_monitor_matrix`.

- [ ] **Step 3: Implement the monitor matrix helper**

Use `apply_patch` to create `paper10_geojepa_mpc/experiments/original_vision_monitor_matrix.py` with this exact content:

```python
import argparse
import json
from pathlib import Path
from typing import Any


THRESHOLDS = {
    "candidate_topk_regret": 0.25,
    "candidate_topk_overlap": 0.50,
    "one_step_topk_regret": 0.25,
}

NEAR_PASS_MARGIN = 0.20


def _as_float(value: Any) -> float:
    if value is None:
        raise ValueError("monitor metric is missing")
    return float(value)


def _failed_metrics(metrics: dict[str, Any]) -> list[str]:
    failed = []
    if _as_float(metrics.get("candidate_topk_regret")) > THRESHOLDS["candidate_topk_regret"]:
        failed.append("candidate_topk_regret")
    if _as_float(metrics.get("candidate_topk_overlap")) < THRESHOLDS["candidate_topk_overlap"]:
        failed.append("candidate_topk_overlap")
    if _as_float(metrics.get("one_step_topk_regret")) < THRESHOLDS["one_step_topk_regret"]:
        failed.append("one_step_topk_regret")
    return failed


def _within_near_pass(metrics: dict[str, Any], failed: list[str]) -> bool:
    if len(failed) != 1:
        return False
    if _as_float(metrics.get("one_step_topk_regret")) <= 0.0:
        return False

    metric = failed[0]
    if metric == "candidate_topk_regret":
        return _as_float(metrics[metric]) <= THRESHOLDS[metric] * (1.0 + NEAR_PASS_MARGIN)
    if metric == "candidate_topk_overlap":
        return _as_float(metrics[metric]) >= THRESHOLDS[metric] * (1.0 - NEAR_PASS_MARGIN)
    if metric == "one_step_topk_regret":
        return _as_float(metrics[metric]) >= THRESHOLDS[metric] * (1.0 - NEAR_PASS_MARGIN)
    return False


def classify_monitor(monitor: dict[str, Any]) -> dict[str, Any]:
    metrics = monitor.get("metrics", {})
    failed = _failed_metrics(metrics)
    if monitor.get("decision") == "continue" and not failed:
        decision_class = "pass"
    elif _within_near_pass(metrics, failed):
        decision_class = "near_pass"
    else:
        decision_class = "fail"

    return {
        "top_k": int(monitor["top_k"]),
        "monitor_decision": monitor.get("decision"),
        "decision_class": decision_class,
        "failed_metrics": failed,
        "candidate_topk_regret": _as_float(metrics.get("candidate_topk_regret")),
        "candidate_topk_overlap": _as_float(metrics.get("candidate_topk_overlap")),
        "one_step_topk_regret": _as_float(metrics.get("one_step_topk_regret")),
    }


def _best_regret(monitors: list[dict[str, Any]]) -> float:
    return min(float(item["candidate_topk_regret"]) for item in monitors)


def _best_overlap(monitors: list[dict[str, Any]]) -> float:
    return max(float(item["candidate_topk_overlap"]) for item in monitors)


def _best_one_step(monitors: list[dict[str, Any]]) -> float:
    return max(float(item["one_step_topk_regret"]) for item in monitors)


def classify_run(run: dict[str, Any]) -> dict[str, Any]:
    monitors = [classify_monitor(item) for item in run.get("monitors", [])]
    if not monitors:
        raise ValueError(f"run {run.get('run_name')} has no monitor rows")

    pass_topks = [item["top_k"] for item in monitors if item["decision_class"] == "pass"]
    near_topks = [item["top_k"] for item in monitors if item["decision_class"] == "near_pass"]
    if pass_topks:
        row_decision = "pass"
        selected_top_k = min(pass_topks)
    elif near_topks:
        row_decision = "near_pass"
        selected_top_k = None
    else:
        row_decision = "fail"
        selected_top_k = None

    return {
        "run_name": str(run["run_name"]),
        "n_states": int(run["n_states"]),
        "candidate_actions": int(run["candidate_actions"]),
        "label_horizon": int(run["label_horizon"]),
        "frontier_fraction": float(run["frontier_fraction"]),
        "label_seed": int(run["label_seed"]),
        "row_decision": row_decision,
        "selected_top_k": selected_top_k,
        "pass_top_ks": pass_topks,
        "near_pass_top_ks": near_topks,
        "best_candidate_topk_regret": _best_regret(monitors),
        "best_candidate_topk_overlap": _best_overlap(monitors),
        "best_one_step_topk_regret": _best_one_step(monitors),
        "monitors": monitors,
    }


def decision_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "pass": sum(1 for row in rows if row["row_decision"] == "pass"),
        "near_pass": sum(1 for row in rows if row["row_decision"] == "near_pass"),
        "fail": sum(1 for row in rows if row["row_decision"] == "fail"),
    }


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Paper10 Original-Vision Stage 1 Monitor Matrix",
        "",
        f"Source summary: `{payload['source_summary']}`",
        "",
        "## Decision Counts",
        "",
        "| decision | count |",
        "|---|---:|",
    ]
    for key in ("pass", "near_pass", "fail"):
        lines.append(f"| {key} | {payload['decision_counts'].get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| run | decision | selected top-k | near-pass top-k | best candidate regret | best candidate overlap | best one-step regret |",
            "|---|---|---:|---|---:|---:|---:|",
        ]
    )
    for row in payload["runs"]:
        selected = row["selected_top_k"] if row["selected_top_k"] is not None else "none"
        near = ",".join(str(item) for item in row["near_pass_top_ks"]) or "none"
        lines.append(
            "| {run} | {decision} | {selected} | {near} | {regret:.4f} | {overlap:.4f} | {one_step:.4f} |".format(
                run=row["run_name"],
                decision=row["row_decision"],
                selected=selected,
                near=near,
                regret=float(row["best_candidate_topk_regret"]),
                overlap=float(row["best_candidate_topk_overlap"]),
                one_step=float(row["best_one_step_topk_regret"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation Lock",
            "",
            "A `pass` row authorizes matched training and rollout follow-up. A `near_pass` row authorizes diagnostic follow-up only. A `fail` row is evidence for that predefined row, not a general rejection of the original Paper10 vision.",
        ]
    )
    return "\n".join(lines) + "\n"


def summarize_ablation(
    summary_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
) -> dict[str, Any]:
    summary_json = Path(summary_json)
    output_json = Path(output_json)
    output_md = Path(output_md)
    source = json.loads(summary_json.read_text(encoding="utf-8"))
    rows = [classify_run(run) for run in source.get("runs", [])]
    payload = {
        "source_summary": str(summary_json),
        "thresholds": THRESHOLDS,
        "near_pass_margin": NEAR_PASS_MARGIN,
        "gate_topks": source.get("gate_topks", []),
        "decision_counts": decision_counts(rows),
        "runs": rows,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = summarize_ablation(args.summary_json, args.output_json, args.output_md)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_monitor_matrix.py -q -p no:cacheprovider
```

Expected: `6 passed`.

- [ ] **Step 5: Commit Task 2**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/original_vision_monitor_matrix.py paper10_geojepa_mpc/tests/test_original_vision_monitor_matrix.py
git diff --cached --check
git commit -m "test: add original vision monitor matrix classifier"
```

Expected: commit succeeds.

---

### Task 3: Add Dongxing Transfer Audit Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_dongxing_transfer_audit.py`
- Create: `paper10_geojepa_mpc/experiments/dongxing_transfer_audit.py`

- [ ] **Step 1: Write failing tests**

Use `apply_patch` to create `paper10_geojepa_mpc/tests/test_dongxing_transfer_audit.py` with this exact content:

```python
import csv

from paper10_geojepa_mpc.experiments.dongxing_transfer_audit import (
    audit_dongxing_transfer,
    markdown_report,
    normalize_family_rows,
    normalize_low_budget_rows,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_normalize_family_rows_maps_transfer_and_scratch():
    rows = normalize_family_rows(
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            }
        ],
        source="family.csv",
    )

    assert rows == [
        {
            "source": "family.csv",
            "comparison_key": "return_50x16_h5",
            "label_type": "return_50x16_h5",
            "label_budget": "",
            "family": "transfer",
            "episodes": 15,
            "reward_mean": 51.0,
            "reward_sd": 18.0,
            "slope_pct_mean": -0.29,
            "cont_mean": 0.020,
            "baimu_ha_mean": 107.0,
        }
    ]


def test_normalize_low_budget_rows_uses_budget_key():
    rows = normalize_low_budget_rows(
        [
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "40.5",
                "reward_sd": "12.4",
                "slope_pct_mean": "-0.24",
                "cont_mean": "0.027",
                "baimu_ha_mean": "373.0",
            }
        ],
        source="low.csv",
    )

    assert rows[0]["comparison_key"] == "low_budget_20"
    assert rows[0]["label_budget"] == "20"
    assert rows[0]["family"] == "scratch"


def test_audit_dongxing_transfer_computes_matched_effects(tmp_path):
    family_csv = tmp_path / "family.csv"
    low_csv = tmp_path / "low.csv"
    out_csv = tmp_path / "audit.csv"
    out_md = tmp_path / "audit.md"
    _write_csv(
        family_csv,
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            },
            {
                "label_type": "return_50x16_h5",
                "mode": "scratch",
                "n_episodes": "15",
                "total_reward_mean": "55.0",
                "total_reward_sd": "20.0",
                "slope_change_pct_mean": "-0.26",
                "cont_change_mean": "0.024",
                "baimu_area_change_ha_mean": "262.0",
            },
        ],
    )
    _write_csv(
        low_csv,
        [
            {
                "budget": "20",
                "family": "transfer",
                "episodes": "15",
                "reward_mean": "44.7",
                "reward_sd": "19.4",
                "slope_pct_mean": "-0.30",
                "cont_mean": "0.022",
                "baimu_ha_mean": "111.0",
            },
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "40.5",
                "reward_sd": "12.5",
                "slope_pct_mean": "-0.24",
                "cont_mean": "0.027",
                "baimu_ha_mean": "373.0",
            },
        ],
    )

    payload = audit_dongxing_transfer([family_csv], [low_csv], out_csv, out_md)

    assert len(payload["comparisons"]) == 2
    effects = {row["comparison_key"]: row["reward_effect_transfer_minus_scratch"] for row in payload["comparisons"]}
    assert effects["return_50x16_h5"] == -4.0
    assert effects["low_budget_20"] == 4.2
    assert out_csv.exists()
    assert out_md.exists()


def test_markdown_report_preserves_negative_transfer_boundary():
    text = markdown_report(
        {
            "comparisons": [
                {
                    "comparison_key": "return_50x16_h5",
                    "transfer_reward_mean": 51.0,
                    "scratch_reward_mean": 55.0,
                    "reward_effect_transfer_minus_scratch": -4.0,
                    "interpretation": "scratch_higher_reward",
                }
            ]
        }
    )

    assert "scratch_higher_reward" in text
    assert "robust transfer superiority" not in text.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_dongxing_transfer_audit.py -q -p no:cacheprovider
```

Expected: fail with `ModuleNotFoundError` for `dongxing_transfer_audit`.

- [ ] **Step 3: Implement the audit helper**

Use `apply_patch` to create `paper10_geojepa_mpc/experiments/dongxing_transfer_audit.py` with this exact content:

```python
import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def normalize_family_rows(rows: Iterable[dict[str, str]], source: str) -> list[dict]:
    normalized = []
    for row in rows:
        normalized.append(
            {
                "source": source,
                "comparison_key": row["label_type"],
                "label_type": row["label_type"],
                "label_budget": "",
                "family": row["mode"],
                "episodes": _int(row, "n_episodes"),
                "reward_mean": _float(row, "total_reward_mean"),
                "reward_sd": _float(row, "total_reward_sd"),
                "slope_pct_mean": _float(row, "slope_change_pct_mean"),
                "cont_mean": _float(row, "cont_change_mean"),
                "baimu_ha_mean": _float(row, "baimu_area_change_ha_mean"),
            }
        )
    return normalized


def normalize_low_budget_rows(rows: Iterable[dict[str, str]], source: str) -> list[dict]:
    normalized = []
    for row in rows:
        budget = row["budget"]
        normalized.append(
            {
                "source": source,
                "comparison_key": f"low_budget_{budget}",
                "label_type": "return_50x16_h5_low_budget",
                "label_budget": budget,
                "family": row["family"],
                "episodes": _int(row, "episodes"),
                "reward_mean": _float(row, "reward_mean"),
                "reward_sd": _float(row, "reward_sd"),
                "slope_pct_mean": _float(row, "slope_pct_mean"),
                "cont_mean": _float(row, "cont_mean"),
                "baimu_ha_mean": _float(row, "baimu_ha_mean"),
            }
        )
    return normalized


def _deduplicate(rows: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for row in rows:
        key = (row["comparison_key"], row["family"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _interpret(reward_effect: float) -> str:
    if reward_effect > 0:
        return "transfer_higher_reward"
    if reward_effect < 0:
        return "scratch_higher_reward"
    return "reward_tie"


def build_comparisons(rows: list[dict]) -> list[dict]:
    by_key: dict[str, dict[str, dict]] = {}
    for row in rows:
        by_key.setdefault(row["comparison_key"], {})[row["family"]] = row

    comparisons = []
    for key in sorted(by_key):
        families = by_key[key]
        if "transfer" not in families or "scratch" not in families:
            continue
        transfer = families["transfer"]
        scratch = families["scratch"]
        reward_effect = transfer["reward_mean"] - scratch["reward_mean"]
        comparisons.append(
            {
                "comparison_key": key,
                "label_type": transfer["label_type"],
                "label_budget": transfer["label_budget"],
                "episodes_transfer": transfer["episodes"],
                "episodes_scratch": scratch["episodes"],
                "transfer_reward_mean": transfer["reward_mean"],
                "scratch_reward_mean": scratch["reward_mean"],
                "reward_effect_transfer_minus_scratch": reward_effect,
                "transfer_reward_sd": transfer["reward_sd"],
                "scratch_reward_sd": scratch["reward_sd"],
                "slope_effect_transfer_minus_scratch": transfer["slope_pct_mean"] - scratch["slope_pct_mean"],
                "cont_effect_transfer_minus_scratch": transfer["cont_mean"] - scratch["cont_mean"],
                "baimu_ha_effect_transfer_minus_scratch": transfer["baimu_ha_mean"] - scratch["baimu_ha_mean"],
                "interpretation": _interpret(reward_effect),
                "transfer_source": transfer["source"],
                "scratch_source": scratch["source"],
            }
        )
    return comparisons


def _write_comparison_csv(path: Path, comparisons: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "comparison_key",
        "label_type",
        "label_budget",
        "episodes_transfer",
        "episodes_scratch",
        "transfer_reward_mean",
        "scratch_reward_mean",
        "reward_effect_transfer_minus_scratch",
        "transfer_reward_sd",
        "scratch_reward_sd",
        "slope_effect_transfer_minus_scratch",
        "cont_effect_transfer_minus_scratch",
        "baimu_ha_effect_transfer_minus_scratch",
        "interpretation",
        "transfer_source",
        "scratch_source",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparisons)


def markdown_report(payload: dict) -> str:
    lines = [
        "# Paper10 Original-Vision Stage 2 Dongxing Transfer Audit",
        "",
        "This audit compares matched transfer and scratch rows from existing Dongxing summaries. It does not create a positive transfer claim.",
        "",
        "| comparison | transfer reward | scratch reward | transfer minus scratch | interpretation |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["comparisons"]:
        lines.append(
            "| {key} | {transfer:.4f} | {scratch:.4f} | {effect:.4f} | {interpretation} |".format(
                key=row["comparison_key"],
                transfer=float(row["transfer_reward_mean"]),
                scratch=float(row["scratch_reward_mean"]),
                effect=float(row["reward_effect_transfer_minus_scratch"]),
                interpretation=row["interpretation"],
            )
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Rows where transfer is higher identify conditional regimes for follow-up. Rows where scratch is higher remain direct evidence against a broad transfer-win claim.",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_dongxing_transfer(
    family_csvs: list[str | Path],
    low_budget_csvs: list[str | Path],
    output_csv: str | Path,
    output_md: str | Path,
) -> dict:
    rows = []
    for path in family_csvs:
        csv_path = Path(path)
        rows.extend(normalize_family_rows(_read_csv(csv_path), source=str(csv_path)))
    for path in low_budget_csvs:
        csv_path = Path(path)
        rows.extend(normalize_low_budget_rows(_read_csv(csv_path), source=str(csv_path)))

    unique_rows = _deduplicate(rows)
    comparisons = build_comparisons(unique_rows)
    payload = {
        "family_csvs": [str(Path(path)) for path in family_csvs],
        "low_budget_csvs": [str(Path(path)) for path in low_budget_csvs],
        "n_normalized_rows": len(unique_rows),
        "comparisons": comparisons,
    }

    _write_comparison_csv(Path(output_csv), comparisons)
    Path(output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md).write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family-csv", action="append", default=[])
    parser.add_argument("--low-budget-csv", action="append", default=[])
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_dongxing_transfer(
        args.family_csv,
        args.low_budget_csv,
        args.output_csv,
        args.output_md,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        Path(args.output_json).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_dongxing_transfer_audit.py -q -p no:cacheprovider
```

Expected: `4 passed`.

- [ ] **Step 5: Commit Task 3**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/dongxing_transfer_audit.py paper10_geojepa_mpc/tests/test_dongxing_transfer_audit.py
git diff --cached --check
git commit -m "test: add Dongxing transfer audit helper"
```

Expected: commit succeeds.

---

### Task 4: Generate Stage 2 Dongxing Audit Outputs

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv`
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.json`

- [ ] **Step 1: Run the audit script on tracked Dongxing summaries**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.dongxing_transfer_audit `
  --family-csv paper10_geojepa_mpc\experiments\results\e0_dongxing_return_label_20x16_family_2026-06-10.csv `
  --family-csv paper10_geojepa_mpc\experiments\results\e0_dongxing_return_label_50x16_family_2026-06-10.csv `
  --low-budget-csv paper10_geojepa_mpc\experiments\results\e0_dongxing_low_label_budget_family_summary_2026-06-10.csv `
  --output-csv paper10_geojepa_mpc\experiments\results\e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv `
  --output-md paper10_geojepa_mpc\experiments\results\e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md `
  --output-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.json
```

Expected:

- JSON is printed to stdout.
- CSV, Markdown, and JSON output files are created under `paper10_geojepa_mpc/experiments/results/`.
- The 50x16 family comparison has `scratch_higher_reward`.
- The low-budget 20 comparison has `transfer_higher_reward`.

- [ ] **Step 2: Inspect the Markdown boundary language**

Run:

```powershell
rg -n "robust transfer superiority|clean positive transfer|dominates scratch" paper10_geojepa_mpc\experiments\results\e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md
```

Expected: no output and exit code `1`.

- [ ] **Step 3: Commit Stage 2 outputs**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.json
git diff --cached --check
git commit -m "docs: add Dongxing transfer audit evidence"
```

Expected: commit succeeds.

---

### Task 5: Add Preflight Guard and Documentation Links

**Files:**
- Modify: `scripts/paper10/preflight_submission_checks.py`
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`
- Modify: `README.md`
- Modify: `MANIFEST.md`
- Modify: `REPRODUCIBILITY.md`

- [ ] **Step 1: Write the failing preflight test assertion**

Modify `paper10_geojepa_mpc/tests/test_submission_preflight.py` inside
`test_submission_preflight_cli_passes_current_repository()` by adding this
assertion after `ceus_research_article_manuscript_draft_current`:

```python
    assert "original_vision_validation_registry_current" in payload["passed_checks"]
```

- [ ] **Step 2: Run the preflight test to verify it fails**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py::test_submission_preflight_cli_passes_current_repository -q -p no:cacheprovider
```

Expected: fail because the new check name is missing.

- [ ] **Step 3: Add the preflight check**

Modify `scripts/paper10/preflight_submission_checks.py` by adding a check function near the other current-document checks. Use this implementation:

```python
def check_original_vision_validation_registry_current(root: Path) -> CheckResult:
    paths = [
        root / "docs" / "superpowers" / "specs" / "2026-06-17-paper10-original-vision-validation-design.md",
        root / "paper10_geojepa_mpc" / "experiments" / "results" / "e0_original_vision_validation_registry_2026-06-17.md",
    ]
    missing = [path for path in paths if not path.exists()]
    if missing:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "missing: " + ", ".join(str(path.relative_to(root)) for path in missing),
        )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
    forbidden = [
        "direct 50-state bishan success",
        "robust bishan-to-dongxing transfer superiority is supported",
        "proves 50-state scale-up",
    ]
    hits = [phrase for phrase in forbidden if phrase in combined]
    if hits:
        return CheckResult(
            "original_vision_validation_registry_current",
            False,
            "forbidden validation wording: " + ", ".join(hits),
        )

    return CheckResult(
        "original_vision_validation_registry_current",
        True,
        "original-vision validation design and registry are current and guarded",
    )
```

Then add `check_original_vision_validation_registry_current` to the check list in `run_checks()`.

- [ ] **Step 4: Link the validation registry in docs**

Add one short bullet to `README.md`, `MANIFEST.md`, and `REPRODUCIBILITY.md`:

```markdown
- Original-vision validation design and registry:
  `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
  and
  `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`.
```

Use the surrounding local section that already lists CEUS or validation handoff material. Do not rewrite unrelated prose.

- [ ] **Step 5: Run focused verification**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py::test_submission_preflight_cli_passes_current_repository -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected:

- pytest target passes.
- preflight prints `Paper10 preflight: PASS`.
- output includes `[ok] original_vision_validation_registry_current`.

- [ ] **Step 6: Commit Task 5**

Run:

```powershell
git add scripts/paper10/preflight_submission_checks.py paper10_geojepa_mpc/tests/test_submission_preflight.py README.md MANIFEST.md REPRODUCIBILITY.md
git diff --cached --check
git commit -m "docs: guard original vision validation registry"
```

Expected: commit succeeds.

---

### Task 6: Prepare Stage 1 Windows Label-Only Environment

**Files:**
- Create outside git: `D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation.env.ps1`

- [ ] **Step 1: Create local run directory**

Run:

```powershell
New-Item -ItemType Directory -Force -Path D:\test\paper10_original_vision_validation\stage1_label_only | Out-Null
```

Expected: directory exists.

- [ ] **Step 2: Create the local env override**

Create `D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation.env.ps1` with this exact content:

```powershell
$DataRoot = "D:\test"
$RunRoot = "D:\test\paper10_original_vision_validation\stage1_label_only"
$PythonBin = "D:\adk\.venv\Scripts\python.exe"
$Device = "cpu"
$TrainOnPass = 0
$RunPytest = 0
$GateTopKs = @(5, 6, 8, 10, 12)

$Grid = @(
    @{
        Name = "frontier_random050_50x16_h5_seed47_f050"
        NStates = 50
        CandidateActions = 16
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 47
        TrainingSeed = 3047
    },
    @{
        Name = "frontier_random050_50x16_h5_seed48_f050"
        NStates = 50
        CandidateActions = 16
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 48
        TrainingSeed = 3048
    },
    @{
        Name = "frontier_random050_50x20_h5_seed47_f050"
        NStates = 50
        CandidateActions = 20
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 47
        TrainingSeed = 3047
    },
    @{
        Name = "frontier_random050_50x20_h5_seed48_f050"
        NStates = 50
        CandidateActions = 20
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 48
        TrainingSeed = 3048
    },
    @{
        Name = "frontier_random050_50x24_h5_seed47_f075"
        NStates = 50
        CandidateActions = 24
        LabelHorizon = 5
        FrontierFraction = 0.75
        LabelSeed = 47
        TrainingSeed = 3047
    },
    @{
        Name = "frontier_random050_50x24_h5_seed48_f075"
        NStates = 50
        CandidateActions = 24
        LabelHorizon = 5
        FrontierFraction = 0.75
        LabelSeed = 48
        TrainingSeed = 3048
    }
)
```

- [ ] **Step 3: Verify required full-data paths before long runs**

Run:

```powershell
Test-Path -LiteralPath D:\test\tool2\transitions.npz
Test-Path -LiteralPath D:\test\tool2\pairwise.npz
Test-Path -LiteralPath D:\test\dem_slope_analysis\output\DLTB_with_slope.gpkg
Test-Path -LiteralPath D:\test\results_real\blocks
Test-Path -LiteralPath D:\test\townships.json
```

Expected: all five commands print `True`.

- [ ] **Step 4: Run preflight before expensive Stage 1**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected: `Paper10 preflight: PASS`.

---

### Task 7: Run Stage 1 Label-Only Matrix

**Files:**
- Generated outside git under `D:\test\paper10_original_vision_validation\stage1_label_only\`
- Create tracked summaries after the run:
  - `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.json`
  - `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md`

- [ ] **Step 1: Run the Windows label-only matrix**

Run:

```powershell
$env:ENV_FILE = "D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation.env.ps1"
.\scripts\windows\run_frontier_random050_ablation_grid.ps1
Remove-Item Env:\ENV_FILE
```

Expected:

- each of the six configured rows produces an `.npz` value-label file;
- each row produces monitor JSON files for top-k `5, 6, 8, 10, 12`;
- `D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation_summary.json` exists;
- `TrainOnPass` remains `0`.

- [ ] **Step 2: Summarize Stage 1 into tracked evidence files**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.original_vision_monitor_matrix `
  --summary-json D:\test\paper10_original_vision_validation\stage1_label_only\frontier_random050_ablation_summary.json `
  --output-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_50state_label_matrix_2026-06-17.json `
  --output-md paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_50state_label_matrix_2026-06-17.md
```

Expected:

- JSON and Markdown summaries are created under `paper10_geojepa_mpc/experiments/results/`.
- Markdown rows contain only `pass`, `near_pass`, or `fail`.
- The interpretation lock says a failed row is not a general rejection of the original vision.

- [ ] **Step 3: Guard against overclaiming in Stage 1 summary**

Run:

```powershell
rg -n "positive 50-state|proves scale-up|robust transfer" paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_50state_label_matrix_2026-06-17.md
```

Expected: no output and exit code `1`.

- [ ] **Step 4: Commit Stage 1 summary files**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.json paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md
git diff --cached --check
git commit -m "docs: add original vision stage1 monitor matrix"
```

Expected: commit succeeds.

---

### Task 8: Generate the Stop/Go Decision Packet

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_original_vision_decision_packet.py`
- Create: `paper10_geojepa_mpc/experiments/original_vision_decision_packet.py`
- Create: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md`

- [ ] **Step 1: Write failing decision-packet tests**

Use `apply_patch` to create `paper10_geojepa_mpc/tests/test_original_vision_decision_packet.py` with this exact content:

```python
import csv
import json

from paper10_geojepa_mpc.experiments.original_vision_decision_packet import (
    build_packet,
    choose_decision,
    write_decision_packet,
)


def test_choose_decision_prefers_confirmatory_rollouts_when_any_row_passes():
    assert choose_decision({"pass": 1, "near_pass": 0, "fail": 5}) == (
        "proceed_to_stage3_confirmatory_rollouts"
    )


def test_choose_decision_expands_seed_matrix_when_only_near_pass_exists():
    assert choose_decision({"pass": 0, "near_pass": 2, "fail": 4}) == (
        "run_stage1_optional_seed49_50_expansion"
    )


def test_choose_decision_keeps_conservative_theme_when_no_row_is_close():
    assert choose_decision({"pass": 0, "near_pass": 0, "fail": 6}) == (
        "keep_conservative_ceus_theme"
    )


def test_build_packet_includes_stage1_counts_stage2_effects_and_decision():
    packet = build_packet(
        stage1_payload={
            "decision_counts": {"pass": 0, "near_pass": 1, "fail": 5},
            "runs": [],
        },
        stage2_comparisons=[
            {
                "comparison_key": "return_50x16_h5",
                "reward_effect_transfer_minus_scratch": "-4.1141",
                "interpretation": "scratch_higher_reward",
            }
        ],
    )

    assert "| pass | 0 |" in packet
    assert "| near_pass | 1 |" in packet
    assert "| return_50x16_h5 | -4.1141 | scratch_higher_reward |" in packet
    assert "Decision: run_stage1_optional_seed49_50_expansion" in packet
    assert "direct 50-state success" not in packet.lower()
    assert "robust transfer superiority" not in packet.lower()



def test_write_decision_packet_reads_json_and_csv(tmp_path):
    stage1 = tmp_path / "stage1.json"
    stage2 = tmp_path / "stage2.csv"
    output = tmp_path / "packet.md"
    stage1.write_text(
        json.dumps({"decision_counts": {"pass": 1, "near_pass": 0, "fail": 5}, "runs": []}),
        encoding="utf-8",
    )
    with stage2.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "comparison_key",
                "reward_effect_transfer_minus_scratch",
                "interpretation",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "comparison_key": "low_budget_20",
                "reward_effect_transfer_minus_scratch": "4.2484",
                "interpretation": "transfer_higher_reward",
            }
        )

    text = write_decision_packet(stage1, stage2, output)

    assert output.exists()
    assert text == output.read_text(encoding="utf-8")
    assert "Decision: proceed_to_stage3_confirmatory_rollouts" in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_decision_packet.py -q -p no:cacheprovider
```

Expected: fail with `ModuleNotFoundError` for `original_vision_decision_packet`.

- [ ] **Step 3: Implement the decision-packet helper**

Use `apply_patch` to create `paper10_geojepa_mpc/experiments/original_vision_decision_packet.py` with this exact content:

```python
import argparse
import csv
import json
from pathlib import Path
from typing import Any


def choose_decision(counts: dict[str, int]) -> str:
    if int(counts.get("pass", 0)) > 0:
        return "proceed_to_stage3_confirmatory_rollouts"
    if int(counts.get("near_pass", 0)) > 0:
        return "run_stage1_optional_seed49_50_expansion"
    return "keep_conservative_ceus_theme"


def _rationale(decision: str) -> str:
    if decision == "proceed_to_stage3_confirmatory_rollouts":
        return (
            "At least one predefined Stage 1 row passed the monitor gate. "
            "Stage 3 may train and roll out only the passing rows, with matched baselines."
        )
    if decision == "run_stage1_optional_seed49_50_expansion":
        return (
            "No predefined Stage 1 row passed, but at least one row was near-pass. "
            "The optional seed49-50 label-only expansion is justified before any training."
        )
    return (
        "No predefined Stage 1 row passed or reached near-pass status. "
        "The validation program should keep the conservative CEUS theme for now."
    )


def _counts(stage1_payload: dict[str, Any]) -> dict[str, int]:
    raw = stage1_payload.get("decision_counts", {})
    return {
        "pass": int(raw.get("pass", 0)),
        "near_pass": int(raw.get("near_pass", 0)),
        "fail": int(raw.get("fail", 0)),
    }


def _comparison_rows(stage2_comparisons: list[dict[str, Any]]) -> list[str]:
    lines = []
    for row in stage2_comparisons:
        effect = float(row["reward_effect_transfer_minus_scratch"])
        lines.append(
            "| {key} | {effect:.4f} | {interpretation} |".format(
                key=row["comparison_key"],
                effect=effect,
                interpretation=row["interpretation"],
            )
        )
    if not lines:
        lines.append("| none | 0.0000 | no_matched_comparison |")
    return lines


def build_packet(stage1_payload: dict[str, Any], stage2_comparisons: list[dict[str, Any]]) -> str:
    counts = _counts(stage1_payload)
    decision = choose_decision(counts)
    lines = [
        "# Paper10 Original-Vision Stage 1-2 Decision Packet",
        "",
        "Date: 2026-06-17",
        "",
        "## Inputs",
        "",
        "- Stage 1 monitor matrix: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_50state_label_matrix_2026-06-17.md`",
        "- Stage 2 Dongxing audit: `paper10_geojepa_mpc/experiments/results/e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.md`",
        "- Design spec: `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`",
        "",
        "## Stage 1 Summary",
        "",
        "| decision | count |",
        "|---|---:|",
        f"| pass | {counts['pass']} |",
        f"| near_pass | {counts['near_pass']} |",
        f"| fail | {counts['fail']} |",
        "",
        "## Stage 2 Summary",
        "",
        "| comparison | transfer minus scratch reward | interpretation |",
        "|---|---:|---|",
    ]
    lines.extend(_comparison_rows(stage2_comparisons))
    lines.extend(
        [
            "",
            "## Stop/Go Decision",
            "",
            f"Decision: {decision}",
            "",
            "## Rationale",
            "",
            _rationale(decision),
            "",
            "This packet is a stop/go control document. It does not change the manuscript claim by itself.",
        ]
    )
    return "\n".join(lines) + "\n"


def _read_stage2_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_decision_packet(stage1_json: str | Path, stage2_csv: str | Path, output_md: str | Path) -> str:
    stage1_path = Path(stage1_json)
    stage2_path = Path(stage2_csv)
    output_path = Path(output_md)
    stage1_payload = json.loads(stage1_path.read_text(encoding="utf-8"))
    stage2_comparisons = _read_stage2_csv(stage2_path)
    text = build_packet(stage1_payload, stage2_comparisons)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1-json", required=True)
    parser.add_argument("--stage2-csv", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(write_decision_packet(args.stage1_json, args.stage2_csv, args.output_md))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_decision_packet.py -q -p no:cacheprovider
```

Expected: `5 passed`.

- [ ] **Step 5: Generate the packet after Stage 1 and Stage 2 outputs exist**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.original_vision_decision_packet `
  --stage1-json paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_50state_label_matrix_2026-06-17.json `
  --stage2-csv paper10_geojepa_mpc\experiments\results\e0_original_vision_stage2_dongxing_transfer_audit_2026-06-17.csv `
  --output-md paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md
```

Expected: `e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md` exists and contains exactly one line beginning with `Decision:`.

- [ ] **Step 6: Verify claim boundaries**

Run:

```powershell
rg -n "direct 50-state success|robust transfer superiority|proves scale-up" paper10_geojepa_mpc\experiments\results\e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md
```

Expected: no output and exit code `1`.

- [ ] **Step 7: Commit the helper and decision packet**

Run:

```powershell
git add paper10_geojepa_mpc/experiments/original_vision_decision_packet.py paper10_geojepa_mpc/tests/test_original_vision_decision_packet.py paper10_geojepa_mpc/experiments/results/e0_original_vision_stage1_stage2_decision_packet_2026-06-17.md
git diff --cached --check
git commit -m "docs: add original vision stage1 stage2 decision packet"
```

Expected: commit succeeds.

---

### Task 9: Final Verification Before Stage 3 Planning

**Files:**
- No new files.

- [ ] **Step 1: Run focused and full validation**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_original_vision_monitor_matrix.py paper10_geojepa_mpc\tests\test_dongxing_transfer_audit.py paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected:

- all selected pytest files pass;
- preflight prints `Paper10 preflight: PASS`.

- [ ] **Step 2: Check repository status**

Run:

```powershell
git status --short --branch
```

Expected: clean working tree on `main...origin/main` or clean working tree with local commits ahead of origin.

- [ ] **Step 3: Decide Stage 3 route from the decision packet**

If the decision packet says `proceed_to_stage3_confirmatory_rollouts`, write a new Stage 3 Colab rollout plan using only rows that passed or were marked diagnostic near-pass.

If the decision packet says `run_stage1_optional_seed49_50_expansion`, create a second local env file with only the approved seed49-50 rows and repeat Tasks 7-9.

If the decision packet says `keep_conservative_ceus_theme`, stop experiment expansion and update the manuscript route without claiming failure of the original vision beyond tested rows.

---

## Self-Review Notes

Spec coverage:

- Stage 0 registry maps to Task 1.
- Stage 1 label-only matrix maps to Tasks 2, 6, and 7.
- Stage 2 Dongxing audit maps to Tasks 3 and 4.
- Guarded claim discipline maps to Tasks 5 and 8.
- Verification before Stage 3 maps to Task 9.

Scope:

- This plan covers Stage 0 through Stage 2 and the Stage 3 gate.
- It does not run Stage 3 confirmatory rollouts until Stage 1 and Stage 2 decisions exist.

Type consistency:

- Monitor row decisions are exactly `pass`, `near_pass`, and `fail`.
- Dongxing family names are exactly `transfer` and `scratch`.
- Output paths match the design spec names for Stage 1 and Stage 2 evidence files.
