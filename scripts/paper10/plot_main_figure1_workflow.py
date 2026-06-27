from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "reviewer_outputs/paper10_main_figure1_workflow"
OUTPUT_STEM = "main_figure1_workflow"


COLORS = {
    "ink": "#273241",
    "muted": "#667085",
    "line": "#8894a5",
    "environment": "#e8f1fb",
    "candidate": "#fff1d8",
    "label": "#eef3e8",
    "monitor": "#f2eafb",
    "pass": "#e4f4ed",
    "stop": "#fff0ec",
    "boundary": "#f6f7f9",
    "accent": "#2f6f9f",
    "pass_edge": "#2f855a",
    "stop_edge": "#c2410c",
}


def _configure_matplotlib() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


def _save_figure(
    fig,
    output_dir: Path,
    stem: str,
    formats: Iterable[str],
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = []
    for fmt in formats:
        path = output_dir / f"{stem}.{fmt}"
        save_kwargs = {"bbox_inches": "tight", "facecolor": "white"}
        if fmt in {"png", "tiff"}:
            save_kwargs["dpi"] = 600
        fig.savefig(path, **save_kwargs)
        output_paths.append(path)
    return output_paths


def _box(
    ax,
    xy: tuple[float, float],
    size: tuple[float, float],
    facecolor: str,
    edgecolor: str,
    label: str,
    title: str,
    lines: list[str],
):
    from matplotlib.patches import FancyBboxPatch

    x, y = xy
    width, height = size
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1.05,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        x + 0.018,
        y + height - 0.038,
        label,
        color=edgecolor,
        fontsize=8,
        fontweight="bold",
        va="top",
    )
    ax.text(
        x + 0.052,
        y + height - 0.038,
        title,
        color=COLORS["ink"],
        fontsize=7.4,
        fontweight="bold",
        va="top",
    )
    start_y = y + height - 0.092
    for index, line in enumerate(lines):
        ax.text(
            x + 0.052,
            start_y - index * 0.034,
            line,
            color=COLORS["ink"],
            fontsize=6.55,
            va="top",
        )
    return patch


def _arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = COLORS["line"],
    dashed: bool = False,
    label: str | None = None,
    label_offset: tuple[float, float] = (0.0, 0.0),
) -> None:
    from matplotlib.patches import FancyArrowPatch

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1.25,
        color=color,
        linestyle=(0, (3, 2)) if dashed else "solid",
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(
            mx,
            my,
            label,
            color=color,
            fontsize=6.35,
            fontweight="bold",
            ha="center",
            va="center",
        )


def _draw_environment_icon(ax, x: float, y: float) -> None:
    from matplotlib.patches import Rectangle

    cell = 0.018
    active = {(0, 1), (1, 1), (2, 0), (3, 2)}
    blocked = {(1, 0), (2, 2)}
    for row in range(3):
        for col in range(4):
            color = "#ffffff"
            if (col, row) in active:
                color = "#b9d7ee"
            if (col, row) in blocked:
                color = "#d6dbe3"
            ax.add_patch(
                Rectangle(
                    (x + col * cell, y + row * cell),
                    cell * 0.84,
                    cell * 0.84,
                    facecolor=color,
                    edgecolor="#8fa6bd",
                    linewidth=0.45,
                )
            )
    ax.text(x + 0.085, y + 0.027, "mask", fontsize=5.6, color=COLORS["muted"])


def _draw_score_icon(ax, x: float, y: float) -> None:
    from matplotlib.patches import Circle

    heights = [0.014, 0.028, 0.021, 0.04]
    colors = ["#d7e3f1", "#9fc5e8", "#f4c273", "#78a878"]
    for index, height in enumerate(heights):
        cx = x + index * 0.024
        ax.plot([cx, cx], [y, y + height], color="#9aa6b2", linewidth=1.0)
        ax.add_patch(
            Circle(
                (cx, y + height),
                0.0065,
                facecolor=colors[index],
                edgecolor="#667085",
                linewidth=0.4,
            )
        )
    ax.text(x + 0.006, y - 0.019, "ranked actions", fontsize=5.6, color=COLORS["muted"])


def _draw_label_icon(ax, x: float, y: float) -> None:
    from matplotlib.patches import Rectangle

    labels = ["R", "r1", "score"]
    for row, label in enumerate(labels):
        ax.add_patch(
            Rectangle(
                (x, y + row * 0.022),
                0.078,
                0.015,
                facecolor="#ffffff",
                edgecolor="#9aa6b2",
                linewidth=0.45,
            )
        )
        ax.text(
            x + 0.086,
            y + row * 0.022 + 0.007,
            label,
            fontsize=5.5,
            color=COLORS["muted"],
            va="center",
        )


def _draw_monitor_icon(ax, x: float, y: float) -> None:
    thresholds = [
        ("regret", "<=0.25", "#dbeafe"),
        ("overlap", ">=0.50", "#dcfce7"),
        ("1-step", ">0.25", "#fef3c7"),
    ]
    for index, (name, value, color) in enumerate(thresholds):
        cy = y + index * 0.024
        ax.plot([x, x + 0.055], [cy, cy], color="#9aa6b2", linewidth=0.8)
        ax.scatter([x + 0.055], [cy], s=10, color="#374151", zorder=3)
        ax.text(x + 0.064, cy + 0.001, f"{name} {value}", fontsize=5.4, va="center")


