# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Benchmarks for the sensor API (pymagba.sensors)."""

import pytest
from pymagba.magnets import CylinderMagnet
from pymagba.sensors import HallLatch, HallSwitch, LinearHallSensor, ObserverCollection

MAGNET = CylinderMagnet(
    position=[0.0, 0.0, 0.01],
    diameter=0.01,
    height=0.005,
    polarization=[0.0, 0.0, 1.0],
)
SENSOR_POSITION = [0.0, 0.0, 0.025]


def test_linear_hall_read_voltage(benchmark):
    sensor = LinearHallSensor(
        position=SENSOR_POSITION,
        sensitive_axis=[0.0, 0.0, 1.0],
        sensitivity=0.05,
        supply_voltage=5.0,
    )
    benchmark(sensor.read_voltage, MAGNET)


def test_hall_switch_read_state(benchmark):
    sensor = HallSwitch(position=SENSOR_POSITION, b_op=0.010)
    benchmark(sensor.read_state, MAGNET)


def test_hall_latch_read_state(benchmark):
    sensor = HallLatch(position=SENSOR_POSITION, b_op=0.010, b_rp=-0.010)
    benchmark(sensor.read_state, MAGNET)


@pytest.mark.parametrize("n_sensors", [10, 1000])
def test_observer_collection_read_all(benchmark, n_sensors):
    sensors = [
        LinearHallSensor(position=[0.00037 * i, 0.0013, 0.025])
        for i in range(n_sensors)
    ]
    collection = ObserverCollection(sensors)
    result = benchmark(collection.read_all, MAGNET)
    assert len(result) == n_sensors
