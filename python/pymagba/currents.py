"""
Current sources for PyMagba.
"""

from .pymagba_binding import (
    CircularCurrent as _CircularCurrent,
    PathCurrent as _PathCurrent,
    TriangleCurrent as _TriangleCurrent,
    SheetCurrent as _SheetCurrent,
)

__all__ = [
    "CircularCurrent",
    "PathCurrent",
    "TriangleCurrent",
    "SheetCurrent",
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

class TriangleCurrent(_TriangleCurrent):
    """
    A single triangular current sheet with homogeneous surface current density.

    Args:
        position (array_like, optional): Base position of the triangle [x, y, z] in meters.
            Defaults to [0, 0, 0].
        orientation (Rotation, optional): Orientation of the triangle.
            Defaults to identity.
        current_density (array_like, optional): Current density vector [Jx, Jy, Jz] in A/m.
            Defaults to [0, 0, 0].
        vertices (array_like, optional): The 3 vertices of the triangle as a 3x3 array.
            Defaults to [[1, 0, 0], [0, 1, 0], [0, 0, 0]].
    """

class SheetCurrent(_SheetCurrent):
    """
    A meshed current sheet.

    Args:
        position (array_like, optional): Base position of the mesh [x, y, z] in meters.
            Defaults to [0, 0, 0].
        orientation (Rotation, optional): Orientation of the mesh.
            Defaults to identity.
        current_densities (array_like, optional): Current densities vectors for each face, 
            provided as an Mx3 array where M is the number of faces. Defaults to empty.
        vertices (array_like, optional): The vertices of the mesh as an Nx3 array.
            Defaults to empty.
        faces (array_like, optional): The faces of the mesh as an Mx3 array of indices.
            Defaults to empty.
    """

    @classmethod
    def from_stl(
        cls,
        path: str,
        position=None,
        orientation=None,
        current_densities=None,
    ) -> "SheetCurrent":
        """
        Creates a SheetCurrent from an STL file.

        Args:
            path (str): The path to the STL file.
            position (array_like, optional): Base position of the mesh [x, y, z] in meters.
                Defaults to [0, 0, 0].
            orientation (Rotation, optional): Orientation of the mesh.
                Defaults to identity.
            current_densities (array_like, optional): Current densities vectors for each face, 
                provided as an Mx3 array where M is the number of faces in the STL. Defaults to empty.

        Returns:
            SheetCurrent: A new SheetCurrent instance.
        """
        return super().from_stl(path, position, orientation, current_densities)  # type: ignore
