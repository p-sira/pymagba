# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import magpylib
from magpylib.magnet import Cylinder, Cuboid
import numpy as np
import pytest
from pytest_benchmark.plugin import benchmark
from scipy.spatial.transform import Rotation

from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection
from pymagba.utils import FloatArray


@pytest.fixture(scope="class")
def observers() -> FloatArray:
    N = 1000
    return np.array(
        [
            [-0.12788963, 0.14872334, -0.35838915],
            [-0.17319799, 0.39177646, 0.22413971],
            [-0.15831916, -0.39768996, 0.41800279],
            [-0.05762575, 0.19985373, 0.02645361],
            [0.19120126, -0.13021813, -0.21615004],
            [0.39272212, 0.36457661, -0.09758084],
            [-0.39270581, -0.19805643, 0.36988649],
            [0.28942161, 0.31003054, -0.29558298],
            [0.13083584, 0.31396182, -0.11231319],
            [-0.04097917, 0.43394138, -0.14109254],
        ]
        * N
    )


@pytest.fixture(scope="function")
def magba_collection() -> SourceCollection:
    m1 = CylinderMagnet(
        position=(0.005, 0.0, 0.0),
        diameter=0.01,
        height=0.02,
        polarization=(0.0, 0.0, 1.0),
    )
    m2 = CuboidMagnet(
        position=(-0.005, 0.0, 0.0),
        dimensions=(0.01, 0.01, 0.01),
        polarization=(0.0, 0.0, -1.0),
    )
    return SourceCollection([m1, m2])


@pytest.fixture(scope="function")
def magpy_collection() -> magpylib.Collection:
    m1 = Cylinder(
        position=(0.005, 0.0, 0.0),
        dimension=(0.01, 0.02),
        polarization=(0.0, 0.0, 1.0),
    )
    m2 = Cuboid(
        position=(-0.005, 0.0, 0.0),
        dimension=(0.01, 0.01, 0.01),
        polarization=(0.0, 0.0, -1.0),
    )
    return magpylib.Collection(m1, m2)


def compute_magba(collection: SourceCollection, observers: FloatArray):
    collection.compute_B(observers)


def compute_magpy(collection: magpylib.Collection, observers: FloatArray):
    collection.getB(observers)


def test_collection_magba(benchmark, magba_collection, observers):
    benchmark(compute_magba, magba_collection, observers)


def test_collection_magpy(benchmark, magpy_collection, observers):
    benchmark(compute_magpy, magpy_collection, observers)
