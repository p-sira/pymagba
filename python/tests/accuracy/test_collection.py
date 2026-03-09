# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
import magpylib as magpy
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.utils import FloatArray


class CollectionTestData(TestData):
    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("collection/collection-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (-0.02, 0.04, -0.06),
            Rotation.from_rotvec([np.pi / 15, -np.pi / 8, np.pi / 3]),
            (-0.02, -0.08, 0.2),
            Rotation.from_rotvec([-np.pi / 1, -np.pi / 2, np.pi / 3]),
        ]


def generate_collection_expected():
    c1 = magpy.magnet.Cylinder(
        dimension=(0.01, 0.02),
        polarization=(1, 2, 3),
        position=(0.005, 0, 0),
    )
    c2 = magpy.magnet.Cuboid(
        dimension=(0.01, 0.01, 0.01),
        polarization=(0, 0, 1),
        position=(-0.005, 0, 0),
    )
    magnet = magpy.Collection(c1, c2)
    generate_general_expected_results(magnet, CollectionTestData)


def test_collection():
    m1 = CylinderMagnet(
        diameter=0.01,
        height=0.02,
        polarization=(1, 2, 3),
        position=(0.005, 0, 0),
    )
    m2 = CuboidMagnet(
        dimensions=(0.01, 0.01, 0.01),
        polarization=(0, 0, 1),
        position=(-0.005, 0, 0),
    )
    magnet = SourceCollection([m1, m2])
    run_test_general(magnet, CollectionTestData, rtol=1e-5, atol=1e-14)


if __name__ == "__main__":
    generate_collection_expected()
