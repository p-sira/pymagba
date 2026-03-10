# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from magpylib.magnet import Cuboid, Sphere, Cylinder
from magpylib.misc import Dipole
import magpylib as magpy

import pymagba.magnets
from .common import get_observer_grid, get_standard_rotation


class MagnetCuboid:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            magnet = pymagba.magnets.CuboidMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                dimensions=(0.1, 0.2, 0.3),
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            magnet = Cuboid(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                dimension=(0.1, 0.2, 0.3),
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetSphere:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            magnet = pymagba.magnets.SphereMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                diameter=0.1,
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            magnet = Sphere(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                diameter=0.1,
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetCylinder:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            magnet = pymagba.magnets.CylinderMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                diameter=0.1,
                height=0.2,
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            magnet = Cylinder(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                dimension=(0.1, 0.2),
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetDipole:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            magnet = pymagba.magnets.Dipole(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                moment=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            magnet = Dipole(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                moment=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetCircular:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            from pymagba.currents import CircularCurrent

            magnet = CircularCurrent(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                diameter=0.2,
                current=10.0,
            )
            self.func = magnet.compute_B
        else:
            magnet = magpy.current.Circle(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                diameter=0.2,
                current=10.0,
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetCollection:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(10000)
        if library == "PyMagba":
            m1 = pymagba.magnets.CylinderMagnet(
                position=(0.005, 0.0, 0.0),
                diameter=0.01,
                height=0.02,
                polarization=(0.0, 0.0, 1.0),
            )
            m2 = pymagba.magnets.CuboidMagnet(
                position=(-0.005, 0.0, 0.0),
                dimensions=(0.01, 0.01, 0.01),
                polarization=(0.0, 0.0, -1.0),
            )
            magnet = pymagba.magnets.SourceCollection([m1, m2])
            self.func = magnet.compute_B
        else:
            m1_py = magpy.magnet.Cylinder(
                position=(0.005, 0.0, 0.0),
                dimension=(0.01, 0.02),
                polarization=(0.0, 0.0, 1.0),
            )
            m2_py = magpy.magnet.Cuboid(
                position=(-0.005, 0.0, 0.0),
                dimension=(0.01, 0.01, 0.01),
                polarization=(0.0, 0.0, -1.0),
            )
            magnet = magpy.Collection(m1_py, m2_py)
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)
