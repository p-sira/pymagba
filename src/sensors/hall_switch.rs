/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::HallSwitch as MagbaHallSwitch;
use pyo3::prelude::*;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::impl_pypose;

#[gen_stub_pyclass]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct HallSwitch {
    pub(crate) inner: MagbaHallSwitch<f64>,
}

#[gen_stub_pymethods]
#[pymethods]
impl HallSwitch {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, b_op=0.010))]
    fn new(
        position: Option<crate::base::ArrayLike3>,
        orientation: Option<crate::base::PyRotation>,
        sensitive_axis: Option<crate::base::ArrayLike3>,
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

    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: crate::base::ArrayLike3) {
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
        let position: [f64; 3] = state.get_item("position")?.unwrap().extract()?;
        let orientation: [f64; 4] = state.get_item("orientation")?.unwrap().extract()?;
        let sensitive_axis: [f64; 3] = state.get_item("sensitive_axis")?.unwrap().extract()?;
        let b_op: f64 = state.get_item("b_op")?.unwrap().extract()?;
        self.inner = MagbaHallSwitch::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(nalgebra::Quaternion::from_vector(
                orientation.into(),
            )),
            sensitive_axis,
            b_op,
        );
        Ok(())
    }

    fn __reduce__(&self, py: Python<'_>) -> PyResult<pyo3::Py<pyo3::types::PyTuple>> {
        let cls = py.get_type::<Self>();
        let state = self.__getstate__(py)?;
        let args = pyo3::types::PyTuple::empty(py);
        Ok(pyo3::types::PyTuple::new(
            py,
            [
                cls.into_any(),
                args.into_any(),
                state.into_bound(py).into_any(),
            ],
        )?
        .unbind())
    }
}

impl_pypose!(HallSwitch);
impl_read_state!(HallSwitch);
