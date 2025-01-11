# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

# type: ignore

from warnings import warn

import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial.transform import Rotation

import pymagba.pymagba_binding as pmb
from pymagba.util import FloatArray, float_array, wrap_vectors2d

# Important! All numpy arguments must be explicitly casted as float!
# This is because numpy seems to keep data as int if possible.
# Normally, they are casted (promoted) automatically during operations.
# But this is not the cast in rust where PyArray is statically typed.
# Example: np.array([1, 2, 3]) -> Error!, Do np.array([1, 2, 3], dtype=float)
# Example: np.zeros(3) -> Error!, Do np.zeros(3, dtype=float)


def cyl_B(
    points: ArrayLike,
    position: ArrayLike,
    orientation: Rotation,
    radius: float,
    height: float,
    polarization: ArrayLike,
) -> FloatArray:
    points = wrap_vectors2d(points)
    position = tuple(float_array(position))
    orientation = orientation.as_quat(scalar_first=True)
    polarization = tuple(float_array(polarization))

    try:
        return pmb.field.cyl_B(
            points, position, orientation, radius, height, polarization
        )
    except RuntimeError as e:
        warn(e)
        return np.zeros(points.shape, dtype=float)


def sum_multiple_cyl_B(
    points: ArrayLike,
    positions: ArrayLike,
    orientations: Rotation,
    radii: ArrayLike,
    heights: ArrayLike,
    polarizations: ArrayLike,
) -> FloatArray:
    points = wrap_vectors2d(points)
    positions = wrap_vectors2d(positions)
    orientations = np.array(
        [orientation.as_quat(scalar_first=True) for orientation in orientations]
    )
    radii = float_array(radii)
    heights = float_array(heights)
    polarizations = wrap_vectors2d(polarizations)
    try:
        return pmb.field.sum_multiple_cyl_B(
            points, positions, orientations, radii, heights, polarizations
        )
    except RuntimeError as e:
        warn(e)
        return np.zeros(points.shape, dtype=float)
