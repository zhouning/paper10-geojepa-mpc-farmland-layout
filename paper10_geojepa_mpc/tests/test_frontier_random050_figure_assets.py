import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
SEEDWISE_CSV = RESULTS / "e0_frontier_random050_seedwise_rewards_2026-06-09.csv"
TOPK_CSV = RESULTS / "e0_frontier_random050_topk_diagnostics_2026-06-09.csv"
PLOT_SCRIPT = ROOT / "scripts" / "paper10" / "plot_frontier_random050_figures.py"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _summary(path: str) -> dict:
    return json.loads((RESULTS / path).read_text(encoding="utf-8"))


def test_seedwise_reward_csv_matches_packaged_rollout_summaries():
    rows = _csv_rows(SEEDWISE_CSV)
    summary_10x12 = _summary(
        "e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json"
    )
    summary_20x16 = _summary(
        "e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json"
    )

    rewards_10x12 = {
        int(row["seed"]): float(row["total_reward"])
        for row in summary_10x12["seed_summaries"]
    }
    rewards_20x16 = {
        int(row["seed"]): float(row["total_reward"])
        for row in summary_20x16["seed_summaries"]
    }

    assert [int(row["seed"]) for row in rows] == [0, 1, 2, 3, 4]
    for row in rows:
        seed = int(row["seed"])
        reward_10x12 = rewards_10x12[seed]
        reward_20x16 = rewards_20x16[seed]
        assert row["reward_10x12_top4"] == f"{reward_10x12:.4f}"
        assert row["reward_20x16_top5"] == f"{reward_20x16:.4f}"
        assert row["reward_delta"] == f"{reward_20x16 - reward_10x12:+.4f}"


def test_topk_diagnostics_csv_records_failed_windows_posthoc_rows():
    rows = _csv_rows(TOPK_CSV)

    assert rows == [
        {
            "run": "50x16 f0.5",
            "states": "50",
            "candidates": "16",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "6",
            "decision": "stop",
            "candidate_regret": "0.3010",
            "candidate_overlap": "0.6533",
            "one_step_regret": "1.4748",
        },
        {
            "run": "50x16 f0.5",
            "states": "50",
            "candidates": "16",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "8",
            "decision": "stop",
            "candidate_regret": "0.1324",
            "candidate_overlap": "0.7350",
            "one_step_regret": "0.1056",
        },
        {
            "run": "50x16 f0.5",
            "states": "50",
            "candidates": "16",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "10",
            "decision": "stop",
            "candidate_regret": "0.1324",
            "candidate_overlap": "0.7560",
            "one_step_regret": "0.0811",
        },
        {
            "run": "50x16 f0.5",
            "states": "50",
            "candidates": "16",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "12",
            "decision": "stop",
            "candidate_regret": "0.1238",
            "candidate_overlap": "0.8067",
            "one_step_regret": "0.0725",
        },
        {
            "run": "50x20 f0.5",
            "states": "50",
            "candidates": "20",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "6",
            "decision": "stop",
            "candidate_regret": "0.5164",
            "candidate_overlap": "0.5467",
            "one_step_regret": "1.3441",
        },
        {
            "run": "50x20 f0.5",
            "states": "50",
            "candidates": "20",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "8",
            "decision": "stop",
            "candidate_regret": "0.4685",
            "candidate_overlap": "0.6175",
            "one_step_regret": "0.1588",
        },
        {
            "run": "50x20 f0.5",
            "states": "50",
            "candidates": "20",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "10",
            "decision": "stop",
            "candidate_regret": "0.0780",
            "candidate_overlap": "0.7280",
            "one_step_regret": "0.0739",
        },
        {
            "run": "50x20 f0.5",
            "states": "50",
            "candidates": "20",
            "frontier_fraction": "0.5",
            "seed": "46",
            "top_k": "12",
            "decision": "stop",
            "candidate_regret": "0.0739",
            "candidate_overlap": "0.7550",
            "one_step_regret": "0.0000",
        },
        {
            "run": "50x24 f0.75",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "0.75",
            "seed": "46",
            "top_k": "6",
            "decision": "stop",
            "candidate_regret": "0.9522",
            "candidate_overlap": "0.3467",
            "one_step_regret": "2.4113",
        },
        {
            "run": "50x24 f0.75",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "0.75",
            "seed": "46",
            "top_k": "8",
            "decision": "stop",
            "candidate_regret": "0.9118",
            "candidate_overlap": "0.4250",
            "one_step_regret": "2.0970",
        },
        {
            "run": "50x24 f0.75",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "0.75",
            "seed": "46",
            "top_k": "10",
            "decision": "stop",
            "candidate_regret": "0.6931",
            "candidate_overlap": "0.4960",
            "one_step_regret": "0.3802",
        },
        {
            "run": "50x24 f0.75",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "0.75",
            "seed": "46",
            "top_k": "12",
            "decision": "stop",
            "candidate_regret": "0.2912",
            "candidate_overlap": "0.6167",
            "one_step_regret": "0.3419",
        },
        {
            "run": "50x24 f1.0",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "1.0",
            "seed": "46",
            "top_k": "6",
            "decision": "stop",
            "candidate_regret": "1.2449",
            "candidate_overlap": "0.3967",
            "one_step_regret": "2.8339",
        },
        {
            "run": "50x24 f1.0",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "1.0",
            "seed": "46",
            "top_k": "8",
            "decision": "stop",
            "candidate_regret": "1.2432",
            "candidate_overlap": "0.4675",
            "one_step_regret": "2.7080",
        },
        {
            "run": "50x24 f1.0",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "1.0",
            "seed": "46",
            "top_k": "10",
            "decision": "stop",
            "candidate_regret": "0.5200",
            "candidate_overlap": "0.5780",
            "one_step_regret": "0.6433",
        },
        {
            "run": "50x24 f1.0",
            "states": "50",
            "candidates": "24",
            "frontier_fraction": "1.0",
            "seed": "46",
            "top_k": "12",
            "decision": "stop",
            "candidate_regret": "0.2691",
            "candidate_overlap": "0.6400",
            "one_step_regret": "0.6011",
        },
    ]


def test_frontier_plot_script_is_offline_figure_entrypoint():
    text = PLOT_SCRIPT.read_text(encoding="utf-8")

    required_tokens = [
        "reviewer_outputs/paper10_frontier_random050_figures",
        "e0_frontier_random050_seedwise_rewards_2026-06-09.csv",
        "e0_frontier_random050_topk_diagnostics_2026-06-09.csv",
        "seedwise_reward_dotplot",
        "topk_diagnostic_lines",
        "matplotlib",
    ]
    for token in required_tokens:
        assert token in text
