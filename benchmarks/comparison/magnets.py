# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import magpylib as magpy
import pymagba.magnets
from magpylib.magnet import Cuboid, Cylinder, Sphere
from magpylib.misc import Dipole

from .common import get_observer_grid, get_standard_rotation


class MagnetCuboid:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
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
            m3 = pymagba.magnets.Dipole(
                position=(0.0, 0.005, 0.0),
                moment=(0.0, 1.0, 0.0),
            )
            magnet = pymagba.magnets.SourceCollection([m1, m2, m3])
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
            m3_py = Dipole(
                position=(0.0, 0.005, 0.0),
                moment=(0.0, 1.0, 0.0),
            )
            magnet = magpy.Collection(m1_py, m2_py, m3_py)
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetTetrahedron:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        if library == "PyMagba":
            magnet = pymagba.magnets.TetrahedronMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            from magpylib.magnet import Tetrahedron

            magnet = Tetrahedron(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetMesh:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]
        if library == "PyMagba":
            magnet = pymagba.magnets.MeshMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=faces,
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            from magpylib.magnet import TriangularMesh

            magnet = TriangularMesh(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=faces,
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class MagnetTriangle:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[-0.1, -0.1, -0.1], [0.1, -0.1, 0.1], [0.0, 0.2, 0.0]]
        if library == "PyMagba":
            magnet = pymagba.magnets.TriangleMagnet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                polarization=(1, 2, 3),
            )
            self.func = magnet.compute_B
        else:
            from magpylib.magnet import TriangularMesh

            magnet = TriangularMesh(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=[[0, 1, 2]],
                polarization=(1, 2, 3),
            )
            self.func = magnet.getB

    def time_compute_B(self, library):
        self.func(self.observers)
