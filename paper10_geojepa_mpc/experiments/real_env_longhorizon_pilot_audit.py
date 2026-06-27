import argparse
import json
from pathlib import Path
from statistics import mean


DATE = "2026-06-27"


def _float(value) -> float:
    return float(value)


def _delta(candidate: float, baseline: float) -> float:
    return round(float(candidate) - float(baseline), 12)


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _final_metrics(payload: dict) -> dict:
    steps = payload.get("steps", [])
    final_step = steps[-1] if steps else {}
    return {
        "slope_change_pct": _float(final_step.get("slope_change_pct", 0.0)),
        "cont_change": _float(final_step.get("cont_change", 0.0)),
        "baimu_area_change_ha": _float(
            final_step.get("baimu_area_change_ha", 0.0)
        ),
    }


def _action_trace(payload: dict) -> list[int]:
    return [int(step.get("action", -1)) for step in payload.get("steps", [])]


def _reward_trace(payload: dict) -> list[float]:
    return [_float(step.get("reward", 0.0)) for step in payload.get("steps", [])]


def _run_row(name: str, source: str, payload: dict) -> dict:
    rewards = _reward_trace(payload)
    steps = payload.get("steps", [])
    select_times = [
        _float(step.get("select_time_sec", 0.0))
        for step in steps
        if "select_time_sec" in step
    ]
    executable_valid = [
        int(step.get("n_executable_valid", step.get("n_valid", 0)))
        for step in steps
    ]
    return {
        "name": name,
        "source": source,
        "checkpoint": payload.get("checkpoint"),
        "prepared_dir": payload.get("prepared_dir"),
        "env_source": payload.get("env_source", "paper9"),
        "seed": int(payload.get("seed", 0)),
        "horizon": int(payload.get("horizon", 0)),
        "top_k": int(payload.get("top_k", 0)),
        "rollout_steps": int(payload.get("rollout_steps", len(steps))),
        "steps_run": int(payload.get("steps_run", len(steps))),
        "mask_mode": payload.get("mask_mode"),
        "selector": payload.get("selector"),
        "candidate_score_mode": payload.get("candidate_score_mode"),
        "candidate_value_weight": payload.get("candidate_value_weight"),
        "total_reward": _float(payload.get("total_reward", sum(rewards))),
        "elapsed_sec": _float(payload.get("elapsed_sec", 0.0)),
        "terminated": bool(payload.get("terminated", False)),
        "truncated": bool(payload.get("truncated", False)),
        "positive_reward_steps": sum(1 for reward in rewards if reward > 0.0),
        "negative_reward_steps": sum(1 for reward in rewards if reward < 0.0),
        "min_executable_valid": min(executable_valid) if executable_valid else 0,
        "mean_select_time_sec": _mean(select_times),
        "final_metrics": _final_metrics(payload),
        "action_trace": _action_trace(payload),
    }


def _first_action_divergence(
    baseline_actions: list[int], candidate_actions: list[int]
) -> int | None:
    for index, (baseline_action, candidate_action) in enumerate(
        zip(baseline_actions, candidate_actions), start=1
    ):
        if baseline_action != candidate_action:
            return index
    if len(baseline_actions) != len(candidate_actions):
        return min(len(baseline_actions), len(candidate_actions)) + 1
    return None


def _shared_prefix_steps(
    baseline_actions: list[int], candidate_actions: list[int]
) -> int:
    count = 0
    for baseline_action, candidate_action in zip(baseline_actions, candidate_actions):
        if baseline_action != candidate_action:
            break
        count += 1
    return count


def _comparison(baseline: dict, candidate: dict) -> dict:
    baseline_actions = baseline["action_trace"]
    candidate_actions = candidate["action_trace"]
    final_metric_deltas = {
        key: _delta(
            candidate["final_metrics"].get(key, 0.0),
            baseline["final_metrics"].get(key, 0.0),
        )
        for key in ("slope_change_pct", "cont_change", "baimu_area_change_ha")
    }
    reward_delta = _delta(candidate["total_reward"], baseline["total_reward"])
    return {
        "total_reward_delta_candidate_minus_baseline": reward_delta,
        "candidate_reward_greater": reward_delta > 0.0,
        "final_metric_deltas": final_metric_deltas,
        "first_action_divergence_step": _first_action_divergence(
            baseline_actions, candidate_actions
        ),
        "shared_prefix_steps": _shared_prefix_steps(
            baseline_actions, candidate_actions
        ),
        "position_action_overlap_count": sum(
            1
            for baseline_action, candidate_action in zip(
                baseline_actions, candidate_actions
            )
            if baseline_action == candidate_action
        ),
        "unique_action_overlap_count": len(
            set(baseline_actions).intersection(candidate_actions)
        ),
        "exact_action_trace_equal": baseline_actions == candidate_actions,
    }


