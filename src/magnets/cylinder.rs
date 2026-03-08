/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CylinderMagnet as MagbaCylinderMagnet;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct CylinderMagnet {
    pub(crate) inner: MagbaCylinderMagnet<f64>,
}

#[pymethods]
impl CylinderMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, diameter=1.0, height=1.0, polarization=None))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        diameter: f64,
        height: f64,
        polarization: Option<crate::util::ArrayLike3>,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);

        Self {
            inner: MagbaCylinderMagnet::new(pos, rot, pol, diameter, height),
        }
    }

    #[getter]
    fn diameter(&self) -> f64 {
        self.inner.diameter()
    }

    #[setter]
    fn set_diameter(&mut self, diameter: f64) {
        self.inner.set_diameter(diameter);
    }

    #[getter]
    fn height(&self) -> f64 {
        self.inner.height()
    }

    #[setter]
    fn set_height(&mut self, height: f64) {
        self.inner.set_height(height);
    }

    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: crate::util::ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }
}

impl_pypose!(CylinderMagnet);
impl_compute_B!(CylinderMagnet);
