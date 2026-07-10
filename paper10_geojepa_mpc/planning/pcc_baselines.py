from typing import Protocol

import numpy as np


class ObservablePolicy(Protocol):
    def select(self, state: dict) -> tuple[int, dict]: ...

    def observe(self, transition: dict) -> None: ...


def matched_pool_size(ensemble_size: int, budget: int = 50) -> int:
    if int(ensemble_size) <= 0 or int(budget) <= 0:
        raise ValueError("ensemble_size and budget must be positive")
    return max(1, int(budget) // int(ensemble_size))


class NoOraclePolicy:
    def __init__(self, policy: ObservablePolicy):
        self.policy = policy

    def select(self, state: dict) -> tuple[int, dict]:
        action, raw_info = self.policy.select(state)
        info = dict(raw_info)
        queries = int(info.get("unexecuted_real_reward_queries", 0))
        if queries != 0:
            raise RuntimeError("deployable baseline queried unexecuted real reward")
        info["unexecuted_real_reward_queries"] = 0
        return int(action), info

    def observe(self, transition: dict) -> None:
        observe = getattr(self.policy, "observe", None)
        if observe is not None:
            observe(transition)


class ExecutableRandomPolicy:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def select(self, state: dict) -> tuple[int, dict]:
        valid = np.flatnonzero(
            np.asarray(state["executable_mask"], dtype=bool)
        ).astype(np.int64)
        if valid.size == 0:
            raise ValueError("executable random policy received an empty action mask")
        return int(self.rng.choice(valid)), {
            "policy": "executable_random",
            "unexecuted_real_reward_queries": 0,
        }

    def observe(self, transition: dict) -> None:
        return None


class OnlineExpertSelector:
    def __init__(
        self,
        experts,
        *,
        learning_rate: float,
        rng: np.random.Generator,
    ):
        if not experts:
            raise ValueError("online expert selector requires at least one expert")
        if not np.isfinite(learning_rate) or float(learning_rate) <= 0.0:
            raise ValueError("expert learning rate must be positive and finite")
        self.experts = list(experts)
        self.learning_rate = float(learning_rate)
        self.rng = rng
        self.log_weights = np.zeros(len(self.experts), dtype=np.float64)
        self.last_selected_expert: int | None = None
        self._last_probability: float | None = None

    def _probabilities(self) -> np.ndarray:
        centered = self.log_weights - self.log_weights.max()
        weights = np.exp(centered)
        return weights / weights.sum()

    def select(self, state: dict) -> tuple[int, dict]:
        if self.last_selected_expert is not None:
            raise RuntimeError("expert selector requires observe before next select")
        probabilities = self._probabilities()
        selected = int(self.rng.choice(len(self.experts), p=probabilities))
        action, raw_info = self.experts[selected].select(state)
        info = dict(raw_info)
        if int(info.get("unexecuted_real_reward_queries", 0)) != 0:
            raise RuntimeError("selected expert queried unexecuted real reward")
        self.last_selected_expert = selected
        self._last_probability = float(probabilities[selected])
        info.update(
            {
                "selected_expert": selected,
                "expert_probability": self._last_probability,
                "unexecuted_real_reward_queries": 0,
            }
        )
        return int(action), info

    def observe(self, transition: dict) -> None:
        if self.last_selected_expert is None or self._last_probability is None:
            raise RuntimeError("expert selector observe called before select")
        selected = self.last_selected_expert
        observe = getattr(self.experts[selected], "observe", None)
        if observe is not None:
            observe(transition)
        reward = float(transition["reward"])
        if not np.isfinite(reward):
            raise ValueError("executed expert reward must be finite")
        importance_weighted_reward = reward / max(self._last_probability, 1e-12)
        self.log_weights[selected] += (
            self.learning_rate * importance_weighted_reward / len(self.experts)
        )
        self.last_selected_expert = None
        self._last_probability = None


def _build_from_factory(name: str, factories: dict):
    if name not in factories:
        raise ValueError(f"missing policy factory for baseline: {name}")
    policy = factories[name]()
    return NoOraclePolicy(policy)


def build_baseline(name: str, context: dict) -> ObservablePolicy:
    name = str(name)
    if name == "oracle_action_audit_diagnostic":
        raise ValueError("oracle action audit is diagnostic and not deployable")
    rng = context.get("rng")
    if not isinstance(rng, np.random.Generator):
        raise ValueError("baseline context requires a NumPy Generator")
    if name == "executable_random":
        return ExecutableRandomPolicy(rng)

    factories = context.get("policy_factories", {})
    if name == "online_expert_selector":
        expert_names = list(context.get("expert_names", []))
        if not expert_names or "online_expert_selector" in expert_names:
            raise ValueError("online expert set is empty or recursive")
        experts = [_build_from_factory(expert, factories) for expert in expert_names]
        return OnlineExpertSelector(
            experts,
            learning_rate=float(context["expert_learning_rate"]),
            rng=rng,
        )
    allowed = {
        "paper9_mpc",
        "legacy_value_filter",
        "model_reward_greedy",
        "rank_only",
        "distributional_risk",
        "pcc_matched",
        "pcc_full",
    }
    if name not in allowed:
        raise ValueError(f"unknown deployable baseline: {name}")
    return _build_from_factory(name, factories)
