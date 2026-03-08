# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np


class PoseMixin:
    """Mixin for objects with position and orientation."""

    @property
    def position(self):
        """Position of the object [x, y, z] in meters."""
        return super().position

    @position.setter
    def position(self, value):
        super().set_position(value)

    @property
    def orientation(self):
        """Orientation as a scipy.spatial.transform.Rotation object."""
        return super().orientation

    @orientation.setter
    def orientation(self, value):
        super().set_orientation(value)

    def translate(self, translation):
        """Translate the object by a displacement vector.

        Args:
            translation (ArrayLike3): Displacement [dx, dy, dz] in meters.
        """
        return super().translate(translation)

    def rotate(self, rot):
        """Rotate the object about its own origin.

        Args:
            rot (Rotation): Rotation to apply. Can be a scipy.spatial.transform.Rotation
                object or a unit quaternion as a list.
        """
        return super().rotate(rot)

    def rotate_anchor(self, rot, anchor):
        """Rotate the object about an arbitrary anchor point.

        Args:
            rot (Rotation): Rotation to apply.
            anchor (ArrayLike3): Anchor point [x, y, z] in meters about which to rotate.
        """
        return super().rotate_anchor(rot, anchor)


class SourceMixin(PoseMixin):
    """Mixin for magnetic sources."""

    def compute_B(self, points):
        """Compute the magnetic flux density B at a batch of observer points.

        Args:
            points (numpy.ndarray): Array of shape (N, 3) containing the observer
                positions [x, y, z] in meters.

        Returns:
            numpy.ndarray: Array of shape (N, 3) with the [Bx, By, Bz] field
                vectors in Tesla at each observer point.
        """
        return super().compute_B(points)


class SensorMixin(PoseMixin):
    """Mixin for magnetic sensors."""

    pass
