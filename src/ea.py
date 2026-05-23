import random
import numpy as np

from deap import base, creator, tools, algorithms

from src.representation import random_genome, largest_connected_component
from src.fitness import evaluate_genome


GRID_SIZE = (8, 8, 8)


try:
    creator.FitnessMax
except AttributeError:
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))

try:
    creator.Individual
except AttributeError:
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)


toolbox = base.Toolbox()


def make_individual():
    genome = random_genome(GRID_SIZE)
    genome = largest_connected_component(genome)
    return creator.Individual(genome)


def mutate_random_flip(individual, flip_prob=0.05):
    """
    Randomly change some voxels to a new material type.
    """
    mutant = individual.copy()

    for index in np.ndindex(mutant.shape):
        if random.random() < flip_prob:
            mutant[index] = random.randint(0, 3)

    mutant = largest_connected_component(mutant)
    individual[:] = mutant[:]

    return (individual,)


def cx_one_point_slice(ind1, ind2):
    """
    Swap part of two robots along the x-axis.
    """
    cut = random.randint(1, ind1.shape[0] - 1)

    child1 = ind1.copy()
    child2 = ind2.copy()

    child1[:cut, :, :] = ind2[:cut, :, :]
    child2[:cut, :, :] = ind1[:cut, :, :]

    child1 = largest_connected_component(child1)
    child2 = largest_connected_component(child2)

    ind1[:] = child1[:]
    ind2[:] = child2[:]

    return ind1, ind2


toolbox.register("individual", make_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_genome)
toolbox.register("mate", cx_one_point_slice)
toolbox.register("mutate", mutate_random_flip)
toolbox.register("select", tools.selTournament, tournsize=3)


def run_evolution(pop_size=30, generations=20, cxpb=0.5, mutpb=0.3):
    """
    Run a basic evolutionary algorithm.
    """
    pop = toolbox.population(n=pop_size)

    hof = tools.HallOfFame(5, similar=np.array_equal)

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("max", np.max)
    stats.register("mean", np.mean)
    stats.register("std", np.std)

    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=generations,
        stats=stats,
        halloffame=hof,
        verbose=True
    )

    return pop, log, hof