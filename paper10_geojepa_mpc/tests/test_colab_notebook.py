import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebooks" / "paper10_frontier_random050_50x24_h5_colab.ipynb"


def _load_notebook() -> dict:
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


def _source_text(notebook: dict) -> str:
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
    )


def test_colab_notebook_is_python3_parseable_json():
    notebook = _load_notebook()

    assert notebook["nbformat"] == 4
    assert notebook["metadata"]["kernelspec"]["name"] == "python3"
    assert notebook["metadata"]["language_info"]["name"] == "python"
    assert "colab" in notebook["metadata"]
    assert len(notebook["cells"]) >= 12


def test_colab_notebook_documents_objective_and_parameters():
    text = _source_text(_load_notebook())

    required_tokens = [
        "frontier_random050",
        "50x24/h5",
        "REPO_URL",
        "REPO_BRANCH",
        "DRIVE_PROJECT_DIR",
        "n_states=50",
        "candidate_actions=24",
        "label_horizon=5",
        "label_seed=45",
        "training_seed=3045",
        "rollout_seeds_optional='1-4'",
        "Outputs are written to Google Drive",
        ".partial.npz",
        "final artifacts already exist",
    ]
    for token in required_tokens:
        assert token in text


def test_colab_notebook_validates_full_data_layout_and_smoke_tests():
    text = _source_text(_load_notebook())

    required_tokens = [
        "drive.mount('/content/drive')",
        "git clone",
        "git fetch origin",
        "pip install -r requirements.txt",
        "tool2/transitions.npz",
        "tool2/pairwise.npz",
        "dem_slope_analysis/output/DLTB_with_slope.gpkg",
        "dem_slope_analysis/output/DLTB_with_slope.shp",
        "results_real/blocks",
        "townships.json",
        "pytest paper10_geojepa_mpc/tests -q -p no:cacheprovider",
    ]
    for token in required_tokens:
        assert token in text


def test_colab_notebook_contains_resumable_experiment_commands():
    text = _source_text(_load_notebook())

    required_tokens = [
        "paper10_geojepa_mpc.experiments.value_label_generation",
        "--n-states 50",
        "--candidate-actions 24",
        "--label-horizon 5",
        "--candidate-mode frontier_random",
        "--frontier-fraction 0.5",
        "--partial-output",
        "paper10_geojepa_mpc.experiments.value_label_diagnostics",
        "paper10_geojepa_mpc.experiments.value_label_monitor",
        "--top-k 3",
        "--top-k 4",
        "--top-k 5",
        "selected_top_k",
        "paper10_geojepa_mpc.experiments.run_e0_value_head_train",
        "--device {device}",
        "--candidate-top-k {selected_top_k}",
        "paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke",
        "--selector value_filter",
        "--candidate-score-mode blend",
        "--candidate-value-weight 0.05",
        "--candidate-value-weight 0.10",
        "--rollout-steps 20",
        "--rollout-steps 100",
        "--seed 0",
        "--seeds 1-4",
        "zipfile.ZipFile",
    ]
    for token in required_tokens:
        assert token in text


def test_colab_notebook_uses_colab_paths_not_windows_paths():
    text = _source_text(_load_notebook())

    forbidden_tokens = [
        "D:\\",
        ".\\.venv",
        "\\Scripts\\python.exe",
        "reviewer_outputs\\",
        "tool2\\transitions.npz",
    ]
    for token in forbidden_tokens:
        assert token not in text

    assert "/content/" in text
    assert "MyDrive" in text


def test_readme_and_manifest_reference_colab_notebook():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    manifest = (ROOT / "MANIFEST.md").read_text(encoding="utf-8")
    notebook_path = "notebooks/paper10_frontier_random050_50x24_h5_colab.ipynb"

    assert notebook_path in readme
    assert "50x24/h5" in readme
    assert notebook_path in manifest
