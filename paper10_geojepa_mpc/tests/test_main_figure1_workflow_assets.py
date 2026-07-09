import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLOT_SCRIPT = ROOT / "scripts" / "paper10" / "plot_main_figure1_workflow.py"


def test_main_figure1_workflow_script_exports_preview_assets(tmp_path):
    result = subprocess.run(
        [sys.executable, str(PLOT_SCRIPT), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = [
        tmp_path / "main_figure1_workflow.png",
        tmp_path / "main_figure1_workflow.svg",
        tmp_path / "main_figure1_workflow.pdf",
    ]
    for path in expected:
        assert path.exists()
        assert str(path) in result.stdout

    svg_text = expected[1].read_text(encoding="utf-8")
    required_tokens = [
        "Monitor gate",
        "decision=continue",
        "Stop as diagnostics",
        "No training on failed labels",
        "selector=value_filter",
    ]
    for token in required_tokens:
        assert token in svg_text


def test_main_figure1_workflow_script_exports_final_submission_assets(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(PLOT_SCRIPT),
            "--variant",
            "final",
            "--output-dir",
            str(tmp_path),
            "--formats",
            "svg",
            "pdf",
            "png",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = [
        tmp_path / "figure_1_monitor_gated_geojepa_mpc_workflow.svg",
        tmp_path / "figure_1_monitor_gated_geojepa_mpc_workflow.pdf",
        tmp_path / "figure_1_monitor_gated_geojepa_mpc_workflow.png",
    ]
    for path in expected:
        assert path.exists()
        assert str(path) in result.stdout

    svg_text = expected[0].read_text(encoding="utf-8")
    assert all(line == line.rstrip() for line in svg_text.splitlines())
    required_tokens = [
        "Constrained task",
        "Monitor gate",
        "decision=continue",
        "Stop as diagnostics",
        "No training on failed labels",
        "selector=value_filter",
        "workflow artwork, not a new experiment",
    ]
    for token in required_tokens:
        assert token in svg_text

    forbidden_preview_tokens = [
        "Monitor-gated GeoJEPA-MPC value filtering workflow",
        "Only monitor-passing labels train the value head",
        "Source modules:",
        ">1a<",
    ]
    for token in forbidden_preview_tokens:
        assert token not in svg_text


def test_main_figure1_workflow_final_svg_export_is_reproducible(tmp_path):
    output_paths = []
    for run_name in ["run_a", "run_b"]:
        output_dir = tmp_path / run_name
        subprocess.run(
            [
                sys.executable,
                str(PLOT_SCRIPT),
                "--variant",
                "final",
                "--output-dir",
                str(output_dir),
                "--formats",
                "svg",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        output_paths.append(
            output_dir / "figure_1_monitor_gated_geojepa_mpc_workflow.svg"
        )

    assert output_paths[0].read_bytes() == output_paths[1].read_bytes()
