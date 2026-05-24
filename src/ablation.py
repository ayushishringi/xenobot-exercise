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


def setup_ablation_toolbox(condition, base_toolbox):
    """
    Modify the DEAP toolbox for a specific ablation condition.
    Conditions: 'baseline', 'no_crossover', 'no_connectivity', 'random_selection', 'single_material', 'no_mutation'
    """
    import random
    from deap import tools
    from src.representation import random_genome, count_filled_voxels

    # Clone the toolbox conceptually (DEAP toolboxes are just objects, we can register over them, 
    # but to be safe we might want a fresh one, assuming base_toolbox is fresh).
    tb = base_toolbox
    
    if condition == 'no_connectivity':
        # Override individual generation to NOT use LCC
        tb.register("individual", lambda: tb.Individual(random_genome()))
        
        # Override mutation and crossover to not use LCC
        # (This is tricky since operators in ea.py hardcode LCC. We'll have to redefine them or just let 
        # the user implement the non-LCC versions in ea.py. For the sake of this scaffolding, we provide mock overrides).
        def mock_mut_flip(ind):
            for index in np.ndindex(ind.shape):
                if random.random() < 0.05:
                    ind[index] = random.randint(0, 3)
            return (ind,)
            
        def mock_cx(ind1, ind2):
            cut = random.randint(1, ind1.shape[0] - 1)
            child1 = ind1.copy()
            child2 = ind2.copy()
            child1[:cut, :, :] = ind2[:cut, :, :]
            child2[:cut, :, :] = ind1[:cut, :, :]
            ind1[:] = child1[:]
            ind2[:] = child2[:]
            return ind1, ind2
            
        tb.register("mutate", mock_mut_flip)
        tb.register("mate", mock_cx)

    elif condition == 'random_selection':
        tb.register("select", tools.selRandom)

    elif condition == 'single_material':
        # Only EMPTY (0) and PASSIVE (1)
        def single_mat_genome():
            return np.random.choice([0, 1], size=(8, 8, 8), p=[0.6, 0.4])
        
        tb.register("individual", lambda: tb.Individual(single_mat_genome()))
        
        def single_mat_mut(ind):
            for index in np.ndindex(ind.shape):
                if random.random() < 0.05:
                    ind[index] = random.randint(0, 1)
            return (ind,)
            
        tb.register("mutate", single_mat_mut)

    return tb


def run_ablation_experiments(seeds=3, pop_size=50, generations=200):
    """
    Run the full suite of ablation experiments for Milestone 3.
    """
    from src.ea import toolbox as base_tb, run_evolution
    import copy
    
    conditions = [
        'baseline', 
        'no_crossover', 
        'no_connectivity', 
        'random_selection', 
        'single_material', 
        'no_mutation'
    ]
    
    results = {}
    
    for cond in conditions:
        print(f"Running condition: {cond}")
        cond_results = []
        for seed in range(seeds):
            print(f"  Seed {seed+1}/{seeds}")
            np.random.seed(seed)
            import random
            random.seed(seed)
            
            # Setup specific probabilities
            cxpb = 0.0 if cond == 'no_crossover' else 0.5
            mutpb = 0.0 if cond == 'no_mutation' else 0.3
            
            # Modify toolbox
            tb = setup_ablation_toolbox(cond, copy.copy(base_tb))
            
            # Re-register to the global toolbox in ea.py temporarily 
            # (In a real implementation, run_evolution should accept the toolbox as an argument)
            import src.ea
            old_tb = src.ea.toolbox
            src.ea.toolbox = tb
            
            pop, log, hof, div = run_evolution(
                pop_size=pop_size, 
                generations=generations, 
                cxpb=cxpb, 
                mutpb=mutpb,
                verbose=False
            )
            
            src.ea.toolbox = old_tb
            
            cond_results.append({
                'log': log,
                'hof': hof,
                'div': div
            })
            
        results[cond] = cond_results
        
    return results