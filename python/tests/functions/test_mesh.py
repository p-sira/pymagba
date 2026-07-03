# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import pytest
from pymagba.magnets import MeshMagnet

def test_mesh_validation_valid():
    # suzanne.stl is a valid closed manifold mesh
    mesh = MeshMagnet.from_stl("testing/data/suzanne.stl")
    assert mesh is not None
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0

def test_mesh_validation_invalid():
    # bad-monkey.stl has holes/defects, should raise an error
    with pytest.raises(ValueError):
        MeshMagnet.from_stl("testing/data/bad-monkey.stl")
