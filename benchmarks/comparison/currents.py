# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import pymagba.currents
from magpylib.current import Polyline

from .common import get_observer_grid, get_standard_rotation


class CurrentPolyline:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
        if library == "PyMagba":
            current_obj = pymagba.currents.PathCurrent(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                current=1.5,
            )
            self.func = current_obj.compute_B
        else:
            current_obj = Polyline(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                current=1.5,
            )
            self.func = current_obj.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class CurrentTriangleCurrent:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[-0.1, -0.1, -0.1], [0.1, -0.1, 0.1], [0.0, 0.2, 0.0]]
        if library == "PyMagba":
            current_obj = pymagba.currents.TriangleCurrent(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                current_density=(1, 2, 3),
            )
            self.func = current_obj.compute_B
        else:
            from magpylib.current import TriangleSheet
            current_obj = TriangleSheet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=[[0, 1, 2]],
                current_densities=[(1, 2, 3)],
            )
            self.func = current_obj.getB

    def time_compute_B(self, library):
        self.func(self.observers)


class CurrentSheetCurrent:
    params = ("PyMagba", "MagpyLib")
    param_names = ("library",)

    def setup(self, library):
        self.observers = get_observer_grid(1000000)
        vertices = [[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1], [0.0, 0.0, 0.1]]
        faces = [[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]]
        current_densities = [(1, 2, 3)] * 4
        if library == "PyMagba":
            current_obj = pymagba.currents.SheetCurrent(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=faces,
                current_densities=current_densities,
            )
            self.func = current_obj.compute_B
        else:
            from magpylib.current import TriangleSheet
            current_obj = TriangleSheet(
                position=(0, 0, 0),
                orientation=get_standard_rotation(),
                vertices=vertices,
                faces=faces,
                current_densities=current_densities,
            )
            self.func = current_obj.getB

    def time_compute_B(self, library):
        self.func(self.observers)
