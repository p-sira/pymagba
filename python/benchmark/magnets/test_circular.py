# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pymagba.currents import CircularCurrent
from pymagba.utils import FloatArray
import magpylib as magpy
import numpy as np
import pytest
from pytest_benchmark.plugin import benchmark
from scipy.spatial.transform import Rotation


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
def magba_current() -> CircularCurrent:
    return CircularCurrent(
        position=(0, 0, 0),
        orientation=Rotation.identity(),
        diameter=0.2,
        current=10.0,
    )


@pytest.fixture(scope="function")
def magpy_current() -> magpy.current.Circle:
    return magpy.current.Circle(
        position=(0, 0, 0),
        orientation=Rotation.identity(),
        diameter=0.2,
        current=10.0,
    )


def compute_magba(current: CircularCurrent, observers: FloatArray):
    current.compute_B(observers)


def compute_magpy(current: magpy.current.Circle, observers: FloatArray):
    current.getB(observers)


def test_circular_magba(benchmark, magba_current, observers):
    benchmark(compute_magba, magba_current, observers)


def test_circular_magpy(benchmark, magpy_current, observers):
    benchmark(compute_magpy, magpy_current, observers)
