import numpy as np


FARMLAND = 1
FOREST = 2


def executable_swap_mask(env) -> np.ndarray:
    mask = np.zeros(len(env.block_parcels), dtype=bool)
    land_use = env.land_use
    swapped = env.swapped
    slopes = env.slopes
    nbr_count = env.farmland_nbr_count
    delta_conn = float(getattr(env, "delta_conn", 0.5))
    gamma_conn = float(getattr(env, "gamma_conn", 1.0))

    for block_id, parcels in enumerate(env.block_parcels):
        parcels = np.asarray(parcels)
        avail = ~swapped[parcels]
        types = land_use[parcels]
        farm_idx = parcels[(types == FARMLAND) & avail]
        forest_idx = parcels[(types == FOREST) & avail]
        if farm_idx.size == 0 or forest_idx.size == 0:
            continue

        farm_scores = slopes[farm_idx] - delta_conn * nbr_count[farm_idx]
        forest_scores = slopes[forest_idx] - gamma_conn * nbr_count[forest_idx]
        best_farm = farm_idx[int(np.argmax(farm_scores))]
        best_forest = forest_idx[int(np.argmin(forest_scores))]
        mask[block_id] = bool(slopes[best_farm] > slopes[best_forest])

    return mask
