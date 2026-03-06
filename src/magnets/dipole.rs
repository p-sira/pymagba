/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::Dipole as MagbaDipole;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

/// Magnetic dipole source.
///
/// Models a point magnetic dipole — a useful approximation for small magnets
/// at distances much greater than their physical size.
///
/// Args:
///     position (list, optional): Position of the dipole ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (list, optional): Orientation as a unit quaternion ``[x, y, z, w]``.
///         Defaults to the identity quaternion.
///     moment (list, optional): Magnetic dipole moment vector ``[mx, my, mz]`` in A·m².
///         Defaults to ``[0.0, 0.0, 0.0]``.
///
/// Examples:
///
///     .. code-block:: python
///
///         from pymagba.magnets import Dipole
///
///         dipole = Dipole(
///             position=[0.0, 0.0, 0.0],
///             moment=[0.0, 0.0, 1.0],
///         )
///
/// References:
///     Ortner, Michael, and Lucas Gabriel Coliado Bandeira. "Magpylib: A Free Python Package
///     for Magnetic Field Computation." SoftwareX 11 (2020): 100466.
///     https://doi.org/10.1016/j.softx.2020.100466
#[pyclass(from_py_object)]
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

    /// Magnetic dipole moment vector ``[mx, my, mz]`` in A·m².
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