def _callout(
    ax,
    xy: tuple[float, float],
    size: tuple[float, float],
    title: str,
    lines: list[str],
) -> None:
    _box(
        ax,
        xy,
        size,
        COLORS["boundary"],
        "#9aa6b2",
        "",
        title,
        lines,
    )


def plot_workflow(output_dir: Path, formats: Iterable[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    _configure_matplotlib()
    fig, ax = plt.subplots(figsize=(7.4, 4.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.03,
        0.955,
        "Monitor-gated GeoJEPA-MPC value filtering workflow",
        fontsize=11.2,
        fontweight="bold",
        color=COLORS["ink"],
        va="top",
    )
    ax.text(
        0.03,
        0.912,
        "Only monitor-passing labels train the value head; failed labels remain diagnostics and claim-boundary evidence.",
        fontsize=7.2,
        color=COLORS["muted"],
        va="top",
    )

    panel_y = 0.61
    panel_h = 0.235
    panel_w = 0.154
    xs = [0.03, 0.224, 0.418, 0.612, 0.806]

    _box(
        ax,
        (xs[0], panel_y),
        (panel_w, panel_h),
        COLORS["environment"],
        COLORS["accent"],
        "1a",
        "Constrained task",
        ["Bishan grid state", "executable swap mask", "valid parcel actions"],
    )
    _draw_environment_icon(ax, xs[0] + 0.054, panel_y + 0.032)

    _box(
        ax,
        (xs[1], panel_y),
        (panel_w, panel_h),
        COLORS["candidate"],
        "#b7791f",
        "1b",
        "Candidate proposal",
        ["rank checkpoint", "frontier_random050", "scores valid actions"],
    )
    _draw_score_icon(ax, xs[1] + 0.055, panel_y + 0.047)

    _box(
        ax,
        (xs[2], panel_y),
        (panel_w, panel_h),
        COLORS["label"],
        "#4d7c0f",
        "1c",
        "Label generation",
        ["multi-step returns", "one-step rewards", "candidate scores"],
    )
    _draw_label_icon(ax, xs[2] + 0.052, panel_y + 0.038)

    _box(
        ax,
        (xs[3], panel_y),
        (panel_w, panel_h),
        COLORS["monitor"],
        "#7e22ce",
        "1d",
        "Monitor gate",
        ["candidate regret", "candidate overlap", "one-step regret"],
    )
    _draw_monitor_icon(ax, xs[3] + 0.05, panel_y + 0.044)

    _box(
        ax,
        (xs[4], panel_y),
        (panel_w, panel_h),
        COLORS["pass"],
        COLORS["pass_edge"],
        "1e",
        "Value-filtered MPC",
        ["decision=continue", "train value head", "selector=value_filter", "100-step rollouts"],
    )

    for index in range(4):
        start = (xs[index] + panel_w + 0.008, panel_y + panel_h * 0.55)
        end = (xs[index + 1] - 0.01, panel_y + panel_h * 0.55)
        _arrow(ax, start, end)

    stop_xy = (0.60, 0.245)
    stop_size = (0.29, 0.18)
    _box(
        ax,
        stop_xy,
        stop_size,
        COLORS["stop"],
        COLORS["stop_edge"],
        "",
        "Stop path",
        ["Stop as diagnostics", "No training on failed labels", "Boundary evidence only"],
    )
    _arrow(
        ax,
        (xs[3] + panel_w * 0.52, panel_y - 0.006),
        (stop_xy[0] + 0.13, stop_xy[1] + stop_size[1] + 0.006),
        color=COLORS["stop_edge"],
        dashed=True,
        label="decision=stop",
        label_offset=(-0.052, 0.0),
    )
    _arrow(
        ax,
        (xs[3] + panel_w + 0.008, panel_y + panel_h * 0.30),
        (xs[4] - 0.01, panel_y + panel_h * 0.30),
        color=COLORS["pass_edge"],
        label="PASS",
        label_offset=(0.0, 0.024),
    )

    _callout(
        ax,
        (0.03, 0.345),
        (0.36, 0.15),
        "Hard constraints",
        [
            "Executable masks remove invalid swaps before scoring.",
            "The planner can choose only actions accepted by the environment.",
        ],
    )
    _callout(
        ax,
        (0.03, 0.17),
        (0.45, 0.14),
        "Manuscript boundary",
        [
            "Positive anchor: Bishan 20x16/top5 under the matched protocol.",
            "Fifty-state and cross-region rows are boundary or calibration evidence.",
        ],
    )
    _callout(
        ax,
        (0.60, 0.075),
        (0.35, 0.105),
        "Reporting policy",
        [
            "Descriptive statistics only unless a new analysis plan is declared.",
            "This schematic is workflow artwork, not a new experiment.",
        ],
    )

    ax.text(
        0.03,
        0.04,
        "Source modules: value_label_generation.py | value_label_monitor.py | run_e0_value_head_train.py | run_e0_env_rollout_smoke.py",
        fontsize=5.8,
        color=COLORS["muted"],
        va="bottom",
    )

    paths = _save_figure(fig, output_dir, OUTPUT_STEM, formats)
    plt.close(fig)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the Paper10 Main Figure 1 workflow schematic preview."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["png", "svg", "pdf"],
        choices=["png", "svg", "pdf", "tiff"],
        help="Output formats to write. Defaults to png svg pdf.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_paths = plot_workflow(args.output_dir, args.formats)
    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
