# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>


from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import magpylib as magpy
import numpy as np
from numpy.testing import assert_allclose
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation
from tests.testing_util import get_small_grid

from pymagba.sources import CylinderMagnet, SourceCollection


class CollectionTestData(ABC):
    @staticmethod
    @abstractmethod
    def get_points() -> NDArray:
        pass

    @staticmethod
    def _get_test_data_paths(data_file_name: str) -> list[Path]:
        """This function helps with numbering."""
        return [
            Path(f"python/tests/data/collection/") / (data_file_name + f"{i}.npy")
            for i in range(5)
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


def _generate_collection_general_expected(
    magnets: list, test_data_class: type[CollectionTestData]
) -> None:
    collection = magpy.Collection(magnets)
    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    # Get starting field
    np.save(data_paths[0], collection.getB(points))

    # Set parent position
    collection.position = test_params[0]
    np.save(data_paths[1], collection.getB(points))

    # Set parent orientation
    collection.orientation = test_params[1]
    np.save(data_paths[2], collection.getB(points))

    # Move parent
    collection.move(test_params[2])
    np.save(data_paths[3], collection.getB(points))

    # Rotate parent
    collection.rotate(test_params[3])
    np.save(data_paths[4], collection.getB(points))


def generate_collection_cylinder_expected():
    magnets = [
        magpy.magnet.Cylinder(
            position,
            orientation,
            (CylinderTestData.CYLINDER_RADIUS * 2, CylinderTestData.CYLINDER_HEIGHT),
            CylinderTestData.CYLINDER_POL,
        )
        for position, orientation in zip(
            CylinderTestData.CYLINDER_POSITIONS, CylinderTestData.CYLINDER_ORIENTATIONS
        )
    ]
    _generate_collection_general_expected(magnets, CylinderTestData)


def _test_collection_general(
    magnets: list, test_data_class: type[CollectionTestData]
) -> None:
    collection = SourceCollection(magnets)
    points = test_data_class.get_points()
    data_paths = test_data_class.get_test_data_paths()
    test_params = test_data_class.get_test_params()

    # Get starting field
    assert_allclose(collection.get_B(points), np.load(data_paths[0]))

    # Set parent position
    collection.position = test_params[0]
    assert_allclose(collection.get_B(points), np.load(data_paths[1]))

    # Set parent orientation
    collection.orientation = test_params[1]
    assert_allclose(collection.get_B(points), np.load(data_paths[2]))

    # Move parent
    collection.move(test_params[2])
    assert_allclose(collection.get_B(points), np.load(data_paths[3]))

    # Rotate parent
    collection.rotate(test_params[3])
    assert_allclose(collection.get_B(points), np.load(data_paths[4]))


def test_collection_cylinder() -> None:
    magnets = [
        CylinderMagnet(
            position,
            orientation,
            CylinderTestData.CYLINDER_RADIUS,
            CylinderTestData.CYLINDER_HEIGHT,
            CylinderTestData.CYLINDER_POL,
        )
        for position, orientation in zip(
            CylinderTestData.CYLINDER_POSITIONS, CylinderTestData.CYLINDER_ORIENTATIONS
        )
    ]
    _test_collection_general(magnets, CylinderTestData)


class CylinderTestData(CollectionTestData):
    @staticmethod
    def get_points() -> NDArray:
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
        return CollectionTestData._get_test_data_paths("collection-cylinder-data")

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
