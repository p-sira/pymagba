/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::currents::CircularCurrent as MagbaCircularCurrent;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{extract_states, try_into_quat, try_into_slice, ArrayLike3, PyRotation},
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct CircularCurrent {
    pub(crate) inner: MagbaCircularCurrent<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl CircularCurrent {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, diameter=1.0, current=1.0))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        diameter: f64,
        current: f64,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaCircularCurrent::new(pos, rot, diameter, current),
        })
    }

    #[getter]
    fn diameter(&self) -> f64 {
        self.inner.diameter()
    }

    #[setter]
    fn set_diameter(&mut self, diameter: f64) -> PyResult<()> {
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_diameter(diameter);
        }))
    }

    #[getter]
    fn current(&self) -> f64 {
        self.inner.current()
    }

    #[setter]
    fn set_current(&mut self, current: f64) {
        self.inner.set_current(current);
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("diameter", self.inner.diameter())?;
        dict.set_item("current", self.inner.current())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, diameter, current]);

        self.inner = MagbaCircularCurrent::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(nalgebra::Quaternion::from_vector(
                orientation.into(),
            )),
            diameter,
            current,
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

impl_pypose!(CircularCurrent);
impl_compute_B!(CircularCurrent);
