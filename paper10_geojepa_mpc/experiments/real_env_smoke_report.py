import argparse
import json
from pathlib import Path
from statistics import mean


DATE = "2026-06-18"


def _float(value) -> float:
    return float(value)


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def build_smoke_report(
    rollout_payload: dict,
    *,
    command: str,
    raw_output: str,
    date: str = DATE,
) -> dict:
    steps = rollout_payload.get("steps", [])
    rewards = [_float(step.get("reward", 0.0)) for step in steps]
    select_times = [_float(step.get("select_time_sec", 0.0)) for step in steps]
    executable_valid = [int(step.get("n_executable_valid", step.get("n_valid", 0))) for step in steps]
    base_valid = [int(step.get("n_base_valid", step.get("n_valid", 0))) for step in steps]
    final_step = steps[-1] if steps else {}

    return {
        "date": date,
        "command": command,
        "raw_output": raw_output,
        "configuration": {
            "checkpoint": rollout_payload.get("checkpoint"),
            "prepared_dir": rollout_payload.get("prepared_dir"),
            "env_source": rollout_payload.get("env_source", "paper9"),
            "seed": int(rollout_payload.get("seed", 0)),
            "horizon": int(rollout_payload.get("horizon", 0)),
            "top_k": int(rollout_payload.get("top_k", 0)),
            "rollout_steps": int(rollout_payload.get("rollout_steps", len(steps))),
            "mask_mode": rollout_payload.get("mask_mode"),
            "selector": rollout_payload.get("selector"),
            "scoring": rollout_payload.get("scoring"),
        },
        "outcome": {
            "steps_run": int(rollout_payload.get("steps_run", len(steps))),
            "total_reward": _float(rollout_payload.get("total_reward", sum(rewards))),
            "elapsed_sec": _float(rollout_payload.get("elapsed_sec", 0.0)),
            "terminated": bool(rollout_payload.get("terminated", False)),
            "truncated": bool(rollout_payload.get("truncated", False)),
            "min_base_valid": min(base_valid) if base_valid else 0,
            "min_executable_valid": min(executable_valid) if executable_valid else 0,
            "mean_select_time_sec": _mean(select_times),
            "positive_reward_steps": sum(1 for reward in rewards if reward > 0.0),
            "negative_reward_steps": sum(1 for reward in rewards if reward < 0.0),
        },
        "final_metrics": {
            "slope_change_pct": _float(final_step.get("slope_change_pct", 0.0)),
            "cont_change": _float(final_step.get("cont_change", 0.0)),
            "baimu_area_change_ha": _float(final_step.get("baimu_area_change_ha", 0.0)),
        },
        "steps": [
            {
                "step": int(step.get("step", index + 1)),
                "action": int(step.get("action", -1)),
                "reward": _float(step.get("reward", 0.0)),
                "n_base_valid": int(step.get("n_base_valid", step.get("n_valid", 0))),
                "n_executable_valid": int(
                    step.get("n_executable_valid", step.get("n_valid", 0))
                ),
                "n_candidates": int(step.get("n_candidates", 0)),
                "completed_swaps": int(step.get("completed_swaps", -1)),
                "select_time_sec": _float(step.get("select_time_sec", 0.0)),
                "slope_change_pct": _float(step.get("slope_change_pct", 0.0)),
                "cont_change": _float(step.get("cont_change", 0.0)),
                "baimu_area_change_ha": _float(step.get("baimu_area_change_ha", 0.0)),
            }
            for index, step in enumerate(steps)
        ],
    }


def markdown_report(payload: dict) -> str:
    config = payload["configuration"]
    outcome = payload["outcome"]
    metrics = payload["final_metrics"]
    lines = [
        "# Paper10 real-environment rollout smoke",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: controlled summary of a short full-Bishan real-environment rollout. This is not a planning-quality result and does not change manuscript performance claims.",
        "",
        "## Command",
        "",
        "```powershell",
        payload["command"],
        "```",
        "",
        f"Raw local output: `{payload['raw_output']}`",
        "",
        "## Configuration",
        "",
        "| field | value |",
        "|---|---|",
    ]
    for key in (
        "checkpoint",
        "prepared_dir",
        "env_source",
        "seed",
        "horizon",
        "top_k",
        "rollout_steps",
        "mask_mode",
        "selector",
        "scoring",
    ):
        lines.append(f"| {key} | `{config.get(key)}` |")

    lines.extend(
        [
            "",
            "## Outcome",
            "",
            "| metric | value |",
            "|---|---:|",
            f"| steps run | {outcome['steps_run']} |",
            f"| total reward | {outcome['total_reward']:.4f} |",
            f"| elapsed seconds | {outcome['elapsed_sec']:.2f} |",
            f"| min base-valid actions | {outcome['min_base_valid']} |",
            f"| min executable-valid actions | {outcome['min_executable_valid']} |",
            f"| mean selection seconds | {outcome['mean_select_time_sec']:.4f} |",
            f"| positive reward steps | {outcome['positive_reward_steps']} |",
            f"| negative reward steps | {outcome['negative_reward_steps']} |",
            f"| final slope change pct | {metrics['slope_change_pct']:.6f} |",
            f"| final contiguity change | {metrics['cont_change']:.6f} |",
            f"| final baimu area change ha | {metrics['baimu_area_change_ha']:.6f} |",
            "",
            "## Step Trace",
            "",
            "| step | action | reward | executable valid | candidates | completed swaps | slope change pct | cont change | baimu area ha | select sec |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for step in payload["steps"]:
        lines.append(
            "| {step} | {action} | {reward:.4f} | {valid} | {candidates} | {swaps} | {slope:.6f} | {cont:.6f} | {baimu:.6f} | {select:.4f} |".format(
                step=step["step"],
                action=step["action"],
                reward=step["reward"],
                valid=step["n_executable_valid"],
                candidates=step["n_candidates"],
                swaps=step["completed_swaps"],
                slope=step["slope_change_pct"],
                cont=step["cont_change"],
                baimu=step["baimu_area_change_ha"],
                select=step["select_time_sec"],
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This smoke confirms the execution chain from a Paper10 checkpoint through the Paper9 adapter, MPC selector, executable mask, and full Bishan `CountyLevelEnv.step`. It is a five-step engineering check, not evidence for a new planning-quality or scale-up claim.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_smoke_report(
    raw_rollout_json: str | Path,
    output_json: str | Path,
    output_md: str | Path,
    *,
    command: str,
    date: str = DATE,
) -> dict:
    raw_path = Path(raw_rollout_json)
    rollout_payload = json.loads(raw_path.read_text(encoding="utf-8"))
    payload = build_smoke_report(
        rollout_payload,
        command=command,
        raw_output=str(raw_path),
        date=date,
    )

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
    parser.add_argument("--raw-rollout-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--command", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = write_smoke_report(
        args.raw_rollout_json,
        args.output_json,
        args.output_md,
        command=args.command,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
