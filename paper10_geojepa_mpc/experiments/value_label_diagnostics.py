import argparse
import json
from pathlib import Path
from typing import Mapping

import numpy as np


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    if x.shape[0] < 2:
        return 0.0
    x_std = float(np.std(x))
    y_std = float(np.std(y))
    if x_std == 0.0 or y_std == 0.0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _rankdata_average(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.shape[0], dtype=np.float64)
    sorted_values = values[order]
    start = 0
    while start < values.shape[0]:
        end = start + 1
        while end < values.shape[0] and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2.0
        start = end
    return ranks


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    return _corr(_rankdata_average(x), _rankdata_average(y))


def _as_2d_float(dataset: Mapping[str, np.ndarray], key: str) -> np.ndarray:
    if key not in dataset:
        raise KeyError(f"dataset must contain '{key}'")
    array = np.asarray(dataset[key], dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"{key} must be a two-dimensional array")
    if array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError(f"{key} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{key} must contain only finite values")
    return array


def _topk_indices(values: np.ndarray, top_k: int) -> np.ndarray:
    return np.argsort(values)[::-1][:top_k]


def _pairwise_disagreement_rate(
    score_row: np.ndarray,
    return_row: np.ndarray,
) -> tuple[float, float]:
    pair_i, pair_j = np.triu_indices(return_row.shape[0], k=1)
    if pair_i.size == 0:
        return 0.0, 0.0
    score_sign = np.sign(score_row[pair_i] - score_row[pair_j])
    return_sign = np.sign(return_row[pair_i] - return_row[pair_j])
    comparable = (score_sign != 0.0) & (return_sign != 0.0)
    if not np.any(comparable):
        return 0.0, 0.0
    disagreement = score_sign[comparable] != return_sign[comparable]
    return float(np.mean(disagreement)), float(np.mean(comparable))


def _alignment_metrics(
    scores: np.ndarray,
    returns: np.ndarray,
    top_k: int,
    regret_key: str,
) -> dict:
    top1_disagreement = []
    topk_overlap = []
    top1_regrets = []
    topk_best_regrets = []
    pearson_by_state = []
    spearman_by_state = []
    pairwise_disagreement = []
    pairwise_comparable = []

    for score_row, return_row in zip(scores, returns):
        score_top1 = int(np.argmax(score_row))
        return_top1 = int(np.argmax(return_row))
        score_topk = _topk_indices(score_row, top_k)
        return_topk = _topk_indices(return_row, top_k)
        score_topk_set = set(int(x) for x in score_topk)
        return_topk_set = set(int(x) for x in return_topk)

        return_best = float(return_row[return_top1])
        score_topk_best_return = float(return_row[score_topk].max())
        pairwise_rate, comparable_fraction = _pairwise_disagreement_rate(
            score_row, return_row
        )

        top1_disagreement.append(float(score_top1 != return_top1))
        topk_overlap.append(float(len(score_topk_set & return_topk_set) / top_k))
        top1_regrets.append(float(return_best - return_row[score_top1]))
        topk_best_regrets.append(float(return_best - score_topk_best_return))
        pearson_by_state.append(_corr(score_row, return_row))
        spearman_by_state.append(_spearman(score_row, return_row))
        pairwise_disagreement.append(pairwise_rate)
        pairwise_comparable.append(comparable_fraction)

    return {
        "pearson_flat": _corr(scores, returns),
        "spearman_flat": _spearman(scores, returns),
        "pearson_state_mean": float(np.mean(pearson_by_state)),
        "spearman_state_mean": float(np.mean(spearman_by_state)),
        "top1_disagreement_rate": float(np.mean(top1_disagreement)),
        "topk_overlap_fraction_mean": float(np.mean(topk_overlap)),
        regret_key: float(np.mean(top1_regrets)),
        "topk_best_return_regret_mean": float(np.mean(topk_best_regrets)),
        "pairwise_disagreement_rate_mean": float(np.mean(pairwise_disagreement)),
        "pairwise_comparable_fraction_mean": float(np.mean(pairwise_comparable)),
    }


