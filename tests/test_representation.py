import numpy as np
import pytest

from src.fitness import evaluate_genome
from src.representation import (
    ACTIVE_N,
    ACTIVE_P,
    EMPTY,
    PASSIVE,
    active_ratio,
    count_active_voxels,
    count_filled_voxels,
    fill_ratio,
    largest_connected_component,
    random_genome,
)
from src.simulator import pseudo_simulated_displacement


def test_random_genome_shape_and_materials():
    np.random.seed(0)
    genome = random_genome(grid_size=(6, 5, 4), density=0.4)
    assert genome.shape == (6, 5, 4)
    assert set(np.unique(genome)) <= {EMPTY, PASSIVE, ACTIVE_P, ACTIVE_N}


@pytest.mark.parametrize("density", [0.0, 1.0])
def test_random_genome_density_extremes(density):
    np.random.seed(0)
    genome = random_genome(grid_size=(4, 4, 4), density=density)
    assert fill_ratio(genome) == density


def test_counts_and_ratios_on_known_grid():
    genome = np.zeros((2, 2, 2), dtype=int)
    genome[0, 0, 0] = PASSIVE
    genome[0, 0, 1] = ACTIVE_P
    genome[0, 1, 0] = ACTIVE_N
    assert count_filled_voxels(genome) == 3
    assert count_active_voxels(genome) == 2
    assert active_ratio(genome) == pytest.approx(2 / 3)
    assert fill_ratio(genome) == pytest.approx(3 / 8)


def test_active_ratio_of_empty_body_is_zero():
    assert active_ratio(np.zeros((3, 3, 3), dtype=int)) == 0.0


def test_largest_connected_component_keeps_only_biggest_body():
    genome = np.zeros((5, 5, 5), dtype=int)
    genome[0, 0, 0:3] = ACTIVE_P  # 3-voxel bar
    genome[4, 4, 4] = PASSIVE  # isolated voxel, not face-connected
    cleaned = largest_connected_component(genome)
    assert count_filled_voxels(cleaned) == 3
    assert cleaned[4, 4, 4] == EMPTY
    # Materials of the kept voxels are unchanged, and the input is not modified.
    assert (cleaned[0, 0, 0:3] == ACTIVE_P).all()
    assert genome[4, 4, 4] == PASSIVE


def test_largest_connected_component_of_empty_grid():
    genome = np.zeros((3, 3, 3), dtype=int)
    cleaned = largest_connected_component(genome)
    assert count_filled_voxels(cleaned) == 0
    assert cleaned is not genome


def test_fitness_functions_are_zero_for_empty_and_positive_for_active_body():
    empty = np.zeros((4, 4, 4), dtype=int)
    assert evaluate_genome(empty) == (0.0,)
    assert pseudo_simulated_displacement(empty) == 0.0

    body = np.zeros((4, 4, 4), dtype=int)
    body[2:4, :, :] = ACTIVE_P  # front half active: asymmetric, connected
    assert evaluate_genome(body)[0] > 0
    assert pseudo_simulated_displacement(body) > 0
