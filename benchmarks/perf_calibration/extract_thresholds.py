#!/usr/bin/env python3
# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Extract readable threshold candidates from calibration report JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_reports(paths: list[Path]) -> list[dict[str, Any]]:
    reports = []
    for path in paths:
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("schema_version") != 2 or not isinstance(
            report.get("candidates"), dict
        ):
            raise SystemExit(f"{path}: unsupported calibration report")
        report["_path"] = str(path)
        reports.append(report)
    return reports


def candidate_label(candidate: dict[str, Any]) -> str:
    details = []
    if candidate.get("api"):
        details.append(candidate["api"])
    if candidate.get("source"):
        details.append(f"source={candidate['source']}")
    if candidate.get("variant") not in {None, "default"}:
        details.append(f"variant={candidate['variant']}")
    if candidate.get("complexity") is not None:
        details.append(f"complexity={candidate['complexity']}")
    return ", ".join(details) or "default"


def extracted_data(reports: list[dict[str, Any]], comparison: str) -> dict[str, Any]:
    comparisons = ("rayon", "gil") if comparison == "all" else (comparison,)
    candidates = {}
    for name in comparisons:
        rows = [
            candidate | {"report": report["_path"]}
            for report in reports
            for candidate in report["candidates"].get(name, [])
        ]
        # Older reports included empty sensor groups in the Rayon section even
        # though sensors never run the forced serial/parallel comparison.
        candidates[name] = (
            [row for row in rows if row["family"] == "field"]
            if name == "rayon"
            else rows
        )

    rayon_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates.get("rayon", []):
        if (
            candidate["family"] == "field"
            and candidate["case"] != "collection"
            and candidate["status"] == "crossover"
        ):
            rayon_by_case[candidate["case"]].append(candidate)

    recommendations = []
    for case, rows in sorted(rayon_by_case.items()):
        first_parallel = max(row["candidate_work_size"] for row in rows)
        recommendations.append(
            {
                "case": case,
                "first_parallel_size": first_parallel,
                "stored_threshold": max(0, first_parallel - 1),
                "candidate_range": [
                    min(row["candidate_work_size"] for row in rows),
                    first_parallel,
                ],
                "workloads": len(rows),
            }
        )

    return {
        "reports": [report["_path"] for report in reports],
        "provenance": [report.get("provenance", {}) for report in reports],
        "rayon_recommendations": recommendations,
        "candidates": candidates,
    }


def markdown(data: dict[str, Any]) -> str:
    lines = ["# Extracted Calibration Thresholds", "", "Reports:", ""]
    lines.extend(f"- `{path}`" for path in data["reports"])

    recommendations = data["rayon_recommendations"]
    if recommendations:
        lines.extend(
            [
                "",
                "## Conservative Rayon Recommendations",
                "",
                "The recommendation is the largest stable crossover among the",
                "functional/object variants present in the supplied reports. Review",
                "variable-complexity workloads before changing code. Source collections",
                "remain in the detailed table but are excluded from this point-only summary.",
                "",
                "| Case | First parallel size | Stored `len >` threshold | Candidate range | Workloads |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in recommendations:
            low, high = row["candidate_range"]
            lines.append(
                f"| {row['case']} | {row['first_parallel_size']:,} | "
                f"{row['stored_threshold']:,} | {low:,}-{high:,} | "
                f"{row['workloads']} |"
            )

    for comparison, candidates in data["candidates"].items():
        comparison_title = "Rayon" if comparison == "rayon" else "GIL"
        lines.extend(
            [
                "",
                f"## {comparison_title} Candidates",
                "",
                "| Family | Case | Workload | Status | Candidate | Maximum tested | Limit |",
                "| --- | --- | --- | --- | ---: | ---: | --- |",
            ]
        )
        for row in sorted(
            candidates,
            key=lambda value: (
                value["family"],
                value["case"],
                candidate_label(value),
            ),
        ):
            candidate = row.get("candidate_work_size")
            maximum = row.get("maximum_tested_work_size")
            lines.append(
                f"| {row['family']} | {row['case']} | {candidate_label(row)} | "
                f"{row['status']} | {candidate if candidate is not None else '—'} | "
                f"{maximum if maximum is not None else '—'} | "
                f"{row.get('search_limit_reason') or '—'} |"
            )
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("reports", nargs="+", type=Path)
    result.add_argument("--comparison", choices=("rayon", "gil", "all"), default="all")
    result.add_argument("--format", choices=("markdown", "json"), default="markdown")
    result.add_argument("--output", type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    data = extracted_data(load_reports(args.reports), args.comparison)
    output = (
        json.dumps(data, indent=2) + "\n" if args.format == "json" else markdown(data)
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
