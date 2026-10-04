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
import threading
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
    "collection",
)
COLLECTION_VARIANTS = ("homogeneous", "mixed", "nested")
CYLINDER_VARIANTS = ("mixed", "axial")
POINT_DISTRIBUTIONS = ("uniform", "clustered", "line")
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
ALL_INPUT_LAYOUTS = (
    "contiguous_f64",
    "contiguous_f32",
    "strided_f64",
    "python_list",
    "singleton_1d",
    "singleton_list",
)
DEFAULT_VALIDATION_LAYOUTS = ALL_INPUT_LAYOUTS[1:]
VARIABLE_CASES = frozenset(("mesh", "path", "sheet", "collection"))
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
            if case == "collection" and api == "functional":
                continue
            if case == "collection":
                variants = args.collection_variants
            elif case == "cylinder":
                variants = args.cylinder_variants
            else:
                variants = ["default"]
            for complexity in complexities:
                for variant in variants:
                    for size in args.sizes:
                        tasks.append(
                            {
                                "family": "field",
                                "case": case,
                                "api": api,
                                "source": None,
                                "variant": variant,
                                "distribution": "uniform",
                                "layout": "contiguous_f64",
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
                            "variant": "default",
                            "distribution": None,
                            "layout": None,
                            "complexity": complexity,
                            "size": size,
                        }
                    )
    return tasks


def run_worker(
    policy: str,
    tasks: list[dict[str, Any]],
    args: argparse.Namespace,
    *,
    phase: str = "coarse",
    checkpoint_dir: Path | None = None,
) -> dict[str, Any]:
    rust_mode, gil_mode = policy.split(":", 1)
    request = {
        "policy": {"rust_mode": rust_mode, "gil_mode": gil_mode},
        "tasks": tasks,
        "repeats": args.repeats,
        "warmups": args.warmups,
        "target_sample_ms": args.target_sample_ms,
        "max_loops": args.max_loops,
        "responsiveness": args.responsiveness,
        "responsiveness_repeats": args.responsiveness_repeats,
        "responsiveness_interval_ms": args.responsiveness_interval_ms,
        "progress": args.progress,
        "phase": phase,
    }
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker"],
        input=json.dumps(request),
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"worker {policy} failed with exit code {completed.returncode}; "
            "see worker stderr above"
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"worker {policy} returned invalid JSON:\n{completed.stdout}\n"
            "see worker stderr above"
        ) from exc
    if checkpoint_dir is not None:
        checkpoint = checkpoint_dir / f"{phase}-{policy.replace(':', '-')}.json"
        checkpoint.write_text(json.dumps(response, indent=2) + "\n")
    return response


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
                "variant": result["variant"],
                "distribution": result["distribution"],
                "layout": result["layout"],
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
                "phase": result["phase"],
                "responsiveness": result["responsiveness"],
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
            row["variant"],
            row["distribution"],
            row["layout"],
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
            comparable.append(
                (
                    size,
                    qualifies,
                    left,
                    right,
                    win_fraction,
                    policies[left_policy]["responsiveness"],
                    policies[right_policy]["responsiveness"],
                )
            )

        if not comparable:
            continue

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
                "variant": group[4],
                "distribution": group[5],
                "layout": group[6],
                "complexity": group[7],
                "work_axis": group[8],
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
                        "qualifies": item[1],
                        "left_responsiveness": item[5],
                        "right_responsiveness": item[6],
                    }
                    for item in comparable
                ],
            }
        )
    return candidates


def refinement_values(evidence: list[dict[str, Any]], count: int) -> list[int]:
    """Return several integer probes around the first observed advantage."""
    qualifying = [index for index, row in enumerate(evidence) if row["qualifies"]]
    if not qualifying:
        return []

    index = qualifying[0]
    lower_index = max(0, index - 1)
    upper_index = min(len(evidence) - 1, index + 1)
    lower = evidence[lower_index]["work_size"]
    upper = evidence[upper_index]["work_size"]
    if lower == upper:
        lower = max(0, lower - 2)
        upper += 2

    existing = {row["work_size"] for row in evidence}
    values = {max(0, evidence[index]["work_size"] - 1), evidence[index]["work_size"] + 1}
    span = upper - lower
    for step in range(1, count + 1):
        values.add(lower + round(span * step / (count + 1)))
    return sorted(value for value in values if value not in existing)


