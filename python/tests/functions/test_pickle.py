import pickle

import numpy as np
from pymagba.currents import PathCurrent, SheetCurrent, TriangleCurrent
from pymagba.magnets import CuboidMagnet, CylinderMagnet, Dipole, SourceCollection
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


def test_pickle_path_current():
    m = PathCurrent(
        position=[0.1, 0.2, 0.3],
        orientation=[0.1, 0.2, 0.3, 0.4],
        current=5.0,
        vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1]],
    )
    b = pickle.dumps(m)
    m2 = pickle.loads(b)

    np.testing.assert_array_equal(m.position, m2.position)
    np.testing.assert_array_equal(m.orientation.as_quat(), m2.orientation.as_quat())
    assert m.current == m2.current
    np.testing.assert_array_equal(m.vertices, m2.vertices)


def test_pickle_triangle_current():
    m = TriangleCurrent(
        position=[0.1, 0.2, 0.3],
        orientation=[0.1, 0.2, 0.3, 0.4],
        current_density=[1.0, 2.0, 3.0],
        vertices=[[-0.1, -0.1, -0.1], [0.1, -0.1, -0.1], [0.0, 0.1, -0.1]],
    )
    b = pickle.dumps(m)
    m2 = pickle.loads(b)

    np.testing.assert_array_equal(m.position, m2.position)
    np.testing.assert_array_equal(m.orientation.as_quat(), m2.orientation.as_quat())
    np.testing.assert_array_equal(m.current_density, m2.current_density)
    np.testing.assert_array_equal(m.vertices, m2.vertices)


def test_pickle_sheet_current():
    m = SheetCurrent(
        position=[0.1, 0.2, 0.3],
        orientation=[0.1, 0.2, 0.3, 0.4],
        current_densities=[
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ],
        vertices=[
            [-0.1, -0.1, -0.1],
            [0.1, -0.1, -0.1],
            [0.0, 0.1, -0.1],
            [0.0, 0.0, 0.1],
        ],
        faces=[[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]],
    )
    b = pickle.dumps(m)
    m2 = pickle.loads(b)

    np.testing.assert_array_equal(m.position, m2.position)
    np.testing.assert_array_equal(m.orientation.as_quat(), m2.orientation.as_quat())
    np.testing.assert_array_equal(m.current_densities, m2.current_densities)
    np.testing.assert_array_equal(m.vertices, m2.vertices)
    np.testing.assert_array_equal(m.faces, m2.faces)


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


def test_pickle_source_collection_initial_pose():
    # Audit item 1: SourceCollection constructed with non-origin position
    # must preserve field calculation across pickle roundtrip
    from pymagba.magnets import SphereMagnet
    point = [0, 0, 2]
    dipole = Dipole(moment=[0, 0, 1])
    col = SourceCollection([dipole], position=[0, 0, 1])

    b_before = col.compute_B(point)
    col_restored = pickle.loads(pickle.dumps(col))
    b_after = col_restored.compute_B(point)

    np.testing.assert_allclose(b_after, b_before, atol=0)
    assert np.allclose(col_restored.position, [0, 0, 1])
    assert np.allclose(col_restored[0].position, [0, 0, 0])


def test_pickle_observer_collection_initial_pose():
    # Audit item 1: ObserverCollection constructed with non-origin position
    from pymagba.magnets import SphereMagnet
    magnet = SphereMagnet()
    point = [0, 0, 2]
    sensor = LinearHallSensor(position=point)
    observers = ObserverCollection([sensor], position=[0, 0, 1])

    v_before = observers.read_all(magnet)
    restored = pickle.loads(pickle.dumps(observers))
    v_after = restored.read_all(magnet)

    np.testing.assert_allclose(v_after, v_before, atol=0)
    assert np.allclose(restored.position, [0, 0, 1])
    assert np.allclose(restored[0].position, point)


def test_pickle_hall_latch_hysteresis():
    # Audit item 3: HallLatch pickle loses hysteresis
    from pymagba.magnets import SphereMagnet
    from pymagba.sensors import HallLatch
    magnet = SphereMagnet()
    zero = SphereMagnet(polarization=[0, 0, 0])
    latch = HallLatch()
    assert latch.read(magnet) is True
    assert latch.read(zero) is True

    restored = pickle.loads(pickle.dumps(latch))
    assert restored.read(zero) is True

