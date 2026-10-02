# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Isolated FFI benchmarks covering input representations, small batch sizes,
collection assembly synchronization, source-type probing, and geometry reuse.
"""

import numpy as np
import pymagba.currents
import pymagba.fields
import pymagba.magnets
from scipy.spatial.transform import Rotation


class RotationInput:
    """Benchmark rotation extraction overhead across different Python representations."""

    params = (
        ["scipy_Rotation", "numpy_array", "python_list", "none"],
        ["Constructor", "RotateMethod", "FunctionalCall"],
    )
    param_names = ("representation", "call_type")

    def setup(self, representation: str, call_type: str):
        scipy_rot = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
        quat_arr = scipy_rot.as_quat()
        quat_list = list(quat_arr)

        if representation == "scipy_Rotation":
            self.rot = scipy_rot
        elif representation == "numpy_array":
            self.rot = quat_arr
        elif representation == "python_list":
            self.rot = quat_list
        else:
            self.rot = None

        self.magnet = pymagba.magnets.CylinderMagnet(
            position=(0, 0, 0),
            diameter=0.1,
            height=0.2,
            polarization=(1, 2, 3),
        )
        self.point = np.array([0.1, 0.2, 0.3])

    def time_rotation(self, representation: str, call_type: str):
        rot = self.rot
        if call_type == "Constructor":
            pymagba.magnets.CylinderMagnet(
                position=(0, 0, 0),
                orientation=rot,
                diameter=0.1,
                height=0.2,
                polarization=(1, 2, 3),
            )
        elif call_type == "RotateMethod":
            if rot is None:
                return
            self.magnet.rotate(rot)
        elif call_type == "FunctionalCall":
            pymagba.fields.cylinder_B(
                self.point,
                orientation=rot,
                diameter=0.1,
                height=0.2,
                polarization=(1, 2, 3),
            )


class PointsInputRepresentation:
    """Benchmark PointsLike extraction across contiguous, strided, float32, and list layouts."""

    params = (
        [
            "c_contiguous_f64",
            "fortran_contiguous_f64",
            "strided_f64",
            "float32",
            "python_list",
            "single_point_1d",
        ],
        [1, 10, 1000],
    )
    param_names = ("layout", "n_points")

    def setup(self, layout: str, n_points: int):
        self.dipole = pymagba.magnets.Dipole(moment=(0, 0, 1))

        if layout == "single_point_1d":
            if n_points != 1:
                self.pts = None
                return
            self.pts = np.array([0.1, 0.2, 0.3], dtype=np.float64)
            return

        base = np.linspace(-1.0, 1.0, n_points * 3).reshape(n_points, 3)
        if layout == "c_contiguous_f64":
            self.pts = np.ascontiguousarray(base, dtype=np.float64)
        elif layout == "fortran_contiguous_f64":
            self.pts = np.asfortranarray(base, dtype=np.float64)
        elif layout == "strided_f64":
            double = np.linspace(-1.0, 1.0, n_points * 6).reshape(n_points * 2, 3)
            self.pts = np.ascontiguousarray(double, dtype=np.float64)[::2]
        elif layout == "float32":
            self.pts = np.ascontiguousarray(base, dtype=np.float32)
        elif layout == "python_list":
            self.pts = base.tolist()

    def time_points_input(self, layout: str, n_points: int):
        if self.pts is None:
            return
        self.dipole.compute_B(self.pts)


class SmallBatchScaling:
    """Benchmark small-batch evaluation to isolate FFI boundary, single-point allocations,
    and GIL release threshold (detach_if_multi at n > 1).
    """

    params = (
        ["Dipole", "Sphere", "Cylinder", "Cuboid", "Collection"],
        [1, 2, 4, 8, 16, 32, 64, 128, 512, 1024],
    )
    param_names = ("geometry", "n_points")

    def setup(self, geometry: str, n_points: int):
        if geometry == "Dipole":
            self.source = pymagba.magnets.Dipole(moment=(1, 2, 3))
        elif geometry == "Sphere":
            self.source = pymagba.magnets.SphereMagnet(
                diameter=0.1, polarization=(1, 2, 3)
            )
        elif geometry == "Cylinder":
            self.source = pymagba.magnets.CylinderMagnet(
                diameter=0.1, height=0.2, polarization=(1, 2, 3)
            )
        elif geometry == "Cuboid":
            self.source = pymagba.magnets.CuboidMagnet(
                dimensions=(0.1, 0.2, 0.3), polarization=(1, 2, 3)
            )
        elif geometry == "Collection":
            m1 = pymagba.magnets.CylinderMagnet(
                position=(0.005, 0, 0),
                diameter=0.01,
                height=0.02,
                polarization=(0, 0, 1),
            )
            m2 = pymagba.magnets.CuboidMagnet(
                position=(-0.005, 0, 0),
                dimensions=(0.01, 0.01, 0.01),
                polarization=(0, 0, -1),
            )
            self.source = pymagba.magnets.SourceCollection([m1, m2])

        if n_points == 1:
            self.observers = np.array([0.1, 0.2, 0.3], dtype=np.float64)
        else:
            self.observers = np.linspace(
                -1.0, 1.0, n_points * 3, dtype=np.float64
            ).reshape(n_points, 3)

    def time_small_batch(self, geometry: str, n_points: int):
        self.source.compute_B(self.observers)


class CollectionAssemblyOverhead:
    """Benchmark sync_assembly overhead by comparing collection evaluation against
    evaluating children individually.
    """

    params = ([1, 2, 4, 8],)
    param_names = ("n_children",)

    def setup(self, n_children: int):
        self.children = []
        for i in range(n_children):
            pos = (i * 0.01, 0.0, 0.0)
            self.children.append(
                pymagba.magnets.CylinderMagnet(
                    position=pos,
                    diameter=0.01,
                    height=0.02,
                    polarization=(0, 0, 1),
                )
            )
        self.col = pymagba.magnets.SourceCollection(self.children)
        self.pt_single = np.array([0.1, 0.2, 0.3], dtype=np.float64)

    def time_collection_eval(self, n_children: int):
        self.col.compute_B(self.pt_single)

    def time_direct_children_eval(self, n_children: int):
        pt = self.pt_single
        for child in self.children:
            child.compute_B(pt)


class SourceTypeProbing:
    """Benchmark SourceRef::try_extract sequential probing across different source variants."""

    params = (
        [
            "Cylinder_variant_1",
            "Cuboid_variant_2",
            "Dipole_variant_3",
            "Sphere_variant_4",
            "Triangle_variant_5",
            "SheetCurrent_variant_11",
            "Collection_variant_12",
        ],
    )
    param_names = ("source_type",)

    def setup(self, source_type: str):
        verts = np.array(
            [[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]],
            dtype=np.float64,
        )
        faces = np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]], dtype=np.uintp)

        if source_type == "Cylinder_variant_1":
            src = pymagba.magnets.CylinderMagnet(
                diameter=0.01, height=0.02, polarization=(0, 0, 1)
            )
        elif source_type == "Cuboid_variant_2":
            src = pymagba.magnets.CuboidMagnet(
                dimensions=(0.01, 0.01, 0.01), polarization=(0, 0, 1)
            )
        elif source_type == "Dipole_variant_3":
            src = pymagba.magnets.Dipole(moment=(0, 0, 1))
        elif source_type == "Sphere_variant_4":
            src = pymagba.magnets.SphereMagnet(diameter=0.01, polarization=(0, 0, 1))
        elif source_type == "Triangle_variant_5":
            src = pymagba.magnets.TriangleMagnet(
                vertices=verts[:3], polarization=(0, 0, 1)
            )
        elif source_type == "SheetCurrent_variant_11":
            src = pymagba.currents.SheetCurrent(
                vertices=verts, faces=faces, current_densities=[(1, 2, 3)] * 4
            )
        else:
            c = pymagba.magnets.CylinderMagnet(
                diameter=0.01, height=0.02, polarization=(0, 0, 1)
            )
            src = pymagba.magnets.SourceCollection([c])

        self.col = pymagba.magnets.SourceCollection([src])
        self.point = np.array([0.1, 0.2, 0.3], dtype=np.float64)

    def time_probe_extraction(self, source_type: str):
        self.col.compute_B(self.point)


class PreparedGeometryReuse:
    """Benchmark rebuilding mesh each call in mesh_B vs reusing MeshMagnet instance."""

    params = (
        ["tetrahedron_4_faces", "suzanne_698_faces"],
        [1, 10],
    )
    param_names = ("mesh_name", "n_points")

    def setup(self, mesh_name: str, n_points: int):
        if mesh_name == "tetrahedron_4_faces":
            self.verts = np.array(
                [
                    [-0.1, -0.1, -0.1],
                    [0.1, -0.1, -0.1],
                    [0.0, 0.1, -0.1],
                    [0.0, 0.0, 0.1],
                ],
                dtype=np.float64,
            )
            self.faces = np.array(
                [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]], dtype=np.uintp
            )
            self.mesh_obj = pymagba.magnets.MeshMagnet(
                vertices=self.verts, faces=self.faces, polarization=(1, 2, 3)
            )
        else:
            import os

            stl_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), "..", "testing", "data", "suzanne.stl"
                )
            )
            self.mesh_obj = pymagba.magnets.MeshMagnet.from_stl(
                stl_path, polarization=(1, 2, 3)
            )
            self.verts = self.mesh_obj.vertices
            self.faces = self.mesh_obj.faces

        if n_points == 1:
            self.observers = np.array([2.0, 2.0, 2.0], dtype=np.float64)
        else:
            self.observers = np.linspace(
                2.0, 3.0, n_points * 3, dtype=np.float64
            ).reshape(n_points, 3)

    def time_functional_rebuild(self, mesh_name: str, n_points: int):
        pymagba.fields.mesh_B(
            self.observers,
            vertices=self.verts,
            faces=self.faces,
            polarization=(1, 2, 3),
        )

    def time_object_cached(self, mesh_name: str, n_points: int):
        self.mesh_obj.compute_B(self.observers)


# Skip automatic execution during standard 'asv run' suites
import inspect

for _cls in [
    RotationInput,
    PointsInputRepresentation,
    SmallBatchScaling,
    CollectionAssemblyOverhead,
    SourceTypeProbing,
    PreparedGeometryReuse,
]:
    for _name, _member in inspect.getmembers(_cls):
        if _name.startswith("time_"):
            _member.skip_benchmark = True
