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


class SelectorPolicy:
    def __init__(self, selector, rng: np.random.Generator, name: str):
        self.selector = selector
        self.rng = rng
        self.name = str(name)

    def select(self, state: dict) -> tuple[int, dict]:
        action, raw_info = self.selector(state, self.rng)
        info = dict(raw_info)
        info.setdefault("policy", self.name)
        info.setdefault("unexecuted_real_reward_queries", 0)
        return int(action), info

    def observe(self, transition: dict) -> None:
        return None


class PCCObservablePolicy:
    def __init__(
        self,
        *,
        ensemble,
        calibrator,
        feedback_scaler,
        reference_policy,
        proposal_rankers,
        candidate_budget: int,
        planning_horizon: int,
        tolerances,
        executable_threshold: float,
        device: str = "cpu",
        max_member_evaluations: int | None = None,
        use_aleatoric_scale: bool = True,
        use_conformal: bool = True,
        pareto_objectives=(
            "reward",
            "slope_benefit",
            "contiguity_benefit",
            "connected_area_benefit",
        ),
        executed_feedback: bool = True,
        reference_fallback: bool = True,
    ):
        self.ensemble = ensemble
        self.calibrator = calibrator
        self.feedback_scaler = feedback_scaler
        self.reference_policy = reference_policy
        self.proposal_rankers = list(proposal_rankers)
        self.candidate_budget = int(candidate_budget)
        self.planning_horizon = int(planning_horizon)
        self.tolerances = np.asarray(tolerances, dtype=np.float64)
        self.executable_threshold = float(executable_threshold)
        self.device = str(device)
        self.max_member_evaluations = max_member_evaluations
        self.use_aleatoric_scale = bool(use_aleatoric_scale)
        self.use_conformal = bool(use_conformal)
        self.pareto_objectives = tuple(pareto_objectives)
        self.executed_feedback = bool(executed_feedback)
        self.reference_fallback = bool(reference_fallback)

    def select(self, state: dict) -> tuple[int, dict]:
        from paper10_geojepa_mpc.planning.pcc_selector import pcc_select_action

        reference_action, reference_info = self.reference_policy.select(state)
        proposal_groups = [ranker(state) for ranker in self.proposal_rankers]
        action, info = pcc_select_action(
            ensemble=self.ensemble,
            calibrator=self.calibrator,
            feedback_scaler=self.feedback_scaler,
            block_features=state["block_features"],
            neighbour_features=state["neighbour_features"],
            global_features=state["global_features"],
            executable_mask=state["executable_mask"],
            reference_policy=lambda: reference_action,
            proposal_groups=proposal_groups,
            candidate_budget=self.candidate_budget,
            planning_horizon=self.planning_horizon,
            tolerances=self.tolerances,
            executable_threshold=self.executable_threshold,
            device=self.device,
            max_member_evaluations=self.max_member_evaluations,
            use_aleatoric_scale=self.use_aleatoric_scale,
            use_conformal=self.use_conformal,
            pareto_objectives=self.pareto_objectives,
            reference_fallback=self.reference_fallback,
        )
        info["reference_policy_info"] = reference_info
        info["executed_feedback"] = self.executed_feedback
        return action, info

    def observe(self, transition: dict) -> None:
        if not self.executed_feedback:
            return
        predicted = transition.get("predicted_mean")
        scale = transition.get("base_scale")
        if predicted is None or scale is None:
            raise ValueError("PCC executed transition lacks immediate prediction")
        self.feedback_scaler.update(
            transition["observed_outcome"],
            predicted,
            scale,
        )


class GreedyRankingPolicy:
    def __init__(self, ranker, name: str):
        self.ranker = ranker
        self.name = str(name)

    def select(self, state: dict) -> tuple[int, dict]:
        ranked = np.asarray(self.ranker(state), dtype=np.int64).reshape(-1)
        if ranked.size == 0:
            raise ValueError(f"{self.name} received no executable candidates")
        return int(ranked[0]), {
            "policy": self.name,
            "n_candidates": int(ranked.size),
            "unexecuted_real_reward_queries": 0,
        }

    def observe(self, transition: dict) -> None:
        return None


class DistributionalRiskPolicy:
    def __init__(
        self,
        *,
        ensemble,
        proposal_rankers,
        candidate_budget: int,
        planning_horizon: int,
        risk_penalty: float,
        device: str = "cpu",
    ):
        if float(risk_penalty) < 0.0:
            raise ValueError("risk penalty must be non-negative")
        self.ensemble = ensemble
        self.proposal_rankers = list(proposal_rankers)
        self.candidate_budget = int(candidate_budget)
        self.planning_horizon = int(planning_horizon)
        self.risk_penalty = float(risk_penalty)
        self.device = str(device)

    def select(self, state: dict) -> tuple[int, dict]:
        from paper10_geojepa_mpc.planning.pcc_selector import (
            build_candidate_pool,
            predict_paired_ensemble,
        )

        proposal_groups = [ranker(state) for ranker in self.proposal_rankers]
        if not proposal_groups or len(proposal_groups[0]) == 0:
            raise ValueError("distributional risk policy received no proposals")
        reference_action = int(proposal_groups[0][0])
        actions = build_candidate_pool(
            reference_action=reference_action,
            proposal_groups=proposal_groups,
            executable_mask=state["executable_mask"],
            candidate_budget=self.candidate_budget,
        )
        prediction = predict_paired_ensemble(
            self.ensemble,
            block_features=state["block_features"],
            neighbour_features=state["neighbour_features"],
            global_features=state["global_features"],
            actions=actions,
            reference_action=reference_action,
            planning_horizon=self.planning_horizon,
            device=self.device,
        )
        score = (
            prediction.candidate_mean[:, 0]
            - self.risk_penalty * prediction.candidate_base_scale[:, 0]
        )
        order = np.lexsort((actions, -score))
        selected = int(order[0])
        return int(actions[selected]), {
            "policy": "distributional_risk",
            "risk_penalty": self.risk_penalty,
            "risk_score": float(score[selected]),
            "member_evaluations": prediction.member_evaluations,
            "model_forward_count": prediction.model_forward_count,
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
