# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Sensor class module."""

from .pymagba_binding import (
    LinearHallSensor as _LinearHallSensor,
    HallSwitch as _HallSwitch,
    HallLatch as _HallLatch,
    ObserverCollection as _ObserverCollection,
)

__all__ = ["LinearHallSensor", "HallSwitch", "HallLatch", "ObserverCollection"]


class LinearHallSensor(_LinearHallSensor):
    """A physical representation of a linear Hall effect sensor.

    Outputs an analog voltage proportional to the magnetic field component along its
    sensitive axis. The output is centered at supply_voltage / 2 (quiescent voltage)
    and clamped to the range [0, supply_voltage].

    Args:

        position (ArrayLike3, optional): Sensor position [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        sensitive_axis (ArrayLike3, optional): The local axis along which the field is
            measured [ax, ay, az]. Normalized internally. Defaults to [0.0, 0.0, 1.0].
        sensitivity (float, optional): Sensor sensitivity in V/T. Defaults to 1.0.
        supply_voltage (float, optional): Supply voltage in volts. Sets the output range
            to [0, supply_voltage] with quiescent point at supply_voltage / 2.
            Defaults to 5.0.

    Examples:

        .. code-block:: python

            from pymagba.sensors import LinearHallSensor
            from pymagba.magnets import CylinderMagnet

            magnet = CylinderMagnet(
                position=[0.0, 0.0, 0.01],
                diameter=0.01,
                height=0.005,
                polarization=[0.0, 0.0, 1.0],
            )
            sensor = LinearHallSensor(
                position=[0.0, 0.0, 0.025],
                sensitive_axis=[0.0, 0.0, 1.0],
                sensitivity=0.05,
                supply_voltage=5.0,
            )
            voltage = sensor.read_voltage(magnet)
    """


class HallSwitch(_HallSwitch):
    """A physical representation of a unipolar Hall effect switch sensor.

    Outputs a digital True/False reading based solely on whether the
    projected magnetic field component along the sensitive axis exceeds the operate
    point b_op. This sensor is stateless — it does not model hysteresis.

    Args:

        position (ArrayLike3, optional): Sensor position [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        sensitive_axis (ArrayLike3, optional): The local axis along which the field is
            measured [ax, ay, az]. Normalized internally. Defaults to [0.0, 0.0, 1.0].
        b_op (float, optional): Magnetic operate point in Tesla. The switch turns ON when the
            projected field exceeds this threshold. Defaults to 0.010 (10 mT).

    Examples:

        .. code-block:: python

            from pymagba.sensors import HallSwitch
            from pymagba.magnets import CylinderMagnet

            magnet = CylinderMagnet(
                position=[0.0, 0.0, 0.01],
                diameter=0.01,
                height=0.005,
                polarization=[0.0, 0.0, 1.0],
            )
            sensor = HallSwitch(
                position=[0.0, 0.0, 0.025],
                sensitive_axis=[0.0, 0.0, 1.0],
                b_op=0.010,
            )
            state = sensor.read_state(magnet)  # True if ON
    """


class HallLatch(_HallLatch):
    """A physical representation of a Hall effect latch sensor.

    Outputs a digital True/False reading based on the magnetic operate point (b_op)
    and release point (b_rp) thresholds. Provides hysteresis by maintaining internal state:

    - When projected field ≥ b_op: state becomes True (Active).
    - When projected field ≤ b_rp: state becomes False (Inactive).
    - When field is between b_rp and b_op: state is preserved.

    Args:

        position (ArrayLike3, optional): Sensor position [x, y, z] in meters.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Orientation as a unit quaternion [x, y, z, w]
            or a scipy.spatial.transform.Rotation object. Defaults to identity.
        sensitive_axis (ArrayLike3, optional): The local axis along which the field is
            measured [ax, ay, az]. Normalized internally. Defaults to [0.0, 0.0, 1.0].
        b_op (float, optional): Magnetic operate point in Tesla. Field must exceed
            this to switch ON. Defaults to 0.010 (10 mT).
        b_rp (float, optional): Magnetic release point in Tesla. Field must fall
            below this to switch OFF. Defaults to -0.010 (-10 mT).

    Examples:

        .. code-block:: python

            from pymagba.sensors import HallLatch
            from pymagba.magnets import CylinderMagnet

            magnet = CylinderMagnet(
                position=[0.0, 0.0, 0.01],
                diameter=0.01,
                height=0.005,
                polarization=[0.0, 0.0, 1.0],
            )
            sensor = HallLatch(
                position=[0.0, 0.0, 0.025],
                sensitive_axis=[0.0, 0.0, 1.0],
                b_op=0.010,
                b_rp=-0.010,
            )
            state = sensor.read_state(magnet)  # True if latched ON
    """


class ObserverCollection(_ObserverCollection):
    """A collection of magnetic sensors.

    Allows grouping multiple sensors (LinearHallSensor, HallSwitch, HallLatch)
    and performing collective readings in a single call.

    Args:

        sensors (list[Sensor], optional): A list of sensor objects to include in the collection.
            Defaults to None.
        position (ArrayLike3, optional): Collection position [x, y, z] in meters.
            This pose is applied to all sensors in addition to their own poses.
            Defaults to [0.0, 0.0, 0.0].
        orientation (PyRotation, optional): Collection orientation.
            Defaults to identity.

    Examples:

        .. code-block:: python

            from pymagba.sensors import ObserverCollection, LinearHallSensor
            from pymagba.magnets import CylinderMagnet

            s1 = LinearHallSensor(position=[0, 0, 0], sensitive_axis=[0, 0, 1])
            s2 = LinearHallSensor(position=[0, 0, 0.01], sensitive_axis=[0, 0, 1])
            coll = ObserverCollection(sensors=[s1, s2])

            magnet = CylinderMagnet(diameter=0.01, height=0.01, polarization=[0, 0, 1])
            outputs = coll.read_all(magnet) # returns [val1, val2]
    """
