/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CuboidMagnet as MagbaCuboidMagnet;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, try_into_slice_or, ArrayLike3, PyRotation,
    },
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct CuboidMagnet {
    pub(crate) inner: MagbaCuboidMagnet<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl CuboidMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, dimensions=None, polarization=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        dimensions: Option<ArrayLike3>,
        polarization: Option<ArrayLike3>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let pol = try_into_slice_or!(polarization, [0.0, 0.0, 1.0]);
        let dim = try_into_slice_or!(dimensions, [1.0, 1.0, 1.0]);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaCuboidMagnet::new(pos, rot, pol, dim),
        })
    }

    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }

    #[getter]
    fn dimensions(&self) -> [f64; 3] {
        self.inner.dimensions().into()
    }

    #[setter]
    fn set_dimensions(&mut self, dim: ArrayLike3) -> PyResult<()> {
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_dimensions(dim.0);
        }))
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("dimensions", <[f64; 3]>::from(self.inner.dimensions()))?;
        dict.set_item("polarization", <[f64; 3]>::from(self.inner.polarization()))?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, dimensions;3, polarization;3]);

        self.inner = MagbaCuboidMagnet::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(nalgebra::Quaternion::from_vector(
                orientation.into(),
            )),
            polarization,
            dimensions,
        );
        Ok(())
    }
}

impl_pypose!(CuboidMagnet);
impl_compute_B!(CuboidMagnet);
