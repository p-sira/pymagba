/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallSwitch as MagbaHallSwitch;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, try_into_slice_or, ArrayLike3, PyRotation,
        SourceRef,
    },
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
        let s_axis = try_into_slice_or!(sensitive_axis, [0.0, 0.0, 1.0]);

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
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_sensitive_axis(axis.0);
        }))
    }

    #[getter]
    fn b_op(&self) -> f64 {
        *self.inner.b_op()
    }

    #[setter]
    fn set_b_op(&mut self, b_op: f64) -> PyResult<()> {
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_b_op(b_op);
        }))
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

        self.inner = MagbaHallSwitch::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(orientation.into()),
            sensitive_axis,
            b_op,
        );
        Ok(())
    }

    fn read_state(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<bool> {
        let source_ref = SourceRef::try_extract(&source)?;
        Ok(self.inner.read_state(source_ref.as_source()))
    }
}

impl_pypose!(HallSwitch);
impl_unified_read!(HallSwitch, bool, Digital);
