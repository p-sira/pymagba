# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
from magpylib.magnet import Cuboid
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.magnets import CuboidMagnet
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.utils import FloatArray


class CuboidTestData(TestData):
    DIMENSIONS = np.array((0.01, 0.02, 0.03))
    POL = np.array((1.0, 2.0, 3.0))

    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("cuboid/small-cuboid-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (-0.02, 0.04, -0.06),
            Rotation.from_rotvec([np.pi / 15, -np.pi / 8, np.pi / 3]),
            (-0.02, -0.08, 0.2),
            Rotation.from_rotvec([-np.pi / 1, -np.pi / 2, np.pi / 3]),
        ]


def generate_cuboid_expected():
    magnet = Cuboid(
        dimension=CuboidTestData.DIMENSIONS,
        polarization=CuboidTestData.POL,
    )
    generate_general_expected_results(magnet, CuboidTestData)


def test_cuboid():
    magnet = CuboidMagnet(
        dimensions=CuboidTestData.DIMENSIONS,
        polarization=CuboidTestData.POL,
    )
    run_test_general(magnet, CuboidTestData, rtol=1e-6, atol=1e-14)


if __name__ == "__main__":
    generate_cuboid_expected()
