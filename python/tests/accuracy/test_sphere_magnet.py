# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
from magpylib.magnet import Sphere
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.magnets import SphereMagnet
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.utils import FloatArray


class SphereMagnetTestData(TestData):
    DIAMETER = 0.025
    POL = np.array((0.5, -1.2, 0.8))

    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("sphere/small-sphere-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (0.01, -0.03, 0.05),
            Rotation.from_rotvec([np.pi / 10, np.pi / 4, -np.pi / 6]),
            (-0.05, 0.02, -0.1),
            Rotation.from_rotvec([np.pi / 3, -np.pi / 2, np.pi / 8]),
        ]


def generate_sphere_expected():
    magnet = Sphere(
        diameter=SphereMagnetTestData.DIAMETER,
        polarization=SphereMagnetTestData.POL,
    )
    generate_general_expected_results(magnet, SphereMagnetTestData)


def test_sphere_magnet():
    magnet = SphereMagnet(
        diameter=SphereMagnetTestData.DIAMETER,
        polarization=SphereMagnetTestData.POL,
    )
    run_test_general(magnet, SphereMagnetTestData, rtol=1e-6, atol=1e-14)


if __name__ == "__main__":
    generate_sphere_expected()
