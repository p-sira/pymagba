# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial.transform import Rotation

from pymagba.fields import _fields
from pymagba.transform import Transform
from pymagba.util import FloatArray, float_array, wrap_vectors2d


# This can use type StrEnum on Python 3.11
class SourceType(str, Enum):
    COLLECTION = "SourceCollection"
    CYLINDER = "CylinderMagnet"


def _collection_get_B(
    points: FloatArray, sources_dict: dict[SourceType, dict]
) -> FloatArray:
    B_net = np.zeros((len(points), 3), dtype=float)
    for source_type, source_properties in sources_dict.items():
        B_net += COLLECTION_FIELD_FUNC[source_type](
            points,
            source_properties["position"],
            source_properties["orientation"],
            *[source_properties[param] for param in FIELD_PARAMS[source_type]],
        )

    return B_net


# Parameter of the source type used in field calculation. Position and orientation
# are implied as the second and third parameters. The first parameter of the field
# functions are points (observer position).
FIELD_PARAMS: dict[SourceType, tuple[str, ...]] = {
    SourceType.COLLECTION: ("sources",),
    SourceType.CYLINDER: ("radius", "height", "polarization"),
}

COLLECTION_FIELD_FUNC = {
    SourceType.COLLECTION: _collection_get_B,
    SourceType.CYLINDER: _fields.sum_multiple_cyl_B,
}


class Source(ABC, Transform):
    def __init__(
        self,
        source_type: SourceType,
        position: ArrayLike,
        orientation: Rotation,
    ) -> None:
        self._source_type = source_type
        super().__init__(position, orientation)

    @abstractmethod
    def get_B(self, points: ArrayLike) -> FloatArray:
        raise NotImplementedError


class SourceCollection(Source):
    def __init__(
        self,
        sources: Iterable[Source] = [],
        position: ArrayLike = (0, 0, 0),
        orientation: Rotation = Rotation.identity(),
    ) -> None:
        self._sources: dict[SourceType, dict[str, Any]] = {}
        self._n_sources = 0
        self.add_sources(sources)

        super().__init__(SourceType.COLLECTION, position, orientation)

    @property
    def position(self) -> FloatArray:
        return self._position

    @position.setter
    def position(self, new_position: ArrayLike) -> None:
        new_position = float_array(new_position)
        translation = new_position - self._position
        self._move_children(translation)
        self._position = new_position

    @property
    def orientation(self) -> Rotation:
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Rotation) -> None:
        rotation = new_orientation * self._orientation.inv()
        self._rotate_children(rotation)
        self._orientation = new_orientation

    def _move_children(self, translation: NDArray) -> None:
        for source_properties in self._sources.values():
            source_properties["position"] += translation

    def _rotate_children(self, rotation: Rotation) -> None:
        for source_params in self._sources.values():
            # Calculate new positions
            source_params["position"] -= self._position
            source_params["position"] = rotation.apply(source_params["position"])
            source_params["position"] += self._position

            # Rotate to new orientations
            source_params["orientation"] = rotation * source_params["orientation"]

    def move(self, translation: ArrayLike) -> None:
        translation = float_array(translation)
        self._move_children(translation)
        self._position += translation

    def rotate(self, rotation: Rotation) -> None:
        self._rotate_children(rotation)
        self._orientation = rotation * self._orientation

    def add_sources(self, sources: Iterable[Source]) -> None:
        # For every new source
        for x, source in enumerate(sources):
            i = x + self._n_sources  # Assign index in the collection

            type_group = self._sources.setdefault(source._source_type, {})

            #
            # Index, position, and orientation
            #
            type_group.setdefault("index", [])
            type_group.setdefault("position", [])
            type_group.setdefault("orientation", [])

            type_group["position"] = list(type_group["position"])
            type_group["orientation"] = list(type_group["orientation"])

            type_group["index"].append(i)
            type_group["position"].append(source.position)
            type_group["orientation"].append(source.orientation.as_quat())

            #
            # Other field parameters
            #
            for param in FIELD_PARAMS[source._source_type]:
                type_group.setdefault(
                    param, []
                )  # Defaults to empty list if key not found
                type_group[param] = list(
                    type_group[param]
                )  # Convert the parameter field to list
                type_group[param].append(
                    getattr(source, param)
                )  # Add the source parameter

        # Loop through the sources dict again to turn some parameters to nparray
        for source_type, source_type_params in self._sources.items():
            source_type_params["position"] = np.array(source_type_params["position"])
            source_type_params["orientation"] = Rotation.from_quat(
                source_type_params["orientation"]
            )
            for param in FIELD_PARAMS[source_type]:
                source_type_params[param] = np.array(source_type_params[param])

    def get_B(self, points: ArrayLike) -> FloatArray:
        return _collection_get_B(wrap_vectors2d(points), self._sources)


class CylinderMagnet(Source):
    def __init__(
        self,
        position: ArrayLike = (0, 0, 0),
        orientation: Rotation = Rotation.identity(),
        radius: float = 1,
        height: float = 1,
        polarization: ArrayLike = (0, 0, 1),
    ) -> None:
        self.radius = radius
        self.height = height
        self.polarization = polarization

        super().__init__(SourceType.CYLINDER, position, orientation)

    def get_B(self, points: ArrayLike):
        return _fields.cyl_B(
            wrap_vectors2d(points),
            self.position,
            self.orientation,
            self.radius,
            self.height,
            self.polarization,
        )
