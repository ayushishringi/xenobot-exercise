import matplotlib.pyplot as plt

from src.representation import EMPTY


def plot_voxel_slices(genome, save_path=None):
    """
    Plot each z-slice of the voxel robot as a 2D grid.
    """
    z_size = genome.shape[2]

    for z in range(z_size):
        plt.figure()
        plt.imshow(genome[:, :, z], vmin=0, vmax=3)
        plt.title(f"Voxel slice z={z}")
        plt.xlabel("y")
        plt.ylabel("x")
        plt.colorbar(label="material type")

        if save_path is not None:
            filename = f"{save_path}_slice_{z}.png"
            plt.savefig(filename, dpi=150, bbox_inches="tight")

        plt.show()

def plot_material_counts(genome):
    """
    Plot how many voxels belong to each material type.
    """
    material_names = ["empty", "passive", "active +", "active -"]
    counts = []

    for material_id in range(4):
        count = (genome == material_id).sum()
        counts.append(count)

    plt.figure()
    plt.bar(material_names, counts)
    plt.xlabel("Material type")
    plt.ylabel("Voxel count")
    plt.title("Material distribution")
    plt.show()