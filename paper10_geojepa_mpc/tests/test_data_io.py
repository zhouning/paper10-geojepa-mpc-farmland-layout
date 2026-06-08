from pathlib import Path

from paper10_geojepa_mpc.training.data_io import summarize_npz_headers


def test_summarize_npz_headers_reads_smoke_pairwise_shapes():
    path = Path("arcgis_toolbox_paper9/_scratch/tool1_smoke/prepared/tool2/pairwise.npz")

    summary = summarize_npz_headers(path)

    assert summary["states_bf"]["shape"] == (100, 30, 17)
    assert summary["states_gf"]["shape"] == (100, 12)
    assert summary["actions"]["shape"] == (100, 10)
    assert summary["rewards"]["shape"] == (100, 10)
    assert summary["rewards"]["dtype"] == "float32"
