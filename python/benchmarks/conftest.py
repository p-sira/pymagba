# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Shared fixtures for the CodSpeed (pytest-codspeed) benchmarks."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

POSITION = (0.1, 0.2, 0.3)
ORIENTATION = Rotation.from_rotvec([np.pi / 7, np.pi / 6, np.pi / 5])

TETRA_VERTICES = np.array(
    [
        [-0.1, -0.1, -0.1],
        [0.1, -0.1, -0.1],
        [0.0, 0.1, -0.1],
        [0.0, 0.0, 0.1],
    ]
)
TETRA_FACES = np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]])


def make_grid(n_per_axis: int) -> np.ndarray:
    """Regular grid of observer points in a [-0.5, 0.5]^3 cube."""
    linsp = np.linspace(-0.5, 0.5, n_per_axis)
    mesh = np.meshgrid(linsp, linsp, linsp)
    return np.column_stack([m.flatten() for m in mesh])


def make_observers(n: int) -> np.ndarray:
    """Pseudo-random observer points, reproducible across runs."""
    rng = np.random.default_rng(42)
    return rng.uniform(-0.5, 0.5, size=(n, 3))


@pytest.fixture(scope="session")
def points() -> np.ndarray:
    """1000 observer points (10x10x10 grid), matching the ASV benchmarks."""
    return make_grid(10)
