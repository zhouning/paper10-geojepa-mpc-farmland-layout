import json

from paper10_geojepa_mpc.experiments.real_data_availability_audit import (
    DataFamily,
    audit_data_families,
    audit_real_data_availability,
    markdown_report,
)


def test_audit_data_families_counts_existing_files_and_missing_required_paths(tmp_path):
    transitions = tmp_path / "tool2" / "transitions.npz"
    transitions.parent.mkdir()
    transitions.write_bytes(b"12345")
    missing_pairwise = tmp_path / "tool2" / "pairwise.npz"
    blocks = tmp_path / "results_real" / "blocks"
    blocks.mkdir(parents=True)
    (blocks / "blocks.geojson").write_text("{}", encoding="utf-8")

    rows = audit_data_families(
        tmp_path,
        [
            DataFamily(
                family_id="bishan_tool2_full",
                label="Full Bishan Tool2 arrays",
                required_paths=("tool2/transitions.npz", "tool2/pairwise.npz"),
                optional_paths=(),
                claim_dependency="Bishan full-data training and rollout reruns",
                manuscript_blocker="Full Bishan Tool2 access route",
            ),
            DataFamily(
                family_id="bishan_blocks",
                label="Bishan prepared block products",
                required_paths=("results_real/blocks",),
                optional_paths=(),
                claim_dependency="Executable-mask real-environment rollouts",
                manuscript_blocker="GPKG-root geospatial input route",
            ),
        ],
    )

    by_id = {row["family_id"]: row for row in rows}
    assert by_id["bishan_tool2_full"]["status"] == "partial"
    assert by_id["bishan_tool2_full"]["present_required_count"] == 1
    assert by_id["bishan_tool2_full"]["missing_required_paths"] == [
        str(missing_pairwise)
    ]
    assert by_id["bishan_tool2_full"]["bytes_present"] == 5
    assert by_id["bishan_blocks"]["status"] == "available"
    assert by_id["bishan_blocks"]["file_count_present"] == 1
    assert by_id["bishan_blocks"]["bytes_present"] == 2


def test_audit_real_data_availability_writes_json_and_markdown(tmp_path):
    output_json = tmp_path / "audit.json"
    output_md = tmp_path / "audit.md"
    (tmp_path / "tool2").mkdir()
    (tmp_path / "tool2" / "transitions.npz").write_bytes(b"abc")
    (tmp_path / "tool2" / "pairwise.npz").write_bytes(b"defg")

    payload = audit_real_data_availability(
        root=tmp_path,
        output_json=output_json,
        output_md=output_md,
        families=[
            DataFamily(
                family_id="bishan_tool2_full",
                label="Full Bishan Tool2 arrays",
                required_paths=("tool2/transitions.npz", "tool2/pairwise.npz"),
                optional_paths=(),
                claim_dependency="Bishan full-data training and rollout reruns",
                manuscript_blocker="Full Bishan Tool2 access route",
            )
        ],
        date="2026-06-18",
    )

    assert payload == json.loads(output_json.read_text(encoding="utf-8"))
    text = output_md.read_text(encoding="utf-8")
    assert text == markdown_report(payload)
    assert "Full Bishan Tool2 arrays" in text
    assert "available" in text
    assert "Full Bishan Tool2 access route" in text
    assert "raw geospatial data are not copied into Git" in text
    assert "direct 50-state success" not in text.lower()


def test_markdown_report_records_submission_blockers_without_claiming_readiness():
    text = markdown_report(
        {
            "date": "2026-06-18",
            "root": "D:\\test",
            "families": [
                {
                    "family_id": "dongxing_prepared",
                    "label": "Dongxing/Neijiang prepared package",
                    "status": "missing",
                    "present_required_count": 0,
                    "required_count": 2,
                    "file_count_present": 0,
                    "bytes_present": 0,
                    "missing_required_paths": [
                        "G:\\我的云端硬盘\\paper4_results\\dongxing\\marl_eval_seed0.json"
                    ],
                    "optional_present_paths": [],
                    "claim_dependency": "External-region full reruns",
                    "manuscript_blocker": "Dongxing/Neijiang prepared-data route",
                    "external_to_git": True,
                }
            ],
            "summary": {"available": 0, "partial": 0, "missing": 1},
        }
    )

    assert "not a data-rights approval" in text
    assert "Dongxing/Neijiang prepared-data route" in text
    assert "External-region full reruns" in text
    assert "direct 50-state success" not in text.lower()
    assert "robust transfer superiority" not in text.lower()
