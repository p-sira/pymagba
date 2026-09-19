# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import magpylib as magpy
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
