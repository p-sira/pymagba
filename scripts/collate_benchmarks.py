import glob
import json
import os

import numpy as np
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
    import inspect
    import sys
    import warnings

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    from benchmarks.comparison import currents as bench_currents
    from benchmarks.comparison import magnets as bench_magnets

    observers = get_observer_grid(100000)
    acc = {}

    modules = [bench_magnets, bench_currents]

    for mod in modules:
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if not name.startswith(("Magnet", "Current", "Composite")):
                continue

            geom_name = name
            for prefix in ["Magnet", "Current", "Composite"]:
                if name.startswith(prefix):
                    geom_name = name[len(prefix) :]
                    break

            try:
                obj_py = cls()
                obj_py.setup("PyMagba")
                func_py = obj_py.func

                obj_ma = cls()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    obj_ma.setup("MagpyLib")
                func_ma = obj_ma.func

                B_py = func_py(observers)
                B_ma = func_ma(observers)
                acc[geom_name] = relative_error(B_py, B_ma)
            except Exception as e:  # noqa: BLE001
                print(f"Skipping {geom_name}: {e}")

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
                # name is like comparison.magnets.MagnetCuboid.time_compute_B
                class_name = name.split(".")[-2]
                geom = class_name.removeprefix("Magnet")
                if len(res) >= 2 and res[0] and res[1]:
                    speedups[geom] = {"py": res[0], "ma": res[1]}
            elif "Current" in name and "time_compute_B" in name:
                # name is like comparison.currents.CurrentPolyline.time_compute_B
                class_name = name.split(".")[-2]
                geom = class_name.removeprefix("Current")
                if len(res) >= 2 and res[0] and res[1]:
                    speedups[geom] = {"py": res[0], "ma": res[1]}

            # Object Creation
            if "ObjectCreation" in name and len(res) == 4:
                speedups["Create Cylinder"] = {"py": res[0], "ma": res[2]}
                speedups["Create Collection"] = {"py": res[1], "ma": res[3]}
            elif "ObjectCreation" in name and len(res) == 8:
                # Fallback
                speedups["Create Cylinder"] = {"py": res[1], "ma": res[5]}
                speedups["Create Collection"] = {"py": res[3], "ma": res[7]}

            # Object Manipulation
            if "ObjectManipulation" in name and len(res) == 8:
                speedups["Translate Cylinder"] = {"py": res[0], "ma": res[4]}
                speedups["Rotate Cylinder"] = {"py": res[1], "ma": res[5]}
                speedups["Translate Collection"] = {"py": res[2], "ma": res[6]}
                speedups["Rotate Collection"] = {"py": res[3], "ma": res[7]}
            elif "ObjectManipulation" in name and len(res) == 16:
                # Fallback for old
                speedups["Translate Cylinder"] = {"py": res[2], "ma": res[10]}
                speedups["Rotate Cylinder"] = {"py": res[3], "ma": res[11]}
                speedups["Translate Collection"] = {"py": res[6], "ma": res[14]}
                speedups["Rotate Collection"] = {"py": res[7], "ma": res[15]}

    accuracy = calc_accuracy()

    import jinja2
    import magpylib
    import pymagba

    pymagba_version = getattr(pymagba, "__version__", "Unknown")
    magpylib_version = getattr(magpylib, "__version__", "Unknown")

    with open("PERFORMANCE.md.j2", "r") as f:
        template = jinja2.Template(f.read())

    magnet_rows = []
    current_rows = []
    composite_rows = []

    def format_row(geom, dict_speedups, dict_acc):
        sp = dict_speedups.get(geom, {})
        acc_data = dict_acc.get(geom)
        return {
            "geom": geom,
            "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "speed": f"{sp['ma'] / sp['py']:.1f}x" if sp and sp.get("py") else "*TBD*",
            "max_e": f"{acc_data[0]:.2e}" if acc_data else "*TBD*",
            "p95_e": f"{acc_data[1]:.2e}" if acc_data else "*TBD*",
        }

    for geom in [
        "Cylinder",
        "Sphere",
        "Cuboid",
        "Dipole",
        "Tetrahedron",
        "Mesh",
        "Triangle",
    ]:
        magnet_rows.append(format_row(geom, speedups, accuracy))

    for geom in ["Circular", "Polyline", "TriangleCurrent", "SheetCurrent"]:
        current_rows.append(format_row(geom, speedups, accuracy))

    for geom in ["Collection"]:
        composite_rows.append(format_row(geom, speedups, accuracy))

    create_rows = []
    for op, label in [
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
    for op, label in [
        ("Translate Cylinder", "Translate Cylinder"),
        ("Rotate Cylinder", "Rotate Cylinder"),
        ("Translate Collection", "Translate Collection"),
        ("Rotate Collection", "Rotate Collection"),
    ]:
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
        magnet_rows=magnet_rows,
        current_rows=current_rows,
        composite_rows=composite_rows,
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
