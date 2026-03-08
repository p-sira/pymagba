/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallLatch as MagbaHallLatch;
use pyo3::prelude::*;

use crate::impl_pypose;

#[pyclass(subclass, from_py_object)]
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

    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: crate::util::ArrayLike3) {
        self.inner.set_sensitive_axis(axis.0);
    }

    #[getter]
    fn b_op(&self) -> f64 {
        *self.inner.b_op()
    }

    #[setter]
    fn set_b_op(&mut self, b_op: f64) {
        self.inner.set_b_op(b_op);
    }

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
