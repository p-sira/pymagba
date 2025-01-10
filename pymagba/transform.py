# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation


class Transform:
    def __init__(
        self,
        position: NDArray,
        orientation: Rotation,
    ) -> None:
        self._position = position
        self._orientation = orientation

    @property
    def position(self) -> NDArray:
        return self._position

    @position.setter
    def position(self, new_position: NDArray) -> None:
        self._position = new_position

    @property
    def orientation(self) -> Rotation:
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Rotation) -> None:
        self._orientation = new_orientation

    def move(self, translation: NDArray) -> None:
        self._position += translation

    def rotate(self, rotation: Rotation) -> None:
        self._orientation.apply(rotation)