# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>


from pathlib import Path
from typing import Any

import magpylib as magpy
import numpy as np
from scipy.spatial.transform import Rotation
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)

from pymagba.sources import CylinderMagnet, SourceCollection
from pymagba.util import FloatArray


def generate_collection_cylinder_expected():
    magnet = magpy.Collection(
        [
            magpy.magnet.Cylinder(
                position,
                orientation,
                (
                    CollectionCylinderTestData.CYLINDER_RADIUS * 2,
                    CollectionCylinderTestData.CYLINDER_HEIGHT,
                ),
                CollectionCylinderTestData.CYLINDER_POL,
            )
            for position, orientation in zip(
                CollectionCylinderTestData.CYLINDER_POSITIONS,
                CollectionCylinderTestData.CYLINDER_ORIENTATIONS,
            )
        ]
    )
    generate_general_expected_results(magnet, CollectionCylinderTestData)


def test_collection_cylinder() -> None:
    magnets = SourceCollection(
        [
            CylinderMagnet(
                position,
                orientation,
                CollectionCylinderTestData.CYLINDER_RADIUS,
                CollectionCylinderTestData.CYLINDER_HEIGHT,
                CollectionCylinderTestData.CYLINDER_POL,
            )
            for position, orientation in zip(
                CollectionCylinderTestData.CYLINDER_POSITIONS,
                CollectionCylinderTestData.CYLINDER_ORIENTATIONS,
            )
        ]
    )
    run_test_general(magnets, CollectionCylinderTestData)


class CollectionCylinderTestData(TestData):
    @staticmethod
    def get_points() -> FloatArray:
        return get_small_grid()

    CYLINDER_POSITIONS = np.array(
        [
            [0.009389999999999999, 0.0, -0.006],
            [0.0029016695771807563, 0.008930420688011491, -0.006],
            [-0.007596669577180755, 0.005519303519026323, -0.006],
            [-0.007596669577180757, -0.005519303519026321, -0.006],
            [0.002901669577180754, -0.008930420688011491, -0.006],
        ]
    )

    CYLINDER_ORIENTATIONS = Rotation.from_quat(
        np.array(
            [
                [
                    0.5,
                    0.4999999999999999,
                    0.5,
                    0.5000000000000001,
                ],
                [
                    -0.6984011233337103,
                    0.11061587104123723,
                    0.11061587104123725,
                    -0.6984011233337104,
                ],
                [
                    -0.32101976096010304,
                    0.6300367553350505,
                    0.6300367553350507,
                    -0.3210197609601031,
                ],
                [
                    -0.32101976096010315,
                    -0.6300367553350504,
                    -0.6300367553350504,
                    -0.3210197609601032,
                ],
                [
                    -0.6984011233337103,
                    -0.11061587104123705,
                    -0.11061587104123706,
                    -0.6984011233337104,
                ],
            ]
        )
    )

    CYLINDER_RADIUS = 1.5e-3
    CYLINDER_HEIGHT = 4e-3
    CYLINDER_POL = np.array((0, 0, 925e-3))

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("collection/collection-cylinder-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (0.05, 0.1, 0.15),
            Rotation.from_rotvec([np.pi / 7, np.pi / 6, np.pi / 5]),
            (-0.03, -0.02, -0.01),
            Rotation.from_rotvec([-np.pi / 3, -np.pi / 2, np.pi / 1]),
        ]


if __name__ == "__main__":
    # generate_collection_cylinder_expected()
    pass
