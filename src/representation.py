import numpy as np

EMPTY = 0
PASSIVE = 1
ACTIVE_P = 2
ACTIVE_N = 3


def random_genome(grid_size=(8, 8, 8), density=0.4):
    """
    Create a random voxel robot.

    0 = empty
    1 = passive material
    2 = active positive material
    3 = active negative material
    """
    genome = np.random.choice(
        [EMPTY, PASSIVE, ACTIVE_P, ACTIVE_N],
        size=grid_size,
        p=[1 - density, density / 3, density / 3, density / 3]
    )

    return genome
def count_filled_voxels(genome):
    """
    Count how many voxels are not empty.
    """
    return int(np.sum(genome != EMPTY))


def count_active_voxels(genome):
    """
    Count how many voxels are active material.
    """
    active_positive = genome == ACTIVE_P
    active_negative = genome == ACTIVE_N

    return int(np.sum(active_positive | active_negative))


def active_ratio(genome):
    """
    Calculate what fraction of the filled body is active material.
    """
    filled = count_filled_voxels(genome)

    if filled == 0:
        return 0.0

    active = count_active_voxels(genome)
    return active / filled


def total_voxels(genome):
    """
    Count the total number of voxel positions in the grid.
    """
    return int(genome.size)

def fill_ratio(genome):
    """
    Calculate what fraction of the grid is filled with material.
    """
    filled = count_filled_voxels(genome)
    total = total_voxels(genome)

    return filled / total