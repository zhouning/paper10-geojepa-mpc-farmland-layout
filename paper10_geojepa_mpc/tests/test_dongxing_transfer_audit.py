import csv

import pytest

from paper10_geojepa_mpc.experiments.dongxing_transfer_audit import (
    audit_dongxing_transfer,
    build_comparisons,
    main,
    markdown_report,
    normalize_family_rows,
    normalize_low_budget_rows,
)


def _write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_normalize_family_rows_maps_transfer_and_scratch():
    rows = normalize_family_rows(
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            }
        ],
        source="family.csv",
    )

    assert rows == [
        {
            "source": "family.csv",
            "comparison_key": "return_50x16_h5",
            "label_type": "return_50x16_h5",
            "label_budget": "",
            "family": "transfer",
            "episodes": 15,
            "reward_mean": 51.0,
            "reward_sd": 18.0,
            "slope_pct_mean": -0.29,
            "cont_mean": 0.020,
            "baimu_ha_mean": 107.0,
        }
    ]


def test_normalize_family_rows_accepts_compact_schema():
    rows = normalize_family_rows(
        [
            {
                "label_type": "return_20x16_h5",
                "family": "scratch",
                "episodes": "15",
                "mean_reward": "48.5",
                "reward_sd": "11.0",
                "slope_pct_mean": "-0.25",
                "cont_mean": "0.023",
                "baimu_ha_mean": "210.0",
            }
        ],
        source="compact.csv",
    )

    assert rows == [
        {
            "source": "compact.csv",
            "comparison_key": "return_20x16_h5",
            "label_type": "return_20x16_h5",
            "label_budget": "",
            "family": "scratch",
            "episodes": 15,
            "reward_mean": 48.5,
            "reward_sd": 11.0,
            "slope_pct_mean": -0.25,
            "cont_mean": 0.023,
            "baimu_ha_mean": 210.0,
        }
    ]


def test_normalize_low_budget_rows_uses_budget_key():
    rows = normalize_low_budget_rows(
        [
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "40.5",
                "reward_sd": "12.4",
                "slope_pct_mean": "-0.24",
                "cont_mean": "0.027",
                "baimu_ha_mean": "373.0",
            }
        ],
        source="low.csv",
    )

    assert rows[0]["comparison_key"] == "low_budget_20"
    assert rows[0]["label_budget"] == "20"
    assert rows[0]["family"] == "scratch"


def test_audit_dongxing_transfer_computes_matched_effects(tmp_path):
    family_csv = tmp_path / "family.csv"
    low_csv = tmp_path / "low.csv"
    out_csv = tmp_path / "audit.csv"
    out_md = tmp_path / "audit.md"
    _write_csv(
        family_csv,
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            },
            {
                "label_type": "return_50x16_h5",
                "mode": "scratch",
                "n_episodes": "15",
                "total_reward_mean": "55.0",
                "total_reward_sd": "20.0",
                "slope_change_pct_mean": "-0.26",
                "cont_change_mean": "0.024",
                "baimu_area_change_ha_mean": "262.0",
            },
        ],
    )
    _write_csv(
        low_csv,
        [
            {
                "budget": "20",
                "family": "transfer",
                "episodes": "15",
                "reward_mean": "44.7",
                "reward_sd": "19.4",
                "slope_pct_mean": "-0.30",
                "cont_mean": "0.022",
                "baimu_ha_mean": "111.0",
            },
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "40.5",
                "reward_sd": "12.5",
                "slope_pct_mean": "-0.24",
                "cont_mean": "0.027",
                "baimu_ha_mean": "373.0",
            },
        ],
    )

    payload = audit_dongxing_transfer([family_csv], [low_csv], out_csv, out_md)

    assert len(payload["comparisons"]) == 2
    effects = {row["comparison_key"]: row["reward_effect_transfer_minus_scratch"] for row in payload["comparisons"]}
    assert effects["return_50x16_h5"] == -4.0
    assert effects["low_budget_20"] == 4.2
    assert out_csv.exists()
    assert out_md.exists()


