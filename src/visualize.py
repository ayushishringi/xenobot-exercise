import matplotlib.pyplot as plt
import numpy as np

try:
    import pyvista as pv
    # Force static backend to avoid trame/asyncio conflicts in Jupyter (Python 3.13)
    pv.set_jupyter_backend('static')
except ImportError:
    pv = None

from src.representation import EMPTY, PASSIVE, ACTIVE_P, ACTIVE_N


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

MAT_COLORS = {
    PASSIVE: [0.8, 0.8, 0.8],  # grey
    ACTIVE_P: [0.2, 0.6, 1.0],  # blue
    ACTIVE_N: [1.0, 0.3, 0.1],  # red
}

def render_genome(genome, title='Xenobot', save_path=None):
    """Render voxel genome as coloured cubes using PyVista (static inline display)."""
    if pv is None:
        print("PyVista is not installed. Skipping 3D render.")
        return None

    # Always render off-screen to avoid trame/asyncio issues in Jupyter
    # Use a large window size for high-quality full-screen renders
    plotter = pv.Plotter(off_screen=True, window_size=[1600, 1000])
    for mat, color in MAT_COLORS.items():
        coords = np.argwhere(genome == mat)
        for x, y, z in coords:
            cube = pv.Cube(center=(x, y, z), x_length=0.95, y_length=0.95, z_length=0.95)
            plotter.add_mesh(cube, color=color, opacity=0.9)
    plotter.add_text(title, font_size=12)
    plotter.show_grid()

    # Save screenshot and display inline
    out_path = save_path if save_path else "/tmp/pyvista_render.png"
    plotter.screenshot(out_path)
    plotter.close()

    # Display inline in Jupyter at full cell width
    try:
        from IPython.display import Image, display
        display(Image(filename=out_path, width=1400))
    except ImportError:
        print(f"Saved render to: {out_path}")

    return out_path


def export_genome_to_stl(genome, save_path):
    """
    Export the voxel genome to an STL file for 3D printing.
    """
    if pv is None:
        print("PyVista is not installed. Cannot export STL.")
        return False

    meshes = []
    coords = np.argwhere(genome != EMPTY)
    for x, y, z in coords:
        cube = pv.Cube(center=(x, y, z), x_length=1.0, y_length=1.0, z_length=1.0)
        meshes.append(cube)

    if not meshes:
        print("Genome is empty! Cannot export STL.")
        return False

    # Merge all meshes into a single mesh
    combined = meshes[0]
    for next_mesh in meshes[1:]:
        combined = combined.merge(next_mesh)

    # Save as STL
    combined.save(save_path)
    print(f"Successfully exported STL mesh to {save_path}")
    return True