def extension_values(
    evidence: list[dict[str, Any]], steps: int, maximum: int
) -> list[int]:
    """Extend an unresolved logarithmic sweep without exceeding its work cap."""
    if not evidence or steps == 0:
        return []
    value = max(row["work_size"] for row in evidence)
    values = []
    for _ in range(steps):
        value = max(1, value * 2)
        if value > maximum:
            break
        values.append(value)
    return values


def extension_tasks(
    candidates: dict[str, list[dict[str, Any]]], steps: int, maximum: int
) -> dict[str, list[dict[str, Any]]]:
    """Build larger work sizes for comparisons without a stable crossover."""
    result: dict[str, list[dict[str, Any]]] = {}
    for comparison, rows in candidates.items():
        tasks: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in rows:
            if row["status"] == "crossover":
                continue
            for value in extension_values(row["evidence"], steps, maximum):
                source_complexity = row["work_axis"] == "source_complexity"
                task = {
                    "family": row["family"],
                    "case": row["case"],
                    "api": row["api"],
                    "source": row["source"],
                    "variant": row["variant"],
                    "distribution": row["distribution"],
                    "layout": row["layout"],
                    "complexity": value if source_complexity else row["complexity"],
                    "size": 1 if source_complexity else value,
                }
                tasks[tuple(task.values())] = task
        result[comparison] = list(tasks.values())
    return result


def refinement_tasks(
    candidates: dict[str, list[dict[str, Any]]], count: int
) -> dict[str, list[dict[str, Any]]]:
    """Build focused tasks for each independent policy comparison."""
    result: dict[str, list[dict[str, Any]]] = {}
    for comparison, rows in candidates.items():
        tasks: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in rows:
            for value in refinement_values(row["evidence"], count):
                source_complexity = row["work_axis"] == "source_complexity"
                task = {
                    "family": row["family"],
                    "case": row["case"],
                    "api": row["api"],
                    "source": row["source"],
                    "variant": row["variant"],
                    "distribution": row["distribution"],
                    "layout": row["layout"],
                    "complexity": value if source_complexity else row["complexity"],
                    "size": 1 if source_complexity else value,
                }
                key = tuple(task.values())
                tasks[key] = task
        result[comparison] = list(tasks.values())
    return result


def candidate_validation_tasks(
    candidates: dict[str, list[dict[str, Any]]], layouts: list[str]
) -> dict[str, list[dict[str, Any]]]:
    """Build cutover-adjacent field tasks for non-primary input layouts."""
    result: dict[str, list[dict[str, Any]]] = {}
    for comparison, rows in candidates.items():
        tasks: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in rows:
            candidate = row["candidate_work_size"]
            if row["family"] != "field" or candidate is None:
                continue
            for size in sorted({max(0, candidate - 1), candidate, candidate + 1}):
                for layout in layouts:
                    if layout.startswith("singleton_") and size != 1:
                        continue
                    task = {
                        "family": row["family"],
                        "case": row["case"],
                        "api": row["api"],
                        "source": row["source"],
                        "variant": row["variant"],
                        "distribution": row["distribution"],
                        "layout": layout,
                        "complexity": row["complexity"],
                        "size": size,
                    }
                    tasks[tuple(task.values())] = task
        result[comparison] = list(tasks.values())
    return result


