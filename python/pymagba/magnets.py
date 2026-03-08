# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

from .pymagba_binding import (
    CylinderMagnet as _CylinderMagnet,
    SourceCollection as _SourceCollection,
    CuboidMagnet as _CuboidMagnet,
    Dipole as _Dipole,
)

__all__ = ["CylinderMagnet", "SourceCollection", "CuboidMagnet", "Dipole"]


class CylinderMagnet(_CylinderMagnet):
    """Uniformly magnetized cylindrical magnet.

    All dimensions are in SI units (meters, Tesla).

    Args:

        position (ArrayLike3, optional): Center of the cylinder [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        diameter (float, optional): Cylinder diameter in meters. Must be positive.
            Defaults to 1.0.
        height (float, optional): Cylinder height in meters. Must be positive.
            Defaults to 1.0.
        polarization (ArrayLike3, optional): Remanence polarization vector [Bx, By, Bz]
            in Tesla. Defaults to [0.0, 0.0, 0.0].

    Examples:

        .. code-block:: python

            from pymagba.magnets import CylinderMagnet
            from scipy.spatial.transform import Rotation

            magnet = CylinderMagnet(
                position=[0.0, 0.0, 0.0],
                orientation=Rotation.from_euler('x', 90, degrees=True),
                diameter=0.01,
                height=0.02,
                polarization=[0.0, 0.0, 1.0],
            )

    References:
        Caciagli, Alessio, et al. "Exact Expression for the Magnetic Field of a Finite Cylinder
        with Arbitrary Uniform Magnetization." Journal of Magnetism and Magnetic Materials 456 (2018): 423-432.
        https://doi.org/10.1016/j.jmmm.2018.02.003

        Derby, Norman, and Stanislaw Olbert. "Cylindrical Magnets and Ideal Solenoids."
        American Journal of Physics 78, no. 3 (2010): 229-235.
        https://doi.org/10.1119/1.3256157
    """


class CuboidMagnet(_CuboidMagnet):
    """Uniformly magnetized cuboid magnet.

    All dimensions are in SI units (meters, Tesla).

    Args:

        position (ArrayLike3, optional): Center of the cuboid [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        dimensions (ArrayLike3, optional): Side lengths [dx, dy, dz] in meters.
            Defaults to [1.0, 1.0, 1.0].
        polarization (ArrayLike3, optional): Remanence polarization vector [Bx, By, Bz]
            in Tesla. Defaults to [0.0, 0.0, 0.0].

    Examples:

        .. code-block:: python

            from pymagba.magnets import CuboidMagnet
            from scipy.spatial.transform import Rotation

            magnet = CuboidMagnet(
                position=[0.0, 0.0, 0.0],
                orientation=Rotation.from_euler('z', 45, degrees=True),
                dimensions=[0.01, 0.01, 0.02],
                polarization=[0.0, 0.0, 1.0],
            )

    References:
        Ortner, Michael, and Lucas Gabriel Coliado Bandeira. "Magpylib: A Free Python Package
        for Magnetic Field Computation." SoftwareX 11 (2020): 100466.
        https://doi.org/10.1016/j.softx.2020.100466
    """


class Dipole(_Dipole):
    """Magnetic dipole source.

    Models a point magnetic dipole - a useful approximation for small magnets
    at distances much greater than their physical size.

    Args:

        position (ArrayLike3, optional): Position of the dipole [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        moment (ArrayLike3, optional): Magnetic dipole moment vector [mx, my, mz] in A·m².
            Defaults to [0.0, 0.0, 0.0].

    Examples:

        .. code-block:: python

            from pymagba.magnets import Dipole

            dipole = Dipole(
                position=[0.0, 0.0, 0.0],
                moment=[0.0, 0.0, 1.0],
            )

    References:
        Ortner, Michael, and Lucas Gabriel Coliado Bandeira. "Magpylib: A Free Python Package
        for Magnetic Field Computation." SoftwareX 11 (2020): 100466.
        https://doi.org/10.1016/j.softx.2020.100466
    """


class SourceCollection(_SourceCollection):
    """A group of magnetic sources that can be transformed and queried as a unit.

    SourceCollection wraps a SourceAssembly from Magba, combining multiple
    magnetic sources (CylinderMagnet, CuboidMagnet, or Dipole) into a single
    object with its own pose. Transformations applied to the collection move
    all child sources relative to the collection's reference frame.

    Args:
    
        sources (list[Source], optional): Iterable of magnetic sources to include.
            Each element must be a CylinderMagnet, CuboidMagnet, or Dipole.
            Defaults to None.

    Examples:

        .. code-block:: python

            from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection
            import numpy as np

            m1 = CylinderMagnet(
                position=[0.005, 0.0, 0.0],
                diameter=0.01,
                height=0.02,
                polarization=[0.0, 0.0, 1.0],
            )
            m2 = CuboidMagnet(
                position=[-0.005, 0.0, 0.0],
                dimensions=[0.01, 0.01, 0.01],
                polarization=[0.0, 0.0, -1.0],
            )
            collection = SourceCollection([m1, m2])
            points = np.array([[0.0, 0.0, 0.05]])
            B = collection.compute_B(points)  # shape (1, 3)
    """
