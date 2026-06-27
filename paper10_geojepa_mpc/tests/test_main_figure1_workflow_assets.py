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
