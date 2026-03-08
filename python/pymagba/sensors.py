# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Sensor class module."""

from .pymagba_binding import (
    LinearHallSensor as _LinearHallSensor,
    HallSwitch as _HallSwitch,
    HallLatch as _HallLatch,
)

__all__ = ["LinearHallSensor", "HallSwitch", "HallLatch"]


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
            voltage = sensor.read_voltage_cylinder(magnet)
    """

    def read_voltage_cylinder(self, source):
        """Compute the analog output voltage (V) in the presence of a CylinderMagnet."""
        return _LinearHallSensor.read_voltage_cylinder(self, source)

    def read_voltage_cuboid(self, source):
        """Compute the analog output voltage (V) in the presence of a CuboidMagnet."""
        return _LinearHallSensor.read_voltage_cuboid(self, source)

    def read_voltage_dipole(self, source):
        """Compute the analog output voltage (V) in the presence of a Dipole source."""
        return _LinearHallSensor.read_voltage_dipole(self, source)

    def read_voltage_collection(self, source):
        """Compute the analog output voltage (V) in the presence of a SourceCollection."""
        return _LinearHallSensor.read_voltage_collection(self, source)


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
            state = sensor.read_state_cylinder(magnet)  # True if ON
    """

    def read_state_cylinder(self, source):
        """Read the digital state of the sensor in the presence of a CylinderMagnet."""
        return _HallSwitch.read_state_cylinder(self, source)

    def read_state_cuboid(self, source):
        """Read the digital state of the sensor in the presence of a CuboidMagnet."""
        return _HallSwitch.read_state_cuboid(self, source)

    def read_state_dipole(self, source):
        """Read the digital state of the sensor in the presence of a Dipole source."""
        return _HallSwitch.read_state_dipole(self, source)

    def read_state_collection(self, source):
        """Read the digital state of the sensor in the presence of a SourceCollection."""
        return _HallSwitch.read_state_collection(self, source)


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
            state = sensor.read_state_cylinder(magnet)  # True if latched ON
    """

    def read_state_cylinder(self, source):
        """Read the digital state of the sensor in the presence of a CylinderMagnet."""
        return _HallLatch.read_state_cylinder(self, source)

    def read_state_cuboid(self, source):
        """Read the digital state of the sensor in the presence of a CuboidMagnet."""
        return _HallLatch.read_state_cuboid(self, source)

    def read_state_dipole(self, source):
        """Read the digital state of the sensor in the presence of a Dipole source."""
        return _HallLatch.read_state_dipole(self, source)

    def read_state_collection(self, source):
        """Read the digital state of the sensor in the presence of a SourceCollection."""
        return _HallLatch.read_state_collection(self, source)