def test_audit_dongxing_transfer_allows_identical_duplicates(tmp_path):
    family_csv = tmp_path / "family.csv"
    low_csv = tmp_path / "low.csv"
    out_csv = tmp_path / "audit.csv"
    out_md = tmp_path / "audit.md"
    transfer = {
        "label_type": "return_50x16_h5",
        "mode": "transfer",
        "n_episodes": "15",
        "total_reward_mean": "51.0",
        "total_reward_sd": "18.0",
        "slope_change_pct_mean": "-0.29",
        "cont_change_mean": "0.020",
        "baimu_area_change_ha_mean": "107.0",
    }
    _write_csv(
        family_csv,
        [
            transfer,
            transfer.copy(),
            {
                "label_type": "return_50x16_h5",
                "mode": "scratch",
                "n_episodes": "15",
                "total_reward_mean": "55.0",
                "total_reward_sd": "20.0",
                "slope_change_pct_mean": "-0.26",
                "cont_change_mean": "0.024",
                "baimu_area_change_ha_mean": "262.0",
            },
        ],
    )
    _write_csv(
        low_csv,
        [
            {
                "budget": "20",
                "family": "transfer",
                "episodes": "15",
                "reward_mean": "44.7",
                "reward_sd": "19.4",
                "slope_pct_mean": "-0.30",
                "cont_mean": "0.022",
                "baimu_ha_mean": "111.0",
            },
            {
                "budget": "20",
                "family": "scratch",
                "episodes": "15",
                "reward_mean": "40.5",
                "reward_sd": "12.5",
                "slope_pct_mean": "-0.24",
                "cont_mean": "0.027",
                "baimu_ha_mean": "373.0",
            },
        ],
    )

    payload = audit_dongxing_transfer([family_csv], [low_csv], out_csv, out_md)

    assert payload["n_normalized_rows"] == 4
    assert len(payload["comparisons"]) == 2


def test_audit_dongxing_transfer_rejects_conflicting_duplicates(tmp_path):
    family_csv = tmp_path / "family.csv"
    out_csv = tmp_path / "audit.csv"
    out_md = tmp_path / "audit.md"
    _write_csv(
        family_csv,
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            },
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "52.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            },
        ],
    )

    with pytest.raises(ValueError, match="Conflicting duplicate rows.*return_50x16_h5.*transfer"):
        audit_dongxing_transfer([family_csv], [], out_csv, out_md)


def test_build_comparisons_orders_low_budgets_numerically():
    rows = []
    for budget in ["20", "5", "10"]:
        rows.extend(
            [
                {
                    "source": "low.csv",
                    "comparison_key": f"low_budget_{budget}",
                    "label_type": "return_50x16_h5_low_budget",
                    "label_budget": budget,
                    "family": "transfer",
                    "episodes": 15,
                    "reward_mean": 50.0,
                    "reward_sd": 1.0,
                    "slope_pct_mean": -0.2,
                    "cont_mean": 0.02,
                    "baimu_ha_mean": 100.0,
                },
                {
                    "source": "low.csv",
                    "comparison_key": f"low_budget_{budget}",
                    "label_type": "return_50x16_h5_low_budget",
                    "label_budget": budget,
                    "family": "scratch",
                    "episodes": 15,
                    "reward_mean": 40.0,
                    "reward_sd": 1.0,
                    "slope_pct_mean": -0.1,
                    "cont_mean": 0.03,
                    "baimu_ha_mean": 200.0,
                },
            ]
        )

    comparisons = build_comparisons(rows)

    assert [row["comparison_key"] for row in comparisons] == [
        "low_budget_5",
        "low_budget_10",
        "low_budget_20",
    ]


def test_main_creates_output_json_parent_directory(tmp_path, monkeypatch):
    family_csv = tmp_path / "family.csv"
    out_csv = tmp_path / "out" / "audit.csv"
    out_md = tmp_path / "out" / "audit.md"
    out_json = tmp_path / "nested" / "audit.json"
    _write_csv(
        family_csv,
        [
            {
                "label_type": "return_50x16_h5",
                "mode": "transfer",
                "n_episodes": "15",
                "total_reward_mean": "51.0",
                "total_reward_sd": "18.0",
                "slope_change_pct_mean": "-0.29",
                "cont_change_mean": "0.020",
                "baimu_area_change_ha_mean": "107.0",
            },
            {
                "label_type": "return_50x16_h5",
                "mode": "scratch",
                "n_episodes": "15",
                "total_reward_mean": "55.0",
                "total_reward_sd": "20.0",
                "slope_change_pct_mean": "-0.26",
                "cont_change_mean": "0.024",
                "baimu_area_change_ha_mean": "262.0",
            },
        ],
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "dongxing_transfer_audit",
            "--family-csv",
            str(family_csv),
            "--output-csv",
            str(out_csv),
            "--output-md",
            str(out_md),
            "--output-json",
            str(out_json),
        ],
    )

    main()

    assert out_json.exists()


def test_markdown_report_preserves_negative_transfer_boundary():
    text = markdown_report(
        {
            "comparisons": [
                {
                    "comparison_key": "return_50x16_h5",
                    "transfer_reward_mean": 51.0,
                    "scratch_reward_mean": 55.0,
                    "reward_effect_transfer_minus_scratch": -4.0,
                    "interpretation": "scratch_higher_reward",
                }
            ]
        }
    )

    assert "scratch_higher_reward" in text
    assert "robust transfer superiority" not in text.lower()
