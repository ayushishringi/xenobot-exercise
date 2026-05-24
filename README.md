# Xenobot-Inspired Soft Robot Evolution

This project explores simple voxel-based soft robot bodies inspired by Xenobots. Each robot is represented as a 3D grid of voxels, where each voxel can be empty, passive material, or active material.

## Project features

The project includes:

- random voxel genome generation
- voxel counting and material statistics
- connectivity repair using the largest connected component
- placeholder and fallback displacement-style fitness functions
- a basic evolutionary algorithm using DEAP
- diagnostic plots and voxel visualizations
- PyVista 3D voxel visualizations
- density ablation experiments
- a documented VoxCraft-sim build/integration attempt
- NSGA-II multi-objective evolutionary search

## How to run

Install dependencies:

```bash
pip install -r requirements.txt
```

## Start Jupyter:
```bash
jupyter notebook
```

## Main notebooks:
```
- `notebooks/milestone1_notebook.ipynb`
- `notebooks/milestone2_notebook.ipynb`
- `notebooks/milestone3_notebook.ipynb`
- `notebooks/milestone4_notebook.ipynb`
```

## Project structure
```
src/                  Source code for representation, fitness, evolution, simulation adapters, and visualization
notebooks/            Milestone notebooks
results/              Generated plots, robot images, and experiment outputs
milestone3_results/   VoxCraft-sim build log and ablation outputs
report/               Final report draft and final report files
```

## VoxCraft-sim note

A real VoxCraft-sim integration was attempted in Google Colab with a T4 GPU. The main voxcraft-sim launcher built successfully, but the required vx3_node_worker executable failed to compile in the available CUDA/Boost environment. Because of this, the project documents the integration attempt and uses a fallback displacement-style simulator for local experiments.

The fallback simulator is not claimed to be real VoxCraft-sim physics. It is used to test the evolutionary pipeline, ablation study, and multi-objective optimization workflow.


Then save with **Cmd + S**.

After that, run:

```bash
git status
git add README.md
git commit -m "Update README for final project status"
git push
git status
```

