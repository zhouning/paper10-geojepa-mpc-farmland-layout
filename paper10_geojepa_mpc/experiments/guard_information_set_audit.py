"""Information-set and baseline stress audit for Paper10 guard evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RESULTS = Path("paper10_geojepa_mpc") / "experiments" / "results"
DEFAULT_AUDIT_ROLLOUT_JSON = (
    RESULTS
    / "e0_bishan_20x16_top5_true_reward_margin_guard_m150_audit_rewardtop7_blend010_seeds0-19_100step_2026-07-07.json"
)
DEFAULT_OUTPUT_JSON = (
    RESULTS / "e0_paper10_guard_information_set_audit_2026-07-09.json"
)
DEFAULT_OUTPUT_MD = (
    RESULTS / "e0_paper10_guard_information_set_audit_2026-07-09.md"
)


MISSING_DYNAMIC_BASELINES = [
    "executable_random_20seed_rollout",
    "greedy_immediate_true_reward_20seed_rollout",
    "rank_only_or_no_value_20seed_rollout",
    "model_reward_proxy_guard_20seed_rollout",
    "candidate_score_proxy_guard_20seed_rollout",
    "full_valid_action_oracle_upper_bound_20seed_rollout",
]


COMPLETED_DYNAMIC_BASELINES = [
    "value_filter_20seed_rollout",
    "true_reward_margin_guard_20seed_rollout",
    "dual7x7_true_reward_guard_diagnostic",
]


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _as_float(value: Any) -> float:
    return float(value)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return float(sum(1 for value in values if value) / len(values))


def _flatten_audit_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in payload.get("episodes", []):
        rows.extend(dict(row) for row in episode.get("audit_rows", []))
    return rows


def _row_reward_for_action(row: dict[str, Any], action: int | None) -> float | None:
    if action is None:
        return None
    action = int(action)
    action_reward_pairs = [
        (row.get("selected_action"), row.get("selected_true_reward")),
        (row.get("audit_best_action"), row.get("audit_best_true_reward")),
        (row.get("model_reward_top1_action"), row.get("model_reward_top1_true_reward")),
        (row.get("candidate_top1_action"), row.get("candidate_top1_true_reward")),
    ]
    for candidate_action, reward in action_reward_pairs:
        if candidate_action is not None and int(candidate_action) == action:
            return _as_float(reward)
    return None


def _policy_reward_summary(
    *,
    rows: list[dict[str, Any]],
    policy_name: str,
    reward_key: str,
    action_key: str | None,
    selected_rewards: list[float],
) -> dict[str, Any]:
    rewards = [_as_float(row[reward_key]) for row in rows if reward_key in row]
    deltas = [reward - selected for reward, selected in zip(rewards, selected_rewards)]
    action_change_rate = 0.0
    true_best_match_rate = 0.0
    if action_key is not None:
        action_change_rate = _rate(
            [int(row[action_key]) != int(row["selected_action"]) for row in rows]
        )
        true_best_match_rate = _rate(
            [int(row[action_key]) == int(row["audit_best_action"]) for row in rows]
        )
    return {
        "policy": policy_name,
        "diagnostic_scope": "statewise immediate action audit, not dynamic rollout",
        "mean_true_reward": _mean(rewards),
        "mean_delta_vs_selected": _mean(deltas),
        "improves_selected_rate": _rate([delta > 0.0 for delta in deltas]),
        "ties_selected_rate": _rate([delta == 0.0 for delta in deltas]),
        "worse_than_selected_rate": _rate([delta < 0.0 for delta in deltas]),
        "action_change_rate": action_change_rate,
        "true_best_match_rate": true_best_match_rate,
    }


def _executed_guard_summary(
    *,
    rows: list[dict[str, Any]],
    selected_rewards: list[float],
) -> dict[str, Any]:
    rewards: list[float] = []
    for row in rows:
        reward = _row_reward_for_action(row, row.get("execution_action"))
        if reward is not None:
            rewards.append(reward)
    deltas = [reward - selected for reward, selected in zip(rewards, selected_rewards)]
    return {
        "policy": "margin_true_reward_guard_executed",
        "diagnostic_scope": "statewise immediate action audit, not dynamic rollout",
        "mean_true_reward": _mean(rewards),
        "mean_delta_vs_selected": _mean(deltas),
        "improves_selected_rate": _rate([delta > 0.0 for delta in deltas]),
        "switch_rate": _rate(
            [int(row.get("execution_action")) != int(row.get("selected_action")) for row in rows]
        ),
        "oracle_dependency": "uses immediate true reward over the audit action set",
    }


def _score_gap_summary(
    rows: list[dict[str, Any]],
    *,
    selected_key: str,
    top1_key: str,
) -> dict[str, Any]:
    gaps = [
        _as_float(row[top1_key]) - _as_float(row[selected_key])
        for row in rows
        if selected_key in row and top1_key in row
    ]
    return {
        "available": bool(gaps),
        "states_with_scores": int(len(gaps)),
        "mean_score_gap_vs_selected": _mean(gaps),
        "positive_gap_rate": _rate([gap > 0.0 for gap in gaps]),
    }


def _statewise_summary(rows: list[dict[str, Any]], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "audited_states": int(len(rows)),
        "seeds": [int(seed) for seed in payload.get("seeds", [])],
        "configured_steps": int(payload.get("steps", 0)),
        "execution_policy": payload.get("execution_policy", "unknown"),
        "true_reward_switch_margin": _as_float(
            payload.get("true_reward_switch_margin", 0.0)
        ),
        "switches": int(
            sum(
                1
                for row in rows
                if int(row.get("execution_action")) != int(row.get("selected_action"))
            )
        ),
        "switch_rate": _rate(
            [
                int(row.get("execution_action")) != int(row.get("selected_action"))
                for row in rows
            ]
        ),
        "mean_audited_actions": _mean(
            [_as_float(row.get("audit_action_count", 0.0)) for row in rows]
        ),
        "mean_valid_actions": _mean(
            [_as_float(row.get("n_valid", 0.0)) for row in rows]
        ),
        "mean_true_reward_time_sec": _mean(
            [_as_float(row.get("true_reward_time_sec", 0.0)) for row in rows]
        ),
        "total_true_reward_time_sec": float(
            sum(_as_float(row.get("true_reward_time_sec", 0.0)) for row in rows)
        ),
        "selected_true_reward_regret_mean": _mean(
            [_as_float(row.get("selected_true_reward_regret", 0.0)) for row in rows]
        ),
        "selected_is_audit_true_best_rate": _mean(
            [_as_float(row.get("selected_is_audit_true_best", 0.0)) for row in rows]
        ),
        "audit_true_best_in_model_reward_topk_rate": _mean(
            [
                _as_float(row.get("audit_true_best_in_model_reward_topk", 0.0))
                for row in rows
            ]
        ),
        "audit_true_best_in_candidate_topk_rate": _mean(
            [
                _as_float(row.get("audit_true_best_in_candidate_topk", 0.0))
                for row in rows
            ]
        ),
    }


def build_guard_information_set_audit(
    *,
    audit_rollout_json: str | Path = DEFAULT_AUDIT_ROLLOUT_JSON,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    audit_path = Path(audit_rollout_json)
    payload = _load_json(audit_path)
    rows = _flatten_audit_rows(payload)
    selected_rewards = [_as_float(row["selected_true_reward"]) for row in rows]

    one_step = {
        "selected_value_filter": _policy_reward_summary(
            rows=rows,
            policy_name="selected_value_filter",
            reward_key="selected_true_reward",
            action_key=None,
            selected_rewards=selected_rewards,
        ),
        "model_reward_top1_proxy": _policy_reward_summary(
            rows=rows,
            policy_name="model_reward_top1_proxy",
            reward_key="model_reward_top1_true_reward",
            action_key="model_reward_top1_action",
            selected_rewards=selected_rewards,
        ),
        "candidate_score_top1_proxy": _policy_reward_summary(
            rows=rows,
            policy_name="candidate_score_top1_proxy",
            reward_key="candidate_top1_true_reward",
            action_key="candidate_top1_action",
            selected_rewards=selected_rewards,
        ),
        "audit_true_best_upper_bound": _policy_reward_summary(
            rows=rows,
            policy_name="audit_true_best_upper_bound",
            reward_key="audit_best_true_reward",
            action_key="audit_best_action",
            selected_rewards=selected_rewards,
        ),
        "margin_true_reward_guard_executed": _executed_guard_summary(
            rows=rows,
            selected_rewards=selected_rewards,
        ),
    }

    return {
        "date": output_date,
        "status": "guard_information_set_and_baseline_stress_audit",
        "source_boundary": {
            "source": "tracked action-audit rollout rows",
            "reran_training": False,
            "reran_rollouts": False,
            "new_dynamic_rollout_baselines": False,
            "statewise_reanalysis_only": True,
        },
        "source_files": {
            "audit_rollout_json": audit_path.as_posix(),
        },
        "information_set_boundary": {
            "primary_guard_information_set": "privileged_immediate_true_reward_action_audit",
            "deployable_without_reward_oracle": False,
            "allowed_primary_role": "oracle/action-audit guard",
            "not_allowed_primary_role": "standalone deployable no-oracle planner",
            "review_risk": (
                "CEUS reviewers may treat the current guard as privileged "
                "simulator/reward access unless a learned or operational proxy "
                "guard is evaluated under the same rollout protocol."
            ),
        },
        "statewise_audit_summary": _statewise_summary(rows, payload),
        "one_step_policy_diagnostics": one_step,
        "proxy_score_gap_diagnostics": {
            "model_reward_margin_guard_inputs": _score_gap_summary(
                rows,
                selected_key="selected_model_reward_score",
                top1_key="model_reward_top1_model_reward_score",
            ),
            "candidate_score_margin_guard_inputs": _score_gap_summary(
                rows,
                selected_key="selected_candidate_score",
                top1_key="candidate_top1_candidate_score",
            ),
        },
        "completed_dynamic_baselines": COMPLETED_DYNAMIC_BASELINES,
        "missing_dynamic_baselines": MISSING_DYNAMIC_BASELINES,
        "claim_gates": {
            "statewise_proxy_screening_supported": bool(rows),
            "oracle_upper_bound_statewise_supported": bool(rows),
            "true_reward_guard_deployable_without_oracle": False,
            "proxy_guard_rollout_superiority_supported": False,
            "dynamic_baseline_suite_complete": False,
            "manuscript_should_call_guard_oracle_action_audit": True,
        },
        "allowed_language": [
            "oracle/action-audit guard",
            "statewise immediate proxy diagnostic",
            "not a standalone deployable no-oracle planner",
            "dynamic proxy-guard rollout remains future work",
        ],
        "blocked_language": [
            "deployable true-reward guard without oracle access",
            "proxy guard rollout superiority",
            "complete dynamic baseline suite",
            "true-reward guard proves learned planner superiority",
        ],
    }


def _fmt(value: Any) -> str:
    return f"{float(value):.4f}"


def guard_information_set_audit_markdown(payload: dict[str, Any]) -> str:
    info = payload["information_set_boundary"]
    summary = payload["statewise_audit_summary"]
    one_step = payload["one_step_policy_diagnostics"]
    gates = payload["claim_gates"]
    lines = [
        "# Paper10 guard information-set and baseline stress audit",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: guard_information_set_and_baseline_stress_audit",
        "",
        "This audit reduces CEUS review risk by separating the current oracle/action-audit guard from no-oracle deployable proxy guards.",
        "It reanalyzes tracked action-audit rollout rows and does not rerun training or dynamic rollouts.",
        "",
        "## Information-Set Boundary",
        "",
        f"- Primary guard role: {info['allowed_primary_role']}.",
        f"- Primary guard information set: `{info['primary_guard_information_set']}`.",
        f"- Deployable without reward oracle: {info['deployable_without_reward_oracle']}.",
        f"- Not allowed role: not a {info['not_allowed_primary_role']}.",
        f"- Review risk: {info['review_risk']}",
        "",
        "## Statewise Audit Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| audited states | {summary['audited_states']} |",
        f"| switches | {summary['switches']} |",
        f"| switch rate | {_fmt(summary['switch_rate'])} |",
        f"| mean audited actions | {_fmt(summary['mean_audited_actions'])} |",
        f"| mean valid actions | {_fmt(summary['mean_valid_actions'])} |",
        f"| selected true-reward regret mean | {_fmt(summary['selected_true_reward_regret_mean'])} |",
        f"| selected is audit true best rate | {_fmt(summary['selected_is_audit_true_best_rate'])} |",
        "",
        "## One-Step Policy Diagnostics",
        "",
        "These rows are statewise immediate diagnostics, not dynamic rollout baselines.",
        "",
        "| policy | mean true reward | delta vs selected | improves selected rate | true-best match rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in [
        "selected_value_filter",
        "model_reward_top1_proxy",
        "candidate_score_top1_proxy",
        "audit_true_best_upper_bound",
        "margin_true_reward_guard_executed",
    ]:
        item = one_step[key]
        lines.append(
            "| "
            f"{key} | {_fmt(item['mean_true_reward'])} | "
            f"{_fmt(item['mean_delta_vs_selected'])} | "
            f"{_fmt(item['improves_selected_rate'])} | "
            f"{_fmt(item.get('true_best_match_rate', 0.0))} |"
        )

    lines.extend(
        [
            "",
            "## Dynamic Baseline Suite Boundary",
            "",
            "Completed dynamic baselines:",
            "",
        ]
    )
    for baseline in payload["completed_dynamic_baselines"]:
        lines.append(f"- {baseline}")
    lines.extend(["", "Missing dynamic baselines:", ""])
    for baseline in payload["missing_dynamic_baselines"]:
        lines.append(f"- {baseline}")

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
            "## Claim Locks",
            "",
            "Do not call the true-reward guard a standalone deployable no-oracle planner.",
            "Do not claim proxy-guard rollout superiority.",
            "Do not claim the dynamic baseline suite is complete.",
            "Do not claim learned planner superiority from the oracle/action-audit guard alone.",
            "",
        ]
    )
    return "\n".join(lines)


def write_guard_information_set_audit(
    *,
    audit_rollout_json: str | Path = DEFAULT_AUDIT_ROLLOUT_JSON,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_md: str | Path = DEFAULT_OUTPUT_MD,
    output_date: str = "2026-07-09",
) -> dict[str, Any]:
    payload = build_guard_information_set_audit(
        audit_rollout_json=audit_rollout_json,
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
        guard_information_set_audit_markdown(payload),
        encoding="utf-8",
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Paper10 guard information-set audit."
    )
    parser.add_argument("--audit-rollout-json", default=str(DEFAULT_AUDIT_ROLLOUT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--date", default="2026-07-09")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_guard_information_set_audit(
        audit_rollout_json=args.audit_rollout_json,
        output_json=args.output_json,
        output_md=args.output_md,
        output_date=args.date,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
