from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
RETURN_LABEL_CSV_NAME = "e0_dongxing_return_label_family_summary_2026-06-10.csv"
LOW_LABEL_CSV_NAME = "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv"
DEFAULT_OUTPUT_DIR = ROOT / "reviewer_outputs/paper10_integrated_dongxing_figures"

FAMILY_COLORS = {
    "transfer": "#4c78a8",
    "scratch": "#f58518",
}
LABEL_ORDER = ["pairwise_1000s", "return_20x16_h5", "return_50x16_h5"]
LABEL_DISPLAY = {
    "pairwise_1000s": "Pairwise",
    "return_20x16_h5": "20x16",
    "return_50x16_h5": "50x16",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _save_figure(fig, output_dir: Path, stem: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    png = output_dir / f"{stem}.png"
    svg = output_dir / f"{stem}.svg"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    return [png, svg]


def _configure_matplotlib() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


def plot_return_label_scaling(
    rows: list[dict[str, str]], output_dir: Path
) -> list[Path]:
    import matplotlib.pyplot as plt

    _configure_matplotlib()
    families = ["transfer", "scratch"]
    width = 0.34
    x_positions = list(range(len(LABEL_ORDER)))

    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    for index, family in enumerate(families):
        family_rows = {
            row["label_type"]: row
            for row in rows
            if row["family"] == family
        }
        offsets = [x + (index - 0.5) * width for x in x_positions]
        means = [_float(family_rows[label], "mean_reward") for label in LABEL_ORDER]
        errors = [_float(family_rows[label], "reward_sd") for label in LABEL_ORDER]
        ax.bar(
            offsets,
            means,
            width=width,
            yerr=errors,
            capsize=2.5,
            color=FAMILY_COLORS[family],
            edgecolor="white",
            linewidth=0.8,
            label=family.capitalize(),
        )
        for x, mean, error in zip(offsets, means, errors):
            ax.text(
                x,
                mean + error + 1.0,
                f"{mean:.1f}",
                ha="center",
                va="bottom",
                fontsize=6.5,
            )

    ax.set_xticks(x_positions)
    ax.set_xticklabels([LABEL_DISPLAY[label] for label in LABEL_ORDER])
    ax.set_xlabel("Dongxing label source")
    ax.set_ylabel("Mean total reward")
    ax.set_ylim(0, 84)
    ax.grid(axis="y", color="#e2e6ea", linewidth=0.8)
    ax.legend(loc="upper left", ncols=2)
    fig.tight_layout()
    paths = _save_figure(fig, output_dir, "dongxing_return_label_scaling")
    plt.close(fig)
    return paths


def plot_low_label_budget_stress_test(
    rows: list[dict[str, str]], output_dir: Path
) -> list[Path]:
    import matplotlib.pyplot as plt

    _configure_matplotlib()
    families = ["transfer", "scratch"]
    means_by_budget_family = {
        (int(row["budget"]), row["family"]): _float(row, "reward_mean")
        for row in rows
    }

    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    for family in families:
        family_rows = sorted(
            [row for row in rows if row["family"] == family],
            key=lambda row: int(row["budget"]),
        )
        budgets = [int(row["budget"]) for row in family_rows]
        means = [_float(row, "reward_mean") for row in family_rows]
        errors = [_float(row, "reward_sd") for row in family_rows]
        ax.errorbar(
            budgets,
            means,
            yerr=errors,
            marker="o",
            capsize=2.5,
            linewidth=1.6,
            color=FAMILY_COLORS[family],
            label=family.capitalize(),
        )
        for budget, mean in zip(budgets, means):
            other_family = "scratch" if family == "transfer" else "transfer"
            other_mean = means_by_budget_family[(budget, other_family)]
            is_higher = mean >= other_mean
            label_offset = 2.1 if is_higher else -2.8
            label_va = "bottom" if is_higher else "top"
            ax.text(
                budget,
                mean + label_offset,
                f"{mean:.1f}",
                ha="center",
                va=label_va,
                fontsize=6.5,
            )

    ax.set_xticks([5, 10, 20])
    ax.set_xlabel("Return-label states")
    ax.set_ylabel("Mean total reward")
    ax.set_ylim(0, 76)
    ax.grid(axis="y", color="#e2e6ea", linewidth=0.8)
    ax.legend(loc="upper left", ncols=2)
    fig.tight_layout()
    paths = _save_figure(fig, output_dir, "dongxing_low_label_budget_stress_test")
    plt.close(fig)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Paper10 integrated Dongxing manuscript figure drafts."
    )
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    return_label_rows = read_csv(args.results_dir / RETURN_LABEL_CSV_NAME)
    low_label_rows = read_csv(args.results_dir / LOW_LABEL_CSV_NAME)

    output_paths = []
    output_paths.extend(plot_return_label_scaling(return_label_rows, args.output_dir))
    output_paths.extend(plot_low_label_budget_stress_test(low_label_rows, args.output_dir))
    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
