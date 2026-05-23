# Evolving Life: Designing Xenobot-Inspired Soft Robots

## Abstract

This project explores the design of simple voxel-based soft robots inspired by Xenobots. Each candidate robot is represented as an 8 by 8 by 8 grid of voxel materials. A basic evolutionary algorithm is used to search for robot bodies with useful structural and active-material properties. The current implementation includes genome generation, connectivity repair, placeholder fitness evaluation, evolutionary search, and diagnostic visualization.

## Introduction

Xenobots are biological-inspired soft robots made from living cells, and they motivate the idea that body structure itself can contribute to behavior. In this project, I modeled each robot as a 3D voxel grid. Each voxel can be empty, passive material, or active material. This representation makes it possible to randomly generate robot bodies and then improve them using evolutionary algorithms.

## Methods

Each genome is stored as a NumPy array with shape 8 by 8 by 8. The value 0 represents empty space, 1 represents passive material, and 2 and 3 represent active materials. After generating a random genome, I applied a largest connected component repair step. This removes disconnected voxel islands and keeps the main connected body.

For early testing, I used a placeholder fitness function instead of a full physics simulator. The score rewards robots that have active material, are connected, and have a reasonable filled volume. This allowed me to test the evolutionary pipeline before adding full simulation.

The evolutionary algorithm was implemented with DEAP. It uses tournament selection, slice-based crossover, and random voxel mutation. The population is evaluated over multiple generations, and the best individuals are stored in a Hall of Fame.

## Experiments

I first tested random genome generation and measured the number of filled voxels, active voxels, fill ratio, and active ratio. I then tested connectivity repair by comparing the number of filled voxels before and after keeping the largest connected component.

For the evolutionary experiment, I ran a baseline evolutionary algorithm with a population size of 30 for 20 generations. I plotted the best and mean fitness values over generations to check whether the search improved over time.

## Results and Discussion

The random genomes often contained disconnected voxel groups, so the connectivity repair step was important. After repair, the number of filled voxels usually decreased because smaller disconnected pieces were removed.

The evolutionary run showed an increase in best fitness and mean fitness over generations. This suggests that selection, mutation, and crossover were able to improve the population according to the placeholder fitness function. The best evolved robot was also visualized using material distribution plots and voxel slice plots.

The current fitness function is not a full movement simulation, so the results should be interpreted as pipeline validation rather than final locomotion performance. The next step would be to replace the placeholder score with VoxCraft-sim displacement-based fitness.

## Conclusion

This project implemented the first stages of a Xenobot-inspired soft robot evolution pipeline. The code can generate voxel robots, repair disconnected bodies, score candidates, run a basic evolutionary algorithm, and visualize the results. The main limitation is that the current fitness function is only a placeholder, but the structure is ready for simulation-based evaluation.

## References

- Kriegman et al. (2020), A scalable pipeline for designing reconfigurable organisms.
- Kriegman et al. (2021), Kinematic self-replication in reconfigurable organisms.
- Cheney et al. (2014), Unshackling Evolution: Evolving Soft Robots with Multiple Materials and a Powerful Generative Encoding.
- DEAP documentation.
- VoxCraft-sim documentation.