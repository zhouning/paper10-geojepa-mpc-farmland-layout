import numpy as np
import pytest

from paper10_geojepa_mpc.experiments.pcc_objectives import (
    OBJECTIVE_NAMES,
    oriented_outcome,
)


def test_oriented_outcome_makes_larger_values_better():
    start = {"avg_slope": 10.0, "contiguity": 0.20, "baimu_area_ha": 100.0}
    end = {"avg_slope": 9.0, "contiguity": 0.25, "baimu_area_ha": 103.0}

    outcome = oriented_outcome(7.5, start, end)

    assert OBJECTIVE_NAMES == (
        "reward",
        "slope_benefit",
        "contiguity_benefit",
        "connected_area_benefit",
    )
    np.testing.assert_allclose(outcome, [7.5, 10.0, 0.05, 3.0])


def test_oriented_outcome_rejects_non_finite_metrics():
    start = {"avg_slope": 10.0, "contiguity": 0.20, "baimu_area_ha": 100.0}
    end = {"avg_slope": np.nan, "contiguity": 0.25, "baimu_area_ha": 103.0}

    with pytest.raises(ValueError, match="finite"):
        oriented_outcome(7.5, start, end)


def test_slope_benefit_is_stable_when_starting_slope_is_zero():
    start = {"avg_slope": 0.0, "contiguity": 0.20, "baimu_area_ha": 100.0}
    end = {"avg_slope": 0.0, "contiguity": 0.20, "baimu_area_ha": 100.0}

    outcome = oriented_outcome(0.0, start, end)

    np.testing.assert_array_equal(outcome, np.zeros(4))
