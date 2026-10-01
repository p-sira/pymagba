/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallLatch as MagbaHallLatch;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{extract_states, try_into_quat, try_into_slice, ArrayLike3, PyRotation, SourceRef},
    macros::impl_pypose,
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct HallLatch {
    pub(crate) inner: MagbaHallLatch<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl HallLatch {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, b_op=0.010, b_rp=-0.010))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        sensitive_axis: Option<ArrayLike3>,
        b_op: f64,
        b_rp: f64,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let s_axis = if let Some(axis) = sensitive_axis {
            crate::base::validate_and_normalize_axis(axis.0)?
        } else {
            nalgebra::Vector3::z()
        };

        if !b_op.is_finite() || !b_rp.is_finite() || b_op <= b_rp {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be greater than B_RP.",
            ));
        }

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaHallLatch::new(pos, rot, s_axis, b_op, b_rp),
        })
    }

    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: ArrayLike3) -> PyResult<()> {
        let s_axis = crate::base::validate_and_normalize_axis(axis.0)?;
        self.inner.set_sensitive_axis(s_axis);
        Ok(())
    }

    #[getter]
    fn b_op(&self) -> f64 {
        *self.inner.b_op()
    }

    #[setter]
    fn set_b_op(&mut self, b_op: f64) -> PyResult<()> {
        if !b_op.is_finite() || b_op <= *self.inner.b_rp() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be greater than B_RP.",
            ));
        }
        self.inner.set_b_op(b_op);
        Ok(())
    }

    #[getter]
    fn b_rp(&self) -> f64 {
        *self.inner.b_rp()
    }

    #[setter]
    fn set_b_rp(&mut self, b_rp: f64) -> PyResult<()> {
        if !b_rp.is_finite() || b_rp >= *self.inner.b_op() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be greater than B_RP.",
            ));
        }
        self.inner.set_b_rp(b_rp);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        let a = self.inner.sensitive_axis();
        dict.set_item("sensitive_axis", [a.x, a.y, a.z])?;
        dict.set_item("b_op", *self.inner.b_op())?;
        dict.set_item("b_rp", *self.inner.b_rp())?;
        dict.set_item(
            "state",
            self.inner.state().load(std::sync::atomic::Ordering::SeqCst),
        )?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: pyo3::Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, sensitive_axis;3, b_op, b_rp]);
        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let s_axis = crate::base::validate_and_normalize_axis(sensitive_axis)?;
        if !b_op.is_finite() || !b_rp.is_finite() || b_op <= b_rp {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be greater than B_RP.",
            ));
        }

        let new_inner =
            catch_unwind_to_pyerr(move || MagbaHallLatch::new(position, rot, s_axis, b_op, b_rp))?;
        if let Ok(Some(saved_state)) = state.get_item("state") {
            let is_active: bool = saved_state.extract()?;
            new_inner
                .state()
                .store(is_active, std::sync::atomic::Ordering::SeqCst);
        }
        self.inner = new_inner;
        Ok(())
    }

    fn read_state(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<bool> {
        let source_ref = SourceRef::try_extract(&source)?;
        Ok(self.inner.read_state(source_ref.as_source()))
    }
}

impl_pypose!(HallLatch);
impl_unified_read!(HallLatch, bool, Digital);
