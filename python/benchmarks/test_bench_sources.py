# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Benchmarks for the object-oriented source API (magnets and currents)."""

import numpy as np
import pytest
from pymagba.currents import CircularCurrent, PathCurrent, SheetCurrent, TriangleCurrent
from pymagba.magnets import (
    CuboidMagnet,
    CylinderMagnet,
    Dipole,
    MeshMagnet,
    SourceCollection,
    SphereMagnet,
    TetrahedronMagnet,
    TriangleMagnet,
)

from .conftest import ORIENTATION, POSITION, TETRA_FACES, TETRA_VERTICES

POLARIZATION = np.array((1.0, 2.0, 3.0))

SOURCES = {
    "CylinderMagnet": lambda: CylinderMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        diameter=0.1,
        height=0.2,
        polarization=POLARIZATION,
    ),
    "CuboidMagnet": lambda: CuboidMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        dimensions=np.array((0.1, 0.2, 0.3)),
        polarization=POLARIZATION,
    ),
    "Dipole": lambda: Dipole(
        position=POSITION, orientation=ORIENTATION, moment=POLARIZATION
    ),
    "SphereMagnet": lambda: SphereMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        diameter=0.1,
        polarization=POLARIZATION,
    ),
    "TriangleMagnet": lambda: TriangleMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, 0.1], [0.0, 0.2, 0.0]],
        polarization=POLARIZATION,
    ),
    "TetrahedronMagnet": lambda: TetrahedronMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        vertices=TETRA_VERTICES.tolist(),
        polarization=POLARIZATION,
    ),
    "MeshMagnet": lambda: MeshMagnet(
        position=POSITION,
        orientation=ORIENTATION,
        vertices=TETRA_VERTICES,
        faces=TETRA_FACES,
        polarization=POLARIZATION,
    ),
    "CircularCurrent": lambda: CircularCurrent(
        position=POSITION, orientation=ORIENTATION, diameter=1.0, current=1.0
    ),
    "PathCurrent": lambda: PathCurrent(
        position=POSITION,
        orientation=ORIENTATION,
        current=100.0,
        vertices=TETRA_VERTICES,
    ),
    "SheetCurrent": lambda: SheetCurrent(
        position=POSITION,
        orientation=ORIENTATION,
        vertices=TETRA_VERTICES,
        faces=TETRA_FACES,
        current_densities=np.tile(POLARIZATION, (4, 1)),
    ),
    "TriangleCurrent": lambda: TriangleCurrent(
        position=POSITION,
        orientation=ORIENTATION,
        vertices=TETRA_VERTICES[:3].tolist(),
        current_density=POLARIZATION,
    ),
}


@pytest.mark.parametrize("source", list(SOURCES))
def test_compute_B(benchmark, source, points):
    obj = SOURCES[source]()
    result = benchmark(obj.compute_B, points)
    assert result.shape == (len(points), 3)


@pytest.mark.parametrize("source", list(SOURCES))
def test_create(benchmark, source):
    benchmark(SOURCES[source])


def _make_collection(n_magnets: int) -> SourceCollection:
    magnets = []
    for i in range(n_magnets):
        x = 0.02 * (i - n_magnets / 2)
        if i % 2 == 0:
            magnets.append(
                CylinderMagnet(
                    position=(x, 0.0, 0.0),
                    diameter=0.01,
                    height=0.02,
                    polarization=(0.0, 0.0, 1.0),
                )
            )
        else:
            magnets.append(
                CuboidMagnet(
                    position=(x, 0.0, 0.0),
                    dimensions=(0.01, 0.01, 0.01),
                    polarization=(0.0, 0.0, -1.0),
                )
            )
    return SourceCollection(magnets)


@pytest.mark.parametrize("n_magnets", [2, 20])
def test_collection_compute_B(benchmark, n_magnets, points):
    collection = _make_collection(n_magnets)
    result = benchmark(collection.compute_B, points)
    assert result.shape == (len(points), 3)


def test_collection_create(benchmark):
    benchmark(_make_collection, 20)


def test_cylinder_translate_rotate(benchmark):
    magnet = SOURCES["CylinderMagnet"]()

    def move():
        for _ in range(100):
            magnet.translate((0.001, 0.0, 0.0))
            magnet.rotate(ORIENTATION)

    benchmark(move)


def test_collection_translate_rotate(benchmark):
    collection = _make_collection(20)

    def move():
        for _ in range(100):
            collection.translate((0.001, 0.0, 0.0))
            collection.rotate(ORIENTATION)

    benchmark(move)
