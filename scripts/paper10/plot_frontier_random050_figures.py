from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
SEEDWISE_CSV_NAME = "e0_frontier_random050_seedwise_rewards_2026-06-09.csv"
TOPK_CSV_NAME = "e0_frontier_random050_topk_diagnostics_2026-06-09.csv"
DEFAULT_OUTPUT_DIR = ROOT / "reviewer_outputs/paper10_frontier_random050_figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _save_figure(fig, output_dir: Path, stem: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    png = output_dir / f"{stem}.png"
    svg = output_dir / f"{stem}.svg"
    fig.savefig(png, dpi=300)
    fig.savefig(svg)
    return [png, svg]


def plot_seedwise_reward_dotplot(rows: list[dict[str, str]], output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    seeds = [int(row["seed"]) for row in rows]
    rewards_10x12 = [_float(row, "reward_10x12_top4") for row in rows]
    rewards_20x16 = [_float(row, "reward_20x16_top5") for row in rows]

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    for seed, reward_a, reward_b in zip(seeds, rewards_10x12, rewards_20x16):
        ax.plot([seed, seed], [reward_a, reward_b], color="#b7bec8", linewidth=1.0)
    ax.plot(seeds, rewards_10x12, marker="o", color="#4c78a8", label="10x12/top4")
    ax.plot(seeds, rewards_20x16, marker="o", color="#f58518", label="20x16/top5")
    ax.set_xlabel("Rollout seed")
    ax.set_ylabel("Total reward over 100 steps")
    ax.set_xticks(seeds)
    ax.grid(axis="y", color="#e2e6ea", linewidth=0.8)
    ax.legend(frameon=False)
    fig.tight_layout()
    paths = _save_figure(fig, output_dir, "seedwise_reward_dotplot")
    plt.close(fig)
    return paths


def _unique_in_order(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def plot_topk_diagnostic_lines(rows: list[dict[str, str]], output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    runs = _unique_in_order([row["run"] for row in rows])
    metrics = [
        ("candidate_regret", "Candidate regret", 0.25),
        ("candidate_overlap", "Candidate overlap", 0.50),
        ("one_step_regret", "One-step regret", 0.25),
    ]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2"]

    fig, axes = plt.subplots(len(metrics), 1, figsize=(6.4, 7.2), sharex=True)
    for axis, (metric_key, label, threshold) in zip(axes, metrics):
        for color, run in zip(colors, runs):
            run_rows = [row for row in rows if row["run"] == run]
            topk = [int(row["top_k"]) for row in run_rows]
            values = [_float(row, metric_key) for row in run_rows]
            axis.plot(topk, values, marker="o", color=color, label=run)
        axis.axhline(threshold, color="#3a3a3a", linestyle="--", linewidth=0.8)
        axis.set_ylabel(label)
        axis.grid(axis="y", color="#e2e6ea", linewidth=0.8)
    axes[-1].set_xlabel("Monitor top-k")
    axes[0].legend(frameon=False, ncol=2)
    fig.tight_layout()
    paths = _save_figure(fig, output_dir, "topk_diagnostic_lines")
    plt.close(fig)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Paper10 frontier_random050 manuscript figure drafts."
    )
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seedwise_rows = read_csv(args.results_dir / SEEDWISE_CSV_NAME)
    topk_rows = read_csv(args.results_dir / TOPK_CSV_NAME)

    output_paths = []
    output_paths.extend(plot_seedwise_reward_dotplot(seedwise_rows, args.output_dir))
    output_paths.extend(plot_topk_diagnostic_lines(topk_rows, args.output_dir))
    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
