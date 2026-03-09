# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import magpylib._src.fields.field_BH_circle
import numpy as np
import pytest
from pytest_benchmark.plugin import benchmark
from scipy.spatial.transform import Rotation

import pymagba.fields


@pytest.fixture(scope="function")
def magba_args():
    # points, position, orientation, diameter, current
    return (0, 0, 0), Rotation.identity(), 0.01, 1.0


@pytest.fixture(scope="function")
def magpy_args(observers):
    # diameter, current
    diameter = np.array([0.01] * len(observers))
    current = np.array([1.0] * len(observers))
    return diameter, current


@pytest.fixture(scope="session")
def observers():
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


def compute_magba(observers, args):
    pymagba.fields.circular_B(observers, *args)


def compute_magpy(observers, args):
    magpylib._src.fields.field_BH_circle._BHJM_circle("B", observers, *args)


def test_circular_field_magba(benchmark, observers, magba_args):
    benchmark(compute_magba, observers, magba_args)


def test_circular_field_magpy(benchmark, observers, magpy_args):
    benchmark(compute_magpy, observers, magpy_args)
