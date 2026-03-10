# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
from numpy.testing import assert_allclose

from pymagba.utils import FloatArray


class TestData(ABC):
    @staticmethod
    @abstractmethod
    def get_points() -> FloatArray:
        pass

    @staticmethod
    def _get_test_data_paths(data_path_str: str) -> list[Path]:
        """Helper to generate paths for numbered test data files.

        Args:
            data_path_str: Base name for the data files.

        Returns:
            Paths relative to python/tests/data.
        """
        return [
            Path(f"python/tests/data/") / (data_path_str + f"{i}.npy") for i in range(5)
        ]

    @staticmethod
    @abstractmethod
    def get_test_data_paths() -> list[Path]:
        """Get the paths to the actual test data files."""
        pass

    @staticmethod
    @abstractmethod
    def get_test_params() -> list[Any]:
        """List parameters used for pose transformation tests.

        Returns:
            Parameters for position, orientation, translation, and rotation.
        """
        pass


def _compute_field(obj, points: FloatArray) -> FloatArray:
    """Helper to call compute_B or getB depending on what is available."""
    if hasattr(obj, "compute_B"):
        return obj.compute_B(points)
    elif hasattr(obj, "getB"):
        return obj.getB(points)
    else:
        raise AttributeError(f"Object {obj} has neither compute_B nor getB method")


def _translate(obj, vec: FloatArray) -> None:
    """Helper to call translate or move depending on what is available."""
    if hasattr(obj, "translate"):
        obj.translate(vec)
    elif hasattr(obj, "move"):
        obj.move(vec)
    else:
        raise AttributeError(f"Object {obj} has neither translate nor move method")


def _rotate(obj, rot: Any) -> None:
    """Helper to call rotate with appropriate arguments."""
    if hasattr(obj, "rotate"):
        obj.rotate(rot)
    elif hasattr(obj, "rotate_from_quat"):
        # magpylib objects
        from scipy.spatial.transform import Rotation

        if isinstance(rot, Rotation):
            obj.rotate(rot)
        else:
            # Assume it might be something magpylib's rotate can handle,
            # but magpylib's .rotate() usually takes a Rotation object too.
            # Let's try raw rotate first.
            obj.rotate(rot)
    else:
        raise AttributeError(f"Object {obj} has no rotate method")


def generate_general_expected_results(magnet, test_data_class: type[TestData]) -> None:
    """Generate and save expected results for a general test suite.

    Args:
        magnet: The magnetic source object to test.
        test_data_class: Class providing test points and parameters.
    """
    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    np.save(data_paths[0], _compute_field(magnet, points))

    magnet.position = test_params[0]
    np.save(data_paths[1], _compute_field(magnet, points))

    magnet.orientation = test_params[1]
    np.save(data_paths[2], _compute_field(magnet, points))

    _translate(magnet, test_params[2])
    np.save(data_paths[3], _compute_field(magnet, points))

    _rotate(magnet, test_params[3])
    np.save(data_paths[4], _compute_field(magnet, points))


def run_test_general(
    magnet, test_data_class: type[TestData], rtol=1e-6, atol=0
) -> None:
    """Validate a source object against pre-generated expected results.

    Args:
        magnet: The magnetic source object to test.
        test_data_class: Class providing test points and parameters.
        rtol: Relative tolerance for comparisons.
        atol: Absolute tolerance for comparisons.
    """
    from scipy.spatial.transform import Rotation

    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    assert_allclose(_compute_field(magnet, points), np.load(data_paths[0]), rtol, atol)

    magnet.position = test_params[0]
    assert_allclose(_compute_field(magnet, points), np.load(data_paths[1]), rtol, atol)

    magnet.orientation = test_params[1]
    assert isinstance(magnet.orientation, Rotation)
    assert_allclose(_compute_field(magnet, points), np.load(data_paths[2]), rtol, atol)

    _translate(magnet, test_params[2])
    assert_allclose(_compute_field(magnet, points), np.load(data_paths[3]), rtol, atol)

    _rotate(magnet, test_params[3])
    assert isinstance(magnet.orientation, Rotation)
    assert_allclose(_compute_field(magnet, points), np.load(data_paths[4]), rtol, atol)


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
