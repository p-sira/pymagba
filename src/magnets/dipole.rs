/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::Dipole as MagbaDipole;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct Dipole {
    pub(crate) inner: MagbaDipole<f64>,
}

#[pymethods]
impl Dipole {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, moment=None))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        moment: Option<crate::util::ArrayLike3>,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let m = moment.map(|m| m.0).unwrap_or([0.0, 0.0, 0.0]);

        Self {
            inner: MagbaDipole::new(pos, rot, m),
        }
    }

    #[getter]
    fn moment(&self) -> [f64; 3] {
        self.inner.moment().into()
    }

    #[setter]
    fn set_moment(&mut self, moment: crate::util::ArrayLike3) {
        self.inner.set_moment(moment.0);
    }
}

impl_pypose!(Dipole);
impl_compute_B!(Dipole);
