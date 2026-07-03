"""
Current sources for PyMagba.
"""

from .pymagba_binding import (
    CircularCurrent as _CircularCurrent,
    PathCurrent as _PathCurrent,
)

__all__ = [
    "CircularCurrent",
    "PathCurrent",
]


class CircularCurrent(_CircularCurrent):
    """
    Physical representation of a circular current loop.

    Args:
        position (array_like, optional): Center of the loop [x, y, z] in meters.
            Defaults to [0, 0, 0].
        orientation (Rotation, optional): Orientation of the loop.
            Defaults to identity.
        diameter (float, optional): Diameter of the loop in meters.
            Defaults to 1.0.
        current (float, optional): Current in the loop in Amperes.
            Defaults to 1.0.
    """

class PathCurrent(_PathCurrent):
    """
    A current path modeling a sequence of straight current-carrying wire segments.

    Args:
        position (array_like, optional): Base position of the path [x, y, z] in meters.
            Defaults to [0, 0, 0].
        orientation (Rotation, optional): Orientation of the path.
            Defaults to identity.
        current (float, optional): Current in the path in Amperes.
            Defaults to 1.0.
        vertices (array_like, optional): The vertices of the path as an Nx3 array.
            Defaults to an empty list.
    """
