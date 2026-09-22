# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

# Standalone pymagba magnet and object benchmarks (no magpylib dependency).
# benchmark_name attributes preserve historical ASV result keys recorded under
# the "magnets.*" and "operations.*" namespaces when these benchmarks were
# part of comparison/magnets.py and comparison/operations.py.

import numpy as np
import pymagba.magnets
from pymagba.currents import CircularCurrent
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


# ---------------------------------------------------------------------------
# Magnet benchmarks
# ---------------------------------------------------------------------------


class MagnetCircular:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = CircularCurrent(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            diameter=0.2,
            current=10.0,
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetCircular.time_compute_B.benchmark_name = "magnets.MagnetCircular.time_compute_B"  # type: ignore[attr-defined]


class MagnetCollection:
    def setup(self):
        self.observers = _get_observer_grid()
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
        self.magnet = pymagba.magnets.SourceCollection([m1, m2, m3])

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetCollection.time_compute_B.benchmark_name = "magnets.MagnetCollection.time_compute_B"  # type: ignore[attr-defined]


class MagnetCuboid:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.CuboidMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            dimensions=(0.1, 0.2, 0.3),
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetCuboid.time_compute_B.benchmark_name = "magnets.MagnetCuboid.time_compute_B"  # type: ignore[attr-defined]


class MagnetCylinder:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.CylinderMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            diameter=0.1,
            height=0.2,
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetCylinder.time_compute_B.benchmark_name = "magnets.MagnetCylinder.time_compute_B"  # type: ignore[attr-defined]


class MagnetDipole:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.Dipole(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            moment=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetDipole.time_compute_B.benchmark_name = "magnets.MagnetDipole.time_compute_B"  # type: ignore[attr-defined]


class MagnetMesh:
    def setup(self):
        self.observers = _get_observer_grid()
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]
        self.magnet = pymagba.magnets.MeshMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            vertices=vertices,
            faces=faces,
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetMesh.time_compute_B.benchmark_name = "magnets.MagnetMesh.time_compute_B"  # type: ignore[attr-defined]


class MagnetSphere:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.SphereMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            diameter=0.1,
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetSphere.time_compute_B.benchmark_name = "magnets.MagnetSphere.time_compute_B"  # type: ignore[attr-defined]


class MagnetTetrahedron:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.TetrahedronMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            vertices=[[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]],
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetTetrahedron.time_compute_B.benchmark_name = "magnets.MagnetTetrahedron.time_compute_B"  # type: ignore[attr-defined]


class MagnetTriangle:
    def setup(self):
        self.observers = _get_observer_grid()
        self.magnet = pymagba.magnets.TriangleMagnet(
            position=(0, 0, 0),
            orientation=_get_standard_rotation(),
            vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, 0.1], [0.0, 0.2, 0.0]],
            polarization=(1, 2, 3),
        )

    def time_compute_B(self):
        self.magnet.compute_B(self.observers)


MagnetTriangle.time_compute_B.benchmark_name = "magnets.MagnetTriangle.time_compute_B"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Object operation benchmarks
# ---------------------------------------------------------------------------


class ObjectCreation:
    params = (["Cylinder", "Collection"],)
    param_names = ("geometry",)

    def time_creation(self, geometry):
        if geometry == "Cylinder":
            for _ in range(10000):
                pymagba.magnets.CylinderMagnet(
                    position=(0, 0, 0),
                    orientation=_get_standard_rotation(),
                    diameter=0.1,
                    height=0.2,
                    polarization=(1, 2, 3),
                )
        elif geometry == "Collection":
            for _ in range(10000):
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
                pymagba.magnets.SourceCollection([m1, m2])


ObjectCreation.time_creation.benchmark_name = "operations.ObjectCreation.time_creation"  # type: ignore[attr-defined]


class ObjectManipulation:
    params = (["Cylinder", "Collection"], ["Translate", "Rotate"])
    param_names = ("geometry", "operation")

    def setup(self, geometry, operation):
        self.rot = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
        if geometry == "Cylinder":
            self.magnet = pymagba.magnets.CylinderMagnet(
                position=(0, 0, 0),
                orientation=_get_standard_rotation(),
                diameter=0.1,
                height=0.2,
                polarization=(1, 2, 3),
            )
        elif geometry == "Collection":
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
            self.magnet = pymagba.magnets.SourceCollection([m1, m2])

    def time_manipulation(self, geometry, operation):
        if operation == "Translate":
            for _ in range(10000):
                self.magnet.translate((0.001, 0.002, 0.003))  # type: ignore[attr-defined]
        elif operation == "Rotate":
            rot_quat = self.rot.as_quat()
            for _ in range(10000):
                self.magnet.rotate(rot_quat)


ObjectManipulation.time_manipulation.benchmark_name = "operations.ObjectManipulation.time_manipulation"  # type: ignore[attr-defined]
