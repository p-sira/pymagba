# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from abc import ABC
from collections.abc import Iterable
from enum import StrEnum
from typing import cast
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation

from pymagba import field
from pymagba.transform import Transform
from pymagba.util import wrap_points2d


class SourceType(StrEnum):
    COLLECTION = "SourceCollection"
    CYLINDER = "CylinderMagnet"


class Source(ABC, Transform):
    def __init__(
        self,
        source_type: SourceType,
        field_params: list[str],
        position: NDArray,
        orientation: Rotation,
    ) -> None:
        self._source_type = source_type
        self._field_params = field_params
        super().__init__(position, orientation)

    @staticmethod
    def _B_func(points: NDArray) -> NDArray:
        raise NotImplementedError

    def get_B(self, points: NDArray) -> NDArray:
        return self._B_func(wrap_points2d(points))


class SourceCollection(Source):
    def __init__(
        self,
        sources: Iterable[Source] = [],
        position=np.zeros(3),
        orientation=Rotation.identity(),
    ) -> None:
        self.sources: dict[SourceType, dict[str, NDArray]] = {}
        self._add_sources(self.sources, sources)

        field_params = ["position", "orientation", "sources"]
        super().__init__(SourceType.COLLECTION, field_params, position, orientation)

    @property
    def position(self) -> NDArray:
        return self._position

    @position.setter
    def position(self, new_position) -> None:
        translation = new_position - self._position
        self._move_children(translation)
        self._position = new_position

    @property
    def orientation(self) -> NDArray:
        return self._orientation

    @orientation.setter
    def orientation(self, new_orientation: Rotation) -> None:
        rotation = new_orientation * self._orientation.inv()
        self._rotate_children(rotation)
        self._orientation = new_orientation

    def _move_children(self, translation: NDArray) -> None:
        for source_properties in self.sources.values():
            source_properties["position"] += translation

    def _rotate_children(self, rotation: Rotation) -> None:
        for source_properties in self.sources.values():
            # Calculate new positions
            source_properties["position"] -= self._position
            source_properties["position"] = rotation.apply(
                source_properties["position"]
            )
            source_properties["position"] += self._position

            # Rotate to new orientations
            source_properties["orientation"] = np.array(
                [
                    rotation * orientation
                    for orientation in source_properties["orientation"]
                ]
            )

    def move(self, translation: NDArray) -> None:
        self._move_children(translation)
        self._position += translation

    def rotate(self, rotation: NDArray) -> None:
        self._rotate_children(rotation)
        self._orientation = rotation * self._orientation

    @staticmethod
    def _add_sources(
        source_dict: dict[SourceType, dict[str, NDArray]], sources: Iterable[Source]
    ) -> None:
        new_sources_by_type: dict[SourceType, list[Source]] = {}
        # Sort new_sources into dict first, so the property of each SourceType and be
        # extracted at once, minimizing list conversion
        for source in sources:
            if source._source_type in new_sources_by_type:
                # SourceType entry found, add new item to list
                new_sources_by_type[source._source_type].append(source)
            else:
                # No entry yet, create new entry and fill with itself
                new_sources_by_type.update({source._source_type: [source]})

        for new_source_type, new_sources in new_sources_by_type.items():
            if not new_source_type in source_dict:
                source_dict[new_source_type] = {}

            type_entry = source_dict[new_source_type]
            for param in new_sources[0]._field_params:
                if param not in type_entry:
                    type_entry[param] = np.array(())

                new_params = [getattr(new_source, param) for new_source in new_sources]
                type_entry[param] = np.array(type_entry[param].tolist() + new_params) # type: ignore

    def get_B(self, points: NDArray) -> NDArray:
        points = wrap_points2d(points)
        B_net = np.zeros(points.shape)

        for source_type, sources in self.sources.items():
            match source_type:
                case SourceType.CYLINDER:
                    B_net += field.sum_multiple_cyl_B(
                        points,
                        np.array(sources["position"]),
                        np.array(sources["orientation"]),
                        np.array(sources["radius"]),
                        np.array(sources["height"]),
                        np.array(sources["polarization"]),
                    )
        return B_net


class CylinderMagnet(Source):
    def __init__(
        self,
        position: NDArray = np.zeros(3),
        orientation: Rotation = Rotation.identity(),
        radius: float = 1,
        height: float = 1,
        polarization: NDArray = np.array([0, 0, 1]),
    ) -> None:
        self.radius = radius
        self.height = height
        self.polarization = polarization

        field_params = ["position", "orientation", "radius", "height", "polarization"]
        self._B_func = lambda points: field.cyl_B(
            points,
            self.position,
            self.orientation,
            self.radius,
            self.height,
            self.polarization,
        )

        super().__init__(SourceType.CYLINDER, field_params, position, orientation)
