import numpy as np
import matplotlib.pyplot as plt


def plot_fitness_curve(logbook, save_path=None):
    """Plot best and mean fitness across generations with std band."""
    generations = logbook.select("gen")
    max_fitness = logbook.select("max")
    mean_fitness = logbook.select("mean")
    std_fitness = logbook.select("std")

    mean_arr = np.array(mean_fitness)
    std_arr = np.array(std_fitness)

    plt.figure(figsize=(10, 4))
    plt.plot(generations, max_fitness, label="Best fitness", color="steelblue")
    plt.plot(generations, mean_fitness, label="Mean fitness", color="coral")
    plt.fill_between(generations,
                     mean_arr - std_arr,
                     mean_arr + std_arr,
                     alpha=0.2, color="coral", label="±1 std")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness over generations")
    plt.legend()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_diversity_curve(diversity_log, save_path=None):
    """Plot mean pairwise Hamming distance over generations."""
    plt.figure(figsize=(10, 4))
    plt.plot(diversity_log, color="green", label="Population diversity")
    plt.xlabel("Generation")
    plt.ylabel("Mean Hamming distance")
    plt.title("Population diversity over generations")
    plt.legend()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_operator_comparison(results_dict, save_path=None):
    """
    Compare multiple operators on a single fitness curve plot.
    results_dict: {operator_name: logbook}
    """
    plt.figure(figsize=(10, 5))
    for name, log in results_dict.items():
        gens = log.select("gen")
        best = log.select("max")
        plt.plot(gens, best, label=name)
    plt.xlabel("Generation")
    plt.ylabel("Best fitness")
    plt.title("Operator comparison — best fitness per generation")
    plt.legend()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_voxel_heatmap(hof_individuals, save_path=None):
    """
    For top-N individuals in HallOfFame, plot material-type frequency per grid cell.
    """
    if len(hof_individuals) == 0:
        return
    grid = np.zeros(hof_individuals[0].shape)
    for ind in hof_individuals:
        active = (ind == 2) | (ind == 3)
        grid += active.astype(float)
    grid /= len(hof_individuals)

    fig, axes = plt.subplots(2, 4, figsize=(14, 6))
    for z, ax in enumerate(axes.flat):
        if z < grid.shape[2]:
            im = ax.imshow(grid[:, :, z], vmin=0, vmax=1, cmap="hot")
            ax.set_title(f"z={z}")
            ax.axis("off")
    fig.colorbar(im, ax=axes.ravel().tolist(), label="Active voxel frequency")
    plt.suptitle("Active voxel heatmap across top individuals")
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
