# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import magpylib._src.fields.field_BH_cylinder
import magpylib._src.fields.field_BH_sphere
import magpylib._src.fields.field_BH_cuboid
import magpylib._src.fields.field_BH_dipole
import magpylib._src.fields.field_BH_circle

import pymagba.fields
from .common import get_observer_grid, get_standard_rotation


class FieldCylinder:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        if library == "PyMagba":
            self.func = pymagba.fields.cylinder_B
            self.args = (
                self.observers,
                (0, 0, 0),
                get_standard_rotation(),
                0.1,
                0.2,
                (1, 2, 3),
            )
        else:
            self.func = magpylib._src.fields.field_BH_cylinder._BHJM_magnet_cylinder
            self.args = (
                "B",
                self.observers,
                np.array([[0.2, 0.2]] * len(self.observers)),
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)


class FieldSphere:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        if library == "PyMagba":
            self.func = pymagba.fields.sphere_B
            self.args = (
                self.observers,
                (0, 0, 0),
                get_standard_rotation(),
                0.1,
                (1, 2, 3),
            )
        else:
            self.func = magpylib._src.fields.field_BH_sphere._BHJM_magnet_sphere
            self.args = (
                "B",
                self.observers,
                np.array([0.1] * len(self.observers)),
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)


class FieldCuboid:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        if library == "PyMagba":
            self.func = pymagba.fields.cuboid_B
            self.args = (
                self.observers,
                (0, 0, 0),
                get_standard_rotation(),
                (0.1, 0.2, 0.3),
                (1, 2, 3),
            )
        else:
            self.func = magpylib._src.fields.field_BH_cuboid._BHJM_magnet_cuboid
            self.args = (
                "B",
                self.observers,
                np.array([[0.1, 0.2, 0.3]] * len(self.observers)),
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)


class FieldDipole:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        if library == "PyMagba":
            self.func = pymagba.fields.dipole_B
            self.args = (self.observers, (0, 0, 0), get_standard_rotation(), (1, 2, 3))
        else:
            self.func = magpylib._src.fields.field_BH_dipole._BHJM_dipole
            self.args = (
                "B",
                self.observers,
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)


class FieldCircular:
    params = ["PyMagba", "MagpyLib"]
    param_names = ["library"]

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        if library == "PyMagba":
            self.func = pymagba.fields.circular_B
            self.args = (self.observers, (0, 0, 0), get_standard_rotation(), 0.01, 1.0)
        else:
            self.func = magpylib._src.fields.field_BH_circle._BHJM_circle
            self.args = (
                "B",
                self.observers,
                np.array([0.01] * len(self.observers)),
                np.array([1.0] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)
