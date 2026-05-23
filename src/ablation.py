import numpy as np

from src.representation import random_genome
from src.simulator import evaluate_with_simulator


def run_density_ablation(densities=(0.2, 0.4, 0.6, 0.8), trials=10):
    """
    Test how initial genome density affects fallback displacement score.
    """
    results = []

    for density in densities:
        scores = []

        for _ in range(trials):
            genome = random_genome(density=density)
            score = evaluate_with_simulator(genome)[0]
            scores.append(score)

        results.append({
            "density": density,
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores)),
            "best_score": float(np.max(scores))
        })

    return results


def print_ablation_results(results):
    """
    Print ablation results in a readable table-like format.
    """
    print("density\tmean_score\tstd_score\tbest_score")

    for row in results:
        print(
            f"{row['density']}\t"
            f"{row['mean_score']:.3f}\t"
            f"{row['std_score']:.3f}\t"
            f"{row['best_score']:.3f}"
        )