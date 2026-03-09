import pickle
import numpy as np
import pytest
from pymagba.magnets import CylinderMagnet, CuboidMagnet, Dipole, SourceCollection
from pymagba.sensors import LinearHallSensor, ObserverCollection


def test_pickle_cylinder():
    m = CylinderMagnet(
        position=[0.1, 0.2, 0.3],
        diameter=0.01,
        height=0.02,
        polarization=[0.0, 0.0, 1.0],
    )
    data = pickle.dumps(m)
    m2 = pickle.loads(data)

    assert np.allclose(m2.position, [0.1, 0.2, 0.3])
    assert m2.diameter == 0.01
    assert m2.height == 0.02
    assert np.allclose(m2.polarization, [0.0, 0.0, 1.0])


def test_pickle_cuboid():
    m = CuboidMagnet(
        position=[0.1, 0.2, 0.3],
        dimensions=[0.01, 0.02, 0.03],
        polarization=[0.0, 1.0, 0.0],
    )
    data = pickle.dumps(m)
    m2 = pickle.loads(data)

    assert np.allclose(m2.position, [0.1, 0.2, 0.3])
    assert np.allclose(m2.dimensions, [0.01, 0.02, 0.03])
    assert np.allclose(m2.polarization, [0.0, 1.0, 0.0])


def test_pickle_dipole():
    m = Dipole(position=[0.1, 0.2, 0.3], moment=[0.0, 0.0, 1.0])
    data = pickle.dumps(m)
    m2 = pickle.loads(data)

    assert np.allclose(m2.position, [0.1, 0.2, 0.3])
    assert np.allclose(m2.moment, [0.0, 0.0, 1.0])


def test_pickle_source_collection_empty():
    col = SourceCollection([])
    print("DEBUG (empty): dumping SourceCollection")
    data = pickle.dumps(col)
    print("DEBUG (empty): loading SourceCollection")
    col2 = pickle.loads(data)
    print("DEBUG (empty): loaded SourceCollection")
    assert np.allclose(col2.position, [0, 0, 0])


def test_pickle_source_collection():
    m1 = CylinderMagnet(position=[0.01, 0, 0], polarization=[0, 0, 1])
    m2 = CuboidMagnet(position=[-0.01, 0, 0], polarization=[0, 0, -1])
    col = SourceCollection([m1, m2])
    col.translate([0, 0.1, 0])

    print("DEBUG: dumping SourceCollection")
    data = pickle.dumps(col)
    print("DEBUG: loading SourceCollection")
    col2 = pickle.loads(data)
    print("DEBUG: loaded SourceCollection")

    # Check pose
    assert np.allclose(col2.position, [0, 0.1, 0])

    # Check field calculation consistency
    pts = np.array([[0, 0, 0.05]])
    b1 = col.compute_B(pts)
    b2 = col2.compute_B(pts)
    assert np.allclose(b1, b2)


def test_pickle_observer_collection():
    s1 = LinearHallSensor(position=[0.005, 0, 0])
    s2 = LinearHallSensor(position=[-0.005, 0, 0])
    col = ObserverCollection([s1, s2])
    col.translate([0, 0.2, 0])

    data = pickle.dumps(col)
    col2 = pickle.loads(data)

    assert np.allclose(col2.position, [0, 0.2, 0])

    # Verify we can still perform reads
    m = CylinderMagnet(position=[0, 0.2, 0.05])
    r1 = col.read_all(m)
    r2 = col2.read_all(m)
    assert np.allclose(r1, r2)
