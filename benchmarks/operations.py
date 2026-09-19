# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from magpylib.magnet import Cuboid, Cylinder
import pymagba.magnets
from .common import get_standard_rotation
from scipy.spatial.transform import Rotation

class ObjectCreation:
    params = (["PyMagba", "MagpyLib"], ["Cuboid", "Cylinder"])
    param_names = ["library", "geometry"]

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

class ObjectManipulation:
    params = (["PyMagba", "MagpyLib"], ["Translate", "Rotate"])
    param_names = ["library", "operation"]

    def setup(self, library, operation):
        self.rot = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
        if library == "PyMagba":
            self.magnet = pymagba.magnets.CuboidMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                dimensions=(0.1, 0.2, 0.3),
                polarization=(1, 2, 3),
            )
            self.move_by = self.magnet.translate
            self.rotate_by = self.magnet.rotate
        else:
            self.magnet = Cuboid(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                dimension=(0.1, 0.2, 0.3),
                polarization=(1, 2, 3),
            )
            self.move_by = self.magnet.move
            self.rotate_by = self.magnet.rotate

    def time_manipulation(self, library, operation):
        if operation == "Translate":
            for _ in range(10000):
                self.move_by((0.001, 0.002, 0.003))
        elif operation == "Rotate":
            for _ in range(10000):
                self.rotate_by(self.rot)
