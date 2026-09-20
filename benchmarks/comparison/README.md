# Performance Comparison Benchmarks

This directory contains our specialized benchmark suite for directly comparing the performance of `pymagba` against `magpylib`. It is isolated from the main library benchmarks to cleanly manage the comparative environments without interfering with PyMagba's internal test workflows.

## Prerequisites
Ensure you have `uv` installed. The ASV (Airspeed Velocity) benchmark framework will automatically create an isolated virtual environment (`.asv/env`) utilizing `uv` and install both `magpylib` and the compiled local version of `pymagba`.

## Running the Benchmarks
To run the full suite of comparative benchmarks, execute the following from the root directory of the repository:

```bash
uv run asv run
```

This will run all configured geometries (Cuboids, Cylinders, Tetrahedrons, etc.) across pure field computation, collection execution, object creation, and object manipulation.

## Generating the Report
Once the benchmarks have completed, you can generate a collated Markdown report (`PERFORMANCE.md`) using the provided script. This script will extract library versions, calculate accuracy errors, and format the output.

Run:

```bash
uv run python scripts/collate_benchmarks.py
```

The resulting `PERFORMANCE.md` file will then be available in the root directory detailing the exact speedups achieved!
