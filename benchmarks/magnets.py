# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import pymagba.magnets
from .common import get_observer_grid, get_standard_rotation


class MagnetCuboid:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        magnet = pymagba.magnets.CuboidMagnet(
            position=(0, 0, 0),
            orientation=get_standard_rotation(),
            dimensions=(0.1, 0.2, 0.3),
            polarization=(1, 2, 3),
        )
        self.func = magnet.compute_B

    def time_compute_B(self):
        self.func(self.observers)


class MagnetSphere:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        magnet = pymagba.magnets.SphereMagnet(
            position=(0, 0, 0),
            orientation=get_standard_rotation(),
            diameter=0.1,
            polarization=(1, 2, 3),
        )
        self.func = magnet.compute_B

    def time_compute_B(self):
        self.func(self.observers)


class MagnetCylinder:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        magnet = pymagba.magnets.CylinderMagnet(
            position=(0, 0, 0),
            orientation=get_standard_rotation(),
            diameter=0.1,
            height=0.2,
            polarization=(1, 2, 3),
        )
        self.func = magnet.compute_B

    def time_compute_B(self):
        self.func(self.observers)


class MagnetDipole:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        magnet = pymagba.magnets.Dipole(
            position=(0, 0, 0),
            orientation=get_standard_rotation(),
            moment=(1, 2, 3),
        )
        self.func = magnet.compute_B

    def time_compute_B(self):
        self.func(self.observers)


class MagnetCircular:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        from pymagba.currents import CircularCurrent

        magnet = CircularCurrent(
            position=(0, 0, 0),
            orientation=get_standard_rotation(),
            diameter=0.2,
            current=10.0,
        )
        self.func = magnet.compute_B

    def time_compute_B(self):
        self.func(self.observers)


class MagnetCollection:
    def setup(self):
        self.observers = get_observer_grid(1000000)
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

    def time_compute_B(self):
        self.func(self.observers)
