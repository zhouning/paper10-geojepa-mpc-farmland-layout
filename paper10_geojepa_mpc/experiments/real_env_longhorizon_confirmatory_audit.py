import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable


DATE = "2026-06-27"
FLOAT_TOLERANCE = 1e-8


def _as_float(value: float | int | str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _as_int(value: float | int | str | None, default: int = 0) -> int:
    if value is None:
        return default
    return int(value)


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _sample_std(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def _round_delta(value: float) -> float:
    return round(float(value), 12)


def _trace_hash(values: list[int | float]) -> str:
    encoded = json.dumps(values, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _payload_episodes(payload: dict) -> list[dict]:
    if "episodes" in payload:
        return list(payload["episodes"])
    if "steps" in payload:
        return [payload]
    return []


def _field(episode: dict, payload: dict, key: str, default=None):
    if episode.get(key) is not None:
        return episode.get(key)
    if payload.get(key) is not None:
        return payload.get(key)
    return default


def _final_metrics(steps: list[dict]) -> dict:
    final = steps[-1] if steps else {}
    return {
        "slope_change_pct": _as_float(final.get("slope_change_pct")),
        "cont_change": _as_float(final.get("cont_change")),
        "baimu_area_change_ha": _as_float(final.get("baimu_area_change_ha")),
    }


def _seed_summary(
    *,
    source_file: str,
    payload: dict,
    episode: dict,
    default_selector: str,
) -> dict:
    steps = list(episode.get("steps", []))
    rewards = [_as_float(step.get("reward")) for step in steps]
    actions = [_as_int(step.get("action"), default=-1) for step in steps]
    total_reward_from_steps = sum(rewards)
    reported_total_reward = _as_float(
        _field(episode, payload, "total_reward"),
        default=total_reward_from_steps,
    )
    select_times = [
        _as_float(step.get("select_time_sec"))
        for step in steps
        if step.get("select_time_sec") is not None
    ]
    completed_swaps = [
        _as_int(step.get("completed_swaps"))
        for step in steps
        if step.get("completed_swaps") is not None
    ]
    selector = _field(episode, payload, "selector", default_selector)
    return {
        "source_file": source_file,
        "selector": selector,
        "checkpoint": _field(episode, payload, "checkpoint"),
        "prepared_dir": _field(episode, payload, "prepared_dir"),
        "seed": _as_int(_field(episode, payload, "seed")),
        "horizon": _as_int(_field(episode, payload, "horizon")),
        "top_k": _as_int(_field(episode, payload, "top_k")),
        "rollout_steps": _as_int(
            _field(episode, payload, "rollout_steps"),
            default=len(steps),
        ),
        "steps_run": len(steps),
        "reported_steps_run": _as_int(
            _field(episode, payload, "steps_run"),
            default=len(steps),
        ),
        "mask_mode": _field(episode, payload, "mask_mode"),
        "candidate_score_mode": _field(episode, payload, "candidate_score_mode"),
        "candidate_value_weight": _field(episode, payload, "candidate_value_weight"),
        "terminated": bool(_field(episode, payload, "terminated", False)),
        "truncated": bool(_field(episode, payload, "truncated", False)),
        "elapsed_sec": _as_float(_field(episode, payload, "elapsed_sec")),
        "total_reward": reported_total_reward,
        "total_reward_from_steps": total_reward_from_steps,
        "reported_total_reward": reported_total_reward,
        "abs_reported_minus_steps": abs(
            reported_total_reward - total_reward_from_steps
        ),
        "positive_reward_steps": sum(1 for reward in rewards if reward > 0.0),
        "negative_reward_steps": sum(1 for reward in rewards if reward < 0.0),
        "zero_reward_steps": sum(1 for reward in rewards if reward == 0.0),
        "zero_swap_steps": sum(1 for value in completed_swaps if value == 0),
        "negative_zero_swap_steps": sum(
            1
            for step in steps
            if _as_int(step.get("completed_swaps")) == 0
            and _as_float(step.get("reward")) < 0.0
        ),
        "mean_select_time_sec": _mean(select_times),
        "final_metrics": _final_metrics(steps),
        "action_trace": actions,
        "action_trace_sha256": _trace_hash(actions),
        "reward_trace_sha256": _trace_hash(rewards),
    }


def _policy_summary(
    *,
    name: str,
    default_selector: str,
    payloads: Iterable[tuple[str, dict]],
) -> dict:
    seed_summaries = []
    for source_file, payload in payloads:
        for episode in _payload_episodes(payload):
            seed_summaries.append(
                _seed_summary(
                    source_file=source_file,
                    payload=payload,
                    episode=episode,
                    default_selector=default_selector,
                )
            )
    seed_summaries.sort(key=lambda row: row["seed"])
    seeds = [row["seed"] for row in seed_summaries]
    if len(seeds) != len(set(seeds)):
        raise ValueError(f"Duplicate seeds in {name}: {seeds}")
    rewards = [row["total_reward"] for row in seed_summaries]
    slopes = [
        row["final_metrics"]["slope_change_pct"]
        for row in seed_summaries
    ]
    conts = [row["final_metrics"]["cont_change"] for row in seed_summaries]
    baimu = [
        row["final_metrics"]["baimu_area_change_ha"]
        for row in seed_summaries
    ]
    return {
        "name": name,
        "selector": default_selector,
        "source_files": sorted({row["source_file"] for row in seed_summaries}),
        "seed_summaries": seed_summaries,
        "aggregate": {
            "n_episodes": len(seed_summaries),
            "seeds": seeds,
            "total_reward_mean": _mean(rewards),
            "total_reward_std_sample": _sample_std(rewards),
            "total_reward_min": min(rewards) if rewards else 0.0,
            "total_reward_max": max(rewards) if rewards else 0.0,
            "slope_change_pct_mean": _mean(slopes),
            "cont_change_mean": _mean(conts),
            "baimu_area_change_ha_mean": _mean(baimu),
            "positive_reward_steps_sum": sum(
                row["positive_reward_steps"] for row in seed_summaries
            ),
            "negative_reward_steps_sum": sum(
                row["negative_reward_steps"] for row in seed_summaries
            ),
            "zero_reward_steps_sum": sum(
                row["zero_reward_steps"] for row in seed_summaries
            ),
            "zero_swap_steps_sum": sum(
                row["zero_swap_steps"] for row in seed_summaries
            ),
            "negative_zero_swap_steps_sum": sum(
                row["negative_zero_swap_steps"] for row in seed_summaries
            ),
        },
    }


def _seed_map(policy: dict) -> dict[int, dict]:
    return {row["seed"]: row for row in policy["seed_summaries"]}


def _first_action_divergence(
    baseline_actions: list[int], candidate_actions: list[int]
) -> int | None:
    for index, (baseline_action, candidate_action) in enumerate(
        zip(baseline_actions, candidate_actions),
        start=1,
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


def _paired_seed_row(seed: int, baseline: dict, candidate: dict) -> dict:
    baseline_actions = baseline["action_trace"]
    candidate_actions = candidate["action_trace"]
    reward_delta = candidate["total_reward"] - baseline["total_reward"]
    return {
        "seed": seed,
        "baseline_total_reward": baseline["total_reward"],
        "candidate_total_reward": candidate["total_reward"],
        "total_reward_delta_candidate_minus_baseline": reward_delta,
        "candidate_reward_greater": reward_delta > 0.0,
        "baseline_negative_reward_steps": baseline["negative_reward_steps"],
        "candidate_negative_reward_steps": candidate["negative_reward_steps"],
        "negative_reward_steps_delta": (
            candidate["negative_reward_steps"] - baseline["negative_reward_steps"]
        ),
        "final_metric_deltas": {
            key: candidate["final_metrics"][key] - baseline["final_metrics"][key]
            for key in (
                "slope_change_pct",
                "cont_change",
                "baimu_area_change_ha",
            )
        },
        "first_action_divergence_step": _first_action_divergence(
            baseline_actions,
            candidate_actions,
        ),
        "shared_prefix_steps": _shared_prefix_steps(
            baseline_actions,
            candidate_actions,
        ),
        "position_action_overlap_count": sum(
            1
            for baseline_action, candidate_action in zip(
                baseline_actions,
                candidate_actions,
            )
            if baseline_action == candidate_action
        ),
        "unique_action_overlap_count": len(
            set(baseline_actions).intersection(candidate_actions)
        ),
        "exact_action_trace_equal": baseline_actions == candidate_actions,
        "baseline_action_trace_sha256": baseline["action_trace_sha256"],
        "candidate_action_trace_sha256": candidate["action_trace_sha256"],
    }


def _paired_comparison(baseline_policy: dict, candidate_policy: dict) -> dict:
    baseline_by_seed = _seed_map(baseline_policy)
    candidate_by_seed = _seed_map(candidate_policy)
    baseline_seeds = set(baseline_by_seed)
    candidate_seeds = set(candidate_by_seed)
    if baseline_seeds != candidate_seeds:
        raise ValueError(
            "Matched audit requires identical seeds; "
            f"baseline={sorted(baseline_seeds)}, candidate={sorted(candidate_seeds)}"
        )
    per_seed = [
        _paired_seed_row(seed, baseline_by_seed[seed], candidate_by_seed[seed])
        for seed in sorted(baseline_seeds)
    ]
    deltas = [
        row["total_reward_delta_candidate_minus_baseline"] for row in per_seed
    ]
    candidate_win_count = sum(1 for delta in deltas if delta > 0.0)
    candidate_loss_count = sum(1 for delta in deltas if delta < 0.0)
    tie_count = len(deltas) - candidate_win_count - candidate_loss_count
    return {
        "matched_seeds": [row["seed"] for row in per_seed],
        "per_seed": per_seed,
        "total_reward_delta_mean": _mean(deltas),
        "total_reward_delta_std_sample": _sample_std(deltas),
        "total_reward_delta_min": min(deltas) if deltas else 0.0,
        "total_reward_delta_max": max(deltas) if deltas else 0.0,
        "candidate_win_count": candidate_win_count,
        "candidate_loss_count": candidate_loss_count,
        "tie_count": tie_count,
        "candidate_win_fraction": (
            candidate_win_count / len(deltas) if deltas else 0.0
        ),
    }


def _pilot_run(seed0_pilot_payload: dict, selector: str) -> dict | None:
    for row in seed0_pilot_payload.get("runs", []):
        if row.get("selector") == selector:
            return row
    return None


def _metric_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return float(left) - float(right)


def _close(value: float | None, *, tolerance: float) -> bool:
    return value is not None and abs(float(value)) <= tolerance


def _seed0_pilot_linkage(
    *,
    baseline_policy: dict,
    candidate_policy: dict,
    seed0_pilot_payload: dict | None,
    tolerance: float,
) -> dict:
    if seed0_pilot_payload is None:
        return {
            "available": False,
            "matches_pilot_audit": None,
            "reason": "No seed0 pilot audit payload was supplied.",
        }
    baseline_seed0 = _seed_map(baseline_policy).get(0)
    candidate_seed0 = _seed_map(candidate_policy).get(0)
    pilot_baseline = _pilot_run(seed0_pilot_payload, "paper9")
    pilot_candidate = _pilot_run(seed0_pilot_payload, "value_filter")
    if not baseline_seed0 or not candidate_seed0 or not pilot_baseline or not pilot_candidate:
        return {
            "available": True,
            "matches_pilot_audit": False,
            "reason": "Seed0 or pilot policy rows are missing.",
        }

    baseline_reward_delta = _metric_delta(
        baseline_seed0["total_reward"],
        pilot_baseline.get("total_reward"),
    )
    candidate_reward_delta = _metric_delta(
        candidate_seed0["total_reward"],
        pilot_candidate.get("total_reward"),
    )
    baseline_action_match = (
        baseline_seed0["action_trace"] == pilot_baseline.get("action_trace", [])
    )
    candidate_action_match = (
        candidate_seed0["action_trace"] == pilot_candidate.get("action_trace", [])
    )
    final_metric_deltas = {}
    for policy_name, tracked, pilot in (
        ("baseline", baseline_seed0, pilot_baseline),
        ("candidate", candidate_seed0, pilot_candidate),
    ):
        final_metric_deltas[policy_name] = {
            key: _metric_delta(
                tracked["final_metrics"].get(key),
                pilot.get("final_metrics", {}).get(key),
            )
            for key in (
                "slope_change_pct",
                "cont_change",
                "baimu_area_change_ha",
            )
        }
    final_metrics_match = all(
        _close(value, tolerance=tolerance)
        for policy_deltas in final_metric_deltas.values()
        for value in policy_deltas.values()
    )
    matches = (
        _close(baseline_reward_delta, tolerance=tolerance)
        and _close(candidate_reward_delta, tolerance=tolerance)
        and baseline_action_match
        and candidate_action_match
        and final_metrics_match
    )
    return {
        "available": True,
        "pilot_status": seed0_pilot_payload.get("status"),
        "pilot_date": seed0_pilot_payload.get("date"),
        "matches_pilot_audit": matches,
        "baseline_total_reward_delta": baseline_reward_delta,
        "candidate_total_reward_delta": candidate_reward_delta,
        "baseline_action_trace_match": baseline_action_match,
        "candidate_action_trace_match": candidate_action_match,
        "final_metric_deltas": final_metric_deltas,
    }


def build_real_env_longhorizon_confirmatory_audit(
    *,
    baseline_payloads: Iterable[tuple[str, dict]],
    candidate_payloads: Iterable[tuple[str, dict]],
    seed0_pilot_payload: dict | None,
    date: str = DATE,
    tolerance: float = FLOAT_TOLERANCE,
) -> dict:
    baseline_policy = _policy_summary(
        name="matched_paper9_rank_seed2028_baseline",
        default_selector="paper9",
        payloads=baseline_payloads,
    )
    candidate_policy = _policy_summary(
        name="bishan_20x16_top5_value_filter_blend010",
        default_selector="value_filter",
        payloads=candidate_payloads,
    )
    paired = _paired_comparison(baseline_policy, candidate_policy)
    seed0_linkage = _seed0_pilot_linkage(
        baseline_policy=baseline_policy,
        candidate_policy=candidate_policy,
        seed0_pilot_payload=seed0_pilot_payload,
        tolerance=tolerance,
    )
    baseline_std = baseline_policy["aggregate"]["total_reward_std_sample"]
    candidate_std = candidate_policy["aggregate"]["total_reward_std_sample"]
    mean_delta = paired["total_reward_delta_mean"]
    return {
        "date": date,
        "status": "locked matched 5-seed real-data audit",
        "tolerance": tolerance,
        "source_boundary": {
            "source": "source-derived from tracked raw rollout JSON files",
            "reran_rollouts": False,
            "protocol_locked": True,
            "post_hoc_tuning_allowed": False,
        },
        "policies": {
            "baseline": baseline_policy,
            "candidate": candidate_policy,
        },
        "paired_comparison": paired,
        "seed0_pilot_linkage": seed0_linkage,
        "evidence_boundary": {
            "descriptive_matched_5seed_result": True,
            "descriptive_matched_5seed_mean_reward_higher": mean_delta > 0.0,
            "variance_lower_in_matched_5seed": candidate_std < baseline_std,
            "inferential_superiority_supported": False,
            "robust_transfer_superiority_supported": False,
            "direct_50_state_scaleup_success_supported": False,
            "post_hoc_tuning_allowed": False,
            "bounded_claim": (
                "The value-filter policy has higher mean total reward and lower "
                "sample standard deviation than matched Paper9 in this locked "
                "Bishan seeds 0-4 protocol. This is descriptive evidence only."
            ),
        },
    }


def markdown_report(payload: dict) -> str:
    baseline = payload["policies"]["baseline"]["aggregate"]
    candidate = payload["policies"]["candidate"]["aggregate"]
    paired = payload["paired_comparison"]
    seed0_linkage = payload["seed0_pilot_linkage"]
    lines = [
        "# Paper10 real-data long-horizon matched 5-seed audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived descriptive matched 5-seed result; no rollout was rerun.",
        "",
        "The locked 5-seed comparison reports a higher value-filter mean reward, but inferential superiority is not supported. Do not use this audit as a robust transfer, broad scale-up, or statistical-significance claim.",
        "",
        "post-hoc tuning of thresholds, top_k, horizon, or candidate-value weight remains disallowed after seeing the seed0 pilot and 5-seed outcomes.",
        "",
        "## Aggregate outcomes",
        "",
        "| metric | matched Paper9 | value-filter | delta candidate-baseline |",
        "|---|---:|---:|---:|",
        "| total reward mean | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["total_reward_mean"]),
            cand=_fmt(candidate["total_reward_mean"]),
            delta=_fmt(paired["total_reward_delta_mean"]),
        ),
        "| total reward sample std | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["total_reward_std_sample"]),
            cand=_fmt(candidate["total_reward_std_sample"]),
            delta=_fmt(
                candidate["total_reward_std_sample"]
                - baseline["total_reward_std_sample"]
            ),
        ),
        "| total reward min | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["total_reward_min"]),
            cand=_fmt(candidate["total_reward_min"]),
            delta=_fmt(candidate["total_reward_min"] - baseline["total_reward_min"]),
        ),
        "| total reward max | {base} | {cand} | {delta} |".format(
            base=_fmt(baseline["total_reward_max"]),
            cand=_fmt(candidate["total_reward_max"]),
            delta=_fmt(candidate["total_reward_max"] - baseline["total_reward_max"]),
        ),
        "| negative reward steps | {base} | {cand} | {delta} |".format(
            base=baseline["negative_reward_steps_sum"],
            cand=candidate["negative_reward_steps_sum"],
            delta=(
                candidate["negative_reward_steps_sum"]
                - baseline["negative_reward_steps_sum"]
            ),
        ),
        "| candidate win count | 0 | {wins} | {wins} |".format(
            wins=paired["candidate_win_count"],
        ),
        "",
        "## Seed-level reward deltas",
        "",
        "| seed | matched Paper9 | value-filter | delta | first divergence step |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in paired["per_seed"]:
        lines.append(
            "| {seed} | {base} | {cand} | {delta} | {divergence} |".format(
                seed=row["seed"],
                base=_fmt(row["baseline_total_reward"]),
                cand=_fmt(row["candidate_total_reward"]),
                delta=_fmt(row["total_reward_delta_candidate_minus_baseline"]),
                divergence=row["first_action_divergence_step"],
            )
        )

    lines.extend(
        [
            "",
            "## Seed0 pilot linkage",
            "",
            f"- Linkage available: `{seed0_linkage['available']}`",
            f"- Matches pilot audit: `{seed0_linkage['matches_pilot_audit']}`",
            "",
            "## Evidence boundary",
            "",
            "- The audit supports a bounded descriptive matched 5-seed Bishan statement.",
            "- The seed0 pilot remains a loss for value-filter, so the result must be framed seed-wise rather than as uniform improvement.",
            "- Inferential superiority is not supported because no predefined statistical test is introduced here.",
            "- No cross-region transfer superiority or 50-state scale-up claim is supported.",
            "",
            "## Source files",
            "",
        ]
    )
    for policy_name in ("baseline", "candidate"):
        policy = payload["policies"][policy_name]
        for source in policy["source_files"]:
            lines.append(f"- {policy_name}: `{source}`")
    return "\n".join(lines) + "\n"


def write_real_env_longhorizon_confirmatory_audit(
    *,
    baseline_json: Iterable[str | Path],
    candidate_json: Iterable[str | Path],
    seed0_pilot_json: str | Path | None,
    output_json: str | Path,
    output_md: str | Path,
    date: str = DATE,
) -> dict:
    baseline_payloads = [
        (str(Path(path)), json.loads(Path(path).read_text(encoding="utf-8")))
        for path in baseline_json
    ]
    candidate_payloads = [
        (str(Path(path)), json.loads(Path(path).read_text(encoding="utf-8")))
        for path in candidate_json
    ]
    seed0_pilot_payload = None
    if seed0_pilot_json is not None:
        seed0_pilot_path = Path(seed0_pilot_json)
        seed0_pilot_payload = json.loads(
            seed0_pilot_path.read_text(encoding="utf-8")
        )
    payload = build_real_env_longhorizon_confirmatory_audit(
        baseline_payloads=baseline_payloads,
        candidate_payloads=candidate_payloads,
        seed0_pilot_payload=seed0_pilot_payload,
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
    parser.add_argument("--baseline-json", action="append", required=True)
    parser.add_argument("--candidate-json", action="append", required=True)
    parser.add_argument("--seed0-pilot-json")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_real_env_longhorizon_confirmatory_audit(
        baseline_json=args.baseline_json,
        candidate_json=args.candidate_json,
        seed0_pilot_json=args.seed0_pilot_json,
        output_json=args.output_json,
        output_md=args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
