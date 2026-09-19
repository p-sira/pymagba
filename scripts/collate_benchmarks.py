import os
import glob
import json
import numpy as np
import pymagba
from pymagba.magnets import CylinderMagnet, SphereMagnet, CuboidMagnet, Dipole
from pymagba.currents import CircularCurrent
from magpylib.magnet import Cylinder, Sphere, Cuboid
from magpylib.misc import Dipole as MagpyDipole
import magpylib as magpy
from magpylib.current import Circle
from scipy.spatial.transform import Rotation
import re

def get_observer_grid(n_points):
    n = int(round(n_points ** (1 / 3.0)))
    x = np.linspace(-1.0, 1.0, n)
    y = np.linspace(-1.0, 1.0, n)
    z = np.linspace(-1.0, 1.0, n)
    X, Y, Z = np.meshgrid(x, y, z)
    return np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))

def get_standard_rotation():
    return Rotation.from_euler("xyz", [10, 20, 30], degrees=True)

def relative_error(B_pymagba, B_magpylib):
    diff = np.linalg.norm(B_pymagba - B_magpylib, axis=1)
    mag = np.linalg.norm(B_magpylib, axis=1)
    mask = mag > 1e-15
    rel_err = np.zeros_like(mag)
    rel_err[mask] = diff[mask] / mag[mask]
    if len(rel_err) == 0:
        return 0.0, 0.0
    return np.max(rel_err), np.percentile(rel_err, 95)

def calc_accuracy():
    observers = get_observer_grid(100000)
    rot = get_standard_rotation()
    acc = {}

    # Cylinder
    m_py = CylinderMagnet(position=(0,0,0), orientation=rot, diameter=0.1, height=0.2, polarization=(1,2,3))
    m_ma = Cylinder(position=(0,0,0), orientation=rot, dimension=(0.1, 0.2), polarization=(1,2,3))
    acc["Cylinder"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))

    # Sphere
    m_py = SphereMagnet(position=(0,0,0), orientation=rot, diameter=0.1, polarization=(1,2,3))
    m_ma = Sphere(position=(0,0,0), orientation=rot, diameter=0.1, polarization=(1,2,3))
    acc["Sphere"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))

    # Cuboid
    m_py = CuboidMagnet(position=(0,0,0), orientation=rot, dimensions=(0.1,0.2,0.3), polarization=(1,2,3))
    m_ma = Cuboid(position=(0,0,0), orientation=rot, dimension=(0.1,0.2,0.3), polarization=(1,2,3))
    acc["Cuboid"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))

    # Dipole
    m_py = Dipole(position=(0,0,0), orientation=rot, moment=(1,2,3))
    m_ma = MagpyDipole(position=(0,0,0), orientation=rot, moment=(1,2,3))
    acc["Dipole"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))

    # Circular
    m_py = CircularCurrent(position=(0,0,0), orientation=rot, diameter=0.01, current=1.0)
    m_ma = Circle(position=(0,0,0), orientation=rot, diameter=0.01, current=1.0)
    acc["Circular"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))

    # Collection
    m1_py = CylinderMagnet(position=(0.005,0,0), diameter=0.01, height=0.02, polarization=(0,0,1))
    m2_py = CuboidMagnet(position=(-0.005,0,0), dimensions=(0.01,0.01,0.01), polarization=(0,0,-1))
    col_py = pymagba.magnets.SourceCollection([m1_py, m2_py])
    
    m1_ma = Cylinder(position=(0.005,0,0), dimension=(0.01, 0.02), polarization=(0,0,1))
    m2_ma = Cuboid(position=(-0.005,0,0), dimension=(0.01,0.01,0.01), polarization=(0,0,-1))
    col_ma = magpy.Collection(m1_ma, m2_ma)
    acc["Collection"] = relative_error(col_py.compute_B(observers), col_ma.getB(observers))

    return acc

