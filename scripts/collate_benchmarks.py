import glob
import inspect
import itertools
import json
import math
import os
import subprocess
import sys
import warnings

import jinja2
import magpylib
import numpy as np
import pymagba


def get_observer_grid(n_points: int) -> np.ndarray:
    n = round(n_points ** (1 / 3.0))
    x = np.linspace(-1.0, 1.0, n)
    y = np.linspace(-1.0, 1.0, n)
    z = np.linspace(-1.0, 1.0, n)
    X, Y, Z = np.meshgrid(x, y, z)
    return np.column_stack((X.ravel(), Y.ravel(), Z.ravel()))


def relative_error(
    B_pymagba: np.ndarray, B_magpylib: np.ndarray
) -> tuple[float, float]:
    diff = np.linalg.norm(B_pymagba - B_magpylib, axis=1)
    mag = np.linalg.norm(B_magpylib, axis=1)
    mask = mag > 1e-15
    rel_err = np.zeros_like(mag)
    rel_err[mask] = diff[mask] / mag[mask]
    if len(rel_err) == 0:
        return 0.0, 0.0
    return float(np.max(rel_err)), float(np.percentile(rel_err, 95))


def calc_accuracy() -> dict[str, tuple[float, float]]:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from benchmarks.comparison import currents as bench_currents
    from benchmarks.comparison import magnets as bench_magnets

    observers = get_observer_grid(100000)
    acc: dict[str, tuple[float, float]] = {}

    for mod in (bench_magnets, bench_currents):
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if not name.startswith(("Magnet", "Current", "Composite")):
                continue

            geom_name = name
            for prefix in ("Magnet", "Current", "Composite"):
                if name.startswith(prefix):
                    geom_name = name.removeprefix(prefix)
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


def parse_asv_results(results: dict) -> dict[str, dict[str, float]]:
    """Dynamically parse comparison benchmarks using ASV's parameter grid metadata."""
    speedups: dict[str, dict[str, float]] = {}

    for name, val in results.items():
        if not name.startswith("comparison.") or not isinstance(val, list) or not val:
            continue
        timings = val[0]
        param_grid = val[1]
        if not timings or not param_grid:
            continue

        # ASV stores param_grid as a list of lists of strings, e.g. [["'PyMagba'", "'MagpyLib'"], ...]
        params = [[p.strip("'\"") for p in level] for level in param_grid]
        if not params or params[0] != ["PyMagba", "MagpyLib"]:
            continue

        # Map each parameter combination in the Cartesian product to its timing
        for param_tuple, timing in zip(itertools.product(*params), timings):
            lib = param_tuple[0]  # "PyMagba" or "MagpyLib"
            lib_key = "py" if lib == "PyMagba" else "ma"
            rest = param_tuple[1:]

            if "comparison.operations.ObjectCreation" in name:
                geom = rest[0]
                key = f"Create {geom}"
            elif "comparison.operations.ObjectManipulation" in name:
                geom, op = rest[0], rest[1]
                key = f"{op} {geom}"
            elif "comparison.operations.SmallBatchComputation" in name:
                geom, n_pts = rest[0], rest[1]
                unit = "point" if n_pts == "1" else "points"
                key = f"{geom} ({n_pts} {unit})"
            elif "comparison.fields." in name:
                key = name.split("Field")[1].split(".")[0]
            elif "comparison.magnets." in name or "comparison.currents." in name:
                class_name = name.split(".")[-2]
                key = class_name.removeprefix("Magnet").removeprefix("Current")
            else:
                continue

            speedups.setdefault(key, {})[lib_key] = timing

    return speedups


def extract_environment(params: dict) -> dict[str, str]:
    try:
        # asv stores ram in KB. Ceil brings it back to physical RAM size (e.g. 15.03 -> 16 GB)
        ram_gb = f"{math.ceil(int(params.get('ram', '0')) / 1024 / 1024)} GB"
    except ValueError:
        ram_gb = "Unknown"

    return {
        "os": params.get("os", "Unknown"),
        "cpu": f"{params.get('cpu', 'Unknown')} ({params.get('num_cpu', '?')} cores)",
        "ram": ram_gb,
        "python": params.get("python", "Unknown"),
    }


