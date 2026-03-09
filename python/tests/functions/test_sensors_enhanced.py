import numpy as np
import pytest
from pymagba.sensors import LinearHallSensor, HallSwitch, HallLatch, ObserverCollection
from pymagba.magnets import (
    CylinderMagnet,
    CuboidMagnet,
    Dipole,
    SphereMagnet,
    SourceCollection,
)
from pymagba.currents import CircularCurrent


def test_sensor_unified_read_all_sources():
    """Verify that all sensors can read from all types of sources."""
    sensors = [
        LinearHallSensor(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1]),
        HallSwitch(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1], b_op=0.001),
        HallLatch(
            position=[0, 0, 0.01], sensitive_axis=[0, 0, 1], b_op=0.001, b_rp=-0.001
        ),
    ]

    sources = [
        CylinderMagnet(diameter=0.01, height=0.01, polarization=[0, 0, 1]),
        CuboidMagnet(dimensions=[0.01, 0.01, 0.01], polarization=[0, 0, 1]),
        Dipole(moment=[0, 0, 1]),
        SphereMagnet(diameter=0.01, polarization=[0, 0, 1]),
        CircularCurrent(diameter=0.01, current=100.0),
    ]

    for sensor in sensors:
        for source in sources:
            # Check unified read
            val = sensor.read(source)
            if isinstance(sensor, LinearHallSensor):
                assert isinstance(val, (float, np.float64))
                assert val > 2.5  # Should be > quiescent
            else:
                assert isinstance(val, bool)
                assert val is True


def test_observer_collection_unified_read():
    """Verify ObserverCollection.read_all with all sources."""
    s1 = LinearHallSensor(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1])
    s2 = HallSwitch(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1], b_op=0.001)
    coll = ObserverCollection(sensors=[s1, s2])

    source = CircularCurrent(diameter=0.01, current=1.0)

    results = coll.read_all(source)
    assert len(results) == 2
    assert isinstance(results[0], float)
    assert isinstance(results[1], (bool, int))


if __name__ == "__main__":
    pytest.main([__file__])
