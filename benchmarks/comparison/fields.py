# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import magpylib._src.fields.field_BH_circle
import magpylib._src.fields.field_BH_cuboid
import magpylib._src.fields.field_BH_cylinder
import magpylib._src.fields.field_BH_dipole
import magpylib._src.fields.field_BH_sphere
import numpy as np
import pymagba.fields

from .common import get_observer_grid, get_standard_rotation


class FieldCylinder:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

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
        self.func(*self.args)  # type: ignore


class FieldSphere:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

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
        self.func(*self.args)  # type: ignore


class FieldCuboid:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

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
        self.func(*self.args)  # type: ignore


class FieldDipole:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

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
        self.func(*self.args)  # type: ignore


class FieldCircular:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

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
        self.func(*self.args)  # type: ignore


class FieldTetrahedron:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        if library == "PyMagba":
            self.func = pymagba.fields.tetrahedron_B
            self.args = (
                self.observers,
                (0, 0, 0),
                get_standard_rotation(),
                (1, 2, 3),
                vertices,
            )
        else:
            import magpylib._src.fields.field_BH_tetrahedron

            self.func = (
                magpylib._src.fields.field_BH_tetrahedron._BHJM_magnet_tetrahedron
            )
            self.args = (
                "B",
                self.observers,
                np.array([vertices] * len(self.observers)),
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)  # type: ignore


class FieldMesh:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]
        if library == "PyMagba":
            self.func = pymagba.fields.mesh_B
            self.args = (
                self.observers,
                (0, 0, 0),
                get_standard_rotation(),
                (1, 2, 3),
                vertices,
                faces,
            )
        else:
            import magpylib._src.fields.field_BH_triangularmesh

            self.func = (
                magpylib._src.fields.field_BH_triangularmesh._BHJM_magnet_trimesh
            )
            v = np.array(vertices)
            mesh = v[faces]
            self.args = (
                "B",
                self.observers,
                np.array([mesh] * len(self.observers)),
                np.array([[1, 2, 3]] * len(self.observers)),
            )

    def time_field(self, library):
        self.func(*self.args)  # type: ignore


def setup_cache():
    import os

    if os.environ.get("CI") == "true":
        raise NotImplementedError("Comparison skipped in CI")


# Restore historical benchmark names for ASV dashboard continuity
for name, obj in list(globals().items()):
    if isinstance(obj, type) and not name.startswith("_"):
        for attr_name in dir(obj):
            if (
                attr_name.startswith(("time_", "peakmem_", "track_"))
            ):
                attr = getattr(obj, attr_name)
                if callable(attr):
                    attr.benchmark_name = f"fields.{name}.{attr_name}"