def main():
    results_dir = ".asv/results"
    json_files = glob.glob(os.path.join(results_dir, "*", "*.json"))
    json_files = [f for f in json_files if "machine.json" not in f]
    
    speedups = {}
    if json_files:
        latest_file = max(json_files, key=os.path.getmtime)
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        results = data.get("results", {})
        for name, val in results.items():
            res = val.get("result", [])
            if not res: continue
            
            # Pure fields
            if "Field" in name and "time_field" in name:
                geom = name.split("Field")[1].split(".")[0]
                if len(res) >= 2 and res[0] and res[1]:
                    speedups[geom] = {"py": res[0], "ma": res[1]}
            elif "Magnet" in name and "time_compute_B" in name:
                geom = name.split("Magnet")[1].split(".")[0]
                if len(res) >= 2 and res[0] and res[1]:
                    speedups[geom] = {"py": res[0], "ma": res[1]}
            
            # Object Creation
            if "ObjectCreation" in name:
                if len(res) == 4:
                    speedups["Create Cuboid"] = {"py": res[0], "ma": res[1]}
                    speedups["Create Cylinder"] = {"py": res[2], "ma": res[3]}
                    
            # Object Manipulation
            if "ObjectManipulation" in name:
                if len(res) == 4:
                    speedups["Translate"] = {"py": res[0], "ma": res[1]}
                    speedups["Rotate"] = {"py": res[2], "ma": res[3]}
                    
    accuracy = calc_accuracy()

    with open("PERFORMANCE.md", "r") as f:
        content = f.read()

    # Rewrite Field table
    field_lines = ["| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |",
                   "|---------------|--------------|---------------|---------|----------------|----------------|"]
    for geom in ["Cylinder", "Sphere", "Cuboid", "Dipole", "Circular", "Collection"]:
        sp = speedups.get(geom, {})
        py_t = f"{sp.get('py', 0)*1000:.2f} ms" if sp else "*TBD*"
        ma_t = f"{sp.get('ma', 0)*1000:.2f} ms" if sp else "*TBD*"
        speed = f"{sp['ma']/sp['py']:.1f}x" if sp and sp.get('py') else "*TBD*"
        
        acc = accuracy.get(geom)
        max_e = f"{acc[0]:.2e}" if acc else "*TBD*"
        p95_e = f"{acc[1]:.2e}" if acc else "*TBD*"
        
        field_lines.append(f"| **{geom}** | {py_t} | {ma_t} | {speed} | {max_e} | {p95_e} |")
    
    content = re.sub(r"\| Geometry Type \|.*?(?=\n\n|\n\*|$)", "\n".join(field_lines), content, flags=re.DOTALL)
    
    # Rewrite Creation table
    create_lines = ["| Operation | PyMagba Time | Magpylib Time | Speedup |",
                    "|-----------|--------------|---------------|---------|"]
    for op, label in [("Create Cuboid", "Instantiate 10,000 Cuboids"), ("Create Cylinder", "Instantiate 10,000 Cylinders")]:
        sp = speedups.get(op, {})
        py_t = f"{sp.get('py', 0)*1000:.2f} ms" if sp else "*TBD*"
        ma_t = f"{sp.get('ma', 0)*1000:.2f} ms" if sp else "*TBD*"
        speed = f"{sp['ma']/sp['py']:.1f}x" if sp and sp.get('py') else "*TBD*"
        create_lines.append(f"| {label} | {py_t} | {ma_t} | {speed} |")
        
    content = re.sub(r"\| Operation \|.*?10,000 Cylinders.*?(?=\n\n|$)", "\n".join(create_lines), content, flags=re.DOTALL)
    
    # Rewrite Manipulation table
    man_lines = ["| Operation | PyMagba Time | Magpylib Time | Speedup |",
                 "|-----------|--------------|---------------|---------|"]
    for op, label in [("Translate", "Translate (10,000 operations)"), ("Rotate", "Rotate (10,000 operations)")]:
        sp = speedups.get(op, {})
        py_t = f"{sp.get('py', 0)*1000:.2f} ms" if sp else "*TBD*"
        ma_t = f"{sp.get('ma', 0)*1000:.2f} ms" if sp else "*TBD*"
        speed = f"{sp['ma']/sp['py']:.1f}x" if sp and sp.get('py') else "*TBD*"
        man_lines.append(f"| {label} | {py_t} | {ma_t} | {speed} |")
        
    content = re.sub(r"\| Operation \|.*?Rotate \(10,000 operations\).*?(?=\n\n|$)", "\n".join(man_lines), content, flags=re.DOTALL)

    with open("PERFORMANCE.md", "w") as f:
        f.write(content)
        
    print("Updated PERFORMANCE.md")

if __name__ == "__main__":
    main()
