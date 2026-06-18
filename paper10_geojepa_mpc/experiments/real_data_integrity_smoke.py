import argparse
import json
import sqlite3
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import numpy as np
from numpy.lib import format as np_format


DATE = "2026-06-18"


def default_data_root() -> Path:
    candidate = Path("D:/test")
    if candidate.exists():
        return candidate
    return Path.cwd()


def _resolve(root: Path, path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return root / value


def _base_result(path: Path, kind: str) -> dict:
    return {
        "kind": kind,
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def inspect_npz_headers(path: str | Path) -> dict:
    target = Path(path)
    result = _base_result(target, "npz")
    if not target.exists():
        result.update({"status": "missing", "arrays": {}, "file_count": 0})
        return result

    try:
        arrays = {}
        with ZipFile(target) as archive:
            for member in archive.namelist():
                if not member.endswith(".npy"):
                    continue
                name = Path(member).stem
                with archive.open(member) as handle:
                    version = np_format.read_magic(handle)
                    if version == (1, 0):
                        shape, fortran_order, dtype = np_format.read_array_header_1_0(
                            handle
                        )
                    elif version == (2, 0):
                        shape, fortran_order, dtype = np_format.read_array_header_2_0(
                            handle
                        )
                    else:
                        raise ValueError(f"unsupported npy header version: {version}")
                arrays[name] = {
                    "shape": list(shape),
                    "dtype": str(dtype),
                    "fortran_order": bool(fortran_order),
                }
        result.update({"status": "readable", "arrays": arrays, "file_count": len(arrays)})
    except (OSError, ValueError, BadZipFile) as exc:
        result.update({"status": "unreadable", "error": str(exc), "arrays": {}, "file_count": 0})
    return result


def _sqlite_rows(conn: sqlite3.Connection, query: str, columns: list[str]) -> list[dict]:
    try:
        cursor = conn.execute(query)
    except sqlite3.DatabaseError:
        return []
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def inspect_geopackage(path: str | Path) -> dict:
    target = Path(path)
    result = _base_result(target, "geopackage")
    if not target.exists():
        result.update(
            {
                "status": "missing",
                "table_names": [],
                "contents": [],
                "geometry_columns": [],
            }
        )
        return result

    try:
        with sqlite3.connect(f"file:{target}?mode=ro", uri=True) as conn:
            table_names = [
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ).fetchall()
            ]
            contents = _sqlite_rows(
                conn,
                "SELECT table_name, data_type, identifier FROM gpkg_contents ORDER BY table_name",
                ["table_name", "data_type", "identifier"],
            )
            geometry_columns = _sqlite_rows(
                conn,
                "SELECT table_name, column_name, geometry_type_name FROM gpkg_geometry_columns ORDER BY table_name, column_name",
                ["table_name", "column_name", "geometry_type_name"],
            )
        result.update(
            {
                "status": "readable",
                "table_names": table_names,
                "contents": contents,
                "geometry_columns": geometry_columns,
            }
        )
    except sqlite3.DatabaseError as exc:
        result.update(
            {
                "status": "unreadable",
                "error": str(exc),
                "table_names": [],
                "contents": [],
                "geometry_columns": [],
            }
        )
    return result


def inspect_directory(path: str | Path, sample_limit: int = 12) -> dict:
    target = Path(path)
    result = _base_result(target, "directory")
    if not target.exists():
        result.update(
            {
                "status": "missing",
                "file_count": 0,
                "bytes": 0,
                "extension_counts": {},
                "sample_files": [],
            }
        )
        return result
    if not target.is_dir():
        result.update(
            {
                "status": "not_directory",
                "file_count": 0,
                "extension_counts": {},
                "sample_files": [],
            }
        )
        return result

    extension_counts: dict[str, int] = {}
    sample_files = []
    file_count = 0
    bytes_total = 0
    for child in sorted(target.rglob("*")):
        if not child.is_file():
            continue
        file_count += 1
        try:
            bytes_total += child.stat().st_size
        except OSError:
            pass
        suffix = child.suffix.lower() or "<none>"
        extension_counts[suffix] = extension_counts.get(suffix, 0) + 1
        if len(sample_files) < sample_limit:
            sample_files.append(str(child.relative_to(target)))

    result.update(
        {
            "status": "readable",
            "file_count": file_count,
            "bytes": bytes_total,
            "extension_counts": dict(sorted(extension_counts.items())),
            "sample_files": sample_files,
        }
    )
    return result


def inspect_json_file(path: str | Path) -> dict:
    target = Path(path)
    result = _base_result(target, "json")
    if not target.exists():
        result.update({"status": "missing", "top_level_type": None, "top_level_keys": []})
        return result

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        result.update({"status": "unreadable", "error": str(exc), "top_level_type": None, "top_level_keys": []})
        return result

    if isinstance(payload, dict):
        keys = sorted(str(key) for key in payload.keys())
        top_level_type = "dict"
    elif isinstance(payload, list):
        keys = []
        top_level_type = "list"
    else:
        keys = []
        top_level_type = type(payload).__name__
    result.update(
        {
            "status": "readable",
            "top_level_type": top_level_type,
            "top_level_keys": keys,
            "item_count": len(payload) if isinstance(payload, (dict, list)) else None,
        }
    )
    return result


def default_npz_paths(root: Path) -> list[Path]:
    return [
        root / "tool2" / "transitions.npz",
        root / "tool2" / "pairwise.npz",
    ]


def default_gpkg_paths(root: Path) -> list[Path]:
    return [root / "dem_slope_analysis" / "output" / "DLTB_with_slope.gpkg"]


def default_directory_paths(root: Path) -> list[Path]:
    return [
        root / "results_real" / "blocks",
        Path("G:/我的云端硬盘/paper4_results/dongxing"),
        Path("G:/我的云端硬盘/paper4_results/dongxing1"),
    ]


def default_json_paths(root: Path) -> list[Path]:
    return [
        root / "townships.json",
        Path("G:/我的云端硬盘/paper4_results/dongxing/colab_timing.json"),
        Path("G:/我的云端硬盘/paper4_results/dongxing/marl_eval_seed0.json"),
        Path("G:/我的云端硬盘/paper4_results/dongxing/county_eval_seed0.json"),
    ]


def _status_counts(groups: dict[str, list[dict]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rows in groups.values():
        for row in rows:
            status = row.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _format_bytes(value: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    amount = float(value)
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(amount)} {unit}"
            return f"{amount:.2f} {unit}"
        amount /= 1024.0
    return f"{value} B"


def markdown_report(payload: dict) -> str:
    lines = [
        "# Paper10 real-data integrity smoke",
        "",
        f"Date: {payload['date']}",
        f"Audited root: `{payload['root']}`",
        "",
        "Status: metadata-only smoke audit for real-data readability. NPZ arrays are read for headers, GeoPackage files are read through SQLite metadata tables, directories are summarized by extension and size, and raw row values are not exported.",
        "",
        "## Summary",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status, count in payload["summary"].items():
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## NPZ header smoke",
            "",
            "| path | status | arrays | bytes |",
            "|---|---|---:|---:|",
        ]
    )
    for row in payload["npz"]:
        lines.append(
            f"| `{row['path']}` | {row['status']} | {row.get('file_count', 0)} | {_format_bytes(int(row.get('bytes', 0)))} |"
        )

    lines.extend(["", "## NPZ arrays", ""])
    for row in payload["npz"]:
        if not row.get("arrays"):
            continue
        lines.append(f"### `{row['path']}`")
        lines.append("")
        lines.append("| array | shape | dtype |")
        lines.append("|---|---|---|")
        for name, meta in row["arrays"].items():
            lines.append(f"| {name} | `{meta['shape']}` | `{meta['dtype']}` |")
        lines.append("")

    lines.extend(
        [
            "## GeoPackage metadata smoke",
            "",
            "| path | status | tables | feature layers | geometry columns | bytes |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in payload["geopackage"]:
        lines.append(
            "| `{path}` | {status} | {tables} | {contents} | {geometry} | {bytes_label} |".format(
                path=row["path"],
                status=row["status"],
                tables=len(row.get("table_names", [])),
                contents=len(row.get("contents", [])),
                geometry=len(row.get("geometry_columns", [])),
                bytes_label=_format_bytes(int(row.get("bytes", 0))),
            )
        )

    lines.extend(
        [
            "",
            "## Directory smoke",
            "",
            "| path | status | files | bytes | extensions |",
            "|---|---|---:|---:|---|",
        ]
    )
    for row in payload["directories"]:
        extensions = ", ".join(
            f"{key}:{value}" for key, value in row.get("extension_counts", {}).items()
        )
        lines.append(
            f"| `{row['path']}` | {row['status']} | {row.get('file_count', 0)} | {_format_bytes(int(row.get('bytes', 0)))} | {extensions or 'none'} |"
        )

    lines.extend(
        [
            "",
            "## JSON schema smoke",
            "",
            "| path | status | top-level type | top-level keys | bytes |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in payload["json"]:
        keys = ", ".join(row.get("top_level_keys", []))
        lines.append(
            f"| `{row['path']}` | {row['status']} | {row.get('top_level_type')} | {keys or 'none'} | {_format_bytes(int(row.get('bytes', 0)))} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This smoke audit supports data-readiness and rerun planning only. It does not change Paper10 performance claims, does not export restricted rows or geometries, and does not replace data-rights approval.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.real_data_integrity_smoke --root D:\\test --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_real_data_integrity_smoke_2026-06-18.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_real_data_integrity_smoke_2026-06-18.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_real_data_integrity(
    root: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    npz_paths: list[str | Path] | None = None,
    gpkg_paths: list[str | Path] | None = None,
    directory_paths: list[str | Path] | None = None,
    json_paths: list[str | Path] | None = None,
    date: str = DATE,
) -> dict:
    root_path = Path(root)
    npz_targets = [
        _resolve(root_path, path)
        for path in (npz_paths if npz_paths is not None else default_npz_paths(root_path))
    ]
    gpkg_targets = [
        _resolve(root_path, path)
        for path in (gpkg_paths if gpkg_paths is not None else default_gpkg_paths(root_path))
    ]
    directory_targets = [
        _resolve(root_path, path)
        for path in (
            directory_paths
            if directory_paths is not None
            else default_directory_paths(root_path)
        )
    ]
    json_targets = [
        _resolve(root_path, path)
        for path in (json_paths if json_paths is not None else default_json_paths(root_path))
    ]

    groups = {
        "npz": [inspect_npz_headers(path) for path in npz_targets],
        "geopackage": [inspect_geopackage(path) for path in gpkg_targets],
        "directories": [inspect_directory(path) for path in directory_targets],
        "json": [inspect_json_file(path) for path in json_targets],
    }
    payload = {
        "date": date,
        "root": str(root_path),
        **groups,
        "summary": _status_counts(groups),
    }

    output_json_path = Path(output_json)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    output_md_path = Path(output_md)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=default_data_root())
    parser.add_argument(
        "--output-json",
        default=Path("paper10_geojepa_mpc")
        / "experiments"
        / "results"
        / "e0_paper10_real_data_integrity_smoke_2026-06-18.json",
    )
    parser.add_argument(
        "--output-md",
        default=Path("paper10_geojepa_mpc")
        / "experiments"
        / "results"
        / "e0_paper10_real_data_integrity_smoke_2026-06-18.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_real_data_integrity(
        root=args.root,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
