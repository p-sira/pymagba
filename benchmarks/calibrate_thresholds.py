#!/usr/bin/env python3
# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Calibrate Magba Rayon and PyMagba GIL-detachment thresholds.

Build the extension first with:

    uv run maturin develop --release --features threshold-calibration

The controller launches one isolated worker per execution policy and writes raw
samples, summaries, candidate crossovers, and build provenance to JSON.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
import zlib
from pathlib import Path
from typing import Any

ALL_CASES = (
    "cylinder",
    "dipole",
    "cuboid",
    "sphere",
    "circular",
    "triangle",
    "tetrahedron",
    "mesh",
    "path",
    "triangle_current",
    "sheet",
)
ALL_SENSOR_CASES = (
    "linear_read",
    "linear_voltage",
    "linear_perp",
    "switch_read",
    "switch_state",
    "latch_read",
    "latch_state",
    "observer_mixed",
)
ALL_SENSOR_SOURCES = ("dipole", "path", "sheet", "collection")
VARIABLE_CASES = frozenset(("mesh", "path", "sheet"))
VARIABLE_SENSOR_SOURCES = frozenset(("path", "sheet", "collection"))
DEFAULT_SIZES = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
DEFAULT_POLICIES = (
    "serial:detach",
    "parallel:detach",
    "auto:retain",
    "auto:detach",
    "auto:auto",
)


def csv_values(value: str, convert: Any = str) -> list[Any]:
    return [convert(item.strip()) for item in value.split(",") if item.strip()]


