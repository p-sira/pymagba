/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::Dipole as MagbaDipole;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{extract_states, try_into_quat, try_into_slice, ArrayLike3, PyRotation},
    macros::{impl_compute_B, impl_pypose},
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct Dipole {
    pub(crate) inner: MagbaDipole<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl Dipole {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, moment=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        moment: Option<ArrayLike3>,
    ) -> Self {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let m = try_into_slice!(moment);

        Self {
            inner: MagbaDipole::new(pos, rot, m),
        }
    }

    #[getter]
    fn moment(&self) -> [f64; 3] {
        self.inner.moment().into()
    }

    #[setter]
    fn set_moment(&mut self, moment: ArrayLike3) {
        self.inner.set_moment(moment.0);
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("moment", <[f64; 3]>::from(self.inner.moment()))?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, moment;3]);

        self.inner = MagbaDipole::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(orientation.into()),
            moment,
        );
        Ok(())
    }
}

impl_pypose!(Dipole);
impl_compute_B!(Dipole);
