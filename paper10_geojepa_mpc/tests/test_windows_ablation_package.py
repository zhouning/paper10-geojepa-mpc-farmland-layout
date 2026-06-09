from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "windows" / "run_frontier_random050_ablation_grid.ps1"
ENV_TEMPLATE = ROOT / "scripts" / "windows" / "frontier_random050_ablation.env.example.ps1"
GUIDE = ROOT / "docs" / "windows_frontier_random050_ablation.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_windows_ablation_runner_is_powershell_and_label_first():
    text = _read(RUNNER)

    required_tokens = [
        "Set-StrictMode -Version Latest",
        "$DataRoot = \"D:\\test\"",
        "$RunRoot = \"D:\\test\\paper10_runs\"",
        "$PythonBin = \"D:\\adk\\.venv\\Scripts\\python.exe\"",
        "$Device = \"cpu\"",
        "$TrainOnPass = 0",
        "$RunPytest = 1",
        "$Grid = @(",
        "NStates = 50",
        "CandidateActions = 16",
        "CandidateActions = 20",
        "CandidateActions = 24",
        "FrontierFraction = 0.75",
        "FrontierFraction = 1.0",
        "LabelSeed = 46",
        "GateTopKs = @(3, 4, 5)",
        "Require-Path (Join-Path $DataRoot \"tool2/transitions.npz\")",
        "Require-Path (Join-Path $DataRoot \"tool2/pairwise.npz\")",
        "Require-Path (Join-Path $DataRoot \"dem_slope_analysis/output/DLTB_with_slope.gpkg\")",
        "Require-Path (Join-Path $DataRoot \"results_real/blocks\")",
        "Require-Path (Join-Path $DataRoot \"townships.json\")",
        "paper10_geojepa_mpc.experiments.value_label_generation",
        "--candidate-mode frontier_random",
        "--frontier-fraction",
        "--partial-output",
        "paper10_geojepa_mpc.experiments.value_label_diagnostics",
        "paper10_geojepa_mpc.experiments.value_label_monitor",
        "paper10_geojepa_mpc.experiments.run_e0_value_head_train",
        "if ($TrainOnPass -eq 1 -and $PassingTopKs.Count -gt 0)",
        "ConvertTo-Json -Depth 8",
        "frontier_random050_ablation_summary.json",
        "frontier_random050_ablation_summary.md",
    ]
    for token in required_tokens:
        assert token in text


def test_windows_runner_captures_native_stderr_without_native_command_error():
    text = _read(RUNNER)

    required_tokens = [
        "Start-Process",
        "-RedirectStandardOutput",
        "-RedirectStandardError",
        "$Process.ExitCode",
        "Get-Content -LiteralPath $StdoutTemp",
        "Get-Content -LiteralPath $StderrTemp",
    ]
    for token in required_tokens:
        assert token in text

    assert "& $File @Arguments 2>&1 | Tee-Object" not in text


def test_windows_env_template_documents_local_overrides():
    text = _read(ENV_TEMPLATE)

    required_tokens = [
        "$DataRoot = \"D:\\test\"",
        "$RunRoot = \"D:\\test\\paper10_runs\"",
        "$PythonBin = \"D:\\adk\\.venv\\Scripts\\python.exe\"",
        "$Device = \"cpu\"",
        "$TrainOnPass = 0",
        "$RunPytest = 1",
        "$GateTopKs = @(3, 4, 5)",
        "NStates = 50",
        "CandidateActions = 16",
        "CandidateActions = 20",
        "CandidateActions = 24",
        "FrontierFraction = 1.0",
        "LabelSeed = 46",
    ]
    for token in required_tokens:
        assert token in text


def test_windows_guide_explains_cpu_data_root_and_gate_flow():
    text = _read(GUIDE)

    required_tokens = [
        "Windows",
        "D:\\test",
        "D:\\adk\\.venv\\Scripts\\python.exe",
        "CUDA is not required",
        "CPU",
        "tool2/transitions.npz",
        "tool2/pairwise.npz",
        "DLTB_with_slope.gpkg",
        "results_real/blocks",
        "townships.json",
        "scripts/windows/frontier_random050_ablation.env.example.ps1",
        "scripts/windows/run_frontier_random050_ablation_grid.ps1",
        "TrainOnPass = 0",
        "TrainOnPass = 1",
        "monitor gate",
        "frontier_random050_ablation_summary.md",
        "50x24/h5 seed45",
    ]
    for token in required_tokens:
        assert token in text


def test_repository_docs_reference_windows_ablation_package():
    readme = _read(ROOT / "README.md")
    repro = _read(ROOT / "REPRODUCIBILITY.md")
    manifest = _read(ROOT / "MANIFEST.md")
    guide_path = "docs/windows_frontier_random050_ablation.md"
    runner_path = "scripts/windows/run_frontier_random050_ablation_grid.ps1"

    for text in (readme, repro, manifest):
        assert guide_path in text
        assert runner_path in text


def test_windows_local_env_is_ignored_and_uses_crlf():
    gitignore = _read(ROOT / ".gitignore")
    gitattributes = _read(ROOT / ".gitattributes")

    assert "/scripts/windows/frontier_random050_ablation.env.ps1" in gitignore
    assert "scripts/windows/*.ps1 text eol=crlf" in gitattributes
