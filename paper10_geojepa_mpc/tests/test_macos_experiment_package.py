from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "macos" / "run_frontier_random050_50x24_h5.sh"
ENV_TEMPLATE = ROOT / "scripts" / "macos" / "frontier_random050_50x24_h5.env.example"
GUIDE = ROOT / "docs" / "macos_frontier_random050_50x24_h5.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_macos_runner_is_posix_shell_and_resumable():
    text = _read(RUNNER)

    required_tokens = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "DATA_ROOT=",
        "RUN_ROOT=",
        "DEVICE=",
        "N_STATES=50",
        "CANDIDATE_ACTIONS=24",
        "LABEL_HORIZON=5",
        "LABEL_SEED=45",
        "TRAINING_SEED=3045",
        "require_path \"$DATA_ROOT/tool2/transitions.npz\"",
        "require_any_path",
        "dem_slope_analysis/output/DLTB_with_slope.gpkg",
        "dem_slope_analysis/output/DLTB_with_slope.shp",
        "dem_slope_analysis/output/DLTB_with_slope.dbf",
        "dem_slope_analysis/output/DLTB_with_slope.shx",
        "run_if_missing",
        "value_label_generation",
        "--candidate-mode frontier_random",
        "--frontier-fraction 0.5",
        "--partial-output",
        "value_label_diagnostics",
        "value_label_monitor",
        "--top-k 3",
        "--top-k 4",
        "--top-k 5",
        "selected_top_k",
        "run_e0_value_head_train",
        "--candidate-top-k \"$selected_top_k\"",
        "run_e0_env_rollout_smoke",
        "--candidate-value-weight 0.05",
        "--candidate-value-weight 0.10",
        "--rollout-steps 20",
        "--rollout-steps 100",
        "--seed 0",
        "RUN_OPTIONAL_SEEDS",
        "--seeds 1-4",
        "zip -r",
    ]
    for token in required_tokens:
        assert token in text


def test_macos_env_template_documents_local_overrides():
    text = _read(ENV_TEMPLATE)

    required_tokens = [
        "DATA_ROOT=/Volumes/",
        "RUN_ROOT=$HOME/paper10_runs",
        "DEVICE=cpu",
        "RUN_OPTIONAL_SEEDS=0",
        "PYTHON_BIN=python3",
        "N_STATES=50",
        "CANDIDATE_ACTIONS=24",
        "LABEL_HORIZON=5",
    ]
    for token in required_tokens:
        assert token in text


def test_macos_guide_explains_pull_data_and_resume_flow():
    text = _read(GUIDE)

    required_tokens = [
        "macOS",
        "git pull",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "DATA_ROOT",
        "tool2/transitions.npz",
        "tool2/pairwise.npz",
        "results_real/blocks/",
        "townships.json",
        "DLTB_with_slope.gpkg",
        "DLTB_with_slope.shp",
        "scripts/macos/frontier_random050_50x24_h5.env.example",
        "scripts/macos/run_frontier_random050_50x24_h5.sh",
        "RUN_OPTIONAL_SEEDS=1",
        "final artifact already exists",
        ".partial.npz",
        "50x24/h5",
    ]
    for token in required_tokens:
        assert token in text


def test_repository_docs_reference_macos_experiment_package():
    readme = _read(ROOT / "README.md")
    repro = _read(ROOT / "REPRODUCIBILITY.md")
    manifest = _read(ROOT / "MANIFEST.md")
    guide_path = "docs/macos_frontier_random050_50x24_h5.md"
    runner_path = "scripts/macos/run_frontier_random050_50x24_h5.sh"

    for text in (readme, repro, manifest):
        assert guide_path in text
        assert runner_path in text


def test_macos_local_env_is_ignored_and_shell_uses_lf():
    gitignore = _read(ROOT / ".gitignore")
    gitattributes = _read(ROOT / ".gitattributes")

    assert "/scripts/macos/frontier_random050_50x24_h5.env" in gitignore
    assert "scripts/macos/*.sh text eol=lf" in gitattributes
