import json
import sqlite3

import numpy as np

from paper10_geojepa_mpc.experiments.real_data_integrity_smoke import (
    audit_real_data_integrity,
    inspect_directory,
    inspect_geopackage,
    inspect_json_file,
    inspect_npz_headers,
    markdown_report,
)


def test_inspect_npz_headers_reads_array_metadata(tmp_path):
    npz_path = tmp_path / "sample.npz"
    np.savez(
        npz_path,
        states=np.zeros((3, 4), dtype=np.float32),
        actions=np.arange(5, dtype=np.int64),
    )

    result = inspect_npz_headers(npz_path)

    assert result["status"] == "readable"
    assert result["file_count"] == 2
    assert result["arrays"]["states"] == {
        "shape": [3, 4],
        "dtype": "float32",
        "fortran_order": False,
    }
    assert result["arrays"]["actions"]["shape"] == [5]


def test_inspect_geopackage_reads_sqlite_metadata_only(tmp_path):
    gpkg_path = tmp_path / "sample.gpkg"
    with sqlite3.connect(gpkg_path) as conn:
        conn.execute(
            "CREATE TABLE gpkg_contents (table_name TEXT, data_type TEXT, identifier TEXT)"
        )
        conn.execute(
            "CREATE TABLE gpkg_geometry_columns (table_name TEXT, column_name TEXT, geometry_type_name TEXT)"
        )
        conn.execute("CREATE TABLE parcels (id INTEGER PRIMARY KEY, slope REAL)")
        conn.execute(
            "INSERT INTO gpkg_contents VALUES ('parcels', 'features', 'parcels')"
        )
        conn.execute(
            "INSERT INTO gpkg_geometry_columns VALUES ('parcels', 'geom', 'MULTIPOLYGON')"
        )

    result = inspect_geopackage(gpkg_path)

    assert result["status"] == "readable"
    assert "gpkg_contents" in result["table_names"]
    assert result["contents"] == [
        {
            "table_name": "parcels",
            "data_type": "features",
            "identifier": "parcels",
        }
    ]
    assert result["geometry_columns"][0]["geometry_type_name"] == "MULTIPOLYGON"


def test_inspect_directory_and_json_file_summarize_without_payload(tmp_path):
    root = tmp_path / "dongxing"
    root.mkdir()
    (root / "metrics.json").write_text(
        json.dumps({"reward": 1.0, "seed": 0, "nested": {"ignored": True}}),
        encoding="utf-8",
    )
    (root / "summary.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    directory = inspect_directory(root)
    json_summary = inspect_json_file(root / "metrics.json")

    assert directory["status"] == "readable"
    assert directory["file_count"] == 2
    assert directory["extension_counts"] == {".csv": 1, ".json": 1}
    assert "metrics.json" in directory["sample_files"]
    assert json_summary["top_level_type"] == "dict"
    assert json_summary["top_level_keys"] == ["nested", "reward", "seed"]
    assert "reward" not in json.dumps(json_summary.get("sample_values", {}))


def test_audit_real_data_integrity_writes_json_and_markdown(tmp_path):
    npz_path = tmp_path / "tool2" / "transitions.npz"
    npz_path.parent.mkdir()
    np.savez(npz_path, transitions=np.zeros((2, 3), dtype=np.float32))
    gpkg_path = tmp_path / "data.gpkg"
    with sqlite3.connect(gpkg_path) as conn:
        conn.execute(
            "CREATE TABLE gpkg_contents (table_name TEXT, data_type TEXT, identifier TEXT)"
        )
    blocks = tmp_path / "blocks"
    blocks.mkdir()
    (blocks / "block0.json").write_text("{}", encoding="utf-8")

    output_json = tmp_path / "integrity.json"
    output_md = tmp_path / "integrity.md"
    payload = audit_real_data_integrity(
        root=tmp_path,
        output_json=output_json,
        output_md=output_md,
        npz_paths=[npz_path],
        gpkg_paths=[gpkg_path],
        directory_paths=[blocks],
        json_paths=[],
        date="2026-06-18",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    text = output_md.read_text(encoding="utf-8")
    assert text == markdown_report(payload)
    assert "NPZ header smoke" in text
    assert "GeoPackage metadata smoke" in text
    assert "Directory smoke" in text
    assert "raw row values are not exported" in text
    assert "direct 50-state success" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
