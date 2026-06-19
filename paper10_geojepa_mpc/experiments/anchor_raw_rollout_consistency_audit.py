import argparse
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable


DATE = "2026-06-19"
FLOAT_TOLERANCE = 1e-8


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def _as_float(value: float | int | str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _as_int(value: float | int | str | None, default: int = 0) -> int:
    if value is None:
        return default
    return int(value)


def _episodes_from_raw(payload: dict) -> list[dict]:
    if "episodes" in payload:
        return list(payload["episodes"])
    if "steps" in payload:
        return [payload]
    return []


def _final_metrics_from_steps(steps: list[dict]) -> dict:
    if not steps:
        return {
            "slope_change_pct": 0.0,
            "cont_change": 0.0,
            "baimu_area_change_ha": 0.0,
        }
    final = steps[-1]
    return {
        "slope_change_pct": _as_float(final.get("slope_change_pct")),
        "cont_change": _as_float(final.get("cont_change")),
        "baimu_area_change_ha": _as_float(final.get("baimu_area_change_ha")),
    }


def _raw_seed_summary(source_file: str, episode: dict) -> dict:
    steps = list(episode.get("steps", []))
    rewards = [_as_float(step.get("reward")) for step in steps]
    total_reward_from_steps = sum(rewards)
    reported_total_reward = _as_float(
        episode.get("total_reward"),
        default=total_reward_from_steps,
    )
    completed_swaps = [
        _as_int(step.get("completed_swaps"))
        for step in steps
        if step.get("completed_swaps") is not None
    ]
    return {
        "source_file": source_file,
        "seed": _as_int(episode.get("seed")),
        "horizon": _as_int(episode.get("horizon")),
        "top_k": _as_int(episode.get("top_k")),
        "steps_run": len(steps),
        "reported_steps_run": _as_int(episode.get("steps_run"), default=len(steps)),
        "elapsed_sec": _as_float(episode.get("elapsed_sec")),
        "total_reward_from_steps": total_reward_from_steps,
        "reported_total_reward": reported_total_reward,
        "abs_reported_minus_steps": abs(reported_total_reward - total_reward_from_steps),
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
        "final_metrics_from_steps": _final_metrics_from_steps(steps),
    }


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _sample_std(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _raw_aggregate(raw_seed_summaries: list[dict]) -> dict:
    rewards = [row["total_reward_from_steps"] for row in raw_seed_summaries]
    slopes = [
        row["final_metrics_from_steps"]["slope_change_pct"]
        for row in raw_seed_summaries
    ]
    conts = [
        row["final_metrics_from_steps"]["cont_change"]
        for row in raw_seed_summaries
    ]
    baimu = [
        row["final_metrics_from_steps"]["baimu_area_change_ha"]
        for row in raw_seed_summaries
    ]
    elapsed = [
        _as_float(row.get("elapsed_sec"))
        for row in raw_seed_summaries
        if row.get("elapsed_sec") is not None
    ]
    return {
        "n_episodes": len(raw_seed_summaries),
        "total_reward_mean": _mean(rewards),
        "total_reward_std_sample": _sample_std(rewards),
        "total_reward_min": min(rewards) if rewards else 0.0,
        "total_reward_max": max(rewards) if rewards else 0.0,
        "slope_change_pct_mean": _mean(slopes),
        "cont_change_mean": _mean(conts),
        "baimu_area_change_ha_mean": _mean(baimu),
        "elapsed_sec_mean": _mean(elapsed),
        "zero_swap_steps_sum": sum(row["zero_swap_steps"] for row in raw_seed_summaries),
        "negative_zero_swap_steps_sum": sum(
            row["negative_zero_swap_steps"] for row in raw_seed_summaries
        ),
    }


def _seed_reward_map(raw_seed_summaries: list[dict]) -> dict[int, float]:
    return {
        int(row["seed"]): float(row["total_reward_from_steps"])
        for row in raw_seed_summaries
    }


def _summary_seed_rows(summary_payload: dict) -> list[dict]:
    return [
        {
            "seed": _as_int(row.get("seed")),
            "total_reward": _as_float(row.get("total_reward")),
            "steps_run": _as_int(row.get("steps_run")),
            "slope_change_pct": _as_float(row.get("slope_change_pct")),
            "cont_change": _as_float(row.get("cont_change")),
            "baimu_area_change_ha": _as_float(row.get("baimu_area_change_ha")),
        }
        for row in summary_payload.get("seed_summaries", [])
    ]


def _single_stage3_anchor(stage3_payload: dict) -> dict:
    anchors = [
        row
        for row in stage3_payload.get("rows", [])
        if row.get("role") == "frozen_anchor"
    ]
    if len(anchors) != 1:
        raise ValueError(f"Expected exactly one frozen_anchor row, found {len(anchors)}")
    return anchors[0]


def _abs_delta(a: float, b: float) -> float:
    return abs(float(a) - float(b))


def _aggregate_deltas(raw_aggregate: dict, other_aggregate: dict) -> dict:
    keys = (
        "n_episodes",
        "total_reward_mean",
        "total_reward_std_sample",
        "total_reward_min",
        "total_reward_max",
        "slope_change_pct_mean",
        "cont_change_mean",
        "baimu_area_change_ha_mean",
        "elapsed_sec_mean",
        "zero_swap_steps_sum",
        "negative_zero_swap_steps_sum",
    )
    return {
        key: _abs_delta(raw_aggregate.get(key, 0.0), other_aggregate.get(key, 0.0))
        for key in keys
    }


def _seed_deltas(raw_seed_summaries: list[dict], seed_rows: list[dict]) -> list[dict]:
    raw_rewards = _seed_reward_map(raw_seed_summaries)
    deltas = []
    for row in sorted(seed_rows, key=lambda item: item["seed"]):
        raw_reward = raw_rewards.get(row["seed"])
        if raw_reward is None:
            deltas.append(
                {
                    "seed": row["seed"],
                    "raw_total_reward": None,
                    "source_total_reward": row["total_reward"],
                    "abs_delta": None,
                }
            )
            continue
        deltas.append(
            {
                "seed": row["seed"],
                "raw_total_reward": raw_reward,
                "source_total_reward": row["total_reward"],
                "abs_delta": _abs_delta(raw_reward, row["total_reward"]),
            }
        )
    return deltas


def _all_close(values: Iterable[float | int | None], *, tolerance: float) -> bool:
    return all(value is not None and float(value) <= tolerance for value in values)


def _summary_consistency(
    raw_seed_summaries: list[dict],
    raw_aggregate: dict,
    summary_payload: dict,
    *,
    tolerance: float,
) -> dict:
    seed_rows = _summary_seed_rows(summary_payload)
    seed_deltas = _seed_deltas(raw_seed_summaries, seed_rows)
    aggregate_deltas = _aggregate_deltas(
        raw_aggregate,
        summary_payload.get("aggregate", {}),
    )
    return {
        "matches_raw": _all_close(
            (seed["abs_delta"] for seed in seed_deltas),
            tolerance=tolerance,
        )
        and _all_close(aggregate_deltas.values(), tolerance=tolerance),
        "seed_rewards": [row["total_reward"] for row in sorted(seed_rows, key=lambda item: item["seed"])],
        "seed_deltas": seed_deltas,
        "aggregate": dict(summary_payload.get("aggregate", {})),
        "aggregate_deltas": aggregate_deltas,
    }


def _stage3_consistency(
    raw_seed_summaries: list[dict],
    raw_aggregate: dict,
    stage3_payload: dict,
    *,
    tolerance: float,
) -> dict:
    anchor = _single_stage3_anchor(stage3_payload)
    stage3_seed_rows = [
        {"seed": seed, "total_reward": reward}
        for seed, reward in zip(anchor.get("seeds", []), anchor.get("seed_level_rewards", []))
    ]
    seed_deltas = _seed_deltas(raw_seed_summaries, stage3_seed_rows)
    aggregate_deltas = _aggregate_deltas(raw_aggregate, anchor.get("aggregate", {}))
    return {
        "matches_raw": _all_close(
            (seed["abs_delta"] for seed in seed_deltas),
            tolerance=tolerance,
        )
        and _all_close(aggregate_deltas.values(), tolerance=tolerance),
        "anchor_role": anchor.get("role"),
        "anchor_run_name": anchor.get("run_name"),
        "seed_rewards": [row["total_reward"] for row in stage3_seed_rows],
        "seed_deltas": seed_deltas,
        "aggregate": dict(anchor.get("aggregate", {})),
        "aggregate_deltas": aggregate_deltas,
    }


def build_anchor_raw_rollout_consistency_audit(
    raw_rollout_payloads: Iterable[tuple[str, dict]],
    summary_payload: dict,
    stage3_payload: dict,
    *,
    date: str = DATE,
    summary_source: str = "summary_json",
    stage3_source: str = "stage3_json",
    tolerance: float = FLOAT_TOLERANCE,
) -> dict:
    raw_seed_summaries = []
    for source_file, payload in raw_rollout_payloads:
        for episode in _episodes_from_raw(payload):
            raw_seed_summaries.append(_raw_seed_summary(source_file, episode))
    raw_seed_summaries.sort(key=lambda row: row["seed"])
    raw_aggregate = _raw_aggregate(raw_seed_summaries)
    summary_consistency = _summary_consistency(
        raw_seed_summaries,
        raw_aggregate,
        summary_payload,
        tolerance=tolerance,
    )
    stage3_consistency = _stage3_consistency(
        raw_seed_summaries,
        raw_aggregate,
        stage3_payload,
        tolerance=tolerance,
    )
    return {
        "date": date,
        "status": "source-derived consistency audit",
        "tolerance": tolerance,
        "sources": {
            "raw_rollouts": sorted(
                {row["source_file"] for row in raw_seed_summaries}
            ),
            "summary_json": summary_source,
            "stage3_json": stage3_source,
        },
        "source_boundary": {
            "new_experimental_claim": False,
            "reran_rollouts": False,
            "interpretation": (
                "This audit recomputes the Bishan 20x16/top5 anchor from "
                "tracked raw rollout step records and checks consistency with "
                "the packaged rollout summary and Stage 3 frozen-anchor row."
            ),
        },
        "raw_seed_summaries": raw_seed_summaries,
        "raw_aggregate": raw_aggregate,
        "summary_consistency": summary_consistency,
        "stage3_consistency": stage3_consistency,
        "overall_consistency_pass": summary_consistency["matches_raw"]
        and stage3_consistency["matches_raw"],
    }


def markdown_report(payload: dict) -> str:
    summary_status = "PASS" if payload["summary_consistency"]["matches_raw"] else "FAIL"
    stage3_status = "PASS" if payload["stage3_consistency"]["matches_raw"] else "FAIL"
    aggregate = payload["raw_aggregate"]
    lines = [
        "# Paper10 anchor raw-rollout consistency audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: source-derived consistency audit for the Bishan 20x16/top5 frozen anchor.",
        "",
        "This audit recomputes the tracked anchor from raw rollout step records. It does not add a new experimental claim. No rollout was rerun.",
        "",
        "## Consistency status",
        "",
        f"- Summary match: {summary_status}",
        f"- Stage 3 frozen-anchor match: {stage3_status}",
        f"- Tolerance: `{payload['tolerance']}`",
        "",
        "## Raw aggregate recomputed from steps",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| n_episodes | {aggregate['n_episodes']} |",
        f"| total_reward_mean | {_fmt(aggregate['total_reward_mean'])} |",
        f"| total_reward_std_sample | {_fmt(aggregate['total_reward_std_sample'])} |",
        f"| total_reward_min | {_fmt(aggregate['total_reward_min'])} |",
        f"| total_reward_max | {_fmt(aggregate['total_reward_max'])} |",
        f"| slope_change_pct_mean | {_fmt(aggregate['slope_change_pct_mean'])} |",
        f"| cont_change_mean | {_fmt(aggregate['cont_change_mean'])} |",
        f"| baimu_area_change_ha_mean | {_fmt(aggregate['baimu_area_change_ha_mean'])} |",
        "",
        "## Seed-level step recomputation",
        "",
        "| seed | steps | total reward from steps | reported total reward | abs delta |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in payload["raw_seed_summaries"]:
        lines.append(
            "| {seed} | {steps} | {raw} | {reported} | {delta} |".format(
                seed=row["seed"],
                steps=row["steps_run"],
                raw=_fmt(row["total_reward_from_steps"]),
                reported=_fmt(row["reported_total_reward"]),
                delta=_fmt(row["abs_reported_minus_steps"]),
            )
        )

    lines.extend(
        [
            "",
            "## Source files",
            "",
        ]
    )
    for path in payload["sources"]["raw_rollouts"]:
        lines.append(f"- raw rollout: `{path}`")
    lines.append(f"- rollout summary: `{payload['sources']['summary_json']}`")
    lines.append(f"- Stage 3 summary: `{payload['sources']['stage3_json']}`")

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            payload["source_boundary"]["interpretation"],
            "The audit supports evidence-chain consistency only; manuscript wording should continue to distinguish this anchor from Stage 3 50-state boundary evidence and from Dongxing transfer calibration evidence.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.anchor_raw_rollout_consistency_audit --raw-rollout paper10_geojepa_mpc\\experiments\\results\\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seed0_100step.json --raw-rollout paper10_geojepa_mpc\\experiments\\results\\e0_env_rollout_frontier_random050_value_head_20x16_h5_seed44_top5_blend010_h5_k50_seeds1-4_100step.json --summary-json paper10_geojepa_mpc\\experiments\\results\\e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json --stage3-json paper10_geojepa_mpc\\experiments\\results\\e0_original_vision_stage3_confirmatory_rollouts_2026-06-18.json --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_anchor_raw_rollout_consistency(
    raw_rollout_paths: Iterable[str | Path],
    summary_path: str | Path,
    stage3_path: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    *,
    date: str = DATE,
) -> dict:
    raw_payloads = []
    for path_value in raw_rollout_paths:
        path = Path(path_value)
        raw_payloads.append((str(path), json.loads(path.read_text(encoding="utf-8"))))
    summary = Path(summary_path)
    stage3 = Path(stage3_path)
    payload = build_anchor_raw_rollout_consistency_audit(
        raw_payloads,
        json.loads(summary.read_text(encoding="utf-8")),
        json.loads(stage3.read_text(encoding="utf-8")),
        date=date,
        summary_source=str(summary),
        stage3_source=str(stage3),
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
    parser.add_argument(
        "--raw-rollout",
        action="append",
        required=True,
        help="Raw rollout JSON. Repeat for single-seed and multi-seed raw files.",
    )
    parser.add_argument("--summary-json", required=True)
    parser.add_argument("--stage3-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--date", default=DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_anchor_raw_rollout_consistency(
        args.raw_rollout,
        args.summary_json,
        args.stage3_json,
        args.output_json,
        args.output_md,
        date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
