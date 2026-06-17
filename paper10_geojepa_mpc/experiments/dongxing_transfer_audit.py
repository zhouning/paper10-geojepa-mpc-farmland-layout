import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def _int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def _difference(left: float, right: float) -> float:
    return round(left - right, 10)


def normalize_family_rows(rows: Iterable[dict[str, str]], source: str) -> list[dict]:
    normalized = []
    for row in rows:
        normalized.append(
            {
                "source": source,
                "comparison_key": row["label_type"],
                "label_type": row["label_type"],
                "label_budget": "",
                "family": row["mode"],
                "episodes": _int(row, "n_episodes"),
                "reward_mean": _float(row, "total_reward_mean"),
                "reward_sd": _float(row, "total_reward_sd"),
                "slope_pct_mean": _float(row, "slope_change_pct_mean"),
                "cont_mean": _float(row, "cont_change_mean"),
                "baimu_ha_mean": _float(row, "baimu_area_change_ha_mean"),
            }
        )
    return normalized


def normalize_low_budget_rows(rows: Iterable[dict[str, str]], source: str) -> list[dict]:
    normalized = []
    for row in rows:
        budget = row["budget"]
        normalized.append(
            {
                "source": source,
                "comparison_key": f"low_budget_{budget}",
                "label_type": "return_50x16_h5_low_budget",
                "label_budget": budget,
                "family": row["family"],
                "episodes": _int(row, "episodes"),
                "reward_mean": _float(row, "reward_mean"),
                "reward_sd": _float(row, "reward_sd"),
                "slope_pct_mean": _float(row, "slope_pct_mean"),
                "cont_mean": _float(row, "cont_mean"),
                "baimu_ha_mean": _float(row, "baimu_ha_mean"),
            }
        )
    return normalized


def _deduplicate(rows: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for row in rows:
        key = (row["comparison_key"], row["family"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _interpret(reward_effect: float) -> str:
    if reward_effect > 0:
        return "transfer_higher_reward"
    if reward_effect < 0:
        return "scratch_higher_reward"
    return "reward_tie"


def build_comparisons(rows: list[dict]) -> list[dict]:
    by_key: dict[str, dict[str, dict]] = {}
    for row in rows:
        by_key.setdefault(row["comparison_key"], {})[row["family"]] = row

    comparisons = []
    for key in sorted(by_key):
        families = by_key[key]
        if "transfer" not in families or "scratch" not in families:
            continue
        transfer = families["transfer"]
        scratch = families["scratch"]
        reward_effect = _difference(transfer["reward_mean"], scratch["reward_mean"])
        comparisons.append(
            {
                "comparison_key": key,
                "label_type": transfer["label_type"],
                "label_budget": transfer["label_budget"],
                "episodes_transfer": transfer["episodes"],
                "episodes_scratch": scratch["episodes"],
                "transfer_reward_mean": transfer["reward_mean"],
                "scratch_reward_mean": scratch["reward_mean"],
                "reward_effect_transfer_minus_scratch": reward_effect,
                "transfer_reward_sd": transfer["reward_sd"],
                "scratch_reward_sd": scratch["reward_sd"],
                "slope_effect_transfer_minus_scratch": _difference(
                    transfer["slope_pct_mean"], scratch["slope_pct_mean"]
                ),
                "cont_effect_transfer_minus_scratch": _difference(transfer["cont_mean"], scratch["cont_mean"]),
                "baimu_ha_effect_transfer_minus_scratch": _difference(
                    transfer["baimu_ha_mean"], scratch["baimu_ha_mean"]
                ),
                "interpretation": _interpret(reward_effect),
                "transfer_source": transfer["source"],
                "scratch_source": scratch["source"],
            }
        )
    return comparisons


def _write_comparison_csv(path: Path, comparisons: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "comparison_key",
        "label_type",
        "label_budget",
        "episodes_transfer",
        "episodes_scratch",
        "transfer_reward_mean",
        "scratch_reward_mean",
        "reward_effect_transfer_minus_scratch",
        "transfer_reward_sd",
        "scratch_reward_sd",
        "slope_effect_transfer_minus_scratch",
        "cont_effect_transfer_minus_scratch",
        "baimu_ha_effect_transfer_minus_scratch",
        "interpretation",
        "transfer_source",
        "scratch_source",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comparisons)


def markdown_report(payload: dict) -> str:
    lines = [
        "# Paper10 Original-Vision Stage 2 Dongxing Transfer Audit",
        "",
        "This audit compares matched transfer and scratch rows from existing Dongxing summaries. It does not create a positive transfer claim.",
        "",
        "| comparison | transfer reward | scratch reward | transfer minus scratch | interpretation |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["comparisons"]:
        lines.append(
            "| {key} | {transfer:.4f} | {scratch:.4f} | {effect:.4f} | {interpretation} |".format(
                key=row["comparison_key"],
                transfer=float(row["transfer_reward_mean"]),
                scratch=float(row["scratch_reward_mean"]),
                effect=float(row["reward_effect_transfer_minus_scratch"]),
                interpretation=row["interpretation"],
            )
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Rows where transfer is higher identify conditional regimes for follow-up. Rows where scratch is higher remain direct evidence against a broad transfer-win claim.",
        ]
    )
    return "\n".join(lines) + "\n"


def audit_dongxing_transfer(
    family_csvs: list[str | Path],
    low_budget_csvs: list[str | Path],
    output_csv: str | Path,
    output_md: str | Path,
) -> dict:
    rows = []
    for path in family_csvs:
        csv_path = Path(path)
        rows.extend(normalize_family_rows(_read_csv(csv_path), source=str(csv_path)))
    for path in low_budget_csvs:
        csv_path = Path(path)
        rows.extend(normalize_low_budget_rows(_read_csv(csv_path), source=str(csv_path)))

    unique_rows = _deduplicate(rows)
    comparisons = build_comparisons(unique_rows)
    payload = {
        "family_csvs": [str(Path(path)) for path in family_csvs],
        "low_budget_csvs": [str(Path(path)) for path in low_budget_csvs],
        "n_normalized_rows": len(unique_rows),
        "comparisons": comparisons,
    }

    _write_comparison_csv(Path(output_csv), comparisons)
    Path(output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(output_md).write_text(markdown_report(payload), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family-csv", action="append", default=[])
    parser.add_argument("--low-budget-csv", action="append", default=[])
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = audit_dongxing_transfer(
        args.family_csv,
        args.low_budget_csv,
        args.output_csv,
        args.output_md,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        Path(args.output_json).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
