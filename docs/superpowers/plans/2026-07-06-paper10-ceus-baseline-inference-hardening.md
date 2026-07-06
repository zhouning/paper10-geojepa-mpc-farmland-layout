# Paper10 CEUS Baseline and Inference Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a source-derived CEUS baseline/inference hardening audit and manuscript patch that make Paper10's matched baseline, mixed seed-wise evidence, secondary-metric tradeoffs, and allowed statistical language machine-checkable.

**Architecture:** Add one focused experiment/audit module that reads existing JSON/CSV artifacts and writes a deterministic Markdown+JSON report; add one manuscript patch Markdown file; extend the existing preflight checker with a guard for the new audit and patch. No training, rollout, or algorithm tuning is performed in this pass.

**Tech Stack:** Python standard library (`json`, `csv`, `statistics`, `math`, `argparse`, `pathlib`), pytest, existing Paper10 preflight framework.

---

## File Structure

- Create `paper10_geojepa_mpc/experiments/ceus_baseline_inference_hardening.py`
  - Computes paired reward summaries, exact diagnostic sign-test p-value, claim gates, secondary-metric tradeoff classification, Markdown report text, and JSON/Markdown file writing.
- Create `paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py`
  - Tests sign-test math, paired mixed-seed summaries, secondary tradeoff classification, current tracked source numbers, and file writing.
- Modify `scripts/paper10/preflight_submission_checks.py`
  - Adds constants for the hardening Markdown/JSON outputs and manuscript patch.
  - Adds `check_paper10_ceus_baseline_inference_hardening_current`.
  - Registers the check in `REQUIRED_PATHS`, `PUBLIC_SUBMISSION_DOCS`, and `CHECKS`.
- Modify `paper10_geojepa_mpc/tests/test_submission_preflight.py`
  - Imports new constants, includes new files in the minimal fixture, and adds preflight failure/guardrail tests.
- Create generated audit outputs:
  - `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
  - `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json`
- Create manuscript patch:
  - `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`
- Modify public docs:
  - `README.md`
  - `MANIFEST.md`
  - `REPRODUCIBILITY.md`
  - `DATA_AVAILABILITY.md`

---

### Task 1: Add Baseline Hardening Audit Tests

**Files:**
- Create: `paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py`
- Expected later implementation: `paper10_geojepa_mpc/experiments/ceus_baseline_inference_hardening.py`

- [ ] **Step 1: Write the failing test file**

Create `paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py` with:

```python
import json
from pathlib import Path

import pytest

from paper10_geojepa_mpc.experiments.ceus_baseline_inference_hardening import (
    build_baseline_hardening_audit,
    classify_secondary_tradeoffs,
    hardening_markdown_report,
    paired_reward_summary,
    two_sided_sign_test_pvalue,
    write_baseline_hardening_audit,
)


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
CURRENT_5SEED = (
    RESULTS / "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
)
MECHANISM_PACKET = RESULTS / "e0_paper10_mechanism_ablation_packet_2026-06-20.json"


def _matched_payload() -> dict:
    return {
        "date": "2026-06-27",
        "policies": {
            "baseline": {
                "aggregate": {
                    "total_reward_mean": 10.0,
                    "total_reward_std_sample": 4.0,
                },
            },
            "candidate": {
                "aggregate": {
                    "total_reward_mean": 11.0,
                    "total_reward_std_sample": 1.0,
                },
            },
        },
        "paired_comparison": {
            "matched_seeds": [0, 1, 2, 3, 4],
            "per_seed": [
                {
                    "seed": 0,
                    "baseline_total_reward": 12.0,
                    "candidate_total_reward": 10.0,
                    "total_reward_delta_candidate_minus_baseline": -2.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.10,
                        "cont_change": 0.02,
                        "baimu_area_change_ha": 5.0,
                    },
                },
                {
                    "seed": 1,
                    "baseline_total_reward": 8.0,
                    "candidate_total_reward": 11.0,
                    "total_reward_delta_candidate_minus_baseline": 3.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.20,
                        "cont_change": -0.01,
                        "baimu_area_change_ha": 2.0,
                    },
                },
                {
                    "seed": 2,
                    "baseline_total_reward": 9.0,
                    "candidate_total_reward": 14.0,
                    "total_reward_delta_candidate_minus_baseline": 5.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.30,
                        "cont_change": 0.01,
                        "baimu_area_change_ha": 1.0,
                    },
                },
                {
                    "seed": 3,
                    "baseline_total_reward": 7.0,
                    "candidate_total_reward": 13.0,
                    "total_reward_delta_candidate_minus_baseline": 6.0,
                    "final_metric_deltas": {
                        "slope_change_pct": 0.15,
                        "cont_change": -0.02,
                        "baimu_area_change_ha": 3.0,
                    },
                },
                {
                    "seed": 4,
                    "baseline_total_reward": 14.0,
                    "candidate_total_reward": 7.0,
                    "total_reward_delta_candidate_minus_baseline": -7.0,
                    "final_metric_deltas": {
                        "slope_change_pct": -0.05,
                        "cont_change": 0.03,
                        "baimu_area_change_ha": -4.0,
                    },
                },
            ],
        },
    }


