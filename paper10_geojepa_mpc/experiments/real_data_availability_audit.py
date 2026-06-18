import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DATE = "2026-06-18"


@dataclass(frozen=True)
class DataFamily:
    family_id: str
    label: str
    required_paths: tuple[str, ...]
    optional_paths: tuple[str, ...]
    claim_dependency: str
    manuscript_blocker: str
    external_to_git: bool = True


def default_data_root() -> Path:
    candidate = Path("D:/test")
    if candidate.exists():
        return candidate
    return Path.cwd()


def default_data_families() -> list[DataFamily]:
    return [
        DataFamily(
            family_id="bishan_tool2_full",
            label="Full Bishan Tool2 arrays",
            required_paths=("tool2/transitions.npz", "tool2/pairwise.npz"),
            optional_paths=(),
            claim_dependency="Bishan full-data training and rollout reruns",
            manuscript_blocker="Full Bishan Tool2 access route",
        ),
        DataFamily(
            family_id="bishan_gpkg_root",
            label="Bishan slope-enriched geospatial root",
            required_paths=("dem_slope_analysis/output/DLTB_with_slope.gpkg",),
            optional_paths=(
                "dem_slope_analysis/output/DLTB_with_slope.shp",
                "dem_slope_analysis/output/DLTB_with_slope.dbf",
                "dem_slope_analysis/output/DLTB_with_slope.shx",
                "dem_slope_analysis/output/DLTB_with_slope.prj",
            ),
            claim_dependency="Executable-mask real-environment rollouts",
            manuscript_blocker="GPKG-root geospatial input route",
        ),
        DataFamily(
            family_id="bishan_rollout_inputs",
            label="Bishan prepared block and township inputs",
            required_paths=("results_real/blocks", "townships.json"),
            optional_paths=(),
            claim_dependency="Full Bishan rollout reproduction",
            manuscript_blocker="GPKG-root geospatial input route",
        ),
        DataFamily(
            family_id="dongxing_cloud_primary",
            label="Dongxing/Neijiang primary prepared-results directory",
            required_paths=("G:/我的云端硬盘/paper4_results/dongxing",),
            optional_paths=(
                "G:/我的云端硬盘/paper4_results/dongxing/colab_timing.json",
                "G:/我的云端硬盘/paper4_results/dongxing/marl_eval_seed0.json",
                "G:/我的云端硬盘/paper4_results/dongxing/county_eval_seed0.json",
            ),
            claim_dependency="External-region full reruns and timing audit",
            manuscript_blocker="Dongxing/Neijiang prepared-data route",
        ),
        DataFamily(
            family_id="dongxing_cloud_alternate",
            label="Dongxing/Neijiang alternate prepared-results directory",
            required_paths=("G:/我的云端硬盘/paper4_results/dongxing1",),
            optional_paths=(),
            claim_dependency="External-region path fallback",
            manuscript_blocker="Dongxing/Neijiang prepared-data route",
        ),
        DataFamily(
            family_id="dongxing_local_candidate",
            label="Dongxing/Neijiang local prepared-results directory",
            required_paths=("D:/test/dongxing",),
            optional_paths=(),
            claim_dependency="External-region local rerun fallback",
            manuscript_blocker="Dongxing/Neijiang prepared-data route",
        ),
    ]


def _resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _file_stats(path: Path) -> tuple[int, int]:
    if path.is_file():
        return 1, path.stat().st_size
    if not path.is_dir():
        return 0, 0

    file_count = 0
    byte_count = 0
    for child in path.rglob("*"):
        if not child.is_file():
            continue
        try:
            byte_count += child.stat().st_size
        except OSError:
            continue
        file_count += 1
    return file_count, byte_count


def _status(required_count: int, present_required_count: int) -> str:
    if present_required_count == required_count:
        return "available"
    if present_required_count == 0:
        return "missing"
    return "partial"


