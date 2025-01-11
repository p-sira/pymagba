# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from numpy.typing import NDArray, ArrayLike

type FloatArray = NDArray[np.floating]


def wrap_vectors2d(array: ArrayLike) -> FloatArray:
    """Wrap array of vectors to 2D and cast to float, throws error when inappropriate shape is given

    Args:
        array (ArrayLike): Array of vector(s)

    Raises:
        ValueError: Inappropriate shape

    Returns:
        FloatArray: Array of vectors (Nx3)
    """
    array = np.array(array, dtype=float)

    if array.shape[-1] == 3:
        if len(array.shape) == 2:
            # It is an array of points
            return array

        if len(array.shape) == 1:
            # It is a single point, wrap it once
            return np.array([array], dtype=float)

    raise ValueError("inputs must have length of 3 or Nx3.")


def float_array(array: ArrayLike) -> FloatArray:
    return np.array(array, dtype=float)
