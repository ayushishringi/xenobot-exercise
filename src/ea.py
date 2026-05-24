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
    """Randomly flip individual voxels to a new material type."""
    mutant = individual.copy()
    for index in np.ndindex(mutant.shape):
        if random.random() < flip_prob:
            mutant[index] = random.randint(0, 3)
    mutant = largest_connected_component(mutant)
    individual[:] = mutant[:]
    return (individual,)

def mutate_block(individual, block_size=2):
    """Replace a random block_size^3 sub-volume with new random material."""
    mutant = individual.copy()
    x = random.randint(0, mutant.shape[0] - block_size)
    y = random.randint(0, mutant.shape[1] - block_size)
    z = random.randint(0, mutant.shape[2] - block_size)
    for i in range(block_size):
        for j in range(block_size):
            for k in range(block_size):
                mutant[x+i, y+j, z+k] = random.randint(0, 3)
    mutant = largest_connected_component(mutant)
    individual[:] = mutant[:]
    return (individual,)

def mutate_grow_shrink(individual, prob_grow=0.3, prob_shrink=0.3):
    """Add or remove single voxels at the body surface."""
    mutant = individual.copy()
    coords = list(np.ndindex(mutant.shape))
    random.shuffle(coords)
    for index in coords[:20]:
        r = random.random()
        if r < prob_grow and mutant[index] == 0:
            mutant[index] = random.randint(1, 3)
        elif r < prob_grow + prob_shrink and mutant[index] != 0:
            mutant[index] = 0
    mutant = largest_connected_component(mutant)
    individual[:] = mutant[:]
    return (individual,)

def cx_one_point_slice(ind1, ind2):
    """Swap a random XY-plane slice between two robots."""
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

def cx_uniform_voxels(ind1, ind2, indpb=0.5):
    """Uniform crossover: swap each voxel independently."""
    child1 = ind1.copy()
    child2 = ind2.copy()
    for index in np.ndindex(ind1.shape):
        if random.random() < indpb:
            child1[index], child2[index] = child2[index], child1[index]
    child1 = largest_connected_component(child1)
    child2 = largest_connected_component(child2)
    ind1[:] = child1[:]
    ind2[:] = child2[:]
    return ind1, ind2

def diversity(population):
    """Mean pairwise Hamming distance across the population."""
    flat = [ind.flatten() for ind in population]
    n = len(flat)
    if n < 2:
        return 0.0
    total = sum(
        np.sum(flat[i] != flat[j])
        for i in range(n) for j in range(i+1, n)
    )
    return float(total / (n*(n-1)/2))

toolbox.register("individual", make_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate_genome)
toolbox.register("mate", cx_one_point_slice)
toolbox.register("mutate", mutate_random_flip)
toolbox.register("select", tools.selTournament, tournsize=3)

def run_evolution(pop_size=50, generations=100, cxpb=0.5, mutpb=0.3,
                  mutator=None, verbose=True):
    """Run evolutionary algorithm, tracking fitness and diversity."""
    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(10, similar=np.array_equal)

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("max", np.max)
    stats.register("mean", np.mean)
    stats.register("std", np.std)

    # Register chosen mutator
    if mutator is not None:
        toolbox.register("mutate", mutator)

    diversity_log = []

    # Allow custom map function for multiprocessing
    map_func = toolbox.map if hasattr(toolbox, "map") else map

    # Evaluate initial population
    fitnesses = list(map_func(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    log = tools.Logbook()
    log.header = ["gen", "max", "mean", "std", "diversity"]

    for gen in range(generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map_func(toolbox.clone, offspring))

        # Crossover
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        # Mutation
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate invalid
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map_func(toolbox.evaluate, invalid))
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        hof.update(pop)

        div = diversity(pop)
        diversity_log.append(div)
        record = stats.compile(pop)
        record["gen"] = gen
        record["diversity"] = div
        log.record(**record)
        if verbose:
            print(log.stream)

    # Restore default mutator
    toolbox.register("mutate", mutate_random_flip)
    return pop, log, hof, diversity_log