def _mechanism_payload() -> dict:
    return {
        "condition_comparisons": {
            "full_gated_masked": {
                "condition": "full_gated_masked",
                "mean_reward": 69.0,
                "std_sample": 1.0,
                "slope_change_pct_mean": -1.25,
                "cont_change_mean": 0.019,
                "baimu_area_change_ha_mean": -207.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
            "heuristic_paper9_masked": {
                "condition": "heuristic_paper9_masked",
                "mean_reward": 67.0,
                "std_sample": 7.0,
                "slope_change_pct_mean": -1.26,
                "cont_change_mean": 0.020,
                "baimu_area_change_ha_mean": -211.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
            "no_mask": {
                "condition": "no_mask",
                "mean_reward": 40.0,
                "std_sample": 10.0,
                "slope_change_pct_mean": -1.09,
                "cont_change_mean": 0.014,
                "baimu_area_change_ha_mean": -195.0,
                "zero_swap_steps_sum": 100.0,
                "negative_zero_swap_steps_sum": 98.0,
            },
            "ungated_top4": {
                "condition": "ungated_top4",
                "mean_reward": 69.0,
                "std_sample": 1.0,
                "slope_change_pct_mean": -1.25,
                "cont_change_mean": 0.019,
                "baimu_area_change_ha_mean": -207.0,
                "zero_swap_steps_sum": 0.0,
                "negative_zero_swap_steps_sum": 0.0,
            },
        },
        "stage3_boundary": {
            "best_value_filter": {
                "run": "existing blend010",
                "mean_total_reward": 67.4913,
                "delta_vs_paper9": -0.0524,
            }
        },
    }


def test_two_sided_sign_test_for_three_wins_two_losses_is_diagnostic_only():
    assert two_sided_sign_test_pvalue(3, 2) == pytest.approx(1.0)
    assert two_sided_sign_test_pvalue(5, 0) == pytest.approx(0.0625)
    assert two_sided_sign_test_pvalue(0, 0) == pytest.approx(1.0)


def test_paired_reward_summary_classifies_mixed_seed_result():
    summary = paired_reward_summary(_matched_payload())

    assert summary["n_seeds"] == 5
    assert summary["candidate_win_count"] == 3
    assert summary["candidate_loss_count"] == 2
    assert summary["tie_count"] == 0
    assert summary["paired_mean_delta"] == pytest.approx(1.0)
    assert summary["paired_median_delta"] == pytest.approx(3.0)
    assert summary["paired_min_delta"] == pytest.approx(-7.0)
    assert summary["paired_max_delta"] == pytest.approx(6.0)
    assert summary["all_seeds_improve"] is False
    assert summary["uniform_superiority_supported"] is False
    assert summary["inferential_superiority_supported"] is False
    assert summary["descriptive_mean_reward_anchor_supported"] is True
    assert summary["sign_test"]["classification"] == "diagnostic_only"
    assert summary["sign_test"]["p_value"] == pytest.approx(1.0)


def test_secondary_tradeoffs_capture_reward_gain_and_metric_mixture():
    tradeoffs = classify_secondary_tradeoffs(_mechanism_payload())

    assert tradeoffs["classification"] == "reward_descriptive_secondary_mixed"
    assert tradeoffs["reward_delta_vs_matched_paper9"] == pytest.approx(2.0)
    assert tradeoffs["std_delta_vs_matched_paper9"] == pytest.approx(-6.0)
    assert tradeoffs["no_mask_negative_zero_swap_steps"] == pytest.approx(98.0)
    assert tradeoffs["ungated_reward_delta_vs_full"] == pytest.approx(0.0)
    assert "cont_change_mean" in tradeoffs["tradeoff_metrics"]
    assert tradeoffs["executable_mask_necessity_supported"] is True
    assert tradeoffs["monitor_gate_direct_reward_gain_supported"] is False


def test_build_current_tracked_hardening_audit_locks_claim_gates():
    audit = build_baseline_hardening_audit(
        matched_5seed=json.loads(CURRENT_5SEED.read_text(encoding="utf-8")),
        mechanism_packet=json.loads(MECHANISM_PACKET.read_text(encoding="utf-8")),
        matched_5seed_source=str(CURRENT_5SEED.relative_to(ROOT)),
        mechanism_packet_source=str(MECHANISM_PACKET.relative_to(ROOT)),
        date="2026-07-06",
    )

    summary = audit["paired_reward_summary"]
    assert audit["status"] == "source-derived CEUS baseline and inference hardening audit"
    assert summary["n_seeds"] == 5
    assert summary["candidate_win_count"] == 3
    assert summary["candidate_loss_count"] == 2
    assert summary["uniform_superiority_supported"] is False
    assert summary["inferential_superiority_supported"] is False
    assert summary["descriptive_mean_reward_anchor_supported"] is True
    assert summary["sign_test"]["p_value"] == pytest.approx(1.0)
    assert summary["paired_mean_delta"] == pytest.approx(1.9268761922171436)
    assert summary["paired_median_delta"] == pytest.approx(3.613740374883278)
    assert audit["secondary_metric_tradeoffs"]["classification"] == (
        "reward_descriptive_secondary_mixed"
    )
    assert audit["claim_gates"]["stage3_50state_scaleup_supported"] is False
    assert audit["claim_gates"]["robust_transfer_superiority_supported"] is False
    assert audit["source_provenance"]["matched_5seed_audit"].endswith(
        "e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json"
    )


def test_markdown_report_uses_hardened_ceus_wording():
    audit = build_baseline_hardening_audit(
        matched_5seed=_matched_payload(),
        mechanism_packet=_mechanism_payload(),
        matched_5seed_source="matched.json",
        mechanism_packet_source="mechanism.json",
        date="2026-07-06",
    )

    text = hardening_markdown_report(audit)

    assert "# Paper10 CEUS baseline and inference hardening audit" in text
    assert "diagnostic_only" in text
    assert "mixed seed-wise outcome" in text
    assert "uniform superiority is not supported" in text
    assert "inferential superiority is not supported" in text
    assert "executable-mask necessity" in text
    assert "monitor gate as evidence control" in text
    assert "statistically significant" not in text
    assert "robustly superior" not in text


def test_write_baseline_hardening_audit_writes_json_and_markdown(tmp_path):
    matched = tmp_path / "matched.json"
    mechanism = tmp_path / "mechanism.json"
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    matched.write_text(json.dumps(_matched_payload()), encoding="utf-8")
    mechanism.write_text(json.dumps(_mechanism_payload()), encoding="utf-8")

    audit = write_baseline_hardening_audit(
        matched_5seed_json=matched,
        mechanism_packet_json=mechanism,
        output_json=output_json,
        output_md=output_md,
        date="2026-07-06",
    )

    assert output_json.exists()
    assert output_md.exists()
    assert json.loads(output_json.read_text(encoding="utf-8")) == audit
    assert output_md.read_text(encoding="utf-8") == hardening_markdown_report(audit)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py -q -p no:cacheprovider
```

Expected: FAIL during import with `ModuleNotFoundError: No module named 'paper10_geojepa_mpc.experiments.ceus_baseline_inference_hardening'`.

- [ ] **Step 3: Commit failing tests**

```powershell
git add paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py
git commit -m "test: cover paper10 ceus baseline hardening audit"
```

---

### Task 2: Implement Source-Derived Hardening Runner

**Files:**
- Create: `paper10_geojepa_mpc/experiments/ceus_baseline_inference_hardening.py`
- Test: `paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py`

- [ ] **Step 1: Add the minimal implementation**

Create `paper10_geojepa_mpc/experiments/ceus_baseline_inference_hardening.py`:

```python
from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any


DATE = "2026-07-06"


def _as_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _sample_std(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def two_sided_sign_test_pvalue(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def paired_reward_summary(matched_5seed: dict[str, Any]) -> dict[str, Any]:
    paired = matched_5seed["paired_comparison"]
    rows = list(paired["per_seed"])
    seed_rows = []
    deltas = []
    wins = 0
    losses = 0
    ties = 0
    for row in rows:
        delta = _as_float(row["total_reward_delta_candidate_minus_baseline"])
        if delta > 0:
            label = "win"
            wins += 1
        elif delta < 0:
            label = "loss"
            losses += 1
        else:
            label = "tie"
            ties += 1
        deltas.append(delta)
        seed_rows.append(
            {
                "seed": row["seed"],
                "baseline_total_reward": _as_float(row["baseline_total_reward"]),
                "candidate_total_reward": _as_float(row["candidate_total_reward"]),
                "delta": delta,
                "outcome": label,
                "final_metric_deltas": row.get("final_metric_deltas", {}),
            }
        )

    baseline_mean = _as_float(
        matched_5seed["policies"]["baseline"]["aggregate"]["total_reward_mean"]
    )
    candidate_mean = _as_float(
        matched_5seed["policies"]["candidate"]["aggregate"]["total_reward_mean"]
    )
    sign_p = two_sided_sign_test_pvalue(wins, losses)
    return {
        "n_seeds": len(seed_rows),
        "seed_rows": seed_rows,
        "baseline_mean_reward": baseline_mean,
        "candidate_mean_reward": candidate_mean,
        "baseline_sample_std": _as_float(
            matched_5seed["policies"]["baseline"]["aggregate"].get(
                "total_reward_std_sample"
            )
        ),
        "candidate_sample_std": _as_float(
            matched_5seed["policies"]["candidate"]["aggregate"].get(
                "total_reward_std_sample"
            )
        ),
        "candidate_win_count": wins,
        "candidate_loss_count": losses,
        "tie_count": ties,
        "paired_mean_delta": mean(deltas) if deltas else 0.0,
        "paired_median_delta": median(deltas) if deltas else 0.0,
        "paired_std_delta": _sample_std(deltas),
        "paired_min_delta": min(deltas) if deltas else 0.0,
        "paired_max_delta": max(deltas) if deltas else 0.0,
        "all_seeds_improve": wins == len(seed_rows) and bool(seed_rows),
        "uniform_superiority_supported": wins == len(seed_rows) and bool(seed_rows),
        "inferential_superiority_supported": False,
        "descriptive_mean_reward_anchor_supported": candidate_mean > baseline_mean,
        "sign_test": {
            "wins": wins,
            "losses": losses,
            "ties_excluded": ties,
            "p_value": sign_p,
            "classification": "diagnostic_only",
            "interpretation": (
                "Small-sample diagnostic only; current CEUS route remains "
                "descriptive because no inferential plan was predefined."
            ),
        },
    }


def _condition(packet: dict[str, Any], name: str) -> dict[str, Any]:
    conditions = packet.get("condition_comparisons", {})
    if name not in conditions:
        raise ValueError(f"missing condition comparison: {name}")
    return conditions[name]


def _delta(left: dict[str, Any], right: dict[str, Any], key: str) -> float:
    return _as_float(left.get(key)) - _as_float(right.get(key))


def classify_secondary_tradeoffs(mechanism_packet: dict[str, Any]) -> dict[str, Any]:
    full = _condition(mechanism_packet, "full_gated_masked")
    matched = _condition(mechanism_packet, "heuristic_paper9_masked")
    no_mask = _condition(mechanism_packet, "no_mask")
    ungated = _condition(mechanism_packet, "ungated_top4")
    metric_deltas = {
        "slope_change_pct_mean": _delta(full, matched, "slope_change_pct_mean"),
        "cont_change_mean": _delta(full, matched, "cont_change_mean"),
        "baimu_area_change_ha_mean": _delta(
            full, matched, "baimu_area_change_ha_mean"
        ),
    }
    aligned = [key for key, value in metric_deltas.items() if value > 0.0]
    tradeoffs = [key for key, value in metric_deltas.items() if value < 0.0]
    neutral = [key for key, value in metric_deltas.items() if value == 0.0]
    reward_delta = _delta(full, matched, "mean_reward")
    ungated_delta = _delta(full, ungated, "mean_reward")
    no_mask_negative_zero_swaps = _as_float(no_mask.get("negative_zero_swap_steps_sum"))
    return {
        "classification": (
            "reward_descriptive_secondary_mixed"
            if reward_delta > 0.0 and bool(tradeoffs)
            else "reward_descriptive_secondary_aligned"
            if reward_delta > 0.0
            else "not_supported"
        ),
        "reward_delta_vs_matched_paper9": reward_delta,
        "std_delta_vs_matched_paper9": _delta(full, matched, "std_sample"),
        "metric_deltas_vs_matched_paper9": metric_deltas,
        "aligned_metrics": aligned,
        "tradeoff_metrics": tradeoffs,
        "neutral_metrics": neutral,
        "no_mask_zero_swap_steps": _as_float(no_mask.get("zero_swap_steps_sum")),
        "no_mask_negative_zero_swap_steps": no_mask_negative_zero_swaps,
        "ungated_reward_delta_vs_full": ungated_delta,
        "executable_mask_necessity_supported": no_mask_negative_zero_swaps > 0.0,
        "monitor_gate_direct_reward_gain_supported": ungated_delta > 0.0,
    }


def build_baseline_hardening_audit(
    *,
    matched_5seed: dict[str, Any],
    mechanism_packet: dict[str, Any],
    matched_5seed_source: str,
    mechanism_packet_source: str,
    date: str = DATE,
) -> dict[str, Any]:
    paired = paired_reward_summary(matched_5seed)
    secondary = classify_secondary_tradeoffs(mechanism_packet)
    return {
        "date": date,
        "status": "source-derived CEUS baseline and inference hardening audit",
        "source_boundary": {
            "reran_training": False,
            "reran_rollouts": False,
            "post_hoc_tuning_allowed": False,
        },
        "source_provenance": {
            "matched_5seed_audit": matched_5seed_source,
            "mechanism_packet": mechanism_packet_source,
        },
        "comparator_taxonomy": {
            "matched_paper9_rank_seed2028": "default matched CEUS baseline",
            "value_filter_20x16_top5": "main descriptive Bishan value-filter anchor",
            "ungated_top4_control": "monitor-gate performance boundary",
            "no_mask_control": "executable-mask necessity control",
            "stage3_50state_rows": "boundary evidence only",
            "dongxing_transfer_scratch_families": "calibration evidence only",
        },
        "paired_reward_summary": paired,
        "secondary_metric_tradeoffs": secondary,
        "claim_gates": {
            "descriptive_mean_reward_anchor_supported": paired[
                "descriptive_mean_reward_anchor_supported"
            ],
            "uniform_superiority_supported": paired["uniform_superiority_supported"],
            "inferential_superiority_supported": paired[
                "inferential_superiority_supported"
            ],
            "executable_mask_necessity_supported": secondary[
                "executable_mask_necessity_supported"
            ],
            "monitor_gate_direct_reward_gain_supported": secondary[
                "monitor_gate_direct_reward_gain_supported"
            ],
            "stage3_50state_scaleup_supported": False,
            "robust_transfer_superiority_supported": False,
            "irregular_cadastral_deployment_supported": False,
        },
        "manuscript_language": {
            "required_phrases": [
                "descriptive matched 5-seed reward anchor",
                "mixed seed-wise outcome",
                "executable-mask necessity",
                "monitor gate as evidence control",
                "Stage 3 boundary evidence",
                "Dongxing/Neijiang calibration evidence",
            ],
            "forbidden_unqualified_phrases": [
                "statistically significant",
                "robustly superior",
                "uniformly superior",
                "direct 50-state Bishan scale-up success",
                "robust Bishan-to-Dongxing transfer superiority",
                "deployment-ready",
            ],
        },
    }


def hardening_markdown_report(audit: dict[str, Any]) -> str:
    summary = audit["paired_reward_summary"]
    secondary = audit["secondary_metric_tradeoffs"]
    gates = audit["claim_gates"]
    lines = [
        "# Paper10 CEUS baseline and inference hardening audit",
        "",
        f"Date: {audit['date']}",
        "",
        "Status: source-derived CEUS baseline and inference hardening audit.",
        "",
        "No training or rollout was rerun. Post-hoc tuning of thresholds, top_k, horizon, blend weights, or candidate-value weight remains disallowed.",
        "",
        "## Matched Baseline Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| n seeds | {summary['n_seeds']} |",
        f"| candidate wins | {summary['candidate_win_count']} |",
        f"| candidate losses | {summary['candidate_loss_count']} |",
        f"| paired mean delta | {_fmt(summary['paired_mean_delta'])} |",
        f"| paired median delta | {_fmt(summary['paired_median_delta'])} |",
        f"| paired min delta | {_fmt(summary['paired_min_delta'])} |",
        f"| paired max delta | {_fmt(summary['paired_max_delta'])} |",
        f"| sign-test p-value | {_fmt(summary['sign_test']['p_value'])} |",
        "",
        "The sign-test readout is `diagnostic_only`. The result is a mixed seed-wise outcome: uniform superiority is not supported and inferential superiority is not supported.",
        "",
        "## Claim Gates",
        "",
        "| claim gate | value |",
        "|---|---|",
    ]
    for key, value in gates.items():
        lines.append(f"| {key} | `{value}` |")
    lines.extend(
        [
            "",
            "## Secondary Metric Tradeoffs",
            "",
            f"Classification: `{secondary['classification']}`",
            "",
            "| metric | delta vs matched Paper9 |",
            "|---|---:|",
        ]
    )
    for key, value in secondary["metric_deltas_vs_matched_paper9"].items():
        lines.append(f"| {key} | {_fmt(value)} |")
    lines.extend(
        [
            "",
            f"- Reward delta versus matched Paper9: {_fmt(secondary['reward_delta_vs_matched_paper9'])}.",
            f"- Standard-deviation delta versus matched Paper9: {_fmt(secondary['std_delta_vs_matched_paper9'])}.",
            f"- No-mask negative zero-swap steps: {_fmt(secondary['no_mask_negative_zero_swap_steps'])}.",
            f"- Ungated top-4 reward delta versus full gated masked: {_fmt(secondary['ungated_reward_delta_vs_full'])}.",
            "",
            "## Manuscript Wording Boundary",
            "",
            "- Allowed: descriptive matched 5-seed reward anchor.",
            "- Required: mixed seed-wise outcome.",
            "- Supported: executable-mask necessity.",
            "- Supported as wording control: monitor gate as evidence control.",
            "- Boundary: Stage 3 boundary evidence.",
            "- Boundary: Dongxing/Neijiang calibration evidence.",
            "- Do not claim uniform superiority, inferential superiority, direct 50-state scale-up, robust transfer superiority, or deployment-ready cadastral planning.",
            "",
            "## Source Provenance",
            "",
            f"- matched 5-seed audit: `{audit['source_provenance']['matched_5seed_audit']}`",
            f"- mechanism packet: `{audit['source_provenance']['mechanism_packet']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_baseline_hardening_audit(
    *,
    matched_5seed_json: str | Path,
    mechanism_packet_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict[str, Any]:
    matched_path = Path(matched_5seed_json)
    mechanism_path = Path(mechanism_packet_json)
    audit = build_baseline_hardening_audit(
        matched_5seed=json.loads(matched_path.read_text(encoding="utf-8")),
        mechanism_packet=json.loads(mechanism_path.read_text(encoding="utf-8")),
        matched_5seed_source=str(matched_path),
        mechanism_packet_source=str(mechanism_path),
        date=date,
    )
    output_json = Path(output_json)
    output_md = Path(output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
    output_md.write_text(hardening_markdown_report(audit), encoding="utf-8")
    return audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 CEUS baseline and inference hardening audit."
    )
    parser.add_argument("--matched-5seed-json", required=True)
    parser.add_argument("--mechanism-packet-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = write_baseline_hardening_audit(
        matched_5seed_json=args.matched_5seed_json,
        mechanism_packet_json=args.mechanism_packet_json,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run focused tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 3: Commit implementation**

```powershell
git add paper10_geojepa_mpc\experiments\ceus_baseline_inference_hardening.py
git commit -m "feat: add paper10 ceus baseline hardening audit"
```

---

### Task 3: Generate Audit Outputs and Manuscript Patch

**Files:**
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`
- Test: `paper10_geojepa_mpc/tests/test_ceus_baseline_inference_hardening.py`

- [ ] **Step 1: Generate the source-derived audit outputs**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.ceus_baseline_inference_hardening `
  --matched-5seed-json paper10_geojepa_mpc\experiments\results\e0_paper10_real_env_longhorizon_5seed_confirmatory_audit_2026-06-27.json `
  --mechanism-packet-json paper10_geojepa_mpc\experiments\results\e0_paper10_mechanism_ablation_packet_2026-06-20.json `
  --output-json paper10_geojepa_mpc\experiments\results\e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json `
  --output-md paper10_geojepa_mpc\experiments\results\e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md `
  --date 2026-07-06
```

Expected: command exits 0 and writes both files.

- [ ] **Step 2: Create the manuscript patch**

Create `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`:

```markdown
# Paper10 CEUS baseline-hardened manuscript patch

Date: 2026-07-06

Status: bounded manuscript patch. This file does not replace the full manuscript
draft and does not add a new experiment. It provides drop-in wording for the
next CEUS manuscript assembly pass using
`e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md` as the current
baseline and inference boundary.

## Abstract Result Sentences

In Bishan, the validated 20x16/top5 value filter produced a descriptive matched
5-seed reward anchor: mean 100-step reward was 69.4705 for the value-filter
policy and 67.5437 for the matched Paper9 baseline under the same H=5, K=50,
executable-mask protocol. The outcome was mixed seed-wise, with the value filter
winning 3 of 5 seeds and losing seeds 0 and 4; therefore the current evidence
does not support uniform superiority or inferential superiority.

## Results: Bishan Matched Baseline Comparison

The Bishan 20x16/top5 policy remained the only positive performance anchor after
baseline hardening. Across the locked seeds 0-4, value-filter mean reward was
69.4705 compared with 67.5437 for the matched Paper9 `rank_seed2028` baseline,
and sample standard deviation was lower for the value-filter policy (1.0004
versus 7.2246). The paired reward deltas were -3.2408, 3.6137, 8.4242, 9.0620
and -8.2248. This establishes a descriptive matched 5-seed reward anchor, but
not a uniform seed-wise improvement. A diagnostic-only two-sided sign test gives
p=1.0000 for the 3-win/2-loss split, so the result should remain descriptive
unless a future predefined inference plan is added before new rollouts.

## Results: Mechanism and Secondary Metrics

The mechanism evidence separates executable-mask necessity from value-filter
superiority. Removing the executable mask reduced mean reward from 69.4705 to
40.3515 and produced 100 zero-swap steps and 98 negative zero-swap steps,
supporting executable-mask necessity for valid rollouts. By contrast, the
ungated top-4 control matched the full gated masked reward, so the monitor gate
should be described as evidence control for label escalation rather than as a
separately demonstrated online reward-gain mechanism. Secondary metrics were
mixed relative to matched Paper9: reward and reward variation favored the
value-filter anchor, while not every final slope, contiguity and baimu-area
indicator moved in the same favorable direction.

## Discussion: Baseline Fairness and Inference Limits

The baseline-hardened interpretation is narrower but more defensible for CEUS.
Paper10 does not show that value filtering is robustly superior across every
seed, region or label scale. It shows that a monitor-gated value-filter
configuration can produce a higher descriptive mean reward than a matched
Paper9 baseline in the Bishan 20x16/top5 setting, while the mixed seed-wise
outcome requires conservative reporting. This framing keeps the contribution in
decision-support terms: the workflow records when a value-label configuration
is usable, when it fails to scale, and when comparator evidence remains only
diagnostic.

## Discussion: Applicability Boundary

The Stage 3 50-state rows remain Stage 3 boundary evidence, and the later
candidate-score sweep did not overturn that boundary. Dongxing/Neijiang remains
Dongxing/Neijiang calibration evidence, not proof of robust transfer
superiority. The current block-level planning-unit abstraction and queen
contiguity are still insufficient to claim deployment-ready irregular cadastral
planning. These boundaries should stay visible because they define the regime in
which the current GeoJEPA-MPC evidence is credible.

## Claim-Evidence Table Updates

| claim | hardened status | manuscript wording |
|---|---|---|
| Bishan 20x16/top5 improves mean reward versus matched Paper9. | supported_descriptive | descriptive matched 5-seed reward anchor |
| Value filter improves every seed. | not_supported | mixed seed-wise outcome; wins 3/5 seeds |
| Value filter is inferentially superior. | not_supported | diagnostic_only sign-test readout; no predefined inference plan |
| Executable mask is necessary for valid rollouts. | supported_descriptive | executable-mask necessity |
| Monitor gate directly improves online reward. | not_supported | monitor gate as evidence control |
| Stage 3 50-state rows show scale-up success. | not_supported | Stage 3 boundary evidence |
| Dongxing proves robust transfer superiority. | not_supported | Dongxing/Neijiang calibration evidence |
| Irregular cadastral deployment is solved. | not_supported | deployment boundary remains open |
```

- [ ] **Step 3: Run focused tests again**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 4: Commit generated audit and patch**

```powershell
git add paper10_geojepa_mpc\experiments\results\e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md `
        paper10_geojepa_mpc\experiments\results\e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json `
        paper10_geojepa_mpc\experiments\results\e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md
git commit -m "docs: add paper10 ceus baseline hardened manuscript patch"
```

---

### Task 4: Add Preflight Guard Tests

**Files:**
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`
- Expected later implementation: `scripts/paper10/preflight_submission_checks.py`

- [ ] **Step 1: Add imports and fixture entries**

In `paper10_geojepa_mpc/tests/test_submission_preflight.py`, extend the import list from `scripts.paper10.preflight_submission_checks`:

```python
    PAPER10_CEUS_BASELINE_HARDENING_JSON,
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
    check_paper10_ceus_baseline_inference_hardening_current,
```

Add the three new paths to `MINIMAL_PREFLIGHT_FIXTURE_FILES` near the other Paper10 audit files:

```python
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENING_JSON,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
```

- [ ] **Step 2: Add failing preflight tests**

Append these tests near the other Paper10 preflight tests:

```python
def test_submission_preflight_current_repository_includes_ceus_baseline_hardening():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert "paper10_ceus_baseline_inference_hardening_current" in payload["passed_checks"]


def test_submission_preflight_minimal_fixture_reports_missing_ceus_baseline_hardening(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    (fixture / PAPER10_CEUS_BASELINE_HARDENING_JSON).unlink()

    result, payload = run_submission_preflight_json(fixture)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "paper10_ceus_baseline_inference_hardening_current" in payload["failed_checks"]
    details = check_details(payload, "paper10_ceus_baseline_inference_hardening_current")
    assert "missing Paper10 CEUS baseline hardening files" in details
    assert str(PAPER10_CEUS_BASELINE_HARDENING_JSON) in details


def test_ceus_baseline_hardening_preflight_rejects_uniform_superiority_flag(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    path = fixture / PAPER10_CEUS_BASELINE_HARDENING_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["claim_gates"]["uniform_superiority_supported"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = check_paper10_ceus_baseline_inference_hardening_current(fixture)

    assert result.name == "paper10_ceus_baseline_inference_hardening_current"
    assert result.ok is False
    assert "uniform_superiority_supported=True" in result.details


def test_ceus_baseline_hardening_preflight_rejects_inferential_superiority_flag(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    path = fixture / PAPER10_CEUS_BASELINE_HARDENING_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["claim_gates"]["inferential_superiority_supported"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = check_paper10_ceus_baseline_inference_hardening_current(fixture)

    assert result.name == "paper10_ceus_baseline_inference_hardening_current"
    assert result.ok is False
    assert "inferential_superiority_supported=True" in result.details


def test_ceus_baseline_hardening_preflight_rejects_statistical_overclaim(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    patch = fixture / PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH
    patch.write_text(
        patch.read_text(encoding="utf-8")
        + "\n\nThe result is statistically significant.\n",
        encoding="utf-8",
    )

    result = check_paper10_ceus_baseline_inference_hardening_current(fixture)

    assert result.name == "paper10_ceus_baseline_inference_hardening_current"
    assert result.ok is False
    assert "forbidden CEUS baseline hardening wording" in result.details
    assert "statistically significant" in result.details


def test_ceus_baseline_hardening_preflight_allows_negative_guardrails(tmp_path):
    fixture = copy_minimal_preflight_fixture(tmp_path)
    patch = fixture / PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH
    patch.write_text(
        patch.read_text(encoding="utf-8")
        + "\n\nDo not claim robust Bishan-to-Dongxing transfer superiority.\n",
        encoding="utf-8",
    )

    result = check_paper10_ceus_baseline_inference_hardening_current(fixture)

    assert result.name == "paper10_ceus_baseline_inference_hardening_current"
    assert result.ok is True
```

- [ ] **Step 3: Run tests to verify they fail**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: FAIL during import because the new constants/check function do not exist yet.

- [ ] **Step 4: Commit failing preflight tests**

```powershell
git add paper10_geojepa_mpc\tests\test_submission_preflight.py
git commit -m "test: guard paper10 ceus baseline hardening preflight"
```

---

### Task 5: Implement Preflight Guard and Public Doc Links

**Files:**
- Modify: `scripts/paper10/preflight_submission_checks.py`
- Modify: `README.md`
- Modify: `MANIFEST.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `DATA_AVAILABILITY.md`
- Test: `paper10_geojepa_mpc/tests/test_submission_preflight.py`

- [ ] **Step 1: Add constants and required paths**

In `scripts/paper10/preflight_submission_checks.py`, add constants near the other Paper10 audit path constants:

```python
PAPER10_CEUS_BASELINE_HARDENING_MD = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md"
)
PAPER10_CEUS_BASELINE_HARDENING_JSON = (
    RESULTS / "e0_paper10_ceus_baseline_inference_hardening_2026-07-06.json"
)
PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH = (
    RESULTS / "e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md"
)
```

Add these constants to `REQUIRED_PATHS` near the existing CEUS review optimization and long-horizon audit entries:

```python
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENING_JSON,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
```

Add these constants to `PUBLIC_SUBMISSION_DOCS` near the other Paper10 public-facing audit docs:

```python
    PAPER10_CEUS_BASELINE_HARDENING_MD,
    PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
```

- [ ] **Step 2: Add overclaim helper**

Add near the submission-readiness helper regexes:

```python
CEUS_BASELINE_NEGATIVE_GUARDRAIL = re.compile(
    r"\b("
    r"do not|does not|not supported|cannot|must not|should not|no "
    r"|without|rather than"
    r")\b",
    re.IGNORECASE,
)
CEUS_BASELINE_CLAUSE_SPLIT_PATTERN = re.compile(r"[;.!?]+")
CEUS_BASELINE_FORBIDDEN_TARGETS = (
    re.compile(r"\bstatistically significant\b", re.IGNORECASE),
    re.compile(r"\brobustly superior\b", re.IGNORECASE),
    re.compile(r"\buniformly superior\b", re.IGNORECASE),
    re.compile(r"\bdirect 50[- ]state Bishan scale[- ]up success\b", re.IGNORECASE),
    re.compile(
        r"\brobust Bishan[- ]to[- ]Dongxing transfer superiority\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bdeployment-ready\b", re.IGNORECASE),
)


def is_ceus_baseline_positive_overclaim(line: str) -> bool:
    for clause in (
        clause.strip()
        for clause in CEUS_BASELINE_CLAUSE_SPLIT_PATTERN.split(line)
    ):
        if not clause:
            continue
        if CEUS_BASELINE_NEGATIVE_GUARDRAIL.search(clause):
            continue
        if any(target.search(clause) for target in CEUS_BASELINE_FORBIDDEN_TARGETS):
            return True
    return False
```

- [ ] **Step 3: Add the check function**

Add before `CHECKS`:

```python
def check_paper10_ceus_baseline_inference_hardening_current(root: Path) -> CheckResult:
    required_files = [
        PAPER10_CEUS_BASELINE_HARDENING_MD,
        PAPER10_CEUS_BASELINE_HARDENING_JSON,
        PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH,
        README,
        MANIFEST,
        REPRODUCIBILITY,
        DATA_AVAILABILITY,
    ]
    missing = [str(path) for path in required_files if not (root / path).exists()]
    if missing:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            "missing Paper10 CEUS baseline hardening files: "
            + ", ".join(missing),
        )

    audit_text = read_text(root / PAPER10_CEUS_BASELINE_HARDENING_MD)
    patch_text = read_text(root / PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH)
    try:
        payload = json.loads(read_text(root / PAPER10_CEUS_BASELINE_HARDENING_JSON))
    except json.JSONDecodeError as exc:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: invalid JSON: {exc}",
        )

    missing_tokens = []
    for doc in (README, MANIFEST, REPRODUCIBILITY, DATA_AVAILABILITY):
        doc_text = read_text(root / doc)
        if PAPER10_CEUS_BASELINE_HARDENING_MD.name not in doc_text:
            missing_tokens.append(f"{doc}: {PAPER10_CEUS_BASELINE_HARDENING_MD.name}")

    required_audit_tokens = [
        "Paper10 CEUS baseline and inference hardening audit",
        "diagnostic_only",
        "mixed seed-wise outcome",
        "uniform superiority is not supported",
        "inferential superiority is not supported",
        "executable-mask necessity",
        "monitor gate as evidence control",
    ]
    for token in required_audit_tokens:
        if token not in audit_text:
            missing_tokens.append(f"{PAPER10_CEUS_BASELINE_HARDENING_MD}: {token}")

    required_patch_tokens = [
        "Paper10 CEUS baseline-hardened manuscript patch",
        "descriptive matched 5-seed reward anchor",
        "mixed seed-wise outcome",
        "diagnostic-only two-sided sign test gives p=1.0000",
        "executable-mask necessity",
        "monitor gate as evidence control",
        "Stage 3 boundary evidence",
        "Dongxing/Neijiang calibration evidence",
    ]
    for token in required_patch_tokens:
        if token not in patch_text:
            missing_tokens.append(
                f"{PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH}: {token}"
            )

    expected_values = {
        ("status",): "source-derived CEUS baseline and inference hardening audit",
        ("source_boundary", "reran_training"): False,
        ("source_boundary", "reran_rollouts"): False,
        ("source_boundary", "post_hoc_tuning_allowed"): False,
        ("paired_reward_summary", "n_seeds"): 5,
        ("paired_reward_summary", "candidate_win_count"): 3,
        ("paired_reward_summary", "candidate_loss_count"): 2,
        ("paired_reward_summary", "uniform_superiority_supported"): False,
        ("paired_reward_summary", "inferential_superiority_supported"): False,
        ("paired_reward_summary", "descriptive_mean_reward_anchor_supported"): True,
        ("paired_reward_summary", "sign_test", "classification"): "diagnostic_only",
        ("claim_gates", "descriptive_mean_reward_anchor_supported"): True,
        ("claim_gates", "uniform_superiority_supported"): False,
        ("claim_gates", "inferential_superiority_supported"): False,
        ("claim_gates", "stage3_50state_scaleup_supported"): False,
        ("claim_gates", "robust_transfer_superiority_supported"): False,
        ("claim_gates", "irregular_cadastral_deployment_supported"): False,
    }
    for path_keys, expected in expected_values.items():
        value = payload
        for key in path_keys:
            if not isinstance(value, dict) or key not in value:
                missing_tokens.append(
                    f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: {'.'.join(path_keys)}"
                )
                value = None
                break
            value = value[key]
        if value != expected:
            missing_tokens.append(
                f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: "
                f"{'.'.join(path_keys)}={value}"
            )

    p_value = (
        payload.get("paired_reward_summary", {})
        .get("sign_test", {})
        .get("p_value")
    )
    if not isinstance(p_value, (float, int)) or abs(float(p_value) - 1.0) > 1e-8:
        missing_tokens.append(
            f"{PAPER10_CEUS_BASELINE_HARDENING_JSON}: sign_test.p_value={p_value}"
        )

    for rel_path, text in (
        (PAPER10_CEUS_BASELINE_HARDENING_MD, audit_text),
        (PAPER10_CEUS_BASELINE_HARDENED_MANUSCRIPT_PATCH, patch_text),
    ):
        for line_no, line in enumerate(text.splitlines(), start=1):
            if is_ceus_baseline_positive_overclaim(line):
                missing_tokens.append(
                    f"{rel_path}:{line_no}: forbidden CEUS baseline hardening wording: {line.strip()}"
                )

    if missing_tokens:
        return CheckResult(
            "paper10_ceus_baseline_inference_hardening_current",
            False,
            "Paper10 CEUS baseline hardening gaps: " + " | ".join(missing_tokens),
        )
    return CheckResult(
        "paper10_ceus_baseline_inference_hardening_current",
        True,
        "Paper10 CEUS baseline hardening audit and manuscript patch are current",
    )
```

- [ ] **Step 4: Register the check**

Add `check_paper10_ceus_baseline_inference_hardening_current` to `CHECKS` after `check_paper10_real_env_longhorizon_confirmatory_audit_current`.

- [ ] **Step 5: Add public document links**

In `README.md`, add near the current CEUS review optimization register paragraph:

```markdown
Use
`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
as the current CEUS baseline and inference hardening audit. It fixes matched
Paper9 versus value-filter wording, keeps the 5-seed result descriptive and
mixed seed-wise, and prevents uniform or inferential superiority claims.
```

In `REPRODUCIBILITY.md`, add the same file to the verification/source-derived audit list with:

```markdown
- `e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`: source-derived
  CEUS baseline and inference wording audit; no rollout or training is rerun.
```

In `MANIFEST.md`, add to the included results list:

```markdown
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`:
  source-derived CEUS baseline and inference hardening audit that locks mixed
  seed-wise wording, diagnostic-only sign-test interpretation, secondary-metric
  tradeoffs and no-overclaim gates for the next CEUS manuscript pass.
- `paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_hardened_manuscript_patch_2026-07-06.md`:
  bounded manuscript patch for the next CEUS assembly pass.
```

In `DATA_AVAILABILITY.md`, add near the manuscript-facing draft references:

```markdown
For the current CEUS baseline and inference wording boundary, including the
descriptive matched 5-seed reward anchor and diagnostic-only sign-test readout,
see:

`paper10_geojepa_mpc/experiments/results/e0_paper10_ceus_baseline_inference_hardening_2026-07-06.md`
```

- [ ] **Step 6: Run focused preflight tests**

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 7: Commit preflight guard and docs**

```powershell
git add scripts\paper10\preflight_submission_checks.py `
        paper10_geojepa_mpc\tests\test_submission_preflight.py `
        README.md MANIFEST.md REPRODUCIBILITY.md DATA_AVAILABILITY.md
git commit -m "test: guard paper10 ceus baseline hardening preflight"
```

---

### Task 6: Final Verification

**Files:**
- No new files.
- Verify all changed files.

- [ ] **Step 1: Run hardening tests**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_ceus_baseline_inference_hardening.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 2: Run preflight tests**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 3: Run repository preflight**

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected output includes:

```text
Paper10 preflight: PASS
[ok] paper10_ceus_baseline_inference_hardening_current: Paper10 CEUS baseline hardening audit and manuscript patch are current
```

- [ ] **Step 4: Run full suite**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Expected: PASS.

- [ ] **Step 5: Inspect git status**

```powershell
git status --short --branch
```

Expected: only the pre-existing untracked `2503.05774v1.pdf` remains.

