# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
from magpylib.magnet import Cylinder
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.sources import CylinderMagnet
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.util import FloatArray


class SmallCylinderTestData(TestData):
    RADIUS = 3e-3
    HEIGHT = 5e-3
    POL = np.array((1, 2, 3))

    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("cylinder/small-cylinder-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (-0.02, 0.04, -0.06),
            Rotation.from_rotvec([np.pi / 15, -np.pi / 8, np.pi / 3]),
            (-0.02, -0.08, 0.2),
            Rotation.from_rotvec([-np.pi / 1, -np.pi / 2, np.pi / 3]),
        ]


def generate_small_cylinder_expected():
    magnet = Cylinder(
        dimension=(SmallCylinderTestData.RADIUS * 2, SmallCylinderTestData.HEIGHT),
        polarization=SmallCylinderTestData.POL,
    )
    generate_general_expected_results(magnet, SmallCylinderTestData)


def test_small_cylinder():
    magnet = CylinderMagnet(
        radius=SmallCylinderTestData.RADIUS,
        height=SmallCylinderTestData.HEIGHT,
        polarization=SmallCylinderTestData.POL,
    )
    run_test_general(magnet, SmallCylinderTestData, rtol=5e-6)


if __name__ == "__main__":
    # generate_small_cylinder_expected()
    pass
