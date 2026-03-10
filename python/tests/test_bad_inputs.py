import numpy as np
import pytest
from pymagba.magnets import (
    SphereMagnet,
    CuboidMagnet,
    CylinderMagnet,
    Dipole,
    SourceCollection,
)
from pymagba.currents import CircularCurrent
from pymagba.sensors import LinearHallSensor, HallSwitch, HallLatch, ObserverCollection


def test_arraylike3_invalid():
    # Wrong number of elements
    with pytest.raises(ValueError, match="Expected exactly 3 elements"):
        SphereMagnet(position=[1, 2])

    with pytest.raises(ValueError, match="Expected exactly 3 elements"):
        SphereMagnet(position=np.array([1.0, 2.0, 3.0, 4.0]))

    # Wrong types
    with pytest.raises(TypeError):
        SphereMagnet(position="abc")


def test_pointslike_invalid():
    m = Dipole(moment=[0, 0, 1])
    # Wrong dimensionality for pointslike
    with pytest.raises(TypeError):
        m.compute_B([[1, 2]])  # Should be list of 3-element lists or a 3-element list


def test_sphere_magnet_validation():
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        SphereMagnet(diameter=-1.0)

    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        SphereMagnet(diameter=0.0)

    s = SphereMagnet(diameter=1.0)
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        s.diameter = -0.5


def test_cylinder_magnet_validation():
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        CylinderMagnet(diameter=-1.0)

    with pytest.raises(ValueError, match="Height cannot be negative"):
        CylinderMagnet(height=0.0)

    c = CylinderMagnet(diameter=1.0, height=1.0)
    with pytest.raises(ValueError, match="Diameter cannot be negative"):
        c.diameter = 0
    with pytest.raises(ValueError, match="Height cannot be negative"):
        c.height = -1.0


def test_cuboid_magnet_validation():
    with pytest.raises(ValueError, match="Dimensions must be non-negative"):
        CuboidMagnet(dimensions=[1.0, -1.0, 1.0])

    c = CuboidMagnet(dimensions=[1, 1, 1])
    with pytest.raises(ValueError, match="Dimensions must be non-negative"):
        c.dimensions = [1, 0, -1]


def test_circular_current_validation():
    with pytest.raises(ValueError, match="Diameter must be positive"):
        CircularCurrent(diameter=-1.0)

    cur = CircularCurrent(diameter=1.0)
    with pytest.raises(ValueError, match="Diameter must be positive"):
        cur.diameter = 0


def test_linear_hall_sensor_validation():
    with pytest.raises(ValueError, match="Supply voltage must be positive"):
        LinearHallSensor(supply_voltage=-5.0)

    s = LinearHallSensor(supply_voltage=5.0)
    with pytest.raises(ValueError, match="Supply voltage must be positive"):
        s.supply_voltage = 0


def test_hall_switch_validation():
    with pytest.raises(ValueError, match="B_OP must be non-negative"):
        HallSwitch(b_op=-0.01)

    sw = HallSwitch(b_op=0.01)
    with pytest.raises(ValueError, match="B_OP must be non-negative"):
        sw.b_op = -0.001


def test_hall_latch_validation():
    with pytest.raises(ValueError, match="B_OP must be greater than B_RP"):
        HallLatch(b_op=0.01, b_rp=0.01)

    with pytest.raises(ValueError, match="B_OP must be greater than B_RP"):
        HallLatch(b_op=0.01, b_rp=0.02)


def test_collection_validation():
    # SourceCollection with non-source
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        SourceCollection(sources=[123])

    sc = SourceCollection()
    with pytest.raises(
        TypeError, match="source must be a valid Magnet, Current, or SourceCollection"
    ):
        sc.append("not a source")

    # ObserverCollection with non-sensor
    with pytest.raises(
        TypeError, match="sensors must be LinearHallSensor, HallSwitch, or HallLatch"
    ):
        ObserverCollection(sensors=[SphereMagnet()])

    oc = ObserverCollection()
    with pytest.raises(
        TypeError, match="sensors must be LinearHallSensor, HallSwitch, or HallLatch"
    ):
        oc.append(Dipole())
