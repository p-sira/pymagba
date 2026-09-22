# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

# Standalone pymagba field benchmarks (no magpylib dependency).
# benchmark_name attributes preserve historical ASV result keys recorded under
# the "fields.*" namespace when these benchmarks were part of comparison/fields.py.

import numpy as np
import pymagba.fields
from scipy.spatial.transform import Rotation


def _get_observer_grid(n=1000000):
    base_observers = np.array(
        [
            [-0.12788963, 0.14872334, -0.35838915],
            [-0.17319799, 0.39177646, 0.22413971],
            [-0.15831916, -0.39768996, 0.41800279],
            [-0.05762575, 0.19985373, 0.02645361],
            [0.19120126, -0.13021813, -0.21615004],
            [0.39272212, 0.36457661, -0.09758084],
            [-0.39270581, -0.19805643, 0.36988649],
            [0.28942161, 0.31003054, -0.29558298],
            [0.13083584, 0.31396182, -0.11231319],
            [-0.04097917, 0.43394138, -0.14109254],
        ]
    )
    return np.tile(base_observers, (n // 10, 1))


def _get_standard_rotation():
    return Rotation.from_euler("xyz", [10, 20, 30], degrees=True)


class FieldCircular:
    def setup(self):
        self.observers = _get_observer_grid()
        self.args = (self.observers, (0, 0, 0), _get_standard_rotation(), 0.01, 1.0)

    def time_field(self):
        pymagba.fields.circular_B(*self.args)


FieldCircular.time_field.benchmark_name = "fields.FieldCircular.time_field"  # type: ignore[attr-defined]


class FieldCuboid:
    def setup(self):
        self.observers = _get_observer_grid()
        self.args = (
            self.observers,
            (0, 0, 0),
            _get_standard_rotation(),
            (0.1, 0.2, 0.3),
            (1, 2, 3),
        )

    def time_field(self):
        pymagba.fields.cuboid_B(*self.args)


FieldCuboid.time_field.benchmark_name = "fields.FieldCuboid.time_field"  # type: ignore[attr-defined]


class FieldCylinder:
    def setup(self):
        self.observers = _get_observer_grid()
        self.args = (
            self.observers,
            (0, 0, 0),
            _get_standard_rotation(),
            0.1,
            0.2,
            (1, 2, 3),
        )

    def time_field(self):
        pymagba.fields.cylinder_B(*self.args)


FieldCylinder.time_field.benchmark_name = "fields.FieldCylinder.time_field"  # type: ignore[attr-defined]


class FieldDipole:
    def setup(self):
        self.observers = _get_observer_grid()
        self.args = (self.observers, (0, 0, 0), _get_standard_rotation(), (1, 2, 3))

    def time_field(self):
        pymagba.fields.dipole_B(*self.args)


FieldDipole.time_field.benchmark_name = "fields.FieldDipole.time_field"  # type: ignore[attr-defined]


class FieldSphere:
    def setup(self):
        self.observers = _get_observer_grid()
        self.args = (
            self.observers,
            (0, 0, 0),
            _get_standard_rotation(),
            0.1,
            (1, 2, 3),
        )

    def time_field(self):
        pymagba.fields.sphere_B(*self.args)


FieldSphere.time_field.benchmark_name = "fields.FieldSphere.time_field"  # type: ignore[attr-defined]


class FieldTetrahedron:
    def setup(self):
        self.observers = _get_observer_grid()
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        self.args = (
            self.observers,
            (0, 0, 0),
            _get_standard_rotation(),
            (1, 2, 3),
            vertices,
        )

    def time_field(self):
        pymagba.fields.tetrahedron_B(*self.args)


FieldTetrahedron.time_field.benchmark_name = "fields.FieldTetrahedron.time_field"  # type: ignore[attr-defined]


class FieldMesh:
    def setup(self):
        self.observers = _get_observer_grid()
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]
        self.args = (
            self.observers,
            (0, 0, 0),
            _get_standard_rotation(),
            (1, 2, 3),
            vertices,
            faces,
        )

    def time_field(self):
        pymagba.fields.mesh_B(*self.args)


FieldMesh.time_field.benchmark_name = "fields.FieldMesh.time_field"  # type: ignore[attr-defined]
