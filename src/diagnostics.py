import matplotlib.pyplot as plt


def plot_fitness_curve(logbook):
    """
    Plot best and average fitness across generations.
    """
    generations = logbook.select("gen")
    max_fitness = logbook.select("max")
    mean_fitness = logbook.select("mean")

    plt.figure()
    plt.plot(generations, max_fitness, label="Best fitness")
    plt.plot(generations, mean_fitness, label="Mean fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness over generations")
    plt.legend()
    plt.show()