# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
from magpylib.current import Circle
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.currents import CircularCurrent
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.utils import FloatArray


class CircularCurrentTestData(TestData):
    DIAMETER = 0.015
    CURRENT = 2.5

    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("current/small-circular-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (-0.02, 0.04, -0.06),
            Rotation.from_rotvec([np.pi / 15, -np.pi / 8, np.pi / 3]),
            (-0.02, -0.08, 0.2),
            Rotation.from_rotvec([-np.pi / 1, -np.pi / 2, np.pi / 3]),
        ]


def generate_circular_expected():
    magnet = Circle(
        diameter=CircularCurrentTestData.DIAMETER,
        current=CircularCurrentTestData.CURRENT,
    )
    generate_general_expected_results(magnet, CircularCurrentTestData)


def test_circular_current():
    magnet = CircularCurrent(
        diameter=CircularCurrentTestData.DIAMETER,
        current=CircularCurrentTestData.CURRENT,
    )
    run_test_general(magnet, CircularCurrentTestData, rtol=1e-6, atol=1e-14)


if __name__ == "__main__":
    generate_circular_expected()
