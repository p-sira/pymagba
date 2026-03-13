"""
Current sources for PyMagba.
"""

from .pymagba_binding import CircularCurrent as _CircularCurrent

__all__ = [
    "CircularCurrent",
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
