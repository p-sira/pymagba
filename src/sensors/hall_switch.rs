/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallSwitch as MagbaHallSwitch;
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
pub struct HallSwitch {
    pub(crate) inner: MagbaHallSwitch<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl HallSwitch {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, b_op=0.010))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        sensitive_axis: Option<ArrayLike3>,
        b_op: f64,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let s_axis = if let Some(axis) = sensitive_axis {
            crate::base::validate_and_normalize_axis(axis.0)?
        } else {
            nalgebra::Vector3::z()
        };

        if !b_op.is_finite() || b_op < 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be non-negative.",
            ));
        }

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaHallSwitch::new(pos, rot, s_axis, b_op),
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
        if !b_op.is_finite() || b_op < 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be non-negative.",
            ));
        }
        self.inner.set_b_op(b_op);
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
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: pyo3::Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, sensitive_axis;3, b_op]);
        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let s_axis = crate::base::validate_and_normalize_axis(sensitive_axis)?;
        if !b_op.is_finite() || b_op < 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "B_OP must be non-negative.",
            ));
        }

        let new_inner =
            catch_unwind_to_pyerr(move || MagbaHallSwitch::new(position, rot, s_axis, b_op))?;
        self.inner = new_inner;
        Ok(())
    }

    fn read_state(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<bool> {
        #[cfg(feature = "threshold-calibration")]
        let py = source.py();
        let source_ref = SourceRef::try_extract(&source)?;
        #[cfg(feature = "threshold-calibration")]
        if crate::execution::should_detach(false) {
            let owned_source = source_ref.into_component();
            return Ok(py.detach(|| self.inner.read_state(&owned_source)));
        }
        Ok(self.inner.read_state(source_ref.as_source()))
    }
}

impl_pypose!(HallSwitch);
impl_unified_read!(HallSwitch, bool, Digital);