def workload_validation_tasks(
    candidates: dict[str, list[dict[str, Any]]], distributions: list[str]
) -> dict[str, list[dict[str, Any]]]:
    """Build candidate-sized field tasks for alternate point distributions."""
    result: dict[str, list[dict[str, Any]]] = {}
    for comparison, rows in candidates.items():
        tasks: dict[tuple[Any, ...], dict[str, Any]] = {}
        for row in rows:
            candidate = row["candidate_work_size"]
            if row["family"] != "field" or candidate is None:
                continue
            for distribution in distributions:
                task = {
                    "family": row["family"],
                    "case": row["case"],
                    "api": row["api"],
                    "source": row["source"],
                    "variant": row["variant"],
                    "distribution": distribution,
                    "layout": "contiguous_f64",
                    "complexity": row["complexity"],
                    "size": candidate,
                }
                tasks[tuple(task.values())] = task
        result[comparison] = list(tasks.values())
    return result


def annotate_search_limits(
    candidates: dict[str, list[dict[str, Any]]], args: argparse.Namespace
) -> None:
    for rows in candidates.values():
        for row in rows:
            tested = [point["work_size"] for point in row["evidence"]]
            row["maximum_tested_work_size"] = max(tested) if tested else None
            if row["status"] == "crossover":
                row["search_limit_reason"] = None
            elif not tested:
                row["search_limit_reason"] = "missing_policy_pair"
            elif max(tested) >= args.max_work_size:
                row["search_limit_reason"] = "max_work_size"
            elif args.extension_steps:
                row["search_limit_reason"] = "extension_steps"
            else:
                row["search_limit_reason"] = "extension_disabled"


def candidate_status_counts(
    candidates: dict[str, list[dict[str, Any]]], policies: list[str]
) -> dict[str, Any]:
    required = {
        "rayon": {"serial:detach", "parallel:detach"},
        "gil": {"auto:retain", "auto:detach"},
    }
    selected = set(policies)
    result = {}
    for comparison, rows in candidates.items():
        counts = {status: 0 for status in ("crossover", "inconclusive", "no_crossover")}
        for row in rows:
            counts[row["status"]] += 1
        result[comparison] = {
            "comparison_available": required[comparison] <= selected,
            "candidate_count": len(rows),
            "statuses": counts,
        }
    return result


