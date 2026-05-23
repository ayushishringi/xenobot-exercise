# Xenobot-Inspired Soft Robot Evolution

This project explores simple voxel-based soft robot bodies inspired by Xenobots. Each robot is represented as a 3D grid of voxels, where each voxel can be empty, passive material, or active material.

So far, the project includes:
- random voxel genome generation
- voxel counting and material statistics
- connectivity repair using the largest connected component
- a simple placeholder fitness function for testing
- a basic evolutionary algorithm using DEAP
- diagnostic plots and voxel visualizations

The full project will later include simulation-based fitness, extended experiments, and robot videos.

## How to run

Install dependencies:

```bash
pip install -r requirements.txt