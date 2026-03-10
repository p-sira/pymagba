# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from pathlib import Path
from typing import Any
import magpylib as magpy
import numpy as np
from scipy.spatial.transform import Rotation
from pymagba.magnets import Dipole
from tests.testing_util import (
    TestData,
    generate_general_expected_results,
    get_small_grid,
    run_test_general,
)
from pymagba.utils import FloatArray


class DipoleTestData(TestData):
    MOMENT = np.array((0.123, 0.456, 0.789))

    @staticmethod
    def get_points() -> FloatArray:
        # Dipole has singularity at origin, but get_small_grid is likely fine
        return get_small_grid()

    @staticmethod
    def get_test_data_paths() -> list[Path]:
        return TestData._get_test_data_paths("dipole/small-dipole-data")

    @staticmethod
    def get_test_params() -> list[Any]:
        return [
            (-0.02, 0.04, -0.06),
            Rotation.from_rotvec([np.pi / 15, -np.pi / 8, np.pi / 3]),
            (-0.02, -0.08, 0.2),
            Rotation.from_rotvec([-np.pi / 1, -np.pi / 2, np.pi / 3]),
        ]


def generate_dipole_expected():
    magnet = magpy.misc.Dipole(
        moment=DipoleTestData.MOMENT,
    )
    generate_general_expected_results(magnet, DipoleTestData)


def test_dipole():
    magnet = Dipole(
        moment=DipoleTestData.MOMENT,
    )
    run_test_general(magnet, DipoleTestData, rtol=1e-6, atol=1e-14)


if __name__ == "__main__":
    generate_dipole_expected()
