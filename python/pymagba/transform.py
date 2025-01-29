# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>
import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial.transform import Rotation

from pymagba.util import float_array, FloatArray


class Transform:
    def __init__(
        self,
        position: ArrayLike,
        orientation: Rotation,
    ) -> None:
        self._position = float_array(position)
        self._orientation = orientation

    @property
    def position(self) -> FloatArray:
        return self._position

    @position.setter
    def position(self, new_position: ArrayLike) -> None:
        self._position = float_array(new_position)

    @property
    def orientation(self) -> Rotation:
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Rotation) -> None:
        self._orientation = new_orientation

    def move(self, translation: ArrayLike) -> None:
        self._position += float_array(translation)

    def rotate(self, rotation: Rotation) -> None:
        self._orientation = rotation * self._orientation