def find_target_file(target_files: list[str]) -> str | None:
    if not target_files:
        return None

    # 1. Allow explicit CLI argument (file path or commit prefix)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            return arg
        for f in target_files:
            if os.path.basename(f).startswith(arg):
                return f

    # 2. Match current git HEAD commit
    try:
        head_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
        head_short = head_commit[:8]
        for f in target_files:
            if os.path.basename(f).startswith(head_short):
                return f
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 3. Fallback: select by commit date inside JSON metadata rather than filesystem mtime
    def get_commit_date(filepath: str) -> int:
        try:
            with open(filepath, "r") as f:
                return json.load(f).get("date", 0)
        except (json.JSONDecodeError, OSError):
            return 0

    return max(target_files, key=get_commit_date)


def main():
    results_dir = ".asv/results"
    json_files = glob.glob(os.path.join(results_dir, "*", "*.json"))
    json_files = [f for f in json_files if "machine.json" not in f]

    # Prefer local machine results over CI runner results if available
    local_files = [f for f in json_files if "github-runner" not in f]
    target_files = local_files if local_files else json_files

    speedups: dict[str, dict[str, float]] = {}
    env: dict[str, str] = {}

    target_file = find_target_file(target_files)
    if target_file:
        print(f"Collating benchmarks from: {target_file}")
        with open(target_file, "r") as f:
            data = json.load(f)

        env = extract_environment(data.get("params", {}))
        speedups = parse_asv_results(data.get("results", {}))

    accuracy = calc_accuracy()

    pymagba_version = getattr(pymagba, "__version__", "Unknown")
    magpylib_version = getattr(magpylib, "__version__", "Unknown")

    with open("PERFORMANCE.md.j2", "r") as f:
        template = jinja2.Template(f.read())

    def format_geom_row(geom: str) -> dict[str, str]:
        sp = speedups.get(geom, {})
        acc_data = accuracy.get(geom)
        return {
            "geom": geom,
            "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "speed": f"{sp['ma'] / sp['py']:.1f}x" if sp and sp.get("py") else "*TBD*",
            "max_e": f"{acc_data[0]:.2e}" if acc_data else "*TBD*",
            "p95_e": f"{acc_data[1]:.2e}" if acc_data else "*TBD*",
        }

    def format_op_row(key: str, label: str | None = None) -> dict[str, str]:
        sp = speedups.get(key, {})
        return {
            "label": label or key,
            "py_t": f"{sp.get('py', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "ma_t": f"{sp.get('ma', 0) * 1000:.2f} ms" if sp else "*TBD*",
            "speed": f"{sp['ma'] / sp['py']:.1f}x" if sp and sp.get("py") else "*TBD*",
        }

    magnet_rows = [
        format_geom_row(geom)
        for geom in [
            "Cylinder",
            "Sphere",
            "Cuboid",
            "Dipole",
            "Tetrahedron",
            "Mesh",
            "Triangle",
        ]
    ]

    current_rows = [
        format_geom_row(geom)
        for geom in ["Circular", "Polyline", "TriangleCurrent", "SheetCurrent"]
    ]

    composite_rows = [format_geom_row("Collection")]

    create_rows = [
        format_op_row("Create Cylinder", "Cylinder"),
        format_op_row("Create Collection", "Collection"),
    ]

    man_rows = [
        format_op_row("Translate Cylinder"),
        format_op_row("Rotate Cylinder"),
        format_op_row("Translate Collection"),
        format_op_row("Rotate Collection"),
    ]

    small_batch_rows = [
        format_op_row(f"{geom} ({pts} point{'s' if pts != 1 else ''})")
        for geom in ["Cylinder", "Cuboid", "Dipole", "Collection"]
        for pts in [1, 10]
    ]

    content = template.render(
        magnet_rows=magnet_rows,
        current_rows=current_rows,
        composite_rows=composite_rows,
        create_rows=create_rows,
        man_rows=man_rows,
        small_batch_rows=small_batch_rows,
        env=env,
        pymagba_version=pymagba_version,
        magpylib_version=magpylib_version,
    )

    with open("PERFORMANCE.md", "w") as f:
        f.write(content)

    print("Updated PERFORMANCE.md")


if __name__ == "__main__":
    main()
