import argparse
import json
from pathlib import Path
from statistics import mean

from paper10_geojepa_mpc.experiments.rollout_summary import (
    aggregate_rollout_summaries,
    summarize_rollout,
)


METRIC_KEYS = (
    "total_reward_mean",
    "slope_change_pct_mean",
    "cont_change_mean",
    "baimu_area_change_ha_mean",
)


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _final_metrics_from_steps(episode: dict) -> dict:
    steps = episode.get("steps", [])
    if not steps:
        return {
            "slope_change_pct": 0.0,
            "cont_change": 0.0,
            "baimu_area_change_ha": 0.0,
        }
    final = steps[-1]
    return {
        "slope_change_pct": float(final.get("slope_change_pct", 0.0)),
        "cont_change": float(final.get("cont_change", 0.0)),
        "baimu_area_change_ha": float(final.get("baimu_area_change_ha", 0.0)),
    }


def _mean_step_field(episodes: list[dict], field: str) -> float:
    values = []
    for episode in episodes:
        for step in episode.get("steps", []):
            if field in step:
                values.append(float(step[field]))
    return _mean(values)


def _episode_summaries(data: dict) -> list[dict]:
    summaries = data.get("episode_summaries")
    if summaries:
        return list(summaries)
    episodes = data.get("episodes")
    if episodes:
        return [summarize_rollout(episode) for episode in episodes]
    if "steps" in data:
        return [summarize_rollout(data)]
    return []


def _aggregate(data: dict, summaries: list[dict]) -> dict:
    if data.get("aggregate"):
        return dict(data["aggregate"])
    return aggregate_rollout_summaries(summaries)


def summarize_run(name: str, data: dict) -> dict:
    """Create a compact, comparable summary for one rollout JSON."""

    raw_episodes = list(data.get("episodes", []))
    raw_by_seed = {
        int(episode["seed"]): episode
        for episode in raw_episodes
        if episode.get("seed") is not None
    }
    summaries = _episode_summaries(data)
    aggregate = _aggregate(data, summaries)

    seeds = []
    select_times = []
    for summary in summaries:
        seed = summary.get("seed")
        raw = raw_by_seed.get(int(seed)) if seed is not None else None
        final_metrics = summary.get("final_metrics")
        if final_metrics is None and raw is not None:
            final_metrics = _final_metrics_from_steps(raw)
        mean_select_time = float(summary.get("mean_select_time_sec", 0.0))
        if mean_select_time == 0.0 and raw is not None:
            mean_select_time = _mean_step_field([raw], "select_time_sec")
        select_times.append(mean_select_time)
        seeds.append(
            {
                "seed": seed,
                "total_reward": float(summary.get("total_reward", 0.0)),
                "final_metrics": final_metrics
                or {
                    "slope_change_pct": 0.0,
                    "cont_change": 0.0,
                    "baimu_area_change_ha": 0.0,
                },
                "mean_select_time_sec": mean_select_time,
            }
        )

    timing = {
        "mean_select_time_sec": _mean(select_times),
        "mean_score_time_sec": _mean_step_field(raw_episodes, "score_time_sec"),
        "mean_first_step_time_sec": _mean_step_field(raw_episodes, "first_step_time_sec"),
        "mean_rollout_time_sec": _mean_step_field(raw_episodes, "rollout_time_sec"),
    }
    return {
        "name": name,
        "aggregate": aggregate,
        "timing": timing,
        "seeds": seeds,
    }


def _delta(candidate: float, baseline: float) -> float:
    return float(candidate) - float(baseline)


