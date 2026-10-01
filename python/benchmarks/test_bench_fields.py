# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Benchmarks for the functional field API (pymagba.fields)."""

import pymagba.fields
import pytest
from scipy.spatial.transform import Rotation

from .conftest import make_observers

ROTATION = Rotation.from_euler("xyz", [10, 20, 30], degrees=True)
VERTICES = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
FACES = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]

FIELDS = {
    "circular": (pymagba.fields.circular_B, ((0, 0, 0), ROTATION, 0.01, 1.0)),
    "cuboid": (
        pymagba.fields.cuboid_B,
        ((0, 0, 0), ROTATION, (0.1, 0.2, 0.3), (1, 2, 3)),
    ),
    "cylinder": (
        pymagba.fields.cylinder_B,
        ((0, 0, 0), ROTATION, 0.1, 0.2, (1, 2, 3)),
    ),
    "dipole": (pymagba.fields.dipole_B, ((0, 0, 0), ROTATION, (1, 2, 3))),
    "sphere": (pymagba.fields.sphere_B, ((0, 0, 0), ROTATION, 0.1, (1, 2, 3))),
    "tetrahedron": (
        pymagba.fields.tetrahedron_B,
        ((0, 0, 0), ROTATION, (1, 2, 3), VERTICES),
    ),
    "mesh": (
        pymagba.fields.mesh_B,
        ((0, 0, 0), ROTATION, (1, 2, 3), VERTICES, FACES),
    ),
}


@pytest.mark.parametrize("n_observers", [1, 10_000])
@pytest.mark.parametrize("field", list(FIELDS))
def test_field_B(benchmark, field, n_observers):
    func, args = FIELDS[field]
    observers = make_observers(n_observers)
    result = benchmark(func, observers, *args)
    assert result.shape == (n_observers, 3)
