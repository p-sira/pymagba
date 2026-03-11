# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import pymagba.fields
from .common import get_observer_grid, get_standard_rotation


class FieldCylinder:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        self.func = pymagba.fields.cylinder_B
        self.args = (
            self.observers,
            (0, 0, 0),
            get_standard_rotation(),
            0.1,
            0.2,
            (1, 2, 3),
        )

    def time_field(self):
        self.func(*self.args)


class FieldSphere:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        self.func = pymagba.fields.sphere_B
        self.args = (
            self.observers,
            (0, 0, 0),
            get_standard_rotation(),
            0.1,
            (1, 2, 3),
        )

    def time_field(self):
        self.func(*self.args)


class FieldCuboid:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        self.func = pymagba.fields.cuboid_B
        self.args = (
            self.observers,
            (0, 0, 0),
            get_standard_rotation(),
            (0.1, 0.2, 0.3),
            (1, 2, 3),
        )

    def time_field(self):
        self.func(*self.args)


class FieldDipole:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        self.func = pymagba.fields.dipole_B
        self.args = (self.observers, (0, 0, 0), get_standard_rotation(), (1, 2, 3))

    def time_field(self):
        self.func(*self.args)


class FieldCircular:
    def setup(self):
        self.observers = get_observer_grid(1000000)
        self.func = pymagba.fields.circular_B
        self.args = (self.observers, (0, 0, 0), get_standard_rotation(), 0.01, 1.0)

    def time_field(self):
        self.func(*self.args)