def git_value(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ("git", "-C", str(root), *args),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def command_value(*args: str) -> str | None:
    try:
        return subprocess.run(
            args, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def controller_provenance(root: Path) -> dict[str, Any]:
    status = git_value(root, "status", "--porcelain")
    magba = root / "vendor" / "magba"
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "executable": sys.executable,
        "cpu_count": os.cpu_count(),
        "rayon_num_threads": os.environ.get("RAYON_NUM_THREADS"),
        "rustc": command_value("rustc", "--version", "--verbose"),
        "pymagba_revision": git_value(root, "rev-parse", "HEAD"),
        "pymagba_dirty": bool(status),
        "magba_revision": git_value(magba, "rev-parse", "HEAD"),
        "command": [sys.executable, *sys.argv],
    }


def build_tasks(args: argparse.Namespace) -> list[dict[str, Any]]:
    tasks = []
    for case in args.cases:
        complexities = args.complexities if case in VARIABLE_CASES else [1]
        for api in args.apis:
            for complexity in complexities:
                for size in args.sizes:
                    tasks.append(
                        {
                            "family": "field",
                            "case": case,
                            "api": api,
                            "source": None,
                            "complexity": complexity,
                            "size": size,
                        }
                    )
    for case in args.sensor_cases:
        sizes = args.sensor_counts if case == "observer_mixed" else [1]
        for source in args.sensor_sources:
            complexities = (
                args.complexities if source in VARIABLE_SENSOR_SOURCES else [1]
            )
            for complexity in complexities:
                for size in sizes:
                    tasks.append(
                        {
                            "family": "sensor",
                            "case": case,
                            "api": "sensor",
                            "source": source,
                            "complexity": complexity,
                            "size": size,
                        }
                    )
    return tasks


def run_worker(
    policy: str, tasks: list[dict[str, Any]], args: argparse.Namespace
) -> dict[str, Any]:
    rust_mode, gil_mode = policy.split(":", 1)
    request = {
        "policy": {"rust_mode": rust_mode, "gil_mode": gil_mode},
        "tasks": tasks,
        "repeats": args.repeats,
        "warmups": args.warmups,
        "target_sample_ms": args.target_sample_ms,
        "max_loops": args.max_loops,
    }
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"worker {policy} failed with exit code {completed.returncode}:\n"
            f"{completed.stderr}"
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"worker {policy} returned invalid JSON:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        ) from exc


def summarize(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for result in results:
        samples = result["samples_ns_per_call"]
        individual_sensor = (
            result["family"] == "sensor" and result["case"] != "observer_mixed"
        )
        summaries.append(
            {
                "family": result["family"],
                "case": result["case"],
                "api": result["api"],
                "source": result["source"],
                "complexity": result["complexity"],
                "size": result["size"],
                "work_axis": "source_complexity"
                if individual_sensor
                else ("sensor_count" if result["family"] == "sensor" else "points"),
                "work_size": result["complexity"]
                if individual_sensor
                else result["size"],
                "policy": result["policy"],
                "median_ns": statistics.median(samples),
                "min_ns": min(samples),
                "max_ns": max(samples),
                "samples_ns": samples,
                "loops": result["loops"],
            }
        )
    return summaries


def find_crossover(
    summaries: list[dict[str, Any]],
    left_policy: str,
    right_policy: str,
    advantage: float = 0.05,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], dict[int, dict[str, dict[str, Any]]]] = {}
    for row in summaries:
        fixed_complexity = (
            None if row["work_axis"] == "source_complexity" else row["complexity"]
        )
        group = (
            row["family"],
            row["case"],
            row["api"],
            row["source"],
            fixed_complexity,
            row["work_axis"],
        )
        grouped.setdefault(group, {}).setdefault(row["work_size"], {})[
            row["policy"]
        ] = row

    candidates = []
    for group, by_size in sorted(grouped.items()):
        comparable = []
        for size, policies in sorted(by_size.items()):
            if left_policy not in policies or right_policy not in policies:
                continue
            left = policies[left_policy]["median_ns"]
            right = policies[right_policy]["median_ns"]
            pairs = zip(
                policies[left_policy]["samples_ns"],
                policies[right_policy]["samples_ns"],
            )
            wins = [
                right_sample <= left_sample * (1.0 - advantage)
                for left_sample, right_sample in pairs
            ]
            win_fraction = sum(wins) / len(wins)
            qualifies = right <= left * (1.0 - advantage) and win_fraction >= 2.0 / 3.0
            comparable.append((size, qualifies, left, right, win_fraction))

        crossover = None
        for current, following in itertools.pairwise(comparable):
            if current[1] and following[1]:
                crossover = current[0]
                break

        if crossover is not None:
            status = "crossover"
        elif comparable and any(item[1] for item in comparable):
            status = "inconclusive"
        else:
            status = "no_crossover"
        candidates.append(
            {
                "family": group[0],
                "case": group[1],
                "api": group[2],
                "source": group[3],
                "complexity": group[4],
                "work_axis": group[5],
                "left_policy": left_policy,
                "right_policy": right_policy,
                "required_advantage": advantage,
                "status": status,
                "candidate_work_size": crossover,
                "evidence": [
                    {
                        "work_size": item[0],
                        "left_median_ns": item[2],
                        "right_median_ns": item[3],
                        "right_win_fraction": item[4],
                    }
                    for item in comparable
                ],
            }
        )
    return candidates


def run_controller(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[1]
    tasks = build_tasks(args)
    policies = list(args.policies)
    random.Random(args.order_seed).shuffle(policies)

    workers = []
    all_results = []
    for index, policy in enumerate(policies, 1):
        print(f"[{index}/{len(policies)}] running isolated policy {policy}", flush=True)
        policy_tasks = [
            task
            for task in tasks
            if task["family"] == "field" or policy.startswith("auto:")
        ]
        worker = run_worker(policy, policy_tasks, args)
        workers.append(worker["provenance"])
        all_results.extend(worker["results"])

    summaries = summarize(all_results)
    candidates = {
        "rayon": find_crossover(summaries, "serial:detach", "parallel:detach"),
        "gil": find_crossover(summaries, "auto:retain", "auto:detach"),
    }
    report = {
        "schema_version": 1,
        "created_unix_ns": time.time_ns(),
        "provenance": controller_provenance(root),
        "configuration": {
            "cases": args.cases,
            "sensor_cases": args.sensor_cases,
            "sensor_sources": args.sensor_sources,
            "sensor_counts": args.sensor_counts,
            "apis": args.apis,
            "sizes": args.sizes,
            "complexities": args.complexities,
            "policies": policies,
            "repeats": args.repeats,
            "warmups": args.warmups,
            "target_sample_ms": args.target_sample_ms,
            "max_loops": args.max_loops,
            "order_seed": args.order_seed,
        },
        "workers": workers,
        "results": all_results,
        "summaries": summaries,
        "candidates": candidates,
    }

    args.results_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    destination = args.results_dir / f"ffi-threshold-{stamp}.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {destination}")
    return 0


def mesh_fixture(complexity: int) -> tuple[Any, Any]:
    import numpy as np

    vertices = []
    faces = []
    for index in range(complexity):
        x = (index % 16) * 0.0015
        y = (index // 16) * 0.0015
        base = len(vertices)
        vertices.extend(
            (
                (x, y, 0.0),
                (x + 0.0008, y, 0.0),
                (x, y + 0.0008, 0.0),
                (x, y, 0.0008),
            )
        )
        faces.extend(
            (
                (base, base + 2, base + 1),
                (base, base + 1, base + 3),
                (base + 1, base + 2, base + 3),
                (base, base + 3, base + 2),
            )
        )
    return np.asarray(vertices, dtype=np.float64), np.asarray(faces, dtype=np.uintp)


def path_fixture(complexity: int) -> Any:
    import numpy as np

    t = np.linspace(0.0, 1.0, complexity + 1)
    return np.column_stack((0.03 * t, 0.004 * np.sin(t * 7.0), 0.003 * np.cos(t * 5.0)))


def case_parameters(case: str, complexity: int) -> tuple[str, str, dict[str, Any]]:
    import numpy as np

    common = {
        "position": (0.003, -0.004, 0.002),
        "orientation": (0.10033164, -0.20066329, 0.05016582, 0.97321693),
    }
    polarization = (0.3, -0.2, 0.8)
    triangle = ((-0.01, -0.008, 0.0), (0.012, -0.006, 0.0), (0.001, 0.013, 0.002))
    tetrahedron = (
        (0.0, 0.0, 0.0),
        (0.012, 0.0, 0.0),
        (0.0, 0.014, 0.0),
        (0.0, 0.0, 0.016),
    )

    if case == "cylinder":
        return (
            "CylinderMagnet",
            "cylinder_B",
            common
            | {
                "diameter": 0.02,
                "height": 0.03,
                "polarization": polarization,
            },
        )
    if case == "dipole":
        return "Dipole", "dipole_B", common | {"moment": (0.4, -0.2, 0.7)}
    if case == "cuboid":
        return (
            "CuboidMagnet",
            "cuboid_B",
            common
            | {
                "dimensions": (0.02, 0.03, 0.04),
                "polarization": polarization,
            },
        )
    if case == "sphere":
        return (
            "SphereMagnet",
            "sphere_B",
            common
            | {
                "diameter": 0.02,
                "polarization": polarization,
            },
        )
    if case == "circular":
        return (
            "CircularCurrent",
            "circular_B",
            common
            | {
                "diameter": 0.03,
                "current": 2.0,
            },
        )
    if case == "triangle":
        return (
            "TriangleMagnet",
            "triangle_B",
            common
            | {
                "polarization": polarization,
                "vertices": triangle,
            },
        )
    if case == "tetrahedron":
        return (
            "TetrahedronMagnet",
            "tetrahedron_B",
            common
            | {
                "polarization": polarization,
                "vertices": tetrahedron,
            },
        )
    if case == "mesh":
        vertices, faces = mesh_fixture(complexity)
        return (
            "MeshMagnet",
            "mesh_B",
            common
            | {
                "polarization": polarization,
                "vertices": vertices,
                "faces": faces,
            },
        )
    if case == "path":
        return (
            "PathCurrent",
            "path_current_B",
            common
            | {
                "current": 2.0,
                "vertices": path_fixture(complexity),
            },
        )
    if case == "triangle_current":
        return (
            "TriangleCurrent",
            "triangle_current_B",
            common
            | {
                "current_density": (1.2, -0.4, 0.3),
                "vertices": triangle,
            },
        )
    if case == "sheet":
        vertices, faces = mesh_fixture(complexity)
        densities = np.tile(np.asarray((1.2, -0.4, 0.3)), (len(faces), 1))
        return (
            "SheetCurrent",
            "sheet_current_B",
            common
            | {
                "current_densities": densities,
                "vertices": vertices,
                "faces": faces,
            },
        )
    raise ValueError(f"unknown case: {case}")


def make_field_call(task: dict[str, Any]) -> Any:
    import numpy as np
    from pymagba import currents, fields, magnets

    seed_text = f"{task['case']}:{task['size']}:{task['complexity']}"
    seed = zlib.crc32(seed_text.encode())
    rng = np.random.default_rng(seed)
    points = rng.uniform((0.04, 0.03, 0.05), (0.12, 0.11, 0.14), (task["size"], 3))
    class_name, function_name, kwargs = case_parameters(
        task["case"], task["complexity"]
    )
    if task["api"] == "functional":
        function = getattr(fields, function_name)
        return lambda: function(points, **kwargs)

    module = currents if class_name.endswith("Current") else magnets
    source = getattr(module, class_name)(**kwargs)
    return lambda: source.compute_B(points)


def make_sensor_source(source: str, complexity: int) -> Any:
    import numpy as np
    from pymagba import currents, magnets

    if source == "dipole":
        return magnets.Dipole(moment=(0.0, 0.0, 1.0))
    if source == "path":
        return currents.PathCurrent(current=2.0, vertices=path_fixture(complexity))
    if source == "sheet":
        vertices, faces = mesh_fixture(complexity)
        densities = np.tile(np.asarray((1.2, -0.4, 0.3)), (len(faces), 1))
        return currents.SheetCurrent(
            current_densities=densities, vertices=vertices, faces=faces
        )
    if source == "collection":
        children = [
            magnets.Dipole(position=(index * 0.0005, 0.0, 0.0), moment=(0.0, 0.0, 1.0))
            for index in range(complexity)
        ]
        return magnets.SourceCollection(children)
    raise ValueError(f"unknown sensor source: {source}")


def sensor_at(index: int, kind: str) -> Any:
    from pymagba import sensors

    position = (0.06 + index * 0.00001, 0.07, 0.08)
    if kind == "linear":
        return sensors.LinearHallSensor(
            position=position,
            sensitive_axis=(0.0, 0.0, 1.0),
            sensitivity=1.2,
            supply_voltage=5.0,
        )
    if kind == "switch":
        return sensors.HallSwitch(
            position=position, sensitive_axis=(0.0, 0.0, 1.0), b_op=1e-6
        )
    if kind == "latch":
        return sensors.HallLatch(
            position=position,
            sensitive_axis=(0.0, 0.0, 1.0),
            b_op=1e-6,
            b_rp=-1e-6,
        )
    raise ValueError(f"unknown sensor kind: {kind}")


def make_sensor_call(task: dict[str, Any]) -> Any:
    from pymagba import sensors

    source = make_sensor_source(task["source"], task["complexity"])
    case = task["case"]
    if case == "observer_mixed":
        kinds = ("linear", "switch", "latch")
        children = [
            sensor_at(index, kinds[index % len(kinds)]) for index in range(task["size"])
        ]
        observer = sensors.ObserverCollection(children)
        return lambda: observer.read_all(source)

    kind, method_name = {
        "linear_read": ("linear", "read"),
        "linear_voltage": ("linear", "read_voltage"),
        "linear_perp": ("linear", "compute_B_perp"),
        "switch_read": ("switch", "read"),
        "switch_state": ("switch", "read_state"),
        "latch_read": ("latch", "read"),
        "latch_state": ("latch", "read_state"),
    }[case]
    sensor = sensor_at(0, kind)
    method = getattr(sensor, method_name)
    return lambda: method(source)


def make_call(task: dict[str, Any]) -> Any:
    if task["family"] == "sensor":
        return make_sensor_call(task)
    return make_field_call(task)


def validate_branches(
    state: dict[str, Any], rust_mode: str, gil_mode: str, *, expect_rust: bool
) -> None:
    serial, parallel = state["rust_branches"]
    retained, detached = state["gil_branches"]
    if expect_rust and rust_mode == "serial" and (serial == 0 or parallel != 0):
        raise RuntimeError(f"forced serial path was not observed: {state}")
    if expect_rust and rust_mode == "parallel" and (parallel == 0 or serial != 0):
        raise RuntimeError(f"forced parallel path was not observed: {state}")
    if gil_mode == "retain" and (retained == 0 or detached != 0):
        raise RuntimeError(f"forced retain path was not observed: {state}")
    if gil_mode == "detach" and (detached == 0 or retained != 0):
        raise RuntimeError(f"forced detach path was not observed: {state}")


def time_task(
    binding: Any,
    task: dict[str, Any],
    policy: dict[str, str],
    request: dict[str, Any],
) -> dict[str, Any]:
    import numpy as np

    reference_call = make_call(task)
    binding._set_threshold_calibration("serial", "retain", True)
    reference = reference_call()
    reference_state = binding._threshold_calibration_state()
    expect_rust = task["family"] == "field"
    validate_branches(reference_state, "serial", "retain", expect_rust=expect_rust)

    call = make_call(task)
    binding._set_threshold_calibration(policy["rust_mode"], policy["gil_mode"], True)
    actual = call()
    policy_state = binding._threshold_calibration_state()
    validate_branches(
        policy_state,
        policy["rust_mode"],
        policy["gil_mode"],
        expect_rust=expect_rust,
    )
    np.testing.assert_allclose(
        np.asarray(actual),
        np.asarray(reference),
        rtol=1e-12,
        atol=1e-14,
        equal_nan=True,
    )

    binding._set_threshold_calibration(policy["rust_mode"], policy["gil_mode"], False)
    for _ in range(request["warmups"]):
        call()

    target_ns = int(request["target_sample_ms"] * 1_000_000)
    start = time.perf_counter_ns()
    call()
    elapsed = max(time.perf_counter_ns() - start, 1)
    loops = max(1, min(request["max_loops"], target_ns // elapsed))

    samples = []
    for _ in range(request["repeats"]):
        start = time.perf_counter_ns()
        result = None
        for _ in range(loops):
            result = call()
        duration = time.perf_counter_ns() - start
        if result is None:
            raise AssertionError("timing loop did not execute")
        samples.append(duration / loops)

    return task | {
        "policy": f"{policy['rust_mode']}:{policy['gil_mode']}",
        "loops": loops,
        "samples_ns_per_call": samples,
        "verification": {
            "reference_state": reference_state,
            "policy_state": policy_state,
        },
    }


def run_worker_process() -> int:
    import importlib.metadata

    import numpy as np
    import pymagba.pymagba_binding as binding

    if not hasattr(binding, "_set_threshold_calibration"):
        raise RuntimeError(
            "the installed extension lacks threshold-calibration; rebuild with "
            "`uv run maturin develop --release --features threshold-calibration`"
        )
    request = json.load(sys.stdin)
    policy = request["policy"]
    results = [time_task(binding, task, policy, request) for task in request["tasks"]]
    response = {
        "provenance": {
            "pid": os.getpid(),
            "policy": policy,
            "python": sys.version,
            "numpy": np.__version__,
            "pymagba": importlib.metadata.version("pymagba"),
            "gil_enabled": getattr(sys, "_is_gil_enabled", lambda: True)(),
            "extension": str(Path(binding.__file__).resolve()),
            "rayon_num_threads": os.environ.get("RAYON_NUM_THREADS"),
        },
        "results": results,
    }
    json.dump(response, sys.stdout)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    result.add_argument("--results-dir", type=Path, default=Path("benchmark-results"))
    result.add_argument(
        "--cases", type=lambda v: csv_values(v), default=list(ALL_CASES)
    )
    result.add_argument(
        "--sensor-cases",
        type=lambda v: csv_values(v),
        default=list(ALL_SENSOR_CASES),
    )
    result.add_argument(
        "--sensor-sources",
        type=lambda v: csv_values(v),
        default=list(ALL_SENSOR_SOURCES),
    )
    result.add_argument(
        "--sensor-counts",
        type=lambda v: csv_values(v, int),
        default=[0, 1, 2, 4, 8, 16, 32, 64],
    )
    result.add_argument(
        "--apis",
        type=lambda v: csv_values(v),
        default=["functional", "object"],
        choices=None,
    )
    result.add_argument(
        "--sizes", type=lambda v: csv_values(v, int), default=list(DEFAULT_SIZES)
    )
    result.add_argument(
        "--complexities", type=lambda v: csv_values(v, int), default=[4, 32]
    )
    result.add_argument(
        "--policies", type=lambda v: csv_values(v), default=list(DEFAULT_POLICIES)
    )
    result.add_argument("--repeats", type=int, default=7)
    result.add_argument("--warmups", type=int, default=3)
    result.add_argument("--target-sample-ms", type=float, default=20.0)
    result.add_argument("--max-loops", type=int, default=100_000)
    result.add_argument("--order-seed", type=int, default=20251004)
    return result


def validate_args(args: argparse.Namespace) -> None:
    unknown_cases = set(args.cases) - set(ALL_CASES)
    if unknown_cases:
        raise SystemExit(f"unknown cases: {', '.join(sorted(unknown_cases))}")
    unknown_sensor_cases = set(args.sensor_cases) - set(ALL_SENSOR_CASES)
    if unknown_sensor_cases:
        raise SystemExit(
            f"unknown sensor cases: {', '.join(sorted(unknown_sensor_cases))}"
        )
    unknown_sensor_sources = set(args.sensor_sources) - set(ALL_SENSOR_SOURCES)
    if unknown_sensor_sources:
        raise SystemExit(
            f"unknown sensor sources: {', '.join(sorted(unknown_sensor_sources))}"
        )
    unknown_apis = set(args.apis) - {"functional", "object"}
    if unknown_apis:
        raise SystemExit(f"unknown APIs: {', '.join(sorted(unknown_apis))}")
    for policy in args.policies:
        try:
            rust_mode, gil_mode = policy.split(":", 1)
        except ValueError as exc:
            raise SystemExit(f"invalid policy: {policy}") from exc
        if rust_mode not in {"auto", "serial", "parallel"}:
            raise SystemExit(f"invalid Rust mode in policy: {policy}")
        if gil_mode not in {"auto", "retain", "detach"}:
            raise SystemExit(f"invalid GIL mode in policy: {policy}")
    if any(size < 0 for size in args.sizes):
        raise SystemExit("sizes must be non-negative")
    if any(size < 0 for size in args.sensor_counts):
        raise SystemExit("sensor counts must be non-negative")
    if any(value < 1 for value in args.complexities):
        raise SystemExit("complexities must be positive")
    if args.repeats < 1 or args.warmups < 0 or args.max_loops < 1:
        raise SystemExit("invalid repeat, warmup, or loop count")


def main() -> int:
    args = parser().parse_args()
    if args.worker:
        return run_worker_process()
    validate_args(args)
    return run_controller(args)


if __name__ == "__main__":
    raise SystemExit(main())
