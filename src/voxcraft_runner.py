import subprocess
import tempfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from src.representation import EMPTY, PASSIVE, ACTIVE_P, ACTIVE_N

VOXCRAFT_BIN = Path(os.environ.get('VOXCRAFT_BIN', 'voxcraft-sim'))

MATERIAL_MAP = {
    PASSIVE: {'r': 0.01, 'E': 1e6, 'rho': 1e3, 'nu': 0.35},
    ACTIVE_P: {'r': 0.01, 'E': 5e5, 'rho': 1e3, 'nu': 0.35, 'cilia': 'True', 'phase': 0.0},
    ACTIVE_N: {'r': 0.01, 'E': 5e5, 'rho': 1e3, 'nu': 0.35, 'cilia': 'True', 'phase': 3.14159},
}

def genome_to_vxa(genome, output_path, sim_time=1.0):
    """Write a .vxa XML file for VoxCraft-sim from genome array."""
    vxa = ET.Element("VXA", Version="1.1")
    
    simulator = ET.SubElement(vxa, "Simulator")
    ET.SubElement(simulator, "Integration", StopTime=str(sim_time))
    
    environment = ET.SubElement(vxa, "Environment")
    gravity = ET.SubElement(environment, "Gravity")
    ET.SubElement(gravity, "Z").text = "-9.81"
    
    vxc = ET.SubElement(vxa, "VXC", Version="0.94")
    
    lattice = ET.SubElement(vxc, "Lattice")
    ET.SubElement(lattice, "Lattice_Dim").text = "0.01"
    ET.SubElement(lattice, "X_Dim_Adj").text = "1"
    ET.SubElement(lattice, "Y_Dim_Adj").text = "1"
    ET.SubElement(lattice, "Z_Dim_Adj").text = "1"
    ET.SubElement(lattice, "X_Line_Offset").text = "0"
    ET.SubElement(lattice, "Y_Line_Offset").text = "0"
    ET.SubElement(lattice, "X_Layer_Offset").text = "0"
    ET.SubElement(lattice, "Y_Layer_Offset").text = "0"
    
    palette = ET.SubElement(vxc, "Palette")
    for mat_id, props in MATERIAL_MAP.items():
        mat = ET.SubElement(palette, "Material", ID=str(mat_id))
        ET.SubElement(mat, "MatType").text = "0"
        ET.SubElement(mat, "Name").text = f"Material_{mat_id}"
        display = ET.SubElement(mat, "Display")
        if mat_id == PASSIVE:
            ET.SubElement(display, "Red").text = "0"
            ET.SubElement(display, "Green").text = "1"
            ET.SubElement(display, "Blue").text = "1"
        elif mat_id == ACTIVE_P:
            ET.SubElement(display, "Red").text = "1"
            ET.SubElement(display, "Green").text = "0"
            ET.SubElement(display, "Blue").text = "0"
        elif mat_id == ACTIVE_N:
            ET.SubElement(display, "Red").text = "0"
            ET.SubElement(display, "Green").text = "1"
            ET.SubElement(display, "Blue").text = "0"
        mechanical = ET.SubElement(mat, "Mechanical")
        for key, value in props.items():
            if key == 'cilia':
                ET.SubElement(mechanical, "Cilia").text = str(value).lower()
            elif key == 'phase':
                ET.SubElement(mechanical, "Phase").text = str(value)
            elif key == 'rho':
                ET.SubElement(mechanical, "Density").text = str(value)
            elif key == 'nu':
                ET.SubElement(mechanical, "Poisson").text = str(value)
            elif key == 'E':
                ET.SubElement(mechanical, "Elastic_Mod").text = str(value)
            elif key == 'r':
                ET.SubElement(mechanical, "Damping_Multiplier").text = str(value)

    structure = ET.SubElement(vxc, "Structure", Compression="ASCII_HIERARCHICAL")
    ET.SubElement(structure, "X_Voxels").text = str(genome.shape[0])
    ET.SubElement(structure, "Y_Voxels").text = str(genome.shape[1])
    ET.SubElement(structure, "Z_Voxels").text = str(genome.shape[2])

    data = ET.SubElement(structure, "Data")
    # VoxCraft expects Z layers separated by CDATA and Y rows separated by newlines
    data_text = ""
    for z in range(genome.shape[2]):
        layer = "<Layer><![CDATA["
        for y in range(genome.shape[1]):
            for x in range(genome.shape[0]):
                layer += str(genome[x, y, z])
        layer += "]]></Layer>"
        data_text += layer

    data.append(ET.fromstring(f"<Data>{data_text}</Data>")[0]) 
    
    # Actually, a better way to do Data is:
    data.clear()
    for z in range(genome.shape[2]):
        layer = ET.SubElement(data, "Layer")
        layer_text = ""
        for y in range(genome.shape[1]):
            for x in range(genome.shape[0]):
                layer_text += str(genome[x, y, z])
        layer.text = layer_text
    
    tree = ET.ElementTree(vxa)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def run_voxcraft(vxa_path, timeout=120):
    """Run voxcraft-sim and return parsed (dx, dy, dz) displacement."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [str(VOXCRAFT_BIN), '-i', str(vxa_path), '-o', tmpdir],
            capture_output=True, text=True, timeout=timeout
        )
        
        if result.returncode != 0:
            return 0.0, 0.0, 0.0
            
        # Parse displacement from VoxCraft output XML (history file)
        history_file = Path(tmpdir) / "history_0.xml"
        if not history_file.exists():
            for child in Path(tmpdir).iterdir():
                if child.name.endswith('.xml'):
                    history_file = child
                    break
        
        if not history_file.exists():
            return 0.0, 0.0, 0.0

        try:
            tree = ET.parse(history_file)
            root = tree.getroot()
            # voxcraft history output has <Record> elements. The last one will have <TargetCM>
            records = root.findall('.//Record')
            if not records:
                return 0.0, 0.0, 0.0
                
            first_cm = records[0].find('TargetCM')
            last_cm = records[-1].find('TargetCM')
            
            if first_cm is None or last_cm is None:
                return 0.0, 0.0, 0.0
                
            fx, fy, fz = float(first_cm.get('x')), float(first_cm.get('y')), float(first_cm.get('z'))
            lx, ly, lz = float(last_cm.get('x')), float(last_cm.get('y')), float(last_cm.get('z'))
            
            return lx - fx, ly - fy, lz - fz
            
        except Exception:
            return 0.0, 0.0, 0.0