def value_label_diagnostics(
    dataset: Mapping[str, np.ndarray],
    top_k: int = 5,
) -> dict:
    """Measure whether multi-step value labels add ranking signal beyond one-step reward."""

    returns = _as_2d_float(dataset, "returns")
    one_step = _as_2d_float(dataset, "one_step_rewards")
    if returns.shape != one_step.shape:
        raise ValueError("returns and one_step_rewards must have the same shape")

    n_states, n_candidates = returns.shape
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    k = min(int(top_k), n_candidates)
    residual = returns - one_step
    return_state_std = returns.std(axis=1)
    one_step_state_std = one_step.std(axis=1)
    residual_state_std = residual.std(axis=1)
    mean_return_state_std = float(np.mean(return_state_std))

    report = {
        "n_states": int(n_states),
        "n_candidates": int(n_candidates),
        "top_k": int(k),
        "label_variation": {
            "return_mean": float(np.mean(returns)),
            "return_std": float(np.std(returns)),
            "return_state_std_mean": mean_return_state_std,
            "return_state_std_median": float(np.median(return_state_std)),
            "one_step_reward_mean": float(np.mean(one_step)),
            "one_step_reward_std": float(np.std(one_step)),
            "one_step_state_std_mean": float(np.mean(one_step_state_std)),
            "one_step_state_std_median": float(np.median(one_step_state_std)),
            "residual_mean": float(np.mean(residual)),
            "residual_std": float(np.std(residual)),
            "residual_abs_mean": float(np.mean(np.abs(residual))),
            "residual_state_std_mean": float(np.mean(residual_state_std)),
            "residual_state_std_median": float(np.median(residual_state_std)),
            "residual_to_return_state_std_ratio": (
                float(np.mean(residual_state_std) / mean_return_state_std)
                if mean_return_state_std > 0.0
                else 0.0
            ),
        },
        "one_step_vs_return": _alignment_metrics(
            one_step,
            returns,
            k,
            regret_key="one_step_top1_return_regret_mean",
        ),
    }

    if "candidate_scores" in dataset:
        candidate_scores = _as_2d_float(dataset, "candidate_scores")
        if candidate_scores.shape != returns.shape:
            raise ValueError("candidate_scores and returns must have the same shape")
        report["candidate_score_vs_return"] = _alignment_metrics(
            candidate_scores,
            returns,
            k,
            regret_key="candidate_top1_return_regret_mean",
        )
    return report


def _fmt(value: float) -> str:
    return f"{float(value):.4f}"


def markdown_report(report: dict) -> str:
    lines = [
        "# Value-label diagnostics",
        "",
        f"States: `{report['n_states']}`",
        f"Candidates per state: `{report['n_candidates']}`",
        f"Top-k: `{report['top_k']}`",
        "",
        "## Label variation",
        "",
        "| metric | value |",
        "|---|---:|",
    ]
    for key, value in report["label_variation"].items():
        lines.append(f"| {key} | {_fmt(value)} |")

    lines.extend(
        [
            "",
            "## One-step reward vs return",
            "",
            "| metric | value |",
            "|---|---:|",
        ]
    )
    for key, value in report["one_step_vs_return"].items():
        lines.append(f"| {key} | {_fmt(value)} |")

    if "candidate_score_vs_return" in report:
        lines.extend(
            [
                "",
                "## Candidate score vs return",
                "",
                "| metric | value |",
                "|---|---:|",
            ]
        )
        for key, value in report["candidate_score_vs_return"].items():
            lines.append(f"| {key} | {_fmt(value)} |")
    return "\n".join(lines) + "\n"


def _load_npz(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    report = value_label_diagnostics(_load_npz(input_path), top_k=args.top_k)
    report["input"] = str(input_path)
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text, encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(markdown_report(report), encoding="utf-8")


if __name__ == "__main__":
    main()
