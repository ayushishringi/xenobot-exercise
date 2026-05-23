from src import fitness
from src.representation import (
    largest_connected_component,
    count_filled_voxels,
    count_active_voxels,
    active_ratio,
    fill_ratio
)


def evaluate_genome(genome):
    """
    Simple placeholder fitness function for Milestone 1.

    This does not use physics simulation yet. It gives a basic score
    based on whether the robot has material, has active voxels, and has
    a reasonable amount of filled space.
    """
    cleaned = largest_connected_component(genome)

    filled = count_filled_voxels(cleaned)

    if filled == 0:
        return (0.0,)

    active = count_active_voxels(cleaned)
    active_fraction = active_ratio(cleaned)
    filled_fraction = fill_ratio(cleaned)

    size_score = 1.0 - abs(filled_fraction - 0.35)

    fitness = active * size_score * (0.5 + active_fraction)

    return (float(fitness),)