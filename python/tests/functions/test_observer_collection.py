# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import numpy as np
from pymagba.sensors import LinearHallSensor, HallSwitch, HallLatch, ObserverCollection
from pymagba.magnets import CylinderMagnet
import pytest


def test_observer_collection_init():
    s1 = LinearHallSensor(position=[0, 0, 0], sensitive_axis=[0, 0, 1])
    s2 = HallSwitch(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1], b_op=0.01)

    coll = ObserverCollection(sensors=[s1, s2], position=[1, 2, 3])

    assert np.allclose(coll.position, [1, 2, 3])


def test_observer_collection_read_all():
    # Create a sensor at [0,0,0.01] sensitive to Z axis
    s1 = LinearHallSensor(
        position=[0, 0, 0.01],
        sensitive_axis=[0, 0, 1],
        sensitivity=1.0,
        supply_voltage=5.0,
    )
    # Create a switch at [0,0,0.01] sensitive to Z axis, b_op=0.1T
    s2 = HallSwitch(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1], b_op=0.1)

    coll = ObserverCollection(sensors=[s1, s2])

    # Create a magnet at [0,0,0]
    magnet = CylinderMagnet(
        diameter=0.01, height=0.01, polarization=[0, 0, 1], position=[0, 0, 0]
    )

    # Read from collection
    results = coll.read_all(magnet)

    assert len(results) == 2
    assert isinstance(results[0], float)
    assert isinstance(results[1], int)

    # Manually check s1 reading
    # B at [0,0,0.01] from cylinder at [0,0,0] with pol [0,0,1]
    # This should be positive.
    assert results[0] > 2.5  # Quiescent is 2.5V


def test_observer_collection_pose_application():
    # Sensor at local [0,0,0]
    s1 = LinearHallSensor(position=[0, 0, 0], sensitive_axis=[0, 0, 1])
    # Collection at [0,0,0.01]
    coll = ObserverCollection(sensors=[s1], position=[0, 0, 0.01])

    # Magnet at [0,0,0]
    magnet = CylinderMagnet(
        diameter=0.01, height=0.01, polarization=[0, 0, 1], position=[0, 0, 0]
    )

    # Reading should be same as sensor at [0,0,0]
    res_coll = coll.read_all(magnet)[0]

    s_direct = LinearHallSensor(position=[0, 0, 0], sensitive_axis=[0, 0, 1])
    res_direct = s_direct.read(magnet)

    assert np.allclose(res_coll, res_direct)


def test_observer_collection_empty():
    coll = ObserverCollection(sensors=[])
    magnet = CylinderMagnet(diameter=0.01, height=0.01, polarization=[0, 0, 1])
    results = coll.read_all(magnet)
    assert len(results) == 0


def test_observer_collection_read_source_collection():
    s1 = LinearHallSensor(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1])
    coll = ObserverCollection(sensors=[s1])

    m1 = CylinderMagnet(
        diameter=0.01, height=0.01, polarization=[0, 0, 1], position=[0, 0, 0]
    )
    from pymagba.magnets import SourceCollection

    sources = SourceCollection(sources=[m1])

    results = coll.read_all(sources)
    assert len(results) == 1

    # Compare with direct reading
    res_direct = s1.read(sources)
    assert np.allclose(results[0], res_direct)


if __name__ == "__main__":
    pytest.main([__file__])
