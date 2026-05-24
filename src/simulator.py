import numpy as np

from src.representation import (
    largest_connected_component,
    count_filled_voxels,
    count_active_voxels,
    active_ratio,
    fill_ratio
)


def pseudo_simulated_displacement(genome):
    """
    Fallback simulation-like fitness used when VoxCraft-sim is not available.

    This is not a real physics simulation. It gives a displacement-style score
    based on body size, active material, and rough front-back asymmetry.
    """
    robot = largest_connected_component(genome)

    filled = count_filled_voxels(robot)

    if filled == 0:
        return 0.0

    active = count_active_voxels(robot)
    active_fraction = active_ratio(robot)
    filled_fraction = fill_ratio(robot)

    x_mid = robot.shape[0] // 2
    front_activity = np.sum((robot[x_mid:, :, :] == 2) | (robot[x_mid:, :, :] == 3))
    back_activity = np.sum((robot[:x_mid, :, :] == 2) | (robot[:x_mid, :, :] == 3))

    asymmetry = abs(front_activity - back_activity) / max(active, 1)

    size_score = 1.0 - abs(filled_fraction - 0.35)

    displacement = active * (0.5 + active_fraction) * (0.5 + asymmetry) * size_score

    return float(displacement)


def evaluate_with_simulator(genome, use_voxcraft=False):
    """
    Evaluate a genome with either VoxCraft-sim or the local fallback.

    The VoxCraft-sim path is left as an integration point because the simulator
    is not available in the current local environment.
    """
    if use_voxcraft:
        import tempfile
        import math
        from src.voxcraft_runner import genome_to_vxa, run_voxcraft
        
        with tempfile.NamedTemporaryFile(suffix=".vxa") as tmp_vxa:
            genome_to_vxa(genome, tmp_vxa.name)
            dx, dy, dz = run_voxcraft(tmp_vxa.name)
            distance = math.sqrt(dx**2 + dy**2)
            return (distance,)

    return (pseudo_simulated_displacement(genome),)