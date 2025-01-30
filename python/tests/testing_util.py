# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
from numpy.testing import assert_allclose

from pymagba.util import FloatArray


class TestData(ABC):
    @staticmethod
    @abstractmethod
    def get_points() -> FloatArray:
        pass

    @staticmethod
    def _get_test_data_paths(data_path_str: str) -> list[Path]:
        """This function helps with numbering.
        Path is relative to python/tests/data"""
        return [
            Path(f"python/tests/data/") / (data_path_str + f"{i}.npy") for i in range(5)
        ]

    @staticmethod
    @abstractmethod
    def get_test_data_paths() -> list[Path]:
        """Get actual data paths."""
        pass

    @staticmethod
    @abstractmethod
    def get_test_params() -> list[Any]:
        """List of params for:
        - magnets.position
        - magnets.orientation
        - magnets.move
        - magnets.rotate
        """
        pass


def generate_general_expected_results(magnet, test_data_class: type[TestData]) -> None:
    """Generate expected test results:
    - Starting field
    - Setting position
    - Setting orientation
    - Moving
    - Rotating"""
    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    np.save(data_paths[0], magnet.getB(points))

    magnet.position = test_params[0]
    np.save(data_paths[1], magnet.getB(points))

    magnet.orientation = test_params[1]
    np.save(data_paths[2], magnet.getB(points))

    magnet.move(test_params[2])
    np.save(data_paths[3], magnet.getB(points))

    magnet.rotate(test_params[3])
    np.save(data_paths[4], magnet.getB(points))


def run_test_general(
    magnet, test_data_class: type[TestData], rtol=1e-6, atol=0
) -> None:
    """Perform test against expected test results:
    - Starting field
    - Setting position
    - Setting orientation
    - Moving
    - Rotating"""
    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    assert_allclose(magnet.get_B(points), np.load(data_paths[0]), rtol, atol)

    magnet.position = test_params[0]
    assert_allclose(magnet.get_B(points), np.load(data_paths[1]), rtol, atol)

    magnet.orientation = test_params[1]
    assert_allclose(magnet.get_B(points), np.load(data_paths[2]), rtol, atol)

    magnet.move(test_params[2])
    assert_allclose(magnet.get_B(points), np.load(data_paths[3]), rtol, atol)

    magnet.rotate(test_params[3])
    assert_allclose(magnet.get_B(points), np.load(data_paths[4]), rtol, atol)


def generate_grid(bounds: FloatArray, N: Iterable) -> FloatArray:
    linsp = [np.linspace(bounds[i, 0], bounds[i, 1], n) for i, n in enumerate(N)]
    mesh = np.meshgrid(*linsp)
    return np.column_stack([m.flatten() for m in mesh])


def generate_small_grid() -> None:
    path = Path("python/tests/data/small-grid.npy")
    bounds = np.array([[-0.25, 0.25]] * 3)
    N = [20] * 3
    points = generate_grid(bounds, N)
    np.save(path, points)


def get_small_grid() -> FloatArray:
    path = Path("python/tests/data/small-grid.npy")
    return np.load(path)


if __name__ == "__main__":
    # generate_small_grid()
    pass
