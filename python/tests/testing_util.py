# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from collections.abc import Iterable
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def generate_grid(bounds: NDArray, N: Iterable) -> NDArray:
    linsp = [np.linspace(bounds[i, 0], bounds[i, 1], n) for i, n in enumerate(N)]
    mesh = np.meshgrid(*linsp)
    return np.column_stack([m.flatten() for m in mesh])


def generate_small_grid() -> None:
    path = Path("python/tests/data/small-grid.npy")
    bounds = np.array([[-0.25, 0.25]] * 3)
    N = [20] * 3
    points = generate_grid(bounds, N)
    np.save(path, points)

def get_small_grid() -> NDArray:
    path = Path("python/tests/data/small-grid.npy")
    return np.load(path)

if __name__ == "__main__":
    # generate_small_grid()
    pass
