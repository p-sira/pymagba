/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::LinearHallSensor as MagbaLinearHallSensor;
use pyo3::prelude::*;

use crate::impl_pypose;

/// A physical representation of a linear Hall effect sensor.
///
/// Outputs an analog voltage proportional to the magnetic field component along its
/// sensitive axis. The output is centered at ``supply_voltage / 2`` (quiescent voltage)
/// and clamped to the range ``[0, supply_voltage]``.
///
/// Args:
///     position (list, optional): Sensor position ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (list, optional): Orientation as a unit quaternion ``[x, y, z, w]``.
///         Defaults to the identity quaternion.
///     sensitive_axis (list, optional): The local axis along which the field is measured
///         ``[ax, ay, az]``. Normalized internally. Defaults to ``[0.0, 0.0, 1.0]`` (Z-axis).
///     sensitivity (float, optional): Sensor sensitivity in V/T. Defaults to ``1.0``.
///     supply_voltage (float, optional): Supply voltage in volts. Sets the output range
///         to ``[0, supply_voltage]`` with quiescent point at ``supply_voltage / 2``.
///         Defaults to ``5.0``.
///
/// Examples:
///
///     .. code-block:: python
///
///         from pymagba.sensors import LinearHallSensor
///         from pymagba.magnets import CylinderMagnet
///
///         magnet = CylinderMagnet(
///             position=[0.0, 0.0, 0.01],
///             diameter=0.01,
///             height=0.005,
///             polarization=[0.0, 0.0, 1.0],
///         )
///         sensor = LinearHallSensor(
///             position=[0.0, 0.0, 0.025],
///             sensitive_axis=[0.0, 0.0, 1.0],
///             sensitivity=0.05,
///             supply_voltage=5.0,
///         )
///         voltage = sensor.read_voltage_cylinder(magnet)
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct LinearHallSensor {
    pub(crate) inner: MagbaLinearHallSensor<f64>,
}

#[pymethods]
impl LinearHallSensor {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, sensitivity=1.0, supply_voltage=5.0))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        sensitive_axis: Option<crate::util::ArrayLike3>,
        sensitivity: f64,
        supply_voltage: f64,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let s_axis = sensitive_axis.map(|a| a.0).unwrap_or([0.0, 0.0, 1.0]);

        Self {
            inner: MagbaLinearHallSensor::new(pos, rot, s_axis, sensitivity, supply_voltage),
        }
    }

    /// The local sensitive axis ``[ax, ay, az]`` (unit vector).
    ///
    /// Setting a new axis rebuilds the sensor, preserving all other parameters.
    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    /// Rebuild with new sensitive_axis while preserving all other parameters.
    #[setter]
    fn set_sensitive_axis(&mut self, axis: crate::util::ArrayLike3) {
        let sensitivity = self.inner.sensitivity();
        let new_inner = MagbaLinearHallSensor::new(
            self.inner.position(),
            self.inner.orientation(),
            axis.0,
            sensitivity,
            self.inner.supply_voltage(),
        );
        self.inner = new_inner;
    }

    /// Sensor sensitivity in V/T.
    #[getter]
    fn sensitivity(&self) -> f64 {
        self.inner.sensitivity()
    }

    #[setter]
    fn set_sensitivity(&mut self, sensitivity: f64) {
        self.inner.set_sensitivity(sensitivity);
    }

    /// Supply voltage in volts. Defines the output range ``[0, supply_voltage]``
    /// and the quiescent (zero-field) voltage at ``supply_voltage / 2``.
    #[getter]
    fn supply_voltage(&self) -> f64 {
        self.inner.supply_voltage()
    }

    #[setter]
    fn set_supply_voltage(&mut self, voltage: f64) {
        self.inner.set_supply_voltage(voltage);
    }
}

impl_pypose!(LinearHallSensor);
impl_read_voltage!(LinearHallSensor);