def run_controller(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[1]
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    run_dir = args.results_dir / f"ffi-threshold-{stamp}-{os.getpid()}"
    run_dir.mkdir(parents=True, exist_ok=False)
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
        worker = run_worker(policy, policy_tasks, args, checkpoint_dir=run_dir)
        workers.append(worker["provenance"])
        all_results.extend(worker["results"])

    summaries = summarize(all_results)
    candidates = {
        "rayon": find_crossover(summaries, "serial:detach", "parallel:detach"),
        "gil": find_crossover(summaries, "auto:retain", "auto:detach"),
    }
    comparison_policies = {
        "rayon": ("serial:detach", "parallel:detach"),
        "gil": ("auto:retain", "auto:detach"),
    }
    extensions = extension_tasks(
        candidates, args.extension_steps, args.max_work_size
    )
    if args.extension_steps:
        for comparison, extension in extensions.items():
            if not extension:
                continue
            print(
                f"extending {comparison} sweep with {len(extension)} tasks",
                flush=True,
            )
            for policy in comparison_policies[comparison]:
                if policy not in args.policies:
                    continue
                worker = run_worker(
                    policy,
                    extension,
                    args,
                    phase="extension",
                    checkpoint_dir=run_dir,
                )
                workers.append(worker["provenance"])
                all_results.extend(worker["results"])
        summaries = summarize(all_results)
        candidates = {
            "rayon": find_crossover(
                summaries, "serial:detach", "parallel:detach"
            ),
            "gil": find_crossover(summaries, "auto:retain", "auto:detach"),
        }

    refined = refinement_tasks(candidates, args.refinement_points)
    if args.refinement_points:
        for comparison, refinement in refined.items():
            if not refinement:
                continue
            print(
                f"refining {comparison} transition with {len(refinement)} tasks",
                flush=True,
            )
            for policy in comparison_policies[comparison]:
                if policy not in args.policies:
                    continue
                worker = run_worker(
                    policy,
                    refinement,
                    args,
                    phase="refinement",
                    checkpoint_dir=run_dir,
                )
                workers.append(worker["provenance"])
                all_results.extend(worker["results"])
        summaries = summarize(all_results)
        candidates = {
            "rayon": find_crossover(
                summaries, "serial:detach", "parallel:detach"
            ),
            "gil": find_crossover(summaries, "auto:retain", "auto:detach"),
        }
    validation_results: list[dict[str, Any]] = []
    validations = candidate_validation_tasks(candidates, args.validation_layouts)
    workload_validations = workload_validation_tasks(
        candidates, args.validation_distributions
    )
    for comparison, tasks_for_comparison in workload_validations.items():
        existing = {tuple(task.values()) for task in validations[comparison]}
        validations[comparison].extend(
            task
            for task in tasks_for_comparison
            if tuple(task.values()) not in existing
        )
    if args.validate_candidates:
        for comparison, validation in validations.items():
            if not validation:
                continue
            print(
                f"validating {comparison} candidate layouts with "
                f"{len(validation)} tasks",
                flush=True,
            )
            policies_for_validation = list(comparison_policies[comparison])
            random.Random(f"{args.order_seed}:{comparison}").shuffle(
                policies_for_validation
            )
            for policy in policies_for_validation:
                if policy not in args.policies:
                    continue
                worker = run_worker(
                    policy,
                    validation,
                    args,
                    phase="validation",
                    checkpoint_dir=run_dir,
                )
                workers.append(worker["provenance"])
                validation_results.extend(worker["results"])
    annotate_search_limits(candidates, args)
    report = {
        "schema_version": 2,
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
            "collection_variants": args.collection_variants,
            "cylinder_variants": args.cylinder_variants,
            "policies": policies,
            "repeats": args.repeats,
            "warmups": args.warmups,
            "target_sample_ms": args.target_sample_ms,
            "max_loops": args.max_loops,
            "order_seed": args.order_seed,
            "refinement_points": args.refinement_points,
            "extension_steps": args.extension_steps,
            "max_work_size": args.max_work_size,
            "responsiveness": args.responsiveness,
            "responsiveness_repeats": args.responsiveness_repeats,
            "responsiveness_interval_ms": args.responsiveness_interval_ms,
            "progress": args.progress,
            "validate_candidates": args.validate_candidates,
            "validation_layouts": args.validation_layouts,
            "validation_distributions": args.validation_distributions,
        },
        "workers": workers,
        "results": all_results,
        "summaries": summaries,
        "candidates": candidates,
        "validations": validation_results,
        "validation_summaries": summarize(validation_results),
        "readiness": candidate_status_counts(candidates, args.policies),
    }

    destination = run_dir / "report.json"
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


