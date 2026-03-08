/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CuboidMagnet as MagbaCuboidMagnet;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct CuboidMagnet {
    pub(crate) inner: MagbaCuboidMagnet<f64>,
}

#[pymethods]
impl CuboidMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, dimensions=None, polarization=None))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        dimensions: Option<crate::util::ArrayLike3>,
        polarization: Option<crate::util::ArrayLike3>,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let dim = dimensions.map(|d| d.0).unwrap_or([1.0, 1.0, 1.0]);

        Self {
            inner: MagbaCuboidMagnet::new(pos, rot, pol, dim),
        }
    }

    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: crate::util::ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }

    #[getter]
    fn dimensions(&self) -> [f64; 3] {
        self.inner.dimensions().into()
    }

    #[setter]
    fn set_dimensions(&mut self, dim: crate::util::ArrayLike3) {
        self.inner.set_dimensions(dim.0);
    }
}

impl_pypose!(CuboidMagnet);
impl_compute_B!(CuboidMagnet);
