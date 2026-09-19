import glob
import json
import os

import magpylib as magpy
import numpy as np
from magpylib.current import Circle
from magpylib.magnet import Cuboid, Cylinder, Sphere, Tetrahedron, TriangularMesh
from magpylib.current import Polyline
from magpylib.misc import Dipole as MagpyDipole
from pymagba.currents import CircularCurrent
from pymagba.magnets import (
    CuboidMagnet,
    CylinderMagnet,
    Dipole,
    SourceCollection,
    SphereMagnet,
    TetrahedronMagnet,
    MeshMagnet,
)
from pymagba.currents import PathCurrent

from scipy.spatial.transform import Rotation


def get_observer_grid(n_points):
    n = round(n_points ** (1 / 3.0))
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
    m_py = CylinderMagnet(
        position=(0, 0, 0),
        orientation=rot,
        diameter=0.1,
        height=0.2,
        polarization=(1, 2, 3),
    )
    m_ma = Cylinder(
        position=(0, 0, 0),
        orientation=rot,
        dimension=(0.1, 0.2),
        polarization=(1, 2, 3),
    )
    acc["Cylinder"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Sphere
    m_py = SphereMagnet(
        position=(0, 0, 0), orientation=rot, diameter=0.1, polarization=(1, 2, 3)
    )
    m_ma = Sphere(
        position=(0, 0, 0), orientation=rot, diameter=0.1, polarization=(1, 2, 3)
    )
    acc["Sphere"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Cuboid
    m_py = CuboidMagnet(
        position=(0, 0, 0),
        orientation=rot,
        dimensions=(0.1, 0.2, 0.3),
        polarization=(1, 2, 3),
    )
    m_ma = Cuboid(
        position=(0, 0, 0),
        orientation=rot,
        dimension=(0.1, 0.2, 0.3),
        polarization=(1, 2, 3),
    )
    acc["Cuboid"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Dipole
    m_py = Dipole(position=(0, 0, 0), orientation=rot, moment=(1, 2, 3))
    m_ma = MagpyDipole(position=(0, 0, 0), orientation=rot, moment=(1, 2, 3))
    acc["Dipole"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Circular
    m_py = CircularCurrent(
        position=(0, 0, 0), orientation=rot, diameter=0.01, current=1.0
    )
    m_ma = Circle(position=(0, 0, 0), orientation=rot, diameter=0.01, current=1.0)
    acc["Circular"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Collection
    m1_py = CylinderMagnet(
        position=(0.005, 0, 0), diameter=0.01, height=0.02, polarization=(0, 0, 1)
    )
    m2_py = CuboidMagnet(
        position=(-0.005, 0, 0), dimensions=(0.01, 0.01, 0.01), polarization=(0, 0, -1)
    )
    m3_py = Dipole(position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0))
    col_py = SourceCollection([m1_py, m2_py, m3_py])

    m1_ma = Cylinder(
        position=(0.005, 0, 0), dimension=(0.01, 0.02), polarization=(0, 0, 1)
    )
    m2_ma = Cuboid(
        position=(-0.005, 0, 0), dimension=(0.01, 0.01, 0.01), polarization=(0, 0, -1)
    )
    m3_ma = MagpyDipole(position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0))
    col_ma = magpy.Collection(m1_ma, m2_ma, m3_ma)
    acc["Collection"] = relative_error(
        col_py.compute_B(observers),
        col_ma.getB(observers),  # type: ignore
    )

    # Tetrahedron
    m_py = TetrahedronMagnet(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        polarization=(1, 2, 3),
    )
    m_ma = Tetrahedron(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        polarization=(1, 2, 3),
    )
    acc["Tetrahedron"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Mesh
    m_py = MeshMagnet(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        faces=[[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]],
        polarization=(1, 2, 3),
    )
    m_ma = TriangularMesh(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        faces=[[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]],
        polarization=(1, 2, 3),
    )
    acc["Mesh"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    # Polyline
    m_py = PathCurrent(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        current=1.5,
    )
    m_ma = Polyline(
        position=(0, 0, 0),
        orientation=rot,
        vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
        current=1.5,
    )
    acc["Polyline"] = relative_error(m_py.compute_B(observers), m_ma.getB(observers))  # type: ignore

    return acc


def main():
    results_dir = ".asv/results"
    json_files = glob.glob(os.path.join(results_dir, "*", "*.json"))
    json_files = [f for f in json_files if "machine.json" not in f]

    speedups = {}
    env = {}
    if json_files:
        latest_file = max(json_files, key=os.path.getmtime)
        with open(latest_file, "r") as f:
            data = json.load(f)

        params = data.get("params", {})
        try:
            import math

            # asv stores ram in KB. OS often reserves ~0.5-1GB for iGPU/hardware,
            # so ceil() brings it back to the physical RAM size (e.g. 15.03 -> 16)
            ram_gb = math.ceil(int(params.get("ram", "0")) / 1024 / 1024)
        except ValueError:
            ram_gb = "Unknown"
        env = {
            "os": params.get("os", "Unknown"),
            "cpu": f"{params.get('cpu', 'Unknown')} ({params.get('num_cpu', '?')} cores)",
            "ram": f"{ram_gb} GB",
            "python": params.get("python", "Unknown"),
        }

        results = data.get("results", {})
        for name, val in results.items():
            if not isinstance(val, list) or not val:
                continue
            res = val[0]
            if not res:
                continue

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
            if "ObjectCreation" in name and len(res) == 6:
                speedups["Create Cuboid"] = {"py": res[0], "ma": res[3]}
                speedups["Create Cylinder"] = {"py": res[1], "ma": res[4]}
                speedups["Create Collection"] = {"py": res[2], "ma": res[5]}
            elif "ObjectCreation" in name and len(res) == 4:
                # Fallback for old json data
                speedups["Create Cuboid"] = {"py": res[0], "ma": res[2]}
                speedups["Create Cylinder"] = {"py": res[1], "ma": res[3]}

            # Object Manipulation
            if "ObjectManipulation" in name and len(res) == 4:
                speedups["Translate"] = {"py": res[0], "ma": res[2]}
                speedups["Rotate"] = {"py": res[1], "ma": res[3]}

    accuracy = calc_accuracy()

    import jinja2
    import pymagba
    import magpylib

    pymagba_version = getattr(pymagba, "__version__", "Unknown")
    magpylib_version = getattr(magpylib, "__version__", "Unknown")

    with open("PERFORMANCE.md.j2", "r") as f:
        template = jinja2.Template(f.read())

    field_rows = []
    for geom in [
        "Cylinder",
        "Sphere",
        "Cuboid",
        "Dipole",
        "Tetrahedron",
        "Mesh",
        "Circular",
        "Polyline",
    ]:
        sp = speedups.get(geom, {})
        acc = accuracy.get(geom)
        field_rows.append(
            {
                "geom": geom,
                "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "speed": f"{sp['ma'] / sp['py']:.1f}x"
                if sp and sp.get("py")
                else "*TBD*",
                "max_e": f"{acc[0]:.2e}" if acc else "*TBD*",
                "p95_e": f"{acc[1]:.2e}" if acc else "*TBD*",
            }
        )

    collection_rows = []
    for geom in ["Collection"]:
        sp = speedups.get(geom, {})
        acc = accuracy.get(geom)
        collection_rows.append(
            {
                "geom": geom,
                "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "speed": f"{sp['ma'] / sp['py']:.1f}x"
                if sp and sp.get("py")
                else "*TBD*",
                "max_e": f"{acc[0]:.2e}" if acc else "*TBD*",
                "p95_e": f"{acc[1]:.2e}" if acc else "*TBD*",
            }
        )

    create_rows = []
    for op, label in [
        ("Create Cuboid", "Cuboid"),
        ("Create Cylinder", "Cylinder"),
        ("Create Collection", "Collection"),
    ]:
        sp = speedups.get(op, {})
        create_rows.append(
            {
                "label": label,
                "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "speed": f"{sp['ma'] / sp['py']:.1f}x"
                if sp and sp.get("py")
                else "*TBD*",
            }
        )

    man_rows = []
    for op, label in [("Translate", "Translate"), ("Rotate", "Rotate")]:
        sp = speedups.get(op, {})
        man_rows.append(
            {
                "label": label,
                "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
                "speed": f"{sp['ma'] / sp['py']:.1f}x"
                if sp and sp.get("py")
                else "*TBD*",
            }
        )

    content = template.render(
        field_rows=field_rows,
        collection_rows=collection_rows,
        create_rows=create_rows,
        man_rows=man_rows,
        env=env,
        pymagba_version=pymagba_version,
        magpylib_version=magpylib_version,
    )

    with open("PERFORMANCE.md", "w") as f:
        f.write(content)

    print("Updated PERFORMANCE.md")


if __name__ == "__main__":
    main()
