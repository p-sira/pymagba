# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import pymagba.magnets
from magpylib import Collection as MagpyCollection
from magpylib.magnet import Cuboid, Cylinder
from magpylib.misc import Dipole as MagpyDipole
from scipy.spatial.transform import Rotation

from .common import get_standard_rotation


class ObjectCreation:
    params = (["PyMagba", "MagpyLib"], ["Cuboid", "Cylinder", "Collection"])
    param_names = ("library", "geometry")

    def time_creation(self, library, geometry):
        if library == "PyMagba":
            if geometry == "Cuboid":
                for _ in range(10000):
                    pymagba.magnets.CuboidMagnet(
                        position=(0, 0, 0),
                        orientation=get_standard_rotation(),
                        dimensions=(0.1, 0.2, 0.3),
                        polarization=(1, 2, 3),
                    )
            elif geometry == "Cylinder":
                for _ in range(10000):
                    pymagba.magnets.CylinderMagnet(
                        position=(0, 0, 0),
                        orientation=get_standard_rotation(),
                        diameter=0.1,
                        height=0.2,
                        polarization=(1, 2, 3),
                    )
            elif geometry == "Collection":
                for _ in range(10000):
                    m1 = pymagba.magnets.CylinderMagnet(
                        position=(0.005, 0.0, 0.0), diameter=0.01, height=0.02, polarization=(0.0, 0.0, 1.0)
                    )
                    m2 = pymagba.magnets.CuboidMagnet(
                        position=(-0.005, 0.0, 0.0), dimensions=(0.01, 0.01, 0.01), polarization=(0.0, 0.0, -1.0)
                    )
                    m3 = pymagba.magnets.Dipole(
                        position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0)
                    )
                    pymagba.magnets.SourceCollection([m1, m2, m3])
        else:
            if geometry == "Cuboid":
                for _ in range(10000):
                    Cuboid(
                        position=(0, 0, 0),
                        orientation=get_standard_rotation(),
                        dimension=(0.1, 0.2, 0.3),
                        polarization=(1, 2, 3),
                    )
            elif geometry == "Cylinder":
                for _ in range(10000):
                    Cylinder(
                        position=(0, 0, 0),
                        orientation=get_standard_rotation(),
                        dimension=(0.1, 0.2),
                        polarization=(1, 2, 3),
                    )
            elif geometry == "Collection":
                for _ in range(10000):
                    m1 = Cylinder(
                        position=(0.005, 0.0, 0.0), dimension=(0.01, 0.02), polarization=(0.0, 0.0, 1.0)
                    )
                    m2 = Cuboid(
                        position=(-0.005, 0.0, 0.0), dimension=(0.01, 0.01, 0.01), polarization=(0.0, 0.0, -1.0)
                    )
                    m3 = MagpyDipole(
                        position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0)
                    )
                    MagpyCollection(m1, m2, m3)


class ObjectManipulation:
    params = (["PyMagba", "MagpyLib"], ["Translate", "Rotate"])
    param_names = ("library", "operation")

    def setup(self, library, operation):
        self.rot = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
        if library == "PyMagba":
            m1 = pymagba.magnets.CylinderMagnet(
                position=(0.005, 0.0, 0.0), diameter=0.01, height=0.02, polarization=(0.0, 0.0, 1.0)
            )
            m2 = pymagba.magnets.CuboidMagnet(
                position=(-0.005, 0.0, 0.0), dimensions=(0.01, 0.01, 0.01), polarization=(0.0, 0.0, -1.0)
            )
            m3 = pymagba.magnets.Dipole(
                position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0)
            )
            self.magnet = pymagba.magnets.SourceCollection([m1, m2, m3])
            self.move_by = self.magnet.translate
            self.rotate_by = self.magnet.rotate
        else:
            m1 = Cylinder(
                position=(0.005, 0.0, 0.0), dimension=(0.01, 0.02), polarization=(0.0, 0.0, 1.0)
            )
            m2 = Cuboid(
                position=(-0.005, 0.0, 0.0), dimension=(0.01, 0.01, 0.01), polarization=(0.0, 0.0, -1.0)
            )
            m3 = MagpyDipole(
                position=(0.0, 0.005, 0.0), moment=(0.0, 1.0, 0.0)
            )
            self.magnet = MagpyCollection(m1, m2, m3)
            self.move_by = self.magnet.move
            self.rotate_by = self.magnet.rotate

    def time_manipulation(self, library, operation):
        if operation == "Translate":
            for _ in range(10000):
                self.move_by((0.001, 0.002, 0.003))
        elif operation == "Rotate":
            for _ in range(10000):
                self.rotate_by(self.rot)
