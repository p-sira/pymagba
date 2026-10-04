# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Multi-threaded Rayon benchmarks around the FFI parallelization thresholds.

These benchmarks are marked ``rayon`` and are meant for the CodSpeed walltime
job, which runs with Rayon using every available CPU. Simulation mode counts
instructions on a single thread, so it cannot show parallel speedups.

For each source, three point counts are measured:

- ``last_serial``: the largest count that still runs serially with the GIL held
- ``first_parallel``: the first count that runs through Rayon with the GIL
  released
- ``large``: a workload well above every cutoff, to track parallel scaling

Comparing ``last_serial`` with ``first_parallel`` shows whether each cutoff is
still worth it on the CI runner.
"""

import pytest

from .conftest import make_observers
from .test_bench_sources import SOURCES, _make_collection

pytestmark = pytest.mark.rayon

# First point count that runs through Rayon, mirroring `src/execution.rs`
# (which stores `first_parallel - 1` because dispatch uses `len > threshold`).
FIRST_PARALLEL = {
    "CylinderMagnet": 768,
    "CuboidMagnet": 160,
    "Dipole": 24_576,
    "SphereMagnet": 24_576,
    "TriangleMagnet": 819,
    "TetrahedronMagnet": 160,
    "MeshMagnet": 16,
    "CircularCurrent": 1_024,
    "PathCurrent": 410,
    "SheetCurrent": 48,
    "TriangleCurrent": 256,
}

LARGE = 100_000


def _cases():
    for source, first_parallel in FIRST_PARALLEL.items():
        yield pytest.param(source, first_parallel - 1, id=f"{source}-last_serial")
        yield pytest.param(source, first_parallel, id=f"{source}-first_parallel")
        yield pytest.param(source, LARGE, id=f"{source}-large")


@pytest.mark.parametrize(("source", "n_points"), list(_cases()))
def test_parallel_compute_B(benchmark, source, n_points):
    obj = SOURCES[source]()
    observers = make_observers(n_points)
    result = benchmark(obj.compute_B, observers)
    assert result.shape == (n_points, 3)


@pytest.mark.parametrize("n_magnets", [2, 20])
def test_parallel_collection_compute_B(benchmark, n_magnets):
    collection = _make_collection(n_magnets)
    observers = make_observers(LARGE)
    result = benchmark(collection.compute_B, observers)
    assert result.shape == (LARGE, 3)
