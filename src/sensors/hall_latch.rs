/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallLatch as MagbaHallLatch;
use pyo3::prelude::*;

use crate::impl_pypose;

/// A physical representation of a Hall effect latch sensor.
///
/// Outputs a digital ``True``/``False`` reading based on the magnetic operate point (``b_op``)
/// and release point (``b_rp``) thresholds. Provides **hysteresis** by maintaining internal state:
///
/// - When projected field ≥ ``b_op``: state becomes ``True`` (Active).
/// - When projected field ≤ ``b_rp``: state becomes ``False`` (Inactive).
/// - When field is between ``b_rp`` and ``b_op``: state is preserved.
///
/// Args:
///     position (list[float] | None): Sensor position ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (list[float] | None): Orientation as a unit quaternion ``[x, y, z, w]``.
///         Defaults to the identity quaternion.
///     sensitive_axis (list[float] | None): The local axis along which the field is measured
///         ``[ax, ay, az]``. Normalized internally. Defaults to ``[0.0, 0.0, 1.0]`` (Z-axis).
///     b_op (float): Magnetic operate point in Tesla. Field must exceed this to switch ON.
///         Defaults to ``0.010`` (10 mT).
///     b_rp (float): Magnetic release point in Tesla. Field must fall below this to switch OFF.
///         Defaults to ``-0.010`` (-10 mT).
///
/// Examples:
///
/// ```python
/// from pymagba.sensors import HallLatch
/// from pymagba.magnets import CylinderMagnet
/// magnet = CylinderMagnet(position=[0.0, 0.0, 0.01], diameter=0.01, height=0.005,
///                         polarization=[0.0, 0.0, 1.0])
/// sensor = HallLatch(
///     position=[0.0, 0.0, 0.025],
///     sensitive_axis=[0.0, 0.0, 1.0],
///     b_op=0.010,
///     b_rp=-0.010,
/// )
/// state = sensor.read_state_cylinder(magnet)  # True if latched ON
/// ```
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct HallLatch {
    pub(crate) inner: MagbaHallLatch<f64>,
}

#[pymethods]
impl HallLatch {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, b_op=0.010, b_rp=-0.010))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        sensitive_axis: Option<crate::util::ArrayLike3>,
        b_op: f64,
        b_rp: f64,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let s_axis = sensitive_axis.map(|a| a.0).unwrap_or([0.0, 0.0, 1.0]);

        Self {
            inner: MagbaHallLatch::new(pos, rot, s_axis, b_op, b_rp),
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

    /// Magnetic operate point in Tesla. The sensor switches ON when the projected field exceeds this value.
    #[getter]
    fn b_op(&self) -> f64 {
        *self.inner.b_op()
    }

    #[setter]
    fn set_b_op(&mut self, b_op: f64) {
        self.inner.set_b_op(b_op);
    }

    /// Magnetic release point in Tesla. The sensor switches OFF when the projected field falls below this value.
    #[getter]
    fn b_rp(&self) -> f64 {
        *self.inner.b_rp()
    }

    #[setter]
    fn set_b_rp(&mut self, b_rp: f64) {
        self.inner.set_b_rp(b_rp);
    }
}

impl_pypose!(HallLatch);
impl_read_state!(HallLatch);
