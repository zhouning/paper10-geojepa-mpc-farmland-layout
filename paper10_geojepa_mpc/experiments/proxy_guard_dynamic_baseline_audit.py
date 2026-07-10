"""Dynamic no-oracle proxy guard stress audit for Paper10."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import stdev
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_VALUE_FILTER_SUMMARY_JSON = (
    RESULTS / "e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json"
)
DEFAULT_MODEL_PROXY_JSON = (
    RESULTS
    / "e0_bishan_20x16_top5_model_reward_proxy_guard_m010_rewardtop1_blend010_seeds0-4_100step_2026-07-09.json"
)
DEFAULT_CANDIDATE_PROXY_JSON = (
    RESULTS
    / "e0_bishan_20x16_top5_candidate_score_proxy_guard_m010_candidatetop1_blend010_seeds0-4_100step_2026-07-09.json"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_proxy_guard_dynamic_baseline_audit_2026-07-09.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_proxy_guard_dynamic_baseline_audit_2026-07-09.md"
)


PROXY_POLICY_KEYS = {
    "model_reward_margin_guard": {
        "policy_label": "model_reward_proxy_guard_m010",
        "action_key": "model_reward_top1_action",
        "reward_key": "model_reward_top1_true_reward",
    },
    "candidate_score_margin_guard": {
        "policy_label": "candidate_score_proxy_guard_m010",
        "action_key": "candidate_top1_action",
        "reward_key": "candidate_top1_true_reward",
    },
}


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _sample_std(values: list[float]) -> float:
    return float(stdev(values)) if len(values) > 1 else 0.0


def _rate(count: int, total: int) -> float:
    return float(count / total) if total else 0.0


def _flatten_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in payload.get("episodes", []):
        rows.extend(dict(row) for row in episode.get("audit_rows", []))
    return rows


def _proxy_summary(
    *,
    payload: dict[str, Any],
    source_path: Path,
    baseline_mean: float,
) -> dict[str, Any]:
    policy = str(payload.get("execution_policy", ""))
    if policy not in PROXY_POLICY_KEYS:
        raise ValueError(f"unsupported proxy execution_policy: {policy}")

    keys = PROXY_POLICY_KEYS[policy]
    episodes = payload.get("episodes", [])
    rewards = [float(episode["total_reward"]) for episode in episodes]
    rows = _flatten_rows(payload)
    switch_rows = [
        row
        for row in rows
        if int(row.get("execution_action")) != int(row.get("selected_action"))
    ]

    improved = 0
    worsened = 0
    tied = 0
    for row in switch_rows:
        delta = float(row[keys["reward_key"]]) - float(row["selected_true_reward"])
        if delta > 0.0:
            improved += 1
        elif delta < 0.0:
            worsened += 1
        else:
            tied += 1

    mean_reward = _mean(rewards)
    return {
        "policy_label": keys["policy_label"],
        "execution_policy": policy,
        "source_json": source_path.as_posix(),
        "seeds": [int(seed) for seed in payload.get("seeds", [])],
        "steps": int(payload.get("steps", 0)),
        "n_episodes": int(len(episodes)),
        "episode_total_rewards": rewards,
        "total_reward_mean": mean_reward,
        "total_reward_std_sample": _sample_std(rewards),
        "total_reward_min": float(min(rewards)) if rewards else 0.0,
        "total_reward_max": float(max(rewards)) if rewards else 0.0,
        "delta_vs_value_filter_5seed_mean": float(mean_reward - baseline_mean),
        "switch_margin_score_space": float(payload.get("true_reward_switch_margin", 0.0)),
        "audit_action_scope": {
            "audit_top_reward": int(payload.get("audit_top_reward", 0)),
            "audit_top_candidate": int(payload.get("audit_top_candidate", 0)),
            "audit_random_sample": int(payload.get("audit_random_sample", 0)),
        },
        "audited_steps": int(len(rows)),
        "switches": int(len(switch_rows)),
        "switch_rate": _rate(len(switch_rows), len(rows)),
        "switches_with_higher_immediate_true_reward": int(improved),
        "switches_with_lower_immediate_true_reward": int(worsened),
        "switches_with_tied_immediate_true_reward": int(tied),
        "higher_immediate_reward_switch_rate": _rate(improved, len(switch_rows)),
        "lower_immediate_reward_switch_rate": _rate(worsened, len(switch_rows)),
        "beats_value_filter_5seed_mean": bool(mean_reward > baseline_mean),
    }


def build_proxy_guard_dynamic_baseline_audit(
    *,
    value_filter_summary_json: str | Path = DEFAULT_VALUE_FILTER_SUMMARY_JSON,
    model_proxy_json: str | Path = DEFAULT_MODEL_PROXY_JSON,
    candidate_proxy_json: str | Path = DEFAULT_CANDIDATE_PROXY_JSON,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    value_filter_path = Path(value_filter_summary_json)
    model_proxy_path = Path(model_proxy_json)
    candidate_proxy_path = Path(candidate_proxy_json)
    value_filter = _load_json(value_filter_path)
    model_proxy = _load_json(model_proxy_path)
    candidate_proxy = _load_json(candidate_proxy_path)

    baseline_mean = float(value_filter["aggregate"]["total_reward_mean"])
    baseline_summary = {
        "policy_label": "value_filter_5seed_anchor",
        "source_json": value_filter_path.as_posix(),
        "n_episodes": int(value_filter["aggregate"]["n_episodes"]),
        "total_reward_mean": baseline_mean,
        "total_reward_std_sample": float(
            value_filter["aggregate"]["total_reward_std_sample"]
        ),
        "seed_total_rewards": [
            float(row["total_reward"]) for row in value_filter.get("seed_summaries", [])
        ],
    }
    proxies = [
        _proxy_summary(
            payload=model_proxy,
            source_path=model_proxy_path,
            baseline_mean=baseline_mean,
        ),
        _proxy_summary(
            payload=candidate_proxy,
            source_path=candidate_proxy_path,
            baseline_mean=baseline_mean,
        ),
    ]

    return {
        "date": output_date,
        "status": "proxy_guard_dynamic_baseline_stress_audit",
        "source_boundary": {
            "reran_training": False,
            "reran_rollouts": True,
            "new_dynamic_rollout_baselines": True,
            "scope": "5-seed no-oracle proxy guard stress test, not 20-seed confirmation",
            "prepared_dir": "D:/test",
        },
        "value_filter_anchor": baseline_summary,
        "proxy_guard_rollouts": proxies,
        "claim_gates": {
            "model_reward_proxy_beats_value_filter_5seed_mean": bool(
                proxies[0]["beats_value_filter_5seed_mean"]
            ),
            "candidate_score_proxy_beats_value_filter_5seed_mean": bool(
                proxies[1]["beats_value_filter_5seed_mean"]
            ),
            "no_oracle_proxy_guard_superiority_supported": bool(
                all(proxy["beats_value_filter_5seed_mean"] for proxy in proxies)
            ),
            "proxy_guard_20seed_confirmation_complete": False,
            "true_reward_guard_remains_oracle_action_audit": True,
            "manuscript_should_not_promote_proxy_guard": True,
        },
        "interpretation": {
            "summary": (
                "The tested no-oracle score-margin proxy guards did not beat the "
                "5-seed value-filter anchor, so statewise proxy gains should not "
                "be converted into a dynamic rollout superiority claim."
            ),
            "allowed_language": [
                "5-seed proxy guard stress test",
                "no-oracle proxy guards did not improve the 5-seed value-filter anchor",
                "statewise proxy diagnostics do not establish dynamic rollout superiority",
            ],
            "blocked_language": [
                "proxy guard rollout superiority",
                "deployable proxy guard is the primary algorithm",
                "true-reward guard is validated as a no-oracle policy",
            ],
        },
    }


def _fmt(value: Any) -> str:
    return f"{float(value):.4f}"


def proxy_guard_dynamic_baseline_audit_markdown(payload: dict[str, Any]) -> str:
    baseline = payload["value_filter_anchor"]
    gates = payload["claim_gates"]
    lines = [
        "# Paper10 proxy guard dynamic baseline stress audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: proxy_guard_dynamic_baseline_stress_audit",
        "",
        "This audit records new 5-seed dynamic rollouts for no-oracle score-margin proxy guards.",
        "It is a stress test, not a 20-seed confirmation.",
        "",
        "## Baseline",
        "",
        "| policy | n | mean reward | sample std |",
        "|---|---:|---:|---:|",
        (
            f"| {baseline['policy_label']} | {baseline['n_episodes']} | "
            f"{_fmt(baseline['total_reward_mean'])} | "
            f"{_fmt(baseline['total_reward_std_sample'])} |"
        ),
        "",
        "## Proxy Dynamic Rollouts",
        "",
        "| policy | n | mean reward | delta vs value filter | switch rate | better switches | worse switches |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for proxy in payload["proxy_guard_rollouts"]:
        lines.append(
            f"| {proxy['policy_label']} | {proxy['n_episodes']} | "
            f"{_fmt(proxy['total_reward_mean'])} | "
            f"{_fmt(proxy['delta_vs_value_filter_5seed_mean'])} | "
            f"{_fmt(proxy['switch_rate'])} | "
            f"{proxy['switches_with_higher_immediate_true_reward']} | "
            f"{proxy['switches_with_lower_immediate_true_reward']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Gates",
            "",
            "| gate | status |",
            "|---|---|",
        ]
    )
    for key, value in gates.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            payload["interpretation"]["summary"],
            "",
            "Do not claim proxy-guard rollout superiority.",
            "Do not present the true-reward guard as a deployable no-oracle policy.",
            "",
        ]
    )
    return "\n".join(lines)


def write_proxy_guard_dynamic_baseline_audit(
    *,
    value_filter_summary_json: str | Path = DEFAULT_VALUE_FILTER_SUMMARY_JSON,
    model_proxy_json: str | Path = DEFAULT_MODEL_PROXY_JSON,
    candidate_proxy_json: str | Path = DEFAULT_CANDIDATE_PROXY_JSON,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    payload = build_proxy_guard_dynamic_baseline_audit(
        value_filter_summary_json=value_filter_summary_json,
        model_proxy_json=model_proxy_json,
        candidate_proxy_json=candidate_proxy_json,
        output_date=output_date,
    )
    output_json_path = Path(output_json)
    output_md_path = Path(output_md)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md_path.write_text(
        proxy_guard_dynamic_baseline_audit_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 proxy guard dynamic baseline stress audit."
    )
    parser.add_argument("--value-filter-summary-json", default=str(DEFAULT_VALUE_FILTER_SUMMARY_JSON))
    parser.add_argument("--model-proxy-json", default=str(DEFAULT_MODEL_PROXY_JSON))
    parser.add_argument("--candidate-proxy-json", default=str(DEFAULT_CANDIDATE_PROXY_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-09")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_proxy_guard_dynamic_baseline_audit(
        value_filter_summary_json=args.value_filter_summary_json,
        model_proxy_json=args.model_proxy_json,
        candidate_proxy_json=args.candidate_proxy_json,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
