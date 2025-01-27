# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from magpylib.magnet import Cylinder
import numpy as np
import pytest
from pytest_benchmark.plugin import benchmark
from scipy.spatial.transform import Rotation

from pymagba.sources import CylinderMagnet
from pymagba.util import FloatArray


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
def magba_magnet() -> CylinderMagnet:
    return CylinderMagnet(
        position=(0, 0, 0),
        orientation=Rotation.identity(),
        radius=0.1,
        height=0.2,
        polarization=(1, 2, 3),
    )


@pytest.fixture(scope="function")
def magpy_magnet() -> Cylinder:
    return Cylinder(
        position=(0, 0, 0),
        orientation=Rotation.identity(),
        dimension=(0.2, 0.2),
        polarization=(1, 2, 3),
    )


def compute_magba(magnet: CylinderMagnet, observers: FloatArray):
    magnet.get_B(observers)


def compute_magpy(magnet: Cylinder, observers: FloatArray):
    magnet.getB(observers)


def test_cylinder_magba(benchmark, magba_magnet, observers):
    benchmark(compute_magba, magba_magnet, observers)


def test_cylinder_magpy(benchmark, magpy_magnet, observers):
    benchmark(compute_magpy, magpy_magnet, observers)


# pytest python/benchmark --benchmark-min-time 1 --benchmark-max-time 5 --benchmark-warmup true --benchmark-warmup-iterations 10
