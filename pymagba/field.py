# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

# type: ignore

from warnings import warn
import pymagba_binding as pmb
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation


def cyl_B(
    points: NDArray,
    position: NDArray,
    orientation: Rotation,
    radius: float,
    height: float,
    polarization: NDArray,
) -> NDArray:
    position = tuple(position)
    orientation = tuple(orientation.as_quat(scalar_first=True))
    polarization = tuple(polarization)
    try:
        return pmb.field.cyl_b(
            points, position, orientation, radius, height, polarization
        )
    except RuntimeError as e:
        warn(e)
        return np.zeros(points.shape)


def sum_multiple_cyl_B(
    points: NDArray,
    positions: NDArray,
    orientations: Rotation,
    radii: NDArray,
    heights: NDArray,
    polarizations: NDArray,
) -> NDArray:
    orientations = np.array(
        [orientation.as_quat(scalar_first=True) for orientation in orientations]
    )
    try:
        return pmb.field.sum_multiple_cyl_b(
            points, positions, orientations, radii, heights, polarizations
        )
    except RuntimeError as e:
        warn(e)
        return np.zeros(points.shape)
