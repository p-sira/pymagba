/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CuboidMagnet as MagbaCuboidMagnet;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
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
        position: Option<crate::base::ArrayLike3>,
        orientation: Option<crate::base::PyRotation>,
        dimensions: Option<crate::base::ArrayLike3>,
        polarization: Option<crate::base::ArrayLike3>,
    ) -> PyResult<Self> {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let dim = dimensions.map(|d| d.0).unwrap_or([1.0, 1.0, 1.0]);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaCuboidMagnet::new(pos, rot, pol, dim),
        })
    }

    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: crate::base::ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }

    #[getter]
    fn dimensions(&self) -> [f64; 3] {
        self.inner.dimensions().into()
    }

    #[setter]
    fn set_dimensions(&mut self, dim: crate::base::ArrayLike3) -> PyResult<()> {
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
        let position: [f64; 3] = state.get_item("position")?.unwrap().extract()?;
        let orientation: [f64; 4] = state.get_item("orientation")?.unwrap().extract()?;
        let dimensions: [f64; 3] = state.get_item("dimensions")?.unwrap().extract()?;
        let polarization: [f64; 3] = state.get_item("polarization")?.unwrap().extract()?;

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
