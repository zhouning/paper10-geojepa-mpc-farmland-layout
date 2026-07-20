from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


@dataclass(frozen=True)
class AblationContract:
    overlay: Mapping[str, object]

    @property
    def changed_fields(self) -> tuple[str, ...]:
        return tuple(self.overlay)


ABLATION_CONTRACTS = MappingProxyType(
    {
        "county_specific_action_embedding": AblationContract(
            MappingProxyType(
                {"representation": "county_specific_action_embedding"}
            )
        ),
        "single_model": AblationContract(
            MappingProxyType({"ensemble_size": 1})
        ),
        "no_aleatoric_scale": AblationContract(
            MappingProxyType({"use_aleatoric_scale": False})
        ),
        "uncalibrated_ensemble_scale": AblationContract(
            MappingProxyType({"use_conformal": False})
        ),
        "reward_only": AblationContract(
            MappingProxyType({"pareto_objectives": ("reward",)})
        ),
        "no_executed_feedback": AblationContract(
            MappingProxyType({"executed_feedback": False})
        ),
        "no_reference_fallback": AblationContract(
            MappingProxyType({"reference_fallback": False})
        ),
        "one_policy_improvement_round": AblationContract(
            MappingProxyType({"policy_round": 1})
        ),
    }
)


def frozen_development_config() -> dict[str, object]:
    return {
        "ensemble_size": 3,
        "joint_coverage": 0.9,
        "tolerance_scale": 0.05,
        "planning_horizon": 3,
        "residual_window": 10,
        "policy_round": 2,
        "representation": "action_relative",
        "use_aleatoric_scale": True,
        "use_conformal": True,
        "pareto_objectives": tuple(OBJECTIVE_NAMES),
        "executed_feedback": True,
        "reference_fallback": True,
    }


def apply_ablation(
    base: Mapping[str, object],
    name: str,
) -> dict[str, object]:
    try:
        contract = ABLATION_CONTRACTS[str(name)]
    except KeyError as exc:
        raise ValueError(f"unknown PCC ablation: {name}") from exc
    changed = deepcopy(dict(base))
    for path, value in contract.overlay.items():
        if path not in changed:
            raise ValueError(f"ablation field is absent from base config: {path}")
        changed[path] = deepcopy(value)
    changed["ablation"] = str(name)
    return changed


def differing_paths(
    left: Mapping[str, object],
    right: Mapping[str, object],
) -> set[str]:
    paths = set()
    for key in set(left) | set(right):
        if key not in left or key not in right:
            paths.add(str(key))
            continue
        left_value = left[key]
        right_value = right[key]
        if isinstance(left_value, Mapping) and isinstance(right_value, Mapping):
            paths.update(
                f"{key}.{child}"
                for child in differing_paths(left_value, right_value)
            )
        elif left_value != right_value:
            paths.add(str(key))
    return paths


def resolve_ablation_ensemble(
    ensemble: Sequence[object],
    *,
    ensemble_size: int,
) -> list[object]:
    if int(ensemble_size) <= 0:
        raise ValueError("ablation ensemble size must be positive")
    if len(ensemble) < int(ensemble_size):
        raise ValueError("checkpoint ensemble is smaller than requested")
    return list(ensemble[: int(ensemble_size)])