def compare_rollout_runs(
    baseline_name: str,
    baseline_data: dict,
    candidate_name: str,
    candidate_data: dict,
) -> dict:
    baseline = summarize_run(baseline_name, baseline_data)
    candidate = summarize_run(candidate_name, candidate_data)

    aggregate_delta = {
        key: _delta(
            candidate["aggregate"].get(key, 0.0),
            baseline["aggregate"].get(key, 0.0),
        )
        for key in METRIC_KEYS
    }
    aggregate_delta["mean_select_time_sec"] = _delta(
        candidate["timing"]["mean_select_time_sec"],
        baseline["timing"]["mean_select_time_sec"],
    )
    aggregate_delta["mean_score_time_sec"] = _delta(
        candidate["timing"]["mean_score_time_sec"],
        baseline["timing"]["mean_score_time_sec"],
    )

    baseline_by_seed = {seed["seed"]: seed for seed in baseline["seeds"]}
    seed_deltas = []
    for seed in candidate["seeds"]:
        base = baseline_by_seed.get(seed["seed"])
        if base is None:
            continue
        seed_deltas.append(
            {
                "seed": seed["seed"],
                "total_reward_delta": _delta(
                    seed["total_reward"], base["total_reward"]
                ),
                "slope_change_pct_delta": _delta(
                    seed["final_metrics"].get("slope_change_pct", 0.0),
                    base["final_metrics"].get("slope_change_pct", 0.0),
                ),
                "cont_change_delta": _delta(
                    seed["final_metrics"].get("cont_change", 0.0),
                    base["final_metrics"].get("cont_change", 0.0),
                ),
                "baimu_area_change_ha_delta": _delta(
                    seed["final_metrics"].get("baimu_area_change_ha", 0.0),
                    base["final_metrics"].get("baimu_area_change_ha", 0.0),
                ),
                "mean_select_time_sec_delta": _delta(
                    seed["mean_select_time_sec"], base["mean_select_time_sec"]
                ),
            }
        )

    return {
        "baseline": baseline,
        "candidate": candidate,
        "aggregate_delta": aggregate_delta,
        "seed_deltas": seed_deltas,
    }


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def markdown_report(comparison: dict) -> str:
    baseline = comparison["baseline"]
    candidate = comparison["candidate"]
    delta = comparison["aggregate_delta"]
    lines = [
        "# Multiseed rollout comparison",
        "",
        f"Baseline: `{baseline['name']}`",
        f"Candidate: `{candidate['name']}`",
        "",
        "| metric | baseline | candidate | delta |",
        "|---|---:|---:|---:|",
    ]
    for key in METRIC_KEYS:
        lines.append(
            "| {key} | {base} | {cand} | {delta} |".format(
                key=key,
                base=_fmt(baseline["aggregate"].get(key, 0.0)),
                cand=_fmt(candidate["aggregate"].get(key, 0.0)),
                delta=_fmt(delta.get(key, 0.0)),
            )
        )
    for key in ("mean_select_time_sec", "mean_score_time_sec"):
        lines.append(
            "| {key} | {base} | {cand} | {delta} |".format(
                key=key,
                base=_fmt(baseline["timing"].get(key, 0.0)),
                cand=_fmt(candidate["timing"].get(key, 0.0)),
                delta=_fmt(delta.get(key, 0.0)),
            )
        )

    lines.extend(
        [
            "",
            "| seed | reward delta | slope delta | cont delta | baimu delta | select-time delta |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in comparison["seed_deltas"]:
        lines.append(
            "| {seed} | {reward} | {slope} | {cont} | {baimu} | {select} |".format(
                seed=row["seed"],
                reward=_fmt(row["total_reward_delta"]),
                slope=_fmt(row["slope_change_pct_delta"]),
                cont=_fmt(row["cont_change_delta"]),
                baimu=_fmt(row["baimu_area_change_ha_delta"]),
                select=_fmt(row["mean_select_time_sec_delta"]),
            )
        )
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--baseline-name", default="baseline")
    parser.add_argument("--candidate-name", default="candidate")
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    comparison = compare_rollout_runs(
        args.baseline_name,
        json.loads(baseline_path.read_text(encoding="utf-8")),
        args.candidate_name,
        json.loads(candidate_path.read_text(encoding="utf-8")),
    )
    text = json.dumps(comparison, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text, encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown_report(comparison), encoding="utf-8")


if __name__ == "__main__":
    main()
