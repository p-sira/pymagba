# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from numpy.typing import NDArray


def wrap_points2d(points: NDArray) -> NDArray:
    if len(points.shape) == 1:
        # It is a single point, wrap it once
        points = np.array([points])

    if len(points.shape) == 2:
        # It is an array of points
        return points

    raise ValueError(
        "points argument must be an array of point (x,y,z) or an array of points (Nx3)."
    )
