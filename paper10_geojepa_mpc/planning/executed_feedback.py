from collections import deque

import numpy as np

from paper10_geojepa_mpc.experiments.pcc_objectives import OBJECTIVE_NAMES


class ExecutedFeedbackScaler:
    def __init__(
        self,
        window: int,
        q_joint: float,
        objective_count: int = len(OBJECTIVE_NAMES),
    ):
        if int(window) <= 0:
            raise ValueError("window must be positive")
        if not np.isfinite(q_joint) or float(q_joint) < 0.0:
            raise ValueError("q_joint must be finite and non-negative")
        if int(objective_count) <= 0:
            raise ValueError("objective_count must be positive")
        self.window = int(window)
        self.q_joint = float(q_joint)
        self.objective_count = int(objective_count)
        self._ratios = deque(maxlen=self.window)

    def update(self, observed, predicted, base_scale) -> None:
        observed = np.asarray(observed, dtype=np.float64).reshape(-1)
        predicted = np.asarray(predicted, dtype=np.float64).reshape(-1)
        base_scale = np.asarray(base_scale, dtype=np.float64).reshape(-1)
        expected_shape = (self.objective_count,)
        if (
            observed.shape != expected_shape
            or predicted.shape != expected_shape
            or base_scale.shape != expected_shape
        ):
            raise ValueError("executed feedback must have one value per objective")
        if not (
            np.isfinite(observed).all()
            and np.isfinite(predicted).all()
            and np.isfinite(base_scale).all()
        ):
            raise ValueError("executed feedback values must be finite")
        if np.any(base_scale <= 0.0):
            raise ValueError("executed feedback base scale must be positive")
        ratio = np.abs(observed - predicted) / base_scale
        self._ratios.append(ratio)

    def multiplier(self) -> np.ndarray:
        if not self._ratios:
            return np.ones(self.objective_count, dtype=np.float64)
        maximum_ratio = np.stack(tuple(self._ratios), axis=0).max(axis=0)
        denominator = max(self.q_joint, 1e-8)
        return np.clip(maximum_ratio / denominator, 1.0, 3.0)

    def state_dict(self) -> dict[str, object]:
        return {
            "window": self.window,
            "q_joint": self.q_joint,
            "objective_count": self.objective_count,
            "ratios": [ratio.tolist() for ratio in self._ratios],
        }

    @classmethod
    def from_state_dict(cls, state: dict[str, object]):
        scaler = cls(
            window=int(state["window"]),
            q_joint=float(state["q_joint"]),
            objective_count=int(state["objective_count"]),
        )
        for raw_ratio in state.get("ratios", []):
            ratio = np.asarray(raw_ratio, dtype=np.float64).reshape(-1)
            if ratio.shape != (scaler.objective_count,) or not np.isfinite(
                ratio
            ).all():
                raise ValueError("stored executed feedback ratios are invalid")
            scaler._ratios.append(ratio)
        return scaler