def build_longhorizon_pilot_audit(
    *,
    baseline_name: str,
    baseline_source: str,
    baseline_payload: dict,
    candidate_name: str,
    candidate_source: str,
    candidate_payload: dict,
    date: str = DATE,
) -> dict:
    baseline = _run_row(baseline_name, baseline_source, baseline_payload)
    candidate = _run_row(candidate_name, candidate_source, candidate_payload)
    comparison = _comparison(baseline, candidate)
    both_complete = (
        baseline["terminated"]
        and candidate["terminated"]
        and not baseline["truncated"]
        and not candidate["truncated"]
    )
    return {
        "date": date,
        "status": "locked seed0 long-horizon pilot audit",
        "source_boundary": {
            "reran_rollouts": False,
            "source": "tracked audit generated from locked raw rollout JSON outputs",
        },
        "runs": [baseline, candidate],
        "comparison": comparison,
        "evidence_boundary": {
            "supports_execution_chain": both_complete,
            "planning_quality_result": False,
            "final_performance_evidence": False,
            "single_seed_pilot_only": True,
            "post_hoc_tuning_allowed": False,
            "value_filter_superiority_supported": False,
            "confirmatory_next_step": "matched seeds 0-4",
            "reason": (
                "This audit is a locked seed0 pilot. A final planning-quality "
                "claim requires the same matched protocol on seeds 0-4."
            ),
        },
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def markdown_report(payload: dict) -> str:
    baseline, candidate = payload["runs"]
    comparison = payload["comparison"]
    deltas = comparison["final_metric_deltas"]
    if comparison["candidate_reward_greater"]:
        reward_sentence = (
            "The value-filter candidate is higher on this seed0 pilot, but "
            "value-filter superiority is not supported until matched seeds `0-4` "
            "are complete."
        )
    else:
        reward_sentence = (
            "The value-filter candidate did not beat matched Paper9 on this "
            "seed0 pilot; value-filter superiority is not supported."
        )

    lines = [
        "# Paper10 real-data long-horizon seed0 pilot audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: locked seed0 pilot; not final planning-quality evidence.",
        "",
        "## Boundary",
        "",
        reward_sentence,
        "",
        "The next confirmatory step remains the same matched protocol on matched seeds `0-4`. Do not tune thresholds, top_k, horizon, or candidate weight to rescue this seed0 result.",
        "",
        "## Sources",
        "",
        f"- `{baseline['name']}`: `{baseline['source']}`",
        f"- `{candidate['name']}`: `{candidate['source']}`",
        "",
        "## Run Outcomes",
        "",
        "| metric | matched Paper9 | value-filter | delta candidate-baseline |",
        "|---|---:|---:|---:|",
        "| total reward | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["total_reward"]),
            cand=_fmt(candidate["total_reward"]),
            delta=_fmt(
                comparison["total_reward_delta_candidate_minus_baseline"]
            ),
        ),
        "| final slope change pct | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["final_metrics"]["slope_change_pct"]),
            cand=_fmt(candidate["final_metrics"]["slope_change_pct"]),
            delta=_fmt(deltas["slope_change_pct"]),
        ),
        "| final contiguity change | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["final_metrics"]["cont_change"]),
            cand=_fmt(candidate["final_metrics"]["cont_change"]),
            delta=_fmt(deltas["cont_change"]),
        ),
        "| final baimu area change ha | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["final_metrics"]["baimu_area_change_ha"]),
            cand=_fmt(candidate["final_metrics"]["baimu_area_change_ha"]),
            delta=_fmt(deltas["baimu_area_change_ha"]),
        ),
        "| negative reward steps | {base} | {cand} | {delta} |".format(
            base=baseline["negative_reward_steps"],
            cand=candidate["negative_reward_steps"],
            delta=candidate["negative_reward_steps"]
            - baseline["negative_reward_steps"],
        ),
        "",
        "## Trace Diagnostics",
        "",
        "| diagnostic | value |",
        "|---|---:|",
        f"| first action divergence step | {comparison['first_action_divergence_step']} |",
        f"| shared prefix steps | {comparison['shared_prefix_steps']} |",
        f"| position action overlap count | {comparison['position_action_overlap_count']} |",
        f"| unique action overlap count | {comparison['unique_action_overlap_count']} |",
        "",
        "## Evidence Boundary",
        "",
        "- Single seed only; descriptive pilot evidence only.",
        "- No inferential statistics or significance claims are introduced.",
        "- No broad scale-up or cross-region superiority claim is supported.",
    ]
    return "\n".join(lines) + "\n"


def write_longhorizon_pilot_audit(
    *,
    baseline_name: str,
    baseline_json: str | Path,
    candidate_name: str,
    candidate_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict:
    baseline_path = Path(baseline_json)
    candidate_path = Path(candidate_json)
    payload = build_longhorizon_pilot_audit(
        baseline_name=baseline_name,
        baseline_source=str(baseline_path),
        baseline_payload=json.loads(baseline_path.read_text(encoding="utf-8")),
        candidate_name=candidate_name,
        candidate_source=str(candidate_path),
        candidate_payload=json.loads(candidate_path.read_text(encoding="utf-8")),
        date=date,
    )
    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path = Path(output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-name", required=True)
    parser.add_argument("--baseline-json", required=True)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--candidate-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_longhorizon_pilot_audit(
        baseline_name=args.baseline_name,
        baseline_json=args.baseline_json,
        candidate_name=args.candidate_name,
        candidate_json=args.candidate_json,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
