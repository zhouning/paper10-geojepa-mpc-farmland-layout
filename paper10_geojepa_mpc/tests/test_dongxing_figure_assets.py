import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "paper10_geojepa_mpc" / "experiments" / "results"
RETURN_LABEL_CSV = RESULTS / "e0_dongxing_return_label_family_summary_2026-06-10.csv"
LOW_LABEL_CSV = RESULTS / "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv"
PLOT_SCRIPT = ROOT / "scripts" / "paper10" / "plot_integrated_dongxing_figures.py"
FIGURE_PLAN = RESULTS / "e0_integrated_dongxing_figure_plan_2026-06-11.md"
SOURCE_DATA_MAP = RESULTS / "e0_source_data_map_with_dongxing_2026-06-11.md"


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_dongxing_return_label_summary_records_expected_family_order():
    rows = _csv_rows(RETURN_LABEL_CSV)

    assert [(row["label_type"], row["family"]) for row in rows] == [
        ("pairwise_1000s", "transfer"),
        ("pairwise_1000s", "scratch"),
        ("return_20x16_h5", "transfer"),
        ("return_20x16_h5", "scratch"),
        ("return_50x16_h5", "transfer"),
        ("return_50x16_h5", "scratch"),
    ]
    assert f"{float(rows[-2]['mean_reward']):.4f}" == "51.6183"
    assert f"{float(rows[-1]['mean_reward']):.4f}" == "55.7324"


def test_dongxing_low_label_summary_preserves_mixed_transfer_boundary():
    rows = _csv_rows(LOW_LABEL_CSV)
    reward_by_budget_family = {
        (int(row["budget"]), row["family"]): float(row["reward_mean"])
        for row in rows
    }

    assert reward_by_budget_family[(5, "scratch")] > reward_by_budget_family[(5, "transfer")]
    assert reward_by_budget_family[(10, "scratch")] > reward_by_budget_family[(10, "transfer")]
    assert reward_by_budget_family[(20, "transfer")] > reward_by_budget_family[(20, "scratch")]


def test_integrated_dongxing_plot_script_exports_figure4_and_figure5(tmp_path):
    result = subprocess.run(
        [sys.executable, str(PLOT_SCRIPT), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = [
        tmp_path / "dongxing_return_label_scaling.png",
        tmp_path / "dongxing_return_label_scaling.svg",
        tmp_path / "dongxing_low_label_budget_stress_test.png",
        tmp_path / "dongxing_low_label_budget_stress_test.svg",
    ]
    for path in expected:
        assert path.exists()
        assert str(path) in result.stdout


def test_integrated_dongxing_figure_plan_and_source_map_bind_submission_assets():
    plan_text = FIGURE_PLAN.read_text(encoding="utf-8")
    map_text = SOURCE_DATA_MAP.read_text(encoding="utf-8")

    required_tokens = [
        "e0_paper10_integrated_manuscript_scaffold_with_dongxing_2026-06-10.md",
        "e0_paper10_integrated_manuscript_tables_with_dongxing_2026-06-10.md",
        "e0_dongxing_return_label_family_summary_2026-06-10.csv",
        "e0_dongxing_low_label_budget_family_summary_2026-06-10.csv",
        "scripts/paper10/plot_integrated_dongxing_figures.py",
        "Figure 4",
        "Figure 5",
        "not robustly supported",
    ]
    for token in required_tokens:
        assert token in plan_text
        assert token in map_text
