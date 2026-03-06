/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallSwitch as MagbaHallSwitch;
use pyo3::prelude::*;

use crate::impl_pypose;

/// A physical representation of a unipolar Hall effect switch sensor.
///
/// Outputs a digital ``True``/``False`` reading based solely on whether the
/// projected magnetic field component along the sensitive axis exceeds the operate
/// point ``b_op``. This sensor is **stateless** — it does not model hysteresis.
///
/// Args:
///     position (list, optional): Sensor position ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (list, optional): Orientation as a unit quaternion ``[x, y, z, w]``.
///         Defaults to the identity quaternion.
///     sensitive_axis (list, optional): The local axis along which the field is measured
///         ``[ax, ay, az]``. Normalized internally. Defaults to ``[0.0, 0.0, 1.0]`` (Z-axis).
///     b_op (float, optional): Magnetic operate point in Tesla. The switch turns ON when the
///         projected field exceeds this threshold. Defaults to ``0.010`` (10 mT).
///
/// Examples:
///
///     .. code-block:: python
///
///         from pymagba.sensors import HallSwitch
///         from pymagba.magnets import CylinderMagnet
///
///         magnet = CylinderMagnet(
///             position=[0.0, 0.0, 0.01],
///             diameter=0.01,
///             height=0.005,
///             polarization=[0.0, 0.0, 1.0],
///         )
///         sensor = HallSwitch(
///             position=[0.0, 0.0, 0.025],
///             sensitive_axis=[0.0, 0.0, 1.0],
///             b_op=0.010,
///         )
///         state = sensor.read_state_cylinder(magnet)  # True if ON
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct HallSwitch {
    pub(crate) inner: MagbaHallSwitch<f64>,
}

#[pymethods]
impl HallSwitch {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, b_op=0.010))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        sensitive_axis: Option<crate::util::ArrayLike3>,
        b_op: f64,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let s_axis = sensitive_axis.map(|a| a.0).unwrap_or([0.0, 0.0, 1.0]);

        Self {
            inner: MagbaHallSwitch::new(pos, rot, s_axis, b_op),
        }
    }

    /// The local sensitive axis ``[ax, ay, az]`` (unit vector). Normalized internally.
    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: crate::util::ArrayLike3) {
        self.inner.set_sensitive_axis(axis.0);
    }

    /// Magnetic operate point in Tesla. The sensor turns ON when the projected field exceeds this value.
    #[getter]
    fn b_op(&self) -> f64 {
        *self.inner.b_op()
    }

    #[setter]
    fn set_b_op(&mut self, b_op: f64) {
        self.inner.set_b_op(b_op);
    }
}

impl_pypose!(HallSwitch);
impl_read_state!(HallSwitch);