def audit_data_families(root: str | Path, families: Iterable[DataFamily]) -> list[dict]:
    root_path = Path(root)
    rows = []
    for family in families:
        required = [_resolve_path(root_path, item) for item in family.required_paths]
        optional = [_resolve_path(root_path, item) for item in family.optional_paths]
        present_required = [path for path in required if path.exists()]
        missing_required = [path for path in required if not path.exists()]
        present_optional = [path for path in optional if path.exists()]
        missing_optional = [path for path in optional if not path.exists()]

        file_count = 0
        byte_count = 0
        for path in present_required + present_optional:
            files, bytes_present = _file_stats(path)
            file_count += files
            byte_count += bytes_present

        rows.append(
            {
                "family_id": family.family_id,
                "label": family.label,
                "status": _status(len(required), len(present_required)),
                "required_count": len(required),
                "present_required_count": len(present_required),
                "file_count_present": file_count,
                "bytes_present": byte_count,
                "required_paths": [str(path) for path in required],
                "present_required_paths": [str(path) for path in present_required],
                "missing_required_paths": [str(path) for path in missing_required],
                "optional_present_paths": [str(path) for path in present_optional],
                "optional_missing_paths": [str(path) for path in missing_optional],
                "claim_dependency": family.claim_dependency,
                "manuscript_blocker": family.manuscript_blocker,
                "external_to_git": family.external_to_git,
            }
        )
    return rows


def _summary(rows: list[dict]) -> dict[str, int]:
    return {
        "available": sum(1 for row in rows if row["status"] == "available"),
        "partial": sum(1 for row in rows if row["status"] == "partial"),
        "missing": sum(1 for row in rows if row["status"] == "missing"),
    }


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
        "# Paper10 real-data availability audit",
        "",
        f"Date: {payload['date']}",
        f"Audited root: `{payload['root']}`",
        "",
        "Status: external-dependency audit for manuscript and rerun planning. This is not a data-rights approval, not a redistribution record, and not evidence that restricted datasets may be deposited.",
        "",
        "The audit records path existence, file counts, and byte totals only; raw geospatial data are not copied into Git.",
        "",
        "## Summary",
        "",
        "| status | data families |",
        "|---|---:|",
    ]
    for key in ("available", "partial", "missing"):
        lines.append(f"| {key} | {payload['summary'].get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Data Families",
            "",
            "| family | status | required paths present | files | bytes | manuscript blocker | claim dependency |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in payload["families"]:
        lines.append(
            "| {label} | {status} | {present}/{required} | {files} | {bytes_label} | {blocker} | {dependency} |".format(
                label=row["label"],
                status=row["status"],
                present=row["present_required_count"],
                required=row["required_count"],
                files=row["file_count_present"],
                bytes_label=_format_bytes(int(row["bytes_present"])),
                blocker=row["manuscript_blocker"],
                dependency=row["claim_dependency"],
            )
        )

    lines.extend(["", "## Missing Required Paths", ""])
    for row in payload["families"]:
        if not row["missing_required_paths"]:
            continue
        lines.append(f"### {row['label']}")
        lines.append("")
        for path in row["missing_required_paths"]:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.extend(["## Optional Paths Present", ""])
    optional_any = False
    for row in payload["families"]:
        if not row["optional_present_paths"]:
            continue
        optional_any = True
        lines.append(f"### {row['label']}")
        lines.append("")
        for path in row["optional_present_paths"]:
            lines.append(f"- `{path}`")
        lines.append("")
    if not optional_any:
        lines.append("No optional paths were present during this audit.")
        lines.append("")

    lines.extend(
        [
            "## Interpretation Boundary",
            "",
            "This report is a readiness map for reruns and Data Availability backfill. It does not change any performance claim. Missing or partial rows identify access or placement blockers that must be closed before full reruns or final manuscript submission wording.",
            "",
            "## Regeneration command",
            "",
            "```powershell",
            "D:\\adk\\.venv\\Scripts\\python.exe -m paper10_geojepa_mpc.experiments.real_data_availability_audit --root D:\\test --output-json paper10_geojepa_mpc\\experiments\\results\\e0_paper10_real_data_availability_audit_2026-06-18.json --output-md paper10_geojepa_mpc\\experiments\\results\\e0_paper10_real_data_availability_audit_2026-06-18.md",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_real_data_availability(
    root: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    families: Iterable[DataFamily] | None = None,
    date: str = DATE,
) -> dict:
    root_path = Path(root)
    data_families = list(families) if families is not None else default_data_families()
    rows = audit_data_families(root_path, data_families)
    payload = {
        "date": date,
        "root": str(root_path),
        "families": rows,
        "summary": _summary(rows),
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
        / "e0_paper10_real_data_availability_audit_2026-06-18.json",
    )
    parser.add_argument(
        "--output-md",
        default=Path("paper10_geojepa_mpc")
        / "experiments"
        / "results"
        / "e0_paper10_real_data_availability_audit_2026-06-18.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_real_data_availability(
        root=args.root,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