def case_parameters(
    case: str, complexity: int, variant: str = "default"
) -> tuple[str, str, dict[str, Any]]:
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
        cylinder_polarization = (0.0, 0.0, 0.9) if variant == "axial" else polarization
        return (
            "CylinderMagnet",
            "cylinder_B",
            common
            | {
                "diameter": 0.02,
                "height": 0.03,
                "polarization": cylinder_polarization,
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


def collection_fixture(complexity: int, variant: str) -> Any:
    from pymagba import currents, magnets

    children = []
    for index in range(complexity):
        position = (index * 0.0005, (index % 3) * 0.0002, 0.0)
        if variant == "homogeneous" or index % 3 == 0:
            child = magnets.Dipole(position=position, moment=(0.2, -0.1, 0.5))
        elif index % 3 == 1:
            child = magnets.CuboidMagnet(
                position=position,
                dimensions=(0.004, 0.005, 0.006),
                polarization=(0.3, -0.2, 0.8),
            )
        else:
            child = currents.CircularCurrent(
                position=position, diameter=0.006, current=1.5
            )
        children.append(child)

    if variant == "nested":
        midpoint = max(1, len(children) // 2)
        nested = [magnets.SourceCollection(children[:midpoint])]
        if midpoint < len(children):
            nested.append(magnets.SourceCollection(children[midpoint:]))
        return magnets.SourceCollection(nested)
    return magnets.SourceCollection(children)


def point_fixture(task: dict[str, Any]) -> Any:
    import numpy as np

    seed_text = (
        f"{task['case']}:{task['variant']}:{task['distribution']}:"
        f"{task['size']}:{task['complexity']}"
    )
    rng = np.random.default_rng(zlib.crc32(seed_text.encode()))
    size = task["size"]
    if task["distribution"] == "uniform":
        return rng.uniform((0.04, 0.03, 0.05), (0.12, 0.11, 0.14), (size, 3))
    if task["distribution"] == "clustered":
        return rng.normal((0.075, 0.065, 0.09), (0.002, 0.003, 0.002), (size, 3))
    if task["distribution"] == "line":
        t = np.linspace(0.0, 1.0, size)
        return np.column_stack((0.04 + 0.08 * t, 0.05 + 0.02 * t, 0.14 - 0.07 * t))
    raise ValueError(f"unknown point distribution: {task['distribution']}")


def make_field_call(task: dict[str, Any]) -> Any:
    import numpy as np
    from pymagba import currents, fields, magnets

    points = point_fixture(task)
    layout = task["layout"]
    if layout == "contiguous_f32":
        points = points.astype(np.float32)
    elif layout == "float32_reference":
        points = points.astype(np.float32).astype(np.float64)
    elif layout == "strided_f64":
        storage = np.empty((task["size"] * 2, 3), dtype=np.float64)
        storage[::2] = points
        points = storage[::2]
    elif layout == "python_list":
        points = points.tolist()
    elif layout == "singleton_1d":
        points = points[0]
    elif layout == "singleton_list":
        points = points[0].tolist()
    elif layout != "contiguous_f64":
        raise ValueError(f"unknown input layout: {layout}")
    if task["case"] == "collection":
        source = collection_fixture(task["complexity"], task["variant"])
        return lambda: source.compute_B(points)

    class_name, function_name, kwargs = case_parameters(
        task["case"], task["complexity"], task["variant"]
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


def measure_responsiveness(
    call: Any, *, repeats: int, interval_ms: float
) -> dict[str, Any]:
    """Measure whether a sleeping Python ticker runs during one extension call."""
    interval_s = interval_ms / 1_000.0
    samples = []
    for _ in range(repeats):
        timestamps: list[int] = []
        ready = threading.Event()
        stop = threading.Event()

        def ticker(
            ready_event: threading.Event = ready,
            stop_event: threading.Event = stop,
            samples: list[int] = timestamps,
        ) -> None:
            ready_event.set()
            while not stop_event.wait(interval_s):
                samples.append(time.perf_counter_ns())

        thread = threading.Thread(target=ticker, daemon=True)
        thread.start()
        ready.wait()
        time.sleep(interval_s * 2)
        try:
            start = time.perf_counter_ns()
            result = call()
            end = time.perf_counter_ns()
            if result is None:
                raise AssertionError("responsiveness call returned no result")
        finally:
            stop.set()
            thread.join()

        duration_ns = max(end - start, 1)
        interval_ns = interval_s * 1_000_000_000
        ticks = sum(
            start + interval_ns < timestamp < end - interval_ns
            for timestamp in timestamps
        )
        expected_ticks = max(duration_ns - 2 * interval_ns, 1) / interval_ns
        samples.append(
            {
                "duration_ns": duration_ns,
                "interior_ticks": ticks,
                "progress_fraction": min(ticks / expected_ticks, 1.0),
            }
        )

    median_duration = statistics.median(row["duration_ns"] for row in samples)
    return {
        "status": "measured"
        if median_duration >= interval_s * 4 * 1_000_000_000
        else "too_short",
        "interval_ms": interval_ms,
        "median_duration_ns": median_duration,
        "median_interior_ticks": statistics.median(
            row["interior_ticks"] for row in samples
        ),
        "median_progress_fraction": statistics.median(
            row["progress_fraction"] for row in samples
        ),
        "samples": samples,
    }


def time_task(
    binding: Any,
    task: dict[str, Any],
    policy: dict[str, str],
    request: dict[str, Any],
) -> dict[str, Any]:
    import numpy as np

    reference_task = task
    if task["family"] == "field" and task["layout"] == "contiguous_f32":
        reference_task = task | {"layout": "float32_reference"}
    elif task["family"] == "field" and task["layout"] != "contiguous_f64":
        reference_task = task | {"layout": "contiguous_f64"}
    reference_call = make_call(reference_task)
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

    responsiveness = None
    if (
        request["responsiveness"]
        and policy["rust_mode"] == "auto"
        and policy["gil_mode"] in {"retain", "detach"}
    ):
        responsiveness = measure_responsiveness(
            call,
            repeats=request["responsiveness_repeats"],
            interval_ms=request["responsiveness_interval_ms"],
        )

    return task | {
        "policy": f"{policy['rust_mode']}:{policy['gil_mode']}",
        "phase": request["phase"],
        "loops": loops,
        "samples_ns_per_call": samples,
        "responsiveness": responsiveness,
        "verification": {
            "reference_state": reference_state,
            "policy_state": policy_state,
        },
    }


def run_worker_process() -> int:
    import importlib.metadata

    import numpy as np
    import pymagba.pymagba_binding as binding
    from tqdm.auto import tqdm

    if not hasattr(binding, "_set_threshold_calibration"):
        raise RuntimeError(
            "the installed extension lacks threshold-calibration; rebuild with "
            "`uv run maturin develop --release --features threshold-calibration`"
        )
    request = json.load(sys.stdin)
    policy = request["policy"]
    policy_name = f"{policy['rust_mode']}:{policy['gil_mode']}"
    tasks = tqdm(
        request["tasks"],
        desc=f"{request['phase']} {policy_name}",
        unit="task",
        dynamic_ncols=True,
        disable=None if request["progress"] else True,
    )
    results = [time_task(binding, task, policy, request) for task in tasks]
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
            "phase": request["phase"],
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
        "--collection-variants",
        type=lambda v: csv_values(v),
        default=list(COLLECTION_VARIANTS),
    )
    result.add_argument(
        "--cylinder-variants",
        type=lambda v: csv_values(v),
        default=list(CYLINDER_VARIANTS),
    )
    result.add_argument(
        "--policies", type=lambda v: csv_values(v), default=list(DEFAULT_POLICIES)
    )
    result.add_argument("--repeats", type=int, default=7)
    result.add_argument("--warmups", type=int, default=3)
    result.add_argument("--target-sample-ms", type=float, default=20.0)
    result.add_argument("--max-loops", type=int, default=100_000)
    result.add_argument("--order-seed", type=int, default=20251004)
    result.add_argument(
        "--refinement-points",
        type=int,
        default=4,
        help="intermediate work sizes measured around each observed transition",
    )
    result.add_argument(
        "--extension-steps",
        type=int,
        default=6,
        help="doublings beyond an unresolved coarse sweep",
    )
    result.add_argument(
        "--max-work-size",
        type=int,
        default=65_536,
        help="point, sensor, or source-complexity cap for automatic extension",
    )
    result.add_argument(
        "--responsiveness",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="measure background Python-thread progress for GIL comparisons",
    )
    result.add_argument("--responsiveness-repeats", type=int, default=3)
    result.add_argument("--responsiveness-interval-ms", type=float, default=0.5)
    result.add_argument(
        "--validate-candidates",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="measure candidate-adjacent non-primary input layouts",
    )
    result.add_argument(
        "--validation-layouts",
        type=lambda v: csv_values(v),
        default=list(DEFAULT_VALIDATION_LAYOUTS),
    )
    result.add_argument(
        "--validation-distributions",
        type=lambda v: csv_values(v),
        default=["clustered", "line"],
    )
    result.add_argument(
        "--dry-run",
        action="store_true",
        help="validate configuration and print the coarse execution plan",
    )
    result.add_argument(
        "--preflight",
        action="store_true",
        help="verify the calibration build and every selected forced policy",
    )
    result.add_argument(
        "--progress",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="show per-worker task progress bars on interactive stderr",
    )
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
    unknown_layouts = set(args.validation_layouts) - set(ALL_INPUT_LAYOUTS)
    if unknown_layouts:
        raise SystemExit(
            f"unknown validation layouts: {', '.join(sorted(unknown_layouts))}"
        )
    unknown_collection_variants = set(args.collection_variants) - set(
        COLLECTION_VARIANTS
    )
    if unknown_collection_variants:
        raise SystemExit(
            "unknown collection variants: "
            f"{', '.join(sorted(unknown_collection_variants))}"
        )
    unknown_cylinder_variants = set(args.cylinder_variants) - set(CYLINDER_VARIANTS)
    if unknown_cylinder_variants:
        raise SystemExit(
            f"unknown cylinder variants: {', '.join(sorted(unknown_cylinder_variants))}"
        )
    unknown_distributions = set(args.validation_distributions) - set(
        POINT_DISTRIBUTIONS
    )
    if unknown_distributions:
        raise SystemExit(
            "unknown validation distributions: "
            f"{', '.join(sorted(unknown_distributions))}"
        )
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
    if args.refinement_points < 0:
        raise SystemExit("refinement points must be non-negative")
    if args.extension_steps < 0 or args.max_work_size < 1:
        raise SystemExit("invalid extension step count or maximum work size")
    if args.responsiveness_repeats < 1 or args.responsiveness_interval_ms <= 0:
        raise SystemExit("invalid responsiveness repeat count or interval")
    if args.target_sample_ms <= 0:
        raise SystemExit("target sample duration must be positive")
    if not args.cases and not args.sensor_cases:
        raise SystemExit("at least one field or sensor case is required")


def print_dry_run(args: argparse.Namespace) -> None:
    tasks = build_tasks(args)
    by_policy = {}
    for policy in args.policies:
        by_policy[policy] = sum(
            task["family"] == "field" or policy.startswith("auto:") for task in tasks
        )
    print(
        json.dumps(
            {
                "coarse_tasks": len(tasks),
                "tasks_by_policy": by_policy,
                "coarse_timing_samples": sum(by_policy.values()) * args.repeats,
                "automatic_extension_steps": args.extension_steps,
                "maximum_work_size": args.max_work_size,
                "candidate_refinement_points": args.refinement_points,
                "candidate_validation": args.validate_candidates,
                "note": "extension, refinement, and validation counts depend on results",
            },
            indent=2,
        )
    )


def run_preflight(args: argparse.Namespace) -> None:
    quick_values = vars(args) | {
        "repeats": 1,
        "warmups": 0,
        "target_sample_ms": 0.001,
        "max_loops": 1,
        "responsiveness": False,
    }
    quick = argparse.Namespace(**quick_values)
    tasks = [
        {
            "family": "field",
            "case": "dipole",
            "api": "object",
            "source": None,
            "variant": "default",
            "distribution": "uniform",
            "layout": "contiguous_f64",
            "complexity": 1,
            "size": 2,
        },
        {
            "family": "sensor",
            "case": "linear_read",
            "api": "sensor",
            "source": "dipole",
            "variant": "default",
            "distribution": None,
            "layout": None,
            "complexity": 1,
            "size": 1,
        },
    ]
    extension = None
    for policy in args.policies:
        policy_tasks = [
            task
            for task in tasks
            if task["family"] == "field" or policy.startswith("auto:")
        ]
        worker = run_worker(policy, policy_tasks, quick, phase="preflight")
        extension = worker["provenance"]["extension"]
    print(f"preflight passed for {len(args.policies)} policies using {extension}")


def main() -> int:
    args = parser().parse_args()
    if args.worker:
        return run_worker_process()
    validate_args(args)
    if args.preflight:
        run_preflight(args)
        return 0
    if args.dry_run:
        print_dry_run(args)
        return 0
    return run_controller(args)


if __name__ == "__main__":
    raise SystemExit(main())
