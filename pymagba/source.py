# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from pymagba import field


class Source(ABC):
    def __init__(
        self,
        position: NDArray,
        orientation: Rotation,
    ) -> None:
        self.position = position
        self.orientation = orientation

    def move(self, translation: NDArray) -> None:
        self.position += translation

    def rotate(self, rotation: Rotation) -> None:
        self.orientation.apply(rotation)

    @abstractmethod
    def get_B(self, points: NDArray) -> NDArray:
        raise NotImplementedError


class CylinderMagnet(Source):
    def __init__(
        self,
        position: NDArray = np.zeros(3),
        orientation: Rotation = Rotation.identity(),
        radius: float = 1,
        height: float = 1,
        polarization: NDArray = np.array([0, 0, 1]),
    ) -> None:
        super().__init__(position, orientation)
        self.radius = radius
        self.height = height
        self.polarization = polarization

    def get_B(self, points: NDArray) -> None:
        if len(points.shape) == 1:
            # It is a single point, wrap it once
            points = np.array([points])

        if len(points.shape) == 2:
            # It is an array of points
            return field.cyl_b(
                points,
                self.position,
                self.orientation,
                self.radius,
                self.height,
                self.polarization,
            )

        raise ValueError(
            "points argument must be a vector (x,y,z) or an array of vector (Nx3)."
        )
