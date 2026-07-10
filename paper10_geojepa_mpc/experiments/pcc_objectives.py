from collections.abc import Mapping

import numpy as np


OBJECTIVE_NAMES = (
    "reward",
    "slope_benefit",
    "contiguity_benefit",
    "connected_area_benefit",
)


def oriented_outcome(
    reward: float,
    start: Mapping[str, float],
    end: Mapping[str, float],
) -> np.ndarray:
    """Return the four PCC outcomes with larger values consistently better."""
    values = np.asarray(
        [
            reward,
            start["avg_slope"],
            end["avg_slope"],
            start["contiguity"],
            end["contiguity"],
            start["baimu_area_ha"],
            end["baimu_area_ha"],
        ],
        dtype=np.float64,
    )
    if not np.isfinite(values).all():
        raise ValueError("PCC objective inputs must be finite")

    slope_denominator = max(abs(values[1]), 1e-8)
    return np.asarray(
        [
            values[0],
            100.0 * (values[1] - values[2]) / slope_denominator,
            values[4] - values[3],
            values[6] - values[5],
        ],
        dtype=np.float64,
    )
