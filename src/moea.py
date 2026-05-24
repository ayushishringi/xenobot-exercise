import random
import numpy as np
from deap import base, creator, tools, algorithms

from src.representation import (
    random_genome,
    largest_connected_component,
    count_filled_voxels,
    active_ratio
)
from src.simulator import evaluate_with_simulator

# Global toggle for VoxCraft-sim
USE_VOXCRAFT = False

def clone_genome(genome):
    return np.array(genome, copy=True)


def mutate_genome(genome, indpb=0.05):
    mutated = np.array(genome, copy=True)

    for index in np.ndindex(mutated.shape):
        if random.random() < indpb:
            mutated[index] = random.randint(0, 3)

    return largest_connected_component(mutated)


def crossover_genomes(parent1, parent2):
    child1 = np.array(parent1, copy=True)
    child2 = np.array(parent2, copy=True)

    split = random.randint(1, parent1.shape[0] - 1)

    child1[:split, :, :] = parent1[:split, :, :]
    child1[split:, :, :] = parent2[split:, :, :]

    child2[:split, :, :] = parent2[:split, :, :]
    child2[split:, :, :] = parent1[split:, :, :]

    return largest_connected_component(child1), largest_connected_component(child2)


MIN_VOXELS = 5  # Minimum number of filled voxels for a valid robot

def evaluate_multiobjective(genome):
    """
    Multi-objective fitness:
    1. Maximize simulated displacement.
    2. Minimize filled voxel count (but penalize empty/trivial robots).
    3. Maximize active material ratio.
    """
    cleaned = largest_connected_component(genome)
    filled = count_filled_voxels(cleaned)

    # Penalize degenerate robots with too few voxels
    if filled < MIN_VOXELS:
        return 0.0, float(filled), 0.0

    displacement = evaluate_with_simulator(cleaned, use_voxcraft=USE_VOXCRAFT)[0]
    active = active_ratio(cleaned)

    return float(displacement), float(filled), float(active)


def setup_toolbox():
    if not hasattr(creator, "FitnessMulti"):
        creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0, 1.0))

    if not hasattr(creator, "IndividualMulti"):
        creator.create("IndividualMulti", np.ndarray, fitness=creator.FitnessMulti)

    toolbox = base.Toolbox()

    toolbox.register(
        "individual",
        lambda: creator.IndividualMulti(random_genome())
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("clone", lambda ind: creator.IndividualMulti(clone_genome(ind)))
    toolbox.register("evaluate", evaluate_multiobjective)
    toolbox.register("mate", crossover_genomes)
    toolbox.register("mutate", mutate_genome)
    toolbox.register("select", tools.selNSGA2)

    return toolbox


def run_multiobjective_evolution(pop_size=32, generations=20, cxpb=0.5, mutpb=0.3):
    # DEAP's selTournamentDCD requires the population size to be a multiple of 4
    if pop_size % 4 != 0:
        pop_size = pop_size + (4 - (pop_size % 4))
        print(f"Adjusted population size to {pop_size} to be a multiple of 4 for NSGA-II.")

    toolbox = setup_toolbox()

    population = toolbox.population(n=pop_size)

    invalid = [ind for ind in population if not ind.fitness.valid]
    for ind in invalid:
        ind.fitness.values = toolbox.evaluate(ind)

    population = toolbox.select(population, len(population))

    log = []

    for gen in range(generations + 1):
        scores = [ind.fitness.values for ind in population]

        log.append({
            "gen": gen,
            "max_displacement": float(max(s[0] for s in scores)),
            "mean_displacement": float(np.mean([s[0] for s in scores])),
            "min_voxels": float(min(s[1] for s in scores)),
            "mean_voxels": float(np.mean([s[1] for s in scores])),
            "max_active_ratio": float(max(s[2] for s in scores))
        })

        if gen == generations:
            break

        offspring = tools.selTournamentDCD(population, len(population))
        offspring = [toolbox.clone(ind) for ind in offspring]

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                new_child1, new_child2 = toolbox.mate(child1, child2)
                child1[:] = new_child1
                child2[:] = new_child2
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < mutpb:
                mutant[:] = toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid:
            ind.fitness.values = toolbox.evaluate(ind)

        population = toolbox.select(population + offspring, pop_size)

    pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]

    # Filter out degenerate robots with too few voxels from the Pareto front
    pareto_front = [ind for ind in pareto_front if count_filled_voxels(largest_connected_component(ind)) >= MIN_VOXELS]

    return population, log, pareto_front