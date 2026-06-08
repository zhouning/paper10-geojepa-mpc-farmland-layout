import numpy as np

from paper10_geojepa_mpc.planning.env_masks import executable_swap_mask


class TinyEnv:
    def __init__(self):
        self.block_parcels = [
            np.array([0, 1, 6]),
            np.array([2, 3]),
            np.array([4, 5]),
        ]
        self.land_use = np.array([1, 2, 1, 2, 1, 2, 1], dtype=np.int8)
        self.swapped = np.zeros(7, dtype=bool)
        self.slopes = np.array([10.0, 5.0, 3.0, 9.0, 8.0, 7.0, 4.0])
        self.farmland_nbr_count = np.zeros(7, dtype=np.int32)
        self.delta_conn = 0.5
        self.gamma_conn = 1.0


def test_executable_swap_mask_excludes_blocks_without_positive_greedy_pair():
    env = TinyEnv()

    mask = executable_swap_mask(env)

    assert mask.tolist() == [True, False, True]


def test_executable_swap_mask_honors_connectivity_adjusted_scores():
    env = TinyEnv()
    env.farmland_nbr_count[0] = 20

    mask = executable_swap_mask(env)

    assert mask.tolist() == [False, False, True]
