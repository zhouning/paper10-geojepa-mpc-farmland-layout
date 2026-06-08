import json
from pathlib import Path

from paper10_geojepa_mpc.experiments.rollout_summary import summarize_rollout


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"


RUN_FILES = {
    "original_h5_reward": RESULT_DIR
    / "e0_env_rollout_full1_h5_k50_seed0_executable_mask_summary.json",
    "original_h1_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_h1_k50_seed0_executable_mask.json",
    "frontier_reward_head_h5_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_value_head_ft_20x50_h3_seed2_h5_k50_seed0.json",
    "frontier_reward_head_h1_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_value_head_ft_20x50_h3_seed2_h1_k50_seed0.json",
    "independent_value_h1_value_as_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h1_k50_seed0_value_scoring.json",
    "independent_value_h5_value_as_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h5_k50_seed0_value_scoring.json",
    "independent_value_h5_blend025_as_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h5_k50_seed0_blend025_scoring.json",
    "independent_value_h5_blend010_as_reward": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h5_k50_seed0_blend010_scoring.json",
    "independent_value_h5_value_filter_reward_rollout": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h5_k50_seed0_value_filter.json",
    "independent_value_h5_value_filter_candidate_blend010_reward_rollout": RESULT_DIR
    / "e0_env_rollout_rank_seed2028_frontier_independent_value_head_20x50_h3_seed2_h5_k50_seed0_value_filter_candidate_blend010.json",
}


def summarize_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "steps" not in data:
        return data
    summary = summarize_rollout(data)
    summary["horizon"] = data.get("horizon")
    summary["selector"] = data.get("selector", "paper9")
    summary["scoring"] = data.get("scoring")
    summary["model_score_mode"] = data.get("model_score_mode", "reward")
    summary["model_value_weight"] = data.get("model_value_weight")
    summary["candidate_score_mode"] = data.get("candidate_score_mode")
    summary["candidate_value_weight"] = data.get("candidate_value_weight")
    return summary


def markdown_table(summaries: dict[str, dict]) -> str:
    lines = [
        "# E0 value-head rollout comparison with value-filter",
        "",
        "| run | selector | H | model score | candidate score | total reward | slope % | cont | baimu ha |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for name, summary in summaries.items():
        final_metrics = summary.get("final_metrics", {})
        lines.append(
            "| {name} | {selector} | {horizon} | {model_score} | "
            "{candidate_score} | {reward:.4f} | {slope:.4f} | {cont:.5f} | "
            "{baimu:.2f} |".format(
                name=name,
                selector=summary.get("selector", "paper9"),
                horizon=summary.get("horizon", ""),
                model_score=summary.get("model_score_mode", "reward"),
                candidate_score=summary.get("candidate_score_mode", ""),
                reward=summary.get("total_reward", 0.0),
                slope=final_metrics.get("slope_change_pct", 0.0),
                cont=final_metrics.get("cont_change", 0.0),
                baimu=final_metrics.get("baimu_area_change_ha", 0.0),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    missing = []
    summaries = {}
    for name, path in RUN_FILES.items():
        if not path.exists():
            missing.append(str(path))
            continue
        summaries[name] = summarize_file(path)

    json_path = RESULT_DIR / "e0_value_head_rollout_comparison_with_value_filter.json"
    md_path = RESULT_DIR / "e0_value_head_rollout_comparison_with_value_filter.md"
    json_path.write_text(json.dumps(summaries, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown_table(summaries), encoding="utf-8")

    brief = {
        name: {
            "selector": summary.get("selector", "paper9"),
            "reward": summary.get("total_reward"),
            "slope": summary.get("final_metrics", {}).get("slope_change_pct"),
            "cont": summary.get("final_metrics", {}).get("cont_change"),
            "baimu": summary.get("final_metrics", {}).get("baimu_area_change_ha"),
        }
        for name, summary in summaries.items()
    }
    print(
        json.dumps(
            {
                "missing": missing,
                "json": str(json_path),
                "md": str(md_path),
                "runs": brief,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
